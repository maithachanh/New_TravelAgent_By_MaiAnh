from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.models import User, Trip, ItineraryDay, ItineraryItem, TripStatus
from app.schemas.schemas import TripCreate, TripOut, ItineraryItemOut
from app.services.pdf_service import generate_itinerary_pdf

router = APIRouter(prefix="/trips", tags=["Trip & Itinerary Management"])

@router.get("/", response_model=List[TripOut])
def get_user_trips(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Trip).filter(Trip.user_id == current_user.id).all()

@router.get("/{trip_id}", response_model=TripOut)
def get_trip_detail(trip_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.post("/", response_model=TripOut)
def create_trip(trip_in: TripCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = Trip(
        user_id=current_user.id,
        title=trip_in.title,
        origin=trip_in.origin,
        destination=trip_in.destination,
        start_date=trip_in.start_date,
        end_date=trip_in.end_date,
        travelers=trip_in.travelers,
        budget=trip_in.budget,
        currency=trip_in.currency,
        preferences=trip_in.preferences,
        status=TripStatus.PLANNING
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

@router.get("/{trip_id}/pdf")
def export_trip_pdf(trip_id: int, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
        
    days_data = []
    for day in trip.days:
        items_data = []
        for item in day.items:
            items_data.append({
                "title": item.title,
                "item_type": item.item_type,
                "start_time": item.start_time,
                "end_time": item.end_time,
                "location": item.location,
                "estimated_cost": item.estimated_cost
            })
        days_data.append({
            "day_number": day.day_number,
            "date": day.date,
            "items": items_data
        })
        
    trip_dict = {
        "title": trip.title,
        "destination": trip.destination,
        "start_date": trip.start_date,
        "end_date": trip.end_date,
        "travelers": trip.travelers,
        "budget": trip.budget,
        "currency": trip.currency,
        "days": days_data
    }

    pdf_bytes = generate_itinerary_pdf(trip_dict)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=Itinerary_{trip.id}.pdf"
    })
