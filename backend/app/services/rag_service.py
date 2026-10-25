import os
import re
import json
from typing import List, Dict, Any, Optional

COLLECTION_NAMES = [
    "destination_knowledge",
    "travel_rules",
    "attraction_knowledge",
    "hotel_knowledge",
    "restaurant_knowledge",
    "transportation_knowledge"
]

DEFAULT_KNOWLEDGE_BASE = [
    # Travel Rules & Visa Knowledge
    {
        "collection": "travel_rules",
        "doc_id": "rule_japan_visa",
        "content": "Quy định nhập cảnh Nhật Bản: Công dân Việt Nam cần xin thị thực (Visa) trước khi khởi hành hoặc e-Visa du lịch. Hộ chiếu còn hạn trên 6 tháng. Thẻ Suica/Pasmo rất thuận tiện cho tàu điện ngầm và thanh toán tiện lợi tại Tokyo và Osaka. Văn hóa: Nhật Bản không có văn hóa tiền tip (tipping).",
        "metadata": {"country": "Nhật Bản", "city": "Tokyo", "category": "visa_customs"}
    },
    {
        "collection": "travel_rules",
        "doc_id": "rule_uk_visa",
        "content": "Quy định du lịch Vương quốc Anh (UK): Du khách Việt Nam cần xin UK Standard Visitor Visa ít nhất 4-6 tuần trước chuyến đi. Hệ thống giao thông công cộng London sử dụng thẻ Oyster hoặc thẻ thanh toán Contactless. Di chuyển từ London đến Liverpool thuận tiện nhất bằng tàu hỏa Avanti West Coast (khoảng 2h15p). Ổ cắm điện loại G 3 chấu vuông.",
        "metadata": {"country": "Vương quốc Anh", "city": "London", "category": "visa_transit"}
    },
    {
        "collection": "travel_rules",
        "doc_id": "rule_france_schengen",
        "content": "Quy định khối Schengen (Pháp, Ý, Đức...): Cần visa Schengen loại C cho phép lưu trú tối đa 90 ngày trong chu kỳ 180 ngày. Cần mua bảo hiểm du lịch quốc tế tối thiểu 30.000 EUR. Tại Paris, sử dụng thẻ Navigo Easy cho tàu điện metro và RER. Tiền tệ sử dụng là Euro (EUR).",
        "metadata": {"country": "Pháp", "city": "Paris", "category": "visa_schengen"}
    },
    {
        "collection": "travel_rules",
        "doc_id": "rule_usa_transit",
        "content": "Quy định du lịch Hoa Kỳ (Mỹ): Du khách cần phỏng vấn xin thị thực B1/B2 hoặc có ESTA (với các nước miễn thị thực). Chuyến bay từ Việt Nam sang New York/Bờ Đông mất tối thiểu 18-24 giờ và quá cảnh ít nhất 1 chặng. Văn hóa tiền boa (tip) tại nhà hàng và dịch vụ tại Mỹ từ 18% đến 22%. Ổ cắm loại A/B điện áp 110V.",
        "metadata": {"country": "Hoa Kỳ", "city": "New York", "category": "visa_customs"}
    },
    {
        "collection": "travel_rules",
        "doc_id": "rule_korea_keta",
        "content": "Quy định du lịch Hàn Quốc: Cần nộp hồ sơ xin visa C-3-9 hoặc K-ETA đối với các quốc tịch miễn thị thực. Thẻ giao thông T-Money dùng cho metro Seoul và xe bus trên toàn quốc. Hoàn thuế (Tax Refund) có thể làm trực tiếp tại sân bay Incheon hoặc các điểm mua sắm lớn như Myeongdong.",
        "metadata": {"country": "Hàn Quốc", "city": "Seoul", "category": "visa_transit"}
    },
    {
        "collection": "travel_rules",
        "doc_id": "rule_thailand_entry",
        "content": "Quy định du lịch Thái Lan: Công dân Việt Nam được miễn visa du lịch 30-60 ngày với mục đích du lịch. Cần có vé máy bay khứ hồi và xác nhận đặt phòng khách sạn. Hệ thống tàu trên cao BTS và tàu ngầm MRT rất tiện lợi tại Bangkok. Trang phục kín đáo lịch sự khi viếng thăm chùa chiền hoàng cung.",
        "metadata": {"country": "Thái Lan", "city": "Bangkok", "category": "visa_customs"}
    },
    {
        "collection": "travel_rules",
        "doc_id": "rule_flight_baggage",
        "content": "Quy định hàng không quốc tế: Hành lý xách tay tiêu chuẩn thông thường là 7kg kích thước 56x36x23cm. Chất lỏng xách tay không quá 100ml mỗi chai và đựng trong túi trong suốt tối đa 1 lít. Hành khách chuyến bay quốc tế cần có mặt tại sân bay trước giờ khởi hành tối thiểu 3 tiếng.",
        "metadata": {"category": "flight_rules"}
    },
    # Destination & Attraction Knowledge
    {
        "collection": "destination_knowledge",
        "doc_id": "dest_tokyo_highlights",
        "content": "Tokyo, Nhật Bản: Thành phố kết hợp giữa hiện đại và truyền thống. Các điểm đến nổi tiếng gồm Đền Senso-ji ở Asakusa, Ngã tư Shibuya náo nhiệt, Tháp truyền hình Tokyo Skytree, Phố điện tử Akihabara và Chợ cá Tsukiji/Toyosu phục vụ hải sản tươi ngon bậc nhất thế giới.",
        "metadata": {"country": "Nhật Bản", "city": "Tokyo", "category": "dest_overview"}
    },
    {
        "collection": "destination_knowledge",
        "doc_id": "dest_kyoto_osaka",
        "content": "Cố đô Kyoto và Osaka: Kyoto lưu giữ văn hóa truyền thống với Rừng trúc Arashiyama, Đền Fushimi Inari ngàn cổng Torii, Chùa Vàng Kinkaku-ji. Osaka là thủ phủ ẩm thực đường phố nổi tiếng với khu Dotonbori, Takoyaki, Okonomiyaki và Lâu đài Osaka uy nghi.",
        "metadata": {"country": "Nhật Bản", "city": "Kyoto", "category": "dest_overview"}
    },
    {
        "collection": "destination_knowledge",
        "doc_id": "dest_paris_highlights",
        "content": "Paris, Pháp: Kinh đô ánh sáng với Tháp Eiffel biểu tượng, Bảo tàng Louvre chứa bức tranh Mona Lisa, Khải Hoàn Môn Arc de Triomphe, Đại lộ Champs-Élysées và Đồi Montmartre với Vương cung thánh đường Sacré-Cœur.",
        "metadata": {"country": "Pháp", "city": "Paris", "category": "dest_overview"}
    },
    {
        "collection": "destination_knowledge",
        "doc_id": "dest_london_liverpool",
        "content": "Vương quốc Anh: London nổi tiếng với Tháp đồng hồ Big Ben, Tu viện Westminster, Cầu Tower Bridge và Bảo tàng Anh. Thành phố cảng Liverpool là quê hương của ban nhạc huyền thoại The Beatles, bến cảng Royal Albert Dock và Sân vận động Anfield của câu lạc bộ bóng đá Liverpool.",
        "metadata": {"country": "Vương quốc Anh", "city": "Liverpool", "category": "dest_overview"}
    },
    {
        "collection": "destination_knowledge",
        "doc_id": "dest_vietnam_tours",
        "content": "Việt Nam: Hà Nội với Phố cổ 36 phố phường và Hồ Gươm lịch sử; Vịnh Hạ Long kỳ quan thiên nhiên thế giới; Đà Nẵng - Hội An với phố cổ lung linh đèn lồng và Cầu Vàng Bà Nà Hills; Thành phố Hồ Chí Minh sầm uất với Nhà thờ Đức Bà, Chợ Bến Thành và ẩm thực đường phố phong phú.",
        "metadata": {"country": "Việt Nam", "city": "Hà Nội", "category": "dest_overview"}
    }
]

