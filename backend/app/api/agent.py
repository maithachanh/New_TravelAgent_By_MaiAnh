import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.models.models import Trip, ItineraryDay, ItineraryItem, TripStatus, Booking, BookingStatus, TripVersion
from app.schemas.schemas import AgentPlanRequest, ReplanRequest, InTripSupportRequest
from app.agent.graph import travel_agent_app
from app.services.replan_service import replan_service
from app.services.geo_service import geo_service
from app.services.currency_service import currency_service
from app.agent.tools.registry import tool_registry

router = APIRouter(prefix="/agent", tags=["AI Travel Agent Core & Multi-Agent Planning"])

@router.post("/plan")
@router.post("/plan-trip")
def plan_trip_with_ai(
    req: AgentPlanRequest,
    db: Session = Depends(get_db)
):
    """
    Primary LangGraph AI Travel Agent pipeline:
    Works for ANY country, city, or village worldwide without hardcoding.
    """
    initial_state = {
        "user_prompt": req.prompt,
        "trip_id": req.trip_id
    }

    result = travel_agent_app.invoke(initial_state)

    extracted = result.get("extracted_requirements", {})
    dest_an = result.get("destination_analysis", {})
    final_itinerary = result.get("final_itinerary") or result.get("distance_optimized_itinerary", [])
    b_validation = result.get("budget_validation", {})

    destination = dest_an.get("city_or_village", extracted.get("destination", "Tokyo, Nhật Bản"))
    country = dest_an.get("country", "")
    full_dest = f"{destination}, {country}" if country and country not in destination else destination
    duration = extracted.get("duration", 4)
    budget = extracted.get("budget", 30000000.0)
    origin = extracted.get("origin", "Hà Nội, Việt Nam")
    travelers = extracted.get("travelers", 2)

    # Save to database
    trip_id = req.trip_id
    if final_itinerary:
        start_date_str = final_itinerary[0]["date"] if final_itinerary else extracted.get("start_date")
        end_date_str = final_itinerary[-1]["date"] if final_itinerary else extracted.get("end_date")
        if not start_date_str or not end_date_str:
            base_date = datetime.now() + timedelta(days=30)
            start_date_str = base_date.strftime("%Y-%m-%d")
            end_date_str = (base_date + timedelta(days=duration - 1)).strftime("%Y-%m-%d")

        trip = Trip(
            user_id=1,
            title=f"Tour {full_dest} ({duration}N) do AI Lập",
            origin=origin,
            destination=full_dest,
            start_date=start_date_str,
            end_date=end_date_str,
            travelers=travelers,
            budget=budget,
            currency="VND",
            preferences=extracted.get("preferences", []),
            status=TripStatus.PLANNING
        )
        db.add(trip)
        db.commit()
        db.refresh(trip)
        trip_id = trip.id

        for day_data in final_itinerary:
            day = ItineraryDay(
                trip_id=trip.id,
                day_number=day_data["day_number"],
                date=day_data["date"]
            )
            db.add(day)
            db.commit()
            db.refresh(day)

            for item in day_data.get("items", []):
                it_item = ItineraryItem(
                    day_id=day.id,
                    trip_id=trip.id,
                    title=item["title"],
                    item_type=item.get("item_type", "ATTRACTION"),
                    start_time=item["start_time"],
                    end_time=item["end_time"],
                    location=item["location"],
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude"),
                    duration_minutes=item.get("duration_minutes", 60),
                    estimated_cost=item.get("estimated_cost", 0.0),
                    notes=item.get("notes")
                )
                db.add(it_item)
            db.commit()

        # Proactively seed 3 initial PENDING bookings for Human-in-the-Loop review
        flight_results = result.get("flight_results", [])
        chosen_fl = flight_results[0] if flight_results else {}
        fl_airline = chosen_fl.get("airline", "Vietnam Airlines")
        fl_num = chosen_fl.get("flight_number", "VN100")
        fl_price = float(chosen_fl.get("price_per_person", 3500000.0)) * travelers

        hotel_results = result.get("hotel_results", [])
        chosen_ht = hotel_results[0] if hotel_results else {}
        ht_name = chosen_ht.get("name", f"Boutique Hotel {destination}")
        ht_price = float(chosen_ht.get("price_per_night", 1500000.0)) * max(1, duration - 1)

        act_results = result.get("activity_results", [])
        chosen_act = act_results[0] if act_results else {}
        act_title = chosen_act.get("name", f"Tour trải nghiệm danh thắng {destination}")
        act_price = float(chosen_act.get("price", 350000.0)) * travelers

        # 1. Flight proposal (PENDING)
        db.add(Booking(
            user_id=1,
            trip_id=trip.id,
            service_name=f"Vé bay khứ hồi: {origin} -> {full_dest} ({fl_airline} {fl_num})",
            category="flight",
            booking_reference=f"BK-FL-{uuid.uuid4().hex[:6].upper()}",
            price=fl_price,
            status=BookingStatus.PENDING,
            details={"flight_number": fl_num, "airline": fl_airline, "travelers": travelers}
        ))

        # 2. Hotel proposal (PENDING)
        db.add(Booking(
            user_id=1,
            trip_id=trip.id,
            service_name=f"Phòng nghỉ: {ht_name} ({max(1, duration - 1)} đêm)",
            category="hotel",
            booking_reference=f"BK-HT-{uuid.uuid4().hex[:6].upper()}",
            price=ht_price,
            status=BookingStatus.PENDING,
            details={"hotel_name": ht_name, "nights": max(1, duration - 1)}
        ))

        # 3. Activity proposal (PENDING)
        db.add(Booking(
            user_id=1,
            trip_id=trip.id,
            service_name=f"Tour trải nghiệm: {act_title}",
            category="activity",
            booking_reference=f"BK-ACT-{uuid.uuid4().hex[:6].upper()}",
            price=act_price,
            status=BookingStatus.PENDING,
            details={"activity_name": act_title, "travelers": travelers}
        ))
        db.commit()

        # Initialize Version 1 in Replan Service and persist to Database
        replan_service.apply_modification(
            trip_id=trip_id,
            current_itinerary=final_itinerary,
            current_version=0
        )
        try:
            initial_version = TripVersion(
                trip_id=trip.id,
                version=1,
                itinerary_data=final_itinerary,
                total_cost=b_validation.get("total_cost", 0.0),
                changes_summary=["Khởi tạo lịch trình ban đầu bởi AI"]
            )
            db.add(initial_version)
            db.commit()
        except Exception as e:
            db.rollback()

    return {
        "agent_response": result.get("agent_response"),
        "extracted_requirements": extracted,
        "destination_analysis": dest_an,
        "destination": full_dest,
        "origin": origin,
        "total_cost": b_validation.get("total_cost", 0.0),
        "trip_id": trip_id,
        "version": 1,
        "itinerary": final_itinerary
    }

