from typing import List, Dict, Any, Optional
from app.agent.tools.base import (
    BaseFlightTool,
    BaseHotelTool,
    BaseRestaurantTool,
    BaseActivityTool
)

class MockFlightProvider(BaseFlightTool):
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: Optional[str] = None,
        travelers: int = 1
    ) -> List[Dict[str, Any]]:
        dest_lower = destination.lower()
        if "hàn quốc" in dest_lower or "seoul" in dest_lower or "korea" in dest_lower or "busan" in dest_lower:
            return [
                {
                    "flight_number": "KE680",
                    "airline": "Korean Air",
                    "origin": origin,
                    "destination": "Seoul (ICN)",
                    "departure": "00:45",
                    "arrival": "06:50",
                    "price_per_person": 8500000.0,
                    "total_price": 8500000.0 * travelers,
                    "currency": "VND",
                    "duration": "4h 05m",
                    "type": "Direct 5-Star"
                },
                {
                    "flight_number": "VJ860",
                    "airline": "VietJet Air",
                    "origin": origin,
                    "destination": "Seoul (ICN)",
                    "departure": "01:55",
                    "arrival": "08:10",
                    "price_per_person": 5200000.0,
                    "total_price": 5200000.0 * travelers,
                    "currency": "VND",
                    "duration": "4h 15m",
                    "type": "Direct"
                },
                {
                    "flight_number": "VN414",
                    "airline": "Vietnam Airlines",
                    "origin": origin,
                    "destination": "Seoul (ICN)",
                    "departure": "10:25",
                    "arrival": "16:35",
                    "price_per_person": 7800000.0,
                    "total_price": 7800000.0 * travelers,
                    "currency": "VND",
                    "duration": "4h 10m",
                    "type": "Direct"
                }
            ]
        elif "tokyo" in dest_lower or "nhật" in dest_lower or "japan" in dest_lower:
            return [
                {
                    "flight_number": "VN300",
                    "airline": "Vietnam Airlines",
                    "origin": origin,
                    "destination": "Tokyo (NRT)",
                    "departure": "00:20",
                    "arrival": "07:35",
                    "price_per_person": 10500000.0,
                    "total_price": 10500000.0 * travelers,
                    "currency": "VND",
                    "duration": "5h 15m",
                    "type": "Direct"
                },
                {
                    "flight_number": "VJ932",
                    "airline": "VietJet Air",
                    "origin": origin,
                    "destination": "Tokyo (NRT)",
                    "departure": "01:45",
                    "arrival": "08:50",
                    "price_per_person": 6800000.0,
                    "total_price": 6800000.0 * travelers,
                    "currency": "VND",
                    "duration": "5h 05m",
                    "type": "Direct"
                }
            ]
        elif "đà nẵng" in dest_lower:
            return [
                {
                    "flight_number": "VN123",
                    "airline": "Vietnam Airlines",
                    "origin": origin,
                    "destination": "Đà Nẵng (DAD)",
                    "departure": "07:15",
                    "arrival": "08:35",
                    "price_per_person": 1450000.0,
                    "total_price": 1450000.0 * travelers,
                    "currency": "VND",
                    "duration": "1h 20m",
                    "type": "Direct"
                }
            ]
        else:
            return [
                {
                    "flight_number": f"FL-{origin[:2].upper()}{destination[:2].upper()}1",
                    "airline": "Vietnam Airlines",
                    "origin": origin,
                    "destination": destination,
                    "departure": "08:30",
                    "arrival": "12:30",
                    "price_per_person": 6500000.0,
                    "total_price": 6500000.0 * travelers,
                    "currency": "VND",
                    "duration": "4h 00m",
                    "type": "Direct"
                }
            ]

