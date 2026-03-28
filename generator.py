import os
import psycopg2
import random
from datetime import datetime
import time

# -------------------------
# Get database URL from Railway environment variables
# -------------------------
DB_URL = os.environ.get('postgresql://postgres:GevlBDqbWBacBKySejnuyBiGagTafqRJ@gondola.proxy.rlwy.net:45721/railway')  # Set this in Railway secrets

if not DB_URL:
    raise ValueError("DB_URL environment variable is not set!")

# -------------------------
# Connect to Neon DB
# -------------------------
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

# -------------------------
# Create the sales table if it doesn't exist
# -------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    sale_date TIMESTAMP,
    product VARCHAR(50),
    region VARCHAR(50),
    sales_amount INT
);
""")
conn.commit()

# -------------------------
# Lists of products and regions
# -------------------------
products = ["Laptop", "Phone", "Tablet"]
regions = ["Baku", "Ganja", "Sumqayit"]

# -------------------------
# Live generator loop
# -------------------------
while True:
    # Insert a new random sale
    cursor.execute("""
        INSERT INTO sales (sale_date, product, region, sales_amount)
        VALUES (%s, %s, %s, %s)
    """, (
        datetime.now(),
        random.choice(products),
        random.choice(regions),
        random.randint(100, 1000)
    ))
    conn.commit()
    print("Inserted new sale at", datetime.now())

    # Optional: Delete old rows to avoid DB overfill (keep last 30 days)
    cursor.execute("DELETE FROM sales WHERE sale_date < NOW() - INTERVAL '30 days'")
    conn.commit()

    # Wait before next insert (adjustable)
    time.sleep(30)  # insert every 30 seconds