import sqlite3
import csv
import json

conn = sqlite3.connect("products.db")
cur = conn.cursor()


## Generate the database schema and populate it with data from the CSV file
## fill with raw data from the CSV file
with open("out/zzz.csv") as f:
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


## Generate distinct values for each column and store them in a new table
## This will be used for the frontend to generate filter options
## Use this otherwise the frontend will be extremely slow
cur = conn.cursor()

def get_cols() -> list[str]:
    omit_list = ["EAN / UPC / JAN", "Model", "Machine Type", "TopSeller", "Monitor Cable", "Controls", "Others", "ISV Certifications", "Base Warranty", "Other Certifications", "Included Upgrade", "End of Support", "Announce Date"]

    cur.execute("SELECT name FROM pragma_table_info('products')")
    column_names: list[str] = [row[0] for row in cur.fetchall()]
    return [col for col in column_names if col not in omit_list]

def get_distinct_values(column_names: list[str]):
    distinct_values_dict: dict[str, list[str]] = {}

    for column in column_names:
        cur.execute(f'SELECT DISTINCT "{column}" FROM "products"')
        results = [row[0] for row in cur.fetchall()]
        distinct_values_dict[column] = results

    return distinct_values_dict

def create_filter_values_table(distinct_values: dict[str, list[str]]):
    cur.execute("DROP TABLE IF EXISTS filter_values")
    cur.execute("""
        CREATE TABLE filter_values (
            column_name TEXT,
            distinct_values_json TEXT
        );
    """)

    for column, values in distinct_values.items():
        # Serialize the list of values to a JSON string
        values_json = json.dumps(values)
        cur.execute("INSERT INTO filter_values (column_name, distinct_values_json) VALUES (?, ?)", (column, values_json))
    conn.commit()

column_names = get_cols()
distinct_values_dict = get_distinct_values(column_names)

create_filter_values_table(distinct_values_dict)

json_output = json.dumps(distinct_values_dict, indent=4)
with open('distinct_values.json', 'w') as json_file:
    json_file.write(json_output)

conn.close()
