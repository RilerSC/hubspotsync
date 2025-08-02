# quick_check_110100747.py
"""
Verificación rápida del contacto 110100747
"""
import os
import sys
sys.path.append('.')

from hubspot_client.writer import HubSpotWriter
from dotenv import load_dotenv

def quick_check():
    load_dotenv()
    
    print("Verificando contacto 110100747...")
    
    writer = HubSpotWriter(dry_run=False)
    contact = writer.find_contact_by_cedula('110100747')
    
    if contact:
        print(f"ENCONTRADO - ID: {contact.id}")
        print(f"Nombre: {contact.properties.get('firstname', 'N/A')} {contact.properties.get('lastname', 'N/A')}")
        print(f"Email: {contact.properties.get('email', 'N/A')}")
        print(f"Numero asociado: {contact.properties.get('numero_asociado', 'N/A')}")
        print(f"Total propiedades: {len(contact.properties)}")
    else:
        print("NO ENCONTRADO")

if __name__ == "__main__":
    quick_check()
