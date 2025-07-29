import requests
import os
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
BASE_URL = "https://api.hubapi.com"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

def list_pipeline_fields():
    url = f"{BASE_URL}/settings/v3/users/teams"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    print("\n🧾 Propiedades encontradas en cada pipeline/stage:")
    for pipeline in data.get("results", []):
        print(f"\n📂 Pipeline: {pipeline.get('label')} (ID: {pipeline.get('id')})")
        for key in pipeline.keys():
            print(f"  🔹 {key}")
        for stage in pipeline.get("stages", []):
            print(f"    📄 Stage: {stage.get('label')} (ID: {stage.get('id')})")
            for skey in stage.keys():
                print(f"      - {skey}")

if __name__ == "__main__":
    list_pipeline_fields()