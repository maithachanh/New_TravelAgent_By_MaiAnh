from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

class TravelAgentState(TypedDict, total=False):
    # Core User Inputs
    user_prompt: str
    user_id: Optional[int]
    trip_id: Optional[int]
    conversation_id: Optional[int]
    language: str

    # 1. User Request Analyzer Output
    analyzer_output: Dict[str, Any]
    intent: Optional[str]

    # 2. Requirement Extractor Output
    extracted_requirements: Dict[str, Any]

    # 3. Destination Analyzer Output
    destination_analysis: Dict[str, Any]
    destination_context: Dict[str, Any]

    # 4. Budget Analyzer Output
    budget_analysis: Dict[str, Any]

    # 5. Search Planner Output
    search_plan: Dict[str, Any]

    # 6 & 7. Tool Results
    flight_results: List[Dict[str, Any]]
    hotel_results: List[Dict[str, Any]]

    # 8. Activity Search Results
    activity_results: List[Dict[str, Any]]

    # 9. Restaurant Search Results
    restaurant_results: List[Dict[str, Any]]

    # RAG Knowledge Retrieved
    rag_knowledge: Dict[str, List[Dict[str, Any]]]

    # 10. Itinerary Generator Output
    raw_itinerary: List[Dict[str, Any]]

    # 11. Distance Optimizer Output
    distance_optimized_itinerary: List[Dict[str, Any]]
    optimized_daily_routes: List[Dict[str, Any]]

    # 12. Budget Validator Output
    budget_validation: Dict[str, Any]

    # 13. Schedule Validator Output
    schedule_validation: Dict[str, Any]

    # 14. Final Itinerary Output
    final_itinerary: List[Dict[str, Any]]

    # Final Agent Natural Language Output Response
    agent_response: str
    suggestions: List[str]
    error: Optional[str]

def initial_state(
    user_prompt: str,
    user_id: Optional[int] = None,
    trip_id: Optional[int] = None,
    conversation_id: Optional[int] = None,
    language: str = "vi",
) -> TravelAgentState:
    return {
        "user_prompt": user_prompt,
        "user_id": user_id,
        "trip_id": trip_id,
        "conversation_id": conversation_id,
        "language": language,
        "analyzer_output": {},
        "intent": "PLAN_NEW_TRIP",
        "extracted_requirements": {},
        "destination_analysis": {},
        "destination_context": {},
        "budget_analysis": {},
        "search_plan": {},
        "flight_results": [],
        "hotel_results": [],
        "activity_results": [],
        "restaurant_results": [],
        "rag_knowledge": {},
        "raw_itinerary": [],
        "distance_optimized_itinerary": [],
        "optimized_daily_routes": [],
        "budget_validation": {},
        "schedule_validation": {},
        "final_itinerary": [],
        "agent_response": "",
        "suggestions": [],
        "error": None
    }
