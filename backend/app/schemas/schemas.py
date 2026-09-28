from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.models import TripStatus, ItemType, BookingStatus

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    language: Optional[str] = "vi"
    currency: Optional[str] = "VND"
    timezone: Optional[str] = "Asia/Ho_Chi_Minh"
    travel_styles: Optional[List[str]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    avatar_url: Optional[str]
    language: str
    currency: str
    timezone: str
    travel_styles: List[str]

    class Config:
        from_attributes = True

# Travel Style Update
class UserPreferencesUpdate(BaseModel):
    language: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    travel_styles: Optional[List[str]] = None

# Destination Schemas
class DestinationCreate(BaseModel):
    country: str
    city: str
    name: str
    category: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    opening_hours: Optional[str] = None
    reference_price: Optional[float] = 0.0
    rating: Optional[float] = 4.5
    description: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = []

class DestinationOut(DestinationCreate):
    id: int

    class Config:
        from_attributes = True

# Itinerary Item Schemas
class ItineraryItemBase(BaseModel):
    title: str
    item_type: ItemType
    start_time: str
    end_time: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    duration_minutes: Optional[int] = 60
    estimated_cost: Optional[float] = 0.0
    notes: Optional[str] = None

class ItineraryItemCreate(ItineraryItemBase):
    day_id: int
    trip_id: int

class ItineraryItemOut(ItineraryItemBase):
    id: int
    day_id: int
    trip_id: int
    booking_id: Optional[int] = None

    class Config:
        from_attributes = True

# Itinerary Day Schemas
class ItineraryDayOut(BaseModel):
    id: int
    day_number: int
    date: str
    notes: Optional[str]
    items: List[ItineraryItemOut] = []

    class Config:
        from_attributes = True

# Trip Schemas
class TripCreate(BaseModel):
    title: str
    origin: str
    destination: str
    start_date: str
    end_date: str
    travelers: int = 1
    budget: float = 0.0
    currency: str = "VND"
    preferences: List[str] = []

class TripOut(TripCreate):
    id: int
    user_id: int
    status: TripStatus
    created_at: datetime
    days: List[ItineraryDayOut] = []

    class Config:
        from_attributes = True

# Booking Schemas
class BookingCreate(BaseModel):
    trip_id: int
    service_name: str
    category: str
    price: float
    details: Optional[Dict[str, Any]] = {}

class BookingOut(BaseModel):
    id: int
    trip_id: int
    user_id: int
    service_name: str
    category: str
    booking_reference: str
    price: float
    status: BookingStatus
    booking_date: datetime

    class Config:
        from_attributes = True

# Agent Query Schemas
class AgentPlanRequest(BaseModel):
    prompt: str  # e.g., "Tôi muốn đi Đà Nẵng 3 ngày 2 đêm từ Hà Nội, ngân sách 10 triệu cho 2 người, thích ẩm thực và biển"
    trip_id: Optional[int] = None

class ReplanRequest(BaseModel):
    trip_id: int
    modified_item_id: int
    new_start_time: Optional[str] = None
    new_end_time: Optional[str] = None
    replacement_title: Optional[str] = None
    notes: Optional[str] = None

class InTripSupportRequest(BaseModel):
    trip_id: int
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    user_query: str # e.g. "Gần đây có nhà hàng ngon nào mở cửa không?" or "Thời tiết xấu, gợi ý hoạt động trong nhà"
