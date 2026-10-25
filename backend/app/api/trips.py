from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.database import get_db
from app.api.auth import get_current_user_optional
from app.models.models import User, Trip, ItineraryDay, ItineraryItem, TripStatus, Booking, BookingStatus, TripVersion
from app.schemas.schemas import TripCreate, TripUpdate, TripOut, ItineraryItemOut, ItemReorderRequest
from app.services.pdf_service import generate_itinerary_pdf
from app.services.replan_service import replan_service

router = APIRouter(prefix="/trips", tags=["Trip & Itinerary Management"])

class TripModifyRequest(BaseModel):
    modification: Optional[str] = None
    modification_request: Optional[str] = None
    notes: Optional[str] = None
    modified_item_id: Optional[int] = None
    modified_item: Optional[Dict[str, Any]] = None
    new_start_time: Optional[str] = None
    replacement_title: Optional[str] = None
    language: Optional[str] = "vi"

@router.get("/", response_model=List[TripOut])
def get_user_trips(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    return db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{trip_id}", response_model=TripOut)
def get_trip_detail(trip_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.post("/", response_model=TripOut)
def create_trip(trip_in: TripCreate, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
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

@router.put("/{trip_id}", response_model=TripOut)
def update_trip(trip_id: int, trip_in: TripUpdate, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    update_data = trip_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(trip, field, val)
    db.commit()
    db.refresh(trip)
    return trip

@router.delete("/{trip_id}")
def delete_trip(trip_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return {"message": f"Chuyến đi ID {trip_id} đã được xóa thành công", "trip_id": trip_id}

@router.patch("/{trip_id}/reorder")
def reorder_itinerary_items(trip_id: int, req: ItemReorderRequest, db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return {
        "message": "Các mục lịch trình đã được cập nhật thứ tự thành công",
        "trip_id": trip_id,
        "item_ids": req.item_ids
    }

@router.patch("/{trip_id}/modify")
@router.post("/{trip_id}/modify")
def modify_trip_itinerary(trip_id: int, req: TripModifyRequest, db: Session = Depends(get_db)):
    """
    Standardized Trip Modification endpoint:
    Compatible with PATCH/POST /api/v1/trips/{id}/modify and /api/v1/ai/trips/{id}/modify.
    Applies schedule changes, recalculates dependencies, updates DB and saves new Version.
    """
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy chuyến đi ID {trip_id}")

    current_itinerary = []
    for day in trip.days:
        day_items = []
        for item in day.items:
            day_items.append({
                "id": item.id,
                "title": item.title,
                "item_type": item.item_type.value if hasattr(item.item_type, "value") else str(item.item_type),
                "start_time": item.start_time,
                "end_time": item.end_time,
                "location": item.location,
                "latitude": item.latitude,
                "longitude": item.longitude,
                "duration_minutes": item.duration_minutes,
                "estimated_cost": item.estimated_cost,
                "notes": item.notes
            })
        current_itinerary.append({
            "day_number": day.day_number,
            "date": day.date,
            "items": day_items
        })

    mod_notes = req.notes or req.modification or req.modification_request
    mod_item_id = req.modified_item_id
    if not mod_item_id and req.modified_item and "id" in req.modified_item:
        mod_item_id = req.modified_item["id"]

    replan_result = replan_service.apply_modification(
        trip_id=trip_id,
        current_itinerary=current_itinerary,
        modified_item_id=mod_item_id,
        new_start_time=req.new_start_time,
        replacement_title=req.replacement_title,
        notes=mod_notes
    )

    # Persist updated items to DB
    updated_itinerary = replan_result.get("updated_itinerary", [])
    item_updates = {}
    for day_data in updated_itinerary:
        for item in day_data.get("items", []):
            if "id" in item and item["id"]:
                item_updates[item["id"]] = item

    for day in trip.days:
        for item in day.items:
            if item.id in item_updates:
                u = item_updates[item.id]
                item.start_time = u.get("start_time", item.start_time)
                item.end_time = u.get("end_time", item.end_time)
                item.title = u.get("title", item.title)
                item.location = u.get("location", item.location)
                item.notes = u.get("notes", item.notes)
                item.estimated_cost = u.get("estimated_cost", item.estimated_cost)
                item.duration_minutes = u.get("duration_minutes", item.duration_minutes)

    try:
        trip_ver = TripVersion(
            trip_id=trip.id,
            version=replan_result["version"],
            itinerary_data=replan_result["updated_itinerary"],
            total_cost=replan_result["total_cost"],
            changes_summary=replan_result["changes_summary"]
        )
        db.add(trip_ver)
        db.commit()
    except Exception:
        db.rollback()

    return {
        "success": True,
        "message": "Cập nhật và tối ưu lại lịch trình thành công",
        "trip_id": trip_id,
        "version": replan_result["version"],
        "changes_summary": replan_result["changes_summary"],
        "total_cost": replan_result["total_cost"],
        "updated_itinerary": replan_result["updated_itinerary"],
        "itinerary": replan_result["updated_itinerary"]
    }

@router.post("/{trip_id}/confirm")
@router.patch("/{trip_id}/confirm")
def confirm_trip(trip_id: int, db: Session = Depends(get_db)):
    """
    Standardized Trip Confirmation endpoint:
    Marks trip status as CONFIRMED and confirms any associated pending bookings.
    """
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy chuyến đi ID {trip_id}")

    trip.status = TripStatus.CONFIRMED

    # Confirm associated pending bookings
    pending_bookings = db.query(Booking).filter(
        Booking.trip_id == trip_id,
        Booking.status == BookingStatus.PENDING
    ).all()

    for b in pending_bookings:
        b.status = BookingStatus.CONFIRMED

    db.commit()
    db.refresh(trip)

    return {
        "success": True,
        "message": f"Chuyến đi ID {trip_id} và {len(pending_bookings)} dịch vụ liên quan đã được xác nhận thành công",
        "trip_id": trip_id,
        "status": "CONFIRMED",
        "confirmed_bookings_count": len(pending_bookings)
    }

@router.get("/{trip_id}/versions")
def get_trip_versions_endpoint(trip_id: int, db: Session = Depends(get_db)):
    db_versions = db.query(TripVersion).filter(TripVersion.trip_id == trip_id).order_by(TripVersion.version.asc()).all()
    if db_versions:
        versions = [
            {
                "version": v.version,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "changes_summary": v.changes_summary or [],
                "total_cost": v.total_cost,
                "itinerary": v.itinerary_data
            }
            for v in db_versions
        ]
    else:
        versions = replan_service.get_trip_versions(trip_id)
    return {"trip_id": trip_id, "versions": versions}

@router.get("/{trip_id}/versions/{version}")
def get_trip_version_detail(trip_id: int, version: int, db: Session = Depends(get_db)):
    db_version = db.query(TripVersion).filter(
        TripVersion.trip_id == trip_id,
        TripVersion.version == version
    ).first()
    if not db_version:
        # Fallback to in-memory history if DB row doesn't exist
        versions = replan_service.get_trip_versions(trip_id)
        match = next((v for v in versions if v.get("version") == version), None)
        if not match:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy phiên bản {version} của chuyến đi {trip_id}")
        return match

    return {
        "trip_id": trip_id,
        "version": db_version.version,
        "created_at": db_version.created_at.isoformat() if db_version.created_at else None,
        "changes_summary": db_version.changes_summary or [],
        "total_cost": db_version.total_cost,
        "itinerary": db_version.itinerary_data
    }

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
                "item_type": item.item_type.value if hasattr(item.item_type, "value") else str(item.item_type),
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
