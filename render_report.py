import sqlite3
from datetime import date
from playwright.sync_api import sync_playwright
from report_data import get_report_data

DB_PATH = "report.db"


def build_html(data: dict) -> str:
    today = date.today().strftime("%Y-%m-%d")

    top_products_rows = "".join(
        f"<tr><td>{p['product']}</td><td>${p['revenue']:.2f}</td></tr>"
        for p in data["top_products"]
    )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    all_orders = conn.execute(
        "SELECT customer, product, amount, created_at FROM orders ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    all_orders_rows = "".join(
        f"<tr><td>{o['customer']}</td><td>{o['product']}</td>"
        f"<td>${o['amount']:.2f}</td><td>{o['created_at']}</td></tr>"
        for o in all_orders
    )

    return f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ font-size: 20px; }}
        .totals {{ display: flex; gap: 40px; margin: 20px 0; }}
        .totals div {{ font-size: 16px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
        thead {{ display: table-header-group; }}
        tr {{ break-inside: avoid; }}
        th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; font-size: 12px; }}
        th {{ background: #f2f2f2; }}
    </style>
    </head>
    <body>
        <h1>Sales Report — {today}</h1>
        <div class="totals">
            <div><strong>Total orders:</strong> {data['total_orders']}</div>
            <div><strong>Total revenue:</strong> ${data['total_revenue']:.2f}</div>
        </div>

        <h2>Top 5 products by revenue</h2>
        <table>
            <thead><tr><th>Product</th><th>Revenue</th></tr></thead>
            <tbody>{top_products_rows}</tbody>
        </table>

        <h2>All orders</h2>
        <table>
            <thead><tr><th>Customer</th><th>Product</th><th>Amount</th><th>Date</th></tr></thead>
            <tbody>{all_orders_rows}</tbody>
        </table>
    </body>
    </html>
    """


def render_pdf(html: str, output_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()


if __name__ == "__main__":
    data = get_report_data()
    html = build_html(data)
    import os
    os.makedirs("reports", exist_ok=True)
    render_pdf(html, "reports/test.pdf")
    print("Saved reports/test.pdf")