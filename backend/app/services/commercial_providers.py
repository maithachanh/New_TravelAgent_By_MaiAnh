"""Credential-gated adapters for commercial travel and place providers.

These adapters return *offers*, never booking confirmations.  A supplier may
change its contract, therefore every live call is isolated here and falls back
to the planner's labelled estimate only when credentials or a response are not
available.  Secrets stay server-side and are never returned to clients.
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import requests

from app.services.geo_service import geo_service


class CommercialProviderService:
    def _airport_iata(self, place: str) -> Optional[str]:
        try:
            airport = geo_service.resolve_destination(place).get("nearest_airport", {})
            return airport.get("iata")
        except Exception:
            return None

    def search_flights(
        self, origin: str, destination: str, departure_date: Optional[str], travelers: int
    ) -> Optional[List[Dict[str, Any]]]:
        origin_iata = self._airport_iata(origin)
        destination_iata = self._airport_iata(destination)
        if not origin_iata or not destination_iata:
            return None
        departure_date = departure_date or (date.today() + timedelta(days=30)).isoformat()
        return (
            self._search_duffel(origin_iata, destination_iata, departure_date, travelers)
            or self._search_amadeus(origin_iata, destination_iata, departure_date, travelers)
        )

    def _search_duffel(
        self, origin: str, destination: str, departure_date: str, travelers: int
    ) -> Optional[List[Dict[str, Any]]]:
        token = os.getenv("DUFFEL_ACCESS_TOKEN", "").strip()
        if not token:
            return None
        try:
            passengers = [{"type": "adult"} for _ in range(max(1, travelers))]
            response = requests.post(
                "https://api.duffel.com/air/offer_requests",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Duffel-Version": "v2",
                    "Content-Type": "application/json",
                },
                json={"data": {"slices": [{"origin": origin, "destination": destination, "departure_date": departure_date}], "passengers": passengers}},
                timeout=12,
            )
            response.raise_for_status()
            offers = response.json().get("data", {}).get("offers", [])
            normalized: List[Dict[str, Any]] = []
            for offer in offers[:10]:
                segments = offer.get("slices", [{}])[0].get("segments", [])
                first = segments[0] if segments else {}
                normalized.append({
                    "offer_id": offer.get("id"),
                    "provider": "Duffel",
                    "is_live": True,
                    "airline": first.get("marketing_carrier", {}).get("name", "Airline"),
                    "flight_number": first.get("marketing_carrier_flight_number", ""),
                    "origin": origin,
                    "destination": destination,
                    "departure": first.get("departing_at"),
                    "arrival": segments[-1].get("arriving_at") if segments else None,
                    "stops": max(0, len(segments) - 1),
                    "price_total": float(offer.get("total_amount", 0)),
                    "currency": offer.get("total_currency", "USD"),
                    "booking_url": None,
                })
            return normalized or None
        except Exception:
            return None

    def _search_amadeus(
        self, origin: str, destination: str, departure_date: str, travelers: int
    ) -> Optional[List[Dict[str, Any]]]:
        client_id = os.getenv("AMADEUS_CLIENT_ID", "").strip()
        client_secret = os.getenv("AMADEUS_CLIENT_SECRET", "").strip()
        if not client_id or not client_secret:
            return None
        base_url = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com").rstrip("/")
        try:
            token_response = requests.post(
                f"{base_url}/v1/security/oauth2/token",
                data={"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret},
                timeout=8,
            )
            token_response.raise_for_status()
            token = token_response.json()["access_token"]
            response = requests.get(
                f"{base_url}/v2/shopping/flight-offers",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "originLocationCode": origin,
                    "destinationLocationCode": destination,
                    "departureDate": departure_date,
                    "adults": max(1, travelers),
                    "max": 10,
                },
                timeout=12,
            )
            response.raise_for_status()
            normalized: List[Dict[str, Any]] = []
            for offer in response.json().get("data", []):
                itinerary = offer.get("itineraries", [{}])[0]
                segments = itinerary.get("segments", [])
                first = segments[0] if segments else {}
                last = segments[-1] if segments else {}
                carrier = first.get("carrierCode", "")
                number = first.get("number", "")
                normalized.append({
                    "offer_id": offer.get("id"),
                    "provider": "Amadeus",
                    "is_live": True,
                    "airline": carrier or "Airline",
                    "flight_number": f"{carrier}{number}",
                    "origin": origin,
                    "destination": destination,
                    "departure": first.get("departure", {}).get("at"),
                    "arrival": last.get("arrival", {}).get("at"),
                    "stops": max(0, len(segments) - 1),
                    "price_total": float(offer.get("price", {}).get("grandTotal", 0)),
                    "currency": offer.get("price", {}).get("currency", "USD"),
                    "booking_url": None,
                })
            return normalized or None
        except Exception:
            return None

    def search_hotels(
        self, city: str, check_in: Optional[str], check_out: Optional[str]
    ) -> Optional[List[Dict[str, Any]]]:
        """Adapter for an approved Booking/Agoda partner endpoint.

        Booking.com and Agoda credentials are partner-specific.  Configure the
        endpoint supplied by that partner rather than hard-coding a private or
        unofficial API.  The normalizer accepts the common ``results`` shape.
        """
        endpoint = os.getenv("HOTEL_PROVIDER_URL", "").strip()
        api_key = os.getenv("HOTEL_PROVIDER_API_KEY", "").strip()
        if not endpoint or not api_key:
            return None
        try:
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
                params={"city": city, "check_in": check_in, "check_out": check_out},
                timeout=12,
            )
            response.raise_for_status()
            rows = response.json().get("results") or response.json().get("data") or []
            return [
                {
                    "provider": "Partner hotel feed",
                    "is_live": True,
                    "hotel_id": row.get("id") or row.get("hotel_id"),
                    "name": row.get("name") or row.get("hotel_name"),
                    "rating": row.get("rating") or row.get("review_score"),
                    "price_per_night": row.get("price_per_night") or row.get("price"),
                    "currency": row.get("currency", "USD"),
                    "address": row.get("address"),
                    "image_url": row.get("image_url") or row.get("image"),
                    "cancellation_policy": row.get("cancellation_policy"),
                    "availability": row.get("availability", "available"),
                    "booking_url": row.get("booking_url"),
                }
                for row in rows[:10]
            ] or None
        except Exception:
            return None

    def search_places(self, query: str, latitude: float, longitude: float, kind: str) -> Optional[List[Dict[str, Any]]]:
        """Google Places API (New) text search with opening hours and ratings."""
        key = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()
        if not key:
            return None
        try:
            response = requests.post(
                "https://places.googleapis.com/v1/places:searchText",
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": key,
                    "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.regularOpeningHours,places.googleMapsUri,places.photos",
                },
                json={"textQuery": query, "locationBias": {"circle": {"center": {"latitude": latitude, "longitude": longitude}, "radius": 12000.0}}},
                timeout=10,
            )
            response.raise_for_status()
            results = []
            for place in response.json().get("places", [])[:10]:
                location = place.get("location", {})
                hours = place.get("regularOpeningHours", {})
                photo = (place.get("photos") or [{}])[0]
                photo_name = photo.get("name")
                results.append({
                    "provider": "Google Places",
                    "is_live": True,
                    "place_id": place.get("id"),
                    "name": place.get("displayName", {}).get("text"),
                    "category": kind,
                    "address": place.get("formattedAddress"),
                    "latitude": location.get("latitude", latitude),
                    "longitude": location.get("longitude", longitude),
                    "rating": place.get("rating"),
                    "review_count": place.get("userRatingCount"),
                    "opening_hours": hours.get("weekdayDescriptions", []),
                    "maps_url": place.get("googleMapsUri"),
                    "photo_resource": photo_name,
                })
            return results or None
        except Exception:
            return None


commercial_provider_service = CommercialProviderService()
