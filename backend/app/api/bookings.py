import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.database import get_db
from app.models.models import Booking, BookingStatus

router = APIRouter(prefix="/bookings", tags=["Booking Management (Human-in-the-loop)"])

class FlightBookingRequest(BaseModel):
    trip_id: int
    flight_number: str
    airline: str
    origin: str
    destination: str
    price: float
    passengers: int = 1
    departure_time: Optional[str] = None

class HotelBookingRequest(BaseModel):
    trip_id: int
    hotel_name: str
    city: str
    check_in: str
    check_out: str
    price: float
    guests: int = 1

class ActivityBookingRequest(BaseModel):
    trip_id: int
    activity_name: str
    location: str
    date: str
    price: float

@router.post("/flight")
def book_flight(req: FlightBookingRequest, db: Session = Depends(get_db)):
    ref = f"BK-FL-{uuid.uuid4().hex[:6].upper()}"
    booking = Booking(
        user_id=1,
        trip_id=req.trip_id,
        service_name=f"Vé bay {req.airline} ({req.flight_number}): {req.origin} -> {req.destination}",
        category="flight",
        booking_reference=ref,
        price=req.price,
        status=BookingStatus.CONFIRMED,
        details={
            "flight_number": req.flight_number,
            "airline": req.airline,
            "origin": req.origin,
            "destination": req.destination,
            "passengers": req.passengers,
            "departure": req.departure_time
        }
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Đặt vé máy bay thành công!", "booking": booking}

@router.post("/hotel")
def book_hotel(req: HotelBookingRequest, db: Session = Depends(get_db)):
    ref = f"BK-HT-{uuid.uuid4().hex[:6].upper()}"
    booking = Booking(
        user_id=1,
        trip_id=req.trip_id,
        service_name=f"Khách sạn: {req.hotel_name} ({req.city})",
        category="hotel",
        booking_reference=ref,
        price=req.price,
        status=BookingStatus.CONFIRMED,
        details={
            "hotel_name": req.hotel_name,
            "city": req.city,
            "check_in": req.check_in,
            "check_out": req.check_out,
            "guests": req.guests
        }
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Đặt phòng khách sạn thành công!", "booking": booking}

@router.post("/activity")
def book_activity(req: ActivityBookingRequest, db: Session = Depends(get_db)):
    ref = f"BK-ACT-{uuid.uuid4().hex[:6].upper()}"
    booking = Booking(
        user_id=1,
        trip_id=req.trip_id,
        service_name=f"Tour / Hoạt động: {req.activity_name}",
        category="activity",
        booking_reference=ref,
        price=req.price,
        status=BookingStatus.CONFIRMED,
        details={
            "activity_name": req.activity_name,
            "location": req.location,
            "date": req.date
        }
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Đặt hoạt động / tour thành công!", "booking": booking}

@router.get("/")
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).order_by(Booking.booking_date.desc()).all()

@router.get("/{id}")
def get_booking_by_id(id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin booking")
    return booking

@router.post("/{id}/confirm")
def confirm_booking(id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin booking")
    booking.status = BookingStatus.CONFIRMED
    db.commit()
    return {"message": "Xác nhận booking thành công!", "booking_reference": booking.booking_reference, "status": "CONFIRMED"}

@router.post("/{id}/cancel")
def cancel_booking(id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin booking")
    booking.status = BookingStatus.CANCELLED
    db.commit()
    return {"message": "Hủy booking thành công!", "booking_reference": booking.booking_reference, "status": "CANCELLED"}

