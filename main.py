import requests
import json
import time
import os
import sys
import re
import csv
from pathlib import Path

def download_data(product_id: str):
    from dotenv import load_dotenv
    load_dotenv()
    headers = {
        'cookie': os.getenv('COOKIE'),
    }
    if not headers['cookie']:
        raise ValueError("Please set your cookie here before running.")

    url = f"https://psref.lenovo.com/api/search/DefinitionFilterAndSearch/ShowModel?pageindex=1&pagesize=300000&product_key={product_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    json_data: dict = response.json()
    data: dict = json_data.get('data')

    if not data:
        return print(f"No data found for {product_id}")

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

    with open(f"out/{product_id}.csv", "w", encoding="utf-16") as f:
        f.write("\n".join(out))

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
    json_data: dict = response.json()
    data: list[dict] = json_data.get('data')

    IDs = extract_product_ids(data[0].get('subcollection', []))
    with open("product_ids.json", "w", encoding="utf-8") as f:
        json.dump(IDs, f)

    return IDs

def postprocess():
    replacement = {
        r"(\^\|\^)?Various docking.*?</u></a>": "Various",
        r"NVIDIA (GeForce )?": "",
        r"Boost Clock ": "",
        r"TGP ": "",
        r"Integrated AMD Radeon ": "AMD Radeon ",
    }

    csv_file = Path("./out/out.csv")
    text = csv_file.read_text()
    for pattern, repl in replacement.items():
        text = re.sub(pattern, repl, text)
    csv_file.write_text(text, encoding="utf-8")

    print("Run conv2db.py next")

def merge_csv_files():
    import pandas as pd
    import glob

    output_filename = 'out.csv'
    all_files = glob.glob('./out/*.csv')
    input_files = [f for f in all_files if not f.endswith(output_filename)]

    df_list = []

    print(f"Found {len(input_files)} files to process...")
    for file in input_files:
        try:
            df = pd.read_csv(file, encoding='utf-16')
            df_list.append(df)
        except Exception as e:
            print(f"  - FAILED to process {file}. Error: {e}")

    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        combined_df.to_csv(output_filename, index=False, na_rep='', encoding='utf-16')
        print(f"\nSuccessfully combined {len(df_list)} files into {output_filename}.")
    else:
        print("\nNo valid files were processed. Output file not created.")


if "--postprocess" in sys.argv:
    print("Postprocessing only...")
    postprocess()
    sys.exit(0)

if "--merge" in sys.argv:
    print("Merging CSV files...")
    merge_csv_files()
    sys.exit(0)


for product_id in get_product_ids():
    print(f"Downloading {product_id}")
    download_data(product_id)
    # time.sleep(0.3)
