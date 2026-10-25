import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "Online"

def test_currency_rates_endpoint():
    resp = client.get("/api/v1/currency/rates?base=USD")
    assert resp.status_code == 200
    data = resp.json()
    assert data["base"] == "USD"
    assert "VND" in data["rates"]

def test_currency_rate_pair_endpoint():
    resp = client.get("/api/v1/currency/rate?from=USD&to=VND")
    assert resp.status_code == 200
    data = resp.json()
    assert data["rate"] > 20000.0

def test_flights_search_keys():
    resp = client.post("/api/v1/flights/search", json={
        "origin": "Hà Nội",
        "destination": "Tokyo",
        "travelers": 2
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "offers" in data
    assert "flights" in data

def test_hotels_search_keys():
    resp = client.post("/api/v1/hotels/search", json={
        "city": "Tokyo"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "accommodations" in data
    assert "hotels" in data

def test_trips_list_endpoint():
    resp = client.get("/api/v1/trips/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_ai_plan_trip_flow():
    resp = client.post("/api/v1/agent/plan-trip", json={
        "prompt": "Tôi muốn đi Tokyo 3 ngày 2 đêm từ Hà Nội, ngân sách 35 triệu cho 2 người"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "itinerary" in data
    assert "destination" in data
    assert len(data["itinerary"]) > 0
    trip_id = data.get("trip_id")
    assert trip_id is not None

    # Test PDF generation endpoint
    pdf_resp = client.get(f"/api/v1/trips/{trip_id}/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 1000

    # Test Trip Modify Endpoint
    mod_resp = client.patch(f"/api/v1/trips/{trip_id}/modify", json={
        "notes": "Đổi giờ ăn tối sang 20:00",
        "new_start_time": "20:00"
    })
    assert mod_resp.status_code == 200
    assert mod_resp.json()["success"] is True
    assert mod_resp.json()["version"] >= 2

    # Test Trip Modify via /ai prefix
    ai_mod_resp = client.patch(f"/api/v1/ai/trips/{trip_id}/modify", json={
        "notes": "Đổi giờ dậy sớm",
        "new_start_time": "07:30"
    })
    assert ai_mod_resp.status_code == 200
    assert ai_mod_resp.json()["success"] is True

    # Test Trip Confirm Endpoint
    conf_resp = client.post(f"/api/v1/trips/{trip_id}/confirm")
    assert conf_resp.status_code == 200
    assert conf_resp.json()["status"] == "CONFIRMED"

    # Test Trip Confirm via /ai prefix
    ai_conf_resp = client.post(f"/api/v1/ai/trips/{trip_id}/confirm")
    assert ai_conf_resp.status_code == 200
    assert ai_conf_resp.json()["status"] == "CONFIRMED"

def test_currency_cross_compatibility():
    # Calling /rates with pair
    resp1 = client.get("/api/v1/currency/rates?from=EUR&to=VND")
    assert resp1.status_code == 200
    assert resp1.json()["rate"] > 0

    # Calling /rate with base
    resp2 = client.get("/api/v1/currency/rate?base=USD")
    assert resp2.status_code == 200
    assert "rates" in resp2.json()

def test_translation_offline_phrases():
    resp = client.post("/api/v1/translation/translate", json={
        "text": "xin chào",
        "target_lang": "en"
    })
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["translated_text"] == "Hello"

def test_clarification_no_destination():
    resp = client.post("/api/v1/agent/plan-trip", json={
        "prompt": "Tư vấn tour du lịch giúp tôi"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "suggestions" in data or "agent_response" in data
