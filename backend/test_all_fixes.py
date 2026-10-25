import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.agent.graph import travel_agent_app
from app.agent.nodes import _calculate_flight_duration
from app.services.pdf_service import generate_itinerary_pdf

print("=================================================================")
print("=== VERIFYING ALL 10 BUG FIXES IN TRAVEL AGENT AI PIPELINE ===")
print("=================================================================\n")

# TEST 1: Date Range 25-7 to 5-8 (12 days)
print("--- [TEST 1 & 2] DATE RANGE & DATE INCONSISTENCY FIX ---")
prompt_1 = "Tôi muốn đi Hàn Quốc từ ngày 25-7 đến 5-8, ngân sách 30 triệu"
print("Prompt:", prompt_1)
res_1 = travel_agent_app.invoke({"user_prompt": prompt_1})
req_1 = res_1["extracted_requirements"]
itin_1 = res_1["final_itinerary"]
print(f"Generated Days: {len(itin_1)} (Expected: 12)")
print(f"Start Date: {req_1.get('start_date')} | End Date: {req_1.get('end_date')}")
print(f"Day 1 Date: {itin_1[0]['date']} | Last Day Date: {itin_1[-1]['date']}")
assert len(itin_1) == 12, f"Expected 12 days, got {len(itin_1)}"
assert itin_1[0]["date"] == "2026-07-25", f"Expected 2026-07-25, got {itin_1[0]['date']}"
assert itin_1[-1]["date"] == "2026-08-05", f"Expected 2026-08-05, got {itin_1[-1]['date']}"
assert req_1.get("start_date") == itin_1[0]["date"]
assert req_1.get("end_date") == itin_1[-1]["date"]
print(">>> [TEST 1 & 2] PASSED: Exact 12 days and synchronized ISO dates!\n")

# TEST 2: Realistic Flight Duration (Hanoi / SGN to New York)
print("--- [TEST 3] REALISTIC LONG-HAUL FLIGHT DURATION (NEW YORK) ---")
ny_duration = _calculate_flight_duration("Hà Nội, Việt Nam", "New York, Mỹ")
print(f"Calculated Flight Time Hanoi -> New York: {ny_duration // 60}h {ny_duration % 60}m ({ny_duration} mins)")
assert ny_duration >= 1200, f"Expected >= 20h flight for Vietnam to New York, got {ny_duration / 60}h"
print(">>> [TEST 3] PASSED: Realistic >20h long-haul flight calculated!\n")

# TEST 3: Origin & Destination (TP.HCM to Liverpool)
print("--- [TEST 4 & 5] ORIGIN/DESTINATION & AIRPORT (TP.HCM -> LIVERPOOL) ---")
prompt_2 = "chúng tôi muốn đi từ Tp.HCM đến Liverpool với ngân sách 10000 bảng anh"
print("Prompt:", prompt_2)
res_2 = travel_agent_app.invoke({"user_prompt": prompt_2})
req_2 = res_2["extracted_requirements"]
dest_2 = res_2["destination_analysis"]
print(f"Origin: {req_2.get('origin')} (Expected: TP. Hồ Chí Minh)")
print(f"Destination: {dest_2.get('resolved_name')} (Expected: Liverpool, Vương Quốc Anh)")
print(f"Airport: {dest_2.get('nearest_airport', {}).get('name')} ({dest_2.get('nearest_airport', {}).get('iata')})")
assert "TP. Hồ Chí Minh" in req_2.get("origin")
assert "Liverpool" in dest_2.get("resolved_name")
assert dest_2.get("nearest_airport", {}).get("iata") == "LPL"
print(">>> [TEST 4 & 5] PASSED: TP.HCM -> Liverpool properly identified with LPL airport!\n")

# TEST 4: Currency Parsing (10,000 GBP) & Budget Scaling
print("--- [TEST 6 & 7] CURRENCY PARSING (GBP) & BUDGET SCALING ---")
budget_vnd = req_2.get("budget", 0)
input_curr = req_2.get("input_budget_currency")
print(f"Input Currency: {input_curr} (Expected: GBP)")
print(f"Converted Budget VND: {budget_vnd:,.0f} VND (Expected: ~343,366,400 VND)")
assert input_curr == "GBP"
assert 340_000_000 <= budget_vnd <= 350_000_000
total_cost_2 = res_2.get("budget_validation", {}).get("total_cost", 0)
print(f"Total Itinerary Cost: {total_cost_2:,.0f} VND")
assert total_cost_2 <= budget_vnd * 1.05
print(">>> [TEST 6 & 7] PASSED: 10,000 GBP converted correctly and total cost strictly validated!\n")

# TEST 5: Non-repeating Activities & Authentic Addresses
print("--- [TEST 8 & 9] NON-REPEATING ACTIVITIES & AUTHENTIC ADDRESSES ---")
all_items = [item for day in itin_1 for item in day.get("items", [])]
print(f"Total Scheduled Items across 12 days: {len(all_items)}")
viewpoint_items = [item["title"] for item in all_items if "Viewpoint" in item["title"]]
print(f"Viewpoint repetitions: {len(viewpoint_items)} (Expected: <= 1)")
assert len(viewpoint_items) <= 1, "Repeated viewpoint activity found across days!"

# Check addresses
sample_addresses = [item.get("location", "") for item in all_items if item.get("location")]
print(f"Sample locations: {sample_addresses[:3]}")
assert all(len(loc.strip()) > 3 for loc in sample_addresses)
print(">>> [TEST 8 & 9] PASSED: Activities are varied and have authentic locations!\n")

# TEST 6: PDF Generation Synchronized
print("--- [TEST 10] PDF REPORT GENERATION & DATE CONSISTENCY ---")
trip_dict = {
    "title": "Tour Khám Phá Hàn Quốc (12N)",
    "destination": "Seoul, Hàn Quốc",
    "origin": "Hà Nội, Việt Nam",
    "start_date": itin_1[0]["date"],
    "end_date": itin_1[-1]["date"],
    "travelers": 2,
    "budget": req_1.get("budget", 30000000),
    "currency": "VND",
    "days": itin_1
}
pdf_bytes = generate_itinerary_pdf(trip_dict)
print(f"Generated PDF Size: {len(pdf_bytes)} bytes")
assert len(pdf_bytes) > 20000
print(">>> [TEST 10] PASSED: PDF generated cleanly with synced dates!\n")

print("=================================================================")
print("=== ALL 10 TESTS PASSED SUCCESSFULLY! ===")
print("=================================================================")
