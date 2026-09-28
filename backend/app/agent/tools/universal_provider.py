from typing import List, Dict, Any, Optional
from app.agent.tools.base import BaseFlightTool, BaseHotelTool, BaseRestaurantTool, BaseActivityTool
from app.services.geo_service import geo_service
from app.services.currency_service import currency_service

# Regional airline routes
INTERNATIONAL_AIRLINES_BY_REGION = {
    "EUROPE": [
        {"airline": "Vietnam Airlines / Air France", "hub": "CDG"},
        {"airline": "Emirates", "hub": "DXB"},
        {"airline": "Qatar Airways", "hub": "DOH"},
        {"airline": "Lufthansa", "hub": "FRA"}
    ],
    "ASIA": [
        {"airline": "Vietnam Airlines", "hub": "HAN/SGN"},
        {"airline": "Singapore Airlines", "hub": "SIN"},
        {"airline": "Korean Air", "hub": "ICN"},
        {"airline": "All Nippon Airways (ANA)", "hub": "HND/NRT"},
        {"airline": "Thai Airways", "hub": "BKK"}
    ],
    "AMERICAS": [
        {"airline": "Vietnam Airlines / Delta Air Lines", "hub": "NRT/ICN"},
        {"airline": "Japan Airlines / American Airlines", "hub": "HND"},
        {"airline": "United Airlines", "hub": "SFO"}
    ]
}

