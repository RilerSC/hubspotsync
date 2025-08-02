# quick_insert_check.py
"""
Verificación rápida del proceso INSERT
"""
import os
import sys
sys.path.append('.')

from db.mssql_connector import MSSQLConnector
from hubspot_client.writer import HubSpotWriter
from dotenv import load_dotenv

def quick_insert_check():
    load_dotenv()
    
    print("VERIFICACION RAPIDA DE INSERT")
    print("=" * 40)
    
    # 1. Test SQL
    try:
        db = MSSQLConnector()
        insert_data = db.get_insert_data()
        print(f"SQL: {len(insert_data)} registros de INSERT")
        
        if len(insert_data) > 0:
            sample = insert_data[0]
            cedula = sample.get('no__de_cedula', 'N/A')
            print(f"Ejemplo - Cedula: {cedula}")
        
    except Exception as e:
        print(f"Error SQL: {e}")
        return
    
    # 2. Test Mapper
    try:
        writer = HubSpotWriter(dry_run=True)
        mapped = writer.insert_field_mapper.map_contact_data(sample)
        print(f"Mapper: {len(mapped)} propiedades mapeadas")
        
    except Exception as e:
        print(f"Error Mapper: {e}")
        return
    
    # 3. Test existencia
    try:
        writer_real = HubSpotWriter(dry_run=False)
        contact = writer_real.find_contact_by_cedula(cedula)
        
        if contact:
            print(f"HubSpot: Contacto YA EXISTE (ID: {contact.id})")
        else:
            print(f"HubSpot: Contacto NO EXISTE - se puede crear")
            
    except Exception as e:
        print(f"Error HubSpot: {e}")
        return
    
    print("VERIFICACION COMPLETADA")

if __name__ == "__main__":
    quick_insert_check()
