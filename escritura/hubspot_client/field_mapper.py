# hubspot_client/field_mapper.py
"""
Mapeo de campos entre SQL Server y HubSpot
"""
from typing import Dict, Any, Optional
from datetime import datetime
import re

from utils.logger import get_logger

class HubSpotFieldMapper:
    """Clase para mapear campos de SQL Server a propiedades de HubSpot"""

    def __init__(self):
        self.logger = get_logger('hubspot_sync.mapper')

        # Mapeo de campos SQL Server -> HubSpot (BASADO EN MAPEO_COLUMNAS.csv y HB_UPDATE.sql)
        self.field_mapping = {
            # Campos básicos de identificación
            'no__de_cedula': 'no__de_cedula',
            'numero_asociado': 'numero_asociado',
            'email': 'email',
            'email_bncr': 'work_email',  # CAMBIADO: de hs_additional_emails a work_email

            # Estado del asociado
            'estado_asociado': 'estado_del_asociado',

            # Productos financieros - Ahorros
            'con_ahorros': 'con_ahorro',
            'tiene_economias': 'con_ahorro_economias',
            'tiene_ahorro_navideno': 'con_ahorro_navideno',
            'tiene_plan_fin_de_ano': 'con_plan_fin_de_ano',
            'tiene_ahorro_fondo_de_inversion': 'con_ahorro_fondo_de_inversion',
            'tiene_ahorro_plan_vacacional': 'con_ahorro_plan_vacacional',
            'tiene_ahorro_plan_aguinaldo': 'con_ahorro_plan_aguinaldo',
            'tiene_ahorro_plan_bono_escolar': 'con_ahorro_plan_bono_escolar',
            'tiene_ahorro_con_proposito': 'con_ahorro_con_proposito',
            'tiene_ahorro_plan_futuro': 'con_ahorro_plan_futuro',

            # Productos financieros - Créditos
            'con_creditos': 'con_credito',
            'sobre_capital_social': 'con_cred__capital_social',
            'adelanto_de_pension': 'con_cred__adelanto_de_pension',
            'consumo_personal': 'con_cred__consumo_personal',
            'salud': 'con_cred__salud',
            'especiales_al_vencimiento': 'con_cred__especial_al_vencimiento',
            'facilito': 'con_cred__facilito',
            'refundicion_de_pasivos': 'con_cred__refundicion_de_pasivos',
            'vivienda_patrimonial': 'con_cred_vivienda_patrimonial',
            'credito_capitalizable': 'con_cred__capitalizable_3',
            'tecnologico': 'con_cred__tecnologico',
            'credifacil': 'con_credifacil',
            'vivienda_cooperativa': 'con_cred__vivienda_cooperativa',
            'multiuso': 'con_cred__multiuso',
            'deuda_unica': 'con_cred__deuda_unica',
            'vivienda_constructivo': 'con_cred__vivienda_constructivo',
            'credito_compra_vehiculos': 'con_cred__vehiculo_nuevos',
            'con_back_to_back': 'con_cred__back_to_back',

            # Productos financieros - Seguros
            'tiene_seguros': 'con_seguro',
            'apoyo_funerario': 'con_seg__apoyo_funerario',
            'seguro_su_vida': 'con_seg__su_vida',
            'poliza_colectiva': 'con_poliza_colectiva',
            'tiene_cesantia': 'con_cesantia',

            # Encargado
            'encargado': 'hubspot_owner_id',
        }

    def map_contact_data(self, sql_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapea los datos de SQL Server al formato requerido por HubSpot
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

        self.logger.debug(f"Campos mapeados: {len(hubspot_properties)} de {len(sql_data)}")
        return hubspot_properties

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
            'no__de_cedula', 'numero_asociado'
        }

        # CAMPOS SELECT/ENUM (SQL Server campos con opciones)
        select_sql_fields = {
            'email_bncr', 'estado_asociado', 'encargado'
        }

        # CAMPOS EMAIL
        email_sql_fields = {'email'}

        # Verificar tipo basado en el campo SQL
        if sql_field in boolean_sql_fields:
            return 'boolean'
        elif sql_field in number_sql_fields:
            return 'number'
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

    def _format_number_hubspot(self, value: Any) -> Optional[int]:
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

            # Convertir a número
            if '.' in str(value):
                return float(value)
            else:
                return int(float(value))
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

    def _clean_cedula(self, cedula: str) -> Optional[str]:
        """Limpia y valida número de cédula"""
        if not cedula:
            return None

        # Remover espacios, guiones y otros caracteres no numéricos
        clean_cedula = re.sub(r'[^0-9]', '', cedula)

        # Validar longitud (cédulas costarricenses suelen tener 9 dígitos)
        if len(clean_cedula) >= 8 and len(clean_cedula) <= 12:
            return clean_cedula

        self.logger.warning(f"Cédula con formato inválido: {cedula}")
        return cedula  # Retornar original si no pasa validación

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

    def _clean_phone(self, phone: str) -> Optional[str]:
        """Limpia número de teléfono"""
        if not phone:
            return None

        # Remover espacios, guiones, paréntesis
        clean_phone = re.sub(r'[^0-9+]', '', phone)

        # Si no tiene código de país, agregar +506 (Costa Rica)
        if clean_phone and not clean_phone.startswith('+'):
            if len(clean_phone) == 8:  # Número local costarricense
                clean_phone = '+506' + clean_phone

        return clean_phone if clean_phone else None

    def _format_date(self, date_value: Any) -> Optional[str]:
        """Formatea fecha para HubSpot (timestamp en milisegundos)"""
        if not date_value:
            return None

        try:
            if isinstance(date_value, datetime):
                # Convertir a timestamp en milisegundos
                timestamp_ms = int(date_value.timestamp() * 1000)
                return str(timestamp_ms)
            elif isinstance(date_value, str):
                # Intentar parsear la fecha
                dt = datetime.strptime(date_value, '%Y-%m-%d')
                timestamp_ms = int(dt.timestamp() * 1000)
                return str(timestamp_ms)
        except Exception as e:
            self.logger.warning(f"Error al formatear fecha {date_value}: {str(e)}")

        return None

    def _format_boolean(self, value: Any) -> Optional[str]:
        """Formatea valor booleano para HubSpot"""
        if value is None:
            return None

        if isinstance(value, bool):
            return 'true' if value else 'false'

        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ['true', '1', 'yes', 'sí', 'si', 'verdadero']:
                return 'true'
            elif value_lower in ['false', '0', 'no', 'falso']:
                return 'false'

        if isinstance(value, (int, float)):
            return 'true' if value != 0 else 'false'

        return None

    def _format_number(self, value: Any) -> Optional[str]:
        """Formatea valor numérico"""
        if value is None:
            return None

        try:
            if isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, str):
                # Intentar convertir string a número
                clean_value = re.sub(r'[^0-9.-]', '', value)
                if clean_value:
                    return str(float(clean_value))
        except Exception as e:
            self.logger.warning(f"Error al formatear número {value}: {str(e)}")

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
