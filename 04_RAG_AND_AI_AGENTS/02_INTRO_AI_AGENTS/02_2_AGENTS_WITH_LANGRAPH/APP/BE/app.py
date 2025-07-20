# backend.py
import os
import json
import re
from typing import TypedDict, List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

# Try to import interrupt - handle if not available in this version
try:
    from langgraph.types import Command, interrupt
    INTERRUPT_AVAILABLE = True
except ImportError:
    try:
        from langgraph import interrupt, Command
        INTERRUPT_AVAILABLE = True
    except ImportError:
        INTERRUPT_AVAILABLE = False
        print("Warning: interrupt function not available, using manual approach")

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Order System API")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

google_api_key = os.environ["GOOGLE_API_KEY"]

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=5,
    google_api_key=google_api_key
)

# State definition for LangGraph
class OrderState(TypedDict):
    user_query: str
    route: str
    products_to_search: List[str]
    search_results: Dict[str, Any]
    wants_to_order: bool
    quantity: int
    messages: List[str]
    current_step: str
    waiting_for_input: bool
    input_type: str
    user_response: Optional[str]  # For user responses

# Request/Response models
class InitialQueryRequest(BaseModel):
    user_query: str

class ConversationResponse(BaseModel):
    message: str
    thread_id: str
    is_complete: bool
    waiting_for_input: bool = False
    current_state: Optional[Dict[str, Any]] = None

class ContinueConversationRequest(BaseModel):
    user_response: str
    thread_id: str
    current_state: Optional[Dict[str, Any]] = None

# Mock product database
PRODUCT_DB = {
    "apple": {"name": "Apple", "price": 1.50, "in_stock": True},
    "orange": {"name": "Orange", "price": 2.00, "in_stock": True},
    "pineapple": {"name": "Pineapple", "price": 5.00, "in_stock": False},
    "banana": {"name": "Banana", "price": 1.00, "in_stock": True},
    "grape": {"name": "Grape", "price": 3.00, "in_stock": True},
    "milk": {"name": "Milk", "price": 2.50, "in_stock": True},
    "bread": {"name": "Bread", "price": 3.00, "in_stock": True}
}

# Create memory saver for persistent conversations
memory = MemorySaver()

# LangGraph node functions
def route_query(state: OrderState) -> OrderState:
    """Route user query to appropriate handler"""
    query = state["user_query"]
    
    prompt = f"""Analyze this user query and determine if it's related to ordering products or just greeting/irrelevant topics.

Query: "{query}"

Respond with either "order" or "greeting" only."""
    
    try:
        response = llm.invoke(prompt)
        route = response.content.strip().lower()
        state["route"] = "order" if "order" in route else "greeting"
        state["current_step"] = "routed"
    except Exception as e:
        state["route"] = "greeting"
        state["current_step"] = "routing_error"
    
    return state

def handle_greeting(state: OrderState) -> OrderState:
    """Handle greeting and irrelevant topics"""
    query = state["user_query"]
    
    prompt = f"""The user said: "{query}"

Provide a friendly response. If it's a greeting, greet them back and mention you can help with ordering products.
Keep it brief and helpful."""
    
    try:
        response = llm.invoke(prompt)
        state["messages"].append(response.content)
        state["current_step"] = "complete"
    except Exception as e:
        state["messages"].append("Hello! I can help you order products. What would you like?")
        state["current_step"] = "complete"
    
    return state

def extract_products(state: OrderState) -> OrderState:
    """Extract and break down products from user query"""
    query = state["user_query"]
    
    prompt = f"""User Query: "{query}"

Instructions:
- Identify all distinct product mentions from the user message
- Generate exactly one simple search term per item, staying close to user phrasing
- Focus on food items, groceries, or products that can be ordered
- Normalize to singular form (e.g., "apples" -> "apple")
- Return output as a JSON array of strings

Examples:
- "Do you have apples, oranges and pineapples?" -> ["apple", "orange", "pineapple"]
- "I want to buy bananas" -> ["banana"]
- "Can I order some milk and bread?" -> ["milk", "bread"]

Return only the JSON array, nothing else:"""
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        if response_text.startswith('[') and response_text.endswith(']'):
            products = json.loads(response_text)
        else:
            json_match = re.search(r'\[.*?\]', response_text)
            if json_match:
                products = json.loads(json_match.group())
            else:
                products = []
        
        state["products_to_search"] = products if isinstance(products, list) else []
        state["current_step"] = "products_extracted"
    except Exception as e:
        state["products_to_search"] = []
        state["current_step"] = "extraction_error"
    
    return state

