import streamlit as st
import requests
import os

# Get backend URL from environment variable (for Kubernetes)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

# Streamlit app
st.title("Chat Interface with Gemini API")

# Input for user message
user_input = st.text_input("You: ", "")

# Send message to backend
if st.button("Send"):
    if user_input:
        response = requests.post(
            f"{BACKEND_URL}/chat",  # Backend service URL from environment
            json={"message": user_input}
        )
        if response.status_code == 200:
            st.markdown(f"Bot: {response.json()['reply']}")
        else:
            st.markdown(f"Error communicating with the backend. Status code: {response.status_code}")