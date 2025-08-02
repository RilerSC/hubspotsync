#!/usr/bin/env python3
"""
Buscar el contacto 107150612 en todas las tablas disponibles
"""

import sys
import os
from datetime import datetime

# Importar los módulos del proyecto
from main import get_sql_connection

def find_contact_everywhere():
    """
    Busca el contacto en todas las tablas posibles
    """
    print("🔍 BUSCANDO CONTACTO 107150612 EN TODAS LAS TABLAS")
    print("=" * 60)
    
    conn = None
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        
        # Listar todas las tablas que contienen 'contact' o 'hs'
        print("\n1️⃣ Listando tablas relacionadas con contactos...")
        tables_query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' 
        AND (TABLE_NAME LIKE '%contact%' OR TABLE_NAME LIKE '%hs%')
        ORDER BY TABLE_NAME
        """
        
        cursor.execute(tables_query)
        tables_result = cursor.fetchall()
        print(f"   📊 Tablas encontradas:")
        
        tables_to_check = []
        for table_row in tables_result:
            table_name = table_row.TABLE_NAME
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
                
                cursor.execute(columns_query)
                columns_result = cursor.fetchall()
                
                if columns_result:
                    cedula_column = columns_result[0].COLUMN_NAME
                    
                    # Buscar el contacto
                    search_query = f"""
                    SELECT COUNT(*) as count 
                    FROM {table_name} 
                    WHERE {cedula_column} = '107150612'
                    """
                    
                    cursor.execute(search_query)
                    search_result = cursor.fetchone()
                    count = search_result.count if search_result else 0
                    
                    if count > 0:
                        print(f"   ✅ ENCONTRADO en {table_name}: {count} registro(s)")
                        
                        # Mostrar detalles del contacto
                        detail_query = f"""
                        SELECT TOP 1 * 
                        FROM {table_name} 
                        WHERE {cedula_column} = '107150612'
                        """
                        
                        cursor.execute(detail_query)
                        columns = [column[0] for column in cursor.description]
                        detail_result = cursor.fetchone()
                        
                        if detail_result:
                            # Crear diccionario del contacto
                            contact = {}
                            for i, value in enumerate(detail_result):
                                contact[columns[i]] = value
                                
                            print(f"      📊 Total campos: {len(contact)}")
                            
                            # Mostrar campos importantes si existen
                            important_fields = ['firstname', 'lastname', 'email', 'estado_asociado', 'numero_asociado']
                            for field in important_fields:
                                if field in contact and contact[field]:
                                    print(f"      {field}: {contact[field]}")
                    else:
                        print(f"   ❌ No encontrado en {table_name}")
                else:
                    print(f"   ⚪ {table_name} - Sin columna de cédula")
                    
            except Exception as e:
                print(f"   ❌ Error en {table_name}: {str(e)[:50]}...")
        
        # También buscar tablas con 'insert' en el nombre
        print(f"\n3️⃣ Buscando tablas con 'insert' en el nombre...")
        insert_tables_query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' 
        AND TABLE_NAME LIKE '%insert%'
        ORDER BY TABLE_NAME
        """
        
        cursor.execute(insert_tables_query)
        insert_tables_result = cursor.fetchall()
        
        for table_row in insert_tables_result:
            table_name = table_row.TABLE_NAME
            print(f"      - {table_name}")
            
            try:
                # Verificar si tiene columna de cédula
                columns_query = f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table_name}' 
                AND COLUMN_NAME IN ('no__de_cedula', 'cedula', 'numero_cedula')
                """
                
                cursor.execute(columns_query)
                columns_result = cursor.fetchall()
                
                if columns_result:
                    cedula_column = columns_result[0].COLUMN_NAME
                    
                    # Contar registros con nuestra cédula
                    search_query = f"""
                    SELECT COUNT(*) as count 
                    FROM {table_name} 
                    WHERE {cedula_column} = '107150612'
                    """
                    
                    cursor.execute(search_query)
                    search_result = cursor.fetchone()
                    count = search_result.count if search_result else 0
                    
                    if count > 0:
                        print(f"        ✅ ENCONTRADO: {count} registro(s)")
                    else:
                        print(f"        ❌ No encontrado")
                else:
                    print(f"        ⚪ Sin columna de cédula")
                    
            except Exception as e:
                print(f"        ❌ Error: {str(e)[:50]}...")
                
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    find_contact_everywhere()
