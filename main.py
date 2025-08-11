import requests
import json
import time
import os

def download_data(product_id: str):
    from dotenv import load_dotenv
    load_dotenv()
    headers = {
        'Cookie': os.getenv('COOKIE'),
    }
    if not headers['Cookie']:
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

    with open(f"out/{product_id}.csv", "w") as f:
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
    with open("product_ids.json", "w") as f:
        json.dump(IDs, f)

    return IDs

product_ids = get_product_ids()

for product_id in product_ids:
    print(f"Downloading {product_id}")
    download_data(product_id)
    time.sleep(1)
