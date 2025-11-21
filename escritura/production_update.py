# production_update.py
"""
Proceso de actualización productivo basado en el éxito de test_cedula_110100747.py
"""
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple
sys.path.append('.')

from hubspot_client.writer import HubSpotWriter
from hubspot_client.field_mapper import HubSpotFieldMapper
from utils.logger import get_logger
from dotenv import load_dotenv
import pyodbc

class ProductionUpdater:
    """
    Clase para manejar actualizaciones productivas en HubSpot
    Basada en el código exitoso de test_cedula_110100747.py
    """

    def __init__(self, dry_run: bool = False):
        """
        Inicializar el actualizador productivo

        Args:
            dry_run: Si True, no hace cambios reales en HubSpot
        """
        load_dotenv()
        self.logger = get_logger('hubspot_sync.production')
        self.writer = HubSpotWriter(dry_run=dry_run)
        self.mapper = HubSpotFieldMapper()
        self.dry_run = dry_run

        # Configuración de SQL Server - SEGURIDAD: Usar settings centralizado
        from config.settings import settings
        self.connection_string = settings.get_sql_connection_string()

        if self.dry_run:
            self.logger.info("🧪 MODO DRY-RUN ACTIVADO - No se harán cambios reales")

    def get_update_data_from_sql(self) -> List[Dict[str, Any]]:
        """
        Obtiene los datos de actualización desde SQL Server usando HB_UPDATE.sql
        EXACTAMENTE como funcionó en el test exitoso

        Returns:
            Lista de diccionarios con datos de contactos para actualizar
        """
        self.logger.info("📊 Obteniendo datos de SQL Server usando HB_UPDATE.sql...")

        # Leer el archivo HB_UPDATE.sql (MISMO PROCESO QUE FUNCIONÓ)
        hb_update_path = os.path.join(os.path.dirname(__file__), 'HB_UPDATE.sql')

        if not os.path.exists(hb_update_path):
            raise FileNotFoundError(f"Archivo HB_UPDATE.sql no encontrado en: {hb_update_path}")

        with open(hb_update_path, 'r', encoding='utf-8') as f:
            sql_query = f.read()

        # SEGURIDAD: Validar query antes de ejecutar
        from utils.security import SecurityError
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE']
        query_upper = sql_query.upper().strip()

        # Permitir solo SELECT, INSERT, UPDATE
        if any(keyword in query_upper for keyword in dangerous_keywords):
            if not query_upper.startswith(('SELECT', 'INSERT', 'UPDATE')):
                self.logger.error("❌ Intento de ejecutar query peligrosa bloqueado")
                raise SecurityError("Query contiene comandos peligrosos no permitidos")

        # Ejecutar consulta
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()
        cursor.execute(sql_query)

        # Obtener nombres de columnas (MISMO PROCESO QUE FUNCIONÓ)
        columns = [desc[0] for desc in cursor.description]

        # Obtener todos los datos
        all_data = []
        for row_data in cursor.fetchall():
            sql_data = dict(zip(columns, row_data))
            all_data.append(sql_data)

        cursor.close()
        conn.close()

        self.logger.info(f"✅ SQL: Obtenidos {len(all_data)} registros para actualizar")
        return all_data

    def process_single_contact_update(self, sql_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Procesa la actualización de un solo contacto
        USANDO EXACTAMENTE EL MISMO PROCESO QUE FUNCIONÓ
        **SEGURIDAD:** Valida y sanitiza inputs antes de procesar

        Args:
            sql_data: Datos del contacto desde SQL Server

        Returns:
            Tuple (éxito, mensaje)
        """
        # SEGURIDAD: Validar que sql_data es un diccionario válido
        if not isinstance(sql_data, dict):
            return False, "Datos de entrada no son un diccionario válido"

        # SEGURIDAD: Sanitizar y validar cédula
        from utils.security import validate_cedula, sanitize_string, mask_sensitive_data
        cedula_raw = sql_data.get('no__de_cedula', 'N/A')
        cedula = sanitize_string(str(cedula_raw), max_length=20) if cedula_raw else 'N/A'

        if not cedula or cedula == 'N/A' or not validate_cedula(cedula):
            cedula_masked = mask_sensitive_data(cedula, visible_chars=2) if cedula != 'N/A' else 'N/A'
            return False, f"Cédula inválida o faltante: {cedula_masked}"

        try:
            # 1. Mapear datos (MISMO PROCESO QUE FUNCIONÓ)
            hubspot_data = self.mapper.map_contact_data(sql_data)

            if not hubspot_data:
                return False, f"No se pudieron mapear datos para cédula {cedula}"

            # 2. Buscar contacto en HubSpot (MISMO PROCESO QUE FUNCIONÓ)
            contact = self.writer.find_contact_by_cedula(cedula)
            if not contact:
                return False, f"Contacto no encontrado en HubSpot para cédula {cedula}"

            # 3. Actualizar CON FORZADO DE PROPIEDADES (LA CLAVE DEL ÉXITO)
            success = self.writer.update_contact(
                contact.id,
                hubspot_data,
                already_mapped=True,
                force_all_properties=True  # ESTO ES LO QUE FUNCIONÓ
            )

            if success:
                return True, f"Contacto {cedula} actualizado exitosamente"
            else:
                return False, f"Falló la actualización del contacto {cedula}"

        except Exception as e:
            error_msg = f"Error procesando contacto {cedula}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def process_batch_updates(self, batch_data: List[Dict[str, Any]], batch_num: int) -> Dict[str, Any]:
        """
        Procesa un lote de actualizaciones

        Args:
            batch_data: Lista de datos de contactos para el lote
            batch_num: Número del lote

        Returns:
            Estadísticas del lote procesado
        """
        self.logger.info(f"🔄 Procesando lote {batch_num}: {len(batch_data)} contactos")

        stats = {
            'batch_number': batch_num,
            'total_contacts': len(batch_data),
            'successful_updates': 0,
            'failed_updates': 0,
            'errors': []
        }

        for i, sql_data in enumerate(batch_data, 1):
            cedula = str(sql_data.get('no__de_cedula', 'N/A'))

            self.logger.debug(f"  📝 Procesando {i}/{len(batch_data)}: Cédula {cedula}")

            success, message = self.process_single_contact_update(sql_data)

            if success:
                stats['successful_updates'] += 1
                self.logger.debug(f"    ✅ {message}")
            else:
                stats['failed_updates'] += 1
                stats['errors'].append(f"Cédula {cedula}: {message}")
                self.logger.warning(f"    ❌ {message}")

            # Pequeña pausa entre contactos para no sobrecargar la API
            if not self.dry_run:
                time.sleep(0.1)

        # Estadísticas del lote
        success_rate = (stats['successful_updates'] / stats['total_contacts']) * 100
        self.logger.info(f"✅ Lote {batch_num} completado: {stats['successful_updates']}/{stats['total_contacts']} exitosos ({success_rate:.1f}%)")

        return stats

    def run_production_update(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Ejecuta el proceso completo de actualización productiva

        Args:
            batch_size: Tamaño de cada lote de procesamiento

        Returns:
            Estadísticas completas del proceso
        """
        start_time = datetime.now()
        self.logger.info("🚀 INICIANDO ACTUALIZACIÓN PRODUCTIVA")
        self.logger.info(f"📊 Configuración: Lotes de {batch_size}, Dry-run: {self.dry_run}")

        try:
            # 1. Obtener datos de SQL Server
            all_update_data = self.get_update_data_from_sql()

            if not all_update_data:
                self.logger.warning("⚠️ No hay datos para actualizar")
                return {'status': 'no_data', 'message': 'No hay datos para actualizar'}

            # 2. Procesar en lotes
            total_contacts = len(all_update_data)
            total_batches = (total_contacts + batch_size - 1) // batch_size

            self.logger.info(f"📈 Procesando {total_contacts} contactos en {total_batches} lotes")

            # Estadísticas generales
            global_stats = {
                'start_time': start_time,
                'total_contacts': total_contacts,
                'total_batches': total_batches,
                'successful_updates': 0,
                'failed_updates': 0,
                'batch_stats': [],
                'errors': []
            }

            # Procesar cada lote
            for batch_num in range(1, total_batches + 1):
                start_idx = (batch_num - 1) * batch_size
                end_idx = min(start_idx + batch_size, total_contacts)
                batch_data = all_update_data[start_idx:end_idx]

                batch_stats = self.process_batch_updates(batch_data, batch_num)

                # Acumular estadísticas
                global_stats['successful_updates'] += batch_stats['successful_updates']
                global_stats['failed_updates'] += batch_stats['failed_updates']
                global_stats['batch_stats'].append(batch_stats)
                global_stats['errors'].extend(batch_stats['errors'])

                # Pausa entre lotes para no sobrecargar la API
                if batch_num < total_batches and not self.dry_run:
                    self.logger.info(f"⏸️ Pausa de 2 segundos antes del siguiente lote...")
                    time.sleep(2)

            # 3. Estadísticas finales
            end_time = datetime.now()
            duration = end_time - start_time
            success_rate = (global_stats['successful_updates'] / total_contacts) * 100

            global_stats['end_time'] = end_time
            global_stats['duration'] = duration
            global_stats['success_rate'] = success_rate

            # Log del resumen final
            self.logger.info("🎉 ACTUALIZACIÓN PRODUCTIVA COMPLETADA")
            self.logger.info(f"⏱️ Tiempo total: {duration}")
            self.logger.info(f"📊 Contactos procesados: {total_contacts}")
            self.logger.info(f"✅ Actualizaciones exitosas: {global_stats['successful_updates']}")
            self.logger.info(f"❌ Actualizaciones fallidas: {global_stats['failed_updates']}")
            self.logger.info(f"📈 Tasa de éxito: {success_rate:.1f}%")

            if global_stats['errors']:
                self.logger.warning(f"⚠️ Errores encontrados: {len(global_stats['errors'])}")
                for error in global_stats['errors'][:10]:  # Mostrar solo los primeros 10
                    self.logger.warning(f"   {error}")
                if len(global_stats['errors']) > 10:
                    self.logger.warning(f"   ... y {len(global_stats['errors']) - 10} errores más")

            return global_stats

        except Exception as e:
            self.logger.error(f"❌ Error crítico en actualización productiva: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'start_time': start_time,
                'end_time': datetime.now()
            }

def main():
    """Función principal para ejecutar actualizaciones productivas"""
    print("=" * 70)
    print("🏭 HUBSPOT SYNC - ACTUALIZACIÓN PRODUCTIVA")
    print("=" * 70)
    print(f"🕐 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Crear actualizador
    updater = ProductionUpdater(dry_run=False)  # Cambiar a True para modo prueba

    # Ejecutar proceso
    results = updater.run_production_update(batch_size=25)  # Lotes de 25 para ser conservadores

    print()
    print("=" * 70)
    if results.get('success_rate', 0) >= 90:
        print("🎉 ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
    elif results.get('success_rate', 0) >= 70:
        print("⚠️ ACTUALIZACIÓN COMPLETADA CON ADVERTENCIAS")
    else:
        print("❌ ACTUALIZACIÓN COMPLETADA CON ERRORES SIGNIFICATIVOS")
    print("=" * 70)

if __name__ == "__main__":
    main()
