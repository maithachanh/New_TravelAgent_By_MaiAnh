from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from app.agent.tools.registry import tool_registry

router = APIRouter(prefix="/places", tags=["Places & Restaurants Search"])

class PlaceSearchRequest(BaseModel):
    city: str
    cuisine_types: Optional[List[str]] = []
    price_range: Optional[str] = "MEDIUM"

@router.post("/search")
def search_places(req: PlaceSearchRequest):
    results = tool_registry.restaurant_tool.search_restaurants(
        city=req.city,
        cuisine_types=req.cuisine_types,
        price_range=req.price_range
    )
    return {
        "city": req.city,
        "count": len(results),
        "places": results
    }
