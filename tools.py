from db import run_query
from ticketing import create_ticket
import sqlite3

DB="data/app.db"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_db_schema",
            "description": "Return database schema: tables and their columns. No row data.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_sql_query",
            "description": "Run a SAFE SELECT query on the database. Max 100 rows.",
            "parameters": {
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "required": ["sql"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Create a support ticket for a human (GitHub issue).",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["title", "body"],
            },
        },
    },
]

def _schema_text():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall()]
    out = []
    for t in tables:
        cur.execute(f"PRAGMA table_info({t});")
        cols = cur.fetchall()
        col_str = ", ".join([f"{c[1]} ({c[2]})" for c in cols])
        out.append(f"{t}: {col_str}")
    con.close()
    return "\n".join(out)

def handle(name, args):
    print("[LOG]", name, args)

    if name == "get_db_schema":
        return {"schema": _schema_text()}

    if name == "run_sql_query":
        df = run_query(args["sql"], limit=100)
        return {"columns": list(df.columns), "rows": df.to_dict(orient="records"), "row_count": len(df)}

    if name == "create_support_ticket":
        url = create_ticket(args["title"], args["body"])
        return {"url": url}

    raise Exception("Unknown tool: " + name)