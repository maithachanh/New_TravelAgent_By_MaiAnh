import sys
import io
import json
from app.agent.graph import travel_agent_app
from app.services.rag_service import rag_service

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_korea_prompt():
    print("\n=======================================================")
    print("=== TESTING HÀN QUỐC PROMPT EXTRACTION & ITINERARY ===")
    print("=======================================================\n")
    
    prompt = "Tôi muốn đi Hàn Quốc 5 ngày vào tháng 12, ngân sách khoảng 30 triệu, thích ẩm thực, mua sắm và tham quan văn hóa cung điện."
    print(f"👉 USER PROMPT: \"{prompt}\"\n")

    initial_state = {
        "user_prompt": prompt,
        "trip_id": None
    }
    
    result = travel_agent_app.invoke(initial_state)

    print("--- 1. REQUIREMENT EXTRACTION RESULT ---")
    extracted = result.get("extracted_requirements", {})
    print(json.dumps(extracted, ensure_ascii=False, indent=2))

    print("\n--- 2. DESTINATION ANALYSIS & VISA INFO ---")
    dest_an = result.get("destination_analysis", {})
    print("Destination:", dest_an.get("destination"))
    print("Best Districts:", dest_an.get("best_districts"))
    print("Visa Info:", dest_an.get("visa_info"))
    print("Currency Rate:", dest_an.get("currency_rate"))

    print("\n--- 3. AGENT RESPONSE ---")
    print(result.get("agent_response"))

    print("\n--- 4. FINAL ITINERARY DAYS FOR HÀN QUỐC ---")
    itinerary = result.get("final_itinerary", [])
    print(f"Total Days Generated: {len(itinerary)}")
    
    for day in itinerary:
        print(f"\n[Day {day['day_number']} - {day['date']}]")
        for item in day.get("items", []):
            print(f"  • {item['start_time']} - {item['end_time']}: {item['title']} ({item['item_type']}) - Cost: {item['estimated_cost']:,.0f} VND")

    print("\n--- 5. RAG MULTI-COLLECTION RETRIEVAL TEST (HÀN QUỐC) ---")
    rag_docs = rag_service.query("Hàn Quốc visa K-ETA T-Money", collection_name="travel_rules")
    for doc in rag_docs:
        print(f"[{doc['collection']}] {doc['content']}")

if __name__ == "__main__":
    test_korea_prompt()
