"""Weather retrieval and itinerary-safe fallback recommendations.

OpenWeather is used only when the application is configured with a server-side
API key.  Planning must remain useful offline, so seasonal guidance is
deterministic and explicitly marked as such when no live forecast is present.
"""

from __future__ import annotations

import os
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional

import requests


SEVERE_CONDITIONS = {"thunderstorm", "tornado", "squall"}
WET_CONDITIONS = {"rain", "drizzle", "snow"}


class WeatherService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
        self.base_url = os.getenv(
            "OPENWEATHER_FORECAST_URL", "https://api.openweathermap.org/data/2.5/forecast"
        )

    def get_forecast(
        self, latitude: Optional[float], longitude: Optional[float], travel_dates: Iterable[str]
    ) -> Dict[str, Any]:
        """Get a 5-day/3-hour OpenWeather forecast, never exposing the API key.

        OpenWeather only covers near-term dates, therefore dates beyond its
        response are omitted rather than represented as invented live weather.
        """
        if not self.api_key or latitude is None or longitude is None:
            return {"source": "seasonal_fallback", "days": [], "is_live": False}
        try:
            response = requests.get(
                self.base_url,
                params={"lat": latitude, "lon": longitude, "appid": self.api_key, "units": "metric"},
                timeout=5,
            )
            response.raise_for_status()
            grouped: Dict[str, List[Dict[str, Any]]] = {}
            for entry in response.json().get("list", []):
                stamp = entry.get("dt_txt", "")
                day_key = stamp[:10]
                if day_key:
                    grouped.setdefault(day_key, []).append(entry)

            requested = set(travel_dates)
            days = []
            for day_key, entries in grouped.items():
                if requested and day_key not in requested:
                    continue
                codes = [str(entry.get("weather", [{}])[0].get("main", "Clear")).lower() for entry in entries]
                rain_probability = max(float(entry.get("pop", 0.0)) for entry in entries)
                temp_values = [float(entry.get("main", {}).get("temp", 0.0)) for entry in entries]
                condition = next((item for item in codes if item in SEVERE_CONDITIONS), None)
                condition = condition or next((item for item in codes if item in WET_CONDITIONS), codes[0] if codes else "clear")
                days.append({
                    "date": day_key,
                    "condition": condition,
                    "rain_probability": round(rain_probability, 2),
                    "temperature_c": round(sum(temp_values) / len(temp_values), 1) if temp_values else None,
                    "severe": condition in SEVERE_CONDITIONS,
                })
            return {"source": "openweather", "days": days, "is_live": True}
        except Exception:
            return {"source": "seasonal_fallback", "days": [], "is_live": False}

    @staticmethod
    def is_risky(forecast: Dict[str, Any]) -> bool:
        return any(
            day.get("severe") or day.get("rain_probability", 0) >= 0.65
            or day.get("condition") in WET_CONDITIONS
            for day in forecast.get("days", [])
        )

    @staticmethod
    def backup_suggestions(city: str) -> List[str]:
        return [
            f"Bảo tàng nghệ thuật/lịch sử tại {city}",
            f"Thủy cung hoặc không gian trải nghiệm trong nhà tại {city}",
            "Trung tâm thương mại có mái che, lớp nấu ăn hoặc quán cà phê ngắm cảnh",
        ]

    @staticmethod
    def seasonal_advisory(country_code: str, city: str, travel_month: int) -> Dict[str, Any]:
        """Conservative regional advisory used only when no live forecast exists."""
        tropical = country_code in {"VN", "TH", "MY", "PH", "ID"}
        if tropical and 5 <= travel_month <= 10:
            message = f"{city} đang trong giai đoạn mưa nhiệt đới theo mùa; hãy giữ một phương án trong nhà."
            if "phú quốc" in city.lower() or "phu quoc" in city.lower():
                message = "Phú Quốc vào mùa mưa (tháng 5–10); nên ưu tiên hoạt động trong nhà và chỉ đi biển/tour đảo khi dự báo an toàn."
            return {"message": message, "risky": True}
        if country_code in {"JP", "KR"} and travel_month in {6, 7, 8}:
            return {"message": f"{city} có thể nóng ẩm hoặc mưa rào mùa hè; chuẩn bị phương án tránh nắng/mưa.", "risky": False}
        return {"message": f"Chưa thấy rủi ro thời tiết theo mùa nổi bật tại {city} cho tháng {travel_month}.", "risky": False}


weather_service = WeatherService()
