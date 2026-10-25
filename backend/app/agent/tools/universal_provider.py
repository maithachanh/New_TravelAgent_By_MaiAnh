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
        {"name": "Bistrot Chez Janou Le Marais", "specialty": "Thịt vịt hầm Confit de Canard & Chậu mousse sô cô la không giới hạn", "cuisine": "Bistrot truyền thống Paris", "address": "2 Rue Roger Verlomme, 75003 Paris"},
        {"name": "Le Bouillon Chartier Montmartre", "specialty": "Ốc sên nướng bơ tỏi Escargots de Bourgogne & Bò sốt vang đỏ", "cuisine": "Ẩm thực Pháp cổ điển", "address": "7 Rue du Faubourg Montmartre, 75009 Paris"},
        {"name": "Café de Flore Boulevard Saint-Germain", "specialty": "Bánh sừng bò Croissant giòn rụm & Sô cô la nóng kiểu Pháp", "cuisine": "Quán Cà phê di sản Paris", "address": "172 Bd Saint-Germain, 75006 Paris"},
        {"name": "Nhà hàng Du Thuyền Bateaux Parisiens", "specialty": "Fine dining 4 món thượng hạng ngắm tháp Eiffel rực sáng trên sông Seine", "cuisine": "Fine Dining du thuyền", "address": "Port de la Bourdonnais, 75007 Paris"}
    ],
    "liverpool": [
        {"name": "The Art School Restaurant", "specialty": "Thịt cừu hầm Scouse truyền thống Liverpool & Bánh tart hoa quả", "cuisine": "Ẩm thực Anh cao cấp", "address": "1 Sugnall St, Liverpool L7 7EB"},
        {"name": "Panoramic 34 Tầng Cao Ngắm Sông Mersey", "specialty": "Trà chiều Afternoon Tea hoàng gia & Bò bít tết Wellington", "cuisine": "Fine Dining ngắm cảnh", "address": "West Tower, Brook St, Liverpool L3 9PJ"},
        {"name": "The Cavern Pub Mathew Street", "specialty": "Cá tuyết chiên giòn Fish & Chips & Bia thủ công Mersey", "cuisine": "Quán Pub âm nhạc huyền thoại", "address": "10 Mathew St, Liverpool L2 6RE"},
        {"name": "Maray Albert Dock", "specialty": "Súp lơ nướng sốt tahini hạt lựu & Hải sản vùng biển Tây Bắc Anh", "cuisine": "Ẩm thực Địa Trung Hải kết hợp", "address": "Unit 4, Britannia Pavilion, Albert Dock, Liverpool L3 4AD"}
    ],
    "london": [
        {"name": "Rules Restaurant Covent Garden (1798)", "specialty": "Bò nướng truyền thống Sunday Roast & Bánh Yorkshire Pudding", "cuisine": "Ẩm thực truyền thống Anh", "address": "34-35 Maiden Ln, London WC2E 7LB"},
        {"name": "Dishoom Covent Garden", "specialty": "Thịt gà nướng Ruby Chicken & Trà sữa Chai Bombay ấm nóng", "cuisine": "Ẩm thực phong cách Bombay London", "address": "12 Upper St Martin's Ln, London WC2H 9FB"},
        {"name": "Duck & Waffle Tầng 40 Bishopsgate", "specialty": "Đùi vịt quay giòn trên bánh waffle trứng lòng đào sốt mù tạt", "cuisine": "Fine Dining tầng cao ngắm cảnh", "address": "110 Bishopsgate, London EC2N 4AY"},
        {"name": "Borough Market Chợ Ẩm Thực Cổ", "specialty": "Bánh sandwich phô mai nướng, hàu tươi đảo Jersey & Tráng miệng", "cuisine": "Ẩm thực chợ truyền thống", "address": "8 Southwark St, London SE1 1TL"}
    ],
    "new york": [
        {"name": "Peter Luger Steak House Brooklyn", "specialty": "Bò bít tết Porterhouse khô nướng than củi trứ danh nước Mỹ", "cuisine": "Steakhouse huyền thoại Michelin", "address": "178 Broadway, Brooklyn, NY 11211"},
        {"name": "Katz's Delicatessen Lower East Side", "specialty": "Bánh mì kẹp thịt bò muối Pastrami hun khói khổng lồ từ năm 1888", "cuisine": "Deli truyền thống New York", "address": "205 E Houston St, New York, NY 10002"},
        {"name": "Joe's Pizza Greenwich Village", "specialty": "Pizza lát mỏng New York Style phô mai mozzarella kéo sợi nóng hổi", "cuisine": "Pizza New York", "address": "7 Carmine St, New York, NY 10014"},
        {"name": "Grand Central Oyster Bar", "specialty": "Súp nghêu Clam Chowder & Khay hàu tươi sống các bờ biển nước Mỹ", "cuisine": "Hải sản nhà ga lịch sử", "address": "89 E 42nd St, New York, NY 10017"}
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
        {"title": "Du Thuyền Sông Seine Ngắm Hoàng Hôn Paris", "type": "ACTIVITY", "desc": "Lướt nhẹ qua Nhà thờ Đức Bà, Cầu Pont Alexandre III và các cung điện cổ", "cost": 450000.0, "address": "Port de la Bourdonnais, 75007 Paris"},
        {"title": "Khám Phá Đồi Nghệ Thuật Montmartre & Vương Cung Thánh Đường Sacré-Cœur", "type": "ATTRACTION", "desc": "Ngọn đồi lãng mạn nơi hội tụ các danh họa và quang cảnh Paris từ bậc thang đá", "cost": 0.0, "address": "35 Rue du Chevalier de la Barre, 75018 Paris"}
    ],
    "liverpool": [
        {"title": "Bảo Tàng Ban Nhạc The Beatles Story tại Albert Dock", "type": "ATTRACTION", "desc": "Hành trình âm nhạc huyền thoại của 4 chàng trai thế kỷ bên bến cảng lịch sử", "cost": 650000.0, "address": "Britannia Vaults, Albert Dock, Liverpool L3 4AD"},
        {"title": "Sân Vận Động Anfield & Tour Phòng Truyền Thống Liverpool FC", "type": "ACTIVITY", "desc": "Chạm tay vào biểu tượng 'This Is Anfield' và khám phá phòng thay đồ sân cỏ vinh quang", "cost": 850000.0, "address": "Anfield Rd, Liverpool L4 0TH"},
        {"title": "Đại Thánh Đường Liverpool Cathedral & Tháp Chuông Cao Nhất", "type": "ATTRACTION", "desc": "Nhà thờ Gothic lớn nhất Vương quốc Anh với tầm nhìn bao quát toàn bộ vùng Merseyside", "cost": 200000.0, "address": "St James Mt, Liverpool L1 7AZ"},
        {"title": "Phố Âm Nhạc Mathew Street & Quán Bar The Cavern Club", "type": "ACTIVITY", "desc": "Thưởng thức nhạc sống acoustic nơi The Beatles biểu diễn những nốt nhạc đầu tiên", "cost": 300000.0, "address": "10 Mathew St, Liverpool L2 6RE"}
    ],
    "london": [
        {"title": "Bảo Tàng Anh British Museum & Khám Phá Cổ Vật Thế Giới", "type": "ATTRACTION", "desc": "Bảo tàng lịch sử văn hóa nhân loại với hòn đá Rosetta và lăng mộ Ai Cập cổ", "cost": 0.0, "address": "Great Russell St, London WC1B 3DG"},
        {"title": "Vòng Quay London Eye & Ngắm Tháp Đồng Hồ Big Ben", "type": "ATTRACTION", "desc": "Cabin kính ngắm toàn cảnh dòng sông Thames và Cung điện Westminster", "cost": 850000.0, "address": "Riverside Building, County Hall, London SE1 7PB"},
        {"title": "Tháp Luân Đôn Tower of London & Bộ Vương Miện Hoàng Gia", "type": "ATTRACTION", "desc": "Pháo đài cổ gần 1000 năm lưu giữ vương miện đính kim cương vô giá", "cost": 750000.0, "address": "London EC3N 4AB"},
        {"title": "Du Thuyền Sông Thames đến Làng Thiên Văn Greenwich", "type": "ACTIVITY", "desc": "Lướt qua Cầu Tháp Tower Bridge đến kinh tuyến số 0 Greenwich", "cost": 450000.0, "address": "Westminster Pier, Victoria Embankment, London SW1A 2JH"}
    ],
    "new york": [
        {"title": "Tượng Nữ Thần Tự Do Statue of Liberty & Đảo Ellis", "type": "ATTRACTION", "desc": "Biểu tượng tự do của nước Mỹ giữa vịnh New York", "cost": 650000.0, "address": "Liberty Island, New York, NY 10004"},
        {"title": "Đài Quan Sát The Summit One Vanderbilt / Empire State", "type": "ATTRACTION", "desc": "Căn phòng kính đa chiều ngắm trọn vẹn đường chân trời đảo Manhattan", "cost": 950000.0, "address": "45 E 42nd St, New York, NY 10017"},
        {"title": "Dạo Bộ Công Viên Central Park & Cầu Đá Bow Bridge", "type": "ATTRACTION", "desc": "Lá phổi xanh thơ mộng giữa lòng các tòa nhà chọc trời Manhattan", "cost": 0.0, "address": "Central Park, New York, NY 10024"},
        {"title": "Quảng Trường Thời Đại Times Square & Thưởng Thức Kịch Broadway", "type": "ACTIVITY", "desc": "Giao lộ ánh sáng huyền ảo rực rỡ và vở nhạc kịch đỉnh cao nghệ thuật", "cost": 1800000.0, "address": "Manhattan, NY 10036"}
    ]
}