def search_products(state: OrderState) -> OrderState:
    """Search for each product separately"""
    products = state["products_to_search"]
    search_results = {}
    
    if not products:
        state["messages"].append("I couldn't find any products in your query. Could you specify what you'd like to order?")
        state["current_step"] = "no_products"
        return state
    
    for product in products:
        product_key = product.lower().strip()
        if product_key in PRODUCT_DB:
            search_results[product] = PRODUCT_DB[product_key]
        else:
            search_results[product] = {"name": product, "price": 0, "in_stock": False}
    
    state["search_results"] = search_results
    
    # Create summary message
    available_products = []
    unavailable_products = []
    
    for product, result in search_results.items():
        if result.get("in_stock", False):
            available_products.append(f"{result['name']} (${result['price']})")
        else:
            unavailable_products.append(product.title())
    
    if available_products:
        message = f"✅ Available: {', '.join(available_products)}"
        if unavailable_products:
            message += f"\n❌ Not available: {', '.join(unavailable_products)}"
        message += f"\n\nWould you like to order any of these? 😊"
        state["current_step"] = "need_confirmation"
    else:
        message = f"❌ Sorry, none of these products are available: {', '.join(unavailable_products)}"
        state["current_step"] = "no_products_available"
    
    state["messages"].append(message)
    return state

def ask_order_confirmation(state: OrderState) -> OrderState:
    """Ask user for order confirmation - uses interrupt if available"""
    # Check if we have available products
    available_products = {k: v for k, v in state["search_results"].items() if v.get("in_stock", False)}
    
    if not available_products:
        state["current_step"] = "no_products_available"
        return state
    
    if INTERRUPT_AVAILABLE:
        try:
            print("DEBUG - Using interrupt for order confirmation")
            # Use interrupt to pause and wait for user input
            user_response = interrupt("Would you like to order any of these products?")
            
            # Process the user's response immediately
            state = process_user_response(state, user_response)
            return state
        except Exception as e:
            print(f"Interrupt failed: {e}")
            # Fall back to manual approach
            state["waiting_for_input"] = True
            state["input_type"] = "confirmation"
            return state
    else:
        # Manual approach - set waiting flags
        state["waiting_for_input"] = True
        state["input_type"] = "confirmation"
        return state

def ask_quantity(state: OrderState) -> OrderState:
    """Ask for quantity - uses interrupt if available"""
    if not state.get("wants_to_order", False):
        return state
    
    if state.get("quantity", 0) > 0:
        return state  # Already have quantity
    
    if INTERRUPT_AVAILABLE:
        try:
            # Use interrupt to ask for quantity
            user_response = interrupt("Perfect! How many would you like?")
            
            # Process quantity immediately
            try:
                quantity = int(user_response.strip())
                if quantity > 0:
                    state["quantity"] = quantity
                    state["current_step"] = "quantity_received"
                else:
                    state["messages"].append("Please enter a valid positive number.")
                    state["current_step"] = "need_quantity"
            except ValueError:
                state["messages"].append("Please enter a valid number for the quantity.")
                state["current_step"] = "need_quantity"
                
            return state
        except Exception as e:
            print(f"Interrupt failed: {e}")
            # Fall back to manual approach
            state["waiting_for_input"] = True
            state["input_type"] = "quantity"
            state["current_step"] = "need_quantity"
            return state
    else:
        # Manual approach
        state["waiting_for_input"] = True
        state["input_type"] = "quantity"
        state["current_step"] = "need_quantity"
        return state

