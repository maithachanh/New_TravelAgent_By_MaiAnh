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
    # 1. Preference Score (0.0 to 1.0)
    category = item.get("item_type", "").lower()
    item_title = item.get("title", "").lower()
    pref_match = any(p.lower() in category or p.lower() in item_title for p in user_preferences)
    pref_score = 1.0 if pref_match else 0.4

    # 2. Distance Score (decaying with km)
    dist = haversine_distance(current_lat, current_lon, item.get("latitude", current_lat), item.get("longitude", current_lon))
    dist_score = max(0.0, 1.0 - (dist / 20.0))  # Max 20km range

    # 3. Budget Score
    cost = item.get("estimated_cost", 0.0)
    budget_score = 1.0 if cost <= budget_remaining else max(0.1, 1.0 - ((cost - budget_remaining) / max(budget_remaining, 1.0)))

    # 4. Time Score
    duration = item.get("duration_minutes", 60)
    time_score = 1.0 if duration <= available_minutes else 0.3

    # 5. Rating Score
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
    Applies Distance Matrix, Nearest-Neighbor TSP heuristic, and Time Window Scheduling
    to construct the optimal daily sequence.
    """
    if not items:
        return []

    prefs = user_preferences or ["culture", "food", "nature"]

    fixed_morning = []
    flexible_items = []

    for item in items:
        if item.get("item_type") in ["FLIGHT", "HOTEL_CHECKIN", "HOTEL_CHECKOUT"]:
            fixed_morning.append(item)
        else:
            flexible_items.append(item)

    # Initial anchor coordinates (from first item or default center)
    cur_lat = items[0].get("latitude") or 16.0
    cur_lon = items[0].get("longitude") or 108.0

    ordered_flex = []
    unvisited = flexible_items.copy()
    remaining_budget = daily_budget

    while unvisited:
        # Score each candidate item
        best_item = max(
            unvisited,
            key=lambda x: compute_multi_factor_score(x, prefs, cur_lat, cur_lon, remaining_budget, 180)
        )
        ordered_flex.append(best_item)
        cur_lat = best_item.get("latitude") or cur_lat
        cur_lon = best_item.get("longitude") or cur_lon
        remaining_budget -= best_item.get("estimated_cost", 0.0)
        unvisited.remove(best_item)

    # Reconstruct timeline starting at 08:30
    timeline: List[Dict[str, Any]] = []
    
    # Add morning fixed item if present
    for f in fixed_morning:
        timeline.append(f)

    start_h = 10 if fixed_morning else 8
    start_m = 30 if fixed_morning else 30

    for idx, item in enumerate(ordered_flex):
        dur = item.get("duration_minutes", 90)
        end_total_m = start_m + dur
        end_h = start_h + end_total_m // 60
        end_m = end_total_m % 60

        item["start_time"] = f"{start_h:02d}:{start_m:02d}"
        item["end_time"] = f"{end_h:02d}:{end_m:02d}"
        timeline.append(item)

        # Buffer transit time (30 mins)
        next_start_m = end_m + 30
        start_h = end_h + next_start_m // 60
        start_m = next_start_m % 60

    return timeline

def calculate_trip_total_cost(days: List[Dict[str, Any]]) -> float:
    total = 0.0
    for day in days:
        for item in day.get("items", []):
            total += float(item.get("estimated_cost", 0.0))
    return total
