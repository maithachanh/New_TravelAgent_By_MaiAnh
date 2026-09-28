from typing import List, Dict, Any

def search_flight_tool(origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
    """Simulated Flight Search API Tool"""
    return [
        {
            "flight_number": "VN123",
            "airline": "Vietnam Airlines",
            "origin": origin,
            "destination": destination,
            "departure": "07:30",
            "arrival": "08:50",
            "price": 1200000.0,
            "currency": "VND"
        },
        {
            "flight_number": "VJ456",
            "airline": "VietJet Air",
            "origin": origin,
            "destination": destination,
            "departure": "10:15",
            "arrival": "11:35",
            "price": 850000.0,
            "currency": "VND"
        }
    ]

def search_hotel_tool(destination: str, check_in: str, check_out: str, styles: List[str] = None) -> List[Dict[str, Any]]:
    """Simulated Hotel Search API Tool"""
    return [
        {
            "name": f"Grand Beach Resort & Spa {destination}",
            "type": "Luxury / Resort",
            "rating": 4.8,
            "price_per_night": 1800000.0,
            "address": f"Bãi biển chính, {destination}",
            "latitude": 16.0600,
            "longitude": 108.2400
        },
        {
            "name": f"Boutique Hotel & Suites {destination}",
            "type": "Budget / Family",
            "rating": 4.5,
            "price_per_night": 750000.0,
            "address": f"Trung tâm thành phố, {destination}",
            "latitude": 16.0544,
            "longitude": 108.2022
        }
    ]

def search_restaurant_tool(destination: str, cuisine_type: str = "Local") -> List[Dict[str, Any]]:
    """Simulated Restaurant Search API Tool"""
    return [
        {
            "name": f"Nhà Hàng Ẩm Thực Địa Phương {destination}",
            "category": "Food",
            "avg_cost": 250000.0,
            "rating": 4.7,
            "address": f"Đường Ẩm Thực, {destination}",
            "latitude": 16.0520,
            "longitude": 108.2150
        },
        {
            "name": f"Hải Sản Tươi Sống Sông Hàn",
            "category": "Food / Seafood",
            "avg_cost": 400000.0,
            "rating": 4.6,
            "address": f"Đường Trần Hưng Đạo, {destination}",
            "latitude": 16.0650,
            "longitude": 108.2300
        }
    ]

def search_attraction_tool(destination: str, styles: List[str] = None) -> List[Dict[str, Any]]:
    """Simulated Attraction / Activity Search API Tool"""
    return [
        {
            "name": f"Bà Nà Hills & Cầu Vàng",
            "category": "Adventure / Cultural",
            "avg_cost": 900000.0,
            "duration_minutes": 240,
            "latitude": 15.9967,
            "longitude": 107.9870
        },
        {
            "name": f"Bãi Biển Mỹ Khê",
            "category": "Relaxation / Nature",
            "avg_cost": 0.0,
            "duration_minutes": 120,
            "latitude": 16.0580,
            "longitude": 108.2450
        },
        {
            "name": f"Ngũ Hành Sơn & Chùa Linh Ứng",
            "category": "Cultural / Nature",
            "avg_cost": 50000.0,
            "duration_minutes": 150,
            "latitude": 16.0020,
            "longitude": 108.2630
        },
        {
            "name": f"Chợ Đêm Sơn Trà & Cầu Rồng",
            "category": "Shopping / Food",
            "avg_cost": 150000.0,
            "duration_minutes": 120,
            "latitude": 16.0610,
            "longitude": 108.2280
        }
    ]