def process_user_response(state: OrderState, user_response: str) -> OrderState:
    """Process user response for order confirmation"""
    # Use LLM to detect intent
    intent_prompt = f"""User said: "{user_response}"

Analyze if the user wants to order/buy products or not. Consider responses in any language.
Look for:
- Positive intent (yes, want, buy, order, take, เอา, ซื้อ, ต้องการ, etc.)
- Negative intent (no, don't want, cancel, ไม่, ไม่เอา, etc.)

Respond with only "YES" if they want to order, or "NO" if they don't want to order."""
    
    try:
        intent_response = llm.invoke(intent_prompt)
        state["wants_to_order"] = "YES" in intent_response.content.strip().upper()
        
        if state["wants_to_order"]:
            # Try to extract quantity from the response
            quantity_prompt = f"""User said: "{user_response}"

Extract any quantity/number mentioned. Look for:
- Numbers (1, 2, 3, สาม, etc.)
- Quantity words (one, two, หนึ่ง, สอง, สาม, etc.)

If a quantity is mentioned, respond with just the number (e.g., "3").
If no quantity mentioned, respond with "0"."""
            
            try:
                quantity_response = llm.invoke(quantity_prompt)
                extracted_quantity = int(quantity_response.content.strip())
                if extracted_quantity > 0:
                    state["quantity"] = extracted_quantity
                    state["current_step"] = "quantity_extracted"
                else:
                    state["current_step"] = "need_quantity"
            except:
                state["current_step"] = "need_quantity"
        else:
            state["current_step"] = "order_declined"
            
    except Exception as e:
        state["wants_to_order"] = False
        state["current_step"] = "confirmation_error"
    
    return state

def process_order_confirmation(state: OrderState) -> OrderState:
    """Process order confirmation response - for manual flow"""
    user_response = state.get("user_response", "")
    return process_user_response(state, user_response)

def finalize_order(state: OrderState) -> OrderState:
    """Finalize order with quantity"""
    # Get first available product from search results
    available_product = None
    for product, details in state["search_results"].items():
        if details.get("in_stock", False):
            available_product = details
            break
    
    quantity = state.get("quantity", 0)
    
    print(f"DEBUG - Finalizing order: available_product = {available_product}, quantity = {quantity}")
    
    if available_product and quantity > 0:
        total = available_product["price"] * quantity
        message = f"Order confirmed: {quantity} {available_product['name']}(s) for ${total:.2f}\n\nThank you for your order! 🎉"
        state["messages"].append(message)
        state["current_step"] = "order_complete"
        print(f"DEBUG - Order completed successfully")
    else:
        print(f"DEBUG - Order failed: available_product = {available_product}, quantity = {quantity}")
        if not available_product:
            state["messages"].append("Sorry, no products are available for ordering.")
        elif quantity <= 0:
            state["messages"].append("Sorry, invalid quantity specified.")
        else:
            state["messages"].append("Sorry, there was an error processing your order.")
        state["current_step"] = "order_error"
    
    return state

def end_conversation(state: OrderState) -> OrderState:
    """End conversation"""
    if state["current_step"] == "order_declined":
        state["messages"].append("No problem! Feel free to ask if you need anything else.")
    elif state["current_step"] == "need_quantity":
        state["messages"].append("Perfect! How many would you like?")
    
    # Mark as not waiting for input when ending
    state["waiting_for_input"] = False
    return state

# Graph routing functions
def should_handle_order(state: OrderState) -> str:
    return "extract_products" if state["route"] == "order" else "handle_greeting"

def should_ask_confirmation(state: OrderState) -> str:
    if state["current_step"] == "need_confirmation":
        return "ask_order_confirmation"
    elif state["current_step"] in ["no_products", "no_products_available"]:
        return "end"
    else:
        return "end"

def continue_after_confirmation(state: OrderState) -> str:
    if state["current_step"] == "quantity_extracted":
        return "finalize_order"
    elif state["current_step"] == "need_quantity":
        return "ask_quantity"
    elif state["current_step"] == "order_declined":
        return "end"
    else:
        return "end"

