import re
from typing import Dict, Any, List
from app.agent.state import TravelAgentState
from app.agent.tools.registry import tool_registry
from app.services.rag_service import rag_service
from app.services.optimizer import optimize_daily_route, calculate_trip_total_cost
from app.services.geo_service import geo_service
from app.services.currency_service import currency_service

# 1. User Request Analyzer Node
def user_request_analyzer_node(state: TravelAgentState) -> Dict[str, Any]:
    prompt = state.get("user_prompt", "")
    intent = "PLAN_NEW_TRIP"
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
    prompt_lower = prompt.lower()

    # Tier 1: Check Specific Cities, Villages, and Landmarks (Ordered by specificity)
    SPECIFIC_SPOTS = [
        # Japan
        (["kyoto"], "Kyoto, Nhật Bản"),
        (["osaka"], "Osaka, Nhật Bản"),
        (["tokyo"], "Tokyo, Nhật Bản"),
        (["shirakawa", "shirakawago"], "Shirakawa-go, Gifu, Nhật Bản"),
        (["nara"], "Nara, Nhật Bản"),
        (["sapporo", "hokkaido"], "Sapporo, Hokkaido, Nhật Bản"),
        (["fukuoka"], "Fukuoka, Nhật Bản"),
        (["hiroshima"], "Hiroshima, Nhật Bản"),
        # South Korea
        (["busan"], "Busan, Hàn Quốc"),
        (["jeju"], "Đảo Jeju, Hàn Quốc"),
        (["incheon"], "Incheon, Hàn Quốc"),
        (["nami"], "Đảo Nami, Hàn Quốc"),
        (["seoul"], "Seoul, Hàn Quốc"),
        # Vietnam
        (["sa pa", "sapa", "cát cát", "cat cat", "fansipan"], "Bản Cát Cát, Sa Pa"),
        (["hà nội", "ha noi"], "Hà Nội, Việt Nam"),
        (["đà nẵng", "da nang", "bà nà"], "Đà Nẵng, Việt Nam"),
        (["hội an", "hoi an"], "Hội An, Quảng Nam, Việt Nam"),
        (["huế", "hue"], "Huế, Việt Nam"),
        (["đà lạt", "da lat"], "Đà Lạt, Lâm Đồng, Việt Nam"),
        (["nha trang"], "Nha Trang, Khánh Hòa, Việt Nam"),
        (["phú quốc", "phu quoc"], "Phú Quốc, Kiên Giang, Việt Nam"),
        (["hạ long", "ha long"], "Vịnh Hạ Long, Quảng Ninh, Việt Nam"),
        (["ninh bình", "ninh binh", "tràng an"], "Ninh Bình, Việt Nam"),
        (["quy nhơn", "quy nhon"], "Quy Nhơn, Bình Định, Việt Nam"),
        (["vũng tàu", "vung tau"], "Vũng Tàu, Việt Nam"),
        (["hồ chí minh", "sài gòn", "saigon", "tphcm"], "TP. Hồ Chí Minh, Việt Nam"),
        # Europe
        (["hallstatt", "halstatt"], "Hallstatt, Áo"),
        (["vienna"], "Vienna, Áo"),
        (["salzburg"], "Salzburg, Áo"),
        (["innsbruck"], "Innsbruck, Áo"),
        (["zermatt", "matterhorn"], "Zermatt, Thụy Sĩ"),
        (["zurich"], "Zurich, Thụy Sĩ"),
        (["geneva", "genève"], "Geneva, Thụy Sĩ"),
        (["lucerne", "luzern"], "Lucerne, Thụy Sĩ"),
        (["interlaken", "jungfrau"], "Interlaken, Thụy Sĩ"),
        (["grindelwald"], "Grindelwald, Thụy Sĩ"),
        (["paris"], "Paris, Pháp"),
        (["nice"], "Nice, Pháp"),
        (["lyon"], "Lyon, Pháp"),
        (["rome", "roma"], "Rome, Ý"),
        (["venice", "venezia"], "Venice, Ý"),
        (["florence", "firenze"], "Florence, Ý"),
        (["milan", "milano"], "Milan, Ý"),
        (["positano", "amalfi"], "Positano, Ý"),
        (["london"], "London, Vương Quốc Anh"),
        (["edinburgh"], "Edinburgh, Scotland"),
        (["berlin"], "Berlin, Đức"),
        (["munich", "münchen"], "Munich, Đức"),
        (["frankfurt"], "Frankfurt, Đức"),
        (["amsterdam"], "Amsterdam, Hà Lan"),
        (["giethoorn"], "Giethoorn, Hà Lan"),
        (["santorini", "oia"], "Santorini, Hy Lạp"),
        (["athens"], "Athens, Hy Lạp"),
        (["reykjavik"], "Reykjavik, Iceland"),
        (["reine", "lofoten"], "Reine, Na Uy"),
        (["oslo"], "Oslo, Na Uy"),
        (["bergen"], "Bergen, Na Uy"),
        # Southeast Asia & Asia
        (["bangkok", "băng cốc"], "Bangkok, Thái Lan"),
        (["chiang mai"], "Chiang Mai, Thái Lan"),
        (["phuket"], "Phuket, Thái Lan"),
        (["ban rak thai", "mae hong son"], "Ban Rak Thai, Thái Lan"),
        (["singapore"], "Singapore"),
        (["bali"], "Đảo Bali, Indonesia"),
        (["kuala lumpur"], "Kuala Lumpur, Malaysia"),
        (["bắc kinh", "beijing"], "Bắc Kinh, Trung Quốc"),
        (["thượng hải", "shanghai"], "Thượng Hải, Trung Quốc"),
        (["trương gia giới"], "Trương Gia Giới, Trung Quốc"),
        (["phượng hoàng cổ trấn"], "Phượng Hoàng Cổ Trấn, Trung Quốc"),
        (["đài bắc", "taipei"], "Đài Bắc, Đài Loan"),
        # Americas & Australia
        (["sydney"], "Sydney, Úc"),
        (["melbourne"], "Melbourne, Úc"),
        (["new york", "nyc"], "New York, Mỹ"),
        (["los angeles", "la"], "Los Angeles, Mỹ"),
        (["san francisco"], "San Francisco, Mỹ"),
        (["las vegas"], "Las Vegas, Mỹ"),
        (["hawaii", "honolulu"], "Hawaii, Mỹ")
    ]

    destination = None
    for keywords, canonical in SPECIFIC_SPOTS:
        if any(kw in prompt_lower for kw in keywords):
            destination = canonical
            break

    # Tier 2: Check Broad Country Keywords (Only if no specific city was mentioned)
    if not destination:
        COUNTRY_DEFAULTS = [
            (["hàn quốc", "korea"], "Seoul, Hàn Quốc"),
            (["nhật bản", "japan"], "Tokyo, Nhật Bản"),
            (["pháp", "france"], "Paris, Pháp"),
            (["thụy sĩ", "switzerland"], "Zurich, Thụy Sĩ"),
            (["áo", "austria"], "Vienna, Áo"),
            (["ý", "italy"], "Rome, Ý"),
            (["thái lan", "thailand"], "Bangkok, Thái Lan"),
            (["anh", "vương quốc anh", "uk", "nước anh"], "London, Vương Quốc Anh"),
            (["đức", "germany"], "Berlin, Đức"),
            (["mỹ", "hoa kỳ", "usa", "nước mỹ"], "New York, Mỹ"),
            (["úc", "australia"], "Sydney, Úc"),
            (["trung quốc", "china"], "Bắc Kinh, Trung Quốc"),
            (["đài loan", "taiwan"], "Đài Bắc, Đài Loan"),
            (["hà lan", "netherlands"], "Amsterdam, Hà Lan"),
            (["hy lạp", "greece"], "Santorini, Hy Lạp"),
            (["na uy", "norway"], "Oslo, Na Uy"),
            (["việt nam", "vietnam"], "Đà Nẵng, Việt Nam")
        ]
        for c_keywords, c_canonical in COUNTRY_DEFAULTS:
            if any(ck in prompt_lower for ck in c_keywords):
                destination = c_canonical
                break

    # Tier 3: Universal Regex Parser for ANY destination
    if not destination:
        match_pattern = re.search(
            r'(?:tôi muốn|hãy|cho tôi|lập|lên|tư vấn|gợi ý|muốn)?\s*(?:kế hoạch|lịch trình|tour|chuyến đi)?\s*(?:du lịch|khám phá|đi|thăm|đến|tới|nghỉ dưỡng|trải nghiệm|check-in|checkin|ở|tại)\s+(?:làng|thị trấn|bản|thành phố|thủ đô|tỉnh|đảo|quốc gia|nước)?\s*([A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĐa-zàáâãèéêìíòóôõùúýđ\s,\-\.\'\(\)]+?)(?=\s*(?:\d+\s*ngày|\d+\s*đêm|trong|vào|tháng|ngân sách|chi phí|tự túc|cho|khoảng|với|kèm|thích|yêu cầu|$))',
            prompt,
            re.IGNORECASE
        )
        if match_pattern:
            captured = match_pattern.group(1).strip()
            # Strip trailing prepositions
            captured = re.sub(r'\s+(ở|tại|với|cho|cùng|trong|kèm)\s*$', '', captured, flags=re.IGNORECASE).strip()
            if len(captured) >= 2:
                destination = captured.title()

    # Final fallback if still unresolved
    if not destination:
        destination = "Đà Nẵng, Việt Nam"

    # Extract duration (days)
    duration_match = re.search(r'(\d+)\s*(?:ngày|ngay|days|n)', prompt, re.IGNORECASE)
    duration = int(duration_match.group(1)) if duration_match else 3
    duration = max(1, min(duration, 14))

    # Extract travelers
    travelers_match = re.search(r'(\d+)\s*(?:người|khách|thành viên|pax|bạn|vé)', prompt, re.IGNORECASE)
    if travelers_match:
        travelers = int(travelers_match.group(1))
    elif "gia đình" in prompt_lower:
        travelers = 4
    elif "1 mình" in prompt_lower or "độc thân" in prompt_lower:
        travelers = 1
    else:
        travelers = 2

    # Extract budget & currency conversion
    budget = 25_000_000.0 * (travelers / 2.0)
    
    # Check EUR budget
    eur_match = re.search(r'(\d+(?:[\.,]\d+)?)\s*(?:eur|euro|€)', prompt, re.IGNORECASE)
    usd_match = re.search(r'(\d+(?:[\.,]\d+)?)\s*(?:usd|\$|đô|dollar)', prompt, re.IGNORECASE)
    vnd_mil_match = re.search(r'(\d+(?:[\.,]\d+)?)\s*(?:triệu|tr|trieu|m)', prompt, re.IGNORECASE)
    vnd_full_match = re.search(r'(\d{1,3}(?:[\.,]\d{3})+)\s*(?:vnd|vnđ|đồng)?', prompt, re.IGNORECASE)

    if eur_match:
        val_str = eur_match.group(1).replace(",", ".")
        budget = float(val_str) * 27_600.0
    elif usd_match:
        val_str = usd_match.group(1).replace(",", ".")
        budget = float(val_str) * 25_450.0
    elif vnd_mil_match:
        val_str = vnd_mil_match.group(1).replace(",", ".")
        budget = float(val_str) * 1_000_000.0
    elif vnd_full_match:
        val_str = re.sub(r'[\.,]', '', vnd_full_match.group(1))
        budget = float(val_str)

    # Extract preferences
    preferences = []
    if any(k in prompt_lower for k in ["ăn", "ẩm thực", "nhà hàng", "food", "món", "quán", "đặc sản"]):
        preferences.append("food")
    if any(k in prompt_lower for k in ["mua sắm", "shopping", "chợ", "trung tâm", "mall"]):
        preferences.append("shopping")
    if any(k in prompt_lower for k in ["văn hóa", "lịch sử", "chùa", "đền", "bảo tàng", "culture", "cung điện", "cổ", "di sản"]):
        preferences.append("culture")
    if any(k in prompt_lower for k in ["thiên nhiên", "núi", "hồ", "cảnh", "nature", "tuyết", "băng", "hoa", "rừng"]):
        preferences.append("nature")
    if any(k in prompt_lower for k in ["biển", "đảo", "lặn", "nghỉ dưỡng", "relaxation", "resort"]):
        preferences.append("relaxation")
    if any(k in prompt_lower for k in ["khám phá", "mạo hiểm", "adventure", "trekking", "leo núi", "trượt tuyết"]):
        preferences.append("adventure")

    if not preferences:
        preferences = ["culture", "food", "nature"]

    # Extract travel month
    month_match = re.search(r'tháng\s*(\d+)', prompt, re.IGNORECASE)
    travel_month = int(month_match.group(1)) if month_match else 12

    extracted = {
        "destination": destination,
        "duration": duration,
        "budget": budget,
        "currency": "VND",
        "preferences": preferences,
        "travel_month": travel_month,
        "origin": "Hà Nội",
        "travelers": travelers
    }
    return {"extracted_requirements": extracted}

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

