import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "report.db"

PRODUCTS = ["Wireless Mouse", "USB-C Cable", "Notebook", "Desk Lamp", "Coffee Mug", "Phone Stand"]
CUSTOMERS = ["Ayşe Kaya", "Mehmet Demir", "Zeynep Yıldız", "Emre Çelik", "Elif Şahin",
             "Burak Arslan", "Selin Koç", "Can Aydın", "Deniz Kurt", "Ece Polat"]

def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Start clean so running twice doesn't double the rows
    cur.execute("DELETE FROM orders")

    today = datetime.now()
    rows = []
    for _ in range(200):
        customer = random.choice(CUSTOMERS)
        product = random.choice(PRODUCTS)
        amount = round(random.uniform(5, 200), 2)
        days_ago = random.randint(0, 29)
        created_at = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        rows.append((customer, product, amount, created_at))

    cur.executemany(
        "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)",
        rows
    )

    conn.commit()
    conn.close()
    print(f"Seeded {len(rows)} orders into {DB_PATH}")

if __name__ == "__main__":
    seed()