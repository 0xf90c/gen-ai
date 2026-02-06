import sqlite3
import pandas as pd

DB="data/app.db"
BLOCK=["drop","delete","update","insert","alter","truncate","pragma","attach","detach","vacuum","reindex"]

def safe(sql):
    s = sql.lower().strip()
    if not s.startswith("select"):
        return False
    return not any(b in s for b in BLOCK)

def run_query(sql, limit=100):
    if not safe(sql):
        raise Exception("Unsafe SQL blocked (SELECT only).")

    # remove trailing semicolon
    sql = sql.strip().rstrip(";")

    # add LIMIT only if none exists
    if " limit " not in sql.lower():
        sql = f"{sql} LIMIT {limit}"

    con = sqlite3.connect(DB)
    df = pd.read_sql_query(sql, con)
    con.close()
    return df

def stats():
    con=sqlite3.connect(DB)
    cur=con.cursor()
    cur.execute("select count(*) from sales")
    rows=cur.fetchone()[0]
    cur.execute("select round(sum(amount),2) from sales")
    revenue=cur.fetchone()[0]
    con.close()
    return rows,revenue