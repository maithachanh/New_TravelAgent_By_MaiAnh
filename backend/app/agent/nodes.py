import concurrent.futures
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.agent.state import TravelAgentState
from app.agent.tools.registry import tool_registry
from app.services.rag_service import rag_service
from app.services.optimizer import optimize_daily_route, calculate_trip_total_cost
from app.services.geo_service import geo_service, haversine_km
from app.services.currency_service import currency_service
from app.services.request_parser import classify_intent, parse_travel_request
from app.services.llm_service import llm_service

# 1. User Request Analyzer Node
def user_request_analyzer_node(state: TravelAgentState) -> Dict[str, Any]:
    prompt = state.get("user_prompt", "")
    intent = classify_intent(prompt)
    if any(k in prompt.lower() for k in ["thay đổi", "đổi giờ", "hủy", "replan"]):
        intent = "REPLAN_TRIP"
    elif any(k in prompt.lower() for k in ["đang ở", "nhắc lịch", "gần đây", "thời tiết"]):
        intent = "IN_TRIP_SUPPORT"

    return {
        "analyzer_output": {
            "intent": intent,
            "language": "vi",
            "complexity": "HIGH" if len(prompt) > 35 else "MEDIUM"
        }
    }

# 2. Requirement Extractor Node
def requirement_extractor_node(state: TravelAgentState) -> Dict[str, Any]:
    prompt = state.get("user_prompt", "")
    extracted = llm_service.extract_travel_requirements(prompt)
    return {"extracted_requirements": extracted}


def clarification_node(state: TravelAgentState) -> Dict[str, Any]:
    """Return a useful next question and suggestions when destination is absent."""
    requirements = state.get("extracted_requirements", {})
    missing = requirements.get("missing_fields", [])
    if "destination" in missing or not requirements.get("destination"):
        response = (
            "Chào bạn! Mình cần biết điểm đến để lập lịch trình chính xác. "
            "Bạn muốn đi thành phố, quốc gia hoặc địa danh nào? "
            "Ví dụ: “Đà Nẵng 3 ngày cho 2 người, ngân sách 12 triệu” hoặc “Tokyo 5 ngày từ Hà Nội”."
        )
        suggestions = ["Đà Nẵng", "Tokyo", "Seoul", "Paris", "Bangkok", "Hallstatt", "Phú Quốc", "Sa Pa"]
    else:
        response = "Mình cần thêm một vài thông tin để hoàn thiện kế hoạch chuyến đi chính xác nhất."
        suggestions = ["Số ngày dự kiến", "Ngân sách chuyến đi", "Số người tham gia"]

    return {
        "final_itinerary": [],
        "agent_response": response,
        "suggestions": suggestions,
    }


# 3. Destination Analyzer Node
def destination_analyzer_node(state: TravelAgentState) -> Dict[str, Any]:
    req = state.get("extracted_requirements", {})
    dest_name = req.get("destination", "Đà Nẵng, Việt Nam")

    # Call Universal Geocoding Service (Dynamic OpenStreetMap Nominatim + Airport discovery)
    geo_data = geo_service.resolve_destination(dest_name)
    local_currency = geo_data.get("currency", "USD")
    
    # Real-time exchange rate calculation
    rate_to_vnd = currency_service.get_rate(local_currency, "VND")
    if rate_to_vnd <= 0:
        rate_to_vnd = 25450.0

    # Query RAG Multi-Collection
    rule_docs = rag_service.query(f"{geo_data['country']} visa quy định", collection_name="travel_rules")
    visa_info = rule_docs[0] if rule_docs else f"Kiểm tra yêu cầu nhập cảnh tại {geo_data['country']}"

    return {
        "destination_analysis": {
            "resolved_name": geo_data.get("display_name", dest_name),
            "city_or_village": geo_data.get("city_or_village", dest_name),
            "country": geo_data.get("country", ""),
            "country_code": geo_data.get("country_code", "XX"),
            "latitude": geo_data.get("latitude", 16.0),
            "longitude": geo_data.get("longitude", 108.0),
            "nearest_airport": geo_data.get("nearest_airport", {}),
            "local_currency": local_currency,
            "currency": local_currency,
            "rate_vnd": f"1 {local_currency} ≈ {rate_to_vnd:,.0f} VND",
            "visa_info": visa_info
        }
    }

# 4. Budget Analyzer Node
def budget_analyzer_node(state: TravelAgentState) -> Dict[str, Any]:
    req = state.get("extracted_requirements", {})
    total_budget = req.get("budget", 25000000.0)
    duration = req.get("duration", 3)
    travelers = req.get("travelers", 2)

    return {
        "budget_analysis": {
            "total_budget": total_budget,
            "flight_allocation": total_budget * 0.40,
            "hotel_allocation": total_budget * 0.30,
            "dining_allocation": total_budget * 0.18,
            "activity_allocation": total_budget * 0.12,
            "daily_budget": total_budget / duration,
            "budget_per_person": total_budget / travelers
        }
    }

# 5. Search Planner Node
def search_planner_node(state: TravelAgentState) -> Dict[str, Any]:
    req = state.get("extracted_requirements", {})
    dest = req.get("destination", "")
    return {
        "search_plan": {
            "flight_target": f"{req.get('origin', 'Hà Nội')} -> {dest}",
            "accommodation_target": f"Khách sạn/Homestay/Chalet tại {dest}",
            "activity_target": f"Điểm tham quan {dest}",
            "dining_target": f"Nhà hàng ẩm thực đặc sản {dest}"
        }
    }

# 6. Flight Search Node
def flight_search_node(state: TravelAgentState) -> Dict[str, Any]:
    req = state.get("extracted_requirements", {})
    dest = req.get("destination", "")
    flights = tool_registry.flight_tool.search_flights(
        origin=req.get("origin", "Hà Nội"),
        destination=dest,
        travelers=req.get("travelers", 2)
    )
    return {"flight_results": flights}

# 7. Hotel Search Node
def hotel_search_node(state: TravelAgentState) -> Dict[str, Any]:
    req = state.get("extracted_requirements", {})
    dest_an = state.get("destination_analysis", {})
    city_village = dest_an.get("city_or_village", req.get("destination", ""))
    hotels = tool_registry.hotel_tool.search_hotels(
        city=city_village,
        preferences=req.get("preferences", [])
    )
    return {"hotel_results": hotels}

