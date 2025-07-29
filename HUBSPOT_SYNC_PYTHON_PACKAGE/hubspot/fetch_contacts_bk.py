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

# Lista de propiedades específicas que queremos obtener
CONTACT_PROPERTIES = [
    'aircall_contact_owner_email',
    'hs_all_owner_ids',
    'numero_asociado',
    'no__de_cedula',
    'estado_del_asociado',
    'hs_full_name_or_email',
    'hs_calculated_phone_number',
    'hs_whatsapp_phone_number',
    'telefono_oficina',
    'telefono_habitacion',
    'email',
    'work_email',
    'hs_additional_emails',
    'date_of_birth',
    'cantidad_de_hijos',
    'provincia',
    'canton',
    'distrito',
    'estado_civil',
    'marital_status',
    'fecha_de_tu_ingreso',
    'salario_neto_semanal_o_quincenal',
    'salario_bruto_semanal_o_quincenal',
    'institucion_en_la_que_labora',
    'oficina'
]


def fetch_contacts_from_hubspot():
    contacts = []
    endpoint = f"{BASE_URL}/crm/v3/objects/contacts"
    params = {
        "limit": 100,
        "archived": "false",
        "properties": CONTACT_PROPERTIES  # Cambiado de PROPERTIES a CONTACT_PROPERTIES
    }

    while True:
        print("🔹 Consultando contactos...")
        response = requests.get(endpoint, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
            break

        data = response.json()
        results = data.get("results", [])
        if not results:
            break

        for contact in results:
            contact_data = contact.get("properties", {})
            contact_data["id"] = contact.get("id")  # Añadimos el ID único del contacto
            contacts.append(contact_data)

        paging = data.get("paging", {}).get("next", {})
        after = paging.get("after")
        if after:
            params["after"] = after
        else:
            break

    return contacts


# ▶️ Ejecutar y mostrar como tabla
if __name__ == "__main__":
    print("🔄 Cargando contactos desde HubSpot con las propiedades específicas...")
    contacts = fetch_contacts_from_hubspot()

    if not contacts:
        print("⚠️ No se encontraron contactos.")
    else:
        print(f"✅ Contactos obtenidos: {len(contacts)}\n")
        print(tabulate(contacts[:10], headers="keys", tablefmt="fancy_grid", showindex=True))  # Muestra primeros 10