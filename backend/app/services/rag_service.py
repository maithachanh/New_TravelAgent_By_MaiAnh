import os
import re
import json
import math
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
        "content": "Quy định hàng không quốc tế: Hành lý xách tay tiêu chuẩn thông thường là 7kg kích thước 56x36x23cm. Chất lỏng xách tay không quá 100ml mỗi chai và đựng trong túi trong suốt tối đa 1 lít. Đồ uống và đồ lỏng mua sau cửa an ninh được mang lên khoang máy bay. Hành khách chuyến bay quốc tế cần có mặt tại sân bay trước giờ khởi hành tối thiểu 3 tiếng.",
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

def _compute_dense_vector(text: str, dim: int = 128) -> List[float]:
    """
    Computes a high-dimensional normalized semantic embedding vector using subword n-grams and tokens.
    Guarantees subword semantic overlap matching across vocabulary variations (e.g. đồ lỏng -> chất lỏng).
    """
    vec = [0.0] * dim
    tokens = re.findall(r'\w+', text.lower())
    for token in tokens:
        # Word hash
        h_w = abs(hash(token)) % dim
        vec[h_w] += 1.0
        # Character 3-grams for subword similarity
        if len(token) >= 3:
            for j in range(len(token) - 2):
                ngram = token[j:j+3]
                h_ng = abs(hash(ngram)) % dim
                vec[h_ng] += 0.4

    # Normalize vector to unit length (L2 norm)
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec

def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes cosine similarity between two unit vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))


