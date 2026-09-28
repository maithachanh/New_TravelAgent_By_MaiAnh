from typing import List, Dict, Any, Optional
from app.services.optimizer import optimize_daily_route, calculate_trip_total_cost

class DynamicReplanService:
    def __init__(self):
        self._trip_history: Dict[int, List[Dict[str, Any]]] = {}

    def apply_modification(
        self,
        trip_id: int,
        current_itinerary: List[Dict[str, Any]],
        modified_item_id: Optional[int] = None,
        new_start_time: Optional[str] = None,
        replacement_title: Optional[str] = None,
        notes: Optional[str] = None,
        current_version: int = 1
    ) -> Dict[str, Any]:
        """
        Dependency Analyzer & Re-planning Engine:
        Analyzes dependencies: Item Modified -> Downstream Schedule Shift -> Budget Recalculation.
        Saves as Version N+1.
        """
        new_version = current_version + 1
        updated_itinerary = []
        changes_applied = []

        for day in current_itinerary:
            day_number = day.get("day_number", 1)
            date = day.get("date", "")
            items = [dict(it) for it in day.get("items", [])]

            item_found = False
            for idx, item in enumerate(items):
                # Match item id or title if id matches
                if (modified_item_id and item.get("id") == modified_item_id) or (modified_item_id == idx + 1 and not item_found):
                    item_found = True
                    old_title = item.get("title", "")

                    if replacement_title:
                        item["title"] = replacement_title
                        changes_applied.append(f"Thay đổi hoạt động: '{old_title}' thành '{replacement_title}'")
                    if new_start_time:
                        item["start_time"] = new_start_time
                        changes_applied.append(f"Dời giờ bắt đầu sang: {new_start_time}")
                    if notes:
                        item["notes"] = notes

            # Re-optimize schedule order & transit buffer for this day if changes occurred
            recalculated_items = optimize_daily_route(items)
            updated_itinerary.append({
                "day_number": day_number,
                "date": date,
                "items": recalculated_items
            })

        if not changes_applied:
            changes_applied.append("Tự động tinh chỉnh lại mốc thời gian và khoảng cách di chuyển giữa các điểm.")

        new_total_cost = calculate_trip_total_cost(updated_itinerary)

        # Store in version history
        if trip_id not in self._trip_history:
            self._trip_history[trip_id] = []
        self._trip_history[trip_id].append({
            "version": new_version,
            "itinerary": updated_itinerary,
            "total_cost": new_total_cost,
            "changes": changes_applied
        })

        return {
            "version": new_version,
            "trip_id": trip_id,
            "changes_summary": "; ".join(changes_applied),
            "total_cost": new_total_cost,
            "updated_itinerary": updated_itinerary
        }

    def get_trip_versions(self, trip_id: int) -> List[Dict[str, Any]]:
        return self._trip_history.get(trip_id, [])

replan_service = DynamicReplanService()
