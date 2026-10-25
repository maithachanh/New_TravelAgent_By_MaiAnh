import pytest
from app.services.request_parser import parse_travel_request, classify_intent

def test_japan_family_trip_prompt():
    prompt = (
        "Tôi muốn đi khắp Nhật Bản trong vòng 7 ngày 6 đêm. "
        "Ngân sách cho chuyến đi này là 500 triệu bao gồm tiền chuyến bay cả đi lẫn về của 4 người. "
        "Chuyến đi này dành cho gia đình 4 người. Chúng tôi ở Thành Phố Hồ Chí Minh."
    )
    req = parse_travel_request(prompt)
    
    # Destination must be Japan / Tokyo, NOT Ho Chi Minh City!
    assert "Nhật Bản" in req["destination"] or "Tokyo" in req["destination"]
    assert "Hồ Chí Minh" not in req["destination"]
    
    # Origin must be Ho Chi Minh City
    assert "Hồ Chí Minh" in req["origin"] or "TP. Hồ Chí Minh" in req["origin"]
    
    # Duration and Travelers
    assert req["duration"] == 7
    assert req["travelers"] == 4
    assert req["budget"] == 500_000_000.0

def test_date_range_duration_extraction():
    prompt = "Tôi muốn đi du lịch từ ngày 25-7 đến 5-8, khởi hành từ Hà Nội đến Đà Nẵng, 2 người"
    req = parse_travel_request(prompt)
    
    # 25-07 to 05-08 is exactly 12 days
    assert req["duration"] == 12
    assert "Đà Nẵng" in req["destination"]
    assert "Hà Nội" in req["origin"]
    assert req["travelers"] == 2

def test_foreign_currency_budget():
    prompt = "Tôi muốn đi Liverpool 5 ngày, ngân sách 10000 bảng anh cho 2 người từ TP.HCM"
    req = parse_travel_request(prompt)
    
    assert "Liverpool" in req["destination"]
    # 10,000 GBP in VND is around 300M+ VND (> 250,000,000)
    assert req["budget"] > 250_000_000

def test_intent_classification():
    assert classify_intent("Tôi muốn đặt chuyến đi mới sang Hàn Quốc") == "PLAN_NEW_TRIP"
    assert classify_intent("Đổi giờ khởi hành của chuyến bay") == "REPLAN_TRIP"
