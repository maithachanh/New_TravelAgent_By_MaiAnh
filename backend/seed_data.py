from app.core.database import SessionLocal, engine, Base
from app.models.models import User, Destination
from app.core.security import get_password_hash
from app.services.rag_service import rag_service

Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    
    # 1. Seed Demo User
    demo_user = db.query(User).filter(User.email == "demo@travelagent.ai").first()
    if not demo_user:
        user = User(
            email="demo@travelagent.ai",
            hashed_password=get_password_hash("password123"),
            full_name="Nguyễn Văn Du Lịch",
            language="vi",
            currency="VND",
            travel_styles=["Adventure", "Food", "Relaxation", "Cultural", "Shopping"]
        )
        db.add(user)
        db.commit()
        print("[Seed] Created Demo User: demo@travelagent.ai / password123")

    # 2. Seed Multi-Collection Knowledge for Hàn Quốc, Tokyo, Đà Nẵng...
    # a) destination_knowledge
    rag_service.add_document(
        collection_name="destination_knowledge",
        doc_id="dest_korea",
        content="Hàn Quốc là thiên đường du lịch Đông Á nổi tiếng với văn hóa K-Pop, thời trang rực rỡ tại Myeongdong & Hongdae, cùng ẩm thực phong phú. Mùa đông tháng 12 có tuyết rơi tại Đảo Nami và các khu trượt tuyết.",
        metadata={"city": "Hàn Quốc", "country": "Hàn Quốc", "category": "guide"}
    )
    rag_service.add_document(
        collection_name="destination_knowledge",
        doc_id="dest_tokyo",
        content="Tokyo là thủ đô nước Nhật, kết hợp hoàn hảo giữa nét hiện đại chọc trời và truyền thống cổ kính. Tháng 12 khí hậu xe lạnh, trời trong xanh, rực rỡ đèn Giáng sinh tại Shibuya, Ginza và Roppongi Hills.",
        metadata={"city": "Tokyo", "country": "Nhật Bản", "category": "guide"}
    )

    # b) travel_rules
    rag_service.add_document(
        collection_name="travel_rules",
        doc_id="rule_korea_visa",
        content="Khách du lịch Việt Nam đến Hàn Quốc cần xin eVisa K-ETA trực tuyến hoặc nộp hồ sơ xin Visa C-3-9. Tỷ giá quy đổi tham khảo: 1 KRW ~ 18.5 VND. Tiền mặt Won (KRW) và Thẻ T-Money rất cần thiết khi đi lại bằng Metro.",
        metadata={"city": "Hàn Quốc", "category": "visa_regulation"}
    )
    rag_service.add_document(
        collection_name="travel_rules",
        doc_id="rule_japan_visa",
        content="Khách du lịch Việt Nam đến Nhật Bản cần xin eVisa du lịch hoặc Visa dán. Hộ chiếu còn hạn trên 6 tháng. Tỷ giá: 1 JPY ~ 170 VND.",
        metadata={"city": "Tokyo", "category": "visa_regulation"}
    )

    # c) attraction_knowledge
    rag_service.add_document(
        collection_name="attraction_knowledge",
        doc_id="attr_gyeongbokgung",
        content="Cung điện Gyeongbokgung (Cảnh Phúc Cung) là cung điện hoàng gia lớn nhất triều đại Joseon. Khách mặc áo Hanbok truyền thống được miễn phí vé vào cổng.",
        metadata={"city": "Hàn Quốc", "category": "culture", "name": "Cung điện Gyeongbokgung"}
    )
    rag_service.add_document(
        collection_name="attraction_knowledge",
        doc_id="attr_nami",
        content="Đảo Nami là bối cảnh bộ phim nổi tiếng Bản Tình Ca Mùa Đông với hai hàng cây lãng mạn phủ tuyết tuyệt đẹp vào tháng 12.",
        metadata={"city": "Hàn Quốc", "category": "nature", "name": "Đảo Nami"}
    )

    # d) hotel_knowledge
    rag_service.add_document(
        collection_name="hotel_knowledge",
        doc_id="hotel_lotte_seoul",
        content="Lotte Hotel Seoul Myeongdong là khách sạn 5 sao cao cấp kết nối trực tiếp với trung tâm thương mại Lotte và ga tàu điện ngầm Euljiro 1-ga.",
        metadata={"city": "Hàn Quốc", "category": "hotel", "district": "Myeongdong"}
    )

    # e) restaurant_knowledge
    rag_service.add_document(
        collection_name="restaurant_knowledge",
        doc_id="rest_samgyetang",
        content="Nhà hàng Tosokchon Samgyetang nổi tiếng nhất Seoul với món Gà hầm sâm tươi núi, nhân sâm 6 năm tuổi cùng nước dùng béo ngậy ngọt thanh.",
        metadata={"city": "Hàn Quốc", "category": "food", "name": "Tosokchon Samgyetang"}
    )
    rag_service.add_document(
        collection_name="restaurant_knowledge",
        doc_id="rest_myeongdong_kyoja",
        content="Myeongdong Kyoja đạt danh hiệu Michelin Bib Gourmand với món bánh mì sủi cảo hấp Mandu nức tiếng và mì Kalguksu truyền thống.",
        metadata={"city": "Hàn Quốc", "category": "food", "name": "Myeongdong Kyoja"}
    )

    # f) transportation_knowledge
    rag_service.add_document(
        collection_name="transportation_knowledge",
        doc_id="trans_tmoney",
        content="Thẻ T-Money là thẻ thanh toán giao thông đa năng tại Hàn Quốc, dùng để đi tàu điện ngầm Seoul Metro, xe buýt và thanh toán tại các cửa hàng tiện lợi GS25, CU, Seven-Eleven.",
        metadata={"city": "Hàn Quốc", "category": "transportation"}
    )

    print("[Seed] Multi-Collection Knowledge seeded successfully into Advanced RAG System!")
    db.close()

if __name__ == "__main__":
    seed()
