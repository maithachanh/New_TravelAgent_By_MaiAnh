from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from app.agent.tools.registry import tool_registry

router = APIRouter(prefix="/hotels", tags=["Hotel & Accommodation Search"])

class HotelSearchRequest(BaseModel):
    city: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    budget_tier: Optional[str] = "MEDIUM"
    preferences: Optional[List[str]] = []

@router.post("/search")
def search_hotels(req: HotelSearchRequest):
    results = tool_registry.hotel_tool.search_hotels(
        city=req.city,
        check_in=req.check_in,
        check_out=req.check_out,
        budget_tier=req.budget_tier,
        preferences=req.preferences
    )
    return {
        "city": req.city,
        "count": len(results),
        "hotels": results,
        "accommodations": results
    }