class AdvancedRAGService:
    def __init__(self):
        self.storage_dir = os.getenv("CHROMA_DB_DIR", "./chroma_storage")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.store_file = os.path.join(self.storage_dir, "rag_store.json")
        self.collections: Dict[str, List[Dict[str, Any]]] = {c: [] for c in COLLECTION_NAMES}
        self._load_or_initialize()

    def _load_or_initialize(self):
        """Loads persistent knowledge base from disk or initializes default multi-country knowledge."""
        if os.path.exists(self.store_file):
            try:
                with open(self.store_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for col in COLLECTION_NAMES:
                        self.collections[col] = data.get(col, [])
                total_docs = sum(len(docs) for docs in self.collections.values())
                if total_docs > 0:
                    return
            except Exception as e:
                print(f"[AdvancedRAGService] Error loading {self.store_file}: {e}")

        # Seed built-in comprehensive default knowledge
        for item in DEFAULT_KNOWLEDGE_BASE:
            self.add_document(
                collection_name=item["collection"],
                doc_id=item["doc_id"],
                content=item["content"],
                metadata=item["metadata"]
            )
        self._persist()

    def _persist(self):
        """Saves current collections to JSON store."""
        try:
            with open(self.store_file, "w", encoding="utf-8") as f:
                json.dump(self.collections, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[AdvancedRAGService] Warning: Failed to persist RAG storage: {e}")

    def clean_text(self, text: str) -> str:
        """Text Cleaning Pipeline: strip HTML, normalize whitespace, clean noise"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_document(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Simple recursive chunking engine"""
        cleaned = self.clean_text(text)
        if len(cleaned) <= chunk_size:
            return [cleaned]
        
        chunks = []
        start = 0
        while start < len(cleaned):
            end = start + chunk_size
            chunk = cleaned[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    def add_document(self, collection_name: str, doc_id: str, content: str, metadata: Dict[str, Any]):
        """
        Add document to target multi-collection with metadata filtering tags
        """
        if collection_name not in self.collections:
            collection_name = "destination_knowledge"

        cleaned_content = self.clean_text(content)
        chunks = self.chunk_document(cleaned_content)

        for idx, chunk in enumerate(chunks):
            chunk_doc = {
                "id": f"{doc_id}_chunk_{idx}",
                "doc_id": doc_id,
                "content": chunk,
                "metadata": metadata
            }
            # Avoid duplicate chunks
            existing_ids = {d["id"] for d in self.collections[collection_name]}
            if chunk_doc["id"] not in existing_ids:
                self.collections[collection_name].append(chunk_doc)
        
        self._persist()

    def query(
        self,
        query_text: str,
        collection_name: Optional[str] = None,
        city_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Multi-collection query with metadata filtering (by city, category, tag)
        """
        target_collections = [collection_name] if collection_name and collection_name in self.collections else COLLECTION_NAMES

        query_words = set(query_text.lower().split())
        results = []

        for col in target_collections:
            for item in self.collections[col]:
                meta = item.get("metadata", {})
                
                # Metadata Filtering Check
                if city_filter and meta.get("city") and city_filter.lower() not in meta.get("city", "").lower():
                    continue
                if category_filter and meta.get("category") and category_filter.lower() not in meta.get("category", "").lower():
                    continue

                # Cosine/TF-IDF approximation via keyword overlap & metadata match
                text_lower = item["content"].lower()
                overlap_score = sum(1 for w in query_words if len(w) > 2 and w in text_lower)
                
                # Boost score if destination/city matches
                if city_filter and city_filter.lower() in text_lower:
                    overlap_score += 3

                if overlap_score > 0:
                    results.append({
                        "collection": col,
                        "content": item["content"],
                        "metadata": meta,
                        "score": overlap_score
                    })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

rag_service = AdvancedRAGService()
