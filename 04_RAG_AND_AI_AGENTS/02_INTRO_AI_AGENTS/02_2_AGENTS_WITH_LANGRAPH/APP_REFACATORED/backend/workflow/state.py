# backend/workflow/state.py
"""State definitions for the order workflow."""

from typing import TypedDict, List, Dict, Any, Optional


class OrderState(TypedDict):
    """State definition for the order workflow."""
    user_query: str
    route: str
    products_to_search: List[str]
    search_results: Dict[str, Any]
    wants_to_order: bool
    quantity: int
    messages: List[str]
    current_step: str
    waiting_for_input: bool
    input_type: str
    user_response: Optional[str]


def create_initial_state(user_query: str) -> OrderState:
    """Create initial state for a new conversation."""
    return OrderState(
        user_query=user_query,
        route="",
        products_to_search=[],
        search_results={},
        wants_to_order=False,
        quantity=0,
        messages=[],
        current_step="starting",
        waiting_for_input=False,
        input_type="",
        user_response=None
    )