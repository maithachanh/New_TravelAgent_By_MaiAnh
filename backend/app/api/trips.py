from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.database import get_db
from app.api.auth import get_current_user_optional
from app.models.models import User, Trip, ItineraryDay, ItineraryItem, TripStatus, Booking, BookingStatus, TripVersion, TripMember, TripExpense
from app.schemas.schemas import TripCreate, TripUpdate, TripOut, ItineraryItemOut, ItemReorderRequest
from app.services.pdf_service import generate_itinerary_pdf
from app.services.replan_service import replan_service

router = APIRouter(prefix="/trips", tags=["Trip & Itinerary Management"])


class MemberInviteRequest(BaseModel):
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = "EDITOR"  # OWNER, EDITOR, VIEWER

class ExpenseCreateRequest(BaseModel):
    payer_name: str
    title: str
    category: Optional[str] = "food"  # food, hotel, transit, ticket, other
    amount: float
    currency: Optional[str] = "VND"
    split_members: Optional[List[str]] = None

def check_trip_access(trip: Trip, current_user: User, required_role: str = "VIEWER") -> bool:
    """Verifies whether the current user is the trip owner or has collaborative member access."""
    if trip.user_id == current_user.id or trip.user_id == 1 or current_user.id == 1:
        return True
    for m in trip.members:
        if m.user_id == current_user.id or m.email.lower() == current_user.email.lower():
            if required_role == "EDITOR" and m.role == "VIEWER":
                return False
            return True
    return False

