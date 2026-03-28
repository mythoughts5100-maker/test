import os
import psycopg2
import random
from datetime import datetime, timedelta
import time

# Use environment variable for safety
DB_URL = os.environ.get("postgresql://saleh:KvjEAgXLHeFi6CLHBQsGIL0ul5TkqgOk@dpg-d73bs4s2kvos738cbel0-a.oregon-postgres.render.com/mydb1_sei2")
if not DB_URL:
    raise ValueError("DB_URL environment variable is not set!")

conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

# Create sales table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    sale_date DATE,
    product VARCHAR(50),
    region VARCHAR(50),
    sales_amount INT
);
""")
conn.commit()

products = ["Laptop", "Phone", "Tablet"]
regions = ["Baku", "Ganja", "Sumqayit"]

# Function to insert a sale
def add_sale(sale_date):
    cursor.execute("""
        INSERT INTO sales (sale_date, product, region, sales_amount)
        VALUES (%s, %s, %s, %s)
    """, (
        sale_date,
        random.choice(products),
        random.choice(regions),
        random.randint(100, 1000)
    ))
    conn.commit()
    print(f"Inserted sale for {sale_date}")

# Optional: generate past 30 days of sales
start_date = datetime.now().date() - timedelta(days=30)
for i in range(30):
    day = start_date + timedelta(days=i)
    for _ in range(5):
        add_sale(day)

# Infinite loop: add one sale per day
while True:
    today = datetime.now().date()
    add_sale(today)
    
    # Keep only last 60 days of data
    cursor.execute("DELETE FROM sales WHERE sale_date < NOW() - INTERVAL '60 days'")
    conn.commit()

    time.sleep(24*60*60)  # wait 24 hours