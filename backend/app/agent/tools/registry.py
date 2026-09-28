import os
from app.agent.tools.base import (
    BaseFlightTool,
    BaseHotelTool,
    BaseRestaurantTool,
    BaseActivityTool
)
from app.agent.tools.universal_provider import (
    UniversalFlightProvider,
    UniversalHotelProvider,
    UniversalRestaurantProvider,
    UniversalActivityProvider
)

class ToolRegistry:
    def __init__(self, mode: str = "UNIVERSAL"):
        self.mode = mode.upper()
        self._init_providers()

    def _init_providers(self):
        # Universal Provider supports all countries, cities, and villages worldwide in real time
        self.flight_tool: BaseFlightTool = UniversalFlightProvider()
        self.hotel_tool: BaseHotelTool = UniversalHotelProvider()
        self.restaurant_tool: BaseRestaurantTool = UniversalRestaurantProvider()
        self.activity_tool: BaseActivityTool = UniversalActivityProvider()

    def set_mode(self, mode: str):
        self.mode = mode.upper()
        self._init_providers()

tool_registry = ToolRegistry(mode=os.getenv("TRAVEL_TOOL_MODE", "UNIVERSAL"))
