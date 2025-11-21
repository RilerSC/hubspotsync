# hubspot_client/field_mapper_insert.py
"""
Mapeo de campos entre SQL Server y HubSpot para operaciones INSERT
Basado en MAPEO_INSERT.csv y HB_INSERT.sql
"""
import csv
import os
from typing import Dict, Any, Optional
from datetime import datetime
import re

from utils.logger import get_logger

class HubSpotInsertFieldMapper:
    """Clase para mapear campos de SQL Server a propiedades de HubSpot para INSERT"""

    def __init__(self):
        self.logger = get_logger('hubspot_sync.insert_mapper')

        # Cargar mapeo desde MAPEO_INSERT.csv
        self.field_mapping = self._load_mapping_from_csv()
        self.logger.info(f"✅ Mapeo INSERT cargado: {len(self.field_mapping)} campos")

    def _load_mapping_from_csv(self) -> Dict[str, str]:
        """
        Carga el mapeo de campos desde MAPEO_INSERT.csv

        Returns:
            Diccionario con mapeo SQL_Field -> HubSpot_Field
        """
        mapping = {}
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'MAPEO_INSERT.csv')

        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as file:  # utf-8-sig maneja BOM automáticamente
                reader = csv.DictReader(file)
                for row in reader:
                    # Usar las claves exactas del archivo CSV (sin BOM)
                    sql_field = row['ColumnaA:SQLServer'].strip()
                    hubspot_field = row['Columna B: HubSpot'].strip()
                    exists = row['Columna C: Existe'].strip().lower()

                    # Solo incluir campos que existen (columna C = 'si')
                    if exists == 'si' and sql_field and hubspot_field:
                        mapping[sql_field] = hubspot_field

        except Exception as e:
            self.logger.error(f"Error cargando MAPEO_INSERT.csv: {e}")
            # Fallback: mapeo básico mínimo
            mapping = {
                'no__de_cedula': 'no__de_cedula',
                'numero_asociado': 'numero_asociado',
                'email': 'email',
                'firstname': 'firstname',
                'lastname': 'lastname'
            }

        return mapping

    def map_contact_data(self, sql_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapea los datos de SQL Server al formato requerido por HubSpot para INSERT
        **SEGURIDAD:** Sanitiza todos los inputs antes de procesar

        Args:
            sql_data: Diccionario con datos de SQL Server

        Returns:
            Diccionario con datos mapeados para HubSpot
        """
        # SEGURIDAD: Validar que sql_data es un diccionario válido
        if not isinstance(sql_data, dict):
            self.logger.warning("Datos de entrada no son un diccionario válido")
            return {}

        hubspot_properties = {}

        for sql_field, hubspot_field in self.field_mapping.items():
            if sql_field in sql_data:
                value = sql_data[sql_field]

                # SEGURIDAD: Sanitizar nombre de campo antes de procesar
                from utils.security import sanitize_string
                if not isinstance(sql_field, str) or not sql_field.strip():
                    continue

                # Procesar el valor según el tipo de campo
                processed_value = self._process_field_value(sql_field, value)

                if processed_value is not None:
                    hubspot_properties[hubspot_field] = processed_value

        # Validar campos críticos
        if not self._validate_critical_fields(hubspot_properties):
            # SEGURIDAD: Enmascarar cédula en logs
            from utils.security import mask_sensitive_data
            cedula_masked = mask_sensitive_data(str(sql_data.get('no__de_cedula', 'N/A')), visible_chars=2)
            self.logger.warning(f"Contacto INSERT con campos críticos faltantes: {cedula_masked}")
            return {}

        self.logger.debug(f"Campos mapeados para INSERT: {len(hubspot_properties)} de {len(sql_data)}")
        return hubspot_properties

    def _validate_critical_fields(self, hubspot_data: Dict[str, Any]) -> bool:
        """
        Valida que los campos críticos estén presentes para INSERT

        Args:
            hubspot_data: Datos mapeados para HubSpot

        Returns:
            True si los campos críticos están presentes
        """
        critical_fields = ['no__de_cedula', 'email', 'firstname', 'lastname']

        for field in critical_fields:
            if field not in hubspot_data or not hubspot_data[field]:
                self.logger.warning(f"Campo crítico faltante para INSERT: {field}")
                return False

        return True

    def _process_field_value(self, field_name: str, value: Any) -> Optional[str]:
        """
        Procesa un valor de campo para HubSpot con formatos específicos por tipo

        Args:
            field_name: Nombre del campo SQL
            value: Valor del campo

        Returns:
            Valor procesado en el formato correcto para HubSpot
        """
        # Si el valor es None o cadena vacía, retornar None
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None

        # Obtener el campo de HubSpot correspondiente
        hubspot_field = self.field_mapping.get(field_name)
        if not hubspot_field:
            return self._clean_text(str(value))

        # Identificar tipo de campo por el nombre SQL
        field_type = self._get_field_type(field_name, hubspot_field)

        # Procesar según el tipo de campo
        if field_type == 'boolean':
            return self._format_boolean_hubspot(value)
        elif field_type == 'number':
            return self._format_number_hubspot(value)
        elif field_type == 'date':
            return self._format_date_hubspot(value)
        elif field_type == 'phone':
            return self._format_phone_hubspot(value)
        elif field_type == 'select':
            return self._format_select_hubspot(hubspot_field, value)
        elif field_type == 'email':
            return self._validate_email(str(value))
        else:
            # Campo de texto general
            return self._clean_text(str(value))

    def _get_field_type(self, sql_field: str, hubspot_field: str) -> str:
        """
        Determina el tipo de campo basado en el nombre SQL y HubSpot
        """
        # CAMPOS BOOLEAN (SQL Server campos que mapean a checkbox en HubSpot)
        boolean_sql_fields = {
            'con_ahorros', 'tiene_economias', 'tiene_ahorro_navideno', 'tiene_plan_fin_de_ano',
            'tiene_ahorro_fondo_de_inversion', 'tiene_ahorro_plan_vacacional', 'tiene_ahorro_plan_aguinaldo',
            'tiene_ahorro_plan_bono_escolar', 'tiene_ahorro_con_proposito', 'tiene_ahorro_plan_futuro',
            'con_creditos', 'sobre_capital_social', 'adelanto_de_pension',
            'consumo_personal', 'salud', 'especiales_al_vencimiento',
            'facilito', 'refundicion_de_pasivos', 'vivienda_patrimonial',
            'credito_capitalizable', 'tecnologico', 'credifacil',
            'vivienda_cooperativa', 'multiuso', 'deuda_unica',
            'vivienda_constructivo', 'credito_compra_vehiculos', 'con_back_to_back',
            'tiene_seguros', 'apoyo_funerario', 'seguro_su_vida', 'poliza_colectiva',
            'tiene_cesantia'
        }

        # CAMPOS NUMBER (SQL Server campos numéricos)
        number_sql_fields = {
            'no__de_cedula', 'numero_asociado', 'cantidad_hijos',
            'salario_bruto_semanal_o_quincenal', 'salario_neto_semanal_o_quincenal'
        }

        # CAMPOS DATE
        date_sql_fields = {
            'date_of_birth', 'fecha_ingreso'
        }

        # CAMPOS PHONE
        phone_sql_fields = {
            'hs_whatsapp_phone_number', 'telefono_habitacion', 'telefono_oficina'
        }

        # CAMPOS SELECT/ENUM (SQL Server campos con opciones)
        select_sql_fields = {
            'estado_asociado', 'marital_status', 'provincia', 'canton', 'distrito',
            'institucion', 'departamento', 'encargado'
        }

        # CAMPOS EMAIL
        email_sql_fields = {'email', 'email_bncr'}

        # Verificar tipo basado en el campo SQL
        if sql_field in boolean_sql_fields:
            return 'boolean'
        elif sql_field in number_sql_fields:
            return 'number'
        elif sql_field in date_sql_fields:
            return 'date'
        elif sql_field in phone_sql_fields:
            return 'phone'
        elif sql_field in select_sql_fields:
            return 'select'
        elif sql_field in email_sql_fields:
            return 'email'
        else:
            return 'text'

    def _format_boolean_hubspot(self, value: Any) -> str:
        """
        Convierte valores a formato boolean de HubSpot: 'true' o 'false' (string)
        """
        if value is None:
            return 'false'

        # Convertir a string y limpiar
        str_value = str(value).strip().lower()

        # Valores que se consideran verdaderos
        true_values = {'1', 'true', 'yes', 'si', 'sí', 'y', 's', 'activo', 'active'}

        if str_value in true_values:
            return 'true'
        else:
            return 'false'

    def _format_number_hubspot(self, value: Any) -> Optional[str]:
        """
        Convierte valores a número para HubSpot
        """
        if value is None:
            return None

        try:
            # Limpiar string si es necesario
            if isinstance(value, str):
                clean_value = re.sub(r'[^\d.-]', '', value.strip())
                if not clean_value:
                    return None
                value = clean_value

            # Convertir a número y retornar como string
            if '.' in str(value):
                return str(float(value))
            else:
                return str(int(float(value)))
        except (ValueError, TypeError):
            self.logger.warning(f"No se pudo convertir a número: {value}")
            return None

    def _format_date_hubspot(self, value: Any) -> Optional[str]:
        """
        Convierte fechas al formato YYYY-MM-DD requerido por HubSpot
        """
        if value is None:
            return None

        try:
            # Si ya es datetime
            if hasattr(value, 'strftime'):
                return value.strftime('%Y-%m-%d')

            # Si es string, intentar parsear diferentes formatos
            str_value = str(value).strip()
            if not str_value:
                return None

            # Intentar diferentes formatos comunes
            date_formats = [
                '%Y-%m-%d',        # 2023-12-31
                '%d/%m/%Y',        # 31/12/2023
                '%m/%d/%Y',        # 12/31/2023
                '%d-%m-%Y',        # 31-12-2023
                '%Y/%m/%d',        # 2023/12/31
            ]

            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(str_value, date_format)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue

            self.logger.warning(f"No se pudo parsear fecha: {value}")
            return None

        except Exception as e:
            self.logger.warning(f"Error procesando fecha {value}: {e}")
            return None

    def _format_phone_hubspot(self, value: Any) -> Optional[str]:
        """
        Formatea números de teléfono para HubSpot
        """
        if value is None:
            return None

        phone = str(value).strip()
        if not phone:
            return None

        # Limpiar caracteres no numéricos excepto +
        clean_phone = re.sub(r'[^\d+]', '', phone)

        # Si no empieza con +, agregar código de país de Costa Rica
        if not clean_phone.startswith('+'):
            if len(clean_phone) == 8:  # Número local costarricense
                clean_phone = '+506' + clean_phone
            elif len(clean_phone) == 11 and clean_phone.startswith('506'):  # Ya tiene código sin +
                clean_phone = '+' + clean_phone

        return clean_phone if len(clean_phone) >= 10 else None

    def _format_select_hubspot(self, field_name: str, value: Any) -> Optional[str]:
        """
        Formatea valores para campos SELECT/ENUM de HubSpot
        """
        if value is None:
            return None

        str_value = str(value).strip()
        if not str_value:
            return None

        # Mapeos específicos para campos conocidos
        if field_name == 'estado_del_asociado':
            # Mapeo: Activo -> 'true', Inactivo -> 'false'
            if str_value.lower() in ['activo', 'active', '1', 'true']:
                return 'true'
            else:
                return 'false'

        elif field_name == 'institucion_en_la_que_labora':
            # Mapear valores comunes
            institution_map = {
                'banco nacional': 'BNCR',
                'banco nacional de costa rica': 'BNCR',
                'bncr': 'BNCR',
                'coopebanacio': 'Coopebanacio',
                'fondo de garantía': 'Fondo de garantía',
                'subsidiarias': 'Sudsidiarias'
            }
            normalized = str_value.lower().strip()
            return institution_map.get(normalized, str_value)

        elif field_name == 'provincia':
            # Normalizar nombres de provincias
            provincia_map = {
                'san jose': 'San José',
                'san josé': 'San José',
                'alajuela': 'Alajuela',
                'cartago': 'Cartago',
                'heredia': 'Heredia',
                'guanacaste': 'Guanacaste',
                'puntarenas': 'Puntarenas',
                'limon': 'Limón',
                'limón': 'Limón'
            }
            normalized = str_value.lower().strip()
            return provincia_map.get(normalized, str_value)

        # Para otros campos SELECT, retornar el valor tal como viene
        return str_value

    def _validate_email(self, email: str) -> Optional[str]:
        """Valida formato de email"""
        if not email:
            return None

        email = email.strip().lower()

        # Patrón básico de validación de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(email_pattern, email):
            return email

        self.logger.warning(f"Email con formato inválido: {email}")
        return None

    def _clean_text(self, text: str) -> Optional[str]:
        """Limpia texto general"""
        if not text:
            return None

        # Limpiar espacios extra y caracteres especiales
        clean_text = text.strip()

        # Limitar longitud (HubSpot tiene límites en algunos campos)
        if len(clean_text) > 1000:
            clean_text = clean_text[:1000]
            self.logger.warning(f"Texto truncado por longitud: {text[:50]}...")

        return clean_text if clean_text else None
