from flask import Flask
import os, psycopg2, random, threading, time
from datetime import datetime

app = Flask(__name__)

# -------------------------
# Database connection function (SAFE way)
# -------------------------
DB_URL = os.environ.get("DB_URL")
if not DB_URL:
    raise ValueError("DB_URL environment variable is not set!")

def get_conn():
    return psycopg2.connect(DB_URL)

# -------------------------
# Create table if not exists
# -------------------------
with get_conn() as conn:
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id SERIAL PRIMARY KEY,
            sale_date DATE,
            product VARCHAR(50),
            region VARCHAR(50),
            sales_amount INT
        );
        """)

products = ["Laptop", "Phone", "Tablet"]
regions = ["Baku", "Ganja", "Sumqayit"]

# -------------------------
# Background generator
# -------------------------
def add_sales_loop():
    while True:
        try:
            now = datetime.now()

            with get_conn() as conn:
                with conn.cursor() as cursor:
                    # Insert 1 row every minute
                    cursor.execute("""
                        INSERT INTO sales (sale_date, product, region, sales_amount)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        now.date(),
                        random.choice(products),
                        random.choice(regions),
                        random.randint(100, 1000)
                    ))

                    print(f"Inserted sale at {now}")

                    # Cleanup once per hour
                    if now.minute == 0:
                        cursor.execute("""
                            DELETE FROM sales 
                            WHERE sale_date < NOW() - INTERVAL '60 days'
                        """)
                        print("Old data cleaned")

        except Exception as e:
            print("Error:", e)

        # Wait 1 minute
        time.sleep(60)

# Start background thread
threading.Thread(target=add_sales_loop, daemon=True).start()

# -------------------------
# Minimal web server
# -------------------------
@app.route("/")
def index():
    return "Sales generator running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))