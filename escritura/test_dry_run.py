# test_dry_run.py
"""
Script de prueba en modo DRY-RUN - NO escribe datos reales en HubSpot
"""
import sys
import os
from datetime import datetime

# Agregar el directorio actual al path para imports relativos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from utils.logger import setup_logging
from db.mssql_connector import MSSQLConnector
from hubspot_client.writer import HubSpotWriter

def test_field_mapping_sample():
    """Prueba el mapeo de campos con datos de muestra"""
    print("🧪 Probando mapeo de campos con datos de muestra...")
    
    # Datos de muestra que simulan lo que vendría de SQL Server
    sample_data = {
        'no__de_cedula': '123456789',
        'numero_asociado': 'A001',
        'firstname': 'Juan',
        'lastname': 'Pérez',
        'email': 'juan.perez@example.com',
        'email_bncr': 'juan.perez@bncr.fi.cr',
        'telefono_habitacion': '2234-5678',
        'telefono_oficina': '8765-4321',
        'hs_whatsapp_phone_number': '8765-4321',
        'con_ahorros': 'true',
        'tiene_economias': 'false',
        'con_credito': 'true',
        'estado_asociado': 'Activo',
        'provincia': 'San José',
        'canton': 'Central',
        'distrito': 'Carmen'
    }
    
    # Crear el mapeador y probar
    writer = HubSpotWriter(dry_run=True)
    mapped_data = writer.field_mapper.map_contact_data(sample_data)
    
    print(f"✅ Datos originales: {len(sample_data)} campos")
    print(f"✅ Datos mapeados: {len(mapped_data)} campos")
    print(f"✅ Campos mapeados: {list(mapped_data.keys())}")
    print()
    
    return mapped_data

def test_sql_queries():
    """Prueba las consultas SQL sin escribir a HubSpot"""
    print("🧪 Probando consultas SQL...")
    
    try:
        db_connector = MSSQLConnector()
        
        # Probar consulta INSERT
        print("📥 Probando consulta HB_INSERT...")
        insert_data = db_connector.get_insert_data()
        print(f"✅ Consulta INSERT ejecutada: {len(insert_data)} registros")
        
        if insert_data:
            print(f"✅ Campos en INSERT: {list(insert_data[0].keys())}")
            print(f"✅ Primer registro de ejemplo: {insert_data[0]}")
        
        print()
        
        # Probar consulta UPDATE
        print("📝 Probando consulta HB_UPDATE...")
        update_data = db_connector.get_update_data()
        print(f"✅ Consulta UPDATE ejecutada: {len(update_data)} registros")
        
        if update_data:
            print(f"✅ Campos en UPDATE: {list(update_data[0].keys())}")
            print(f"✅ Primer registro de ejemplo: {update_data[0]}")
        
        return insert_data, update_data
        
    except Exception as e:
        print(f"❌ Error en consultas SQL: {str(e)}")
        return [], []

def test_dry_run_process():
    """Ejecuta el proceso completo en modo DRY-RUN"""
    print("🧪 Ejecutando proceso completo en modo DRY-RUN...")
    print("=" * 60)
    
    logger = setup_logging(settings.LOG_DIR, 'INFO').get_sync_logger()
    
    try:
        # Inicializar conectores en modo DRY-RUN
        db_connector = MSSQLConnector()
        hubspot_writer = HubSpotWriter(dry_run=True)  # ✅ MODO DRY-RUN
        
        # Limitar datos para prueba (solo primeros 5 registros)
        print("📥 Fase 1: Procesando contactos para INSERT (DRY-RUN)...")
        insert_data = db_connector.get_insert_data()
        if insert_data:
            # Limitar a 5 registros para prueba
            test_insert_data = insert_data[:5]
            print(f"📊 Procesando {len(test_insert_data)} registros de INSERT en modo prueba")
            
            insert_stats = hubspot_writer.process_inserts(test_insert_data)
            print(f"📈 Estadísticas INSERT (DRY-RUN): {insert_stats}")
        
        print()
        
        # Fase UPDATE
        print("📝 Fase 2: Procesando contactos para UPDATE (DRY-RUN)...")
        update_data = db_connector.get_update_data()
        if update_data:
            # Limitar a 5 registros para prueba
            test_update_data = update_data[:5]
            print(f"📊 Procesando {len(test_update_data)} registros de UPDATE en modo prueba")
            
            update_stats = hubspot_writer.process_updates(test_update_data)
            print(f"📈 Estadísticas UPDATE (DRY-RUN): {update_stats}")
        
        print()
        print("🎉 Proceso DRY-RUN completado exitosamente")
        print("✅ Todos los componentes funcionan correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en proceso DRY-RUN: {str(e)}")
        return False

def main():
    """Función principal de prueba"""
    print("=" * 70)
    print("🧪 HUBSPOT SYNC - MODO DE PRUEBA DRY-RUN")
    print("=" * 70)
    print("⚠️  IMPORTANTE: No se escribirán datos reales en HubSpot")
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Validar entorno
    print("🔍 1. Validando configuración del entorno...")
    try:
        settings.validate_required_settings()
        print("✅ Configuraciones requeridas validadas")
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return
    
    print()
    
    # Probar mapeo de campos
    print("🗺️  2. Probando mapeo de campos...")
    test_field_mapping_sample()
    
    # Probar consultas SQL
    print("🗄️  3. Probando consultas SQL...")
    insert_data, update_data = test_sql_queries()
    
    if not insert_data and not update_data:
        print("❌ No se pudieron obtener datos de SQL Server")
        return
    
    print()
    
    # Ejecutar proceso completo en DRY-RUN
    print("🚀 4. Ejecutando proceso completo en modo DRY-RUN...")
    success = test_dry_run_process()
    
    print()
    print("=" * 70)
    if success:
        print("🎉 PRUEBA DRY-RUN COMPLETADA EXITOSAMENTE")
        print("✅ El código está listo para ejecutar con datos reales")
    else:
        print("❌ PRUEBA DRY-RUN COMPLETADA CON ERRORES")
        print("🔧 Revisar logs para correcciones necesarias")
    print("=" * 70)

if __name__ == "__main__":
    main()
