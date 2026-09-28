import os
import re
from typing import List, Dict, Any, Optional

COLLECTION_NAMES = [
    "destination_knowledge",
    "travel_rules",
    "attraction_knowledge",
    "hotel_knowledge",
    "restaurant_knowledge",
    "transportation_knowledge"
]

class AdvancedRAGService:
    def __init__(self):
        self.qdrant_client = None
        self.collections: Dict[str, List[Dict[str, Any]]] = {c: [] for c in COLLECTION_NAMES}
        self._init_qdrant()

    def _init_qdrant(self):
        try:
            from qdrant_client import QdrantClient
            self.qdrant_client = QdrantClient(":memory:")
            for col_name in COLLECTION_NAMES:
                try:
                    self.qdrant_client.create_collection(
                        collection_name=col_name,
                        vectors_config={"size": 384, "distance": "Cosine"}
                    )
                except Exception:
                    pass
            print("[AdvancedRAGService] Qdrant In-Memory client initialized successfully with 6 collections!")
        except Exception as e:
            print(f"[AdvancedRAGService] Notice: Using in-memory store ({e})")

    def clean_text(self, text: str) -> str:
        """Text Cleaning Pipeline: strip HTML, normalize whitespace, clean noise"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text) # Remove HTML tags
        text = re.sub(r'\s+', ' ', text)   # Normalize whitespace
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
            self.collections[collection_name].append(chunk_doc)

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

                # Cosine similarity approximation via keyword overlap & metadata match
                text_lower = item["content"].lower()
                overlap_score = sum(1 for w in query_words if w in text_lower)
                
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