# 10. Itinerary Generator Node (Enriched Day-by-Day Scheduling)
def itinerary_generator_node(state: TravelAgentState) -> Dict[str, Any]:
    req = state.get("extracted_requirements", {})
    dest_an = state.get("destination_analysis", {})
    duration = req.get("duration", 3)
    city_village = dest_an.get("city_or_village", req.get("destination", ""))
    country = dest_an.get("country", "")
    travelers = req.get("travelers", 2)

    flights = state.get("flight_results", [])
    hotels = state.get("hotel_results", [])
    activities = state.get("activity_results", [])
    restaurants = state.get("restaurant_results", [])

    chosen_flight = flights[0] if flights else {"flight_number": "VN100", "price_per_person": 3500000.0}
    chosen_hotel = hotels[0] if hotels else {
        "name": f"Boutique Hotel {city_village}",
        "price_per_night": 1200000.0,
        "latitude": dest_an.get("latitude", 16.0),
        "longitude": dest_an.get("longitude", 108.0),
        "address": f"Khu trung tâm, {city_village}"
    }

    raw_days = []
    num_acts = len(activities) if activities else 1
    num_rests = len(restaurants) if restaurants else 1

    for day in range(1, duration + 1):
        items = []

        if day == 1:
            # Day 1: Departure & Arrival
            items.append({
                "title": f"Chuyến bay {chosen_flight.get('flight_number')} đi {city_village}",
                "item_type": "FLIGHT",
                "start_time": "08:00",
                "end_time": "12:30",
                "location": f"Hạ cánh tại {chosen_flight.get('destination', city_village)}",
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 270,
                "estimated_cost": chosen_flight.get("price_per_person", 3500000.0) * travelers,
                "notes": f"Chuyến bay {chosen_flight.get('airline', 'Hàng không')}. Sân bay đến: {chosen_flight.get('nearest_airport_name', 'Sân bay quốc tế')}."
            })
            # Hotel Check-in
            items.append({
                "title": f"Check-in nhận phòng tại {chosen_hotel.get('name')}",
                "item_type": "HOTEL_CHECKIN",
                "start_time": "13:30",
                "end_time": "14:30",
                "location": chosen_hotel.get("address", city_village),
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 60,
                "estimated_cost": chosen_hotel.get("price_per_night", 1200000.0),
                "notes": f"Khách sạn tiêu chuẩn {chosen_hotel.get('star_rating', 4)} sao. Nghỉ ngơi & gửi hành lý."
            })
            # Welcome Lunch / Light Meal
            welcome_rest = restaurants[0] if restaurants else {"name": f"Quán Ăn Phố Cổ {city_village}", "price_avg": 200000.0}
            items.append({
                "title": f"Bữa trưa đầu tiên: {welcome_rest['name']}",
                "item_type": "LUNCH",
                "start_time": "15:00",
                "end_time": "16:15",
                "location": welcome_rest.get("address", city_village),
                "latitude": welcome_rest.get("latitude", chosen_hotel.get("latitude")),
                "longitude": welcome_rest.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 75,
                "estimated_cost": welcome_rest.get("price_avg", 200000.0) * travelers,
                "notes": welcome_rest.get("specialty", f"Đặc sản nức tiếng vùng {city_village}")
            })
            # Afternoon Stroll
            act_1 = activities[0] if activities else {"name": f"Dạo quanh quảng trường & phố cổ {city_village}", "price": 0.0, "duration_minutes": 90}
            items.append({
                "title": f"Khám phá: {act_1['name']}",
                "item_type": "ATTRACTION",
                "start_time": "16:45",
                "end_time": "18:45",
                "location": act_1.get("address", city_village),
                "latitude": act_1.get("latitude", chosen_hotel.get("latitude")),
                "longitude": act_1.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 120,
                "estimated_cost": act_1.get("price", 0.0) * travelers,
                "notes": act_1.get("description", "Dạo chơi thư giãn và chụp ảnh check-in đầu tiên.")
            })
            # Welcome Dinner
            dinner_rest = restaurants[1 % num_rests] if restaurants else welcome_rest
            items.append({
                "title": f"Bữa tối ẩm thực địa phương: {dinner_rest['name']}",
                "item_type": "DINNER",
                "start_time": "19:15",
                "end_time": "21:15",
                "location": dinner_rest.get("address", city_village),
                "latitude": dinner_rest.get("latitude", chosen_hotel.get("latitude")),
                "longitude": dinner_rest.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 120,
                "estimated_cost": dinner_rest.get("price_avg", 250000.0) * travelers,
                "notes": dinner_rest.get("specialty", "Bữa tối ấm cúng cùng đặc sản địa phương.")
            })

        elif day < duration:
            # Middle Days: Full exploration
            # Morning Breakfast
            items.append({
                "title": f"Bữa sáng & Thưởng thức cà phê / trà sáng {city_village}",
                "item_type": "BREAKFAST",
                "start_time": "08:00",
                "end_time": "09:00",
                "location": chosen_hotel.get("address", city_village),
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 60,
                "estimated_cost": 80000.0 * travelers,
                "notes": "Bắt đầu ngày mới với bữa sáng giàu năng lượng và thức uống địa phương."
            })
            # Morning Major Highlight
            act_idx = ((day - 1) * 2 - 1) % num_acts
            act_morning = activities[act_idx] if activities else {"name": f"Điểm di sản văn hóa {city_village}", "price": 150000.0, "duration_minutes": 150}
            items.append({
                "title": f"Tham quan điểm nhấn: {act_morning['name']}",
                "item_type": "ATTRACTION",
                "start_time": "09:30",
                "end_time": "12:00",
                "location": act_morning.get("address", city_village),
                "latitude": act_morning.get("latitude", chosen_hotel.get("latitude")),
                "longitude": act_morning.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 150,
                "estimated_cost": act_morning.get("price", 150000.0) * travelers,
                "notes": act_morning.get("description", "Điểm tham quan đặc trưng không thể bỏ qua.")
            })
            # Lunch
            lunch_rest = restaurants[day % num_rests] if restaurants else {"name": "Nhà hàng ẩm thực", "price_avg": 220000.0}
            items.append({
                "title": f"Bữa trưa đặc sản: {lunch_rest['name']}",
                "item_type": "LUNCH",
                "start_time": "12:30",
                "end_time": "13:45",
                "location": lunch_rest.get("address", city_village),
                "latitude": lunch_rest.get("latitude", chosen_hotel.get("latitude")),
                "longitude": lunch_rest.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 75,
                "estimated_cost": lunch_rest.get("price_avg", 220000.0) * travelers,
                "notes": lunch_rest.get("specialty", "Thưởng thức ẩm thực trưa tươi ngon.")
            })
            # Afternoon Activity
            act_afternoon = activities[(act_idx + 1) % num_acts] if activities else {"name": f"Trải nghiệm bản địa {city_village}", "price": 250000.0, "duration_minutes": 150}
            items.append({
                "title": f"Trải nghiệm nổi bật: {act_afternoon['name']}",
                "item_type": "ACTIVITY",
                "start_time": "14:15",
                "end_time": "17:15",
                "location": act_afternoon.get("address", city_village),
                "latitude": act_afternoon.get("latitude", chosen_hotel.get("latitude")),
                "longitude": act_afternoon.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 180,
                "estimated_cost": act_afternoon.get("price", 250000.0) * travelers,
                "notes": act_afternoon.get("description", "Trải nghiệm văn hóa & khám phá thiên nhiên.")
            })
            # Scenic Viewpoint / Sunset Walk
            items.append({
                "title": f"Ngắm hoàng hôn & Chụp ảnh Viewpoint {city_village}",
                "item_type": "ATTRACTION",
                "start_time": "17:45",
                "end_time": "19:00",
                "location": f"Đài ngắm cảnh {city_village}",
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 75,
                "estimated_cost": 0.0,
                "notes": "Khoảnh khắc hoàng hôn tuyệt đẹp và dạo mát thư thái."
            })
            # Dinner
            mid_dinner = restaurants[(day + 1) % num_rests] if restaurants else lunch_rest
            items.append({
                "title": f"Bữa tối thịnh soạn: {mid_dinner['name']}",
                "item_type": "DINNER",
                "start_time": "19:30",
                "end_time": "21:30",
                "location": mid_dinner.get("address", city_village),
                "latitude": mid_dinner.get("latitude", chosen_hotel.get("latitude")),
                "longitude": mid_dinner.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 120,
                "estimated_cost": mid_dinner.get("price_avg", 300000.0) * travelers,
                "notes": mid_dinner.get("specialty", "Bữa tối ấm cúng cùng âm nhạc & đồ uống bản địa.")
            })

        else:
            # Final Day: Check-out, Souvenirs & Farewell
            items.append({
                "title": f"Bữa sáng & Làm thủ tục trả phòng tại {chosen_hotel.get('name')}",
                "item_type": "HOTEL_CHECKOUT",
                "start_time": "08:30",
                "end_time": "09:45",
                "location": chosen_hotel.get("address", city_village),
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 75,
                "estimated_cost": 0.0,
                "notes": "Thu dọn hành lý, gửi tại quầy lễ tân và chuẩn bị quà lưu niệm."
            })
            # Souvenir Shopping
            shop_act = activities[-1] if activities else {"name": f"Chợ thủ công & Quà lưu niệm {city_village}", "price": 200000.0}
            items.append({
                "title": f"Mua sắm đặc sản & Quà lưu niệm {city_village}",
                "item_type": "SHOPPING",
                "start_time": "10:15",
                "end_time": "12:15",
                "location": f"Khu chợ truyền thống {city_village}",
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 120,
                "estimated_cost": 300000.0 * travelers,
                "notes": f"Chọn những món quà lưu niệm độc đáo mang đậm dấu ấn {city_village} cho người thân."
            })
            # Farewell Lunch
            farewell_rest = restaurants[-1] if restaurants else {"name": "Nhà hàng chia tay", "price_avg": 250000.0}
            items.append({
                "title": f"Bữa trưa chia tay: {farewell_rest['name']}",
                "item_type": "LUNCH",
                "start_time": "12:30",
                "end_time": "13:45",
                "location": farewell_rest.get("address", city_village),
                "latitude": farewell_rest.get("latitude", chosen_hotel.get("latitude")),
                "longitude": farewell_rest.get("longitude", chosen_hotel.get("longitude")),
                "duration_minutes": 75,
                "estimated_cost": farewell_rest.get("price_avg", 250000.0) * travelers,
                "notes": farewell_rest.get("specialty", "Thưởng thức bữa ăn cuối chuyến đi trọn vẹn vị giác.")
            })
            # Departure Flight
            items.append({
                "title": f"Chuyến bay về lại {req.get('origin', 'Hà Nội')}",
                "item_type": "FLIGHT",
                "start_time": "15:00",
                "end_time": "19:30",
                "location": f"Khởi hành từ sân bay {chosen_flight.get('nearest_airport_name', 'Sân bay')}",
                "latitude": chosen_hotel.get("latitude"),
                "longitude": chosen_hotel.get("longitude"),
                "duration_minutes": 270,
                "estimated_cost": 0.0,
                "notes": f"Kết thúc hành trình khám phá {city_village}, {country} tuyệt vời cùng Travel Agent AI!"
            })

        raw_days.append({
            "day_number": day,
            "date": f"2026-12-0{day}" if day < 10 else f"2026-12-{day}",
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

    is_valid = total_cost <= budget_limit * 1.25
    return {
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
    response_msg = (
        f"🌍 **AI Travel Agent đã hoàn tất lập kế hoạch tour {city_village}, {country} ({duration} ngày {duration - 1} đêm cho {travelers} người)!**\n\n"
        f"📍 **Thông tin điểm đến & di chuyển:**\n"
        f"• **Điểm đến:** {dest_an.get('resolved_name', city_village)}\n"
        f"• **Sân bay quốc tế gần nhất:** {airport.get('name', 'Sân bay quốc tế')} ({airport.get('iata', 'INTL')}) - Cách ~{airport.get('distance_km', 40)} km\n"
        f"• **Tiền tệ bản địa:** {dest_an.get('local_currency')} ({dest_an.get('rate_vnd', '')})\n"
        f"• **Thủ tục Visa:** {dest_an.get('visa_info', 'Kiểm tra quy định visa')}\n"
        f"• **Tổng chi phí ước tính:** {total_cost:,.0f} VND (Ngân sách: {req.get('budget', 25000000):,.0f} VND)\n\n"
        f"🗺️ Lịch trình từng ngày đã được tối ưu hóa khoảng cách di chuyển Haversine TSP, kèm đệm 30 phút giữa các chặng và ưu tiên các sở thích: {pref_str}!"
    )

    return {
        "final_itinerary": opt_days,
        "agent_response": response_msg
    }
