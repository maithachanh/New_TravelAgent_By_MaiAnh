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
