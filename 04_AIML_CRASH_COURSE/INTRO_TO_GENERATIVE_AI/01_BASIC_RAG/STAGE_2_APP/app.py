import streamlit as st
from functions import search_restaurants, create_restaurant_embeddings, generate_response

# Set page title
st.title("Simple Image Display")

# Add some descriptive text
st.write("This is a basic Streamlit app that displays an image.")

@st.cache_data
def get_restaurant_embeddings():
    print("Creating restaurant embeddings...")
    return create_restaurant_embeddings()

# Get cached embeddings
restaurant_embeddings = get_restaurant_embeddings()    

def retrieval_augmented_generation(query):
    restaurant_results = search_restaurants(query, restaurant_embeddings)

    # 3. Augmented and Generation
    print("Generating response...")
    response = generate_response(query, restaurant_results)
    return response, restaurant_results

user_query = st.text_input("user_input")
if user_query:
    response, search_results = retrieval_augmented_generation(user_query)
    st.markdown(response)
    st.markdown(search_results)
    # Display an image directly
    # Add a footer
    st.markdown("---")
    st.write("Thank you for using this simple app!")