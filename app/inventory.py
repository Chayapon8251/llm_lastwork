"""Read-only SQLite snapshot with bound values; model cannot submit raw SQL."""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def connect():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE equipment(id TEXT PRIMARY KEY, code TEXT, name TEXT, category TEXT, status TEXT, deposit INTEGER)")
    rows = json.loads((ROOT / "data/inventory.json").read_text(encoding="utf-8"))
    db.executemany("INSERT INTO equipment VALUES(:id,:code,:name,:category,:status,:deposit)", rows)
    db.commit()
    db.execute("PRAGMA query_only = ON")
    return db


def query_inventory(category=None, code=None, status=None):
    conditions, params = [], []
    for field, value in (("category", category), ("code", code), ("status", status)):
        if value is not None:
            conditions.append(field + " = ?")
            params.append(value.upper() if field == "code" else value)
    sql = "SELECT id, code, name, category, status, deposit FROM equipment"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY category, code, id LIMIT 30"
    with connect() as db:
        rows = [dict(row) for row in db.execute(sql, params)]
    return {"source_id": "inventory", "source": "data/inventory.json", "snapshot": "synthetic-fixed-v1", "items": rows, "count": len(rows), "sql": sql, "parameters": params}
