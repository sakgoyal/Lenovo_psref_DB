import json
import re
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any, NotRequired, TypedDict

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

REGEX_REPLACEMENTS: dict[re.Pattern[str], str] = {
    re.compile(r"(\^\|\^)?Various docking.*?</u></a>"): "Various",
    re.compile(r"Non-WWAN"): "",
    re.compile(r"NVIDIA (GeForce )?"): "",
    re.compile(r"Boost Clock "): "",
    re.compile(r"TGP "): "",
    re.compile(r"None"): "",
    re.compile(r"RoHS compliant"): "RoHS",
    re.compile(r"military test passed"): "",
    re.compile(r"Integrated AMD Radeon "): "AMD Radeon ",
    re.compile(r"Memory soldered to systemboard, no slots"): "No Slots",
    re.compile(r"microSD Card Reader"): "microSD",
    re.compile(r"TPM 2.0 Enabled"): "TPM 2.0",
    re.compile(r"1x Ethernet \(RJ-45\)"): "Ethernet",
    re.compile(r"100/1000M \(RJ-45\)"): "1GbE",
    re.compile(r"2.5GbE \(RJ-45\)"): "2.5GbE",
    re.compile(r"No [oO]nboard Ethernet"): "",
    re.compile(r"Pen Not Supported"): "",
    re.compile(r"No support"): "",
    re.compile(r"No card reader"): "",
    re.compile(r"Non-AI PC"): "",
    re.compile(r"No smart card reader"): "",
    re.compile(r"High Definition \(HD\) Audio, "): "",
    re.compile(r"No color calibration"): "",
    re.compile(r"Kensington Nano Security Slot, 2.5 x 6 mm"): "Kensington Nano",
    re.compile(r"No physical locks"): "",
    re.compile(r"Headphone \/ microphone combo jack \(3.5mm\)"): "3.5mm Combo Jack",
    re.compile(r"\^\|\^"): " | ",
    re.compile(r"IR camera for Windows Hello \(facial recognition\)"): "Windows Hello IR Camera",
    re.compile(r"\xa0"): " ", # incoming data is UTF-16. so we need to strip all these out to compress them
}

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-infobars")
driver = webdriver.Chrome(options=chrome_options)

print("Fetching product IDs...", flush=True)

def get_product_ids() -> list[ProductIDs]:
    driver.get("https://psref.lenovo.com")
    time.sleep(2)
    driver.get("https://psref.lenovo.com/filter/")
    time.sleep(2)

    driver.get("https://psref.lenovo.com/api/home/Menu/info")
    time.sleep(2)

    driver.get("https://psref.lenovo.com")
    time.sleep(1)

    driver.get("https://psref.lenovo.com/api/home/Menu/info")
    time.sleep(3)

    json_data = driver.find_element(By.TAG_NAME, "pre").text
    response: dict[str, Any] = json.loads(json_data)
    data: list[ProductIDs] | None = response.get('data')

    if not data:
        raise ValueError("Could not get menu data from API")
    return data

API_DATA = get_product_ids()

print("Fetched product IDs.", flush=True)

def extract_product_ids(data: list["ProductIDs"]) -> list[str]:
    product_ids: list[str] = []
    for item in data:
        if item.get('type') == 'product':
            product_ids.append(item.get('id'))
        if item.get('subcollection'):
            product_ids.extend(extract_product_ids(item['subcollection']))
    return product_ids

product_ids = extract_product_ids(API_DATA[0].get('subcollection', []))

dataframes: list[pd.DataFrame] = []  # List to store DataFrames in memory

