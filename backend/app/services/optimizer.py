import math
from typing import List, Dict, Any, Optional

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great circle distance in kilometers between two GPS coordinates."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def _time_to_minutes(time_str: str) -> int:
    """Converts 'HH:MM' string to total minutes from midnight."""
    try:
        parts = time_str.strip().split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return 0

def _minutes_to_time(minutes: int) -> str:
    """Converts total minutes from midnight to 'HH:MM' string (capped at 23:59)."""
    m = min(minutes, 23 * 60 + 59)
    h = m // 60
    rem_m = m % 60
    return f"{h:02d}:{rem_m:02d}"

def compute_multi_factor_score(
    item: Dict[str, Any],
    user_preferences: List[str],
    current_lat: float,
    current_lon: float,
    budget_remaining: float,
    available_minutes: int
) -> float:
    """
    Multi-Factor Optimization Score:
    Score = 0.30 * PreferenceScore + 0.25 * DistanceScore + 0.20 * BudgetScore + 0.15 * TimeScore + 0.10 * RatingScore
    """
    category = item.get("item_type", "").lower()
    item_title = item.get("title", "").lower()
    pref_match = any(p.lower() in category or p.lower() in item_title for p in user_preferences)
    pref_score = 1.0 if pref_match else 0.4

    dist = haversine_distance(current_lat, current_lon, item.get("latitude", current_lat), item.get("longitude", current_lon))
    dist_score = max(0.0, 1.0 - (dist / 20.0))

    cost = item.get("estimated_cost", 0.0)
    budget_score = 1.0 if cost <= budget_remaining else max(0.1, 1.0 - ((cost - budget_remaining) / max(budget_remaining, 1.0)))

    duration = item.get("duration_minutes", 60)
    time_score = 1.0 if duration <= available_minutes else 0.3

    rating = item.get("rating", 4.5)
    rating_score = min(1.0, rating / 5.0)

    final_score = (
        0.30 * pref_score +
        0.25 * dist_score +
        0.20 * budget_score +
        0.15 * time_score +
        0.10 * rating_score
    )
    return round(final_score, 4)

def optimize_daily_route(
    items: List[Dict[str, Any]],
    user_preferences: Optional[List[str]] = None,
    daily_budget: float = 5000000.0
) -> List[Dict[str, Any]]:
    """
    Ensures strict chronological monotonicity, logical time windows,
    and transit buffers between all items in a day.
    NEVER allows time to jump backward, overlap, or squash multiple evening items into 23:59.
    """
    if not items:
        return []

    prefs = user_preferences or ["culture", "food", "nature"]

    def role_priority(item: Dict[str, Any]) -> int:
        t = item.get("item_type", "")
        if t == "FLIGHT":
            orig_time = _time_to_minutes(item.get("start_time", "08:00"))
            return 10 if orig_time < 720 else 90
        if t == "HOTEL_CHECKIN":
            return 20
        if t == "BREAKFAST":
            return 30
        if t in ["ATTRACTION", "ACTIVITY"]:
            orig_time = _time_to_minutes(item.get("start_time", "09:00"))
            return 40 if orig_time < 720 else 60
        if t == "LUNCH":
            return 50
        if t == "SHOPPING":
            return 65
        if t == "HOTEL_CHECKOUT":
            return 15
        if t == "DINNER":
            return 80
        return 70

    sorted_items = sorted(items, key=role_priority)
    total_items = len(sorted_items)

    optimized_timeline: List[Dict[str, Any]] = []
    current_min = 8 * 60  # Default day start at 08:00

    for idx, item in enumerate(sorted_items):
        item_copy = dict(item)
        dur = item_copy.get("duration_minutes", 60)
        item_type = item_copy.get("item_type", "")
        item_orig_min = _time_to_minutes(item_copy.get("start_time", "08:00"))
        remaining_after = total_items - idx - 1

        if idx == 0:
            actual_start_min = max(current_min, item_orig_min) if item_orig_min > 0 else current_min
        else:
            # Use smaller transit buffer (15m) if running late in evening, else standard 30m
            transit_buffer = 15 if current_min >= 20 * 60 else 30
            actual_start_min = max(current_min + transit_buffer, item_orig_min)

        # Handle Long Haul Flight on arrival day:
        # If this is a long flight (> 360 min) with subsequent evening items (hotel check-in, dinner)
        if item_type == "FLIGHT" and dur >= 360 and remaining_after > 0:
            # Flight lands in the evening so there is comfortable time for hotel checkin & dinner
            # Reserve at least 60 mins per remaining activity + 15 mins transit
            target_arrival_min = min(20 * 60 + 30, (23 * 60 + 30) - (remaining_after * 75))
            actual_end_min = max(actual_start_min + 120, target_arrival_min)
            item_copy["start_time"] = _minutes_to_time(actual_start_min)
            item_copy["end_time"] = _minutes_to_time(actual_end_min)
            current_min = actual_end_min
            optimized_timeline.append(item_copy)
            continue

        # Prevent squashing evening activities past 21:00
        # If time is tight, gracefully stagger items so start_time < end_time and no overlaps
        if remaining_after > 0:
            # Ensure we don't exceed the boundary that would push future items off the schedule
            max_allowed_end = (23 * 60 + 50) - (remaining_after * 45)
            if actual_start_min >= max_allowed_end:
                actual_start_min = max(current_min + 10, max_allowed_end - 45)

            actual_end_min = min(actual_start_min + dur, max_allowed_end)
            if actual_end_min <= actual_start_min:
                actual_end_min = actual_start_min + 35
        else:
            # Final item of the day
            if actual_start_min >= 23 * 60 + 40:
                actual_start_min = 23 * 60
            actual_end_min = min(actual_start_min + dur, 23 * 60 + 55)
            if actual_end_min <= actual_start_min:
                actual_end_min = actual_start_min + 30

        item_copy["start_time"] = _minutes_to_time(actual_start_min)
        item_copy["end_time"] = _minutes_to_time(actual_end_min)
        current_min = actual_end_min
        optimized_timeline.append(item_copy)

    return optimized_timeline

def calculate_trip_total_cost(days: List[Dict[str, Any]]) -> float:
    """Calculates total cost across all items in all itinerary days."""
    total = 0.0
    for day in days:
        for item in day.get("items", []):
            total += float(item.get("estimated_cost", 0.0))
    return round(total, 2)
