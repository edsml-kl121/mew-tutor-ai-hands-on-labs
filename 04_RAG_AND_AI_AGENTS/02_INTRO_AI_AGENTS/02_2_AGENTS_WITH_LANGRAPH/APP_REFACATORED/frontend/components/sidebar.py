# frontend/components/sidebar.py
"""Sidebar components."""

import streamlit as st

from services.api_client import check_backend_connection
from utils.session import add_message, reset_conversation, clear_chat
from components.chat import start_new_conversation


def render_example_queries():
    """Render example query buttons."""
    st.header("💡 Example Queries")
    
    examples = [
        "I want apples",
        "Do you have bananas?",
        "Can I order milk and bread?",
        "Hello, how are you?",
        "เอาแอปเปิ้ล 3 ชิ้น"
    ]
    
    for i, example in enumerate(examples):
        if st.button(example, key=f"example_{i}"):
            add_message("user", example)
            reset_conversation()
            start_new_conversation(example)
            st.rerun()


def render_features():
    """Render features list."""
    st.markdown("---")
    st.markdown("**Features:**")
    st.markdown("- LangGraph workflow with interrupts")
    st.markdown("- Thread-based conversations")
    st.markdown("- Hybrid interrupt/manual mode")
    st.markdown("- Multi-language support")
    st.markdown("- Smart conversation flow")


def render_controls():
    """Render control buttons."""
    if st.button("Clear Chat", key="clear_chat"):
        clear_chat()
        st.rerun()


def render_connection_status():
    """Render backend connection status."""
    if check_backend_connection():
        st.success("🟢 Backend Connected")
    else:
        st.error("🔴 Backend Offline")


def render_sidebar():
    """Render the complete sidebar."""
    with st.sidebar:
        render_example_queries()
        render_features()
        render_controls()
        render_connection_status()