# Authentic city-level culinary catalog
CITY_CUISINES: Dict[str, List[Dict[str, str]]] = {
    "hallstatt": [
        {"name": "Nhà hàng Gasthof Simony Hallstatt", "specialty": "Cá hồi hồ Salzkammergut nướng bơ chanh & Bánh táo Apfelstrudel", "cuisine": "Ẩm thực truyền thống Áo"},
        {"name": "Brauhaus Hallstatt am See", "specialty": "Thịt bê chiên giòn Wiener Schnitzel & Bia thủ công địa phương", "cuisine": "Bia & Đồ nướng Áo"},
        {"name": "Quán Cafe Derbl bên Quảng trường chợ", "specialty": "Bánh ngọt Sachertorte sốt kem & Cà phê Viennese Melange", "cuisine": "Tiệm bánh & Cà phê cổ"},
        {"name": "Seecafé Hallstatt", "specialty": "Súp bí đỏ kem tươi & Bánh mì nướng bơ tỏi bên bờ hồ", "cuisine": "Ẩm thực nhẹ & Cà phê hồ"}
    ],
    "zermatt": [
        {"name": "Restaurant Schäferstube Zermatt", "specialty": "Lẩu phô mai Swiss Cheese Fondue & Thịt cừu nướng đá Valais", "cuisine": "Ẩm thực truyền thống Thụy Sĩ"},
        {"name": "Whymper-Stube Matterhorn", "specialty": "Bánh khoai tây bào chiên Rösti đút lò phô mai Raclette", "cuisine": "Đặc sản vùng núi Alps"},
        {"name": "Chez Vrony ngắm đỉnh Matterhorn", "specialty": "Thịt bò khô Bündnerfleisch & Rượu vang vùng Valais", "cuisine": "Fine Dining vùng núi"},
        {"name": "Pizzeria Ristorante Molino Zermatt", "specialty": "Pizza củi nướng phô mai Ý & Mì Ý nấm truffle tuyết", "cuisine": "Món Ý & Vùng núi"}
    ],
    "kyoto": [
        {"name": "Nhà hàng Kaiseki truyền thống Gion Karyo", "specialty": "Yến tiệc Kaiseki 9 món hoa nghệ thuật mùa lá phong / hoa anh đào", "cuisine": "Ẩm thực Cố đô Kaiseki"},
        {"name": "Quán Mì Udon Omen Gion", "specialty": "Mì Udon làm thủ công kèm mè rang thơm và rau củ tươi Kyoto", "cuisine": "Mì Nhật Bản gia truyền"},
        {"name": "Trà quán Uji Matcha Tsujiri Honten", "specialty": "Kem matcha nhiều tầng, bánh wagashi hoa sen và trà sencha cao cấp", "cuisine": "Trà đạo & Tráng miệng Nhật"},
        {"name": "Nhà hàng Chay Shojin Ryori Shigetsu", "specialty": "Ẩm thực chay chùa thiền Tenryu-ji thanh tịnh chuẩn Michelin", "cuisine": "Ẩm thực Chay Nhật Bản"}
    ],
    "osaka": [
        {"name": "Quán Takoyaki Kukuru Dotonbori", "specialty": "Bánh bạch tuộc Takoyaki sốt tương gừng thơm ngậy rắc cá ngừ bào", "cuisine": "Ẩm thực đường phố Osaka"},
        {"name": "Nhà hàng Bò Nướng Matsuzaka Beef Yakiniku M", "specialty": "Thịt bò Matsuzaka và Wagyu nướng than hồng mềm tan trong miệng", "cuisine": "Bò nướng cao cấp Yakiniku"},
        {"name": "Quán Okonomiyaki Mizuno", "specialty": "Bánh xèo Nhật Bản Okonomiyaki gia truyền từ năm 1945", "cuisine": "Bánh xèo Nhật Bản"},
        {"name": "Chợ Hải Sản Kuromon Ichiba", "specialty": "Sò điệp nướng mỡ hành, cá ngừ Otoro tươi sống & Cua tuyết hấp", "cuisine": "Hải sản tươi sống"}
    ],
    "tokyo": [
        {"name": "Ichiran Ramen Shinjuku", "specialty": "Mì Tonkotsu Ramen nước hầm xương heo đậm đà béo ngậy ô riêng tư", "cuisine": "Ramen Nhật Bản"},
        {"name": "Chợ Hải Sản Tsukiji Outer Market", "specialty": "Cơm hải sản Kaisen-don cá ngừ Toro tươi sống & Cầu gai Uni", "cuisine": "Sushi & Hải sản"},
        {"name": "Gyukatsu Motomura Akihabara", "specialty": "Bò cuộn bột rán tái nướng trên phiến đá nóng thơm lừng", "cuisine": "Bò chiên Nhật Bản"},
        {"name": "Torikizoku Roppongi", "specialty": "Xiên gà nướng Yakitori sốt tare đậm đà & Bia tươi mát lạnh", "cuisine": "Quán nhậu Izakaya"}
    ],
    "busan": [
        {"name": "Chợ Hải Sản Jagalchi Market Busan", "specialty": "Cua hoàng đế hấp gừng sả, cá tươi sashimi và lẩu hải sản cay Maeuntang", "cuisine": "Hải sản tươi sống Busan"},
        {"name": "Quán Canh Thịt Heo Ssangdung-i Dwaeji Gukbap", "specialty": "Canh hầm thịt heo Dwaeji Gukbap thơm nồng tỏi ớt ăn kèm kim chi giòn", "cuisine": "Đặc sản truyền thống Busan"},
        {"name": "Quán Mì Lạnh Milmyeon Halmae", "specialty": "Mì bột lúa mì nước dùng mát lạnh đập đá bào đặc sản cảng Busan", "cuisine": "Mì lạnh Busan"},
        {"name": "The Bay 101 Bờ Biển Haeundae", "specialty": "Cá tuyết chiên giòn Fish & Chips ngắm toàn cảnh du thuyền vịnh Marine City", "cuisine": "Ẩm thực ngắm cảnh đêm"}
    ],
    "jeju": [
        {"name": "Nhà Hàng Thịt Heo Đen Donsadon Jeju", "specialty": "Thịt lợn đen Jeju Heukdwaeji nướng than hoa chấm mắm cá cơm Meljeot", "cuisine": "Đặc sản Đảo Jeju"},
        {"name": "Quán Bào Ngư Myeongjin Jeonbok", "specialty": "Cơm niêu bào ngư nướng bơ tỏi Jeonbok dolsot-bap bổ dưỡng", "cuisine": "Hải sản bào ngư Jeju"},
        {"name": "Osulloc Tea Museum Cafe", "specialty": "Bánh kem trà xanh cuộn & Trà tuyết đồi chè hữu cơ Seogwipo", "cuisine": "Trà xanh & Tráng miệng"},
        {"name": "Quán Sashimi Bờ Biển Seongsan", "specialty": "Cá thu nướng than và gỏi hải sản bắt sống bởi các nữ thợ lặn Haenyeo", "cuisine": "Ẩm thực nữ hải nữ Haenyeo"}
    ],
    "seoul": [
        {"name": "Tosokchon Samgyetang Gyeongbokgung", "specialty": "Gà tần sâm tươi núi 6 năm tuổi nước dùng béo ngậy ngọt thanh", "cuisine": "Ẩm thực truyền thống Hàn Quốc"},
        {"name": "Myeongdong Kyoja Michelin", "specialty": "Bánh mì sủi cảo Mandu hấp mọng nước & Mì Kalguksu gia truyền", "cuisine": "Mì & Sủi cảo Hàn"},
        {"name": "Maple Tree House BBQ Hongdae", "specialty": "Thịt bò Hanwoo nướng than hoa mềm mọng ướp gia vị sốt lê", "cuisine": "Korean BBQ Thịt nướng"},
        {"name": "Chợ Gwangjang Market", "specialty": "Bánh xèo đậu xanh Bindaetteok giòn rụm & Thịt bò sống Yukhoe", "cuisine": "Ẩm thực chợ truyền thống"}
    ],
    "đà lạt": [
        {"name": "Lẩu Gà Lá É Tao Ngộ Đà Lạt", "specialty": "Lẩu gà thả đồi nấu lá é cay nồng măng chua ấm lòng đêm sương", "cuisine": "Đặc sản Đà Lạt"},
        {"name": "Lẩu Bò Ba Toa Nhà Gỗ Quán Xưa", "specialty": "Lẩu bắp bò mềm ngọt nước xương ống hầm củ quả thảo mộc", "cuisine": "Ẩm thực cao nguyên"},
        {"name": "Tiệm Bánh Căn Lệ & Sữa Đậu Nành Nóng", "specialty": "Bánh căn giòn rụm xíu mại trứng cút & Sữa hạt thơm lừng", "cuisine": "Ăn vặt đêm Đà Lạt"},
        {"name": "Quán Cà Phê Mây Đồi Dã Chiến", "specialty": "Cà phê Arabica Cầu Đất nguyên chất ngắm thung lũng đèn lãng mạn", "cuisine": "Cà phê ngắm cảnh"}
    ],
    "nha trang": [
        {"name": "Hải Sản Bờ Kè Tháp Bà Nha Trang", "specialty": "Tôm hùm nướng phô mai, mực một nắng nướng sa tế & ốc hương xào bơ tỏi", "cuisine": "Hải sản tươi sống Nha Trang"},
        {"name": "Quán Nem Nướng Đặng Văn Quyên", "specialty": "Nem nướng than hoa cuộn ram giòn rụm chấm nước sốt tôm thịt vàng óng", "cuisine": "Đặc sản Ninh Hòa Nha Trang"},
        {"name": "Quán Bún Sứa & Bún Chả Cá Năm Beo", "specialty": "Bún sứa biển giòn sần sật nước dùng cá thu thanh ngọt", "cuisine": "Ẩm thực biển dân dã"},
        {"name": "Sailing Club Nha Trang Ven Biển", "specialty": "Cocktail miền nhiệt đới & Bò bít tết hảo hạng nghe sóng vỗ", "cuisine": "Nhà hàng & Bar bãi biển"}
    ],
    "sa pa": [
        {"name": "Nhà hàng Ẩm Thực Sa Pa Bản Cát Cát", "specialty": "Thịt lợn cắp nách nướng than hoa & Cá hồi Thác Bạc nướng giấy bạc", "cuisine": "Đặc sản Tây Bắc"},
        {"name": "Quán Thắng Cố A Quỳnh Sa Pa", "specialty": "Nồi lẩu Thắng Cố ngựa gia truyền thảo quả quế hồi & Rượu ngô nồng ấm", "cuisine": "Ẩm thực bản địa H'Mông"},
        {"name": "Quán Nướng Than Phố Cầu Mây", "specialty": "Xiên bò cuộn cải mèo nướng, nấm kim châm và cơm lam dẻo thơm", "cuisine": "Ẩm thực phố đêm Sa Pa"},
        {"name": "Cà phê Fansipan Legend Ngắm Mây", "specialty": "Trà đào quế táo đỏ & Cà phê nóng bồng bềnh giữa biển mây", "cuisine": "Cà phê săn mây"}
    ],
    "đà nẵng": [
        {"name": "Bánh Tráng Cuốn Thịt Heo Đại Lộc", "specialty": "Thịt heo hai đầu da giòn ngọt cuốn bánh tráng chấm mắm nêm đậm đà", "cuisine": "Đặc sản Đà Nẵng"},
        {"name": "Hải Sản Bé Mặn Đường Võ Nguyên Giáp", "specialty": "Ghẹ rang me, tôm sú nướng muối ớt & Cháo hàu biển tươi", "cuisine": "Hải sản tươi sống Đà Nẵng"},
        {"name": "Bún Chả Cá Bà Hờn", "specialty": "Bún chả cá thu cá ngừ nước lèo bí đỏ ngọt thanh gia truyền 40 năm", "cuisine": "Ẩm thực xứ Quảng"},
        {"name": "Cà Phê Bờ Sông Hàn Ngắm Cầu Rồng", "specialty": "Cà phê dừa béo ngậy ngắm cảnh Cầu Rồng phun lửa về đêm", "cuisine": "Cà phê ngắm cảnh sông Hàn"}
    ],
    "paris": [
        {"name": "Bistrot Chez Janou Le Marais", "specialty": "Thịt vịt hầm Confit de Canard & Chậu mousse sô cô la không giới hạn", "cuisine": "Bistrot truyền thống Paris"},
        {"name": "Le Bouillon Chartier Montmartre", "specialty": "Ốc sên nướng bơ tỏi Escargots de Bourgogne & Bò sốt vang đỏ", "cuisine": "Ẩm thực Pháp cổ điển"},
        {"name": "Café de Flore Boulevard Saint-Germain", "specialty": "Bánh sừng bò Croissant giòn rụm & Sô cô la nóng kiểu Pháp", "cuisine": "Quán Cà phê di sản Paris"},
        {"name": "Nhà hàng Du Thuyền Bateaux Parisiens", "specialty": "Fine dining 4 món thượng hạng ngắm tháp Eiffel rực sáng trên sông Seine", "cuisine": "Fine Dining du thuyền"}
    ]
}

