from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.models import Destination
from app.schemas.schemas import DestinationCreate, DestinationOut

router = APIRouter(prefix="/destinations", tags=["Destination Management"])

@router.get("/", response_model=List[DestinationOut])
def get_destinations(
    city: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Destination)
    if city:
        query = query.filter(Destination.city.ilike(f"%{city}%"))
    if category:
        query = query.filter(Destination.category == category)
    return query.all()

@router.post("/", response_model=DestinationOut)
def create_destination(dest_in: DestinationCreate, db: Session = Depends(get_db)):
    dest = Destination(**dest_in.model_dump())
    db.add(dest)
    db.commit()
    db.refresh(dest)
    return dest
