from langgraph.graph import StateGraph, END
from app.agent.state import TravelAgentState
from app.agent.nodes import (
    user_request_analyzer_node,
    requirement_extractor_node,
    clarification_node,
    destination_analyzer_node,
    budget_analyzer_node,
    search_planner_node,
    flight_search_node,
    hotel_search_node,
    activity_search_node,
    restaurant_search_node,
    parallel_search_node,
    itinerary_generator_node,
    distance_optimizer_node,
    budget_validator_node,
    schedule_validator_node,
    critique_reviewer_node,
    final_itinerary_node
)

def build_upgraded_travel_agent_graph():
    workflow = StateGraph(TravelAgentState)

    # Add all nodes in the DAG
    workflow.add_node("user_request_analyzer", user_request_analyzer_node)
    workflow.add_node("requirement_extractor", requirement_extractor_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("destination_analyzer", destination_analyzer_node)
    workflow.add_node("budget_analyzer", budget_analyzer_node)
    workflow.add_node("search_planner", search_planner_node)
    workflow.add_node("parallel_search", parallel_search_node)
    workflow.add_node("flight_search", flight_search_node)
    workflow.add_node("hotel_search", hotel_search_node)
    workflow.add_node("activity_search", activity_search_node)
    workflow.add_node("restaurant_search", restaurant_search_node)
    workflow.add_node("itinerary_generator", itinerary_generator_node)
    workflow.add_node("distance_optimizer", distance_optimizer_node)
    workflow.add_node("budget_validator", budget_validator_node)
    workflow.add_node("schedule_validator", schedule_validator_node)
    workflow.add_node("critique_reviewer", critique_reviewer_node)
    workflow.add_node("final_itinerary", final_itinerary_node)

    # Set Entry Point
    workflow.set_entry_point("user_request_analyzer")

    # Clean deterministic DAG pipeline:
    # If destination is present, proceed to full planning with sensible defaults;
    # only divert to clarification if destination is genuinely missing.
    workflow.add_edge("user_request_analyzer", "requirement_extractor")
    workflow.add_conditional_edges(
        "requirement_extractor",
        lambda state: "clarification" if (
            state.get("extracted_requirements", {}).get("missing_fields") and
            not state.get("extracted_requirements", {}).get("destination")
        ) else "destination_analyzer",
        {
            "clarification": "clarification",
            "destination_analyzer": "destination_analyzer",
        },
    )
    workflow.add_edge("clarification", END)
    workflow.add_edge("destination_analyzer", "budget_analyzer")
    workflow.add_edge("budget_analyzer", "search_planner")
    
    # Concurrently search Flights, Hotels, Activities, and Restaurants
    workflow.add_edge("search_planner", "parallel_search")
    workflow.add_edge("parallel_search", "itinerary_generator")
    
    workflow.add_edge("itinerary_generator", "distance_optimizer")
    workflow.add_edge("distance_optimizer", "budget_validator")
    workflow.add_edge("budget_validator", "schedule_validator")
    
    # Critique & Reviewer Agent Node validates fatigue, seasonal risks & packing advice
    workflow.add_edge("schedule_validator", "critique_reviewer")
    workflow.add_edge("critique_reviewer", "final_itinerary")
    workflow.add_edge("final_itinerary", END)

    return workflow.compile()

travel_agent_app = build_upgraded_travel_agent_graph()
