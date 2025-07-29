import requests
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

ACCESS_TOKEN = os.getenv("HUBSPOT_TOKEN")
BASE_URL = 'https://api.hubapi.com'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

def fetch_owners():
    owners = []
    url = f"{BASE_URL}/crm/v3/owners/"
    params = {"limit": 100}

    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
            break

        data = response.json()
        owners.extend(data.get("results", []))

        paging = data.get("paging", {}).get("next", {}).get("link")
        url = paging if paging else None  # Continúa si hay más páginas

    return owners

if __name__ == "__main__":
    print(f"🔐 TOKEN CARGADO: {ACCESS_TOKEN}")
    owners = fetch_owners()

    tabla = []
    for owner in owners:
        tabla.append({
            "ID": owner.get("id"),
            "Nombre": owner.get("firstName", "") + " " + owner.get("lastName", ""),
            "Email": owner.get("email"),
            "Activo": owner.get("active"),
            "Creado en": owner.get("createdAt")
        })

    print(tabulate(tabla, headers="keys", tablefmt="fancy_grid", showindex=True))