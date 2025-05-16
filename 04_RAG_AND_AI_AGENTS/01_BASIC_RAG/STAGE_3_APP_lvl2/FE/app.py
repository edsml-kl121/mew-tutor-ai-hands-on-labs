import streamlit as st
import requests

# Streamlit app
st.title("Chat Interface with Gemini API")

# Input for user message
user_input = st.text_input("You: ", "")

# Send message to backend
if st.button("Send"):
    if user_input:
        response = requests.post(
            "http://localhost:8000/chat",  # Backend service URL
            json={"message": user_input}
        )
        if response.status_code == 200:
            st.markdown(f"Bot: {response.json()['reply']}")
        else:
            st.markdown("Error communicating with the backend.")