import sqlite3, random, os
from datetime import datetime, timedelta

os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/app.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS sales(
 id INTEGER PRIMARY KEY,
 date TEXT,
 customer TEXT,
 product TEXT,
 region TEXT,
 amount REAL
)
""")

c.execute("DELETE FROM sales")

products = ["Basic","Pro","Enterprise"]
regions = ["EU","US","APAC"]

for i in range(2000):
    c.execute("""
    INSERT INTO sales(date,customer,product,region,amount)
    VALUES(?,?,?,?,?)
    """,(
        (datetime.now()-timedelta(days=random.randint(1,365))).strftime("%Y-%m-%d"),
        f"CUST{random.randint(1,400)}",
        random.choice(products),
        random.choice(regions),
        round(random.uniform(20,500),2)
    ))

conn.commit()
conn.close()
print("Database created with 2000 rows")