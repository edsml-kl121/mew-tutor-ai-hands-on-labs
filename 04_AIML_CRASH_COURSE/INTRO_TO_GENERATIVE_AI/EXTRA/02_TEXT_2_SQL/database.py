import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

def init_database():
    conn = sqlite3.connect('sales.db')
    c = conn.cursor()
    
    # Create sales table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            product_name TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL
        )
    ''')
    
    # Check if data exists
    c.execute("SELECT COUNT(*) FROM sales")
    if c.fetchone()[0] == 0:
        # Generate sample data
        products = [
            ("Laptop", 999.99),
            ("Smartphone", 699.99),
            ("Headphones", 149.99),
            ("Tablet", 499.99),
            ("Smartwatch", 299.99)
        ]
        
        # Generate data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        sample_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Generate 3-8 sales per day
            daily_sales = random.randint(3, 8)
            for _ in range(daily_sales):
                product, price = random.choice(products)
                quantity = random.randint(1, 5)
                total = price * quantity
                
                sample_data.append((
                    current_date.strftime('%Y-%m-%d'),
                    product,
                    quantity,
                    price,
                    total
                ))
            current_date += timedelta(days=1)
        
        # Insert sample data
        c.executemany(
            "INSERT INTO sales (date, product_name, quantity, unit_price, total_amount) "
            "VALUES (?, ?, ?, ?, ?)",
            sample_data
        )
    
    conn.commit()
    conn.close()

def execute_query(query):
    conn = sqlite3.connect('sales.db')
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        conn.close()
