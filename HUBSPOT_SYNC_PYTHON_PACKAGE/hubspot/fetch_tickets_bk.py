import requests
import os
from dotenv import load_dotenv

load_dotenv()
# print("🔐 TOKEN CARGADO:", os.getenv("HUBSPOT_TOKEN"))

# Lista completa de propiedades a consultar
TICKETS_PROPERTIES = [
    "ahorro",
    "ayuda_a_solicitar",
    "closed_date",
    "createdate",
    "credito_a_solicitar__general_",
    "estatus_del_caso",
    "fecha_de_vencimiento",
    "gestion",
    "hs_all_accessible_team_ids",
    "hs_all_assigned_business_unit_ids",
    "hs_all_owner_ids",
    "hs_all_team_ids",
    "hs_object_id",
    "hs_pipeline",
    "hs_pipeline_stage",
    "hs_ticket_category",
    "hs_time_in_1",
    "hs_time_in_1003044136",
    "hs_time_in_1003044137",
    "hs_time_in_1003044138",
    "hs_time_in_1003044139",
    "hs_time_in_1021621009",
    "hs_time_in_1021621010",
    "hs_time_in_1021621012",
    "hs_time_in_1059156405",
    "hs_time_in_1059156406",
    "hs_time_in_1059156407",
    "hs_time_in_1059156408",
    "hs_time_in_2",
    "hs_time_in_3",
    "hs_time_in_4",
    "hs_time_in_996931961",
    "hs_time_in_998152531",
    "hs_time_in_998152532",
    "hs_time_in_998152533",
    "hs_time_in_998152534",
    "hs_time_in_998177860",
    "hs_time_in_998177861",
    "hs_time_in_998177862",
    "hs_time_in_998177863",
    "hs_time_in_998177866",
    "hs_time_in_998177867",
    "hs_time_in_998177868",
    "hs_time_in_998177869",
    "hs_time_in_998195594",
    "hs_time_in_998195602",
    "hs_time_in_998195603",
    "hs_time_in_998208332",
    "hs_time_in_998213226",
    "hs_time_in_998213227",
    "hs_time_in_998213228",
    "hs_time_in_998213229",
    "hs_time_in_998217505",
    "hs_time_in_998225797",
    "hs_time_in_998225798",
    "hs_time_in_998225799",
    "hs_time_in_998225800",
    "hs_time_in_998232684",
    "hs_time_in_998232685",
    "hs_time_in_998232686",
    "hs_time_in_998232687",
    "hs_time_in_998232694",
    "hs_time_in_998232695",
    "hs_time_in_998232696",
    "hs_time_in_998232697",
    "hs_v2_latest_time_in_1",
    "hs_v2_latest_time_in_1003044136",
    "hs_v2_latest_time_in_1003044137",
    "hs_v2_latest_time_in_1003044138",
    "hs_v2_latest_time_in_1003044139",
    "hs_v2_latest_time_in_1021621009",
    "hs_v2_latest_time_in_1021621010",
    "hs_v2_latest_time_in_1021621012",
    "hs_v2_latest_time_in_1059156405",
    "hs_v2_latest_time_in_1059156406",
    "hs_v2_latest_time_in_1059156407",
    "hs_v2_latest_time_in_1059156408",
    "hs_v2_latest_time_in_4",
    "hs_v2_latest_time_in_996931961",
    "hs_v2_latest_time_in_998152531",
    "hs_v2_latest_time_in_998152532",
    "hs_v2_latest_time_in_998152533",
    "hs_v2_latest_time_in_998152534",
    "hs_v2_latest_time_in_998177860",
    "hs_v2_latest_time_in_998177861",
    "hs_v2_latest_time_in_998177862",
    "hs_v2_latest_time_in_998177863",
    "hs_v2_latest_time_in_998177866",
    "hs_v2_latest_time_in_998177867",
    "hs_v2_latest_time_in_998177868",
    "hs_v2_latest_time_in_998177869",
    "hs_v2_latest_time_in_998195594",
    "hs_v2_latest_time_in_998195602",
    "hs_v2_latest_time_in_998195603",
    "hs_v2_latest_time_in_998208332",
    "hs_v2_latest_time_in_998213226",
    "hs_v2_latest_time_in_998213227",
    "hs_v2_latest_time_in_998213228",
    "hs_v2_latest_time_in_998213229",
    "hs_v2_latest_time_in_998217505",
    "hs_v2_latest_time_in_998225797",
    "hs_v2_latest_time_in_998225798",
    "hs_v2_latest_time_in_998225799",
    "hs_v2_latest_time_in_998225800",
    "hs_v2_latest_time_in_998232684",
    "hs_v2_latest_time_in_998232685",
    "hs_v2_latest_time_in_998232686",
    "hs_v2_latest_time_in_998232687",
    "hs_v2_latest_time_in_998232694",
    "hs_v2_latest_time_in_998232695",
    "hs_v2_latest_time_in_998232696",
    "hs_v2_latest_time_in_998232697",
    "hubspot_owner_assigneddate",
    "hubspot_owner_id",
    "hubspot_team_id",
    "monto_a_liquidar",
    "monto_adicional",
    "monto_aprobado",
    "monto_original",
    "monto_polizas",
    "monto_renovado",
    "motivo_de_la_certificacion",
    "no_cert__inversion",
    "nombre_del_convenio",
    "nuevo_total"
]

def fetch_tickets_from_hubspot():
    url = "https://api.hubapi.com/crm/v3/objects/tickets"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    params_base = [("limit", 100)] + [("properties", prop) for prop in TICKETS_PROPERTIES]
    all_deals = []
    after = None

    while True:
        params = params_base.copy()
        if after:
            params.append(("after", after))

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("❌ Error:", response.status_code)
            print(response.text)
            response.raise_for_status()

        data = response.json()
        deals = data.get("results", [])
        all_deals.extend(deals)

        paging = data.get("paging")
        if paging and paging.get("next") and paging["next"].get("after"):
            after = paging["next"]["after"]
        else:
            break

    return all_deals