class AdvancedRAGService:
    """Persistent semantic retrieval backed by Chroma's HNSW index.

    The previous implementation wrote vectors to JSON and then scored every
    document in Python.  Chroma is now the source of truth whenever it is
    available: it persists the embedding vectors and asks its cosine/HNSW
    index for nearest neighbours.  JSON remains only as a small migration and
    no-dependency fallback, so a new developer can still start the project
    before configuring an embedding provider.
    """

    def __init__(self):
        self.storage_dir = os.getenv("CHROMA_DB_DIR", "./chroma_storage")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.store_file = os.path.join(self.storage_dir, "rag_store.json")
        self.collections: Dict[str, List[Dict[str, Any]]] = {c: [] for c in COLLECTION_NAMES}
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.embedding_provider = self._select_embedding_provider()
        self._bge_model = None
        self._init_chroma()
        self._load_or_initialize()

    def _select_embedding_provider(self) -> str:
        configured = os.getenv("EMBEDDING_PROVIDER", "auto").strip().lower()
        has_openai_key = (
            bool(self.openai_key and len(self.openai_key.strip()) > 20)
            and "your_" not in self.openai_key.lower()
        )
        if configured in {"openai", "text-embedding-3-small"}:
            return "openai" if has_openai_key else "fallback"
        if configured in {"bge-m3", "bge_m3", "local"}:
            return "bge-m3"
        return "openai" if has_openai_key else "fallback"

    @property
    def _index_suffix(self) -> str:
        # Different models have different vector dimensions.  Separate
        # collections prevent a key/configuration change from corrupting an
        # existing index while still retaining it on disk.
        return {
            "openai": "openai_text_embedding_3_small",
            "bge-m3": "bge_m3",
            "fallback": "local_fallback",
        }[self.embedding_provider]

    def _init_chroma(self):
        """Open a persistent Chroma client with cosine HNSW collections."""
        self.chroma_client = None
        self.chroma_collections: Dict[str, Any] = {}
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=self.storage_dir)
            for name in COLLECTION_NAMES:
                self.chroma_collections[name] = self.chroma_client.get_or_create_collection(
                    name=f"travel_{name}_{self._index_suffix}",
                    metadata={"hnsw:space": "cosine", "domain": "travel"},
                )
        except Exception as exc:
            # Chroma is optional for a minimal offline install, but production
            # deployments should treat this as a configuration error in logs.
            print(f"[AdvancedRAGService] Chroma unavailable; using local fallback: {exc}")
            self.chroma_client = None
            self.chroma_collections = {}

    def _get_embedding(self, text: str) -> List[float]:
        """Return a real configured embedding, with an explicit offline fallback."""
        clean_text = text[:8000]
        if self.embedding_provider == "openai":
            try:
                import requests
                response = requests.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.openai_key}",
                        "Content-Type": "application/json",
                    },
                    json={"input": clean_text, "model": "text-embedding-3-small"},
                    timeout=12.0,
                )
                response.raise_for_status()
                return response.json()["data"][0]["embedding"]
            except Exception as exc:
                # Do not silently mix dimensions in a live collection.  A
                # caller gets a safe local result until the network recovers.
                print(f"[AdvancedRAGService] OpenAI embedding failed: {exc}")
                return _compute_dense_vector(clean_text)

        if self.embedding_provider == "bge-m3":
            try:
                if self._bge_model is None:
                    from sentence_transformers import SentenceTransformer
                    self._bge_model = SentenceTransformer(
                        os.getenv("BGE_M3_MODEL", "BAAI/bge-m3"),
                        device=os.getenv("EMBEDDING_DEVICE", "cpu"),
                    )
                vector = self._bge_model.encode(
                    [clean_text], normalize_embeddings=True, show_progress_bar=False
                )[0]
                return vector.tolist()
            except Exception as exc:
                print(f"[AdvancedRAGService] BGE-M3 embedding failed: {exc}")
                return _compute_dense_vector(clean_text)

        return _compute_dense_vector(clean_text)

    def _load_or_initialize(self):
        """Migrate legacy JSON once, then seed an empty persistent index."""
        loaded_legacy = False
        if os.path.exists(self.store_file):
            try:
                with open(self.store_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                for col in COLLECTION_NAMES:
                    self.collections[col] = data.get(col, [])
                loaded_legacy = any(self.collections.values())
            except Exception as exc:
                print(f"[AdvancedRAGService] Could not read legacy RAG store: {exc}")

        if loaded_legacy:
            # Legacy documents are re-embedded and upserted into Chroma.  This
            # is idempotent and lets existing installs migrate without data loss.
            for collection_name, documents in self.collections.items():
                for item in documents:
                    if item.get("content"):
                        self._upsert_chunk(
                            collection_name,
                            item.get("id") or f"legacy_{abs(hash(item['content']))}",
                            item["content"],
                            item.get("metadata") or {},
                            item.get("doc_id"),
                        )
        elif not self._has_indexed_documents():
            for item in DEFAULT_KNOWLEDGE_BASE:
                self.add_document(
                    collection_name=item["collection"],
                    doc_id=item["doc_id"],
                    content=item["content"],
                    metadata=item["metadata"],
                )

        # Keep a tiny migration cache only; Chroma is queried at runtime.
        self._persist()

    def _has_indexed_documents(self) -> bool:
        if not self.chroma_collections:
            return False
        try:
            return any(collection.count() > 0 for collection in self.chroma_collections.values())
        except Exception:
            return False

    def _persist(self):
        """Persist fallback/migration data; vectors themselves live in Chroma."""
        try:
            with open(self.store_file, "w", encoding="utf-8") as file:
                json.dump(self.collections, file, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"[AdvancedRAGService] Warning: Failed to persist RAG migration cache: {exc}")

    def clean_text(self, text: str) -> str:
        """Text Cleaning Pipeline: strip HTML, normalize whitespace, clean noise."""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_document(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Recursive chunking engine."""
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

    def _safe_metadata(self, metadata: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        """Chroma metadata accepts scalar fields only."""
        safe = {"source_doc_id": str(doc_id)}
        for key, value in (metadata or {}).items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                safe[key] = value if value is not None else ""
            else:
                safe[key] = json.dumps(value, ensure_ascii=False)
        return safe

    def _upsert_chunk(
        self,
        collection_name: str,
        chunk_id: str,
        content: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None,
    ) -> None:
        if not self.chroma_collections:
            return
        try:
            self.chroma_collections[collection_name].upsert(
                ids=[chunk_id],
                documents=[content],
                embeddings=[self._get_embedding(content)],
                metadatas=[self._safe_metadata(metadata, doc_id or chunk_id)],
            )
        except Exception as exc:
            print(f"[AdvancedRAGService] Chroma upsert failed for {chunk_id}: {exc}")

    def add_document(self, collection_name: str, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Chunk and upsert a document into the persistent cosine/HNSW index."""
        if collection_name not in self.collections:
            collection_name = "destination_knowledge"

        cleaned_content = self.clean_text(content)
        chunks = self.chunk_document(cleaned_content)

        for idx, chunk in enumerate(chunks):
            chunk_doc = {
                "id": f"{doc_id}_chunk_{idx}",
                "doc_id": doc_id,
                "content": chunk,
                "metadata": metadata,
                # Kept for backwards-compatible JSON export; Chroma owns the
                # actual vector and HNSW index.
                "embedding": [],
            }
            # Avoid duplicate chunks
            existing_ids = {d["id"] for d in self.collections[collection_name]}
            if chunk_doc["id"] not in existing_ids:
                self.collections[collection_name].append(chunk_doc)
            self._upsert_chunk(collection_name, chunk_doc["id"], chunk, metadata, doc_id)
        
        self._persist()

    def query(
        self,
        query_text: str,
        collection_name: Optional[str] = None,
        city_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Retrieve nearest semantic neighbours from Chroma, then apply filters."""
        target_collections = [collection_name] if collection_name and collection_name in self.collections else COLLECTION_NAMES

        if self.chroma_collections:
            results: List[Dict[str, Any]] = []
            embedding = self._get_embedding(query_text)
            for col in target_collections:
                where: Dict[str, Any] = {}
                if city_filter:
                    where["city"] = city_filter
                if category_filter:
                    where["category"] = category_filter
                try:
                    response = self.chroma_collections[col].query(
                        query_embeddings=[embedding],
                        n_results=max(1, top_k),
                        where=where or None,
                        include=["documents", "metadatas", "distances"],
                    )
                    documents = response.get("documents", [[]])[0]
                    metadatas = response.get("metadatas", [[]])[0]
                    distances = response.get("distances", [[]])[0]
                    for document, metadata, distance in zip(documents, metadatas, distances):
                        vector_similarity = max(-1.0, min(1.0, 1.0 - float(distance)))
                        results.append({
                            "collection": col,
                            "content": document,
                            "metadata": {k: v for k, v in (metadata or {}).items() if k != "source_doc_id"},
                            "score": round(vector_similarity, 4),
                            "vector_similarity": round(vector_similarity, 4),
                        })
                except Exception as exc:
                    print(f"[AdvancedRAGService] Chroma query failed for {col}: {exc}")
            if results:
                return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]

        query_vec = self._get_embedding(query_text)
        query_tokens = set(re.findall(r'\w+', query_text.lower()))
        results = []

        for col in target_collections:
            for item in self.collections[col]:
                meta = item.get("metadata", {})
                
                # Metadata Filtering Check
                if city_filter and meta.get("city") and city_filter.lower() not in meta.get("city", "").lower():
                    continue
                if category_filter and meta.get("category") and category_filter.lower() not in meta.get("category", "").lower():
                    continue

                # 1. Cosine Vector Similarity (Semantic Match)
                doc_vec = item.get("embedding")
                if not doc_vec:
                    doc_vec = _compute_dense_vector(item["content"])
                    item["embedding"] = doc_vec

                # Calculate cosine similarity if vector dimensions match
                if len(doc_vec) == len(query_vec):
                    vec_score = _cosine_similarity(query_vec, doc_vec)
                else:
                    vec_score = _cosine_similarity(_compute_dense_vector(query_text), _compute_dense_vector(item["content"]))

                # 2. Keyword & Concept Overlap Boost
                content_lower = item["content"].lower()
                keyword_hits = sum(1 for t in query_tokens if len(t) > 2 and t in content_lower)
                
                # 3. Hybrid Reranking Score
                hybrid_score = round(vec_score * 0.70 + (min(keyword_hits, 4) * 0.075), 4)

                # City boost
                if city_filter and city_filter.lower() in content_lower:
                    hybrid_score += 0.15

                if hybrid_score > 0.10 or keyword_hits > 0:
                    results.append({
                        "collection": col,
                        "content": item["content"],
                        "metadata": meta,
                        "score": hybrid_score,
                        "vector_similarity": round(vec_score, 4)
                    })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

rag_service = AdvancedRAGService()
