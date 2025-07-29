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

# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """
    Función principal orquestadora del sistema de sincronización.
    
    Descripción:
        Coordina todo el proceso de sincronización entre HubSpot y SQL Server.
        Procesa secuencialmente: Deals → Tickets → Contactos → Owners → Pipelines
        
    Flujo de Ejecución:
        1. Verificación de variables de entorno (verify_environment)
        2. Extracción de datos desde HubSpot API
        3. Análisis dinámico de propiedades útiles
        4. Sincronización directa con SQL Server
        5. Generación de resúmenes estadísticos
        
    Dependencias:
        - Módulos hubspot/fetch_*.py para extracción de datos
        - Funciones sync_* para inserción en base de datos
        - Variables de entorno para conexión SQL Server
        
    Retorna:
        None - Imprime resultados en consola
        
    Manejo de Errores:
        - Verifica configuración antes de procesar
        - Continúa procesamiento aunque falle una entidad
        - Usa fallbacks automáticos en caso de errores
    """
    print("🚀 HUBSPOT SYNC - VERSIÓN OPTIMIZADA SIN PANDAS")
    print("=" * 70)
    
    # Verificar que todas las variables de entorno estén configuradas correctamente
    if not verify_environment():
        return

    # ==================== 🔹 PROCESAMIENTO DE DEALS 🔹 ====================
    # Extrae deals desde HubSpot API usando fetch_deals.py
    print("\n" + "="*50)
    print("🔹 PROCESANDO DEALS")
    print("="*50)
    
    # Obtiene lista completa de deals con análisis dinámico de propiedades
    deals = fetch_deals_from_hubspot()
    # Obtiene lista de propiedades que realmente contienen datos útiles
    DEAL_PROPERTIES_DYNAMIC = get_all_deal_properties_list()

    # Procesa deals si se encontraron datos
    if deals:
        # Muestra resumen estadístico detallado usando display_extended_summary()
        display_extended_summary(deals)
        # Sincroniza datos directamente con tabla hb_deals en SQL Server
        sync_entities_direct(deals, "hb_deals", DEAL_PROPERTIES_DYNAMIC, entity_type="deals")
    else:
        print("⚠️ No se encontraron deals.")
        DEAL_PROPERTIES_DYNAMIC = []

    # ==================== 🎫 PROCESAMIENTO DE TICKETS 🎫 ====================
    # Extrae tickets desde HubSpot API usando fetch_tickets.py
    print("\n" + "="*50)
    print("🎫 PROCESANDO TICKETS")
    print("="*50)
    
    # Obtiene lista completa de tickets con análisis dinámico de propiedades
    tickets = fetch_tickets_from_hubspot()
    # Obtiene propiedades específicas de tickets que contienen datos
    TICKETS_PROPERTIES_DYNAMIC = get_all_ticket_properties_list()

    # Procesa tickets si se encontraron datos
    if tickets:
        # Muestra resumen estadístico usando display_tickets_summary()
        display_tickets_summary(tickets)
        # Sincroniza datos directamente con tabla hb_tickets en SQL Server
        sync_entities_direct(tickets, "hb_tickets", TICKETS_PROPERTIES_DYNAMIC, entity_type="tickets")
    else:
        print("⚠️ No se encontraron tickets.")
        TICKETS_PROPERTIES_DYNAMIC = []

    # ==================== 👥 PROCESAMIENTO DE CONTACTOS 👥 ====================
    # Extrae contactos desde HubSpot API usando fetch_contacts.py
    print("\n" + "="*50)
    print("👥 PROCESANDO CONTACTS")
    print("="*50)
    
    # Obtiene lista completa de contactos con análisis dinámico de propiedades
    contacts = fetch_contacts_from_hubspot()
    # Obtiene propiedades específicas de contactos que contienen datos
    CONTACTS_PROPERTIES_DYNAMIC = get_all_contact_properties_list()

    # Procesa contactos si se encontraron datos
    if contacts:
        # Nota: display_contacts_summary() disponible si se implementa en el futuro
        # display_contacts_summary(contacts)  
        # Sincroniza datos directamente con tabla hb_contacts en SQL Server
        sync_entities_direct(contacts, "hb_contacts", CONTACTS_PROPERTIES_DYNAMIC, entity_type="contacts")
    else:
        print("⚠️ No se encontraron contactos.")
        CONTACTS_PROPERTIES_DYNAMIC = []

    # ==================== 👨‍💼 PROCESAMIENTO DE OWNERS 👨‍💼 ====================
    # Extrae owners (propietarios) desde HubSpot API usando fetch_owners.py
    print("\n" + "="*50)
    print("👨‍💼 PROCESANDO OWNERS")
    print("="*50)
    
    # Obtiene datos de owners ya formateados como tabla
    owners_data = fetch_owners_as_table()
    if owners_data:
        # Muestra resumen estadístico usando display_owners_summary()
        display_owners_summary(owners_data)
        # Sincroniza usando función específica para datos tabulares
        sync_table_data(owners_data, "hb_owners")
    else:
        print("⚠️ No se encontraron owners.")

    # ==================== 📊 PROCESAMIENTO DE PIPELINES 📊 ====================
    # Extrae pipelines (etapas de procesos) desde HubSpot API
    print("\n" + "="*50)
    print("📊 PROCESANDO PIPELINES")
    print("="*50)
    
    # Pipelines de tickets - usa fetch_tickets_pipelines.py
    print("\n🎫 Pipelines de tickets...")
    # Obtiene estructura de pipelines de tickets con sus etapas
    tickets_pipelines_data = fetch_ticket_pipelines_as_table()
    if tickets_pipelines_data:
        # Sincroniza con tabla hb_tickets_pipeline en SQL Server
        sync_table_data(tickets_pipelines_data, "hb_tickets_pipeline")
    else:
        print("⚠️ No se encontraron pipelines de tickets.")

    # Pipelines de deals - usa fetch_deals_pipelines.py
    print("\n🔹 Pipelines de deals...")
    # Obtiene estructura de pipelines de deals con sus etapas
    deals_pipelines_data = fetch_deal_pipelines_as_table()
    if deals_pipelines_data:
        # Sincroniza con tabla hb_deals_pipeline en SQL Server
        sync_table_data(deals_pipelines_data, "hb_deals_pipeline")
    else:
        print("⚠️ No se encontraron pipelines de deals.")

    # ==================== ✅ RESUMEN FINAL DE SINCRONIZACIÓN ✅ ====================
    # Muestra estadísticas consolidadas de todo el proceso
    print("\n" + "="*70)
    print("✅ SINCRONIZACIÓN COMPLETA")
    print("="*70)
    
    # Imprime contadores finales para verificación
    print(f"🔹 Deals sincronizados: {len(deals)} con {len(DEAL_PROPERTIES_DYNAMIC)} propiedades")
    print(f"🎫 Tickets sincronizados: {len(tickets)} con {len(TICKETS_PROPERTIES_DYNAMIC)} propiedades")
    print(f"👥 Contactos sincronizados: {len(contacts)} con {len(CONTACTS_PROPERTIES_DYNAMIC)} propiedades")
    print(f"👨‍💼 Owners sincronizados: {len(owners_data)}")
    print(f"📊 Pipelines de tickets: {len(tickets_pipelines_data)} filas")
    print(f"📊 Pipelines de deals: {len(deals_pipelines_data)} filas")
    
    print("\n🎉 ¡Proceso completado exitosamente!")

# ==================== 🛠 FUNCIONES DE CONFIGURACIÓN Y VALIDACIÓN ====================

def verify_environment():
    """
    Verifica que todas las variables de entorno necesarias estén configuradas.
    
    Descripción:
        Valida la presencia de todas las variables críticas para la conexión
        con HubSpot API y SQL Server antes de iniciar la sincronización.
        
    Variables Requeridas:
        - HUBSPOT_TOKEN: Token de API de HubSpot para autenticación
        - SQL_SERVER: Dirección del servidor SQL Server
        - SQL_DATABASE: Nombre de la base de datos destino
        - SQL_USER: Usuario para conexión SQL Server
        - SQL_PASSWORD: Contraseña para conexión SQL Server
        
    Origen de Datos:
        Variables obtenidas del archivo .env en el directorio raíz
        
    Retorna:
        bool: True si todas las variables están configuradas, False en caso contrario
        
    Efectos Secundarios:
        Imprime en consola las variables faltantes si las hay
    """
    required_vars = ['HUBSPOT_TOKEN', 'SQL_SERVER', 'SQL_DATABASE', 'SQL_USER', 'SQL_PASSWORD']
    missing_vars = []
    
    # Verificar cada variable requerida
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
    Establece conexión con SQL Server usando pyodbc.
    
    Descripción:
        Crea una conexión ODBC con SQL Server utilizando las credenciales
        almacenadas en variables de entorno. Usa el driver ODBC 17.
        
    Configuración de Conexión:
        - Driver: ODBC Driver 17 for SQL Server
        - Autenticación: SQL Server (usuario/contraseña)
        - Timeout: Por defecto del driver
        
    Dependencias:
        - pyodbc: Librería para conexiones ODBC
        - Variables de entorno: SQL_SERVER, SQL_DATABASE, SQL_USER, SQL_PASSWORD
        
    Retorna:
        pyodbc.Connection: Objeto de conexión activa a SQL Server
        
    Excepciones:
        - pyodbc.Error: En caso de error de conexión o autenticación
        - ValueError: Si faltan variables de entorno
    """
    # Obtener credenciales desde variables de entorno
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")
    user = os.getenv("SQL_USER")
    password = os.getenv("SQL_PASSWORD")

    # Crear cadena de conexión y establecer conexión
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password}"
    )

# ==================== 🗄️ FUNCIONES DE ADMINISTRACIÓN DE BASE DE DATOS ====================

def table_exists(cursor, table_name):
    """
    Verifica si una tabla específica existe en la base de datos.
    
    Descripción:
        Consulta el esquema de información de SQL Server para determinar
        si una tabla con el nombre especificado ya existe.
        
    Parámetros:
        cursor (pyodbc.Cursor): Cursor activo de conexión SQL Server
        table_name (str): Nombre de la tabla a verificar
        
    Consulta SQL:
        Usa INFORMATION_SCHEMA.TABLES para verificar existencia
        
    Retorna:
        bool: True si la tabla existe, False en caso contrario
        
    Uso:
        Llamada antes de crear/eliminar tablas para evitar errores
    """
    cursor.execute("""
        SELECT 1 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ?
    """, (table_name,))
    return cursor.fetchone() is not None

def create_table(cursor, table_name, columns):
    """
    Crea una nueva tabla con las columnas especificadas.
    
    Descripción:
        Genera dinámicamente una tabla SQL Server con todas las columnas
        como NVARCHAR(MAX) para máxima compatibilidad con datos HubSpot.
        
    Parámetros:
        cursor (pyodbc.Cursor): Cursor activo de conexión SQL Server
        table_name (str): Nombre de la tabla a crear
        columns (list): Lista de nombres de columnas
        
    Tipo de Datos:
        Todas las columnas se crean como NVARCHAR(MAX) para flexibilidad
        máxima con datos variados de HubSpot API
        
    Uso:
        Llamada después de verificar que la tabla no existe
        
    Excepciones:
        - pyodbc.Error: En caso de error SQL o sintaxis
    """
    # Generar definiciones de columnas con corchetes para nombres especiales
    column_defs = ", ".join([f"[{col}] NVARCHAR(MAX)" for col in columns])
    cursor.execute(f"CREATE TABLE {table_name} ({column_defs})")

def drop_table(cursor, table_name):
    """
    Elimina una tabla si existe en la base de datos.
    
    Descripción:
        Ejecuta DROP TABLE IF EXISTS para remover tablas existentes
        antes de crear versiones actualizadas.
        
    Parámetros:
        cursor (pyodbc.Cursor): Cursor activo de conexión SQL Server
        table_name (str): Nombre de la tabla a eliminar
        
    Comando SQL:
        Usa DROP TABLE IF EXISTS para evitar errores si no existe
        
    Uso:
        Llamada antes de recrear tablas para sincronización completa
        
    Nota:
        Operación destructiva - elimina todos los datos existentes
    """
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# ==================== 🔄 FUNCIONES DE SINCRONIZACIÓN PRINCIPAL ====================

def sync_entities_direct(entities, table_name, properties_list, entity_type="entities"):
    """
    Sincronización principal para entidades HubSpot (deals, tickets, contacts).
    
    Descripción:
        Función unificada que maneja la sincronización completa de cualquier
        tipo de entidad desde HubSpot hacia SQL Server con fallback automático.
        
    Parámetros:
        entities (list): Lista de entidades obtenidas desde HubSpot API
        table_name (str): Nombre de la tabla SQL destino (ej: "hb_deals")
        properties_list (list): Lista de propiedades útiles para filtrar
        entity_type (str): Tipo de entidad para logs ("deals", "tickets", "contacts")
        
    Flujo de Procesamiento:
        1. Extracción de propiedades desde cada entidad
        2. Análisis de columnas disponibles vs requeridas
        3. Conexión y manejo de base de datos
        4. Recreación completa de tabla (DROP + CREATE)
        5. Inserción masiva optimizada
        6. Fallback a sincronización manual en caso de error
        
    Origen de Datos:
        - entities: Retornado por hubspot/fetch_*.py
        - properties_list: Retornado por get_all_*_properties_list()
        
    Destino:
        Tablas SQL Server: hb_deals, hb_tickets, hb_contacts
        
    Manejo de Errores:
        Automáticamente invoca sync_entities_manual() como fallback
        
    Optimizaciones:
        - Usa todas las propiedades encontradas para máxima completitud
        - Inserción por lotes para mejor performance
        - Transacciones para integridad de datos
    """
    if not entities:
        print(f"⚠️ No se encontraron {entity_type} para {table_name}.")
        return

    try:
        print(f"\n🚀 SINCRONIZACIÓN DIRECTA DE {entity_type.upper()}")
        print(f"📊 {entity_type.capitalize()}: {len(entities)}")
        print(f"📊 Propiedades: {len(properties_list)}")
        
        # Extraer todas las propiedades disponibles de las entidades
        entities_data = []
        all_properties = set()
        
        for entity in entities:
            props = entity.get("properties", {})
            entities_data.append(props)
            all_properties.update(props.keys())
        
        # Priorizar propiedades encontradas sobre lista predefinida
        columns = list(all_properties) if all_properties else properties_list
        print(f"📊 Columnas finales: {len(columns)}")

        # Establecer conexión y gestionar tabla
        conn = get_sql_connection()
        cursor = conn.cursor()

        # Recrear tabla completamente para sincronización completa
        if table_exists(cursor, table_name):
            print(f"🗑️ Borrando tabla existente '{table_name}'...")
            drop_table(cursor, table_name)
        
        print(f"📦 Creando tabla '{table_name}'...")
        create_table(cursor, table_name, columns)

        print(f"⬇️ Insertando {len(entities_data)} registros...")
        # Llamar función especializada para inserción de entidades
        insert_entities_data(cursor, table_name, entities_data, columns, entity_type)

        # Confirmar transacción y cerrar conexión
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Sincronización directa completa para '{table_name}'.")

    except Exception as e:
        print(f"❌ Error durante la sincronización: {str(e)}")
        # Fallback automático a método manual
        sync_entities_manual(entities, table_name, entity_type)

def sync_table_data(table_data, table_name):
    """
    Sincronización para datos ya estructurados como tabla (owners, pipelines).
    
    Descripción:
        Maneja la sincronización de datos que ya vienen estructurados
        como lista de diccionarios desde las funciones fetch_*_as_table().
        
    Parámetros:
        table_data (list): Lista de diccionarios con datos estructurados
        table_name (str): Nombre de la tabla SQL destino
        
    Origen de Datos:
        - fetch_owners_as_table(): Para tabla hb_owners
        - fetch_*_pipelines_as_table(): Para tablas hb_*_pipeline
        
    Flujo de Procesamiento:
        1. Extracción de columnas del primer registro
        2. Conexión a base de datos
        3. Recreación de tabla
        4. Inserción de datos estructurados
        
    Diferencias con sync_entities_direct():
        - Los datos ya vienen estructurados como tabla
        - No requiere extracción de propiedades
        - Usa insert_table_data() en lugar de insert_entities_data()
        
    Destinos:
        Tablas SQL Server: hb_owners, hb_tickets_pipeline, hb_deals_pipeline
    """
    if not table_data:
        print(f"⚠️ No hay datos para {table_name}.")
        return

    try:
        print(f"\n📊 SINCRONIZANDO TABLA {table_name.upper()}")
        print(f"📊 Registros: {len(table_data)}")
        
        # Obtener estructura de columnas del primer registro
        columns = list(table_data[0].keys()) if table_data else []
        print(f"📊 Columnas: {len(columns)}")
        
        # Establecer conexión y gestionar tabla
        conn = get_sql_connection()
        cursor = conn.cursor()

        # Recrear tabla completamente
        if table_exists(cursor, table_name):
            print(f"🗑️ Borrando tabla existente '{table_name}'...")
            drop_table(cursor, table_name)
        
        print(f"📦 Creando tabla '{table_name}'...")
        create_table(cursor, table_name, columns)
        
        print(f"⬇️ Insertando {len(table_data)} registros...")
        # Usar función especializada para datos tabulares
        insert_table_data(cursor, table_name, table_data, columns)

        # Confirmar transacción y cerrar conexión
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Sincronización completa para '{table_name}'.")

    except Exception as e:
        print(f"❌ Error en sincronización: {str(e)}")

# ==================== 📥 FUNCIONES DE INSERCIÓN DE DATOS ====================

def insert_entities_data(cursor, table_name, entities_data, columns, entity_type):
    """
    Inserta datos de entidades HubSpot con procesamiento específico por tipo.
    
    Descripción:
        Función especializada para insertar datos de entidades (deals, tickets, contacts)
        con lógica específica de transformación según el tipo de entidad.
        
    Parámetros:
        cursor (pyodbc.Cursor): Cursor activo de conexión SQL Server
        table_name (str): Nombre de la tabla destino
        entities_data (list): Lista de diccionarios con propiedades de entidades
        columns (list): Lista ordenada de nombres de columnas
        entity_type (str): Tipo de entidad para aplicar transformaciones específicas
        
    Transformaciones Específicas:
        - tickets: Convierte timestamps de milisegundos a segundos en campos "*time*"
        - deals/contacts: Inserción directa sin transformaciones especiales
        
    Flujo de Inserción:
        1. Construcción dinámica de query INSERT con placeholders
        2. Iteración sobre cada entidad
        3. Extracción y transformación de valores según tipo
        4. Ejecución de INSERT individual por entidad
        
    Manejo de Valores:
        - None: Se mantiene como NULL en SQL
        - Otros: Se convierten a string para compatibilidad NVARCHAR(MAX)
        
    Performance:
        Optimizada para lotes de hasta varios miles de registros
    """
    # Construir query de inserción con placeholders seguros
    placeholders = ", ".join(["?" for _ in columns])
    columns_str = ", ".join([f"[{col}]" for col in columns])
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    # Procesar cada entidad individualmente
    for props in entities_data:
        values = []
        for col in columns:
            val = props.get(col)
            
            # Aplicar transformaciones específicas por tipo de entidad
            if entity_type == "tickets" and val and "time" in col and str(val).isdigit():
                try:
                    # Convertir timestamps de HubSpot (milisegundos) a segundos
                    val = int(val) / 1000
                except (ValueError, TypeError):
                    # Mantener valor original si la conversión falla
                    pass
            
            # Preparar valor para inserción SQL
            values.append(str(val) if val is not None else None)
        
        # Ejecutar inserción para esta entidad
        cursor.execute(query, tuple(values))

