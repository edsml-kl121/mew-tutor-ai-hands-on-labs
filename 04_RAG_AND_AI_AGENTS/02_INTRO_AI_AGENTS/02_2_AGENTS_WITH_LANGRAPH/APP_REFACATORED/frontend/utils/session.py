# frontend/utils/session.py
"""Session state management utilities."""

import streamlit as st
from typing import Dict, Any


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = "waiting_for_query"
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "current_state" not in st.session_state:
        st.session_state.current_state = {}


def add_message(role: str, content: str):
    """Add message to chat history."""
    st.session_state.messages.append({"role": role, "content": content})


def reset_conversation():
    """Reset conversation state."""
    st.session_state.conversation_state = "waiting_for_query"
    st.session_state.thread_id = None
    st.session_state.current_state = {}


def update_conversation_state(
    thread_id: str = None,
    conversation_state: str = None,
    current_state: Dict[str, Any] = None
):
    """Update conversation state variables."""
    if thread_id is not None:
        st.session_state.thread_id = thread_id
    if conversation_state is not None:
        st.session_state.conversation_state = conversation_state
    if current_state is not None:
        st.session_state.current_state = current_state


def clear_chat():
    """Clear all chat messages and reset conversation."""
    st.session_state.messages = []
    reset_conversation()