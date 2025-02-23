import streamlit as st

# Set page title
st.title("Simple Image Display")

# Add some descriptive text
st.write("This is a basic Streamlit app that displays an image.")

# Display an image directly
st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", 
         caption="Streamlit Logo", 
         width=400)

# Add a bit more text
st.write("The image above is displayed directly without requiring an upload.")

# Add a footer
st.markdown("---")
st.write("Thank you for using this simple app!")