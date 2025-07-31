# hubspot_client/writer.py
"""
Cliente para escribir datos en HubSpot usando la API oficial v3
"""
import time
from typing import List, Dict, Any, Optional, Tuple
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput, BatchInputSimplePublicObjectBatchInputForCreate
from hubspot.crm.contacts.exceptions import ApiException

from config.settings import settings
from utils.logger import get_logger
from .field_mapper import HubSpotFieldMapper

class HubSpotWriter:
    """Cliente para escribir contactos en HubSpot"""
    
    def __init__(self, dry_run: bool = False):
        self.logger = get_logger('hubspot_sync.api')
        self.hubspot_client = HubSpot(access_token=settings.HUBSPOT_TOKEN)
        self.field_mapper = HubSpotFieldMapper()
        self.batch_size = min(settings.BATCH_SIZE, 100)  # HubSpot limita a 100 por batch
        self.dry_run = dry_run  # Modo de prueba sin escribir datos
        
        if self.dry_run:
            self.logger.info("🧪 MODO DRY-RUN ACTIVADO - No se escribirán datos reales")
        
    def test_connection(self) -> bool:
        """
        Prueba la conexión con HubSpot
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            self.logger.info("🧪 Probando conexión con HubSpot...")
            
            # Intentar obtener información básica de la cuenta
            response = self.hubspot_client.crm.contacts.basic_api.get_page(limit=1)
            
            self.logger.info("✅ Conexión con HubSpot exitosa")
            return True
            
        except ApiException as e:
            self.logger.error(f"❌ Error de API de HubSpot: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error al conectar con HubSpot: {str(e)}")
            return False
    
    def contact_exists(self, cedula: str) -> Optional[str]:
        """
        Verifica si un contacto existe en HubSpot por número de cédula
        
        Args:
            cedula: Número de cédula del contacto
            
        Returns:
            ID del contacto si existe, None si no existe
        """
        try:
            # En modo dry-run, simular búsqueda (siempre devolver None para simular contactos nuevos)
            if self.dry_run:
                # Simular que algunos contactos existen (los que terminan en números pares)
                exists = cedula and len(cedula) > 0 and cedula[-1] in ['0', '2', '4', '6', '8']
                if exists:
                    fake_id = f"existing_{cedula}"
                    self.logger.debug(f"🧪 [DRY-RUN] Contacto simulado como existente - Cédula: {cedula}")
                    return fake_id
                else:
                    self.logger.debug(f"🧪 [DRY-RUN] Contacto simulado como nuevo - Cédula: {cedula}")
                    return None
            
            # Buscar contacto por cédula usando la API de búsqueda
            search_request = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "no__de_cedula",
                                "operator": "EQ",
                                "value": cedula
                            }
                        ]
                    }
                ],
                "limit": 1
            }
            
            response = self.hubspot_client.crm.contacts.search_api.do_search(
                public_object_search_request=search_request
            )
            
            if response.results:
                contact_id = response.results[0].id
                self.logger.debug(f"Contacto encontrado con cédula {cedula}: ID {contact_id}")
                return contact_id
            
            return None
            
        except ApiException as e:
            if e.status == 404:
                return None
            self.logger.error(f"Error al buscar contacto con cédula {cedula}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error inesperado al buscar contacto {cedula}: {str(e)}")
            return None
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """
        Crea un nuevo contacto en HubSpot
        
        Args:
            contact_data: Datos del contacto desde SQL Server
            
        Returns:
            ID del contacto creado o None si falló
        """
        try:
            # Mapear datos a formato HubSpot
            hubspot_properties = self.field_mapper.map_contact_data(contact_data)
            
            if not hubspot_properties.get('no__de_cedula'):
                self.logger.warning(f"Contacto sin cédula válida, omitiendo: {contact_data}")
                return None
            
            # En modo dry-run, solo simular la creación
            if self.dry_run:
                cedula = hubspot_properties.get('no__de_cedula')
                fake_contact_id = f"dry_run_{cedula}"
                self.logger.info(f"🧪 [DRY-RUN] Contacto que se crearía - Cédula: {cedula}, Campos: {len(hubspot_properties)}")
                self.logger.debug(f"🧪 [DRY-RUN] Propiedades: {hubspot_properties}")
                return fake_contact_id
            
            # Crear objeto de entrada para HubSpot
            simple_public_object_input = SimplePublicObjectInput(properties=hubspot_properties)
            
            # Crear contacto
            response = self.hubspot_client.crm.contacts.basic_api.create(
                simple_public_object_input=simple_public_object_input
            )
            
            contact_id = response.id
            cedula = hubspot_properties.get('no__de_cedula')
            
            self.logger.info(f"✅ Contacto creado - Cédula: {cedula}, ID: {contact_id}")
            return contact_id
            
        except ApiException as e:
            self.logger.error(f"❌ Error de API al crear contacto: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error inesperado al crear contacto: {str(e)}")
            return None
    
    def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> bool:
        """
        Actualiza un contacto existente en HubSpot
        
        Args:
            contact_id: ID del contacto en HubSpot
            contact_data: Datos actualizados del contacto
            
        Returns:
            True si la actualización fue exitosa
        """
        try:
            # Mapear datos a formato HubSpot
            hubspot_properties = self.field_mapper.map_contact_data(contact_data)
            
            # En modo dry-run, solo simular la actualización
            if self.dry_run:
                cedula = hubspot_properties.get('no__de_cedula', 'N/A')
                self.logger.info(f"🧪 [DRY-RUN] Contacto que se actualizaría - Cédula: {cedula}, ID: {contact_id}, Campos: {len(hubspot_properties)}")
                self.logger.debug(f"🧪 [DRY-RUN] Propiedades: {hubspot_properties}")
                return True
            
            # Crear objeto de entrada para actualización
            simple_public_object_input = SimplePublicObjectInput(properties=hubspot_properties)
            
            # Actualizar contacto
            response = self.hubspot_client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                simple_public_object_input=simple_public_object_input
            )
            
            cedula = hubspot_properties.get('no__de_cedula', 'N/A')
            self.logger.info(f"✅ Contacto actualizado - Cédula: {cedula}, ID: {contact_id}")
            return True
            
        except ApiException as e:
            self.logger.error(f"❌ Error de API al actualizar contacto {contact_id}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error inesperado al actualizar contacto {contact_id}: {str(e)}")
            return False
    
    def create_contacts_batch(self, contacts_data: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Crea múltiples contactos en lote
        
        Args:
            contacts_data: Lista de datos de contactos
            
        Returns:
            Tupla (exitosos, fallidos)
        """
        if not contacts_data:
            return 0, 0
        
        self.logger.info(f"🔄 Creando lote de {len(contacts_data)} contactos...")
        
        # Preparar datos para batch
        batch_inputs = []
        for contact_data in contacts_data:
            hubspot_properties = self.field_mapper.map_contact_data(contact_data)
            
            # Solo incluir contactos con cédula válida
            if hubspot_properties.get('no__de_cedula'):
                batch_input = SimplePublicObjectInput(properties=hubspot_properties)
                batch_inputs.append(batch_input)
        
        if not batch_inputs:
            self.logger.warning("❌ No hay contactos válidos para crear en lote")
            return 0, len(contacts_data)
        
        # En modo dry-run, solo simular la creación en lote
        if self.dry_run:
            self.logger.info(f"🧪 [DRY-RUN] Lote que se crearía - Contactos válidos: {len(batch_inputs)}")
            for i, batch_input in enumerate(batch_inputs[:3]):  # Mostrar solo los primeros 3 como ejemplo
                self.logger.debug(f"🧪 [DRY-RUN] Contacto {i+1}: {batch_input.properties}")
            if len(batch_inputs) > 3:
                self.logger.debug(f"🧪 [DRY-RUN] ... y {len(batch_inputs) - 3} contactos más")
            return len(batch_inputs), 0
        
        try:
            # Crear lote
            batch_input_request = BatchInputSimplePublicObjectBatchInputForCreate(inputs=batch_inputs)
            response = self.hubspot_client.crm.contacts.batch_api.create(
                batch_input_simple_public_object_batch_input_for_create=batch_input_request
            )
            
            successful = len(response.results) if response.results else 0
            failed = len(batch_inputs) - successful
            
            self.logger.info(f"✅ Lote completado - Exitosos: {successful}, Fallidos: {failed}")
            return successful, failed
            
        except ApiException as e:
            self.logger.error(f"❌ Error de API en creación por lotes: {e}")
            return 0, len(batch_inputs)
        except Exception as e:
            self.logger.error(f"❌ Error inesperado en creación por lotes: {str(e)}")
            return 0, len(batch_inputs)
    
    def process_inserts(self, insert_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Procesa todos los datos de INSERT
        
        Args:
            insert_data: Lista de contactos para insertar
            
        Returns:
            Diccionario con estadísticas de la operación
        """
        total_contacts = len(insert_data)
        self.logger.info(f"🚀 Iniciando proceso de INSERT para {total_contacts} contactos")
        
        stats = {
            'total': total_contacts,
            'processed': 0,
            'created': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Procesar en lotes
        for i in range(0, total_contacts, self.batch_size):
            batch = insert_data[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total_contacts + self.batch_size - 1) // self.batch_size
            
            self.logger.info(f"📦 Procesando lote {batch_num}/{total_batches} ({len(batch)} contactos)")
            
            # Filtrar contactos que no existen
            new_contacts = []
            for contact in batch:
                cedula = contact.get('no__de_cedula')
                if cedula:
                    # Limpiar cédula para búsqueda
                    clean_cedula = self.field_mapper._clean_cedula(str(cedula))
                    if clean_cedula and not self.contact_exists(clean_cedula):
                        new_contacts.append(contact)
                    else:
                        stats['skipped'] += 1
                        self.logger.debug(f"Contacto ya existe o cédula inválida: {cedula}")
                else:
                    stats['skipped'] += 1
                    self.logger.warning("Contacto sin cédula, omitiendo")
            
            # Crear contactos nuevos en lote
            if new_contacts:
                created, failed = self.create_contacts_batch(new_contacts)
                stats['created'] += created
                stats['errors'] += failed
            
            stats['processed'] += len(batch)
            
            # Pausa entre lotes para respetar rate limits
            if i + self.batch_size < total_contacts:
                time.sleep(0.1)
        
        self.logger.info(f"✅ Proceso INSERT completado: {stats}")
        return stats
    
    def process_updates(self, update_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Procesa todos los datos de UPDATE
        
        Args:
            update_data: Lista de contactos para actualizar
            
        Returns:
            Diccionario con estadísticas de la operación
        """
        total_contacts = len(update_data)
        self.logger.info(f"🔄 Iniciando proceso de UPDATE para {total_contacts} contactos")
        
        stats = {
            'total': total_contacts,
            'processed': 0,
            'updated': 0,
            'not_found': 0,
            'errors': 0
        }
        
        for i, contact_data in enumerate(update_data, 1):
            cedula = contact_data.get('no__de_cedula')
            
            if not cedula:
                stats['errors'] += 1
                self.logger.warning(f"Contacto {i} sin cédula, omitiendo")
                continue
            
            # Limpiar cédula
            clean_cedula = self.field_mapper._clean_cedula(str(cedula))
            if not clean_cedula:
                stats['errors'] += 1
                self.logger.warning(f"Cédula inválida en contacto {i}: {cedula}")
                continue
            
            # Verificar si el contacto existe
            contact_id = self.contact_exists(clean_cedula)
            
            if contact_id:
                # Actualizar contacto existente
                if self.update_contact(contact_id, contact_data):
                    stats['updated'] += 1
                else:
                    stats['errors'] += 1
            else:
                stats['not_found'] += 1
                self.logger.debug(f"Contacto no encontrado para actualizar - Cédula: {clean_cedula}")
            
            stats['processed'] += 1
            
            # Progreso cada 100 contactos
            if i % 100 == 0:
                self.logger.info(f"📊 Progreso UPDATE: {i}/{total_contacts} ({stats})")
            
            # Pausa para respetar rate limits
            time.sleep(0.05)
        
        self.logger.info(f"✅ Proceso UPDATE completado: {stats}")
        return stats
