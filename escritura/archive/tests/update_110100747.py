# update_110100747.py
"""
Actualización para contacto 110100747
"""
import os
import sys
import time
sys.path.append('.')

from hubspot_client.writer import HubSpotWriter
from hubspot_client.field_mapper import HubSpotFieldMapper
from dotenv import load_dotenv
import pyodbc

def update_110100747():
    load_dotenv()
    
    print("ACTUALIZANDO CONTACTO 110100747")
    print("=" * 40)
    
    cedula = '110100747'
    
    # 1. Obtener datos de SQL
    print("1. Obteniendo datos de SQL...")
    
    connection_string = f"""
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={os.getenv('SQL_SERVER')};
    DATABASE={os.getenv('SQL_DATABASE')};
    UID={os.getenv('SQL_USER')};
    PWD={os.getenv('SQL_PASSWORD')};
    TrustServerCertificate=yes;
    """
    
    # Leer HB_UPDATE.sql
    hb_update_path = os.path.join(os.path.dirname(__file__), 'HB_UPDATE.sql')
    with open(hb_update_path, 'r', encoding='utf-8') as f:
        sql_query = f.read()
    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute(sql_query)
    
    columns = [desc[0] for desc in cursor.description]
    
    # Buscar registro específico
    row = None
    for row_data in cursor.fetchall():
        if str(row_data[0]) == cedula:
            row = row_data
            break
    
    cursor.close()
    conn.close()
    
    if not row:
        print(f"ERROR: No encontrado en SQL")
        return
    
    sql_data = dict(zip(columns, row))
    print(f"SQL: {len(sql_data)} campos obtenidos")
    
    # 2. Mapear datos
    print("2. Mapeando datos...")
    mapper = HubSpotFieldMapper()
    hubspot_data = mapper.map_contact_data(sql_data)
    print(f"HubSpot: {len(hubspot_data)} campos mapeados")
    
    # 3. Actualizar en HubSpot
    print("3. Actualizando en HubSpot...")
    writer = HubSpotWriter(dry_run=False)
    
    contact = writer.find_contact_by_cedula(cedula)
    if not contact:
        print("ERROR: Contacto no encontrado")
        return
    
    print(f"Contacto ID: {contact.id}")
    
    # ACTUALIZAR CON FORZADO DE PROPIEDADES
    success = writer.update_contact(
        contact.id, 
        hubspot_data, 
        already_mapped=True,
        force_all_properties=True
    )
    
    print(f"Resultado: {'EXITO' if success else 'FALLO'}")
    
    if success:
        print("4. Verificando resultado...")
        time.sleep(3)
        
        updated = writer.find_contact_by_cedula(cedula)
        if updated:
            print(f"Verificado - Total propiedades: {len(updated.properties)}")
            
            # Verificar algunos campos clave
            key_fields = ['con_ahorro', 'con_credito', 'estado_del_asociado', 'work_email']
            for field in key_fields:
                expected = hubspot_data.get(field, 'N/A')
                actual = updated.properties.get(field, 'NOT_FOUND')
                status = "OK" if actual == expected else "FAIL"
                print(f"  {field}: {actual} (esperado: {expected}) [{status}]")

if __name__ == "__main__":
    update_110100747()
