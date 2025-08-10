import sqlite3
import csv

conn = sqlite3.connect("products.db")
cur = conn.cursor()

with open("out/out.csv", encoding="utf-16") as f:
    reader = csv.reader(f)
    headers = next(reader)
    cols = ", ".join(f'"{h}" TEXT' if h != "Model" else '"Model" TEXT PRIMARY KEY' for h in headers)
    cur.execute(f"CREATE TABLE IF NOT EXISTS products ({cols})")
    cur.execute("BEGIN TRANSACTION")
    batch = []
    placeholders = ", ".join("?" * len(headers))
    insert_sql = f"INSERT OR IGNORE INTO products VALUES ({placeholders})"
    for row in reader:
        batch.append(row)
        if len(batch) >= 100:
            cur.executemany(insert_sql, batch)
            batch.clear()
    if batch:
        cur.executemany(insert_sql, batch)
    conn.commit()

cur.execute('CREATE INDEX IF NOT EXISTS idx_country_region ON products("Country/Region")')
cur.execute('CREATE INDEX IF NOT EXISTS idx_memory ON products("Memory")')
cur.execute('CREATE INDEX IF NOT EXISTS idx_processor ON products("Processor")')
cur.execute('CREATE INDEX IF NOT EXISTS idx_display ON products("Display")')
conn.commit()

conn.close()
