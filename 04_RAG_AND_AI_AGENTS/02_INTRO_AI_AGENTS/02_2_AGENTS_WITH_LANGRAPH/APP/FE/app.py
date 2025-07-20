# frontend.py
import streamlit as st
import requests
import json

# Configure Streamlit
st.set_page_config(
    page_title="Order System",
    page_icon="🛒",
    layout="centered"
)

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = "waiting_for_query"
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "current_state" not in st.session_state:
    st.session_state.current_state = {}

def add_message(role: str, content: str):
    """Add message to chat history"""
    st.session_state.messages.append({"role": role, "content": content})

def reset_conversation():
    """Reset conversation state"""
    st.session_state.conversation_state = "waiting_for_query"
    st.session_state.thread_id = None
    st.session_state.current_state = {}

def start_new_conversation(user_query: str):
    """Start a new conversation"""
    try:
        response = requests.post(f"{BACKEND_URL}/start-conversation", 
                               json={"user_query": user_query})
        
        if response.status_code == 200:
            result = response.json()
            add_message("assistant", result["message"])
            
            # Store thread ID for subsequent requests
            st.session_state.thread_id = result["thread_id"]
            
            # Check if conversation is waiting for input
            if result.get("waiting_for_input", False):
                # Store current state if provided (for fallback mode)
                if result.get("current_state"):
                    st.session_state.current_state = result["current_state"]
                
                # Determine what kind of input we're waiting for based on the message content
                message_lower = result["message"].lower()
                if "would you like to order" in message_lower or "order any of these" in message_lower:
                    st.session_state.conversation_state = "need_confirmation"
                elif "how many" in message_lower or "quantity" in message_lower:
                    st.session_state.conversation_state = "need_quantity"
                else:
                    st.session_state.conversation_state = "waiting_for_input"
            else:
                # Check if this looks like it should be a confirmation request
                message_lower = result["message"].lower()
                if ("available:" in message_lower and "would you like to order" in message_lower):
                    # This should be a confirmation state but backend didn't mark it as waiting
                    st.session_state.conversation_state = "need_confirmation"
                    # Manually create state for fallback mode - extract search results from message
                    search_results = {}
                    # Try to extract product info from the message
                    if "apple" in message_lower and "$1.5" in result["message"]:
                        search_results["apple"] = {"name": "Apple", "price": 1.5, "in_stock": True}
                    
                    st.session_state.current_state = {
                        "user_query": user_query,
                        "route": "order", 
                        "products_to_search": list(search_results.keys()),
                        "search_results": search_results,
                        "messages": [result["message"]],
                        "current_step": "need_confirmation",
                        "quantity": 0,
                        "wants_to_order": False
                    }
                else:
                    # Conversation is complete
                    st.session_state.conversation_state = "complete"
        else:
            add_message("assistant", "Sorry, there was an error processing your request.")
            st.session_state.conversation_state = "complete"
    
    except requests.exceptions.RequestException as e:
        add_message("assistant", f"Connection error: {str(e)}")
        st.session_state.conversation_state = "complete"

def continue_conversation(user_response: str):
    """Continue existing conversation"""
    try:
        # Prepare request payload
        payload = {
            "user_response": user_response,
            "thread_id": st.session_state.thread_id
        }
        
        # Add current_state if available (for fallback mode)
        if st.session_state.current_state:
            payload["current_state"] = st.session_state.current_state
        
        response = requests.post(f"{BACKEND_URL}/continue-conversation", 
                               json=payload)
        
        if response.status_code == 200:
            result = response.json()
            add_message("assistant", result["message"])
            
            # Update thread ID if changed
            st.session_state.thread_id = result["thread_id"]
            
            # Check if still waiting for input
            if result.get("waiting_for_input", False):
                # Update current state if provided
                if result.get("current_state"):
                    st.session_state.current_state = result["current_state"]
                
                # Determine next state based on message content
                message_lower = result["message"].lower()
                if "how many" in message_lower or "quantity" in message_lower or "perfect!" in message_lower:
                    st.session_state.conversation_state = "need_quantity"
                elif "would you like to order" in message_lower or "order any of these" in message_lower:
                    st.session_state.conversation_state = "need_confirmation"
                else:
                    st.session_state.conversation_state = "waiting_for_input"
            else:
                # Conversation is complete
                st.session_state.conversation_state = "complete"
        else:
            add_message("assistant", "Sorry, there was an error processing your response.")
            st.session_state.conversation_state = "complete"
    
    except requests.exceptions.RequestException as e:
        add_message("assistant", f"Connection error: {str(e)}")
        st.session_state.conversation_state = "complete"

# Main UI
st.title("🛒 Order System")
st.markdown("Welcome! Ask about products or place an order.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Debug info
with st.expander("Debug Info", expanded=False):
    st.write(f"Conversation State: {st.session_state.conversation_state}")
    st.write(f"Thread ID: {st.session_state.thread_id}")
    st.write(f"Has Current State: {bool(st.session_state.current_state)}")
    if st.session_state.current_state:
        st.write(f"Current State Keys: {list(st.session_state.current_state.keys())}")

# Handle input based on conversation state
if st.session_state.conversation_state == "need_confirmation":
    st.markdown("---")
    st.markdown("**🤔 Would you like to place an order?**")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        user_response = st.text_input("Your response:", placeholder="Type your response or use buttons...", key="confirmation_input")
    
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

elif st.session_state.conversation_state == "need_quantity":
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

elif st.session_state.conversation_state == "waiting_for_input":
    st.markdown("---")
    st.markdown("**💬 Please respond:**")
    
    user_response = st.text_input("Your response:", placeholder="Type your response...", key="general_input")
    
    if user_response and st.button("Send", key="send_general"):
        add_message("user", user_response)
        continue_conversation(user_response)
        st.rerun()

elif st.session_state.conversation_state in ["waiting_for_query", "complete"]:
    # Regular chat input
    if prompt := st.chat_input("Ask about products or place an order..."):
        add_message("user", prompt)
        reset_conversation()
        start_new_conversation(prompt)
        st.rerun()

# Sidebar
with st.sidebar:
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
    
    st.markdown("---")
    st.markdown("**Features:**")
    st.markdown("- LangGraph workflow with interrupts")
    st.markdown("- Thread-based conversations")
    st.markdown("- Hybrid interrupt/manual mode")
    st.markdown("- Multi-language support")
    st.markdown("- Smart conversation flow")
    
    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.messages = []
        reset_conversation()
        st.rerun()

# Connection status indicator
try:
    health_response = requests.get(f"{BACKEND_URL}/health", timeout=2)
    if health_response.status_code == 200:
        st.sidebar.success("🟢 Backend Connected")
    else:
        st.sidebar.error("🔴 Backend Error")
except:
    st.sidebar.error("🔴 Backend Offline")

# Footer
st.markdown("---")
st.markdown("*Powered by LangGraph + LangChain + Gemini + FastAPI + Streamlit*")