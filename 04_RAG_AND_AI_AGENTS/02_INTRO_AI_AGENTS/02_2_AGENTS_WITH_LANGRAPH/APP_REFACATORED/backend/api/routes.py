# backend/api/routes.py
"""API routes for the order system."""

import uuid
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from core.models import (
    InitialQueryRequest, ContinueConversationRequest, 
    ConversationResponse, HealthResponse
)
from workflow.state import create_initial_state, OrderState
from workflow.graph import workflow
from workflow.nodes import INTERRUPT_AVAILABLE, process_order_confirmation

router = APIRouter()


def handle_interrupt_mode(initial_state: OrderState, thread_id: str) -> ConversationResponse:
    """Handle conversation in interrupt mode."""
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        result = workflow.invoke(initial_state, config=config)
        state_snapshot = workflow.get_state(config)
        
        if state_snapshot.next:  # Graph is interrupted/waiting
            message = result["messages"][-1] if result["messages"] else "Please respond:"
            return ConversationResponse(
                message=message,
                thread_id=thread_id,
                is_complete=False,
                waiting_for_input=True,
                current_state=result
            )
        else:
            message = result["messages"][-1] if result["messages"] else "Hello! How can I help you?"
            return ConversationResponse(
                message=message,
                thread_id=thread_id,
                is_complete=True,
                waiting_for_input=False
            )
    except Exception as e:
        if "interrupt" in str(e).lower():
            try:
                state_snapshot = workflow.get_state(config)
                current_values = state_snapshot.values
                message = current_values["messages"][-1] if current_values["messages"] else "Please respond:"
                
                return ConversationResponse(
                    message=message,
                    thread_id=thread_id,
                    is_complete=False,
                    waiting_for_input=True,
                    current_state=current_values
                )
            except Exception:
                raise e
        else:
            raise e


def handle_manual_mode(initial_state: OrderState, thread_id: str) -> ConversationResponse:
    """Handle conversation in manual mode."""
    final_state = None
    for step in workflow.stream(initial_state):
        for node_name, node_state in step.items():
            final_state = node_state
    
    if final_state and final_state.get("waiting_for_input", False):
        return ConversationResponse(
            message=final_state["messages"][-1],
            thread_id=thread_id,
            is_complete=False,
            waiting_for_input=True,
            current_state=dict(final_state)
        )
    else:
        message = final_state["messages"][-1] if final_state and final_state["messages"] else "Hello! How can I help you?"
        return ConversationResponse(
            message=message,
            thread_id=thread_id,
            is_complete=True,
            waiting_for_input=False
        )


def handle_manual_continue(request: ContinueConversationRequest) -> ConversationResponse:
    """Handle continuing conversation in manual mode."""
    if not request.current_state:
        return ConversationResponse(
            message="Session expired. Please start a new conversation.",
            thread_id=request.thread_id,
            is_complete=True,
            waiting_for_input=False
        )
    
    # Reconstruct state from request
    state = OrderState(
        user_query=request.current_state.get("user_query", ""),
        route=request.current_state.get("route", ""),
        products_to_search=request.current_state.get("products_to_search", []),
        search_results=request.current_state.get("search_results", {}),
        wants_to_order=request.current_state.get("wants_to_order", False),
        quantity=request.current_state.get("quantity", 0),
        messages=request.current_state.get("messages", []),
        current_step=request.current_state.get("current_step", ""),
        waiting_for_input=False,
        input_type="",
        user_response=request.user_response
    )
    
    # Handle based on current step
    if state["current_step"] == "need_confirmation":
        state = process_order_confirmation(state)
        
        if state["current_step"] == "quantity_extracted":
            from workflow.nodes import finalize_order
            state = finalize_order(state)
            return ConversationResponse(
                message=state["messages"][-1],
                thread_id=request.thread_id,
                is_complete=True,
                waiting_for_input=False
            )
        elif state["current_step"] == "need_quantity":
            return ConversationResponse(
                message="Perfect! How many would you like?",
                thread_id=request.thread_id,
                is_complete=False,
                waiting_for_input=True,
                current_state=dict(state)
            )
        else:
            return ConversationResponse(
                message="No problem! Feel free to ask if you need anything else.",
                thread_id=request.thread_id,
                is_complete=True,
                waiting_for_input=False
            )
    
    elif state["current_step"] == "need_quantity":
        try:
            quantity = int(request.user_response.strip())
            state["quantity"] = quantity
            from workflow.nodes import finalize_order
            state = finalize_order(state)
            return ConversationResponse(
                message=state["messages"][-1],
                thread_id=request.thread_id,
                is_complete=True,
                waiting_for_input=False
            )
        except ValueError:
            return ConversationResponse(
                message="Please enter a valid number for the quantity.",
                thread_id=request.thread_id,
                is_complete=False,
                waiting_for_input=True,
                current_state=dict(state)
            )
    
    else:
        return ConversationResponse(
            message="I'm not sure how to help with that. Could you start a new conversation?",
            thread_id=request.thread_id,
            is_complete=True,
            waiting_for_input=False
        )


@router.post("/start-conversation", response_model=ConversationResponse)
async def start_conversation(request: InitialQueryRequest):
    """Start a new conversation with user query."""
    try:
        thread_id = str(uuid.uuid4())
        initial_state = create_initial_state(request.user_query)
        
        if INTERRUPT_AVAILABLE:
            try:
                return handle_interrupt_mode(initial_state, thread_id)
            except Exception:
                # Fall back to manual mode
                pass
        
        return handle_manual_mode(initial_state, thread_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/continue-conversation", response_model=ConversationResponse)
async def continue_conversation(request: ContinueConversationRequest):
    """Continue conversation with user response."""
    try:
        if INTERRUPT_AVAILABLE and not request.current_state:
            config = {"configurable": {"thread_id": request.thread_id}}
            
            try:
                from langgraph.types import Command
                result = workflow.invoke(Command(resume=request.user_response), config=config)
                state_snapshot = workflow.get_state(config)
                
                if state_snapshot.next:
                    message = result["messages"][-1] if result["messages"] else "Please respond:"
                    return ConversationResponse(
                        message=message,
                        thread_id=request.thread_id,
                        is_complete=False,
                        waiting_for_input=True,
                        current_state=result
                    )
                else:
                    message = result["messages"][-1] if result["messages"] else "Thank you!"
                    return ConversationResponse(
                        message=message,
                        thread_id=request.thread_id,
                        is_complete=True,
                        waiting_for_input=False
                    )
            except Exception:
                # Fall back to manual mode
                pass
        
        return handle_manual_continue(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error continuing conversation: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy")