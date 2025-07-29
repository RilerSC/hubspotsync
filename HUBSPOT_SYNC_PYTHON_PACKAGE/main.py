#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                            HUBSPOT SYNC - SISTEMA PRINCIPAL
================================================================================

Archivo:            main.py
Versión Python:     3.13+ (Actualizado para máximo rendimiento)
Descripción:        Sistema principal de sincronización entre HubSpot y SQL Server.
                   Extrae datos de HubSpot (deals, tickets, contactos, owners, 
                   pipelines) y los sincroniza con una base de datos SQL Server.
                   
Funcionalidades:
    - Sincronización completa de entidades HubSpot
    - Análisis dinámico de propiedades
    - Inserción masiva optimizada sin pandas
    - Manejo de errores y fallbacks automáticos
    - Resúmenes estadísticos detallados
    - Optimizado para Python 3.13

Dependencias:
    - hubspot/fetch_*.py: Módulos de extracción de datos
    - .env: Variables de configuración
    - SQL Server con ODBC Driver 17

Autor:              Ing. Jose Ríler Solórzano Campos
Fecha de Creación:  11 de julio de 2025
Derechos de Autor:  © 2025 Jose Ríler Solórzano Campos. Todos los derechos reservados.
Licencia:           Uso exclusivo del autor. Prohibida la distribución sin autorización.

================================================================================
"""

# ==================== IMPORTS DE MÓDULOS HUBSPOT ====================
# Importa todas las funciones de extracción y procesamiento de HubSpot
from hubspot.fetch_deals import fetch_deals_from_hubspot, get_all_deal_properties_list, display_extended_summary
from hubspot.fetch_tickets import fetch_tickets_from_hubspot, get_all_ticket_properties_list, display_tickets_summary
from hubspot.fetch_tickets_pipelines import fetch_ticket_pipelines_as_table
from hubspot.fetch_deals_pipelines import fetch_deal_pipelines_as_table
from hubspot.fetch_owners import fetch_owners_as_table, display_owners_summary
from hubspot.fetch_contacts import fetch_contacts_from_hubspot, get_all_contact_properties_list

# ==================== IMPORTS ESTÁNDAR ====================
# Librerías estándar para configuración, base de datos y sistema operativo
from dotenv import load_dotenv  # Carga variables de entorno desde archivo .env
from pathlib import Path        # Manejo de rutas de archivos multiplataforma
import pyodbc                  # Conector ODBC para SQL Server
import os                      # Variables de entorno del sistema

# ==================== CONFIGURACIÓN INICIAL ====================
# Carga las variables de entorno desde el archivo .env ubicado en el directorio raíz
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# El resto del código permanece igual...
def main():
    """
    Función principal orquestadora - COMPLETAMENTE OPTIMIZADA SIN PANDAS
    """
    print("🚀 HUBSPOT SYNC - VERSIÓN OPTIMIZADA SIN PANDAS")
    print("=" * 70)
    
    # Verificar configuración
    if not verify_environment():
        return

    # ==================== 🔹 DEALS (OPTIMIZADO) 🔹 ====================
    print("\n" + "="*50)
    print("🔹 PROCESANDO DEALS")
    print("="*50)
    
    deals = fetch_deals_from_hubspot()
    DEAL_PROPERTIES_DYNAMIC = get_all_deal_properties_list()

    if deals:
        display_extended_summary(deals)
        sync_entities_direct(deals, "hb_deals", DEAL_PROPERTIES_DYNAMIC, entity_type="deals")
    else:
        print("⚠️ No se encontraron deals.")
        DEAL_PROPERTIES_DYNAMIC = []

    # ==================== 🎫 TICKETS (OPTIMIZADO) 🎫 ====================
    print("\n" + "="*50)
    print("🎫 PROCESANDO TICKETS")
    print("="*50)
    
    tickets = fetch_tickets_from_hubspot()
    TICKETS_PROPERTIES_DYNAMIC = get_all_ticket_properties_list()

    if tickets:
        display_tickets_summary(tickets)
        sync_entities_direct(tickets, "hb_tickets", TICKETS_PROPERTIES_DYNAMIC, entity_type="tickets")
    else:
        print("⚠️ No se encontraron tickets.")
        TICKETS_PROPERTIES_DYNAMIC = []

    # ==================== 👥 CONTACTS (OPTIMIZADO) 👥 ====================
    print("\n" + "="*50)
    print("👥 PROCESANDO CONTACTS")
    print("="*50)
    
    contacts = fetch_contacts_from_hubspot()
    CONTACTS_PROPERTIES_DYNAMIC = get_all_contact_properties_list()

    if contacts:
        # display_contacts_summary(contacts)  # Si tienes esta función
        sync_entities_direct(contacts, "hb_contacts", CONTACTS_PROPERTIES_DYNAMIC, entity_type="contacts")
    else:
        print("⚠️ No se encontraron contactos.")
        CONTACTS_PROPERTIES_DYNAMIC = []

    # ==================== 👨‍💼 OWNERS (OPTIMIZADO) 👨‍💼 ====================
    print("\n" + "="*50)
    print("👨‍💼 PROCESANDO OWNERS")
    print("="*50)
    
    owners_data = fetch_owners_as_table()
    if owners_data:
        display_owners_summary(owners_data)
        sync_table_data(owners_data, "hb_owners")
    else:
        print("⚠️ No se encontraron owners.")

    # ==================== 📊 PIPELINES 📊 ====================
    print("\n" + "="*50)
    print("📊 PROCESANDO PIPELINES")
    print("="*50)
    
    # Pipelines de tickets
    print("\n🎫 Pipelines de tickets...")
    tickets_pipelines_data = fetch_ticket_pipelines_as_table()
    if tickets_pipelines_data:
        sync_table_data(tickets_pipelines_data, "hb_tickets_pipeline")
    else:
        print("⚠️ No se encontraron pipelines de tickets.")

    # Pipelines de deals
    print("\n🔹 Pipelines de deals...")
    deals_pipelines_data = fetch_deal_pipelines_as_table()
    if deals_pipelines_data:
        sync_table_data(deals_pipelines_data, "hb_deals_pipeline")
    else:
        print("⚠️ No se encontraron pipelines de deals.")

    # ==================== ✅ RESUMEN FINAL ✅ ====================
    print("\n" + "="*70)
    print("✅ SINCRONIZACIÓN COMPLETA")
    print("="*70)
    
    print(f"🔹 Deals sincronizados: {len(deals)} con {len(DEAL_PROPERTIES_DYNAMIC)} propiedades")
    print(f"🎫 Tickets sincronizados: {len(tickets)} con {len(TICKETS_PROPERTIES_DYNAMIC)} propiedades")
    print(f"👥 Contactos sincronizados: {len(contacts)} con {len(CONTACTS_PROPERTIES_DYNAMIC)} propiedades")
    print(f"👨‍💼 Owners sincronizados: {len(owners_data)}")
    print(f"📊 Pipelines de tickets: {len(tickets_pipelines_data)} filas")
    print(f"📊 Pipelines de deals: {len(deals_pipelines_data)} filas")
    
    print("\n🎉 ¡Proceso completado exitosamente!")

# ==================== 🛠 FUNCIONES DE SOPORTE ====================

def verify_environment():
    """
    Verifica que todas las variables de entorno estén configuradas
    """
    required_vars = ['HUBSPOT_TOKEN', 'SQL_SERVER', 'SQL_DATABASE', 'SQL_USER', 'SQL_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ Configuración verificada correctamente")
    return True

def get_sql_connection():
    """
    Crea conexión a SQL Server
    """
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    user = os.getenv("SQL_USER")
    password = os.getenv("SQL_PASSWORD")

    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password}"
    )

def table_exists(cursor, table_name):
    """
    Verifica si una tabla existe
    """
    cursor.execute("""
        SELECT 1 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ?
    """, (table_name,))
    return cursor.fetchone() is not None

def create_table(cursor, table_name, columns):
    """
    Crea una tabla con las columnas especificadas
    """
    column_defs = ", ".join([f"[{col}] NVARCHAR(MAX)" for col in columns])
    cursor.execute(f"CREATE TABLE {table_name} ({column_defs})")

def drop_table(cursor, table_name):
    """
    Elimina una tabla si existe
    """
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# ==================== 🧩 FUNCIONES DE SINCRONIZACIÓN UNIFICADAS ====================

def sync_entities_direct(entities, table_name, properties_list, entity_type="entities"):
    """
    Sincronización directa para entities (deals, tickets, contacts) - UNIFICADA
    """
    if not entities:
        print(f"⚠️ No se encontraron {entity_type} para {table_name}.")
        return

    try:
        print(f"\n🚀 SINCRONIZACIÓN DIRECTA DE {entity_type.upper()}")
        print(f"📊 {entity_type.capitalize()}: {len(entities)}")
        print(f"📊 Propiedades: {len(properties_list)}")
        
        # Extraer propiedades de todas las entidades
        entities_data = []
        all_properties = set()
        
        for entity in entities:
            props = entity.get("properties", {})
            entities_data.append(props)
            all_properties.update(props.keys())
        
        # Usar todas las propiedades encontradas o la lista especificada
        columns = list(all_properties) if all_properties else properties_list
        print(f"📊 Columnas finales: {len(columns)}")

        conn = get_sql_connection()
        cursor = conn.cursor()

        if table_exists(cursor, table_name):
            print(f"🗑️ Borrando tabla existente '{table_name}'...")
            drop_table(cursor, table_name)
        
        print(f"📦 Creando tabla '{table_name}'...")
        create_table(cursor, table_name, columns)

        print(f"⬇️ Insertando {len(entities_data)} registros...")
        insert_entities_data(cursor, table_name, entities_data, columns, entity_type)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Sincronización directa completa para '{table_name}'.")

    except Exception as e:
        print(f"❌ Error durante la sincronización: {str(e)}")
        # Intentar sincronización manual
        sync_entities_manual(entities, table_name, entity_type)

def sync_table_data(table_data, table_name):
    """
    Función de sync para datos en formato de tabla (lista de diccionarios)
    """
    if not table_data:
        print(f"⚠️ No hay datos para {table_name}.")
        return

    try:
        print(f"\n📊 SINCRONIZANDO TABLA {table_name.upper()}")
        print(f"📊 Registros: {len(table_data)}")
        
        # Obtener columnas del primer registro
        columns = list(table_data[0].keys()) if table_data else []
        print(f"📊 Columnas: {len(columns)}")
        
        conn = get_sql_connection()
        cursor = conn.cursor()

        if table_exists(cursor, table_name):
            print(f"🗑️ Borrando tabla existente '{table_name}'...")
            drop_table(cursor, table_name)
        
        print(f"📦 Creando tabla '{table_name}'...")
        create_table(cursor, table_name, columns)
        
        print(f"⬇️ Insertando {len(table_data)} registros...")
        insert_table_data(cursor, table_name, table_data, columns)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Sincronización completa para '{table_name}'.")

    except Exception as e:
        print(f"❌ Error en sincronización: {str(e)}")

def insert_entities_data(cursor, table_name, entities_data, columns, entity_type):
    """
    Inserta datos de entidades con lógica específica por tipo
    """
    placeholders = ", ".join(["?" for _ in columns])
    columns_str = ", ".join([f"[{col}]" for col in columns])
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    for props in entities_data:
        values = []
        for col in columns:
            val = props.get(col)
            
            # Procesamiento específico por tipo de entidad
            if entity_type == "tickets" and val and "time" in col and str(val).isdigit():
                try:
                    val = int(val) / 1000  # Convertir millisegundos a segundos
                except (ValueError, TypeError):
                    pass
            
            values.append(str(val) if val is not None else None)
        
        cursor.execute(query, tuple(values))

def insert_table_data(cursor, table_name, table_data, columns):
    """
    Inserta datos de tabla genéricos
    """
    placeholders = ", ".join(["?" for _ in columns])
    columns_str = ", ".join([f"[{col}]" for col in columns])
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    for row in table_data:
        values = [str(row.get(col)) if row.get(col) is not None else None for col in columns]
        cursor.execute(query, tuple(values))

def sync_entities_manual(entities, table_name, entity_type):
    """
    Sincronización manual sin pandas como fallback
    """
    if not entities:
        return
        
    try:
        print(f"🔧 Iniciando sincronización manual para {entity_type}...")
        
        # Extraer propiedades de todas las entidades
        all_properties = set()
        entities_data = []
        
        for entity in entities:
            props = entity.get("properties", {})
            entities_data.append(props)
            all_properties.update(props.keys())
        
        columns = list(all_properties)
        
        conn = get_sql_connection()
        cursor = conn.cursor()

        if table_exists(cursor, table_name):
            drop_table(cursor, table_name)
        
        create_table(cursor, table_name, columns)
        insert_entities_data(cursor, table_name, entities_data, columns, entity_type)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Sincronización manual completa para '{table_name}'.")

    except Exception as e:
        print(f"❌ Error en sincronización manual: {str(e)}")

# ==================== 🏁 EJECUTAR SCRIPT PRINCIPAL ====================
if __name__ == "__main__":
    main()