class MockHotelProvider(BaseHotelTool):
    def search_hotels(
        self,
        city: str,
        check_in: Optional[str] = None,
        check_out: Optional[str] = None,
        budget_tier: Optional[str] = "MEDIUM",
        preferences: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        city_lower = city.lower()
        if "hàn quốc" in city_lower or "seoul" in city_lower or "korea" in city_lower:
            return [
                {
                    "id": "h_seoul_1",
                    "name": "Lotte Hotel Seoul Myeongdong",
                    "district": "Myeongdong",
                    "rating": 4.9,
                    "star_rating": 5,
                    "price_per_night": 2800000.0,
                    "currency": "VND",
                    "address": "30 Eulji-ro, Jung-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5653,
                    "longitude": 126.9809,
                    "amenities": ["Ngay Trung Tâm Myeongdong", "Lotte Department Store Connected", "Metro Station"]
                },
                {
                    "id": "h_seoul_2",
                    "name": "RYSE Autograph Collection Hongdae",
                    "district": "Hongdae",
                    "rating": 4.7,
                    "star_rating": 4,
                    "price_per_night": 2100000.0,
                    "currency": "VND",
                    "address": "130 Yanghwa-ro, Mapo-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5550,
                    "longitude": 126.9216,
                    "amenities": ["Khu Giới Trẻ Hongdae", "Rooftop Lounge", "Thiết Kế Nghệ Thuật"]
                },
                {
                    "id": "h_seoul_3",
                    "name": "Nine Tree Premier Hotel Myeongdong 2",
                    "district": "Myeongdong / Euljiro",
                    "rating": 4.6,
                    "star_rating": 4,
                    "price_per_night": 1550000.0,
                    "currency": "VND",
                    "address": "28 Mareunnae-ro, Jung-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5641,
                    "longitude": 126.9892,
                    "amenities": ["Đi Bộ Đến Chợ Myeongdong", "Giá Hợp Lý", "Phòng Sạch Sẽ"]
                }
            ]
        elif "tokyo" in city_lower or "nhật" in city_lower:
            return [
                {
                    "id": "h_tokyo_1",
                    "name": "Shinjuku Granbell Hotel Tokyo",
                    "district": "Shinjuku",
                    "rating": 4.6,
                    "star_rating": 4,
                    "price_per_night": 2200000.0,
                    "currency": "VND",
                    "address": "2-14-5 Kabukicho, Shinjuku-ku, Tokyo",
                    "latitude": 35.6961,
                    "longitude": 139.7046,
                    "amenities": ["Free Wi-Fi", "Rooftop Bar", "Metro Station 3m walk"]
                },
                {
                    "id": "h_tokyo_2",
                    "name": "Shibuya Stream Excel Hotel Tokyu",
                    "district": "Shibuya",
                    "rating": 4.8,
                    "star_rating": 4,
                    "price_per_night": 3100000.0,
                    "currency": "VND",
                    "address": "3-21-3 Shibuya, Shibuya-ku, Tokyo",
                    "latitude": 35.6580,
                    "longitude": 139.7016,
                    "amenities": ["Shopping Connected", "Direct Station Access"]
                }
            ]
        elif "đà nẵng" in city_lower:
            return [
                {
                    "id": "h_dn_1",
                    "name": "Novotel Danang Premier Han River",
                    "district": "Hải Châu",
                    "rating": 4.7,
                    "star_rating": 5,
                    "price_per_night": 1950000.0,
                    "currency": "VND",
                    "address": "36 Bạch Đằng, Hải Châu, Đà Nẵng",
                    "latitude": 16.0740,
                    "longitude": 108.2230,
                    "amenities": ["Infinity Pool", "River View"]
                }
            ]
        else:
            return [
                {
                    "id": f"h_{city_lower[:3]}_1",
                    "name": f"Hotel Central Premier {city}",
                    "district": "Center",
                    "rating": 4.6,
                    "star_rating": 4,
                    "price_per_night": 1800000.0,
                    "currency": "VND",
                    "address": f"Central District, {city}",
                    "latitude": 37.56,
                    "longitude": 126.98,
                    "amenities": ["Wi-Fi", "Breakfast", "Center Location"]
                }
            ]

class MockRestaurantProvider(BaseRestaurantTool):
    def search_restaurants(
        self,
        city: str,
        cuisine_types: Optional[List[str]] = None,
        price_range: Optional[str] = "MEDIUM"
    ) -> List[Dict[str, Any]]:
        city_lower = city.lower()
        if "hàn quốc" in city_lower or "seoul" in city_lower or "korea" in city_lower:
            return [
                {
                    "name": "Tosokchon Samgyetang (Gà Tần Sâm)",
                    "cuisine": "Korean Traditional / Samgyetang",
                    "rating": 4.9,
                    "price_avg": 360000.0,
                    "currency": "VND",
                    "address": "5 Jahamun-ro 5-gil, Jongno-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5777,
                    "longitude": 126.9716,
                    "specialty": "Gà hầm sâm tươi núi cao cấp nổi tiếng nhất Hàn Quốc"
                },
                {
                    "name": "Myeongdong Kyoja (Bánh Mì Sủi Cảo & Mì Kalguksu)",
                    "cuisine": "Noodles & Mandu",
                    "rating": 4.8,
                    "price_avg": 220000.0,
                    "currency": "VND",
                    "address": "29 Myeongdong 10-gil, Jung-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5625,
                    "longitude": 126.9856,
                    "specialty": "Mì nước súp đậm đà & Sủi cảo hấp Mandu Michelin Bib Gourmand"
                },
                {
                    "name": "Maple Tree House (Bò Nướng BBQ Hàn Quốc)",
                    "cuisine": "Korean BBQ / Hanwoo Beef",
                    "rating": 4.8,
                    "price_avg": 550000.0,
                    "currency": "VND",
                    "address": "116 Itaewon-ro, Yongsan-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5348,
                    "longitude": 126.9940,
                    "specialty": "Thịt bò Hanwoo cao cấp nướng than hoa mềm mọng"
                },
                {
                    "name": "Chợ Truyền Thống Gwangjang Market",
                    "cuisine": "Korean Street Food",
                    "rating": 4.7,
                    "price_avg": 180000.0,
                    "currency": "VND",
                    "address": "88 Changgyeonggung-ro, Jongno-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5701,
                    "longitude": 126.9998,
                    "specialty": "Bánh hẹ giòn Bindaetteok, Tteokbokki cay nồng & Mayak Kimbap"
                }
            ]
        elif "tokyo" in city_lower or "nhật" in city_lower:
            return [
                {
                    "name": "Ichiran Ramen Shibuya",
                    "cuisine": "Ramen / Japanese",
                    "rating": 4.8,
                    "price_avg": 250000.0,
                    "currency": "VND",
                    "address": "1-22-7 Jinnan, Shibuya-ku, Tokyo",
                    "latitude": 35.6605,
                    "longitude": 139.7005,
                    "specialty": "Tonkotsu Ramen mì mì nước béo ngậy"
                },
                {
                    "name": "Chợ Hải Sản Tsukiji Outer Market",
                    "cuisine": "Sushi & Seafood",
                    "rating": 4.9,
                    "price_avg": 450000.0,
                    "currency": "VND",
                    "address": "4-16-2 Tsukiji, Chuo-ku, Tokyo",
                    "latitude": 35.6654,
                    "longitude": 139.7707,
                    "specialty": "Cơm hải sản Uni, Toro tươi rói tại chỗ"
                }
            ]
        elif "đà nẵng" in city_lower:
            return [
                {
                    "name": "Bánh Xèo Bà Dưỡng",
                    "cuisine": "Local Street Food",
                    "rating": 4.7,
                    "price_avg": 120000.0,
                    "currency": "VND",
                    "address": "K280/23 Hoàng Diệu, Hải Châu, Đà Nẵng",
                    "latitude": 16.0520,
                    "longitude": 108.2150,
                    "specialty": "Bánh xèo giòn rụm & nước chấm đậu phụng"
                }
            ]
        else:
            return [
                {
                    "name": f"Nhà Hàng Đặc Sản {city}",
                    "cuisine": "Local Cuisine",
                    "rating": 4.6,
                    "price_avg": 250000.0,
                    "currency": "VND",
                    "address": f"Khu ẩm thực {city}",
                    "latitude": 37.56,
                    "longitude": 126.98,
                    "specialty": "Ẩm thực địa phương hấp dẫn"
                }
            ]

class MockActivityProvider(BaseActivityTool):
    def search_activities(
        self,
        city: str,
        categories: Optional[List[str]] = None,
        duration_days: int = 3
    ) -> List[Dict[str, Any]]:
        city_lower = city.lower()
        if "hàn quốc" in city_lower or "seoul" in city_lower or "korea" in city_lower:
            return [
                {
                    "name": "Cung Điện Gyeongbokgung & Thuê Áo Hanbok",
                    "category": "culture",
                    "price": 100000.0,
                    "currency": "VND",
                    "duration_minutes": 180,
                    "address": "161 Sajik-ro, Jongno-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5796,
                    "longitude": 126.9770,
                    "description": "Cung điện Hoàng Gia lớn nhất triều đại Joseon, miễn phí vé khi mặc trang phục Hanbok truyền thống."
                },
                {
                    "name": "Tháp N Seoul Tower & Cầu Khóa Tình Yêu Núi Namsan",
                    "category": "sightseeing",
                    "price": 280000.0,
                    "currency": "VND",
                    "duration_minutes": 150,
                    "address": "105 Namsangongwon-gil, Yongsan-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5512,
                    "longitude": 126.9882,
                    "description": "Biểu tượng lãng mạn của Seoul ngắm toàn cảnh thành phố rực rỡ từ đài quan sát."
                },
                {
                    "name": "Mua Sắm Phố Myeongdong & Trẻ Trung Hongdae",
                    "category": "shopping",
                    "price": 500000.0,
                    "currency": "VND",
                    "duration_minutes": 180,
                    "address": "Myeongdong & Hongdae, Seoul, Hàn Quốc",
                    "latitude": 37.5636,
                    "longitude": 126.9822,
                    "description": "Thiên đường mua sắm mỹ phẩm, thời trang K-Pop và nghệ thuật đường phố sinh viên."
                },
                {
                    "name": "Đảo Nami (Bối Cảnh Phim Bản Tình Ca Mùa Đông)",
                    "category": "nature",
                    "price": 320000.0,
                    "currency": "VND",
                    "duration_minutes": 240,
                    "address": "1 Namisum-gil, Namsan-myeon, Chuncheon, Gangwon-do, Hàn Quốc",
                    "latitude": 37.7914,
                    "longitude": 127.5255,
                    "description": "Hòn đảo hình bán nguyệt lãng mạn nổi tiếng với hai hàng cây bạch đàn lá vàng/băng tuyết thơ mộng."
                },
                {
                    "name": "Công Viên Giải Trí Lotte World & Lotte World Tower",
                    "category": "adventure",
                    "price": 750000.0,
                    "currency": "VND",
                    "duration_minutes": 210,
                    "address": "240 Olympic-ro, Songpa-gu, Seoul, Hàn Quốc",
                    "latitude": 37.5111,
                    "longitude": 127.0982,
                    "description": "Khu phức hợp công viên giải trí trong nhà lớn nhất thế giới cùng tòa tháp 123 tầng cao nhất Hàn Quốc."
                }
            ]
        elif "tokyo" in city_lower or "nhật" in city_lower:
            return [
                {
                    "name": "Chùa Asakusa Senso-ji & Phố Nakamise",
                    "category": "culture",
                    "price": 0.0,
                    "currency": "VND",
                    "duration_minutes": 150,
                    "address": "2-3-1 Asakusa, Taito-ku, Tokyo",
                    "latitude": 35.7148,
                    "longitude": 139.7967,
                    "description": "Ngôi chùa cổ nhất Tokyo với tháp 5 tầng."
                },
                {
                    "name": "Khu Phố Mua Sắm Ginza & Mua Sắm Shibuya 109",
                    "category": "shopping",
                    "price": 500000.0,
                    "currency": "VND",
                    "duration_minutes": 180,
                    "address": "Ginza & Shibuya, Tokyo",
                    "latitude": 35.6717,
                    "longitude": 139.7649,
                    "description": "Thiên đường mua sắm đồ hiệu."
                }
            ]
        else:
            return [
                {
                    "name": f"Tham quan & Khám phá {city}",
                    "category": "culture",
                    "price": 200000.0,
                    "currency": "VND",
                    "duration_minutes": 150,
                    "address": f"Center of {city}",
                    "latitude": 37.56,
                    "longitude": 126.98,
                    "description": "Danh lam thắng cảnh và văn hóa nổi tiếng địa phương"
                }
            ]
