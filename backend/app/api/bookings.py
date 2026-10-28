import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.core.database import get_db
from app.models.models import Booking, BookingStatus, User, Trip
from app.api.auth import get_current_user_optional
from app.agent.tools.registry import tool_registry
from app.services.payment_service import payment_service

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

class RestaurantBookingRequest(BaseModel):
    trip_id: int
    restaurant_name: str
    city: str
    date: str
    time: str
    price: float
    guests: int = 1

@router.post("/flight")
def book_flight(req: FlightBookingRequest, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    ref = f"BK-FL-{uuid.uuid4().hex[:6].upper()}"
    booking = Booking(
        user_id=current_user.id if current_user else 1,
        trip_id=req.trip_id,
        service_name=f"Vé bay {req.airline} ({req.flight_number}): {req.origin} -> {req.destination}",
        category="flight",
        booking_reference=ref,
        price=req.price,
        status=BookingStatus.PENDING,
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
def book_hotel(req: HotelBookingRequest, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    ref = f"BK-HT-{uuid.uuid4().hex[:6].upper()}"
    booking = Booking(
        user_id=current_user.id if current_user else 1,
        trip_id=req.trip_id,
        service_name=f"Khách sạn: {req.hotel_name} ({req.city})",
        category="hotel",
        booking_reference=ref,
        price=req.price,
        status=BookingStatus.PENDING,
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
def book_activity(req: ActivityBookingRequest, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    ref = f"BK-ACT-{uuid.uuid4().hex[:6].upper()}"
    booking = Booking(
        user_id=current_user.id if current_user else 1,
        trip_id=req.trip_id,
        service_name=f"Tour / Hoạt động: {req.activity_name}",
        category="activity",
        booking_reference=ref,
        price=req.price,
        status=BookingStatus.PENDING,
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

@router.post("/restaurant")
def book_restaurant(req: RestaurantBookingRequest, current_user: User = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    ref = f"BK-RES-{uuid.uuid4().hex[:6].upper()}"
    booking = Booking(
        user_id=current_user.id if current_user else 1,
        trip_id=req.trip_id,
        service_name=f"Nhà hàng: {req.restaurant_name} ({req.city})",
        category="restaurant",
        booking_reference=ref,
        price=req.price,
        status=BookingStatus.PENDING,
        details={
            "restaurant_name": req.restaurant_name,
            "city": req.city,
            "date": req.date,
            "time": req.time,
            "guests": req.guests
        }
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Đặt bàn nhà hàng thành công!", "booking": booking}

@router.get("/recommendations")
def get_booking_recommendations(
    destination: str = Query("Tokyo, Nhật Bản"),
    origin: str = Query("TP. Hồ Chí Minh, Việt Nam"),
    trip_id: Optional[int] = 1
):
    """
    Returns curated hotel, flight, activity, and restaurant options for the user to browse and 1-click book.
    """
    city_village = destination.split(",")[0].strip() if "," in destination else destination

    flights = tool_registry.flight_tool.search_flights(origin=origin, destination=destination, travelers=2)
    hotels = tool_registry.hotel_tool.search_hotels(city=city_village)
    activities = tool_registry.activity_tool.search_activities(city=city_village)
    restaurants = tool_registry.restaurant_tool.search_restaurants(city=city_village)

    return {
        "destination": destination,
        "origin": origin,
        "trip_id": trip_id,
        "recommended_hotels": hotels[:3],
        "recommended_flights": flights[:3],
        "recommended_activities": activities[:4],
        "recommended_restaurants": restaurants[:4],
        "notice": "Dịch vụ được chọn lọc dựa trên vị trí trung tâm, đánh giá cao (>4.5 sao) và mức giá tối ưu."
    }

@router.get("/")
def get_all_bookings(
    trip_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Booking)
    if trip_id:
        query = query.filter(Booking.trip_id == trip_id)
    return query.order_by(Booking.booking_date.desc()).offset(skip).limit(limit).all()

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


class CheckoutRequest(BaseModel):
    booking_id: Optional[int] = None
    booking_ids: Optional[List[int]] = None
    trip_id: Optional[int] = None
    payment_method: str = "VNPAY"  # VNPAY, MOMO, STRIPE, CREDIT_CARD
    card_number: Optional[str] = None
    card_holder: Optional[str] = None
    card_expiry: Optional[str] = None
    phone_number: Optional[str] = None
    return_url: Optional[str] = None

@router.post("/checkout")
@router.post("/{booking_id}/checkout")
def checkout_and_pay(
    booking_id: Optional[int] = None,
    req: Optional[CheckoutRequest] = None,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Simulated Gateway Checkout & Instant Ticket / Voucher Issuance:
    Supports VNPay, MoMo, Stripe, and Credit Cards.
    Marks bookings as CONFIRMED, records transaction ID, and generates electronic QR voucher.
    """
    req_booking_id = booking_id or (req.booking_id if req else None)
    bookings_to_pay: List[Booking] = []

    if req_booking_id:
        b = db.query(Booking).filter(Booking.id == req_booking_id).first()
        if not b:
            raise HTTPException(status_code=404, detail=f"Booking ID {req_booking_id} không tồn tại")
        bookings_to_pay.append(b)
    elif req and req.booking_ids:
        bookings_to_pay = db.query(Booking).filter(Booking.id.in_(req.booking_ids)).all()
    elif req and req.trip_id:
        bookings_to_pay = db.query(Booking).filter(
            Booking.trip_id == req.trip_id,
            Booking.status == BookingStatus.PENDING
        ).all()

    if not bookings_to_pay:
        raise HTTPException(status_code=400, detail="Không tìm thấy dịch vụ nào cần thanh toán.")

    method = (req.payment_method if req else "VNPAY").upper()
    try:
        checkout = payment_service.start_checkout(
            bookings_to_pay, method, req.return_url if req else None
        )
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # Real gateways only create a session here. A verified webhook is required
    # before a live booking can leave PENDING.
    if checkout["mode"] == "live":
        for booking in bookings_to_pay:
            details = dict(booking.details or {})
            details["payment"] = {
                "transaction_id": checkout["transaction_id"],
                "method": checkout["provider"],
                "status": "PENDING_GATEWAY_CONFIRMATION",
                "provider_session_id": checkout.get("provider_session_id"),
            }
            booking.details = details
            booking.payment_provider = checkout["provider"]
            booking.payment_transaction_id = checkout["transaction_id"]
        db.commit()
        return {
            "success": True, "status": "PENDING", "mode": "live",
            "transaction_id": checkout["transaction_id"],
            "payment_method": checkout["provider"], "total_amount": checkout["amount"],
            "currency": "VND", "checkout_url": checkout["checkout_url"],
            "message": "Payment session created; booking stays pending until the gateway confirms it.",
        }

    # Explicit development sandbox: useful for local demos, never advertised
    # as a provider payment. It emulates a verified event and issues a QR code.
    timestamp = datetime.utcnow()
    voucher_code = checkout["voucher_code"]
    receipt_items = []
    for booking in bookings_to_pay:
        booking.status = BookingStatus.CONFIRMED
        booking.payment_provider = checkout["provider"]
        booking.payment_transaction_id = checkout["transaction_id"]
        booking.paid_at = timestamp
        booking.voucher_code = voucher_code
        details = dict(booking.details or {})
        details["payment"] = {
            "transaction_id": checkout["transaction_id"], "method": checkout["provider"],
            "paid_at": timestamp.isoformat(), "amount": booking.price,
            "voucher_code": voucher_code, "mode": "sandbox",
        }
        booking.details = details
        receipt_items.append({"booking_id": booking.id, "service_name": booking.service_name, "category": booking.category, "price": booking.price, "reference": booking.booking_reference})
    db.commit()
    qr_image_url = f"https://img.vietqr.io/image/970422-190365789123-compact2.png?amount={int(checkout['amount'])}&addInfo={checkout['transaction_id']}&accountName=AI%20TRAVEL%20AGENT"
    return {
        "success": True, "status": "CONFIRMED", "mode": "sandbox",
        "transaction_id": checkout["transaction_id"], "payment_method": checkout["provider"],
        "total_amount": checkout["amount"], "currency": "VND", "paid_at": timestamp.isoformat(),
        "voucher_code": voucher_code, "qr_code_url": qr_image_url,
        "confirmed_items_count": len(bookings_to_pay), "receipt_items": receipt_items,
        "message": "Sandbox payment confirmed; no live gateway charge was made.",
    }
    total_amount = sum(b.price for b in bookings_to_pay)
    txn_id = f"TXN-{method}-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.utcnow().isoformat()
    qr_voucher_code = f"VOUCHER-{uuid.uuid4().hex[:10].upper()}"

    # VietQR / Payment QR link
    clean_amount = int(total_amount)
    qr_image_url = f"https://img.vietqr.io/image/970422-190365789123-compact2.png?amount={clean_amount}&addInfo={txn_id}&accountName=AI%20TRAVEL%20AGENT"

    receipt_items = []
    for b in bookings_to_pay:
        b.status = BookingStatus.CONFIRMED
        details = dict(b.details or {})
        details["payment"] = {
            "transaction_id": txn_id,
            "method": method,
            "paid_at": timestamp,
            "amount": b.price,
            "voucher_code": qr_voucher_code,
            "card_last4": req.card_number[-4:] if req and req.card_number and len(req.card_number) >= 4 else "8888"
        }
        b.details = details
        receipt_items.append({
            "booking_id": b.id,
            "service_name": b.service_name,
            "category": b.category,
            "price": b.price,
            "reference": b.booking_reference
        })

    db.commit()

    return {
        "success": True,
        "message": f"Thanh toán thành công qua cổng {method}! Toàn bộ vé và phòng đã được xác nhận.",
        "transaction_id": txn_id,
        "payment_method": method,
        "total_amount": total_amount,
        "currency": "VND",
        "paid_at": timestamp,
        "voucher_code": qr_voucher_code,
        "qr_code_url": qr_image_url,
        "confirmed_items_count": len(bookings_to_pay),
        "receipt_items": receipt_items,
        "status": "CONFIRMED"
    }


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Settle a Stripe checkout only after validating its signed event."""
    body = await request.body()
    signature = request.headers.get("stripe-signature", "")
    if not payment_service.verify_stripe_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature")
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid webhook payload") from exc
    if payload.get("type") != "checkout.session.completed":
        return {"received": True, "updated": 0}

    session = payload.get("data", {}).get("object", {})
    metadata = session.get("metadata", {})
    transaction_id = metadata.get("transaction_id")
    booking_ids = [int(value) for value in metadata.get("booking_ids", "").split(",") if value.isdigit()]
    if not transaction_id or not booking_ids:
        raise HTTPException(status_code=400, detail="Webhook is missing travel booking metadata")

    bookings = db.query(Booking).filter(Booking.id.in_(booking_ids)).all()
    now = datetime.utcnow()
    voucher_code = f"VOUCHER-{uuid.uuid4().hex[:10].upper()}"
    for booking in bookings:
        booking.status = BookingStatus.PAID
        booking.payment_provider = "STRIPE"
        booking.payment_transaction_id = transaction_id
        booking.paid_at = now
        booking.voucher_code = voucher_code
        details = dict(booking.details or {})
        details["payment"] = {
            "transaction_id": transaction_id, "method": "STRIPE", "paid_at": now.isoformat(),
            "voucher_code": voucher_code, "provider_session_id": session.get("id"), "status": "PAID",
        }
        booking.details = details
    db.commit()
    return {"received": True, "updated": len(bookings), "status": "PAID"}
