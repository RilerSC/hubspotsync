# main.py
"""
Script principal para sincronización de datos SQL Server -> HubSpot
"""
import sys
import os
from datetime import datetime

# Agregar el directorio actual al path para imports relativos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from utils.logger import setup_logging, get_logger
from db.mssql_connector import MSSQLConnector
from hubspot_client.writer import HubSpotWriter
from hubspot_client.field_mapper import HubSpotFieldMapper

def validate_environment():
    """Valida que el entorno esté configurado correctamente"""
    print("🔍 Validando configuración del entorno...")
    
    try:
        # Validar configuraciones requeridas
        settings.validate_required_settings()
        print("✅ Configuraciones requeridas validadas")
        
        # Verificar archivos de consulta SQL
        if not os.path.exists(settings.QUERY_INSERT_FILE):
            raise FileNotFoundError(f"Archivo de consulta INSERT no encontrado: {settings.QUERY_INSERT_FILE}")
        
        if not os.path.exists(settings.QUERY_UPDATE_FILE):
            raise FileNotFoundError(f"Archivo de consulta UPDATE no encontrado: {settings.QUERY_UPDATE_FILE}")
        
        print("✅ Archivos de consulta SQL encontrados")
        return True
        
    except Exception as e:
        print(f"❌ Error en validación del entorno: {str(e)}")
        return False

def test_connections():
    """Prueba las conexiones a SQL Server y HubSpot"""
    print("🧪 Probando conexiones...")
    
    # Probar SQL Server
    with MSSQLConnector() as db:
        if not db.test_connection():
            print("❌ Error: No se pudo conectar a SQL Server")
            return False
    
    # Probar HubSpot
    hubspot_writer = HubSpotWriter()
    if not hubspot_writer.test_connection():
        print("❌ Error: No se pudo conectar a HubSpot")
        return False
    
    print("✅ Todas las conexiones funcionan correctamente")
    return True

def sync_data():
    """Ejecuta el proceso completo de sincronización usando la estrategia exitosa"""
    logger = get_logger('hubspot_sync.main')
    
    logger.info("🚀 Iniciando sincronización SQL Server -> HubSpot")
    logger.info("📝 Usando estrategia EXITOSA con force_all_properties=True")
    logger.info(f"Configuración: Lotes de {settings.BATCH_SIZE}, Debug: {settings.DEBUG_MODE}")
    
    start_time = datetime.now()
    
    try:
        # Inicializar conectores
        db_connector = MSSQLConnector()
        hubspot_writer = HubSpotWriter()
        
        # ==================== PROCESO INSERT ====================
        logger.info("📥 Fase 1: Procesando contactos para INSERT...")
        
        try:
            insert_data = db_connector.get_insert_data()
            logger.info(f"📊 Datos INSERT obtenidos: {len(insert_data)} registros")
            
            if insert_data:
                insert_stats = hubspot_writer.process_inserts(insert_data)
                logger.info(f"📈 Estadísticas INSERT: {insert_stats}")
            else:
                logger.info("ℹ️ No hay datos para INSERT")
                
        except Exception as e:
            logger.error(f"❌ Error en proceso INSERT: {str(e)}")
        
        # ==================== PROCESO UPDATE (MEJORADO) ====================
        logger.info("📝 Fase 2: Procesando contactos para UPDATE...")
        logger.info("🔧 Usando método mejorado basado en test exitoso de cédula 110100747")
        
        try:
            update_data = db_connector.get_update_data()
            logger.info(f"📊 Datos UPDATE obtenidos: {len(update_data)} registros")
            
            if update_data:
                # USAR EL NUEVO MÉTODO MEJORADO
                update_stats = hubspot_writer.process_updates(update_data)
                logger.info(f"📈 Estadísticas UPDATE: {update_stats}")
                
                # Evaluar éxito del proceso
                success_rate = update_stats.get('updated', 0) / max(update_stats.get('processed', 1), 1) * 100
                if success_rate >= 90:
                    logger.info("🎉 UPDATE completado con EXCELENTE tasa de éxito")
                elif success_rate >= 70:
                    logger.warning("⚠️ UPDATE completado con tasa de éxito aceptable")
                else:
                    logger.error("❌ UPDATE completado con baja tasa de éxito")
            else:
                logger.info("ℹ️ No hay datos para UPDATE")
                logger.info("ℹ️ No hay datos para UPDATE")
                
        except Exception as e:
            logger.error(f"❌ Error en proceso UPDATE: {str(e)}")
        
        # ==================== RESUMEN FINAL ====================
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("🎉 Sincronización completada")
        logger.info(f"⏱️ Tiempo total de ejecución: {duration}")
        logger.info(f"📅 Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📅 Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error crítico en sincronización: {str(e)}")
        return False
    
    finally:
        # Limpiar conexiones
        try:
            db_connector.disconnect()
        except:
            pass

def main():
    """Función principal"""
    print("=" * 70)
    print("📡 HUBSPOT SYNC - SINCRONIZACIÓN SQL SERVER -> HUBSPOT")
    print("=" * 70)
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Validar entorno
    if not validate_environment():
        print("❌ Falló la validación del entorno. Verifique la configuración.")
        sys.exit(1)
    
    # Probar conexiones
    if not test_connections():
        print("❌ Falló la prueba de conexiones. Verifique las credenciales.")
        sys.exit(1)
    
    print("✅ Validaciones completadas. Iniciando sincronización...")
    print()
    
    # Ejecutar sincronización
    success = sync_data()
    
    print()
    print("=" * 70)
    if success:
        print("🎉 SINCRONIZACIÓN COMPLETADA EXITOSAMENTE")
    else:
        print("❌ SINCRONIZACIÓN COMPLETADA CON ERRORES")
    print("=" * 70)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