def continue_after_quantity(state: OrderState) -> str:
    if state.get("quantity", 0) > 0 and state.get("wants_to_order", False):
        return "finalize_order"
    else:
        return "end"

# Create LangGraph
def create_order_graph():
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
        return workflow.compile(checkpointer=memory)
    else:
        return workflow.compile()

# Global graph instance
graph = create_order_graph()

# API Endpoints
@app.post("/start-conversation", response_model=ConversationResponse)
async def start_conversation(request: InitialQueryRequest):
    """Start a new conversation with user query"""
    try:
        # Create a unique thread ID
        import uuid
        thread_id = str(uuid.uuid4())
        
        initial_state = OrderState(
            user_query=request.user_query,
            route="",
            products_to_search=[],
            search_results={},
            wants_to_order=False,
            quantity=0,
            messages=[],
            current_step="starting",
            waiting_for_input=False,
            input_type="",
            user_response=None
        )
        
        if INTERRUPT_AVAILABLE:
            config = {"configurable": {"thread_id": thread_id}}
            
            try:
                # Run the graph
                result = graph.invoke(initial_state, config=config)
                
                # Check if the thread is interrupted
                state_snapshot = graph.get_state(config)
                
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
                    # Conversation completed
                    message = result["messages"][-1] if result["messages"] else "Hello! How can I help you?"
                    return ConversationResponse(
                        message=message,
                        thread_id=thread_id,
                        is_complete=True,
                        waiting_for_input=False
                    )
            except Exception as e:
                print(f"Interrupt mode failed with exception: {e}")
                # Check if it's specifically an interrupt exception
                if "Interrupt" in str(e.__class__.__name__) or "interrupt" in str(e).lower():
                    # This is an interrupt - get the current state
                    try:
                        state_snapshot = graph.get_state(config)
                        current_values = state_snapshot.values
                        message = current_values["messages"][-1] if current_values["messages"] else "Please respond:"
                        
                        return ConversationResponse(
                            message=message,
                            thread_id=thread_id,
                            is_complete=False,
                            waiting_for_input=True,
                            current_state=current_values
                        )
                    except Exception as inner_e:
                        print(f"Failed to get state after interrupt: {inner_e}")
                        # Fall back to manual mode
                        pass
                else:
                    # Different kind of error, fall back to manual mode
                    pass
        
        # Manual mode (fallback or no interrupt support)
        final_state = None
        for step in graph.stream(initial_state):
            for node_name, node_state in step.items():
                final_state = node_state
        
        # Check if waiting for input
        if final_state.get("waiting_for_input", False):
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
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/continue-conversation", response_model=ConversationResponse)
async def continue_conversation(request: ContinueConversationRequest):
    """Continue conversation with user response"""
    try:
        if INTERRUPT_AVAILABLE and not request.current_state:
            print("DEBUG - Using interrupt mode")
            # Use interrupt mode
            config = {"configurable": {"thread_id": request.thread_id}}
            
            try:
                # Resume the graph with the user's response using Command
                result = graph.invoke(
                    Command(resume=request.user_response), 
                    config=config
                )
                
                # Check if the thread is still interrupted
                state_snapshot = graph.get_state(config)
                
                if state_snapshot.next:  # Graph is still interrupted/waiting
                    message = result["messages"][-1] if result["messages"] else "Please respond:"
                    
                    return ConversationResponse(
                        message=message,
                        thread_id=request.thread_id,
                        is_complete=False,
                        waiting_for_input=True,
                        current_state=result
                    )
                else:
                    # Conversation completed
                    message = result["messages"][-1] if result["messages"] else "Thank you!"
                    return ConversationResponse(
                        message=message,
                        thread_id=request.thread_id,
                        is_complete=True,
                        waiting_for_input=False
                    )
            except Exception as e:
                print(f"Resume failed with exception: {e}")
                # Check if it's specifically an interrupt exception
                if "Interrupt" in str(e.__class__.__name__) or "interrupt" in str(e).lower():
                    # This is another interrupt - get the current state
                    try:
                        state_snapshot = graph.get_state(config)
                        current_values = state_snapshot.values
                        message = current_values["messages"][-1] if current_values["messages"] else "Please respond:"
                        
                        return ConversationResponse(
                            message=message,
                            thread_id=request.thread_id,
                            is_complete=False,
                            waiting_for_input=True,
                            current_state=current_values
                        )
                    except Exception as inner_e:
                        print(f"Failed to get state after resume interrupt: {inner_e}")
                        # Fall back to manual mode
                        pass
                else:
                    # Different kind of error, fall back to manual mode
                    pass
        else:
            print(f"DEBUG - Using manual mode, has current_state: {bool(request.current_state)}")
        
        # Manual mode (original working approach)
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
        
        print(f"DEBUG - Continue conversation: current_step = {state['current_step']}")
        print(f"DEBUG - Reconstructed search_results: {state['search_results']}")
        print(f"DEBUG - User response: {request.user_response}")
        print(f"DEBUG - Full current_state keys: {list(request.current_state.keys())}")
        
        # If search_results is empty but we have a user_query, try to reconstruct
        if not state["search_results"] and state.get("user_query"):
            print("DEBUG - Attempting to reconstruct search_results from user_query")
            user_query = state["user_query"].lower()
            reconstructed_results = {}
            
            # Check for common products mentioned in the query
            for product_key, product_data in PRODUCT_DB.items():
                if product_key in user_query or product_data["name"].lower() in user_query:
                    reconstructed_results[product_key] = product_data
                    print(f"DEBUG - Reconstructed: {product_key} -> {product_data}")
            
            if reconstructed_results:
                state["search_results"] = reconstructed_results
                print(f"DEBUG - Updated search_results: {state['search_results']}")
        
        # Determine what to do based on current step
        if state["current_step"] == "need_confirmation":
            print("DEBUG - Processing order confirmation")
            # Process order confirmation
            state = process_order_confirmation(state)
            print(f"DEBUG - After confirmation: current_step = {state['current_step']}")
            
            if state["current_step"] == "quantity_extracted":
                # Quantity was extracted, finalize order
                state = finalize_order(state)
                return ConversationResponse(
                    message=state["messages"][-1],
                    thread_id=request.thread_id,
                    is_complete=True,
                    waiting_for_input=False
                )
            elif state["current_step"] == "need_quantity":
                print("DEBUG - Need quantity, setting up state")
                # Update the state for quantity request
                state["current_step"] = "need_quantity"
                return ConversationResponse(
                    message="Perfect! How many would you like?",
                    thread_id=request.thread_id,
                    is_complete=False,
                    waiting_for_input=True,
                    current_state=dict(state)
                )
            else:
                # Order declined
                return ConversationResponse(
                    message="No problem! Feel free to ask if you need anything else.",
                    thread_id=request.thread_id,
                    is_complete=True,
                    waiting_for_input=False
                )
        
        elif state["current_step"] == "need_quantity":
            print("DEBUG - Processing quantity input")
            print(f"DEBUG - Current state search_results: {state.get('search_results', {})}")
            # Process quantity input
            try:
                quantity = int(request.user_response.strip())
                print(f"DEBUG - Parsed quantity: {quantity}")
                state["quantity"] = quantity
                state = finalize_order(state)
                return ConversationResponse(
                    message=state["messages"][-1],
                    thread_id=request.thread_id,
                    is_complete=True,
                    waiting_for_input=False
                )
            except ValueError:
                print(f"DEBUG - Failed to parse quantity: {request.user_response}")
                return ConversationResponse(
                    message="Please enter a valid number for the quantity.",
                    thread_id=request.thread_id,
                    is_complete=False,
                    waiting_for_input=True,
                    current_state=dict(state)
                )
        
        else:
            print(f"DEBUG - Unknown state: {state['current_step']}")
            return ConversationResponse(
                message="I'm not sure how to help with that. Could you start a new conversation?",
                thread_id=request.thread_id,
                is_complete=True,
                waiting_for_input=False
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error continuing conversation: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)