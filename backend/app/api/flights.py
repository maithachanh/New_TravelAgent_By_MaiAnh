from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from app.agent.tools.registry import tool_registry

router = APIRouter(prefix="/flights", tags=["Flight Search & Offers"])

class FlightSearchRequest(BaseModel):
    origin: str = "Hà Nội"
    destination: str
    departure_date: Optional[str] = None
    travelers: int = 1

@router.post("/search")
def search_flights(req: FlightSearchRequest):
    results = tool_registry.flight_tool.search_flights(
        origin=req.origin,
        destination=req.destination,
        departure_date=req.departure_date,
        travelers=req.travelers
    )
    return {
        "origin": req.origin,
        "destination": req.destination,
        "travelers": req.travelers,
        "count": len(results),
        "offers": results
    }
