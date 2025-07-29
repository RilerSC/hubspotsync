import requests
import os
from dotenv import load_dotenv
from tabulate import tabulate
import pandas as pd

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
BASE_URL = "https://api.hubapi.com"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_ticket_pipelines_as_table():
    url = f"{BASE_URL}/crm/v3/pipelines/tickets"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    tabla = []
    for pipeline in data.get("results", []):
        pipeline_id = pipeline.get("id")
        pipeline_label = pipeline.get("label")
        for stage in pipeline.get("stages", []):
            tabla.append({
                "pipeline_id": pipeline_id,
                "pipeline_label": pipeline_label,
                "stage_id": stage.get("id"),
                "stage_label": stage.get("label")
            })

    return pd.DataFrame(tabla)

if __name__ == "__main__":
    df = fetch_ticket_pipelines_as_table()
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=True))