# Authentic city-level activity catalog
CITY_ACTIVITIES: Dict[str, List[Dict[str, Any]]] = {
    "hallstatt": [
        {"title": "Dạo bộ Làng Cổ Hallstatt & Chụp ảnh Viewpoint Skywalk", "type": "ATTRACTION", "desc": "Ngắm toàn cảnh ngôi làng cổ tích phản chiếu trên mặt hồ phẳng lặng", "cost": 0.0},
        {"title": "Thám hiểm Mỏ Muối Cổ Salzwelten Hallstatt (7000 năm tuổi)", "type": "ACTIVITY", "desc": "Trải nghiệm đường trượt gỗ thợ mỏ và đi tàu điện ngầm dưới lòng núi đá", "cost": 950000.0},
        {"title": "Du thuyền ngắm cảnh Hồ Hallstätter See", "type": "ACTIVITY", "desc": "Thưởng ngoạn không khí trong lành giữa thung lũng núi Dachstein", "cost": 420000.0},
        {"title": "Khu Nhà Thờ Xương Beinhaus Charnel House", "type": "ATTRACTION", "desc": "Di tích lịch sử độc đáo với hơn 600 hộp sọ được vẽ hoa nghệ thuật", "cost": 150000.0}
    ],
    "zermatt": [
        {"title": "Tàu bánh răng Gornergrat ngắm Đỉnh Matterhorn hùng vĩ", "type": "ACTIVITY", "desc": "Tuyến tàu leo núi nổi tiếng nhất ngắm 29 đỉnh núi phủ tuyết trắng xóa", "cost": 2100000.0},
        {"title": "Khám phá Làng Cổ Zermatt & Tuyến Phố Không Khói Xe Bahnhofstrasse", "type": "ATTRACTION", "desc": "Đi dạo giữa những ngôi nhà gỗ truyền thống nghìn năm tuổi", "cost": 0.0},
        {"title": "Cáp treo Matterhorn Glacier Paradise cao nhất châu Âu", "type": "ACTIVITY", "desc": "Tham quan cung điện băng trong lòng sông băng vĩnh cửu", "cost": 2500000.0},
        {"title": "Hồ Riffelsee Phản Chiếu Bóng Matterhorn", "type": "ATTRACTION", "desc": "Hồ nước trên núi tuyệt đẹp chụp ảnh phản chiếu đỉnh núi huyền thoại", "cost": 0.0}
    ],
    "kyoto": [
        {"title": "Chùa Vàng Kinkaku-ji Lộng Lẫy Giữa Hồ Nước", "type": "ATTRACTION", "desc": "Ngôi chùa dát vàng biểu tượng Kyoto soi bóng lung linh trên mặt hồ gương", "cost": 120000.0},
        {"title": "Đền Ngàn Cổng Đỏ Fushimi Inari Taisha", "type": "ATTRACTION", "desc": "Đường hầm hàng ngàn cổng Torii đỏ thắm chạy dài qua núi rừng thiêng", "cost": 0.0},
        {"title": "Rừng Trúc Xanh Arashiyama & Cầu Togetsukyo", "type": "ATTRACTION", "desc": "Con đường tre trúc rì rào xanh ngắt dẫn đến chùa cổ Tenryu-ji", "cost": 0.0},
        {"title": "Phố Cổ Gion & Gặp Gỡ Nghệ Nhân Geisha", "type": "ACTIVITY", "desc": "Khu phố đèn lồng gỗ cổ kính với cơ hội bắt gặp Geisha kiêu sa", "cost": 350000.0}
    ],
    "osaka": [
        {"title": "Lâu Đài Cổ Kính Osaka Castle & Công Viên Vườn Hoa", "type": "ATTRACTION", "desc": "Biểu tượng lịch sử hào hùng của tướng quân Toyotomi Hideyoshi", "cost": 150000.0},
        {"title": "Phố Đèn Neon Dotonbori & Check-in Biển Hiệu Glico Man", "type": "ATTRACTION", "desc": "Trung tâm giải trí rực rỡ nhất Osaka bên bờ kênh tấp nập thuyền bè", "cost": 0.0},
        {"title": "Khu Giải Trí Universal Studios Japan (USJ)", "type": "ACTIVITY", "desc": "Thế giới phù thủy Harry Potter và công viên Super Nintendo World đỉnh cao", "cost": 1800000.0},
        {"title": "Đài Quan Sát Tòa Nhà Umeda Sky Building Floating Garden", "type": "ATTRACTION", "desc": "Ngắm toàn cảnh thành phố Osaka 360 độ từ cầu kính treo lơ lửng", "cost": 350000.0}
    ],
    "tokyo": [
        {"title": "Chùa Cổ Asakusa Senso-ji & Phố Đèn Lồng Đỏ Nakamise", "type": "ATTRACTION", "desc": "Ngôi chùa cổ kính nhất Tokyo với tháp 5 tầng và cổng Kaminarimon", "cost": 0.0},
        {"title": "Tháp Tokyo Skytree & Ngắm Núi Phú Sĩ Từ Trên Cao", "type": "ATTRACTION", "desc": "Tháp truyền hình cao nhất thế giới ngắm toàn cảnh thủ đô Tokyo", "cost": 480000.0},
        {"title": "Trải Nghiệm Nghệ Thuật Kỹ Thuật Số teamLab Planets Tokyo", "type": "ACTIVITY", "desc": "Không gian ánh sáng tương tác vô cực đỉnh cao nghệ thuật thị giác", "cost": 750000.0},
        {"title": "Giao Lộ Shibuya Hối Hả & Phố Trẻ Harajuku", "type": "SHOPPING", "desc": "Giao lộ đông đúc nhất hành tinh và phố thời trang độc đáo Takeshita", "cost": 0.0}
    ],
    "busan": [
        {"title": "Bãi Biển Haeundae & Du Thuyền Ngắm Cầu Gwangan", "type": "ATTRACTION", "desc": "Bãi biển đẹp nhất Hàn Quốc với bờ cát trắng mịn và lễ hội biển sôi động", "cost": 450000.0},
        {"title": "Làng Văn Hóa Gamcheon Lộng Lẫy Sắc Màu", "type": "ATTRACTION", "desc": "Được mệnh danh Santorini của châu Á với những ngôi nhà bậc thang rực rỡ", "cost": 0.0},
        {"title": "Đền Cổ Haedong Yonggungsa Bên Vách Đá Biển", "type": "ATTRACTION", "desc": "Ngôi chùa phật giáo hiếm hoi xây dựng sát mép biển nghe sóng vỗ rì rào", "cost": 0.0},
        {"title": "Tàu Cáp Treo Trên Không Busan Air Cruise Songdo", "type": "ACTIVITY", "desc": "Trải nghiệm cáp treo đáy kính vượt biển ngắm vịnh Songdo tuyệt đẹp", "cost": 380000.0}
    ],
    "jeju": [
        {"title": "Chinh Phục Đỉnh Núi Lửa Hallasan Hùng Vĩ", "type": "ATTRACTION", "desc": "Đỉnh núi cao nhất Hàn Quốc với hồ nước miệng núi lửa và thảm thực vật kỳ thú", "cost": 0.0},
        {"title": "Đỉnh Mặt Trời Mọc Seongsan Ilchulbong", "type": "ATTRACTION", "desc": "Di sản thiên nhiên thế giới UNESCO với đài hình nón nhô ra biển Thái Bình Dương", "cost": 120000.0},
        {"title": "Hang Động Dung Nham Manjanggul Cave", "type": "ACTIVITY", "desc": "Hệ thống ống dung nham ngầm dưới đất kỳ vĩ hàng triệu năm tuổi", "cost": 100000.0},
        {"title": "Thác Nước Cheonjiyeon & Con Đường Bờ Biển Seopjikoji", "type": "ATTRACTION", "desc": "Dải đất ven biển thơ mộng xuất hiện trong hàng loạt bộ phim truyền hình Hàn", "cost": 80000.0}
    ],
    "seoul": [
        {"title": "Cung Điện Hoàng Gia Gyeongbokgung & Thuê Áo Hanbok", "type": "ATTRACTION", "desc": "Tham quan cung điện lớn nhất Joseon, miễn phí vé khi mặc áo Hanbok", "cost": 150000.0},
        {"title": "Tháp N Seoul Tower & Cầu Khóa Tình Yêu Núi Namsan", "type": "ATTRACTION", "desc": "Ngắm toàn cảnh Seoul lung linh về đêm từ đài quan sát trên cao", "cost": 380000.0},
        {"title": "Mua Sắm & Khám Phá Phố Trẻ Hongdae - Myeongdong", "type": "SHOPPING", "desc": "Thiên đường mua sắm mỹ phẩm, thời trang và nghệ thuật biểu diễn đường phố", "cost": 500000.0},
        {"title": "Làng Cổ Hanok Bukchon Truyền Thống", "type": "ATTRACTION", "desc": "Ngắm những ngôi nhà cổ xưa gìn giữ nét văn hóa nguyên vẹn giữa lòng thủ đô", "cost": 0.0}
    ],
    "đà lạt": [
        {"title": "Quảng Trường Lâm Viên & Dạo Bộ Hồ Xuân Hương", "type": "ATTRACTION", "desc": "Biểu tượng nụ hoa Atiso và hoa dã quỳ khổng lồ bên mặt hồ thơ mộng", "cost": 0.0},
        {"title": "Khu Du Lịch Thác Datanla & Máng Trượt Dài Nhất Đông Nam Á", "type": "ACTIVITY", "desc": "Trải nghiệm máng trượt xuyên rừng thông nguyên sinh đổ dồn xuống thác nước", "cost": 250000.0},
        {"title": "Chinh Phục Đỉnh Langbiang Huyền Thoại", "type": "ACTIVITY", "desc": "Đi xe Jeep vượt dốc đứng ngắm trọn vẹn thành phố mộng mơ từ độ cao 2.167m", "cost": 150000.0},
        {"title": "Dinh III Bảo Đại & Vườn Hoa Cẩm Tú Cầu Cầu Đất", "type": "ATTRACTION", "desc": "Dinh thự nghỉ mát của vị hoàng đế cuối cùng và đồi hoa rực rỡ sắc màu", "cost": 100000.0}
    ],
    "nha trang": [
        {"title": "Tour Du Thuyền 4 Đảo & Lặn Ngắm San Hô Hòn Mun", "type": "ACTIVITY", "desc": "Khu bảo tồn sinh vật biển rực rỡ với làn nước trong vắt nhìn thấu đáy", "cost": 650000.0},
        {"title": "Quần Thể Di Tích Tháp Bà Ponagar & Tắm Bùn Khoáng I-Resort", "type": "ATTRACTION", "desc": "Di tích văn hóa Chăm pa ngàn năm tuổi và thư giãn tắm bùn khoáng nóng", "cost": 300000.0},
        {"title": "Tổ Hợp Vui Chơi VinWonders Hòn Tre & Cáp Treo Vượt Biển", "type": "ACTIVITY", "desc": "Cáp treo vượt biển vịnh Nha Trang và thế giới trò chơi mạo hiểm công viên nước", "cost": 950000.0},
        {"title": "Chùa Long Sơn Tượng Phật Trắng Kim Thân Phật Tổ", "type": "ATTRACTION", "desc": "Bức tượng Phật ngoài trời lớn nhất Nha Trang tọa lạc trên đỉnh đồi Trại Thủy", "cost": 0.0}
    ],
    "sa pa": [
        {"title": "Khám Phá Bản Cát Cát Của Người H'Mông & Thác Tiên Sa", "type": "ATTRACTION", "desc": "Bản làng cổ tích đẹp nhất vùng Tây Bắc với cối xay nước khổng lồ và nhà gỗ", "cost": 150000.0},
        {"title": "Chinh Phục Đỉnh Fansipan 3.143m - Nóc Nhà Đông Dương", "type": "ACTIVITY", "desc": "Tuyến cáp treo Sun World vượt thung lũng Mường Hoa chạm tay vào cột mốc nóc nhà", "cost": 850000.0},
        {"title": "Đèo Ô Quy Hồ & Cầu Kính Rồng Mây Săn Hoàng Hôn", "type": "ATTRACTION", "desc": "Tứ đại đỉnh đèo hiểm trở ngắm hoàng hôn đỏ rực buông trên dãy Hoàng Liên Sơn", "cost": 400000.0},
        {"title": "Nhà Thờ Đá Sa Pa & Chợ Phiên Tình Yêu", "type": "ATTRACTION", "desc": "Dấu ấn kiến trúc Pháp cổ bằng đá và không khí nhộn nhịp văn hóa thổ cẩm", "cost": 0.0}
    ],
    "đà nẵng": [
        {"title": "Khu Du Lịch Bà Nà Hills & Check-in Cầu Vàng Bàn Tay Khổng Lồ", "type": "ACTIVITY", "desc": "Cây cầu vàng huyền thoại được nâng đỡ bởi bàn tay rêu phong vươn giữa mây trời", "cost": 950000.0},
        {"title": "Bán Đảo Sơn Trà & Viếng Chùa Linh Ứng Tượng Phật Bà 67m", "type": "ATTRACTION", "desc": "Ngắm voọc chà vá chân nâu quý hiếm và toàn cảnh bờ biển Đà Nẵng từ trên cao", "cost": 0.0},
        {"title": "Danh Thắng Ngũ Hành Sơn & Động Huyền Không Huyền Bí", "type": "ATTRACTION", "desc": "Hệ thống 5 ngọn núi đá vôi kỳ vĩ cùng hang động và chùa tháp cổ kính", "cost": 50000.0},
        {"title": "Dạo Bộ Cầu Rồng Phun Lửa & Du Thuyền Sông Hàn Về Đêm", "type": "ACTIVITY", "desc": "Thưởng thức màn trình diễn phun lửa phun nước kỳ thú của Cầu Rồng biểu tượng", "cost": 200000.0}
    ],
    "paris": [
        {"title": "Bảo Tàng Nghệ Thuật Musée du Louvre & Chiêm Ngưỡng Nàng Mona Lisa", "type": "ATTRACTION", "desc": "Bảo tàng lớn nhất thế giới lưu giữ kiệt tác nghệ thuật vô giá nhân loại", "cost": 550000.0},
        {"title": "Lên Đài Quan Sát Tháp Eiffel & Ngắm Toàn Cảnh Paris", "type": "ATTRACTION", "desc": "Biểu tượng kinh đô ánh sáng ngắm toàn cảnh thung lũng sông Seine", "cost": 750000.0},
        {"title": "Du Thuyền Sông Seine Ngắm Hoàng Hôn Paris", "type": "ACTIVITY", "desc": "Lướt nhẹ qua Nhà thờ Đức Bà, Cầu Pont Alexandre III và các cung điện cổ", "cost": 450000.0},
        {"title": "Khám Phá Đồi Nghệ Thuật Montmartre & Vương Cung Thánh Đường Sacré-Cœur", "type": "ATTRACTION", "desc": "Ngọn đồi lãng mạn nơi hội tụ các danh họa và quang cảnh Paris từ bậc thang đá", "cost": 0.0}
    ]
}

