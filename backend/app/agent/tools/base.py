from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseFlightTool(ABC):
    @abstractmethod
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: Optional[str] = None,
        travelers: int = 1
    ) -> List[Dict[str, Any]]:
        """Search available flights with prices, times, and airlines"""
        pass

class BaseHotelTool(ABC):
    @abstractmethod
    def search_hotels(
        self,
        city: str,
        check_in: Optional[str] = None,
        check_out: Optional[str] = None,
        budget_tier: Optional[str] = "MEDIUM",
        preferences: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search available hotels with price_per_night, star rating, coordinates, and district"""
        pass

class BaseRestaurantTool(ABC):
    @abstractmethod
    def search_restaurants(
        self,
        city: str,
        cuisine_types: Optional[List[str]] = None,
        price_range: Optional[str] = "MEDIUM"
    ) -> List[Dict[str, Any]]:
        """Search top-rated local restaurants with specialties and coordinates"""
        pass

class BaseActivityTool(ABC):
    @abstractmethod
    def search_activities(
        self,
        city: str,
        categories: Optional[List[str]] = None,
        duration_days: int = 3
    ) -> List[Dict[str, Any]]:
        """Search sightseeing attractions and cultural activities with entry fees and duration"""
        pass
