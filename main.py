import requests
import json
import os
import sys
import re
import glob
import pandas as pd
import re

## TODO: make postprocessing more useful by splitting CPU details into separate columns
## for more granular filtering options

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

    with open(f"out/{product_id}.csv", "w", encoding="ascii") as f:
        text = "\n".join(out)
        replacement = {
            r"(\^\|\^)?Various docking.*?</u></a>": "Various",
            r"Non-WWAN": "",
            r"NVIDIA (GeForce )?": "",
            r"Boost Clock ": "",
            r"TGP ": "",
            r"None": "",
            r"RoHS compliant": "RoHS",
            r"MIL-STD-810H military test passed": "MIL-STD-810H",
            r"Integrated AMD Radeon ": "AMD Radeon ",
            r"Memory soldered to systemboard, no slots": "No Slots",
            r"microSD Card Reader": "microSD",
            r"TPM 2.0 Enabled": "TPM 2.0",
            r"1x Ethernet \(RJ-45\)": "Ethernet",
            r"100/1000M \(RJ-45\)": "1GbE",
            r"2.5GbE \(RJ-45\)": "2.5GbE",
            r"No Onboard Ethernet": "",
            r"No onboard Ethernet": "",
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
            r"Ü": "U",
            r"ü": "u",
            r"•": " | ",
            r"°": "",
            r"–": "-",
            r"≤": "<=",
            r"è": "e",
            r"\xa0": " ", # incoming data is UTF-16. so we need to strip all these out to compress them
        }
        for pattern, repl in replacement.items():
            text = re.sub(pattern, repl, text)

        # Check for non-ASCII characters
        check = set(ch for ch in text if ord(ch) > 127)
        if len(check) > 0:
            raise f"Non-ASCII characters found in {product_id}: {check}"

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
    json_data: dict = response.json()
    data: list[dict] = json_data.get('data')

    IDs = extract_product_ids(data[0].get('subcollection', []))
    with open("product_ids.json", "w", encoding="ascii") as f:
        json.dump(IDs, f)

    return IDs

for product_id in get_product_ids():
    print(f"Downloading {product_id}")
    download_data(product_id)