def download_data(product_id: str) -> None:
    print(f"{product_id}: Downloading...", end="", flush=True)
    url = f"https://psref.lenovo.com/api/search/DefinitionFilterAndSearch/ShowModel?pageindex=1&pagesize=300000&product_key={product_id}"

    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
    json_data: dict[str, Any] = json.loads(driver.find_element(By.TAG_NAME, "pre").text)
    data: ShowModel | None = json_data.get('data')
    print("Processing...", end="", flush=True)

    if not data:
        raise ValueError(f"No data found for {product_id}")

    def escape_csv(val: str | None) -> str:
        if val is None:
            return ""
        s = str(val)
        s = s.replace('"', '""')
        s = s.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        if any(c in s for c in [',', '"', '\n', '\r']):
            return f'"{s}"'
        return s

    Path("./out").mkdir(parents=True, exist_ok=True)

    cols = data.get('cols', [])
    rows = data.get('rows', [])
    out = [",".join(escape_csv(col) for col in cols)]

    for row in rows:
        out.append(",".join(escape_csv(item) for item in row))

    with open(f"out/{product_id}.csv", "w", encoding="utf-8") as f:
        text = "\n".join(out)
        for pattern, repl in REGEX_REPLACEMENTS.items():
            text = pattern.sub(repl, text)
        f.write(text)

    print("Done.", flush=True)

for i, product_id in enumerate(product_ids):
    if len(sys.argv) > 1:
        if i >= int(sys.argv[1]):
            break
    download_data(product_id)

df_list = [pd.read_csv(f) for f in Path("./out").rglob("*.csv")]
combined_df = pd.concat(df_list, ignore_index=True, sort=False).astype(str)
combined_df.to_parquet("database/products.parquet", index=False, compression=None)

def get_cols() -> list[str]:
    omit_list = ["EAN / UPC / JAN", "Model", "Machine Type", "TopSeller", "Monitor Cable", "Controls", "Others", "ISV Certifications", "Base Warranty", "Other Certifications", "Included Upgrade", "End of Support", "Announce Date"]
    return [col for col in combined_df.columns.to_list() if col not in omit_list]

column_names = get_cols()

def get_distinct_values(column_names: list[str]) -> dict[str, list[str]]:
    return {col: combined_df[col].dropna().unique().tolist() for col in column_names}

distinct_values_dict = get_distinct_values(column_names)

def create_filter_values_table(distinct_values: dict[str, list[str]]) -> None:
    filter_values_list = [
        {"column_name": col, "options": json.dumps(values)}
        for col, values in distinct_values.items()
    ]
    pd.DataFrame(filter_values_list).to_parquet("database/filter_values.parquet", index=False, compression=None)

create_filter_values_table(distinct_values_dict)


filter_df = pd.read_parquet("database/filter_values.parquet")
filter_df = filter_df[~filter_df['column_name'].isin(['Region', "Screen-to-Body Ratio", 'Optical', 'Docking', 'Included Upgrade', 'Announce Date', 'Standard Ports', 'Operating System', 'Dimensions (WxDxH)', 'Product', 'End of Support'])]
filter: Iterator[tuple[str, list[str]]] = filter_df.itertuples(index=False, name=None)

filter_dict: dict[str, list[str]] = {}
for column, options in filter:
    val: list[str] = json.loads(options)
    # sort values and remove empty strings
    val = sorted([v for v in val if v])
    val = [v for v in val if v.lower() != 'nan']
    filter_dict[column] = val

with open('finder/src/routes/data.ts', 'w') as f:
    f.write("export const filters = ")
    f.write(json.dumps(filter_dict, indent=4))


## type definitions

class ShowModel(TypedDict):
	cols: list[str]
	rows: list[list[str]]


class ProductInfo(TypedDict):
	href: NotRequired[str]
	MarketingName: NotRequired[str]
	isNewProduct: NotRequired[bool]
	ProductID: NotRequired[str]
	ConfigLastUpdateTime: NotRequired[str]
	SpecLastUpdateTime: NotRequired[str]

class ProductIDs(TypedDict):
	id: str
	name: str
	type: str
	subcollection: list["ProductIDs"] # recursive type
	info: ProductInfo

# Close the WebDriver at the end of the script
driver.quit()
