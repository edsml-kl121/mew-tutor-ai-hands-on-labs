# backend/workflow/graph.py
"""LangGraph workflow setup and routing logic."""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from workflow.state import OrderState
from workflow.nodes import (
    route_query, handle_greeting, extract_products, search_products,
    ask_order_confirmation, process_order_confirmation, ask_quantity,
    finalize_order, end_conversation, INTERRUPT_AVAILABLE
)


def should_handle_order(state: OrderState) -> str:
    """Route based on query type."""
    return "extract_products" if state["route"] == "order" else "handle_greeting"


def should_ask_confirmation(state: OrderState) -> str:
    """Route after product search."""
    if state["current_step"] == "need_confirmation":
        return "ask_order_confirmation"
    elif state["current_step"] in ["no_products", "no_products_available"]:
        return "end"
    else:
        return "end"


def continue_after_confirmation(state: OrderState) -> str:
    """Route after order confirmation."""
    if state["current_step"] == "quantity_extracted":
        return "finalize_order"
    elif state["current_step"] == "need_quantity":
        return "ask_quantity"
    elif state["current_step"] == "order_declined":
        return "end"
    else:
        return "end"


def continue_after_quantity(state: OrderState) -> str:
    """Route after quantity input."""
    if state.get("quantity", 0) > 0 and state.get("wants_to_order", False):
        return "finalize_order"
    else:
        return "end"


class OrderWorkflow:
    """Order workflow manager."""
    
    def __init__(self):
        """Initialize the workflow."""
        self.memory = MemorySaver()
        self.graph = self._create_graph()
    
    def _create_graph(self):
        """Create and configure the LangGraph workflow."""
        workflow = StateGraph(OrderState)
        
        # Add nodes
        workflow.add_node("route_query", route_query)
        workflow.add_node("handle_greeting", handle_greeting)
        workflow.add_node("extract_products", extract_products)
        workflow.add_node("search_products", search_products)
        workflow.add_node("ask_order_confirmation", ask_order_confirmation)
        workflow.add_node("process_order_confirmation", process_order_confirmation)
        workflow.add_node("ask_quantity", ask_quantity)
        workflow.add_node("finalize_order", finalize_order)
        workflow.add_node("end", end_conversation)
        
        # Set entry point
        workflow.set_entry_point("route_query")
        
        # Add edges
        workflow.add_conditional_edges("route_query", should_handle_order)
        workflow.add_edge("handle_greeting", "end")
        workflow.add_edge("extract_products", "search_products")
        workflow.add_conditional_edges("search_products", should_ask_confirmation)
        workflow.add_conditional_edges("ask_order_confirmation", continue_after_confirmation)
        workflow.add_edge("process_order_confirmation", "ask_quantity")
        workflow.add_conditional_edges("ask_quantity", continue_after_quantity)
        workflow.add_edge("finalize_order", "end")
        workflow.add_edge("end", END)
        
        if INTERRUPT_AVAILABLE:
            return workflow.compile(checkpointer=self.memory)
        else:
            return workflow.compile()
    
    def invoke(self, state: OrderState, config=None):
        """Invoke the workflow."""
        return self.graph.invoke(state, config=config)
    
    def stream(self, state: OrderState):
        """Stream the workflow execution."""
        return self.graph.stream(state)
    
    def get_state(self, config):
        """Get the current state of the workflow."""
        return self.graph.get_state(config)


# Global workflow instance
workflow = OrderWorkflow()