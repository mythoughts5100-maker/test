from flask import Flask
import os, psycopg2, random, threading, time
from datetime import datetime, timedelta

app = Flask(__name__)

# -------------------------
# Database connection from environment variable
# -------------------------
DB_URL = os.environ.get("DB_URL")
if not DB_URL:
    raise ValueError("DB_URL environment variable is not set!")

conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

# -------------------------
# Create sales table if not exists
# -------------------------
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

# -------------------------
# Function to insert sales
# -------------------------
def add_sales_loop():
    while True:
        today = datetime.now().date()
        # Insert 5 random sales per day
        for _ in range(5):
            cursor.execute("""
                INSERT INTO sales (sale_date, product, region, sales_amount)
                VALUES (%s, %s, %s, %s)
            """, (
                today,
                random.choice(products),
                random.choice(regions),
                random.randint(100, 1000)
            ))
            conn.commit()
            print(f"Inserted sale for {today}")
        # Delete old sales beyond 60 days
        cursor.execute("DELETE FROM sales WHERE sale_date < NOW() - INTERVAL '60 days'")
        conn.commit()
        # Wait 24 hours
        time.sleep(24*60*60)

# Run generator in background thread
threading.Thread(target=add_sales_loop, daemon=True).start()

# -------------------------
# Minimal web server to keep free tier alive
# -------------------------
@app.route("/")
def index():
    return "Sales generator running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))