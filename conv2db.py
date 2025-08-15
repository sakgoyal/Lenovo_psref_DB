import sys
import duckdb
import json

duckdb.sql("CREATE TABLE products AS FROM read_csv('./out/*.csv', union_by_name = true);")

# cur.execute('CREATE INDEX IF NOT EXISTS idx_country_region ON products("Country/Region")')
# cur.execute('CREATE INDEX IF NOT EXISTS idx_memory ON products("Memory")')
# cur.execute('CREATE INDEX IF NOT EXISTS idx_processor ON products("Processor")')
# cur.execute('CREATE INDEX IF NOT EXISTS idx_display ON products("Display")')
# conn.commit()

## Generate distinct values for each column and store them in a new table
## This will be used for the frontend to generate filter options
## Use this otherwise the frontend will be extremely slow

def get_cols() -> list[str]:
    omit_list = ["EAN / UPC / JAN", "Model", "Machine Type", "TopSeller", "Monitor Cable", "Controls", "Others", "ISV Certifications", "Base Warranty", "Other Certifications", "Included Upgrade", "End of Support", "Announce Date"]

    rows = duckdb.execute("SELECT name FROM pragma_table_info('products')").fetchall()
    column_names: list[str] = [row[0] for row in rows]
    return [col for col in column_names if col not in omit_list]

def get_distinct_values(column_names: list[str]):
    distinct_values_dict: dict[str, list[str]] = {}

    for column in column_names:
        rows = duckdb.execute(f'SELECT DISTINCT "{column}" FROM "products"').fetchall()
        results = [row[0] for row in rows]
        distinct_values_dict[column] = results

    return distinct_values_dict

def create_filter_values_table(distinct_values: dict[str, list[str]]):
    duckdb.execute("DROP TABLE IF EXISTS filter_values")
    duckdb.execute("""
        CREATE TABLE filter_values (
            column_name TEXT,
            distinct_values_json TEXT
        );
    """)

    for column, values in distinct_values.items():
        # Serialize the list of values to a JSON string
        values_json = json.dumps(values)
        duckdb.execute("INSERT INTO filter_values (column_name, distinct_values_json) VALUES (?, ?)", (column, values_json))

column_names = get_cols()
distinct_values_dict = get_distinct_values(column_names)

create_filter_values_table(distinct_values_dict)
