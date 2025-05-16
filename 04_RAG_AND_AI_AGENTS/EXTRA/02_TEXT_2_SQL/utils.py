import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_visualization(df, query_type):
    try:
        if df.empty:
            return None
        
        if 'date' in df.columns:
            if 'total_amount' in df.columns or 'quantity' in df.columns:
                # Time series visualization
                fig = px.line(df, x='date', 
                            y=['total_amount'] if 'total_amount' in df.columns else ['quantity'],
                            title='Sales Over Time')
                return fig
        
        if 'product_name' in df.columns:
            if 'total_amount' in df.columns:
                # Bar chart for product sales
                fig = px.bar(df, x='product_name', y='total_amount',
                           title='Sales by Product')
                return fig
            elif 'quantity' in df.columns:
                # Bar chart for product quantity
                fig = px.bar(df, x='product_name', y='quantity',
                           title='Quantity by Product')
                return fig
        
        # Default table view for other types of data
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns),
                       fill_color='paleturquoise',
                       align='left'),
            cells=dict(values=[df[col] for col in df.columns],
                      fill_color='lavender',
                      align='left'))
        ])
        return fig
    except Exception as e:
        raise Exception(f"Visualization error: {str(e)}")
