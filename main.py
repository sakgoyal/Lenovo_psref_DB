import json
import os
import re
import time

import duckdb
import requests
from selenium import webdriver

## TODO: make postprocessing more useful by splitting CPU details into separate columns
## for more granular filtering options. ignore for now


def get_session_cookie():
    # set headless mode
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)


    try:
        driver.get("https://psref.lenovo.com")
        time.sleep(1)
        driver.get("https://psref.lenovo.com/api/home/Menu/info")
        time.sleep(1)
        driver.get("https://psref.lenovo.com")
        time.sleep(1)
        #     response = requests.get('https://psref.lenovo.com/api/home/Menu/info')
        # data: list[dict] = response.json()['data']
        driver.get("https://psref.lenovo.com/api/home/Menu/info")
        data = json.loads(driver.find_element("tag name", "pre").text).get('data')


        cookies = driver.get_cookies()
        cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

        print("Cookies:", cookie_string)
        return cookie_string, extract_product_ids(data[0].get('subcollection', []))

    finally:
        driver.quit()

def download_data(product_id: str, cookie: str):
    url = f"https://psref.lenovo.com/api/search/DefinitionFilterAndSearch/ShowModel?pageindex=1&pagesize=300000&product_key={product_id}"

    response = requests.get(url, headers={ 'cookie': cookie })
    response.raise_for_status()
    json_data: dict[str,dict] = response.json()
    data = json_data.get('data')

    if not data:
        raise ValueError(f"No data found for {product_id}")

    def escape_csv(val):
        if val is None:
            return ""
        s = str(val)
        s = s.replace('"', '""')
        s = s.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        if any(c in s for c in [',', '"', '\n', '\r']):
            return f'"{s}"'
        return s

    if not os.path.exists('out'):
        os.makedirs('out')

    cols = data.get('cols', [])
    rows = data.get('rows', [])
    out = [",".join(escape_csv(col) for col in cols)]

    for row in rows:
        out.append(",".join(escape_csv(item) for item in row))

    with open(f"out/{product_id}.csv", "w", encoding="utf-8") as f:
        text = "\n".join(out)
        replacement = {
            r"(\^\|\^)?Various docking.*?</u></a>": "Various",
            r"Non-WWAN": "",
            r"NVIDIA (GeForce )?": "",
            r"Boost Clock ": "",
            r"TGP ": "",
            r"None": "",
            r"RoHS compliant": "RoHS",
            r"military test passed": "",
            r"Integrated AMD Radeon ": "AMD Radeon ",
            r"Memory soldered to systemboard, no slots": "No Slots",
            r"microSD Card Reader": "microSD",
            r"TPM 2.0 Enabled": "TPM 2.0",
            r"1x Ethernet \(RJ-45\)": "Ethernet",
            r"100/1000M \(RJ-45\)": "1GbE",
            r"2.5GbE \(RJ-45\)": "2.5GbE",
            r"No [oO]nboard Ethernet": "",
            r"Pen Not Supported": "",
            r"No support": "",
            r"No card reader": "",
            r"Non-AI PC": "",
            r"No smart card reader": "",
            r"High Definition \(HD\) Audio, ": "",
            r"No color calibration": "",
            r"Kensington Nano Security Slot, 2.5 x 6 mm": "Kensington Nano",
            r"No physical locks": "",
            r"Headphone \/ microphone combo jack \(3.5mm\)": "3.5mm Combo Jack",
            r"\^\|\^": " | ",
            r"IR camera for Windows Hello \(facial recognition\)": "Windows Hello IR Camera",
            r"\xa0": " ", # incoming data is UTF-16. so we need to strip all these out to compress them
        }
        for pattern, repl in replacement.items():
            text = re.sub(pattern, repl, text)
        f.write(text)

def extract_product_ids(data: list[dict]) -> list[str]:
    product_ids = []
    for item in data:
        if item.get('type') == 'product':
            product_ids.append(item.get('id'))
        if item.get('subcollection'):
            product_ids.extend(extract_product_ids(item['subcollection']))
    return product_ids

def get_product_ids():
    response = requests.get('https://psref.lenovo.com/api/home/Menu/info')
    response.raise_for_status()
    data: list[dict] = response.json()['data'] # data from all device categories. deeply nested

    print('Product IDs:', data[0].get('subcollection'))

    return extract_product_ids(data[0].get('subcollection', [])) # get only laptop subcollection which is the first item

cookie, pIDs = get_session_cookie()
for product_id in pIDs:
    print(f"Downloading {product_id}")
    download_data(product_id, cookie)

duckdb.sql("CREATE TABLE products AS FROM read_csv('./out/*.csv', union_by_name = true);")

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
            options TEXT
        );
    """)

    for column, values in distinct_values.items():
        values_json = json.dumps(values)
        duckdb.execute("INSERT INTO filter_values (column_name, options) VALUES (?, ?)", (column, values_json))

column_names = get_cols()
distinct_values_dict = get_distinct_values(column_names)

create_filter_values_table(distinct_values_dict)

duckdb.execute("EXPORT DATABASE 'finder/static/export' (FORMAT parquet);")


filter: list[tuple[str, str]] = duckdb.query("SELECT * FROM filter_values WHERE column_name NOT IN ('Optical', 'Docking', 'Included Upgrade', 'Announce Date', 'Standard Ports', 'Operating System', 'Dimensions (WxDxH)', 'Product', 'End of Support');").fetchall()
filter_dict = {}
for column, options in filter:
    val = json.loads(options)
    # sort values and remove empty strings
    val = sorted([v for v in val if v])
    filter_dict[column] = val

with open('finder/src/routes/data.ts', 'w') as f:
    f.write("export const filters = ")
    f.write(json.dumps(filter_dict, indent=4))