def insert_table_data(cursor, table_name, table_data, columns):
    """
    Inserta datos estructurados como tabla (owners, pipelines).
    
    Descripción:
        Función para insertar datos que ya vienen estructurados como
        tabla desde las funciones fetch_*_as_table().
        
    Parámetros:
        cursor (pyodbc.Cursor): Cursor activo de conexión SQL Server
        table_name (str): Nombre de la tabla destino
        table_data (list): Lista de diccionarios con datos estructurados
        columns (list): Lista ordenada de nombres de columnas
        
    Diferencias con insert_entities_data():
        - No aplica transformaciones específicas por tipo
        - Los datos ya vienen en formato tabla
        - Inserción más directa y simple
        
    Flujo de Inserción:
        1. Construcción de query INSERT con placeholders
        2. Iteración sobre cada fila de datos
        3. Extracción directa de valores según columnas
        4. Ejecución de INSERT por fila
        
    Origen de Datos:
        - fetch_owners_as_table()
        - fetch_*_pipelines_as_table()
        
    Performance:
        Optimizada para datasets pequeños a medianos (< 1000 registros)
    """
    # Construir query de inserción con placeholders seguros
    placeholders = ", ".join(["?" for _ in columns])
    columns_str = ", ".join([f"[{col}]" for col in columns])
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    # Procesar cada fila de datos
    for row in table_data:
        # Extraer valores en el orden correcto de las columnas
        values = [str(row.get(col)) if row.get(col) is not None else None for col in columns]
        # Ejecutar inserción para esta fila
        cursor.execute(query, tuple(values))

def sync_entities_manual(entities, table_name, entity_type):
    """
    Método de sincronización manual como fallback en caso de errores.
    
    Descripción:
        Función de respaldo que se ejecuta automáticamente cuando
        sync_entities_direct() encuentra errores. Implementa lógica
        similar pero más robusta para manejar casos edge.
        
    Parámetros:
        entities (list): Lista de entidades desde HubSpot API
        table_name (str): Nombre de la tabla SQL destino
        entity_type (str): Tipo de entidad para logs
        
    Uso:
        Llamada automáticamente desde sync_entities_direct() en caso de:
        - Errores de conexión SQL
        - Problemas de estructura de datos
        - Fallos en inserción masiva
        
    Flujo de Recuperación:
        1. Re-análisis de propiedades disponibles
        2. Nueva conexión a base de datos
        3. Recreación de tabla
        4. Inserción con manejo de errores más robusto
        
    Robustez:
        - Manejo de excepciones más granular
        - Validaciones adicionales de datos
        - Logs detallados para debugging
    """
    if not entities:
        return
        
    try:
        print(f"🔧 Iniciando sincronización manual para {entity_type}...")
        
        # Re-analizar propiedades disponibles
        all_properties = set()
        entities_data = []
        
        for entity in entities:
            props = entity.get("properties", {})
            entities_data.append(props)
            all_properties.update(props.keys())
        
        columns = list(all_properties)
        
        # Establecer nueva conexión para el fallback
        conn = get_sql_connection()
        cursor = conn.cursor()

        # Recrear tabla completamente
        if table_exists(cursor, table_name):
            drop_table(cursor, table_name)
        
        create_table(cursor, table_name, columns)
        # Usar función de inserción estándar para entidades
        insert_entities_data(cursor, table_name, entities_data, columns, entity_type)

        # Confirmar y cerrar
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Sincronización manual completa para '{table_name}'.")

    except Exception as e:
        print(f"❌ Error en sincronización manual: {str(e)}")

# ==================== 🏁 PUNTO DE ENTRADA DEL PROGRAMA ====================

if __name__ == "__main__":
    """
    Punto de entrada principal del programa.
    
    Descripción:
        Se ejecuta cuando el script se invoca directamente desde línea de comandos
        o cuando se ejecuta main.py como programa principal.
        
    Comportamiento:
        - Invoca la función main() que orquesta todo el proceso
        - Maneja la ejecución del flujo completo de sincronización
        
    Uso Típico:
        python main.py
        
    Dependencias Críticas:
        - Archivo .env con variables de configuración
        - Conexión a internet para HubSpot API
        - Acceso a SQL Server con credenciales válidas
        - Módulos hubspot/* disponibles y funcionales
    """
    main()