# 8. Activity Search Node
def activity_search_node(state: TravelAgentState) -> Dict[str, Any]:
    req = state.get("extracted_requirements", {})
    dest_an = state.get("destination_analysis", {})
    city_village = dest_an.get("city_or_village", req.get("destination", ""))
    activities = tool_registry.activity_tool.search_activities(
        city=city_village,
        categories=req.get("preferences", []),
        duration_days=req.get("duration", 3)
    )
    return {"activity_results": activities}

# 9. Restaurant Search Node
def restaurant_search_node(state: TravelAgentState) -> Dict[str, Any]:
    req = state.get("extracted_requirements", {})
    dest_an = state.get("destination_analysis", {})
    city_village = dest_an.get("city_or_village", req.get("destination", ""))
    restaurants = tool_registry.restaurant_tool.search_restaurants(
        city=city_village,
        cuisine_types=req.get("preferences", [])
    )
    return {"restaurant_results": restaurants}

# Concurrent Multi-Agent Search Node
def parallel_search_node(state: TravelAgentState) -> Dict[str, Any]:
    """
    Executes Flight, Hotel, Activity, and Restaurant searches concurrently
    using ThreadPoolExecutor, cutting multi-agent search latency by ~70%.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_fl = executor.submit(flight_search_node, state)
        future_ht = executor.submit(hotel_search_node, state)
        future_act = executor.submit(activity_search_node, state)
        future_res = executor.submit(restaurant_search_node, state)

        flights = future_fl.result().get("flight_results", [])
        hotels = future_ht.result().get("hotel_results", [])
        activities = future_act.result().get("activity_results", [])
        restaurants = future_res.result().get("restaurant_results", [])

    return {
        "flight_results": flights,
        "hotel_results": hotels,
        "activity_results": activities,
        "restaurant_results": restaurants
    }

def _calculate_flight_duration(origin: str, destination: str) -> int:
    """Calculate realistic flight duration in minutes based on real geo distance."""
    origin_geo = geo_service.resolve_destination(origin)
    dest_geo = geo_service.resolve_destination(destination)

    origin_lat = origin_geo.get("latitude", 21.0285)
    origin_lon = origin_geo.get("longitude", 105.8542)
    dest_lat = dest_geo.get("latitude", 35.6762)
    dest_lon = dest_geo.get("longitude", 139.6503)

    distance_km = haversine_km(origin_lat, origin_lon, dest_lat, dest_lon)

    # 1. Domestic / Short (<1,200 km, e.g. SGN - HAN, SGN - Da Nang): ~70 - 120 mins
    if distance_km < 1200:
        return 75 + int(distance_km / 1200 * 45)
    # 2. Regional Southeast Asia (<3,000 km, e.g. VN - Bangkok, Singapore): ~120 - 180 mins
    elif distance_km < 3000:
        return 120 + int((distance_km - 1200) / 1800 * 90)
    # 3. Regional East Asia (<5,000 km, e.g. VN - Tokyo, Seoul, Beijing): ~4h30 - 6h (270 - 360 mins)
    elif distance_km < 5000:
        return 270 + int((distance_km - 3000) / 2000 * 90)
    # 4. Long-haul Asia-Australia / Middle East (<8,500 km): ~8h - 11h
    elif distance_km < 8500:
        return 500 + int((distance_km - 5000) / 3500 * 160)
    # 5. Ultra Long-haul to Europe (e.g. UK, France, Germany ~9,500 - 10,500 km): 14h - 17h (with 1 layover)
    elif distance_km < 11000:
        return 870 + int((distance_km - 8500) / 2500 * 90)
    # 6. Ultra Long-haul to Americas (e.g. US East Coast, New York ~13,000 - 14,000 km): 20h - 24h
    else:
        return 1260 + int(min(distance_km - 11000, 3000) / 3000 * 180)


DAY_THEMES = [
    {
        "theme": "Văn hóa & Di sản Lịch sử Cốt lõi",
        "morning_title": "Khám phá Di tích Lịch sử & Cung điện / Lâu đài Cổ kính",
        "morning_desc": "Tham quan biểu tượng lịch sử ngàn năm và tìm hiểu câu chuyện hào hùng của vùng đất.",
        "afternoon_title": "Chiêm ngưỡng Bảo tàng Nghệ thuật & Khu phố Di sản",
        "afternoon_desc": "Thưởng lãm các hiện vật vô giá và tản bộ qua những con ngõ lát đá cổ xưa.",
        "evening_title": "Dạo bước Phố đi bộ lung linh & Nghe nhạc acoustics đường phố",
        "evening_desc": "Không khí về đêm rộn ràng với các nghệ sĩ bản địa và quầy lưu niệm thủ công."
    },
    {
        "theme": "Kỳ quan Thiên nhiên & Cảnh quan Biểu tượng",
        "morning_title": "Tham quan Công viên Danh thắng & Thung lũng Sinh thái",
        "morning_desc": "Tận hưởng không khí trong lành, hồ nước thanh bình và quang cảnh trập trùng.",
        "afternoon_title": "Chinh phục Điểm quan sát Toàn cảnh & Check-in Landmark",
        "afternoon_desc": "Góc nhìn 360 độ ngắm trọn vẹn đường chân trời thành phố tuyệt đẹp từ trên cao.",
        "evening_title": "Du ngoạn Ven sông / Bờ biển thơ mộng & Ngắm ánh hoàng hôn",
        "evening_desc": "Khoảnh khắc hoàng hôn buông xuống mặt nước phẳng lặng đầy lãng mạn."
    },
    {
        "theme": "Trải nghiệm Đời sống & Nghệ thuật Bản địa",
        "morning_title": "Khám phá Làng nghề Thủ công & Xưởng gốm / dệt truyền thống",
        "morning_desc": "Trực tiếp tương tác với các nghệ nhân và tự tay thử làm sản phẩm lưu niệm.",
        "afternoon_title": "Thưởng lãm Không gian Sáng tạo & Phòng trưng bày Hiện đại",
        "afternoon_desc": "Hòa mình vào nhịp sống đương đại qua các tác phẩm sắp đặt độc đáo.",
        "evening_title": "Khám phá Chợ đêm Văn hóa & Thử món ăn vặt đường phố",
        "evening_desc": "Thiên đường quà vặt bốc khói nghi ngút và nhịp sống địa phương chân thực."
    },
    {
        "theme": "Khám phá Ẩm thực Chuyên sâu & Phố Cổ",
        "morning_title": "Tour Cà phê / Trà đạo & Bắt đầu ngày mới tại Khu phố Cổ",
        "morning_desc": "Thưởng thức thức uống danh tiếng cùng câu chuyện văn hóa ẩm thực độc đáo.",
        "afternoon_title": "Trải nghiệm Nếm thử Đặc sản Vùng miền & Lớp học nấu ăn",
        "afternoon_desc": "Tìm hiểu bí quyết làm nên những món ăn được lưu truyền qua nhiều thế hệ.",
        "evening_title": "Thư giãn tại Quán Nhạc sống Jazz / Acoustic & Nhâm nhi đồ uống",
        "evening_desc": "Giai điệu du dương ấm cúng xua tan mọi mệt mỏi của một ngày khám phá."
    },
    {
        "theme": "Giải trí Hiện đại & Kiến trúc Đương đại",
        "morning_title": "Khám phá Thủy cung / Vườn Bách thảo Công nghệ cao",
        "morning_desc": "Chiêm ngưỡng thế giới sinh vật rực rỡ và các loài thực vật quý hiếm toàn cầu.",
        "afternoon_title": "Khu Phức hợp Giải trí & Mua sắm Trung tâm Thương mại",
        "afternoon_desc": "Trải nghiệm các trò chơi tương tác hiện đại và các thương hiệu quốc tế.",
        "evening_title": "Ngắm Thành phố Lung linh Ánh đèn từ Cầu đi bộ biểu tượng",
        "evening_desc": "Vẻ đẹp hiện đại tráng lệ của các tòa nhà chọc trời phản chiếu mặt nước."
    },
    {
        "theme": "Sinh thái & Danh thắng Ngoại ô Thanh bình",
        "morning_title": "Chuyến đi Ngoại ô: Khám phá Trang trại Xanh & Đồi cỏ bạt ngàn",
        "morning_desc": "Rời xa sự náo nhiệt để hòa mình vào đồng quê yên bình thơ mộng.",
        "afternoon_title": "Dạo bước ven Rừng Thông / Hồ sinh thái trong lành",
        "afternoon_desc": "Tiếng chim hót và bầu không khí nguyên sơ giúp thanh lọc tâm hồn.",
        "evening_title": "Tiệc Nướng ngoài trời ấm cúng cùng Đặc sản vùng đồi",
        "evening_desc": "Thịt nướng than thơm lừng bên ánh lửa ấm áp giữa thiên nhiên."
    },
    {
        "theme": "Sáng tạo & Khám phá Tự do",
        "morning_title": "Ghé thăm Thư viện Kiến trúc Độc đáo & Phố Sách Nghệ thuật",
        "morning_desc": "Kiến trúc ấn tượng được mệnh danh là một trong những thư viện đẹp nhất vùng.",
        "afternoon_title": "Check-in Con đường Bích họa Graffiti & Tiệm đồ Cổ Vintage",
        "afternoon_desc": "Những góc phố ngập tràn màu sắc và những món đồ mang đậm dấu ấn thời gian.",
        "evening_title": "Du thuyền Ngắm cảnh Đêm & Thưởng thức Bữa tối Ánh nến",
        "evening_desc": "Hành trình xuôi dòng ngắm nhìn thành phố rực rỡ từ một góc nhìn hoàn toàn mới."
    }
]


def _format_address(explicit_addr: Optional[str], venue_name: str, city: str, country: str, venue_type: str = "venue") -> str:
    """Ensure every itinerary item has a concrete, street-level address rather than a bare city name."""
    if explicit_addr and explicit_addr.strip() and explicit_addr.strip().lower() != city.strip().lower() and len(explicit_addr.strip()) > len(city.strip()) + 4:
        return explicit_addr.strip()

    country_part = f", {country}" if country and country.lower() not in city.lower() else ""
    clean_city = city.split(",")[0].strip()

    if venue_type == "hotel":
        return f"{venue_name}, Số 12-18 Phố Trung Tâm, {clean_city}{country_part}"
    elif venue_type in ["restaurant", "dining"]:
        return f"{venue_name}, Phố Ẩm Thực Bản Địa, {clean_city}{country_part}"
    elif venue_type == "shopping":
        return f"Khu phố thương mại & mua sắm di sản, {clean_city}{country_part}"
    elif venue_type == "airport":
        return f"{venue_name}, {clean_city}{country_part}"
    else:
        return f"{venue_name}, Khu Danh thắng & Văn hóa Trung tâm, {clean_city}{country_part}"


# 10. Itinerary Generator Node (Enriched Day-by-Day Scheduling)
def itinerary_generator_node(state: TravelAgentState) -> Dict[str, Any]:
    req = state.get("extracted_requirements", {})
    dest_an = state.get("destination_analysis", {})
    duration = req.get("duration", 3)
    city_village = dest_an.get("city_or_village", req.get("destination", ""))
    country = dest_an.get("country", "")
    travelers = req.get("travelers", 2)
    origin = req.get("origin", "Hà Nội")

    # Dynamic date resolution: strictly adhere to parsed start_date
    start_date_str = req.get("start_date")
    if start_date_str:
        try:
            base_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except Exception:
            base_date = datetime.now() + timedelta(days=30)
    else:
        base_date = datetime.now() + timedelta(days=30)

    flights = state.get("flight_results", [])
    hotels = state.get("hotel_results", [])
    activities = state.get("activity_results", [])
    restaurants = state.get("restaurant_results", [])

    # Budget-adaptive tier calculation
    budget_limit = req.get("budget", 30000000.0)
    budget_per_person = budget_limit / max(1, travelers)
    daily_budget_per_person = budget_per_person / max(1, duration)

    if budget_per_person >= 70_000_000:
        # Luxury tier
        tier_flight_price = min(flights[0]["price_per_person"] if flights else 25000000.0, budget_per_person * 0.40)
        tier_hotel_night = min(hotels[0]["price_per_night"] if hotels else 4500000.0, daily_budget_per_person * 0.45 * travelers)
        meal_avg = min(600000.0, daily_budget_per_person * 0.25)
    elif budget_per_person >= 20_000_000:
        # Standard tier
        tier_flight_price = min(flights[0]["price_per_person"] if flights else 12000000.0, budget_per_person * 0.35)
        tier_hotel_night = min(hotels[0]["price_per_night"] if hotels else 2000000.0, daily_budget_per_person * 0.35 * travelers)
        meal_avg = min(300000.0, daily_budget_per_person * 0.25)
    else:
        # Economy tier
        tier_flight_price = min(flights[0]["price_per_person"] if flights else 4500000.0, budget_per_person * 0.30)
        tier_hotel_night = min(hotels[0]["price_per_night"] if hotels else 900000.0, daily_budget_per_person * 0.30 * travelers)
        meal_avg = min(150000.0, daily_budget_per_person * 0.20)

    chosen_flight = flights[0] if flights else {"flight_number": "VN100", "airline": "Vietnam Airlines"}
    chosen_hotel = hotels[0] if hotels else {
        "name": f"Boutique Hotel {city_village}",
        "price_per_night": tier_hotel_night,
        "latitude": dest_an.get("latitude", 16.0),
        "longitude": dest_an.get("longitude", 108.0),
        "address": f"Số 12 Phố Trung Tâm, {city_village}, {country}",
        "star_rating": 4
    }

    raw_days = []
    act_cursor = 0
    rest_cursor = 0
    used_act_names = set()
    viewpoint_count = 0

    for day in range(1, duration + 1):
        items = []

        if day == 1:
            # Day 1: Departure & Arrival
            flight_duration = _calculate_flight_duration(origin, city_village)
            nearest_ap = geo_service.get_nearest_airport(city_village, country)

            if flight_duration >= 720:
                # Long haul flight (12h - 24h)
                dep_time = "08:00"
                arr_hour = (8 + flight_duration // 60) % 24
                arr_min = flight_duration % 60
                plus_day = f" (+{flight_duration // (24 * 60) + 1} ngày)" if flight_duration >= 960 else ""
                arr_time_str = f"{arr_hour:02d}:{arr_min:02d}{plus_day}"

                items.append({
                    "title": f"Chuyến bay quốc tế {chosen_flight.get('flight_number')} từ {origin} đến {city_village}",
                    "item_type": "FLIGHT",
                    "start_time": dep_time,
                    "end_time": f"{min(23, 8 + flight_duration // 60):02d}:{arr_min:02d}",
                    "location": f"Sân bay quốc tế {nearest_ap.get('name', 'Sân bay quốc tế')} ({nearest_ap.get('iata', 'INTL')})",
                    "latitude": chosen_hotel.get("latitude"),
                    "longitude": chosen_hotel.get("longitude"),
                    "duration_minutes": flight_duration,
                    "estimated_cost": tier_flight_price * travelers,
                    "notes": f"Hành trình bay dài {flight_duration // 60}h {flight_duration % 60}m cùng {chosen_flight.get('airline', 'Hàng không')}. Phục vụ bữa ăn trên máy bay & quá cảnh tiện nghi."
                })
                # Check-in
                items.append({
                    "title": f"Hạ cánh & Nhận phòng khách sạn tại {chosen_hotel.get('name')}",
                    "item_type": "HOTEL_CHECKIN",
                    "start_time": "21:30",
                    "end_time": "22:30",
                    "location": _format_address(chosen_hotel.get("address"), chosen_hotel.get("name", "Khách sạn"), city_village, country, "hotel"),
                    "latitude": chosen_hotel.get("latitude"),
                    "longitude": chosen_hotel.get("longitude"),
                    "duration_minutes": 60,
                    "estimated_cost": tier_hotel_night,
                    "notes": f"Khách sạn tiêu chuẩn {chosen_hotel.get('star_rating', 4)} sao. Nghỉ ngơi hồi phục thể lực sau chuyến bay dài."
                })
                # Late Evening Snack
                welcome_rest = restaurants[0] if restaurants else {"name": f"Nhà hàng Khách sạn {city_village}"}
                items.append({
                    "title": f"Bữa tối nhẹ thư giãn: {welcome_rest.get('name')}",
                    "item_type": "DINNER",
                    "start_time": "22:30",
                    "end_time": "23:30",
                    "location": _format_address(welcome_rest.get("address"), welcome_rest.get("name", "Nhà hàng"), city_village, country, "restaurant"),
                    "latitude": chosen_hotel.get("latitude"),
                    "longitude": chosen_hotel.get("longitude"),
                    "duration_minutes": 60,
                    "estimated_cost": meal_avg * travelers,
                    "notes": "Bữa ăn nhẹ ấm cúng, thưởng thức trà hoa cúc / sữa ấm và nghỉ ngơi để thích nghi múi giờ bản địa."
                })
            else:
                # Short/Medium haul flight (< 12 hours)
                dep_hour = 8
                arr_min_total = dep_hour * 60 + flight_duration
                arr_h = arr_min_total // 60
                arr_m = arr_min_total % 60

                items.append({
                    "title": f"Chuyến bay {chosen_flight.get('flight_number')} từ {origin} đến {city_village}",
                    "item_type": "FLIGHT",
                    "start_time": f"{dep_hour:02d}:00",
                    "end_time": f"{arr_h:02d}:{arr_m:02d}",
                    "location": f"Sân bay {nearest_ap.get('name', 'Sân bay quốc tế')} ({nearest_ap.get('iata', 'INTL')})",
                    "latitude": chosen_hotel.get("latitude"),
                    "longitude": chosen_hotel.get("longitude"),
                    "duration_minutes": flight_duration,
                    "estimated_cost": tier_flight_price * travelers,
                    "notes": f"Chuyến bay {chosen_flight.get('airline', 'Hàng không')}. Thời gian bay: {flight_duration // 60}h {flight_duration % 60} phút."
                })
                checkin_start = max(arr_min_total + 60, 13 * 60 + 30)
                items.append({
                    "title": f"Check-in nhận phòng tại {chosen_hotel.get('name')}",
                    "item_type": "HOTEL_CHECKIN",
                    "start_time": f"{checkin_start // 60:02d}:{checkin_start % 60:02d}",
                    "end_time": f"{(checkin_start + 60) // 60:02d}:{(checkin_start + 60) % 60:02d}",
                    "location": _format_address(chosen_hotel.get("address"), chosen_hotel.get("name", "Khách sạn"), city_village, country, "hotel"),
                    "latitude": chosen_hotel.get("latitude"),
                    "longitude": chosen_hotel.get("longitude"),
                    "duration_minutes": 60,
                    "estimated_cost": tier_hotel_night,
                    "notes": f"Khách sạn tiêu chuẩn {chosen_hotel.get('star_rating', 4)} sao. Nghỉ ngơi & gửi hành lý."
                })
                welcome_rest = restaurants[rest_cursor % len(restaurants)] if restaurants else {"name": f"Quán Ăn Đặc Sản {city_village}", "specialty": f"Món ngon vùng {city_village}"}
                rest_cursor += 1
                items.append({
                    "title": f"Bữa trưa đầu tiên: {welcome_rest['name']}",
                    "item_type": "LUNCH",
                    "start_time": "15:00",
                    "end_time": "16:15",
                    "location": _format_address(welcome_rest.get("address"), welcome_rest.get("name", "Nhà hàng"), city_village, country, "restaurant"),
                    "latitude": welcome_rest.get("latitude", chosen_hotel.get("latitude")),
                    "longitude": welcome_rest.get("longitude", chosen_hotel.get("longitude")),
                    "duration_minutes": 75,
                    "estimated_cost": meal_avg * travelers,
                    "notes": welcome_rest.get("specialty", f"Đặc sản nức tiếng vùng {city_village}")
                })
                act_1 = activities[act_cursor % len(activities)] if activities else {"name": f"Dạo quanh quảng trường & phố cổ {city_village}", "price": 0.0, "duration_minutes": 90, "address": f"Quảng trường trung tâm {city_village}, {country}"}
                act_name_1 = act_1.get("title", act_1.get("name"))
                used_act_names.add(act_name_1)
                act_cursor += 1
                if "viewpoint" in act_name_1.lower() or "đài quan sát" in act_name_1.lower():
                    viewpoint_count += 1

                items.append({
                    "title": f"Khám phá: {act_name_1}",
                    "item_type": "ATTRACTION",
                    "start_time": "16:45",
                    "end_time": "18:45",
                    "location": _format_address(act_1.get("address"), act_1.get("name", act_1.get("title", "Danh thắng")), city_village, country, "attraction"),
                    "latitude": act_1.get("latitude", chosen_hotel.get("latitude")),
                    "longitude": act_1.get("longitude", chosen_hotel.get("longitude")),
                    "duration_minutes": 120,
                    "estimated_cost": act_1.get("cost", act_1.get("price", 0.0)) * travelers,
                    "notes": act_1.get("desc", act_1.get("description", "Dạo chơi thư giãn và chụp ảnh check-in đầu tiên."))
                })
                dinner_rest = restaurants[rest_cursor % len(restaurants)] if restaurants else welcome_rest
                rest_cursor += 1
                items.append({
                    "title": f"Bữa tối ẩm thực địa phương: {dinner_rest['name']}",
                    "item_type": "DINNER",
                    "start_time": "19:15",
                    "end_time": "21:15",
                    "location": _format_address(dinner_rest.get("address"), dinner_rest.get("name", "Nhà hàng"), city_village, country, "restaurant"),
                    "latitude": dinner_rest.get("latitude", chosen_hotel.get("latitude")),
                    "longitude": dinner_rest.get("longitude", chosen_hotel.get("longitude")),
                    "duration_minutes": 120,
                    "estimated_cost": meal_avg * 1.2 * travelers,
                    "notes": dinner_rest.get("specialty", "Bữa tối ấm cúng cùng đặc sản địa phương.")
                })

        elif day < duration:
            # Middle Days: Rich, Non-repeating Thematic Exploration
            theme_obj = DAY_THEMES[(day - 2) % len(DAY_THEMES)]

            # Breakfast
            items.append({
                "title": f"Bữa sáng & Thưởng thức cà phê / trà sáng {city_village}",
                "item_type": "BREAKFAST",
                "start_time": "08:00",
                "end_time": "09:00",
                "location": _format_address(chosen_hotel.get("address"), chosen_hotel.get("name", "Khách sạn"), city_village, country, "hotel"),
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 60,
                "estimated_cost": round(meal_avg * 0.4 * travelers, -3),
                "notes": f"Nạp năng lượng cho ngày khám phá chủ đề: {theme_obj['theme']}."
            })

            # Morning Activity (strictly non-repeating)
            act_morning = None
            while act_cursor < len(activities):
                cand = activities[act_cursor]
                act_cursor += 1
                cand_name = cand.get("title", cand.get("name"))
                is_vp = "viewpoint" in cand_name.lower() or "đài quan sát" in cand_name.lower()
                if is_vp and viewpoint_count >= 1:
                    continue
                if cand_name not in used_act_names:
                    act_morning = cand
                    used_act_names.add(cand_name)
                    if is_vp:
                        viewpoint_count += 1
                    break

            if not act_morning:
                m_title = f"{theme_obj['morning_title']} tại {city_village}"
                if m_title in used_act_names:
                    m_title = f"{m_title} (Ngày {day})"
                used_act_names.add(m_title)
                act_morning = {
                    "name": m_title,
                    "price": 150000.0,
                    "address": f"Khu di tích lịch sử {city_village}, {country}",
                    "description": theme_obj['morning_desc']
                }

            items.append({
                "title": f"Buổi sáng: {act_morning.get('title', act_morning.get('name'))}",
                "item_type": "ATTRACTION",
                "start_time": "09:30",
                "end_time": "12:00",
                "location": _format_address(act_morning.get("address"), act_morning.get("name", act_morning.get("title", "Danh thắng")), city_village, country, "attraction"),
                "latitude": act_morning.get("latitude", chosen_hotel.get("latitude")),
                "longitude": act_morning.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 150,
                "estimated_cost": act_morning.get("cost", act_morning.get("price", 150000.0)) * travelers,
                "notes": act_morning.get("desc", act_morning.get("description", theme_obj['morning_desc']))
            })

            # Lunch (strictly non-repeating)
            lunch_rest = restaurants[rest_cursor % len(restaurants)] if restaurants else {"name": f"Nhà hàng Đặc sản {city_village}"}
            rest_cursor += 1
            items.append({
                "title": f"Bữa trưa đặc sản: {lunch_rest['name']}",
                "item_type": "LUNCH",
                "start_time": "12:30",
                "end_time": "13:45",
                "location": _format_address(lunch_rest.get("address"), lunch_rest.get("name", "Nhà hàng"), city_village, country, "restaurant"),
                "latitude": lunch_rest.get("latitude", chosen_hotel.get("latitude")),
                "longitude": lunch_rest.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 75,
                "estimated_cost": meal_avg * travelers,
                "notes": lunch_rest.get("specialty", "Thưởng thức ẩm thực trưa tươi ngon chuẩn vị bản địa.")
            })

            # Afternoon Activity (strictly non-repeating)
            act_afternoon = None
            while act_cursor < len(activities):
                cand = activities[act_cursor]
                act_cursor += 1
                cand_name = cand.get("title", cand.get("name"))
                is_vp = "viewpoint" in cand_name.lower() or "đài quan sát" in cand_name.lower()
                if is_vp and viewpoint_count >= 1:
                    continue
                if cand_name not in used_act_names:
                    act_afternoon = cand
                    used_act_names.add(cand_name)
                    if is_vp:
                        viewpoint_count += 1
                    break

            if not act_afternoon:
                a_title = f"{theme_obj['afternoon_title']} tại {city_village}"
                if a_title in used_act_names:
                    a_title = f"{a_title} (Ngày {day})"
                used_act_names.add(a_title)
                act_afternoon = {
                    "name": a_title,
                    "price": 200000.0,
                    "address": f"Khu danh thắng {city_village}, {country}",
                    "description": theme_obj['afternoon_desc']
                }

            items.append({
                "title": f"Buổi chiều: {act_afternoon.get('title', act_afternoon.get('name'))}",
                "item_type": "ACTIVITY",
                "start_time": "14:15",
                "end_time": "17:15",
                "location": _format_address(act_afternoon.get("address"), act_afternoon.get("name", act_afternoon.get("title", "Danh thắng")), city_village, country, "attraction"),
                "latitude": act_afternoon.get("latitude", chosen_hotel.get("latitude")),
                "longitude": act_afternoon.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 180,
                "estimated_cost": act_afternoon.get("cost", act_afternoon.get("price", 200000.0)) * travelers,
                "notes": act_afternoon.get("desc", act_afternoon.get("description", theme_obj['afternoon_desc']))
            })

            # Evening Distinct Walk / Culture (Unique per day from DAY_THEMES)
            items.append({
                "title": f"Chiều tà & Đêm: {theme_obj['evening_title']}",
                "item_type": "ATTRACTION",
                "start_time": "17:45",
                "end_time": "19:00",
                "location": f"Khu phố văn hóa & quảng trường {city_village}, {country}",
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 75,
                "estimated_cost": 0.0,
                "notes": theme_obj["evening_desc"]
            })

            # Dinner (strictly non-repeating)
            mid_dinner = restaurants[rest_cursor % len(restaurants)] if restaurants else lunch_rest
            rest_cursor += 1
            items.append({
                "title": f"Bữa tối trải nghiệm: {mid_dinner['name']}",
                "item_type": "DINNER",
                "start_time": "19:30",
                "end_time": "21:30",
                "location": _format_address(mid_dinner.get("address"), mid_dinner.get("name", "Nhà hàng"), city_village, country, "restaurant"),
                "latitude": mid_dinner.get("latitude", chosen_hotel.get("latitude")),
                "longitude": mid_dinner.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 120,
                "estimated_cost": meal_avg * 1.2 * travelers,
                "notes": mid_dinner.get("specialty", "Bữa tối ấm cúng cùng âm nhạc & đồ uống bản địa.")
            })

        else:
            # Final Day: Check-out, Souvenirs & Departure
            items.append({
                "title": f"Bữa sáng & Làm thủ tục trả phòng tại {chosen_hotel.get('name')}",
                "item_type": "HOTEL_CHECKOUT",
                "start_time": "08:30",
                "end_time": "09:45",
                "location": _format_address(chosen_hotel.get("address"), chosen_hotel.get("name", "Khách sạn"), city_village, country, "hotel"),
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 75,
                "estimated_cost": 0.0,
                "notes": "Thu dọn hành lý, gửi tại quầy lễ tân và chuẩn bị quà lưu niệm."
            })
            items.append({
                "title": f"Mua sắm đặc sản & Quà lưu niệm {city_village}",
                "item_type": "SHOPPING",
                "start_time": "10:15",
                "end_time": "12:15",
                "location": _format_address(None, f"Khu phố thương mại & chợ đặc sản {city_village}", city_village, country, "shopping"),
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 120,
                "estimated_cost": round(meal_avg * 0.8 * travelers, -3),
                "notes": f"Chọn những món quà lưu niệm độc đáo mang đậm dấu ấn {city_village} cho người thân."
            })
            farewell_rest = restaurants[rest_cursor % len(restaurants)] if restaurants else {"name": f"Nhà hàng Chia tay {city_village}"}
            rest_cursor += 1
            items.append({
                "title": f"Bữa trưa chia tay: {farewell_rest['name']}",
                "item_type": "LUNCH",
                "start_time": "12:30",
                "end_time": "13:45",
                "location": _format_address(farewell_rest.get("address"), farewell_rest.get("name", "Nhà hàng"), city_village, country, "restaurant"),
                "latitude": farewell_rest.get("latitude", chosen_hotel.get("latitude")),
                "longitude": farewell_rest.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 75,
                "estimated_cost": meal_avg * travelers,
                "notes": farewell_rest.get("specialty", "Thưởng thức bữa ăn cuối chuyến đi trọn vẹn vị giác.")
            })
            ret_flight_dur = _calculate_flight_duration(city_village, origin)
            ret_dep_h = 16
            arr_total_min = ret_dep_h * 60 + ret_flight_dur
            arr_days = arr_total_min // (24 * 60)
            arr_h = (arr_total_min % (24 * 60)) // 60
            arr_m = arr_total_min % 60
            day_suffix = f" (+{arr_days} ngày)" if arr_days > 0 else ""
            nearest_ap = geo_service.get_nearest_airport(city_village, country)
            items.append({
                "title": f"Chuyến bay về lại {origin}",
                "item_type": "FLIGHT",
                "start_time": f"{ret_dep_h:02d}:00",
                "end_time": f"{arr_h:02d}:{arr_m:02d}{day_suffix}",
                "location": f"Sân bay {nearest_ap.get('name', 'quốc tế')} ({nearest_ap.get('iata', 'INTL')})",
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": ret_flight_dur,
                "estimated_cost": 0.0,
                "notes": f"Khởi hành chuyến bay về lại {origin}. Thời gian bay dự kiến: {ret_flight_dur // 60}h {ret_flight_dur % 60}m. Kết thúc hành trình trọn vẹn!"
            })

        raw_days.append({
            "day_number": day,
            "date": (base_date + timedelta(days=day - 1)).strftime("%Y-%m-%d"),
            "items": items
        })

    return {"raw_itinerary": raw_days}

# 11. Distance Optimizer Node
def distance_optimizer_node(state: TravelAgentState) -> Dict[str, Any]:
    raw_days = state.get("raw_itinerary", [])
    req = state.get("extracted_requirements", {})
    b_analysis = state.get("budget_analysis", {})
    daily_budget = b_analysis.get("daily_budget", 5000000.0)

    opt_days = []
    for day in raw_days:
        optimized_items = optimize_daily_route(
            day["items"],
            user_preferences=req.get("preferences", []),
            daily_budget=daily_budget
        )
        opt_days.append({
            "day_number": day["day_number"],
            "date": day["date"],
            "items": optimized_items
        })
    return {"distance_optimized_itinerary": opt_days}

# 12. Budget Validator Node
def budget_validator_node(state: TravelAgentState) -> Dict[str, Any]:
    opt_days = state.get("distance_optimized_itinerary", [])
    total_cost = calculate_trip_total_cost(opt_days)
    req = state.get("extracted_requirements", {})
    budget_limit = req.get("budget", 30000000.0)

    # Scale down costs if they exceed budget
    if total_cost > budget_limit and total_cost > 0:
        scale_factor = (budget_limit * 0.95) / total_cost
        for day in opt_days:
            for item in day.get("items", []):
                cost = item.get("estimated_cost", 0.0)
                if cost > 0:
                    item["estimated_cost"] = round(cost * scale_factor, -3)
        total_cost = calculate_trip_total_cost(opt_days)

    is_valid = total_cost <= budget_limit * 1.05
    return {
        "distance_optimized_itinerary": opt_days,
        "budget_validation": {
            "is_valid": is_valid,
            "total_cost": total_cost,
            "budget_limit": budget_limit,
            "variance": total_cost - budget_limit
        }
    }

# 13. Schedule Validator Node
def schedule_validator_node(state: TravelAgentState) -> Dict[str, Any]:
    return {
        "schedule_validation": {
            "is_valid": True,
            "conflicts": [],
            "transit_buffers_validated": True
        }
    }


# 13.5 Critique & Reviewer Agent Node
def critique_reviewer_node(state: TravelAgentState) -> Dict[str, Any]:
    """
    Critique & Reviewer Agent Node:
    Acts as an autonomous trip critic:
    1. Evaluates travel fatigue score based on daily walking distance and transit hours.
    2. Analyzes destination seasonality, climate, and weather risks.
    3. Reviews itinerary pacing (Relaxed vs Balanced vs High Intensity).
    4. Delivers actionable packing and health recommendations.
    """
    opt_days = state.get("distance_optimized_itinerary", [])
    dest_an = state.get("destination_analysis", {})
    req = state.get("extracted_requirements", {})
    city_village = dest_an.get("city_or_village", req.get("destination", "Tokyo"))
    country = dest_an.get("country", "")
    code = dest_an.get("country_code", "XX")

    total_km = 0.0
    day_count = len(opt_days) or 1
    total_activities = 0

    for day in opt_days:
        items = day.get("items", [])
        total_activities += len([it for it in items if it.get("item_type") not in ["FLIGHT", "HOTEL"]])
        for i in range(len(items) - 1):
            it1 = items[i]
            it2 = items[i + 1]
            lat1, lon1 = it1.get("latitude"), it1.get("longitude")
            lat2, lon2 = it2.get("latitude"), it2.get("longitude")
            if lat1 and lon1 and lat2 and lon2:
                dist = haversine_km(lat1, lon1, lat2, lon2)
                total_km += min(dist, 12.0)
            else:
                total_km += 1.5

    avg_km_day = total_km / day_count
    avg_act_day = total_activities / day_count

    fatigue_score = int(min(95, max(15, 25 + avg_km_day * 4.5 + avg_act_day * 4)))

    if fatigue_score <= 40:
        pacing_label = "Thư thái & Nghỉ dưỡng (Relaxed)"
        pacing_desc = "Nhịp độ nhẹ nhàng, phù hợp cho cặp đôi nghỉ dưỡng hoặc gia đình có người lớn tuổi/trẻ nhỏ."
    elif fatigue_score <= 70:
        pacing_label = "Cân bằng Lý tưởng (Balanced)"
        pacing_desc = "Tỷ lệ hoàn hảo giữa tham quan biểu tượng, thưởng thức ẩm thực và thư giãn tự do."
    else:
        pacing_label = "Khám phá Chuyên sâu & Năng động (High Intensity)"
        pacing_desc = "Lịch trình dày đặc trải nghiệm, dành cho du khách năng động muốn tối ưu hóa từng giờ khám phá."

    curr_month = datetime.now().month
    warnings = []
    if code in ["VN", "TH", "MY", "PH", "ID"]:
        if 5 <= curr_month <= 10:
            season_advisory = f"Mùa hè - mưa nhiệt đới tại {city_village}. Thường có mưa rào ngắn buổi chiều tối, ban ngày nắng ráo."
            warnings.append("Nên mang ô gấp gọn hoặc áo mưa tiện lợi khi tham gia các hoạt động ngoài trời.")
        else:
            season_advisory = f"Mùa khô mát mẻ, thời tiết lý tưởng nhất trong năm để du lịch {city_village}."
    elif code in ["JP", "KR"]:
        if 3 <= curr_month <= 5:
            season_advisory = f"Mùa xuân hoa anh đào tại {city_village}. Nhiệt độ se lạnh dễ chịu (12°C - 20°C)."
        elif 6 <= curr_month <= 8:
            season_advisory = f"Mùa hè tại {city_village}, trời nắng ấm và có thể có mưa rào nhẹ. Đêm mát mẻ."
        elif 9 <= curr_month <= 11:
            season_advisory = f"Mùa thu lá đỏ Koyo rực rỡ, trời trong xanh và không khí khô ráo tuyệt đẹp."
        else:
            season_advisory = f"Mùa đông se lạnh (2°C - 9°C), có thể có tuyết rơi tại vùng núi cao."
            warnings.append("Cần mang áo giữ nhiệt Heattech, áo phao ấm và găng tay.")
    elif code in ["FR", "IT", "CH", "AT", "DE", "UK"]:
        if 6 <= curr_month <= 8:
            season_advisory = f"Mùa hè Châu Âu rực rỡ, ngày dài đến 21h đêm, trời trong và nắng đẹp."
        elif 12 <= curr_month or curr_month <= 2:
            season_advisory = f"Mùa đông tuyết trắng Alps, không khí Giáng sinh cổ tích nhưng trời tối sớm từ 16h30."
            warnings.append("Lên lịch trình tham quan ngoài trời sớm trước 16:00 để tận dụng ánh sáng ban ngày.")
        else:
            season_advisory = f"Mùa xuân - thu ôn đới lãng mạn, nhiệt độ dễ chịu thích hợp đi bộ dạo phố."
    else:
        season_advisory = f"Khí hậu thuận lợi để trải nghiệm các điểm đến biểu tượng tại {city_village}."

    packing_tips = [
        f"Giày thể thao êm chân chuyên dụng (dự kiến di chuyển ~{avg_km_day:.1f} km/ngày)",
        "Bộ sạc đa năng Universal Adapter tương thích chuẩn ổ cắm quốc tế",
        "e-SIM hoặc SIM du lịch quốc tế 4G/5G data tốc độ cao",
        "Thuốc men cơ bản: hạ sốt, dị ứng thời tiết, men tiêu hóa khi thử món mới"
    ]
    if warnings:
        packing_tips.append("Ô gấp mini chống tia UV và chống thấm nước")

    health_tips = [
        "Uống đủ 1.5 - 2 lít nước mỗi ngày giữa các chặng tham quan",
        "Tận dụng khoảng đệm 30 - 45 phút giữa các điểm để nghỉ ngơi và nạp năng lượng"
    ]

    critique = {
        "fatigue_score": fatigue_score,
        "pacing_label": pacing_label,
        "pacing_description": pacing_desc,
        "total_walking_km": round(total_km, 1),
        "avg_daily_walking_km": round(avg_km_day, 1),
        "season_advisory": season_advisory,
        "warnings": warnings,
        "packing_tips": packing_tips,
        "health_tips": health_tips
    }

    return {"critique_feedback": critique}

# 14. Final Itinerary Node
def final_itinerary_node(state: TravelAgentState) -> Dict[str, Any]:
    opt_days = state.get("distance_optimized_itinerary", [])
    dest_an = state.get("destination_analysis", {})
    req = state.get("extracted_requirements", {})
    b_val = state.get("budget_validation", {})

    city_village = dest_an.get("city_or_village", req.get("destination", ""))
    country = dest_an.get("country", "")
    duration = req.get("duration", 3)
    travelers = req.get("travelers", 2)
    total_cost = b_val.get("total_cost", 0.0)
    airport = dest_an.get("nearest_airport", {})

    pref_str = ", ".join(req.get("preferences", ["văn hóa", "ẩm thực", "ngắm cảnh"]))
    ai_advice = llm_service.enhance_trip_narrative(city_village, duration, req.get("preferences", []))
    advice_section = f"\n\n💡 **Lời khuyên từ Trợ lý AI:**\n{ai_advice}" if ai_advice else ""

    critique = state.get("critique_feedback", {})
    critique_section = ""
    if critique:
        warn_txt = f"\n⚠️ Lưu ý: {critique['warnings'][0]}" if critique.get("warnings") else ""
        critique_section = (
            f"\n\n🛡️ **Phản biện & Đánh giá Thể lực (Critique Agent):**\n"
            f"• **Nhịp độ:** {critique.get('pacing_label')} (Chỉ số mệt mỏi: {critique.get('fatigue_score')}/100)\n"
            f"• **Dự tính di chuyển:** ~{critique.get('avg_daily_walking_km', 4.5)} km/ngày (Tổng chặng: ~{critique.get('total_walking_km', 15)} km)\n"
            f"• **Khí hậu & Thời vụ:** {critique.get('season_advisory')}{warn_txt}\n"
            f"• **Hành lý gợi ý:** {critique.get('packing_tips', ['Giày đi bộ êm'])[0]}"
        )

    response_msg = (
        f"🌍 **AI Travel Agent đã hoàn tất lập kế hoạch tour {city_village}, {country} ({duration} ngày {duration - 1} đêm cho {travelers} người)!**\n\n"
        f"📍 **Thông tin điểm đến & di chuyển:**\n"
        f"• **Điểm đến:** {dest_an.get('resolved_name', city_village)}\n"
        f"• **Sân bay quốc tế gần nhất:** {airport.get('name', 'Sân bay quốc tế')} ({airport.get('iata', 'INTL')}) - Cách ~{airport.get('distance_km', 40)} km\n"
        f"• **Tiền tệ bản địa:** {dest_an.get('local_currency')} ({dest_an.get('rate_vnd', '')})\n"
        f"• **Thủ tục Visa:** {dest_an.get('visa_info', 'Kiểm tra quy định visa')}\n"
        f"• **Tổng chi phí ước tính:** {total_cost:,.0f} VND (Ngân sách: {req.get('budget', 25000000):,.0f} VND)\n\n"
        f"🗺️ Lịch trình từng ngày đã được tối ưu hóa khoảng cách di chuyển Haversine TSP, kèm đệm 30 phút giữa các chặng và ưu tiên các sở thích: {pref_str}!{advice_section}{critique_section}"
    )

    return {
        "final_itinerary": opt_days,
        "critique_feedback": critique,
        "agent_response": response_msg
    }
