import streamlit as st
import requests

# Page setup
st.title("Customer Service Agent")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial welcome message
    st.session_state.messages.append({"role": "assistant", "content": "Hello! How can I help you today?"})

# Session ID input (hidden in sidebar to keep main interface clean)
session_id = st.sidebar.text_input("Session ID", value="default_session")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")
if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get bot response
    try:
        response = requests.post(
            "http://localhost:8001/chat",
            json={"input": user_input, "session_id": session_id},
            timeout=10
        )
        bot_response = response.json().get("response", "No response received.")
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
    
    # Refresh the app to show new messages
    st.rerun()