class UniversalFlightProvider(BaseFlightTool):
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: Optional[str] = None,
        travelers: int = 1
    ) -> List[Dict[str, Any]]:
        geo = geo_service.resolve_destination(destination)
        airport = geo.get("nearest_airport", {})
        dest_airport_code = airport.get("iata", "INTL")
        dest_country = geo.get("country", destination)
        code = geo.get("country_code", "XX")

        # Determine route & airlines
        if code in ["AT", "CH", "FR", "DE", "IT", "ES", "NL", "UK", "IS", "NO"]:
            airlines = INTERNATIONAL_AIRLINES_BY_REGION["EUROPE"]
            base_price = 14500000.0
            duration_str = "13h 45m (1 stop)"
        elif code in ["US", "CA"]:
            airlines = INTERNATIONAL_AIRLINES_BY_REGION["AMERICAS"]
            base_price = 19500000.0
            duration_str = "16h 20m (1 stop)"
        elif code in ["JP", "KR"]:
            airlines = INTERNATIONAL_AIRLINES_BY_REGION["ASIA"]
            base_price = 7800000.0
            duration_str = "4h 45m (Direct)"
        elif code in ["TH", "SG", "MY"]:
            airlines = INTERNATIONAL_AIRLINES_BY_REGION["ASIA"]
            base_price = 3200000.0
            duration_str = "2h 10m (Direct)"
        else:
            airlines = INTERNATIONAL_AIRLINES_BY_REGION["ASIA"]
            base_price = 2200000.0 if code == "VN" else 12500000.0
            duration_str = "1h 30m" if code == "VN" else "8h 30m"

        results = []
        flight_times = [
            ("00:45", "06:30"),
            ("08:15", "14:50"),
            ("19:30", "07:15 (+1)")
        ]
        
        for idx, fl in enumerate(airlines[:3]):
            dep, arr = flight_times[idx % len(flight_times)]
            results.append({
                "flight_number": f"{fl['airline'][:2].upper()}{100 + idx * 25}",
                "airline": fl["airline"],
                "origin": origin,
                "destination": f"{destination} ({dest_airport_code})",
                "nearest_airport_name": airport.get("name", "International Airport"),
                "departure_time": dep,
                "arrival_time": arr,
                "duration": duration_str,
                "price_per_person": base_price + idx * 800000.0,
                "currency": "VND",
                "stops": 0 if "Direct" in duration_str else 1
            })
        return results

