import sqlite3
import json

conn = sqlite3.connect('products.db')
cursor = conn.cursor()

def get_cols() -> list[str]:
    omit_list = ["EAN / UPC / JAN", "Model", "Machine Type", "TopSeller", "Monitor Cable", "Controls", "Others", "ISV Certifications", "Base Warranty", "Other Certifications", "Included Upgrade", "End of Support", "Announce Date"]

    cursor.execute("SELECT name FROM pragma_table_info('products')")
    column_names: list[str] = [row[0] for row in cursor.fetchall()]
    return [col for col in column_names if col not in omit_list]

def get_distinct_values(column_names: list[str]):
    distinct_values_dict: dict[str, list[str]] = {}

    for column in column_names:
        sql_command = f'SELECT DISTINCT "{column}" FROM "products"'
        cursor.execute(sql_command)
        results = [row[0] for row in cursor.fetchall()]
        distinct_values_dict[column] = results

    return distinct_values_dict

def create_filter_values_table(distinct_values: dict[str, list[str]]):
    cursor.execute("DROP TABLE IF EXISTS filter_values")
    cursor.execute("""
        CREATE TABLE filter_values (
            column_name TEXT,
            distinct_values_json TEXT
        );
    """)

    for column, values in distinct_values.items():
        # Serialize the list of values to a JSON string
        values_json = json.dumps(values)
        cursor.execute("INSERT INTO filter_values (column_name, distinct_values_json) VALUES (?, ?)", (column, values_json))
    conn.commit()

column_names = get_cols()
distinct_values_dict = get_distinct_values(column_names)

create_filter_values_table(distinct_values_dict)

json_output = json.dumps(distinct_values_dict, indent=4)
with open('distinct_values.json', 'w', encoding="utf-8") as json_file:
    json_file.write(json_output)

conn.close()