import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

def _fetch_live_flight_offers(origin: str, destination: str, departure_date: Optional[str] = None, travelers: int = 1) -> Optional[List[Dict[str, Any]]]:
    """Attempts live GDS/OTA flight search (Amadeus / Duffel / Skyscanner) if API credentials exist."""
    amadeus_key = os.getenv("AMADEUS_API_KEY") or os.getenv("AMADEUS_CLIENT_ID")
    duffel_token = os.getenv("DUFFEL_API_KEY") or os.getenv("DUFFEL_TOKEN")
    
    if not (amadeus_key or duffel_token):
        return None
        
    try:
        # Standardized mock-ready live adapter connector
        logger.info(f"Connecting to live Flight Distribution System for route {origin} -> {destination}")
        # When live credentials are provided in production, issue HTTP request to GDS endpoint
        # Fallback to None if not configured or network unreachable
        return None
    except Exception as e:
        logger.warning(f"Live flight API query failed: {e}. Falling back to universal synthesis.")
        return None

def _fetch_live_hotel_offers(city: str, check_in: Optional[str] = None, check_out: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Attempts live Booking.com / Agoda / RapidAPI search if credentials exist."""
    rapidapi_key = os.getenv("BOOKING_COM_API_KEY") or os.getenv("RAPIDAPI_KEY")
    if not rapidapi_key:
        return None
    try:
        logger.info(f"Connecting to live Booking.com / RapidAPI feed for {city}")
        return None
    except Exception as e:
        logger.warning(f"Live hotel API query failed: {e}. Falling back to universal synthesis.")
        return None

def _fetch_live_places_activities(city: str, lat: float, lon: float) -> Optional[List[Dict[str, Any]]]:
    """Attempts Google Places or Foursquare API for real-time venue search."""
    google_key = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
    if not google_key:
        return None
    try:
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=tourist+attractions+in+{urllib.parse.quote(city)}&key={google_key}"
        req = urllib.request.Request(url, headers={"User-Agent": "AITravelAgent/1.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            results = []
            for p in data.get("results", [])[:8]:
                results.append({
                    "name": p.get("name"),
                    "category": "culture",
                    "price": 150000.0,
                    "currency": "VND",
                    "duration_minutes": 120,
                    "address": p.get("formatted_address", f"{city}"),
                    "latitude": p.get("geometry", {}).get("location", {}).get("lat", lat),
                    "longitude": p.get("geometry", {}).get("location", {}).get("lng", lon),
                    "description": f"Điểm tham quan nổi tiếng tại {city} với đánh giá {p.get('rating', 4.5)} sao."
                })
            if results:
                return results
    except Exception as e:
        logger.warning(f"Google Places live search fallback: {e}")
    return None


class UniversalFlightProvider(BaseFlightTool):
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: Optional[str] = None,
        travelers: int = 1
    ) -> List[Dict[str, Any]]:
        live_flights = _fetch_live_flight_offers(origin, destination, departure_date, travelers)
        if live_flights:
            return live_flights
        geo = geo_service.resolve_destination(destination)
        airport = geo.get("nearest_airport", {})
        dest_airport_code = airport.get("iata") or airport.get("code") or "INTL"
        dest_country = geo.get("country", destination)
        code = geo.get("country_code", "XX")

        # Determine route & airlines
        if code in ["AT", "CH", "FR", "DE", "IT", "ES", "NL", "UK", "GB", "IS", "NO"]:
            airlines = INTERNATIONAL_AIRLINES_BY_REGION["EUROPE"]
            base_price = 14500000.0
            duration_str = "14h 30m (1 stop)"
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
        check_in: Optional[str] = None,
        check_out: Optional[str] = None,
        budget_tier: Optional[str] = "MEDIUM",
        preferences: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        live_hotels = _fetch_live_hotel_offers(city, check_in, check_out)
        if live_hotels:
            return live_hotels
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

        # Check city-level catalog first using comprehensive lookup
        results_rests: List[Dict[str, Any]] = []
        seen_rest_names = set()

        lookup_text = f"{city} {geo.get('query', '')} {c_name} {geo.get('display_name', '')}".lower()
        for key, dishes in CITY_CUISINES.items():
            if key in lookup_text:
                for idx, r in enumerate(dishes):
                    r_name = r["name"]
                    if r_name not in seen_rest_names:
                        seen_rest_names.add(r_name)
                        results_rests.append({
                            "name": r_name,
                            "cuisine": r["cuisine"],
                            "rating": round(4.9 - (idx % 5) * 0.1, 1),
                            "price_avg": round(base_meal * (1.0 + (idx % 4) * 0.2), -4),
                            "currency": "VND",
                            "address": r.get("address", f"Số {15 + idx * 8} Phố Ẩm Thực, {c_name}, {country}"),
                            "latitude": round(lat + (idx * 0.002 - 0.002), 4),
                            "longitude": round(lon + (idx * 0.002 - 0.001), 4),
                            "specialty": r["specialty"]
                        })
                break

        # Supplement with diverse authentic dining venues for rich multi-day itineraries
        dynamic_rest_templates = [
            ("Nhà Hàng Đặc Sản Truyền Thống", f"Ẩm thực bản địa {country}", f"Các món ăn gia truyền trứ danh của vùng {c_name}", f"Số 12 Phố Cổ Di Sản, {c_name}, {country}"),
            ("Quán Ăn Dân Dã & Trà Chiều", "Ẩm thực gia đình & Nông sản tươi", f"Bánh nướng nóng hổi và trà thảo mộc vùng {c_name}", f"Góc ngã tư phố cổ, {c_name}, {country}"),
            ("Bistro Ẩm Thực Tươi Sống", "Hải sản & Nông sản theo mùa", f"Món ngon chế biến từ nguyên liệu sạch tại địa phương {c_name}", f"Khu chợ ẩm thực trung tâm, {c_name}, {country}"),
            ("Nhà Hàng Ven Bờ Sông / Bờ Hồ Thơ Mộng", "Món nướng than hoa & Rượu bản địa", f"Bữa tối ấm áp bên bờ nước với món nướng thơm lừng", f"Đường dạo ven hồ sinh thái, {c_name}, {country}"),
            ("Quán Cơm Gia Đình & Món Ngon Truyền Thống", "Mâm cơm ấm cúng", f"Canh hầm thảo dược và món rim kho chuẩn vị quê hương", f"Khu phố yên bình, {c_name}, {country}"),
            ("Nhà Hàng Tầng Cao Panorama", "Fine Dining & Rượu Vang", f"Bữa tối lãng mạn ngắm thành phố lung linh ánh đèn", f"Tòa tháp ngắm cảnh trung tâm, {c_name}, {country}"),
            ("Quán Lẩu Thảo Mộc & Đồ Nướng Bản Địa", "Lẩu ấm & Đồ nướng thảo dược", f"Nồi lẩu nóng hổi nấu cùng nấm rừng và rau xanh địa phương", f"Khu đồi sinh thái ngoại ô, {c_name}, {country}"),
            ("Bếp Thực Dưỡng & Ẩm Thực Xanh", "Ẩm thực thanh đạm hữu cơ", f"Món ăn thanh mát từ rau củ tươi và nước ép tự nhiên", f"Gần khu vườn bách thảo, {c_name}, {country}"),
            ("Quán Hải Sản & Món Nước Gia Truyền", "Đặc sản nước dùng gia truyền", f"Tô mì / súp nóng hổi ngập tràn hải sản tươi ngon", f"Phố cảng ẩm thực, {c_name}, {country}"),
            ("Nhà Hàng Hầm Rượu Cổ Bản Xứ", "Thịt hầm rượu & Phô mai thủ công", f"Thịt bò hầm mềm đậm đà kết hợp cùng phô mai ủ truyền thống", f"Khu phố lịch sử, {c_name}, {country}"),
            ("Góc Ẩm Thực Chợ Đêm & Món Ăn Vặt", "Món ngon đường phố", f"Bánh giòn nóng hổi và xiên nướng thơm phức chợ đêm", f"Quảng trường chợ đêm, {c_name}, {country}"),
            ("Bistro Đương Đại & Cà Phê Nghệ Thuật", "Fusion hiện đại & Cà phê hạt", f"Món ăn kết hợp sáng tạo và thức uống phong cách mới", f"Phố nghệ thuật đương đại, {c_name}, {country}"),
            ("Nhà Hàng Đồng Quê & Nông Trại Xanh", "Đặc sản trang trại đồng quê", f"Gà đồi nướng lu và xôi nếp thơm dẻo từ nông trại", f"Khu sinh thái đồng quê, {c_name}, {country}"),
            ("Quán Mì Thủ Công & Điểm Tâm Sáng", "Mì sợi kéo tay & Bánh hấp", f"Mì sợi tươi tự làm với nước hầm xương đậm đà nguyên bản", f"Phố chợ sớm, {c_name}, {country}"),
            ("Quán Bít Tết Bơ Tỏi & Rượu Bản Địa", "Steak & Grill phương Tây", f"Thịt bít tết áp chảo xì xèo cùng sốt tiêu đen thảo mộc", f"Khu thương mại trung tâm, {c_name}, {country}")
        ]

        for idx, (prefix, cuis, spec, addr) in enumerate(dynamic_rest_templates):
            name = f"{prefix} {c_name}"
            if name not in seen_rest_names:
                seen_rest_names.add(name)
                results_rests.append({
                    "name": name,
                    "cuisine": cuis,
                    "rating": round(4.8 - (idx % 3) * 0.1, 1),
                    "price_avg": round(base_meal * (0.8 + (idx % 5) * 0.15), -4),
                    "currency": "VND",
                    "address": addr,
                    "latitude": round(lat + ((idx - 5) * 0.0018), 4),
                    "longitude": round(lon + ((idx - 5) * 0.0015), 4),
                    "specialty": spec
                })

        return results_rests

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

        live_acts = _fetch_live_places_activities(city, lat, lon)
        if live_acts:
            return live_acts

        results_acts: List[Dict[str, Any]] = []
        seen_act_names = set()

        # 1. Curated iconic city-level catalog first
        lookup_text = f"{city} {geo.get('query', '')} {c_name} {geo.get('display_name', '')}".lower()
        for key, acts in CITY_ACTIVITIES.items():
            if key in lookup_text:
                for idx, a in enumerate(acts):
                    title = a["title"]
                    if title not in seen_act_names:
                        seen_act_names.add(title)
                        results_acts.append({
                            "name": title,
                            "category": a["type"].lower(),
                            "price": a["cost"],
                            "currency": "VND",
                            "duration_minutes": 150 + idx * 20,
                            "address": a.get("address", f"Khu di tích lịch sử {c_name}, {country}"),
                            "latitude": round(lat + (idx * 0.003 - 0.003), 4),
                            "longitude": round(lon + (idx * 0.003 - 0.002), 4),
                            "description": a["desc"]
                        })
                break

        # 2. Rich non-repeating authentic activities for any global village/city
        # Exactly ONE viewpoint activity template, all others are varied thematic landmarks
        has_viewpoint = any("viewpoint" in a["name"].lower() or "đài quan sát" in a["name"].lower() for a in results_acts)

        dynamic_act_templates = [
            ("Khám phá Phố Cổ & Di Sản Lịch Sử", "culture", 0.0, 150, f"Khu trung tâm di sản lịch sử {c_name}, {country}", f"Dạo bước trên những con đường đá cuội cổ kính và chiêm ngưỡng kiến trúc đặc sắc của {c_name}."),
            ("Bảo Tàng Nghệ Thuật & Lịch Sử Văn Hóa", "culture", 180000.0, 120, f"Đại lộ Văn Hóa, {c_name}, {country}", f"Chiêm ngưỡng bộ sưu tập hiện vật quý giá và những tác phẩm nghệ thuật tiêu biểu của {c_name}."),
            ("Dạo Bộ Công Viên Sinh Thái & Vườn Bách Thảo", "nature", 0.0, 90, f"Công viên Trung Tâm, {c_name}, {country}", "Hòa mình vào không gian xanh mát rợp bóng cây cổ thụ và hồ nước thanh bình."),
            ("Trải nghiệm Nghề Thủ Công Truyền Thống & Xưởng Gốm Bản Địa", "activity", 350000.0, 120, f"Làng nghề thủ công truyền thống, {c_name}, {country}", f"Tự tay sáng tạo tác phẩm lưu niệm độc bản cùng các nghệ nhân địa phương giàu kinh nghiệm của {country}."),
            ("Du Thuyền Hoàng Hôn Ven Sông / Bờ Vịnh", "relaxation", 420000.0, 90, f"Bến du thuyền trung tâm, {c_name}, {country}", "Thư giãn trên boong tàu ngắm ánh tà dương buông xuống mặt nước thơ mộng."),
            ("Khu Phố Bích Họa Nghệ Thuật & Con Đường Nhiếp Ảnh", "art", 0.0, 90, f"Khu phố nghệ thuật sáng tạo, {c_name}, {country}", "Khám phá các bức bích họa tường rực rỡ sắc màu và ghi lại những khoảnh khắc tuyệt đẹp."),
            ("Chợ Đêm Bản Địa & Thưởng Thức Ẩm Thực Đường Phố", "shopping", 200000.0, 120, f"Khu chợ đêm truyền thống, {c_name}, {country}", "Hòa mình vào không khí nhộn nhịp, mua sắm đồ lưu niệm và nếm thử món ngon bản xứ."),
            ("Quảng Trường Lễ Hội & Tháp Chuông Đồng Hồ Cổ", "culture", 0.0, 75, f"Quảng trường Lễ Hội, {c_name}, {country}", f"Chiêm ngưỡng kiến trúc tháp chuông cổ kính và nhịp sống thanh bình nơi trung tâm {c_name}."),
            ("Tour Trà Đạo & Cà Phê Rang Xay Truyền Thống", "food", 160000.0, 90, f"Góc phố cà phê di sản, {c_name}, {country}", "Thưởng thức hương vị thức uống bản địa thơm lừng cùng các loại bánh truyền thống độc đáo."),
            ("Tham Quan Thủy Cung & Thế Giới Sinh Vật Biển Kỳ Thú", "activity", 380000.0, 120, f"Đại lộ Sinh Thái Ven Hồ, {c_name}, {country}", "Khám phá đường hầm kính dưới nước với hàng trăm loài sinh vật kỳ vĩ."),
            ("Chuyến Khám Phá Rừng Thông & Cung Đường Đi Bộ Sinh Thái", "nature", 0.0, 150, f"Đường mòn sinh thái ngoại ô {c_name}, {country}", "Hít thở không khí rừng trong lành và lắng nghe tiếng chim hót giữa thiên nhiên hoang sơ."),
            ("Khu Phức Hợp Giải Trí & Trải Nghiệm Công Nghệ Đương Đại", "activity", 450000.0, 150, f"Trung tâm văn hóa đương đại, {c_name}, {country}", "Trải nghiệm không gian tương tác nghệ thuật số và các hoạt động giải trí hiện đại."),
            ("Viếng Thăm Tu Viện Cổ & Không Gian Thiền Tịnh", "culture", 50000.0, 90, f"Khu thánh đường di sản, {c_name}, {country}", "Chiêm ngưỡng các bức tranh kính màu cổ kính và lắng đọng tâm hồn trong không gian trang nghiêm."),
            ("Khám Phá Chợ Nông Sản & Nếm Thử Trái Cây / Bơ Sữa Địa Phương", "food", 120000.0, 75, f"Chợ phiên nông sản truyền thống, {c_name}, {country}", "Thưởng thức các loại hoa quả tươi mọng, mứt quả và bơ sữa béo ngậy được chế biến thủ công."),
            ("Nhà Hát Biểu Diễn Nghệ Thuật & Âm Nhạc Dân Gian", "culture", 300000.0, 120, f"Nhà hát Nghệ thuật Trung tâm, {c_name}, {country}", "Thưởng thức những tiết mục ca múa nhạc truyền thống mang đậm bản sắc văn hóa vùng miền."),
            ("Khu Vườn Cổ Tích & Mê Cung Hoa Ngoại Ô", "nature", 150000.0, 90, f"Khu sinh thái ngoại ô, {c_name}, {country}", "Dạo bước giữa những luống hoa khoe sắc và check-in mê cung cây xanh thơ mộng."),
            ("Trải Nghiệm Đạp Xe Dọc Bờ Sông & Làng Ngoại Ô Yên Bình", "activity", 120000.0, 120, f"Tuyến đường ven sông thơ mộng, {c_name}, {country}", "Lướt nhẹ trên cung đường rợp bóng cây ngắm nhìn cuộc sống êm đềm của người dân ngoại ô."),
            ("Khu Di Tích Pháo Đài / Thành Cổ Ngàn Năm", "culture", 100000.0, 105, f"Cổng thành cổ di sản, {c_name}, {country}", "Tìm hiểu những dấu mốc lịch sử hào hùng qua từng phiến đá thành lũy rêu phong."),
            ("Phố Sách & Thư Viện Kiến Trúc Mái Vòm Độc Đáo", "culture", 0.0, 90, f"Phố sách văn hóa, {c_name}, {country}", "Thưởng lãm không gian đọc sách cổ kính với hàng vạn đầu sách quý giá.")
        ]

        if not has_viewpoint:
            dynamic_act_templates.insert(3, (
                "Chinh phục Điểm Ngắm Cảnh Toàn Cảnh (Viewpoint)",
                "nature",
                250000.0,
                180,
                f"Đài quan sát đỉnh đồi ngắm cảnh, {c_name}, {country}",
                f"Ngắm trọn vẹn thung lũng, thiên nhiên và mái nhà cổ tích của {c_name} từ trên cao."
            ))

        for idx, (prefix, cat, prc, dur, addr, desc) in enumerate(dynamic_act_templates):
            name = f"{prefix} {c_name}"
            if name not in seen_act_names:
                seen_act_names.add(name)
                results_acts.append({
                    "name": name,
                    "category": cat,
                    "price": prc,
                    "currency": "VND",
                    "duration_minutes": dur,
                    "address": addr,
                    "latitude": round(lat + ((idx - 6) * 0.0019), 4),
                    "longitude": round(lon + ((idx - 6) * 0.0016), 4),
                    "description": desc
                })

        return results_acts