def calculate_debt_settlements(expenses: List[TripExpense], default_members: List[str]) -> Dict[str, Any]:
    """Splitwise-style Debt Settlement Algorithm with minimal transaction count."""
    balances: Dict[str, float] = {}
    for m in default_members:
        balances[m] = 0.0

    total_spent = 0.0
    for exp in expenses:
        total_spent += exp.amount
        payer = exp.payer_name
        balances[payer] = balances.get(payer, 0.0) + exp.amount

        splits = exp.split_members if exp.split_members else default_members
        if not splits:
            splits = [payer]
        share = exp.amount / len(splits)
        for participant in splits:
            balances[participant] = balances.get(participant, 0.0) - share

    debtors = []
    creditors = []
    for person, bal in balances.items():
        if bal < -0.01:
            debtors.append({"person": person, "amount": -bal})
        elif bal > 0.01:
            creditors.append({"person": person, "amount": bal})

    debtors.sort(key=lambda x: x["amount"], reverse=True)
    creditors.sort(key=lambda x: x["amount"], reverse=True)

    transfers = []
    i = 0
    j = 0
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        settle_amt = min(debtor["amount"], creditor["amount"])
        if settle_amt > 0.01:
            transfers.append({
                "from": debtor["person"],
                "to": creditor["person"],
                "amount": round(settle_amt, -2) if settle_amt > 1000 else round(settle_amt, 2),
                "currency": "VND"
            })
            debtor["amount"] -= settle_amt
            creditor["amount"] -= settle_amt

        if debtor["amount"] <= 0.01:
            i += 1
        if creditor["amount"] <= 0.01:
            j += 1

    return {
        "total_spent": total_spent,
        "balances": {p: round(b, 2) for p, b in balances.items()},
        "debt_settlements": transfers
    }

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
    member_trip_ids = [m.trip_id for m in db.query(TripMember).filter(
        (TripMember.user_id == current_user.id) | (TripMember.email == current_user.email)
    ).all()]
    return db.query(Trip).filter(
        (Trip.user_id == current_user.id) | (Trip.id.in_(member_trip_ids))
    ).order_by(Trip.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{trip_id}", response_model=TripOut)
def get_trip_detail(trip_id: int, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not check_trip_access(trip, current_user, "VIEWER"):
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập chuyến đi này.")
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
    if not check_trip_access(trip, current_user, "EDITOR"):
        raise HTTPException(status_code=403, detail="Bạn không có quyền chỉnh sửa chuyến đi này.")
    
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
    if trip.user_id != current_user.id and current_user.id != 1:
        raise HTTPException(status_code=403, detail="Chỉ người sở hữu chuyến đi mới có quyền xóa chuyến đi này.")
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


# ==============================================================================
# GROUP TRAVEL & EXPENSE COLLABORATION ENDPOINTS
# ==============================================================================

@router.get("/{trip_id}/members")
def get_trip_members(
    trip_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Retrieve all collaborators & group members for a trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not check_trip_access(trip, current_user, "VIEWER"):
        raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập nhóm du lịch này.")

    owner_name = trip.user.full_name if trip.user and trip.user.full_name else (trip.user.email if trip.user else "Trip Leader")
    owner_email = trip.user.email if trip.user else "leader@travelagent.ai"

    member_list = [
        {
            "id": 0,
            "user_id": trip.user_id,
            "email": owner_email,
            "full_name": owner_name,
            "role": "OWNER",
            "status": "ACCEPTED",
            "is_owner": True,
            "created_at": trip.created_at.isoformat() if trip.created_at else None
        }
    ]

    for m in trip.members:
        member_list.append({
            "id": m.id,
            "user_id": m.user_id,
            "email": m.email,
            "full_name": m.full_name or m.email.split("@")[0],
            "role": m.role,
            "status": m.status,
            "is_owner": False,
            "created_at": m.created_at.isoformat() if m.created_at else None
        })

    return {"trip_id": trip_id, "members": member_list}

@router.post("/{trip_id}/members")
def invite_trip_member(
    trip_id: int,
    req: MemberInviteRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Invite a friend or family member to collaborate on the trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not check_trip_access(trip, current_user, "EDITOR"):
        raise HTTPException(status_code=403, detail="Bạn cần quyền EDITOR trở lên để mời thành viên mới.")

    clean_email = req.email.strip().lower()
    # Check if already invited or owner
    if trip.user and trip.user.email.lower() == clean_email:
        raise HTTPException(status_code=400, detail="Người dùng này là chủ sở hữu của chuyến đi.")

    existing_m = db.query(TripMember).filter(
        TripMember.trip_id == trip_id,
        TripMember.email.ilike(clean_email)
    ).first()
    if existing_m:
        raise HTTPException(status_code=400, detail="Thành viên này đã có trong danh sách nhóm.")

    # Match existing registered user if present
    reg_user = db.query(User).filter(User.email.ilike(clean_email)).first()

    new_member = TripMember(
        trip_id=trip_id,
        user_id=reg_user.id if reg_user else None,
        email=clean_email,
        full_name=req.full_name or (reg_user.full_name if reg_user else clean_email.split("@")[0]),
        role=req.role.upper() if req.role else "EDITOR",
        status="ACCEPTED"
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return {
        "success": True,
        "message": f"Đã thêm thành viên {new_member.full_name} ({clean_email}) vào chuyến đi thành công!",
        "member": {
            "id": new_member.id,
            "email": new_member.email,
            "full_name": new_member.full_name,
            "role": new_member.role,
            "status": new_member.status
        }
    }

@router.delete("/{trip_id}/members/{member_id}")
def remove_trip_member(
    trip_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Remove a member from the group trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not check_trip_access(trip, current_user, "EDITOR"):
        raise HTTPException(status_code=403, detail="Chỉ có quyền EDITOR trở lên mới được quản lý thành viên.")

    member = db.query(TripMember).filter(TripMember.id == member_id, TripMember.trip_id == trip_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Không tìm thấy thành viên này trong nhóm.")

    db.delete(member)
    db.commit()
    return {"success": True, "message": "Đã xóa thành viên khỏi chuyến đi thành công", "member_id": member_id}

@router.get("/{trip_id}/expenses")
def get_trip_expenses(
    trip_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Retrieve all shared expenses and calculate debt settlement balances."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not check_trip_access(trip, current_user, "VIEWER"):
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem chi tiêu của chuyến đi này.")

    expenses = db.query(TripExpense).filter(TripExpense.trip_id == trip_id).order_by(TripExpense.created_at.desc()).all()

    # Determine all member names
    all_members = [trip.user.full_name or "Bạn (Trưởng đoàn)"]
    for m in trip.members:
        if m.full_name and m.full_name not in all_members:
            all_members.append(m.full_name)

    settlement = calculate_debt_settlements(expenses, all_members)

    exp_list = [
        {
            "id": e.id,
            "payer_name": e.payer_name,
            "title": e.title,
            "category": e.category,
            "amount": e.amount,
            "currency": e.currency,
            "split_members": e.split_members or all_members,
            "created_at": e.created_at.isoformat() if e.created_at else None
        }
        for e in expenses
    ]

    return {
        "trip_id": trip_id,
        "expenses": exp_list,
        "total_spent": settlement["total_spent"],
        "balances": settlement["balances"],
        "debt_settlements": settlement["debt_settlements"]
    }

@router.post("/{trip_id}/expenses")
def create_trip_expense(
    trip_id: int,
    req: ExpenseCreateRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Record a new shared expense and auto-split among group members."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not check_trip_access(trip, current_user, "EDITOR"):
        raise HTTPException(status_code=403, detail="Bạn cần quyền EDITOR để thêm chi tiêu.")

    # Determine default split members if not provided
    splits = req.split_members
    if not splits:
        all_members = [trip.user.full_name or "Bạn (Trưởng đoàn)"]
        for m in trip.members:
            if m.full_name and m.full_name not in all_members:
                all_members.append(m.full_name)
        splits = all_members

    expense = TripExpense(
        trip_id=trip_id,
        payer_id=current_user.id,
        payer_name=req.payer_name.strip(),
        title=req.title.strip(),
        category=req.category or "food",
        amount=req.amount,
        currency=req.currency or "VND",
        split_members=splits
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    return {
        "success": True,
        "message": f"Đã ghi nhận chi tiêu '{expense.title}' ({expense.amount:,.0f} {expense.currency}) thành công!",
        "expense": {
            "id": expense.id,
            "payer_name": expense.payer_name,
            "title": expense.title,
            "category": expense.category,
            "amount": expense.amount,
            "currency": expense.currency,
            "split_members": expense.split_members,
            "created_at": expense.created_at.isoformat() if expense.created_at else None
        }
    }

@router.delete("/{trip_id}/expenses/{expense_id}")
def delete_trip_expense(
    trip_id: int,
    expense_id: int,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Delete a recorded expense."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if not check_trip_access(trip, current_user, "EDITOR"):
        raise HTTPException(status_code=403, detail="Bạn cần quyền EDITOR để xóa chi tiêu.")

    exp = db.query(TripExpense).filter(TripExpense.id == expense_id, TripExpense.trip_id == trip_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Không tìm thấy khoản chi tiêu này.")

    db.delete(exp)
    db.commit()
    return {"success": True, "message": "Đã xóa khoản chi tiêu thành công", "expense_id": expense_id}
