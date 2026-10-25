import json
import asyncio
from typing import List, Dict, Any, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["Real-time WebSockets & Live Agent Updates"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.trip_subscribers: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        for trip_id, subs in list(self.trip_subscribers.items()):
            subs.discard(websocket)

    def subscribe_trip(self, trip_id: int, websocket: WebSocket):
        if trip_id not in self.trip_subscribers:
            self.trip_subscribers[trip_id] = set()
        self.trip_subscribers[trip_id].add(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast JSON message to all connected clients."""
        payload = json.dumps(message)
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.disconnect(d)

    async def broadcast_trip_update(self, trip_id: int, message: Dict[str, Any]):
        """Send update to subscribers of a specific trip or broadcast if none specific."""
        subscribers = self.trip_subscribers.get(trip_id, set())
        targets = subscribers if subscribers else self.active_connections
        payload = json.dumps(message)
        dead = []
        for connection in targets:
            try:
                await connection.send_text(payload)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.disconnect(d)

manager = ConnectionManager()

@router.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial connected greeting
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "status": "connected",
            "message": "Kết nối thời gian thực với AI Travel Agent thành công!"
        }))
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action") or msg.get("type")
                if action == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": msg.get("timestamp")}))
                elif action == "subscribe" and "trip_id" in msg:
                    manager.subscribe_trip(int(msg["trip_id"]), websocket)
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "trip_id": msg["trip_id"],
                        "message": f"Đã đăng ký theo dõi cập nhật chuyến đi {msg['trip_id']}"
                    }))
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
