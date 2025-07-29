import requests
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("HUBSPOT_TOKEN")

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

url = 'https://api.hubapi.com/crm/v3/properties/contacts'
all_properties = []
after = None

while True:
    params = {}
    if after:
        params["after"] = after

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    all_properties.extend(data.get("results", []))
    after = data.get("paging", {}).get("next", {}).get("after")
    if not after:
        break

print(f"🔢 Total de propiedades encontradas: {len(all_properties)}\n")
for prop in all_properties:
    print(f"🧾 {prop['name']}  |  Tipo: {prop['type']}  |  Etiqueta: {prop.get('label', '')}")