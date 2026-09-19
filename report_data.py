import sqlite3
import json

DB_PATH = "report.db"


def get_report_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Toplam sipariş sayısı
    total_orders = cur.execute("SELECT COUNT(*) AS c FROM orders").fetchone()["c"]

    # Toplam gelir
    total_revenue = cur.execute("SELECT SUM(amount) AS s FROM orders").fetchone()["s"]

    # En çok gelir getiren ilk 5 ürün
    top_products = cur.execute("""
        SELECT product, SUM(amount) AS revenue
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
    """).fetchall()

    # Son 7 gündeki günlük sipariş sayısı
    orders_last_7_days = cur.execute("""
        SELECT created_at, COUNT(*) AS count
        FROM orders
        WHERE created_at >= date('now', '-7 days')
        GROUP BY created_at
        ORDER BY created_at
    """).fetchall()

    conn.close()

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "top_products": [dict(row) for row in top_products],
        "orders_last_7_days": [dict(row) for row in orders_last_7_days],
    }


if __name__ == "__main__":
    data = get_report_data()
    print(json.dumps(data, indent=2))