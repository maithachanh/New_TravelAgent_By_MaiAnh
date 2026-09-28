from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from app.agent.tools.registry import tool_registry

router = APIRouter(prefix="/activities", tags=["Sightseeing & Activities Search"])

class ActivitySearchRequest(BaseModel):
    city: str
    categories: Optional[List[str]] = []
    duration_days: int = 3

@router.post("/search")
def search_activities(req: ActivitySearchRequest):
    results = tool_registry.activity_tool.search_activities(
        city=req.city,
        categories=req.categories,
        duration_days=req.duration_days
    )
    return {
        "city": req.city,
        "count": len(results),
        "activities": results
    }
