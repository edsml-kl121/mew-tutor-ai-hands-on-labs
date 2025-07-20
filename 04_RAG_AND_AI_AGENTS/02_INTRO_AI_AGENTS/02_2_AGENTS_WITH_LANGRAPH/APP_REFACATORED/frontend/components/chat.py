# frontend/components/chat.py
"""Chat interface components."""

import streamlit as st

from services.api_client import api_client
from utils.session import (
    add_message, reset_conversation, update_conversation_state
)


def handle_api_response(response, user_input: str):
    """Handle API response and update session state."""
    if response.success:
        result = response.data
        add_message("assistant", result["message"])
        
        # Update session state
        update_conversation_state(
            thread_id=result["thread_id"],
            current_state=result.get("current_state")
        )
        
        # Determine conversation state
        if result.get("waiting_for_input", False):
            message_lower = result["message"].lower()
            if "would you like to order" in message_lower or "order any of these" in message_lower:
                update_conversation_state(conversation_state="need_confirmation")
            elif "how many" in message_lower or "quantity" in message_lower:
                update_conversation_state(conversation_state="need_quantity")
            else:
                update_conversation_state(conversation_state="waiting_for_input")
        else:
            # Check for special cases where backend didn't mark as waiting
            message_lower = result["message"].lower()
            if "available:" in message_lower and "would you like to order" in message_lower:
                # Manually create state for fallback mode
                search_results = {}
                if "apple" in message_lower and "$1.5" in result["message"]:
                    search_results["apple"] = {"name": "Apple", "price": 1.5, "in_stock": True}
                
                fallback_state = {
                    "user_query": user_input,
                    "route": "order",
                    "products_to_search": list(search_results.keys()),
                    "search_results": search_results,
                    "messages": [result["message"]],
                    "current_step": "need_confirmation",
                    "quantity": 0,
                    "wants_to_order": False
                }
                
                update_conversation_state(
                    conversation_state="need_confirmation",
                    current_state=fallback_state
                )
            else:
                update_conversation_state(conversation_state="complete")
    else:
        add_message("assistant", response.error)
        update_conversation_state(conversation_state="complete")


def start_new_conversation(user_query: str):
    """Start a new conversation with the backend."""
    response = api_client.start_conversation(user_query)
    handle_api_response(response, user_query)


def continue_conversation(user_response: str):
    """Continue existing conversation with the backend."""
    response = api_client.continue_conversation(
        user_response=user_response,
        thread_id=st.session_state.thread_id,
        current_state=st.session_state.current_state
    )
    handle_api_response(response, user_response)


def render_chat_messages():
    """Render chat message history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


def render_confirmation_input():
    """Render order confirmation input interface."""
    st.markdown("---")
    st.markdown("**🤔 Would you like to place an order?**")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        user_response = st.text_input(
            "Your response:", 
            placeholder="Type your response or use buttons...", 
            key="confirmation_input"
        )
    
    with col2:
        if st.button("✅ Yes", use_container_width=True, key="yes_btn"):
            add_message("user", "Yes, I want to order")
            continue_conversation("Yes, I want to order")
            st.rerun()
    
    with col3:
        if st.button("❌ No", use_container_width=True, key="no_btn"):
            add_message("user", "No, thank you")
            continue_conversation("No, thank you")
            st.rerun()
    
    if user_response and st.button("Send Response", key="send_confirmation"):
        add_message("user", user_response)
        continue_conversation(user_response)
        st.rerun()


def render_quantity_input():
    """Render quantity input interface."""
    st.markdown("---")
    st.markdown("**🔢 How many would you like?**")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        quantity = st.number_input("Quantity:", min_value=1, value=1, key="quantity_input")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Confirm Order", use_container_width=True, key="confirm_order"):
            add_message("user", str(quantity))
            continue_conversation(str(quantity))
            st.rerun()


def render_general_input():
    """Render general response input interface."""
    st.markdown("---")
    st.markdown("**💬 Please respond:**")
    
    user_response = st.text_input(
        "Your response:", 
        placeholder="Type your response...", 
        key="general_input"
    )
    
    if user_response and st.button("Send", key="send_general"):
        add_message("user", user_response)
        continue_conversation(user_response)
        st.rerun()


def render_chat_input():
    """Render main chat input for new conversations."""
    if prompt := st.chat_input("Ask about products or place an order..."):
        add_message("user", prompt)
        reset_conversation()
        start_new_conversation(prompt)
        st.rerun()


def render_debug_info():
    """Render debug information."""
    with st.expander("Debug Info", expanded=False):
        st.write(f"Conversation State: {st.session_state.conversation_state}")
        st.write(f"Thread ID: {st.session_state.thread_id}")
        st.write(f"Has Current State: {bool(st.session_state.current_state)}")
        if st.session_state.current_state:
            st.write(f"Current State Keys: {list(st.session_state.current_state.keys())}")


def render_chat_interface():
    """Render the complete chat interface."""
    # Display chat history
    render_chat_messages()
    
    # Debug info
    render_debug_info()
    
    # Handle input based on conversation state
    if st.session_state.conversation_state == "need_confirmation":
        render_confirmation_input()
    elif st.session_state.conversation_state == "need_quantity":
        render_quantity_input()
    elif st.session_state.conversation_state == "waiting_for_input":
        render_general_input()
    elif st.session_state.conversation_state in ["waiting_for_query", "complete"]:
        render_chat_input()