# production_insert_full.py
"""
INSERT MASIVO COMPLETO con todos los datos de HB_INSERT.sql
Captura y reporta TODOS los errores de email duplicado para revisión manual
"""
import os
import sys
import time
import csv
from datetime import datetime
sys.path.append('.')

from hubspot_client.writer import HubSpotWriter
from db.mssql_connector import MSSQLConnector
from utils.logger import get_logger
from dotenv import load_dotenv

def production_insert_full():
    """
    INSERT masivo completo con reporte de conflictos
    """
    load_dotenv()
    
    print("=" * 80)
    print("🚀 INSERT MASIVO COMPLETO - TODOS LOS REGISTROS DE HB_INSERT.sql")
    print("=" * 80)
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Generará reporte de conflictos para revisión manual")
    print()
    
    logger = get_logger('hubspot_sync.production_insert')
    
    # 1. Obtener TODOS los datos de INSERT
    print("1. 📊 CARGANDO TODOS LOS DATOS DE INSERT...")
    
    try:
        db_connector = MSSQLConnector()
        insert_data = db_connector.get_insert_data()
        total_records = len(insert_data)
        print(f"   ✅ {total_records} registros cargados desde HB_INSERT.sql")
        
        if total_records == 0:
            print("   ❌ No hay datos para procesar")
            return False
        
    except Exception as e:
        print(f"   ❌ Error cargando datos: {e}")
        return False
    
    # 2. Inicializar el writer
    print(f"\n2. 🔧 INICIALIZANDO HUBSPOT WRITER...")
    
    try:
        writer = HubSpotWriter(dry_run=False)  # MODO REAL
        print(f"   ✅ Writer inicializado con {len(writer.insert_field_mapper.field_mapping)} campos mapeados")
        
    except Exception as e:
        print(f"   ❌ Error inicializando writer: {e}")
        return False
    
    # 3. Confirmación antes de proceder
    print(f"\n3. ⚠️ CONFIRMACIÓN MASIVA:")
    print(f"   📊 Se procesarán {total_records} registros")
    print(f"   🎯 Se crearán contactos nuevos en HubSpot")
    print(f"   📋 Se generará reporte de conflictos")
    print(f"   ⏱️ Tiempo estimado: {(total_records * 0.5) / 60:.1f} minutos")
    print()
    
    confirmation = input("   ¿Proceder con INSERT MASIVO? (CONFIRMAR): ").strip().upper()
    
    if confirmation != 'CONFIRMAR':
        print("   ❌ Operación cancelada")
        return False
    
    # 4. Ejecutar INSERT masivo con captura de conflictos
    print(f"\n4. 🚀 EJECUTANDO INSERT MASIVO...")
    
    # Preparar archivos de reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    conflict_report_file = f"insert_conflicts_{timestamp}.csv"
    success_report_file = f"insert_success_{timestamp}.csv"
    
    # Estadísticas detalladas
    stats = {
        'total': total_records,
        'processed': 0,
        'created': 0,
        'conflicts': 0,  # Email ya existe
        'already_exists': 0,  # Cédula ya existe
        'invalid': 0,
        'errors': 0,
        'conflict_details': [],
        'success_details': [],
        'error_details': []
    }
    
    # Preparar CSV de conflictos
    conflict_fieldnames = [
        'cedula', 'email', 'firstname', 'lastname', 'numero_asociado',
        'existing_hubspot_id', 'error_message', 'timestamp'
    ]
    
    success_fieldnames = [
        'cedula', 'email', 'firstname', 'lastname', 'numero_asociado',
        'new_hubspot_id', 'properties_written', 'timestamp'
    ]
    
    with open(conflict_report_file, 'w', newline='', encoding='utf-8') as conflict_file, \
         open(success_report_file, 'w', newline='', encoding='utf-8') as success_file:
        
        conflict_writer = csv.DictWriter(conflict_file, fieldnames=conflict_fieldnames)
        success_writer = csv.DictWriter(success_file, fieldnames=success_fieldnames)
        
        conflict_writer.writeheader()
        success_writer.writeheader()
        
        print(f"   📝 Reportes: {conflict_report_file} y {success_report_file}")
        print(f"   🚀 Iniciando procesamiento...")
        print()
        
        # Procesar contacto por contacto
        for i, contact_data in enumerate(insert_data, 1):
            cedula = str(contact_data.get('no__de_cedula', 'N/A'))
            email = contact_data.get('email', 'N/A')
            firstname = contact_data.get('firstname', 'N/A')
            lastname = contact_data.get('lastname', 'N/A')
            numero_asociado = contact_data.get('numero_asociado', 'N/A')
            
            # Progreso cada 100 registros
            if i % 100 == 0 or i <= 10:
                print(f"   📊 Progreso: {i}/{total_records} ({(i/total_records)*100:.1f}%) - Cédula: {cedula}")
            
            try:
                stats['processed'] += 1
                
                # 1. Validar que tiene cédula
                if not cedula or cedula == 'N/A':
                    stats['invalid'] += 1
                    continue
                
                # 2. Mapear datos
                hubspot_properties = writer.insert_field_mapper.map_contact_data(contact_data)
                
                if not hubspot_properties:
                    stats['invalid'] += 1
                    continue
                
                # 3. Verificar si YA EXISTE por cédula
                existing_contact = writer.find_contact_by_cedula(cedula)
                
                if existing_contact:
                    stats['already_exists'] += 1
                    continue
                
                # 4. Intentar crear contacto
                try:
                    success = writer._create_single_contact_with_exceptions(hubspot_properties)
                    
                    if success:
                        stats['created'] += 1
                        
                        # Registrar éxito
                        success_record = {
                            'cedula': cedula,
                            'email': email,
                            'firstname': firstname,
                            'lastname': lastname,
                            'numero_asociado': numero_asociado,
                            'new_hubspot_id': 'Created',  # Se podría obtener el ID real
                            'properties_written': len(hubspot_properties),
                            'timestamp': datetime.now().isoformat()
                        }
                        success_writer.writerow(success_record)
                        success_file.flush()  # Forzar escritura inmediata
                        stats['success_details'].append(success_record)
                        
                    else:
                        stats['errors'] += 1
                
                except Exception as create_error:
                    error_str = str(create_error)
                    
                    # Detectar conflicto de email (409)
                    if "409" in error_str and "already exists" in error_str:
                        stats['conflicts'] += 1
                        
                        # Extraer ID existente si está disponible
                        existing_id = 'Unknown'
                        if 'Existing ID: ' in error_str:
                            try:
                                existing_id = error_str.split('Existing ID: ')[1].split('"')[0]
                            except:
                                pass
                        
                        # Registrar conflicto para revisión manual
                        conflict_record = {
                            'cedula': cedula,
                            'email': email,
                            'firstname': firstname,
                            'lastname': lastname,
                            'numero_asociado': numero_asociado,
                            'existing_hubspot_id': existing_id,
                            'error_message': error_str,
                            'timestamp': datetime.now().isoformat()
                        }
                        conflict_writer.writerow(conflict_record)
                        conflict_file.flush()  # Forzar escritura inmediata
                        stats['conflict_details'].append(conflict_record)
                        
                        # Log para debugging
                        print(f"   ⚠️ Conflicto detectado - Cédula: {cedula}, Email: {email}, HubSpot ID: {existing_id}")
                        
                    else:
                        stats['errors'] += 1
                        stats['error_details'].append(f"Cédula {cedula}: {error_str}")
                
            except Exception as e:
                stats['errors'] += 1
                stats['error_details'].append(f"Cédula {cedula}: Error procesando - {str(e)}")
            
            # Flush cada 50 registros para asegurar que se escriban los datos
            if i % 50 == 0:
                success_file.flush()
                conflict_file.flush()
    
    # 5. Resumen final
    print(f"\n5. 📊 RESUMEN FINAL:")
    print(f"   📈 Total procesados: {stats['processed']}")
    print(f"   ✅ Contactos creados: {stats['created']}")
    print(f"   ⚠️ Conflictos de email: {stats['conflicts']}")
    print(f"   🔄 Ya existían (cédula): {stats['already_exists']}")
    print(f"   ❌ Inválidos: {stats['invalid']}")
    print(f"   ❌ Otros errores: {stats['errors']}")
    print()
    
    # Tasas de éxito
    if stats['processed'] > 0:
        creation_rate = (stats['created'] / stats['processed']) * 100
        conflict_rate = (stats['conflicts'] / stats['processed']) * 100
        print(f"   📈 Tasa de creación: {creation_rate:.1f}%")
        print(f"   ⚠️ Tasa de conflictos: {conflict_rate:.1f}%")
    
    # 6. Información de archivos generados
    print(f"\n6. 📋 ARCHIVOS GENERADOS:")
    print(f"   ✅ Éxitos: {success_report_file} ({stats['created']} registros)")
    print(f"   ⚠️ Conflictos: {conflict_report_file} ({stats['conflicts']} registros)")
    print()
    
    if stats['conflicts'] > 0:
        print(f"🔍 CONFLICTOS PARA REVISIÓN MANUAL:")
        print(f"   📁 Archivo: {conflict_report_file}")
        print(f"   📊 Total: {stats['conflicts']} contactos con email duplicado")
        print(f"   🎯 Acción: Revisar estos contactos en HubSpot y actualizar cédulas")
        print()
        
        # Mostrar primeros 5 conflictos
        print(f"   📋 Primeros conflictos:")
        for i, conflict in enumerate(stats['conflict_details'][:5]):
            print(f"      {i+1}. Cédula {conflict['cedula']} | Email: {conflict['email']} | ID: {conflict['existing_hubspot_id']}")
    
    print(f"\n" + "=" * 80)
    print(f"🎉 INSERT MASIVO COMPLETADO")
    print(f"=" * 80)
    
    return True

def main():
    """Función principal"""
    print("\n" + "⚠️" * 15 + " ADVERTENCIA CRÍTICA " + "⚠️" * 15)
    print("ESTE SCRIPT EJECUTARÁ INSERT MASIVO EN HUBSPOT")
    print("PROCESARÁ TODOS LOS REGISTROS DE HB_INSERT.sql")
    print("PUEDE CREAR MILES DE CONTACTOS EN HUBSPOT")
    print("⚠️" * 50)
    print()
    
    proceed = input("¿REALMENTE deseas proceder con INSERT MASIVO? (MASIVO/NO): ").strip().upper()
    
    if proceed != 'MASIVO':
        print("❌ Operación cancelada - Respuesta requerida: MASIVO")
        return False
    
    success = production_insert_full()
    
    if success:
        print("🎉 PROCESO MASIVO EXITOSO")
        print("📋 Revisar archivos de reporte para conflictos")
    else:
        print("❌ PROCESO FALLIDO")
    
    return success

if __name__ == "__main__":
    main()
