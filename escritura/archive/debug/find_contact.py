#!/usr/bin/env python3
"""
Buscar el contacto 107150612 en todas las tablas disponibles
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.mssql_connector import MSSQLConnector

def find_contact_everywhere():
    """
    Busca el contacto en todas las tablas posibles
    """
    print("🔍 BUSCANDO CONTACTO 107150612 EN TODAS LAS TABLAS")
    print("=" * 60)
    
    connector = MSSQLConnector()
    
    try:
        # Listar todas las tablas que contienen 'contact' o 'hs'
        print("\n1️⃣ Listando tablas relacionadas con contactos...")
        tables_query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' 
        AND (TABLE_NAME LIKE '%contact%' OR TABLE_NAME LIKE '%hs%')
        ORDER BY TABLE_NAME
        """
        
        tables_result = connector.execute_query(tables_query)
        print(f"   📊 Tablas encontradas:")
        
        tables_to_check = []
        for table_row in tables_result:
            table_name = table_row['TABLE_NAME']
            print(f"      - {table_name}")
            tables_to_check.append(table_name)
        
        # Buscar el contacto en cada tabla
        print(f"\n2️⃣ Buscando contacto 107150612 en cada tabla...")
        
        for table_name in tables_to_check:
            try:
                # Verificar si la tabla tiene columna de cédula
                columns_query = f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}' 
                AND COLUMN_NAME IN ('no__de_cedula', 'cedula', 'numero_cedula')
                """
                
                columns_result = connector.execute_query(columns_query)
                
                if columns_result:
                    cedula_column = columns_result[0]['COLUMN_NAME']
                    
                    # Buscar el contacto
                    search_query = f"""
                    SELECT COUNT(*) as count 
                    FROM {table_name} 
                    WHERE {cedula_column} = '107150612'
                    """
                    
                    search_result = connector.execute_query(search_query)
                    count = search_result[0]['count'] if search_result else 0
                    
                    if count > 0:
                        print(f"   ✅ ENCONTRADO en {table_name}: {count} registro(s)")
                        
                        # Mostrar detalles del contacto
                        detail_query = f"""
                        SELECT TOP 1 * 
                        FROM {table_name} 
                        WHERE {cedula_column} = '107150612'
                        """
                        
                        detail_result = connector.execute_query(detail_query)
                        if detail_result:
                            contact = detail_result[0]
                            print(f"      📊 Total campos: {len(contact)}")
                            
                            # Mostrar campos importantes si existen
                            important_fields = ['firstname', 'lastname', 'email', 'estado_asociado', 'numero_asociado']
                            for field in important_fields:
                                if field in contact:
                                    print(f"      {field}: {contact[field]}")
                    else:
                        print(f"   ❌ No encontrado en {table_name}")
                else:
                    print(f"   ⚪ {table_name} - Sin columna de cédula")
                    
            except Exception as e:
                print(f"   ❌ Error en {table_name}: {str(e)[:50]}...")
                
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        connector.disconnect()

if __name__ == "__main__":
    find_contact_everywhere()
