import sqlite3
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from report_data import get_report_data
from render_report import build_html, render_pdf

DB_PATH = "report.db"
app = FastAPI()


def init_reports_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_reports_table()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reports", status_code=201)
def create_report(force: bool = False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if not force:
        existing = cur.execute(
            "SELECT id, path FROM reports WHERE date(created_at) = date('now') ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if existing is not None:
            conn.close()
            return JSONResponse(
                status_code=200,
                content={"id": existing["id"], "file": f"/reports/{existing['id']}/file"}
            )

    data = get_report_data()
    html = build_html(data)

    # Insert a placeholder row first to get an id
    cur.execute(
        "INSERT INTO reports (path, created_at) VALUES (?, datetime('now'))",
        ("",)
    )
    report_id = cur.lastrowid

    os.makedirs("reports", exist_ok=True)
    file_path = f"reports/{report_id}.pdf"
    render_pdf(html, file_path)

    cur.execute("UPDATE reports SET path = ? WHERE id = ?", (file_path, report_id))
    conn.commit()
    conn.close()

    return {"id": report_id, "file": f"/reports/{report_id}/file"}


@app.get("/reports/{report_id}")
def get_report(report_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "file": f"/reports/{row['id']}/file",
    }


@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT path FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(row[0], media_type="application/pdf")