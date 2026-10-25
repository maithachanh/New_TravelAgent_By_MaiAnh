import enum
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class TripStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    CONFIRMED = "CONFIRMED"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ItemType(str, enum.Enum):
    FLIGHT = "FLIGHT"
    HOTEL_CHECKIN = "HOTEL_CHECKIN"
    HOTEL_CHECKOUT = "HOTEL_CHECKOUT"
    RESTAURANT = "RESTAURANT"
    ATTRACTION = "ATTRACTION"
    MUSEUM = "MUSEUM"
    SHOPPING = "SHOPPING"
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    TRANSPORT = "TRANSPORT"
    ACTIVITY = "ACTIVITY"

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    language = Column(String(10), default="vi")
    currency = Column(String(10), default="VND")
    timezone = Column(String(50), default="Asia/Ho_Chi_Minh")
    
    # Store user travel styles: ["Adventure", "Cultural", "Food"]
    travel_styles = Column(JSON, default=list)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100), index=True, nullable=False)
    city = Column(String(100), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(50), index=True) # attraction, hotel, restaurant, activity, transport
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500), nullable=True)
    opening_hours = Column(String(255), nullable=True)
    reference_price = Column(Float, default=0.0) # in VND/USD
    rating = Column(Float, default=4.5)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    tags = Column(JSON, default=list) # e.g., ["Food", "Cultural", "Nightlife"]

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    start_date = Column(String(20), nullable=False) # YYYY-MM-DD
    end_date = Column(String(20), nullable=False)   # YYYY-MM-DD
    travelers = Column(Integer, default=1)
    budget = Column(Float, default=0.0)
    currency = Column(String(10), default="VND")
    preferences = Column(JSON, default=list) # Selected travel styles for this trip
    status = Column(Enum(TripStatus), default=TripStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trips")
    days = relationship("ItineraryDay", back_populates="trip", cascade="all, delete-orphan", order_by="ItineraryDay.day_number")
    bookings = relationship("Booking", back_populates="trip", cascade="all, delete-orphan")
    versions = relationship("TripVersion", back_populates="trip", cascade="all, delete-orphan", order_by="TripVersion.version")

class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    date = Column(String(20), nullable=False) # YYYY-MM-DD
    notes = Column(Text, nullable=True)

    trip = relationship("Trip", back_populates="days")
    items = relationship("ItineraryItem", back_populates="day", cascade="all, delete-orphan", order_by="ItineraryItem.start_time")

class ItineraryItem(Base):
    __tablename__ = "itinerary_items"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("itinerary_days.id"), nullable=False, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    item_type = Column(Enum(ItemType), default=ItemType.ATTRACTION)
    start_time = Column(String(10), nullable=False) # HH:MM
    end_time = Column(String(10), nullable=False)   # HH:MM
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    duration_minutes = Column(Integer, default=60)
    estimated_cost = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", use_alter=True), nullable=True)

    day = relationship("ItineraryDay", back_populates="items")
    booking = relationship("Booking", foreign_keys=[booking_id], uselist=False)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False) # flight, hotel, restaurant, activity
    booking_reference = Column(String(100), unique=True, nullable=False, index=True)
    price = Column(Float, default=0.0)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, index=True)
    booking_date = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, default=dict)

    trip = relationship("Trip", back_populates="bookings")
    user = relationship("User", back_populates="bookings")

class TripVersion(Base):
    __tablename__ = "trip_versions"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False, index=True)
    itinerary_data = Column(JSON, nullable=False)
    total_cost = Column(Float, default=0.0)
    changes_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", back_populates="versions")

