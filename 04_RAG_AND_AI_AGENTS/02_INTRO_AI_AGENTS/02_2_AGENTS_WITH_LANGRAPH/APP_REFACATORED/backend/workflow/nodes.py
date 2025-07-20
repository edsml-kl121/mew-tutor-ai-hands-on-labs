# backend/workflow/nodes.py
"""Node functions for the order workflow graph."""

from typing import Dict, Any

from workflow.state import OrderState
from services.llm_service import llm_service
from services.product_service import product_service

# Try to import interrupt - handle if not available
try:
    from langgraph.types import Command, interrupt
    INTERRUPT_AVAILABLE = True
except ImportError:
    try:
        from langgraph import interrupt, Command
        INTERRUPT_AVAILABLE = True
    except ImportError:
        INTERRUPT_AVAILABLE = False


def route_query(state: OrderState) -> OrderState:
    """Route user query to appropriate handler."""
    route = llm_service.route_query(state["user_query"])
    state["route"] = route
    state["current_step"] = "routed"
    return state


def handle_greeting(state: OrderState) -> OrderState:
    """Handle greeting and irrelevant topics."""
    response = llm_service.handle_greeting(state["user_query"])
    state["messages"].append(response)
    state["current_step"] = "complete"
    return state


def extract_products(state: OrderState) -> OrderState:
    """Extract and break down products from user query."""
    products = llm_service.extract_products(state["user_query"])
    state["products_to_search"] = products
    state["current_step"] = "products_extracted"
    return state


def search_products(state: OrderState) -> OrderState:
    """Search for each product separately."""
    products = state["products_to_search"]
    
    if not products:
        state["messages"].append("I couldn't find any products in your query. Could you specify what you'd like to order?")
        state["current_step"] = "no_products"
        return state
    
    search_results = product_service.search_products(products)
    state["search_results"] = search_results
    
    message = product_service.format_search_results(search_results)
    state["messages"].append(message)
    
    available_products = product_service.get_available_products(search_results)
    if available_products:
        state["current_step"] = "need_confirmation"
    else:
        state["current_step"] = "no_products_available"
    
    return state


def ask_order_confirmation(state: OrderState) -> OrderState:
    """Ask user for order confirmation - uses interrupt if available."""
    available_products = product_service.get_available_products(state["search_results"])
    
    if not available_products:
        state["current_step"] = "no_products_available"
        return state
    
    if INTERRUPT_AVAILABLE:
        try:
            user_response = interrupt("Would you like to order any of these products?")
            state = process_user_response(state, user_response)
            return state
        except Exception:
            state["waiting_for_input"] = True
            state["input_type"] = "confirmation"
            return state
    else:
        state["waiting_for_input"] = True
        state["input_type"] = "confirmation"
        return state


def ask_quantity(state: OrderState) -> OrderState:
    """Ask for quantity - uses interrupt if available."""
    if not state.get("wants_to_order", False):
        return state
    
    if state.get("quantity", 0) > 0:
        return state
    
    if INTERRUPT_AVAILABLE:
        try:
            user_response = interrupt("Perfect! How many would you like?")
            
            try:
                quantity = int(user_response.strip())
                if quantity > 0:
                    state["quantity"] = quantity
                    state["current_step"] = "quantity_received"
                else:
                    state["messages"].append("Please enter a valid positive number.")
                    state["current_step"] = "need_quantity"
            except ValueError:
                state["messages"].append("Please enter a valid number for the quantity.")
                state["current_step"] = "need_quantity"
                
            return state
        except Exception:
            state["waiting_for_input"] = True
            state["input_type"] = "quantity"
            state["current_step"] = "need_quantity"
            return state
    else:
        state["waiting_for_input"] = True
        state["input_type"] = "quantity"
        state["current_step"] = "need_quantity"
        return state


def process_user_response(state: OrderState, user_response: str) -> OrderState:
    """Process user response for order confirmation."""
    wants_to_order = llm_service.detect_order_intent(user_response)
    state["wants_to_order"] = wants_to_order
    
    if wants_to_order:
        quantity = llm_service.extract_quantity(user_response)
        if quantity > 0:
            state["quantity"] = quantity
            state["current_step"] = "quantity_extracted"
        else:
            state["current_step"] = "need_quantity"
    else:
        state["current_step"] = "order_declined"
    
    return state


def process_order_confirmation(state: OrderState) -> OrderState:
    """Process order confirmation response - for manual flow."""
    user_response = state.get("user_response", "")
    return process_user_response(state, user_response)


def finalize_order(state: OrderState) -> OrderState:
    """Finalize order with quantity."""
    available_products = product_service.get_available_products(state["search_results"])
    
    if not available_products:
        state["messages"].append("Sorry, no products are available for ordering.")
        state["current_step"] = "order_error"
        return state
    
    # Get first available product
    product_name = list(available_products.keys())[0]
    product_details = available_products[product_name]
    quantity = state.get("quantity", 0)
    
    if quantity > 0:
        message = product_service.format_order_confirmation(product_details, quantity)
        state["messages"].append(message)
        state["current_step"] = "order_complete"
    else:
        state["messages"].append("Sorry, invalid quantity specified.")
        state["current_step"] = "order_error"
    
    return state


def end_conversation(state: OrderState) -> OrderState:
    """End conversation."""
    if state["current_step"] == "order_declined":
        state["messages"].append("No problem! Feel free to ask if you need anything else.")
    elif state["current_step"] == "need_quantity":
        state["messages"].append("Perfect! How many would you like?")
    
    state["waiting_for_input"] = False
    return state