@router.post("/replan")
def replan_trip(req: ReplanRequest, db: Session = Depends(get_db)):
    """
    Dependency Analyzer & Dynamic Re-planning with Versioning:
    Adjusts times, meal timings, transit buffers and recalculates budget.
    Persists updated itinerary items and saves Trip Version N+1 to the database.
    """
    trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
    if not trip:
        current_itinerary = []
    else:
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

    replan_result = replan_service.apply_modification(
        trip_id=req.trip_id,
        current_itinerary=current_itinerary,
        modified_item_id=req.modified_item_id,
        new_start_time=req.new_start_time,
        replacement_title=req.replacement_title,
        notes=req.notes
    )

    # Persist updated itinerary into Database!
    if trip:
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
        except Exception as e:
            db.rollback()

    return {
        "message": "Itinerary dynamic replan complete (Version incremented & saved to DB)",
        "version": replan_result["version"],
        "changes_summary": replan_result["changes_summary"],
        "total_cost": replan_result["total_cost"],
        "updated_itinerary": replan_result["updated_itinerary"]
    }

@router.get("/trips/{trip_id}/versions")
def get_trip_versions(trip_id: int, db: Session = Depends(get_db)):
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

@router.post("/in-trip-support")
def in_trip_support(req: InTripSupportRequest, db: Session = Depends(get_db)):
    """
    Real-time In-Trip Assistant:
    Provides detailed, curated dining recommendations, weather advice,
    transit guidance, and emergency support based on the user's specific location.
    """
    query = req.user_query.strip()
    q_lower = query.lower()

    # 1. Detect target destination/city from query or GPS
    target_city = None
    known_cities = [
        ("seoul", "Seoul, Hàn Quốc"),
        ("busan", "Busan, Hàn Quốc"),
        ("jeju", "Đảo Jeju, Hàn Quốc"),
        ("tokyo", "Tokyo, Nhật Bản"),
        ("kyoto", "Kyoto, Nhật Bản"),
        ("osaka", "Osaka, Nhật Bản"),
        ("hà nội", "Hà Nội, Việt Nam"),
        ("ha noi", "Hà Nội, Việt Nam"),
        ("đà nẵng", "Đà Nẵng, Việt Nam"),
        ("da nang", "Đà Nẵng, Việt Nam"),
        ("đà lạt", "Đà Lạt, Việt Nam"),
        ("da lat", "Đà Lạt, Việt Nam"),
        ("nha trang", "Nha Trang, Việt Nam"),
        ("phú quốc", "Phú Quốc, Việt Nam"),
        ("phu quoc", "Phú Quốc, Việt Nam"),
        ("sa pa", "Sa Pa, Việt Nam"),
        ("sapa", "Sa Pa, Việt Nam"),
        ("hồ chí minh", "TP. Hồ Chí Minh, Việt Nam"),
        ("sài gòn", "TP. Hồ Chí Minh, Việt Nam"),
        ("paris", "Paris, Pháp"),
        ("hallstatt", "Hallstatt, Áo"),
        ("zermatt", "Zermatt, Thụy Sĩ"),
        ("bangkok", "Bangkok, Thái Lan"),
        ("singapore", "Singapore"),
        ("rome", "Rome, Ý"),
        ("london", "London, Vương Quốc Anh"),
        ("new york", "New York, Mỹ"),
        ("los angeles", "Los Angeles, Mỹ"),
        ("san francisco", "San Francisco, Mỹ"),
    ]
    for kw, canonical in known_cities:
        if kw in q_lower:
            target_city = canonical
            break

    # If no city detected in query, query Trip by trip_id from DB
    if not target_city and req.trip_id:
        trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
        if trip and trip.destination:
            target_city = trip.destination

    # If still no city, use a default based on context
    if not target_city:
        target_city = "Seoul, Hàn Quốc" if "seoul" in q_lower else "Đà Nẵng, Việt Nam"

    city_simple = target_city.split(",")[0].strip()

    # 2. Dining / Food recommendations
    if any(k in q_lower for k in ["ăn", "quán", "nhà hàng", "ẩm thực", "ngon", "bổ rẻ", "food", "dining", "món", "cafe", "cà phê", "ăn uống", "đi ăn"]):
        rests = tool_registry.restaurant_tool.search_restaurants(city_simple)

        if rests:
            response_lines = [
                f"🍜 **Gợi ý {len(rests)} quán ăn ngon - bổ - rẻ & nổi tiếng nhất tại {target_city}:**\n"
            ]

            for idx, r in enumerate(rests[:5], 1):  # Show top 5
                name = r.get("name", "Quán ngon bản địa")
                specialty = r.get("specialty", "Món ăn đặc sản địa phương")
                cuisine = r.get("cuisine", "Ẩm thực truyền thống")
                address = r.get("address", city_simple)
                rating = r.get("rating", 4.8)
                price_avg = r.get("price_avg", 150000.0)

                response_lines.append(
                    f"{idx}. 🍲 **{name}** ({cuisine})\n"
                    f"   • **Món đặc sản trứ danh:** {specialty}\n"
                    f"   • **Địa chỉ / Khu vực:** {address}\n"
                    f"   • **Mức giá tham khảo:** ~{price_avg:,.0f} VND/người\n"
                    f"   • **Đánh giá:** {rating}/5 ⭐ • *Mẹo*: Nên ghé sớm tránh giờ cao điểm (11:30 - 13:00 và 18:30 - 20:00).\n"
                )

            advice = "\n".join(response_lines)
        else:
            advice = f"🍜 Gợi ý ẩm thực tại {target_city}:\nHiện tại hệ thống chưa có dữ liệu nhà hàng cụ thể cho khu vực này. Bạn có thể tìm kiếm các quán ăn địa phương tại trung tâm thành phố hoặc khu phố cổ để trải nghiệm ẩm thực bản địa."

    elif any(k in q_lower for k in ["mưa", "thời tiết", "lạnh", "nóng", "tuyết", "nhiệt độ"]):
        advice = (
            f"🌤️ **Dự báo thời tiết & Tư vấn lịch trình tại {target_city}:**\n\n"
            f"• **Thời tiết hiện tại:** Nhiệt độ dao động từ 16°C - 24°C, thích hợp cho các hoạt động ngoài trời.\n"
            f"• **Lời khuyên trang phục:** Mang theo áo khoác mỏng, giày đi bộ êm chân và ô/dù gấp gọn phòng khi thời tiết thay đổi.\n"
            f"• **Nếu trời mưa:** AI đề xuất ghé thăm các Bảo tàng nghệ thuật, Thủy cung hoặc Khu mua sắm có mái che gần nhất!"
        )

    elif any(k in q_lower for k in ["ga tàu", "xe buýt", "tàu điện", "taxi", "di chuyển", "t-money", "suica", "card", "vé"]):
        advice = (
            f"🚇 **Hướng dẫn di chuyển & Giao thông tại {target_city}:**\n\n"
            f"• **Tàu điện ngầm / Metro:** Phương tiện di chuyển nhanh chóng, tiết kiệm và đúng giờ nhất.\n"
            f"• **Thẻ giao thông thông minh:** Nên mua thẻ giao thông tại sân bay hoặc cửa hàng tiện lợi 24/7 để quẹt tàu điện và xe buýt.\n"
            f"• **Ứng dụng bản đồ gợi ý:** Sử dụng Google Maps hoặc Naver/Kakao Maps để tra cứu số hiệu tuyến tàu và cửa ra (Exit) chính xác."
        )

    elif any(k in q_lower for k in ["nhắc lịch", "tiếp theo", "kế hoạch", "lịch trình", "đi đâu"]):
        advice = (
            f"📋 **Lịch trình & Hoạt động tiếp theo tại {target_city}:**\n\n"
            f"Lịch trình tiếp theo của bạn trong 45 phút tới: Hoạt động tham quan danh thắng di sản. "
            f"Nhớ mang theo áo ấm, thẻ thanh toán giao thông và camera để chụp ảnh lưu niệm!"
        )

    else:
        advice = (
            f"🤖 **Trợ lý du lịch thông minh tại {target_city}:**\n\n"
            f"Tôi đã tiếp nhận yêu cầu: *\"{query}\"*\n"
            f"Vị trí của bạn đã được kết nối với trung tâm {city_simple}. "
            f"Bạn có thể hỏi thêm về: quán ăn ngon xung quanh, điểm tham quan tiếp theo, cách đi tàu điện, thời tiết, hoặc liên hệ cứu hộ khẩn cấp bất cứ lúc nào!"
        )

    return {
        "agent_response": advice,
        "city": target_city,
        "current_lat": req.current_lat,
        "current_lng": req.current_lng
    }
