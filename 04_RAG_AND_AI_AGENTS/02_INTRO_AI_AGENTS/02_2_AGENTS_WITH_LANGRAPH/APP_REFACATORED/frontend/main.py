# frontend/main.py
"""Streamlit application entry point."""

import streamlit as st

from components.chat import render_chat_interface
from components.sidebar import render_sidebar
from services.api_client import check_backend_connection
from utils.session import initialize_session_state

# Configure Streamlit
st.set_page_config(
    page_title="Order System",
    page_icon="🛒",
    layout="centered"
)


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    # Main UI
    st.title("🛒 Order System")
    st.markdown("Welcome! Ask about products or place an order.")
    
    # Render chat interface
    render_chat_interface()
    
    # Render sidebar
    render_sidebar()
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by LangGraph + LangChain + Gemini + FastAPI + Streamlit*")


if __name__ == "__main__":
    main()