class UniversalHotelProvider(BaseHotelTool):
    def search_hotels(
        self,
        city: str,
        budget_tier: Optional[str] = "MEDIUM",
        preferences: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        geo = geo_service.resolve_destination(city)
        c_name = geo["city_or_village"]
        country = geo["country"]
        code = geo.get("country_code", "XX")
        lat = geo["latitude"]
        lon = geo["longitude"]

        # Base pricing per night based on country tier
        if code in ["CH", "NO", "IS", "US"]:
            base_rate = 4200000.0
        elif code in ["AT", "FR", "DE", "IT", "JP", "KR", "AU", "SG"]:
            base_rate = 2600000.0
        elif code in ["TH", "VN", "MY", "ID", "PH"]:
            base_rate = 1100000.0
        else:
            base_rate = 1900000.0

        hotels = [
            {
                "id": f"h_{abs(hash(c_name)) % 1000}_1",
                "name": f"Heritage Boutique Hotel & Chalet {c_name}",
                "district": f"Trung tâm lịch sử {c_name}",
                "rating": 4.9,
                "star_rating": 5,
                "price_per_night": round(base_rate * 1.35, -4),
                "currency": "VND",
                "address": f"Khu trung tâm di sản, {c_name}, {country}",
                "latitude": round(lat + 0.002, 4),
                "longitude": round(lon + 0.003, 4),
                "amenities": ["Toàn cảnh view đẹp", "Bữa sáng Buffet cao cấp", "Xe đưa đón sân bay", "Free Wi-Fi"]
            },
            {
                "id": f"h_{abs(hash(c_name)) % 1000}_2",
                "name": f"{c_name} Panorama Viewpoint Lodge & Suites",
                "district": f"Ven đồi ngắm cảnh {c_name}",
                "rating": 4.7,
                "star_rating": 4,
                "price_per_night": round(base_rate * 0.95, -4),
                "currency": "VND",
                "address": f"Khu ngắm cảnh bình minh, {c_name}, {country}",
                "latitude": round(lat - 0.003, 4),
                "longitude": round(lon - 0.002, 4),
                "amenities": ["Ban công view núi/hồ", "Nhà hàng ẩm thực bản địa", "Tour guide địa phương"]
            },
            {
                "id": f"h_{abs(hash(c_name)) % 1000}_3",
                "name": f"Traditional Guesthouse & Homestay {c_name}",
                "district": f"Làng cổ {c_name}",
                "rating": 4.6,
                "star_rating": 3,
                "price_per_night": round(base_rate * 0.65, -4),
                "currency": "VND",
                "address": f"Khu dân cư truyền thống, {c_name}, {country}",
                "latitude": round(lat + 0.001, 4),
                "longitude": round(lon - 0.004, 4),
                "amenities": ["Trải nghiệm đời sống bản địa", "Bếp gia đình ấm cúng", "Giá cả hợp lý"]
            }
        ]
        return hotels

class UniversalRestaurantProvider(BaseRestaurantTool):
    def search_restaurants(
        self,
        city: str,
        cuisine_types: Optional[List[str]] = None,
        price_range: Optional[str] = "MEDIUM"
    ) -> List[Dict[str, Any]]:
        geo = geo_service.resolve_destination(city)
        c_name = geo["city_or_village"]
        country = geo["country"]
        code = geo.get("country_code", "XX")
        lat = geo["latitude"]
        lon = geo["longitude"]
        c_lower = c_name.lower().strip()

        # Base price per meal
        if code in ["CH", "NO", "IS"]:
            base_meal = 750000.0
        elif code in ["AT", "FR", "DE", "IT", "JP", "KR", "US", "AU"]:
            base_meal = 420000.0
        elif code in ["VN", "TH", "ID"]:
            base_meal = 180000.0
        else:
            base_meal = 300000.0

        # Check city-level catalog first
        for key, dishes in CITY_CUISINES.items():
            if key in c_lower:
                rests = []
                for idx, r in enumerate(dishes):
                    rests.append({
                        "name": r["name"],
                        "cuisine": r["cuisine"],
                        "rating": round(4.9 - idx * 0.1, 1),
                        "price_avg": round(base_meal * (1.0 + idx * 0.2), -4),
                        "currency": "VND",
                        "address": f"Khu ẩm thực {c_name}, {country}",
                        "latitude": round(lat + (idx * 0.002 - 0.002), 4),
                        "longitude": round(lon + (idx * 0.002 - 0.001), 4),
                        "specialty": r["specialty"]
                    })
                return rests

        # Dynamic authentic restaurants for any global village/city
        return [
            {
                "name": f"Nhà hàng Đặc Sản Truyền Thống {c_name}",
                "cuisine": f"Ẩm thực bản địa {country}",
                "rating": 4.9,
                "price_avg": round(base_meal, -4),
                "currency": "VND",
                "address": f"Quảng trường trung tâm {c_name}, {country}",
                "latitude": round(lat + 0.0015, 4),
                "longitude": round(lon + 0.0010, 4),
                "specialty": f"Các món ăn truyền thống gia truyền trứ danh của vùng {c_name}"
            },
            {
                "name": f"Quán Ăn Dân Dã & Cafe Phố Cổ {c_name}",
                "cuisine": "Ẩm thực gia đình & Cafe view đẹp",
                "rating": 4.8,
                "price_avg": round(base_meal * 0.75, -4),
                "currency": "VND",
                "address": f"Góc phố cổ di sản, {c_name}, {country}",
                "latitude": round(lat - 0.0020, 4),
                "longitude": round(lon + 0.0015, 4),
                "specialty": f"Bánh nướng nóng hổi và đồ uống đặc sản truyền thống của {c_name}"
            },
            {
                "name": f"Nhà Hàng View Toàn Cảnh {c_name} Panorama",
                "cuisine": "Fine Dining & Rượu Vang Bản Địa",
                "rating": 4.9,
                "price_avg": round(base_meal * 1.4, -4),
                "currency": "VND",
                "address": f"Điểm ngắm hoàng hôn, {c_name}, {country}",
                "latitude": round(lat + 0.0035, 4),
                "longitude": round(lon - 0.0025, 4),
                "specialty": f"Bữa tối lãng mạn ngắm hoàng hôn buông xuống thung lũng {c_name}"
            },
            {
                "name": f"Bistro Ẩm Thực Tươi Sống {c_name}",
                "cuisine": "Hải sản & Nông sản theo mùa",
                "rating": 4.7,
                "price_avg": round(base_meal * 0.9, -4),
                "currency": "VND",
                "address": f"Khu chợ ẩm thực, {c_name}, {country}",
                "latitude": round(lat - 0.0012, 4),
                "longitude": round(lon - 0.0030, 4),
                "specialty": f"Món ăn thơm ngon chế biến từ nông sản tươi sạch vùng {c_name}"
            }
        ]

class UniversalActivityProvider(BaseActivityTool):
    def search_activities(
        self,
        city: str,
        categories: Optional[List[str]] = None,
        duration_days: int = 3
    ) -> List[Dict[str, Any]]:
        geo = geo_service.resolve_destination(city)
        c_name = geo["city_or_village"]
        country = geo["country"]
        code = geo.get("country_code", "XX")
        lat = geo["latitude"]
        lon = geo["longitude"]
        c_lower = c_name.lower().strip()

        # Check city-level catalog first
        for key, acts in CITY_ACTIVITIES.items():
            if key in c_lower:
                results = []
                for idx, a in enumerate(acts):
                    results.append({
                        "name": a["title"],
                        "category": a["type"].lower(),
                        "price": a["cost"],
                        "currency": "VND",
                        "duration_minutes": 150 + idx * 20,
                        "address": f"{c_name}, {country}",
                        "latitude": round(lat + (idx * 0.003 - 0.003), 4),
                        "longitude": round(lon + (idx * 0.003 - 0.002), 4),
                        "description": a["desc"]
                    })
                return results

        # Dynamic authentic activities for any global village/city
        return [
            {
                "name": f"Khám phá Phố Cổ & Di Sản Lịch Sử {c_name}",
                "category": "culture",
                "price": 0.0,
                "currency": "VND",
                "duration_minutes": 150,
                "address": f"Trung tâm lịch sử {c_name}, {country}",
                "latitude": round(lat + 0.001, 4),
                "longitude": round(lon + 0.002, 4),
                "description": f"Dạo bước trên những con đường đá cuội cổ kính và chiêm ngưỡng kiến trúc đặc sắc của {c_name}."
            },
            {
                "name": f"Chinh phục Điểm Ngắm Cảnh Toàn Cảnh (Viewpoint) {c_name}",
                "category": "nature",
                "price": 250000.0,
                "currency": "VND",
                "duration_minutes": 180,
                "address": f"Đài quan sát đỉnh đồi ngắm cảnh, {c_name}, {country}",
                "latitude": round(lat + 0.004, 4),
                "longitude": round(lon - 0.003, 4),
                "description": f"Ngắm trọn vẹn thung lũng, thiên nhiên và mái nhà cổ tích của {c_name} từ trên cao."
            },
            {
                "name": f"Trải nghiệm Văn Hóa & Nghề Thủ Công Bản Địa {c_name}",
                "category": "activity",
                "price": 450000.0,
                "currency": "VND",
                "duration_minutes": 120,
                "address": f"Làng nghề nghệ nhân truyền thống, {c_name}, {country}",
                "latitude": round(lat - 0.002, 4),
                "longitude": round(lon - 0.002, 4),
                "description": f"Tự tay trải nghiệm sản phẩm văn hóa đặc sắc cùng các nghệ nhân bản địa {country}."
            },
            {
                "name": f"Chợ Đêm & Mua Sắm Quà Lưu Niệm Bản Địa {c_name}",
                "category": "shopping",
                "price": 300000.0,
                "currency": "VND",
                "duration_minutes": 120,
                "address": f"Khu chợ truyền thống {c_name}, {country}",
                "latitude": round(lat - 0.001, 4),
                "longitude": round(lon + 0.003, 4),
                "description": f"Khám phá các gian hàng thủ công, đồ lưu niệm và món ăn vặt về đêm."
            },
            {
                "name": f"Du Thuyền / Xe Ngựa Ngắm Cảnh Thiên Nhiên {c_name}",
                "category": "relaxation",
                "price": 380000.0,
                "currency": "VND",
                "duration_minutes": 90,
                "address": f"Khu bến thuyền ngắm cảnh, {c_name}, {country}",
                "latitude": round(lat + 0.0025, 4),
                "longitude": round(lon + 0.0015, 4),
                "description": f"Hòa mình vào không gian bình yên trong lành của cảnh sắc thiên nhiên {c_name}."
            }
        ]
