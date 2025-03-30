import streamlit as st
import pandas as pd
from database import init_database, execute_query
from sql_generator import generate_sql_query
from utils import create_visualization

# Initialize the session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Initialize the database
init_database()

st.title("Natural Language to SQL Chat Assistant")

# Sidebar with query history
with st.sidebar:
    st.header("Query History")
    for idx, (question, query) in enumerate(st.session_state.query_history):
        st.text(f"Q{idx + 1}: {question[:50]}...")
        with st.expander("Show SQL"):
            st.code(query, language="sql")

# Main chat interface
user_question = st.text_input("Ask a question about sales data:", 
                            placeholder="e.g., What is the total sales for last week?")

if user_question:
    try:
        # Generate SQL query
        with st.spinner("Generating SQL query..."):
            result = generate_sql_query(user_question)
            sql_query = result['sql_query']
            explanation = result['explanation']
        
        # Display the generated SQL
        st.subheader("Generated SQL Query")
        st.code(sql_query, language="sql")
        st.markdown(f"*Explanation: {explanation}*")
        
        # Execute query and display results
        with st.spinner("Executing query..."):
            df = execute_query(sql_query)
            
            # Add to query history
            st.session_state.query_history.append((user_question, sql_query))
            
            # Display results
            st.subheader("Query Results")
            st.dataframe(df)
            
            # Create and display visualization
            fig = create_visualization(df, user_question.lower())
            if fig:
                st.plotly_chart(fig)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.error("Please try rephrasing your question or check if it's related to the available data.")

# Display sample questions
st.markdown("---")
st.markdown("### Sample Questions")
st.markdown("""
- What is the total sales for each product?
- Show me daily sales for the last week
- Which product had the highest quantity sold?
- What is the average sale amount per day?
""")
