import { useState, useEffect } from 'react';
import { getApiBaseUrl } from '../api/index';

type ConnectionStatus = 'connected' | 'connecting' | 'disconnected';
type MessageHandler = (data: any) => void;

class RealtimeClient {
  private ws: WebSocket | null = null;
  private status: ConnectionStatus = 'disconnected';
  private listeners: Set<MessageHandler> = new Set();
  private statusListeners: Set<(s: ConnectionStatus) => void> = new Set();
  private reconnectTimer: any = null;
  private pingInterval: any = null;

  constructor() {
    this.connect();
  }

  public connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      this.updateStatus('connecting');
      const baseUrl = getApiBaseUrl();
      const wsProtocol = baseUrl.startsWith('https://') ? 'wss://' : 'ws://';
      const cleanHost = baseUrl.replace(/^https?:\/\//, '');
      const wsUrl = `${wsProtocol}${cleanHost}/ws/updates`;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.updateStatus('connected');
        this.startHeartbeat();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.listeners.forEach(handler => handler(data));
        } catch {
          // Non-JSON message
        }
      };

      this.ws.onclose = () => {
        this.updateStatus('disconnected');
        this.stopHeartbeat();
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.updateStatus('disconnected');
        this.stopHeartbeat();
        if (this.ws) {
          try { this.ws.close(); } catch {}
        }
      };
    } catch {
      this.updateStatus('disconnected');
      this.scheduleReconnect();
    }
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'ping', timestamp: Date.now() }));
      }
    }, 25000);
  }

  private stopHeartbeat() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 5000);
  }

  private updateStatus(newStatus: ConnectionStatus) {
    this.status = newStatus;
    this.statusListeners.forEach(listener => listener(newStatus));
  }

  public getStatus(): ConnectionStatus {
    return this.status;
  }

  public subscribe(handler: MessageHandler): () => void {
    this.listeners.add(handler);
    return () => {
      this.listeners.delete(handler);
    };
  }

  public onStatusChange(listener: (s: ConnectionStatus) => void): () => void {
    this.statusListeners.add(listener);
    listener(this.status);
    return () => {
      this.statusListeners.delete(listener);
    };
  }

  public send(msg: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  }

  public subscribeToTrip(tripId: number) {
    this.send({ action: 'subscribe', trip_id: tripId });
  }
}

export const realtimeClient = new RealtimeClient();

/** React Hook for Real-time Connection & Messages */
export const useRealtime = () => {
  const [status, setStatus] = useState<ConnectionStatus>(realtimeClient.getStatus());
  const [lastMessage, setLastMessage] = useState<any>(null);

  useEffect(() => {
    const unsubStatus = realtimeClient.onStatusChange(setStatus);
    const unsubMsg = realtimeClient.subscribe(setLastMessage);
    return () => {
      unsubStatus();
      unsubMsg();
    };
  }, []);

  return {
    status,
    isConnected: status === 'connected',
    lastMessage,
    reconnect: () => realtimeClient.connect(),
    subscribeToTrip: (tripId: number) => realtimeClient.subscribeToTrip(tripId),
  };
};
