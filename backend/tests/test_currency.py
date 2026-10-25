import pytest
from app.services.currency_service import currency_service

def test_supported_currencies():
    supported = currency_service.get_supported_currencies()
    assert "USD" in supported
    assert "VND" in supported
    assert "EUR" in supported
    assert "JPY" in supported
    assert "GBP" in supported

def test_exchange_rate_usd_vnd():
    details = currency_service.get_rate_details("USD", "VND")
    assert details["from_currency"] == "USD"
    assert details["to_currency"] == "VND"
    assert details["rate"] > 20000.0

def test_convert_currency():
    res = currency_service.convert(100.0, "USD", "VND")
    assert res["amount"] == 100.0
    assert res["from_currency"] == "USD"
    assert res["to_currency"] == "VND"
    assert res["converted_amount"] > 2_000_000.0

def test_get_all_rates():
    data = currency_service.get_all_rates("USD")
    assert data["base"] == "USD"
    assert "rates" in data
    assert "VND" in data["rates"]
    assert "EUR" in data["rates"]
    assert data["rates"]["USD"] == 1.0
