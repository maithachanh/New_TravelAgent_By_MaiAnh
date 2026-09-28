import sys
import io
import json
from app.agent.graph import travel_agent_app
from app.services.currency_service import currency_service
from app.services.geo_service import geo_service

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_destination(prompt: str, label: str):
    print(f"\n=======================================================")
    print(f"=== TEST: {label} ===")
    print(f"👉 PROMPT: \"{prompt}\"")
    
    result = travel_agent_app.invoke({"user_prompt": prompt, "trip_id": None})
    
    extracted = result.get("extracted_requirements", {})
    dest_an = result.get("destination_analysis", {})
    itinerary = result.get("final_itinerary", [])
    airport = dest_an.get("nearest_airport", {})

    print(f"✓ Extracted Destination: {extracted.get('destination')}")
    print(f"✓ Resolved Location: {dest_an.get('resolved_name')}")
    print(f"✓ Country: {dest_an.get('country')} (Code: {dest_an.get('country_code')})")
    print(f"✓ Nearest Airport: {airport.get('name')} ({airport.get('iata')}) - {airport.get('distance_km')} km")
    print(f"✓ Local Currency & Rate: {dest_an.get('local_currency')} ({dest_an.get('rate_vnd')})")
    print(f"✓ Visa Info: {dest_an.get('visa_info')}")
    print(f"✓ Days Planned: {len(itinerary)}")

    if itinerary:
        print("  Sample Day 1 Activities:")
        for it in itinerary[0].get("items", [])[:3]:
            print(f"    • {it.get('start_time')} - {it.get('end_time')}: {it.get('title')} ({it.get('item_type')}) - {it.get('estimated_cost'):,.0f} VND")

def main():
    print("🌍 TESTING UNIVERSAL WORLDWIDE REAL-TIME TRAVEL PLANNING")

    # 1. A village in Austria
    test_destination(
        "Tôi muốn đi thăm làng Hallstatt ở Áo 3 ngày vào tháng 12, ngân sách 35 triệu, thích ngắm cảnh hồ và ẩm thực truyền thống.",
        "LÀNG HALLSTATT Ở ÁO (VILLAGE IN AUSTRIA)"
    )

    # 2. An alpine town in Switzerland
    test_destination(
        "Tôi muốn đi thị trấn Zermatt ở Thụy Sĩ 4 ngày ngắm tuyết và đỉnh Matterhorn, ngân sách 50 triệu.",
        "THỊ TRẤN ZERMATT Ở THỤY SĨ (TOWN IN SWITZERLAND)"
    )

    # 3. A village in Sa Pa Vietnam
    test_destination(
        "Tôi muốn đi bản Cát Cát Sa Pa 3 ngày nghỉ dưỡng cùng gia đình, ngân sách 12 triệu.",
        "BẢN CÁT CÁT SA PA (VILLAGE IN VIETNAM)"
    )

    # 4. South Korea
    test_destination(
        "Tôi muốn đi Hàn Quốc 5 ngày ăn thịt nướng và tham quan cung điện, ngân sách 28 triệu.",
        "HÀN QUỐC (SOUTH KOREA)"
    )

if __name__ == "__main__":
    main()
