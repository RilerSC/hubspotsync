# verify_properties_exist.py
"""
Verificar si las propiedades personalizadas existen en HubSpot
"""
import os
import sys
sys.path.append('.')

from hubspot_client.writer import HubSpotWriter
from dotenv import load_dotenv
import requests

def verify_properties_exist():
    """
    Verificar si las propiedades existen
    """
    load_dotenv()
    
    print("VERIFICANDO EXISTENCIA DE PROPIEDADES...")
    
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Lista de propiedades a verificar
    target_fields = [
        'con_ahorro', 'con_credito', 'con_ahorro_economias', 
        'estado_del_asociado', 'work_email'
    ]
    
    print("Verificando propiedades en HubSpot API:")
    print("=" * 50)
    
    for field in target_fields:
        url = f"https://api.hubapi.com/crm/v3/properties/contacts/{field}"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                prop_data = response.json()
                print(f"{field}: EXISTS")
                print(f"  - Type: {prop_data.get('type', 'Unknown')}")
                print(f"  - Field Type: {prop_data.get('fieldType', 'Unknown')}")
                print(f"  - Label: {prop_data.get('label', 'Unknown')}")
            else:
                print(f"{field}: NOT FOUND (Status: {response.status_code})")
                
        except Exception as e:
            print(f"{field}: ERROR - {str(e)}")
        
        print()

if __name__ == "__main__":
    verify_properties_exist()
