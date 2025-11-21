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
from utils.security import validate_cedula, sanitize_string, mask_sensitive_data
from .field_mapper import HubSpotFieldMapper
from .field_mapper_insert import HubSpotInsertFieldMapper

class HubSpotWriter:
    """Cliente para escribir contactos en HubSpot"""

    def __init__(self, dry_run: bool = False):
        self.logger = get_logger('hubspot_sync.api')
        self.hubspot_client = HubSpot(access_token=settings.HUBSPOT_TOKEN)
        self.field_mapper = HubSpotFieldMapper()  # Para UPDATE
        self.insert_field_mapper = HubSpotInsertFieldMapper()  # Para INSERT
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
        # SEGURIDAD: Validar formato de cédula
        if not cedula:
            self.logger.warning("Intento de búsqueda con cédula vacía")
            return None

        # Sanitizar y validar cédula
        cedula_clean = sanitize_string(cedula, max_length=20)
        if not cedula_clean or not validate_cedula(cedula_clean):
            self.logger.warning(f"Cédula con formato inválido: {mask_sensitive_data(cedula, visible_chars=2)}")
            return None

        cedula = cedula_clean

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

    def find_contact_by_cedula(self, cedula: str):
        """
        Busca y retorna el contacto completo por número de cédula
        **SEGURIDAD:** Valida y sanitiza cédula antes de buscar

        Args:
            cedula: Número de cédula del contacto

        Returns:
            Objeto contacto de HubSpot si existe, None si no existe
        """
        # SEGURIDAD: Validar formato de cédula
        if not cedula:
            self.logger.warning("Intento de búsqueda con cédula vacía")
            return None

        # Sanitizar y validar cédula
        cedula_clean = sanitize_string(cedula, max_length=20)
        if not cedula_clean or not validate_cedula(cedula_clean):
            self.logger.warning(f"Cédula con formato inválido: {mask_sensitive_data(cedula, visible_chars=2)}")
            return None

        cedula = cedula_clean

        try:
            if self.dry_run:
                self.logger.debug(f"🧪 [DRY-RUN] Búsqueda simulada - Cédula: {mask_sensitive_data(cedula, visible_chars=2)}")
                return None

            # Buscar contacto por cédula usando la API de búsqueda
            from hubspot.crm.contacts import PublicObjectSearchRequest, Filter, FilterGroup

            # Lista completa de propiedades a solicitar (incluyendo todas las personalizadas)
            all_properties = [
                # Propiedades básicas
                "firstname", "lastname", "email", "numero_asociado", "no__de_cedula", "work_email",
                # Propiedades de estado
                "estado_del_asociado", "hubspot_owner_id",
                # Propiedades de ahorros
                "con_ahorro", "con_ahorro_economias", "con_ahorro_navideno", "con_plan_fin_de_ano",
                "con_ahorro_fondo_de_inversion", "con_ahorro_plan_vacacional", "con_ahorro_plan_aguinaldo",
                "con_ahorro_plan_bono_escolar", "con_ahorro_con_proposito", "con_ahorro_plan_futuro",
                # Propiedades de créditos
                "con_credito", "con_cred__capital_social", "con_cred__adelanto_de_pension",
                "con_cred__consumo_personal", "con_cred__salud", "con_cred__especial_al_vencimiento",
                "con_cred__facilito", "con_cred__refundicion_de_pasivos", "con_cred_vivienda_patrimonial",
                "con_cred__capitalizable_3", "con_cred__tecnologico", "con_credifacil",
                "con_cred__vivienda_cooperativa", "con_cred__multiuso", "con_cred__deuda_unica",
                "con_cred__vivienda_constructivo", "con_cred__vehiculo_nuevos", "con_cred__back_to_back",
                # Propiedades de seguros
                "con_seguro", "con_seg__apoyo_funerario", "con_seg__su_vida", "con_poliza_colectiva", "con_cesantia"
            ]

            search_request = PublicObjectSearchRequest(
                filter_groups=[
                    FilterGroup(
                        filters=[
                            Filter(
                                property_name="no__de_cedula",
                                operator="EQ",
                                value=cedula
                            )
                        ]
                    )
                ],
                properties=all_properties,
                limit=1
            )

            # Ejecutar búsqueda
            search_response = self.hubspot_client.crm.contacts.search_api.do_search(
                public_object_search_request=search_request
            )

            if search_response.results and len(search_response.results) > 0:
                contact = search_response.results[0]
                self.logger.info(f"✅ Contacto encontrado - Cédula: {cedula}, ID: {contact.id}")
                return contact
            else:
                self.logger.info(f"❌ Contacto no encontrado - Cédula: {cedula}")
                return None

        except Exception as e:
            self.logger.error(f"Error buscando contacto por cédula {cedula}: {e}")
            return None

    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """
        Crea un nuevo contacto en HubSpot
        **SEGURIDAD:** Valida y sanitiza inputs antes de procesar

        Args:
            contact_data: Datos del contacto desde SQL Server

        Returns:
            ID del contacto creado o None si falló
        """
        # SEGURIDAD: Validar que contact_data es un diccionario válido
        if not isinstance(contact_data, dict):
            self.logger.warning("Datos de contacto no son un diccionario válido")
            return None

        try:
            # Mapear datos a formato HubSpot
            hubspot_properties = self.field_mapper.map_contact_data(contact_data)

            # SEGURIDAD: Validar cédula antes de procesar
            cedula = hubspot_properties.get('no__de_cedula')
            if not cedula or not validate_cedula(cedula):
                cedula_masked = mask_sensitive_data(str(cedula), visible_chars=2) if cedula else "N/A"
                self.logger.warning(f"Contacto sin cédula válida, omitiendo: {cedula_masked}")
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

    def update_contact(self, contact_id: str, contact_data: Dict[str, Any], already_mapped: bool = False, force_all_properties: bool = True) -> bool:
        """
        Actualiza un contacto existente en HubSpot
        **SEGURIDAD:** Valida y sanitiza inputs antes de procesar

        Args:
            contact_id: ID del contacto en HubSpot
            contact_data: Datos del contacto (SQL o ya mapeados a HubSpot)
            already_mapped: Si True, los datos ya están mapeados a formato HubSpot
            force_all_properties: Si True, fuerza la asignación de TODAS las propiedades personalizadas

        Returns:
            True si la actualización fue exitosa
        """
        # SEGURIDAD: Validar contact_id y contact_data
        if not contact_id or not isinstance(contact_id, str):
            self.logger.warning("Contact ID inválido o faltante")
            return False

        if not isinstance(contact_data, dict):
            self.logger.warning("Propiedades de HubSpot no son un diccionario válido")
            return False

        # SEGURIDAD: Sanitizar contact_id
        contact_id = sanitize_string(contact_id, max_length=50)
        if not contact_id:
            self.logger.warning("Contact ID no pudo ser sanitizado")
            return False

        try:
            # Mapear datos a formato HubSpot solo si no están ya mapeados
            if already_mapped:
                hubspot_properties = contact_data.copy()
            else:
                hubspot_properties = self.field_mapper.map_contact_data(contact_data)

            # NUEVA FUNCIONALIDAD: Forzar asignación de todas las propiedades personalizadas
            if force_all_properties:
                hubspot_properties = self._ensure_all_custom_properties(hubspot_properties)

            # En modo dry-run, solo simular la actualización
            if self.dry_run:
                cedula = hubspot_properties.get('no__de_cedula', 'N/A')
                self.logger.info(f"🧪 [DRY-RUN] Contacto que se actualizaría - Cédula: {cedula}, ID: {contact_id}, Campos: {len(hubspot_properties)}")
                self.logger.debug(f"🧪 [DRY-RUN] Propiedades: {hubspot_properties}")
                return True

            # Log detallado de lo que se va a enviar
            cedula = hubspot_properties.get('no__de_cedula', 'N/A')
            self.logger.info(f"🔄 Actualizando contacto - Cédula: {cedula}, ID: {contact_id}, Propiedades: {len(hubspot_properties)}")
            self.logger.debug(f"📝 Propiedades a enviar: {hubspot_properties}")

            # Crear objeto de entrada para actualización
            simple_public_object_input = SimplePublicObjectInput(properties=hubspot_properties)

            # Actualizar contacto
            response = self.hubspot_client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                simple_public_object_input=simple_public_object_input
            )

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
        Procesa todos los datos de INSERT usando la estrategia exitosa
        NUEVA LÓGICA: Verifica contacto por contacto si existe en HubSpot antes de crear

        Args:
            insert_data: Lista de contactos para insertar desde SQL Server

        Returns:
            Diccionario con estadísticas de la operación
        """
        total_contacts = len(insert_data)
        self.logger.info(f"🚀 Iniciando proceso de INSERT para {total_contacts} contactos")
        self.logger.info("📝 Usando estrategia: verificar existencia individual + crear solo nuevos")

        stats = {
            'total': total_contacts,
            'processed': 0,
            'created': 0,
            'already_exists': 0,
            'invalid': 0,
            'errors': 0,
            'error_details': []
        }

        # Procesar contacto por contacto para verificación precisa
        for i, contact_data in enumerate(insert_data, 1):
            cedula = str(contact_data.get('no__de_cedula', 'N/A'))

            self.logger.info(f"🔍 Verificando {i}/{total_contacts}: Cédula {cedula}")

            try:
                # 1. Validar que tiene cédula
                if not cedula or cedula == 'N/A':
                    stats['invalid'] += 1
                    error_msg = f"Contacto sin cédula válida"
                    stats['error_details'].append(f"Registro {i}: {error_msg}")
                    self.logger.warning(f"   ❌ {error_msg}")
                    continue

                # 2. Mapear datos usando INSERT mapper
                hubspot_properties = self.insert_field_mapper.map_contact_data(contact_data)

                if not hubspot_properties:
                    stats['invalid'] += 1
                    error_msg = f"No se pudieron mapear datos para cédula {cedula}"
                    stats['error_details'].append(error_msg)
                    self.logger.warning(f"   ❌ {error_msg}")
                    continue

                # 3. Verificar si YA EXISTE en HubSpot (CLAVE DE LA SEPARACIÓN)
                existing_contact = self.find_contact_by_cedula(cedula)

                if existing_contact:
                    stats['already_exists'] += 1
                    self.logger.info(f"   ⚠️ Contacto {cedula} YA EXISTE en HubSpot (ID: {existing_contact.id}) - Omitiendo INSERT")
                    continue

                # 4. NO EXISTE → Crear nuevo contacto
                self.logger.debug(f"   📝 Creando nuevo contacto con {len(hubspot_properties)} propiedades")

                success = self._create_single_contact(hubspot_properties)

                if success:
                    stats['created'] += 1
                    self.logger.info(f"   ✅ Contacto {cedula} creado exitosamente")
                else:
                    stats['errors'] += 1
                    error_msg = f"Falló la creación del contacto {cedula}"
                    stats['error_details'].append(error_msg)
                    self.logger.warning(f"   ❌ {error_msg}")

            except Exception as e:
                stats['errors'] += 1
                error_msg = f"Error procesando contacto {cedula}: {str(e)}"
                stats['error_details'].append(error_msg)
                self.logger.error(f"   ❌ {error_msg}")

            stats['processed'] += 1

            # Pequeña pausa entre contactos para no sobrecargar la API
            if not self.dry_run and i < total_contacts:
                time.sleep(0.2)  # Pausa más larga para INSERT (más conservador)

            # Log de progreso cada 10 contactos
            if i % 10 == 0:
                creation_rate = (stats['created'] / stats['processed']) * 100 if stats['processed'] > 0 else 0
                self.logger.info(f"📊 Progreso: {i}/{total_contacts} procesados, {stats['created']} creados ({creation_rate:.1f}%)")

        # Estadísticas finales
        creation_rate = (stats['created'] / stats['processed']) * 100 if stats['processed'] > 0 else 0

        self.logger.info("🎉 Proceso INSERT completado:")
        self.logger.info(f"   📊 Total procesados: {stats['processed']}")
        self.logger.info(f"   ✅ Contactos creados: {stats['created']}")
        self.logger.info(f"   ⚠️ Ya existían: {stats['already_exists']}")
        self.logger.info(f"   ❌ Inválidos: {stats['invalid']}")
        self.logger.info(f"   ❌ Errores: {stats['errors']}")
        self.logger.info(f"   📈 Tasa de creación: {creation_rate:.1f}%")

        # Log de primeros errores si los hay
        if stats['error_details']:
            self.logger.warning(f"⚠️ Primeros errores encontrados:")
            for error in stats['error_details'][:5]:
                self.logger.warning(f"   {error}")
            if len(stats['error_details']) > 5:
                self.logger.warning(f"   ... y {len(stats['error_details']) - 5} errores más")

        return stats

    def _create_single_contact(self, hubspot_properties: Dict[str, Any]) -> bool:
        """
        Crea un solo contacto en HubSpot

        Args:
            hubspot_properties: Propiedades ya mapeadas para HubSpot

        Returns:
            True si la creación fue exitosa
        """
        try:
            cedula = hubspot_properties.get('no__de_cedula', 'N/A')

            # En modo dry-run, solo simular la creación
            if self.dry_run:
                self.logger.info(f"🧪 [DRY-RUN] Contacto que se crearía - Cédula: {cedula}, Campos: {len(hubspot_properties)}")
                self.logger.debug(f"🧪 [DRY-RUN] Propiedades: {hubspot_properties}")
                return True

            # Log detallado de lo que se va a enviar
            self.logger.debug(f"📝 Creando contacto - Cédula: {cedula}, Propiedades: {len(hubspot_properties)}")
            self.logger.debug(f"📝 Propiedades a enviar: {hubspot_properties}")

            # Crear objeto de entrada para HubSpot
            simple_public_object_input = SimplePublicObjectInput(properties=hubspot_properties)

            # Crear contacto usando el parámetro correcto
            response = self.hubspot_client.crm.contacts.basic_api.create(
                simple_public_object_input_for_create=simple_public_object_input
            )

            contact_id = response.id
            self.logger.info(f"✅ Contacto creado - Cédula: {cedula}, ID: {contact_id}")
            return True

        except ApiException as e:
            self.logger.error(f"❌ Error de API al crear contacto: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error inesperado al crear contacto: {str(e)}")
            return False

    def _create_single_contact_with_exceptions(self, hubspot_properties: Dict[str, Any]) -> bool:
        """
        Crea un solo contacto en HubSpot PROPAGANDO LAS EXCEPCIONES
        Para uso en scripts que necesitan manejar errores específicos como 409 (conflictos)

        Args:
            hubspot_properties: Propiedades ya mapeadas para HubSpot

        Returns:
            True si la creación fue exitosa

        Raises:
            ApiException: Errores de la API de HubSpot (incluye 409 conflicts)
            Exception: Otros errores inesperados
        """
        cedula = hubspot_properties.get('no__de_cedula', 'N/A')

        # En modo dry-run, solo simular la creación
        if self.dry_run:
            self.logger.info(f"🧪 [DRY-RUN] Contacto que se crearía - Cédula: {cedula}, Campos: {len(hubspot_properties)}")
            self.logger.debug(f"🧪 [DRY-RUN] Propiedades: {hubspot_properties}")
            return True

        # Log detallado de lo que se va a enviar
        self.logger.debug(f"📝 Creando contacto - Cédula: {cedula}, Propiedades: {len(hubspot_properties)}")
        self.logger.debug(f"📝 Propiedades a enviar: {hubspot_properties}")

        # Crear objeto de entrada para HubSpot
        simple_public_object_input = SimplePublicObjectInput(properties=hubspot_properties)

        # Crear contacto usando el parámetro correcto
        # NOTA: Las excepciones se propagan intencionalmente para manejo específico
        response = self.hubspot_client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=simple_public_object_input
        )

        contact_id = response.id
        self.logger.info(f"✅ Contacto creado - Cédula: {cedula}, ID: {contact_id}")
        return True

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

    def _ensure_all_custom_properties(self, hubspot_properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asegura que TODAS las propiedades personalizadas estén incluidas en la actualización.
        Para propiedades no presentes, asigna valores por defecto para forzar su creación.

        Args:
            hubspot_properties: Propiedades actuales a enviar

        Returns:
            Diccionario con todas las propiedades personalizadas incluidas
        """
        # LISTA COMPLETA de propiedades personalizadas que manejamos
        all_custom_properties = {
            # Propiedades boolean (checkbox) - valor por defecto 'false'
            'con_ahorro': 'false',
            'con_ahorro_economias': 'false',
            'con_ahorro_navideno': 'false',
            'con_plan_fin_de_ano': 'false',
            'con_ahorro_fondo_de_inversion': 'false',
            'con_ahorro_plan_vacacional': 'false',
            'con_ahorro_plan_aguinaldo': 'false',
            'con_ahorro_plan_bono_escolar': 'false',
            'con_ahorro_con_proposito': 'false',
            'con_ahorro_plan_futuro': 'false',
            'con_credito': 'false',
            'con_cred__capital_social': 'false',
            'con_cred__adelanto_de_pension': 'false',
            'con_cred__consumo_personal': 'false',
            'con_cred__salud': 'false',
            'con_cred__especial_al_vencimiento': 'false',
            'con_cred__facilito': 'false',
            'con_cred__refundicion_de_pasivos': 'false',
            'con_cred_vivienda_patrimonial': 'false',
            'con_cred__capitalizable_3': 'false',
            'con_cred__tecnologico': 'false',
            'con_credifacil': 'false',
            'con_cred__vivienda_cooperativa': 'false',
            'con_cred__multiuso': 'false',
            'con_cred__deuda_unica': 'false',
            'con_cred__vivienda_constructivo': 'false',
            'con_cred__vehiculo_nuevos': 'false',
            'con_cred__back_to_back': 'false',
            'con_seguro': 'false',
            'con_seg__apoyo_funerario': 'false',
            'con_seg__su_vida': 'false',
            'con_poliza_colectiva': 'false',
            'con_cesantia': 'false',

            # Propiedades select - valor por defecto None (se omiten si no tienen valor)
            'estado_del_asociado': None,
            'hubspot_owner_id': None,

            # Propiedades de texto/email - valor por defecto None
            'work_email': None,
        }

        # Crear copia de las propiedades actuales
        complete_properties = hubspot_properties.copy()

        # Agregar propiedades faltantes con valores por defecto
        added_properties = []
        for prop_name, default_value in all_custom_properties.items():
            if prop_name not in complete_properties and default_value is not None:
                complete_properties[prop_name] = default_value
                added_properties.append(prop_name)

        # Log de propiedades agregadas
        if added_properties:
            self.logger.debug(f"🔧 Propiedades agregadas con valores por defecto: {added_properties}")

        self.logger.debug(f"📝 Total propiedades finales: {len(complete_properties)} (originales: {len(hubspot_properties)}, agregadas: {len(added_properties)})")

        return complete_properties

    def process_updates(self, update_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Procesa todos los datos de UPDATE usando la estrategia exitosa
        BASADO EXACTAMENTE EN EL CÓDIGO QUE FUNCIONÓ en test_cedula_110100747.py

        Args:
            update_data: Lista de contactos para actualizar desde SQL Server

        Returns:
            Diccionario con estadísticas de la operación
        """
        total_contacts = len(update_data)
        self.logger.info(f"🚀 Iniciando proceso de UPDATE para {total_contacts} contactos")
        self.logger.info("📝 Usando estrategia EXITOSA con force_all_properties=True")

        stats = {
            'total': total_contacts,
            'processed': 0,
            'updated': 0,
            'not_found': 0,
            'errors': 0,
            'error_details': []
        }

        # Procesar contacto por contacto (más seguro para actualizaciones críticas)
        for i, contact_data in enumerate(update_data, 1):
            cedula = str(contact_data.get('no__de_cedula', 'N/A'))

            self.logger.info(f"🔄 Procesando {i}/{total_contacts}: Cédula {cedula}")

            try:
                # 1. Mapear datos (MISMO PROCESO QUE FUNCIONÓ)
                hubspot_properties = self.field_mapper.map_contact_data(contact_data)

                if not hubspot_properties:
                    stats['errors'] += 1
                    error_msg = f"No se pudieron mapear datos para cédula {cedula}"
                    stats['error_details'].append(error_msg)
                    self.logger.warning(f"   ❌ {error_msg}")
                    continue

                # 2. Buscar contacto en HubSpot (MISMO PROCESO QUE FUNCIONÓ)
                contact = self.find_contact_by_cedula(cedula)

                if not contact:
                    stats['not_found'] += 1
                    self.logger.warning(f"   ❌ Contacto no encontrado en HubSpot para cédula {cedula}")
                    continue

                # 3. Actualizar CON FORZADO DE PROPIEDADES (LA CLAVE DEL ÉXITO)
                self.logger.debug(f"   📝 Actualizando contacto ID: {contact.id} con {len(hubspot_properties)} propiedades")

                success = self.update_contact(
                    contact.id,
                    hubspot_properties,
                    already_mapped=True,
                    force_all_properties=True  # ESTO ES LO QUE FUNCIONÓ AL 100%
                )

                if success:
                    stats['updated'] += 1
                    self.logger.info(f"   ✅ Contacto {cedula} actualizado exitosamente")
                else:
                    stats['errors'] += 1
                    error_msg = f"Falló la actualización del contacto {cedula} (ID: {contact.id})"
                    stats['error_details'].append(error_msg)
                    self.logger.warning(f"   ❌ {error_msg}")

            except Exception as e:
                stats['errors'] += 1
                error_msg = f"Error procesando contacto {cedula}: {str(e)}"
                stats['error_details'].append(error_msg)
                self.logger.error(f"   ❌ {error_msg}")

            stats['processed'] += 1

            # Pequeña pausa entre contactos para no sobrecargar la API
            if not self.dry_run and i < total_contacts:
                time.sleep(0.1)

            # Log de progreso cada 10 contactos
            if i % 10 == 0:
                success_rate = (stats['updated'] / stats['processed']) * 100 if stats['processed'] > 0 else 0
                self.logger.info(f"📊 Progreso: {i}/{total_contacts} procesados, {stats['updated']} exitosos ({success_rate:.1f}%)")

        # Estadísticas finales
        success_rate = (stats['updated'] / stats['processed']) * 100 if stats['processed'] > 0 else 0

        self.logger.info("🎉 Proceso UPDATE completado:")
        self.logger.info(f"   📊 Total procesados: {stats['processed']}")
        self.logger.info(f"   ✅ Actualizaciones exitosas: {stats['updated']}")
        self.logger.info(f"   ❌ No encontrados: {stats['not_found']}")
        self.logger.info(f"   ❌ Errores: {stats['errors']}")
        self.logger.info(f"   📈 Tasa de éxito: {success_rate:.1f}%")

        # Log de primeros errores si los hay
        if stats['error_details']:
            self.logger.warning(f"⚠️ Primeros errores encontrados:")
            for error in stats['error_details'][:5]:
                self.logger.warning(f"   {error}")
            if len(stats['error_details']) > 5:
                self.logger.warning(f"   ... y {len(stats['error_details']) - 5} errores más")

        return stats
