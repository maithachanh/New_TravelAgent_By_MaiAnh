import requests
import time
from typing import Dict, Any, Optional

FALLBACK_RATES_TO_USD: Dict[str, float] = {
    "USD": 1.0,
    "VND": 25450.0,
    "EUR": 0.92,
    "JPY": 152.5,
    "KRW": 1380.0,
    "THB": 36.5,
    "CHF": 0.89,
    "GBP": 0.79,
    "AUD": 1.52,
    "SGD": 1.35,
    "CNY": 7.24,
    "CAD": 1.36,
    "ISK": 139.0,
    "NOK": 10.6,
    "SEK": 10.4,
    "DKK": 6.87,
    "NZD": 1.64,
    "MYR": 4.71,
    "IDR": 16200.0,
    "PHP": 58.5,
    "TWD": 32.4
}

class CurrencyExchangeService:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl_seconds = 3600  # 1 hour cache

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        from_c = from_currency.upper().strip()
        to_c = to_currency.upper().strip()

        if from_c == to_c:
            return 1.0

        cache_key = f"{from_c}_{to_c}"
        now = time.time()
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["timestamp"] < self._ttl_seconds:
                return entry["rate"]

        # Try live Frankfurter API
        try:
            url = f"https://api.frankfurter.app/latest?from={from_c}&to={to_c}"
            resp = requests.get(url, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                rate = float(data.get("rates", {}).get(to_c, 0.0))
                if rate > 0:
                    self._cache[cache_key] = {"rate": rate, "timestamp": now}
                    return rate
        except Exception:
            pass

        # Fallback to internal cross-rate calculation via USD base
        rate = self._compute_fallback_rate(from_c, to_c)
        self._cache[cache_key] = {"rate": rate, "timestamp": now}
        return rate

    def convert(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        rate = self.get_rate(from_currency, to_currency)
        converted_amount = amount * rate
        return {
            "amount": amount,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "rate": rate,
            "converted_amount": round(converted_amount, 2),
            "formatted": f"{converted_amount:,.2f} {to_currency.upper()}",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def _compute_fallback_rate(self, from_c: str, to_c: str) -> float:
        usd_to_from = FALLBACK_RATES_TO_USD.get(from_c, 1.0)
        usd_to_to = FALLBACK_RATES_TO_USD.get(to_c, 1.0)
        # 1 from_c = (1 / usd_to_from) * usd_to_to
        if usd_to_from == 0:
            return 1.0
        return (1.0 / usd_to_from) * usd_to_to

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
            "MYR": "Malaysian Ringgit (MYR)",
            "IDR": "Indonesian Rupiah (IDR)",
            "PHP": "Philippine Peso (PHP)",
            "TWD": "New Taiwan Dollar (TWD)"
        }

currency_service = CurrencyExchangeService()
