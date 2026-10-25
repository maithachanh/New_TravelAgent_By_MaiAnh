import pytest
from app.services.replan_service import replan_service

def test_replan_version_increment_and_time_adjustment():
    initial_itinerary = [
        {
            "day_number": 1,
            "date": "2026-11-01",
            "items": [
                {
                    "id": 101,
                    "title": "Chuyến bay VN100",
                    "start_time": "08:00",
                    "end_time": "12:00",
                    "duration_minutes": 240,
                    "estimated_cost": 5000000,
                    "location": "Sân bay"
                },
                {
                    "id": 102,
                    "title": "Ăn trưa",
                    "start_time": "12:30",
                    "end_time": "13:30",
                    "duration_minutes": 60,
                    "estimated_cost": 300000,
                    "location": "Trung tâm"
                }
            ]
        }
    ]

    # Replan item 101 starting at 09:30 instead of 08:00
    res = replan_service.apply_modification(
        trip_id=999,
        current_itinerary=initial_itinerary,
        modified_item_id=101,
        new_start_time="09:30"
    )

    assert res["version"] >= 1
    updated_items = res["updated_itinerary"][0]["items"]
    # Check that item 101 now starts at 09:30
    assert updated_items[0]["start_time"] == "09:30"
    # End time should shift by 240 minutes -> 13:30
    assert updated_items[0]["end_time"] == "13:30"
    # Next item should shift accordingly after transit buffer
    assert updated_items[1]["start_time"] >= "13:30"
