"""Currency conversion with real-time live rates, bounded cache, and multi-tier fallbacks."""

from __future__ import annotations

from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional
import requests

# Offline fallback reference values (only used if all live rate APIs are unreachable)
OFFLINE_RATES_TO_USD: Dict[str, float] = {
    "USD": 1.0,
    "VND": 25_950.0,
    "EUR": 0.89,
    "JPY": 157.7,
    "KRW": 1_390.0,
    "THB": 36.8,
    "CHF": 0.88,
    "GBP": 0.78,
    "AUD": 1.54,
    "SGD": 1.34,
    "CNY": 7.24,
    "CAD": 1.37,
    "ISK": 138.0,
    "NOK": 10.8,
    "SEK": 10.5,
    "DKK": 6.85,
    "NZD": 1.68,
    "MYR": 4.68,
    "IDR": 16_300.0,
    "PHP": 58.2,
    "TWD": 32.2,
}


class CurrencyExchangeService:
    def __init__(self) -> None:
        self._rates_cache: Dict[str, float] = {}
        self._cache_timestamp: float = 0.0
        self._cache_last_updated_str: str = ""
        self._cache_source: str = ""
        self._ttl_seconds: int = 15 * 60  # Cache live table for 15 minutes

    def _fetch_live_rates(self) -> bool:
        """
        Fetches live exchange rates from high-availability open APIs.
        Supports 160+ world currencies including VND, USD, EUR, JPY, KRW, CHF, etc.
        """
        now = time.time()
        # 1. Primary: open.er-api.com
        try:
            resp = requests.get("https://open.er-api.com/v6/latest/USD", timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                rates = data.get("rates", {})
                if rates and "VND" in rates and "EUR" in rates:
                    self._rates_cache = {k.upper(): float(v) for k, v in rates.items()}
                    self._cache_timestamp = now
                    self._cache_last_updated_str = data.get("time_last_update_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
                    self._cache_source = "Open Exchange Rates API (Cập nhật thời gian thực)"
                    return True
        except Exception:
            pass

        # 2. Secondary fallback: exchangerate-api.com
        try:
            resp = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                rates = data.get("rates", {})
                if rates and "VND" in rates:
                    self._rates_cache = {k.upper(): float(v) for k, v in rates.items()}
                    self._cache_timestamp = now
                    self._cache_last_updated_str = data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
                    self._cache_source = "ExchangeRate-API (Cập nhật thời gian thực)"
                    return True
        except Exception:
            pass

        return False

    def _ensure_rates(self) -> None:
        now = time.time()
        if not self._rates_cache or (now - self._cache_timestamp > self._ttl_seconds):
            success = self._fetch_live_rates()
            if not success and not self._rates_cache:
                # If network is completely offline, populate with offline table
                self._rates_cache = OFFLINE_RATES_TO_USD.copy()
                self._cache_timestamp = now
                self._cache_last_updated_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                self._cache_source = "Bảng tỷ giá tham chiếu dự phòng (Ngoại tuyến)"

    def get_rate_details(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        from_c = (from_currency or "VND").upper().strip()
        to_c = (to_currency or "USD").upper().strip()

        if from_c == to_c:
            return {
                "rate": 1.0,
                "from_currency": from_c,
                "to_currency": to_c,
                "source": "Cùng loại tiền tệ",
                "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            }

        self._ensure_rates()
        rates = self._rates_cache

        usd_to_from = rates.get(from_c) or OFFLINE_RATES_TO_USD.get(from_c, 1.0)
        usd_to_to = rates.get(to_c) or OFFLINE_RATES_TO_USD.get(to_c, 1.0)

        # 1 from_c = (1 / usd_to_from) * usd_to_to
        if usd_to_from <= 0:
            rate = 1.0
        else:
            rate = (1.0 / usd_to_from) * usd_to_to

        return {
            "rate": round(rate, 6 if rate < 1 else 4),
            "from_currency": from_c,
            "to_currency": to_c,
            "source": self._cache_source,
            "last_updated": self._cache_last_updated_str
        }

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        return float(self.get_rate_details(from_currency, to_currency)["rate"])

    def convert(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        if amount <= 0:
            amount = 1.0

        details = self.get_rate_details(from_currency, to_currency)
        rate = details["rate"]
        converted_amount = amount * rate

        from_c = details["from_currency"]
        to_c = details["to_currency"]

        # Formatting
        if to_c in ["VND", "JPY", "KRW"]:
            formatted = f"{round(converted_amount):,.0f} {to_c}"
        else:
            formatted = f"{converted_amount:,.2f} {to_c}"

        return {
            "amount": amount,
            "from_currency": from_c,
            "to_currency": to_c,
            "rate": rate,
            "converted_amount": round(converted_amount, 2),
            "formatted": formatted,
            "source": details["source"],
            "last_updated": details["last_updated"]
        }

    def get_supported_currencies(self) -> Dict[str, str]:
        return {
            "VND": "Việt Nam Đồng (VND)",
            "USD": "United States Dollar (USD)",
            "EUR": "Euro (EUR)",
            "JPY": "Japanese Yen (JPY)",
            "KRW": "South Korean Won (KRW)",
            "THB": "Thai Baht (THB)",
            "CHF": "Swiss Franc (CHF)",
            "GBP": "British Pound (GBP)",
            "AUD": "Australian Dollar (AUD)",
            "SGD": "Singapore Dollar (SGD)",
            "CNY": "Chinese Yuan (CNY)",
            "CAD": "Canadian Dollar (CAD)",
            "ISK": "Icelandic Króna (ISK)",
            "NOK": "Norwegian Krone (NOK)",
            "SEK": "Swedish Krona (SEK)",
            "TWD": "New Taiwan Dollar (TWD)",
            "MYR": "Malaysian Ringgit (MYR)",
            "IDR": "Indonesian Rupiah (IDR)",
            "PHP": "Philippine Peso (PHP)",
        }

    def get_all_rates(self, base_currency: str = "USD") -> Dict[str, Any]:
        """Returns all exchange rates relative to the requested base currency."""
        base_c = (base_currency or "USD").upper().strip()
        self._ensure_rates()
        usd_to_base = self._rates_cache.get(base_c) or OFFLINE_RATES_TO_USD.get(base_c, 1.0)
        if usd_to_base <= 0:
            usd_to_base = 1.0

        rates = {}
        for cur, rate_to_usd in self._rates_cache.items():
            rate = (1.0 / usd_to_base) * rate_to_usd
            rates[cur] = round(rate, 6 if rate < 1 else 4)

        return {
            "base": base_c,
            "rates": rates,
            "source": self._cache_source,
            "last_updated": self._cache_last_updated_str or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }


currency_service = CurrencyExchangeService()
