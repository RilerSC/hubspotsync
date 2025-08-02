# hubspot_client/field_mapper_fixed.py
"""
Mapeo de campos entre SQL Server y HubSpot - VERSIÓN CORREGIDA
Solo incluye propiedades que realmente existen en HubSpot
"""
from typing import Dict, Any, Optional
from datetime import datetime
import re

from utils.logger import get_logger

class HubSpotFieldMapper:
    """Clase para mapear campos de SQL Server a propiedades de HubSpot"""
    
    def __init__(self):
        self.logger = get_logger('hubspot_sync.mapper')
        
        # Mapeo de campos SQL Server -> HubSpot
        # ✅ SOLO PROPIEDADES QUE REALMENTE EXISTEN EN HUBSPOT
        self.field_mapping = {
            # Campos básicos de identificación - ✅ VERIFICADOS
            'no__de_cedula': 'no__de_cedula',        # ✅ Confirmada personalizada
            'numero_asociado': 'numero_asociado',     # ✅ Confirmada personalizada
            
            # Campos estándar de HubSpot - ✅ VERIFICADOS
            'firstname': 'firstname',                 # ✅ Estándar
            'lastname': 'lastname',                   # ✅ Estándar
            'email': 'email',                         # ✅ Estándar
            'phone': 'phone',                         # ✅ Estándar
            'company': 'company',                     # ✅ Estándar
            
            # Campos adicionales estándar disponibles
            'mobilephone': 'mobilephone',             # ✅ Estándar
            'state': 'state',                         # ✅ Estándar
            'city': 'city',                           # ✅ Estándar
            'address': 'address',                     # ✅ Estándar
            'lifecyclestage': 'lifecyclestage',       # ✅ Estándar
            'createdate': 'createdate',               # ✅ Estándar
            'date_of_birth': 'date_of_birth',         # ✅ Estándar
            'marital_status': 'marital_status',       # ✅ Estándar
            'department': 'department',               # ✅ Estándar
            'annualrevenue': 'annualrevenue',         # ✅ Estándar
            
            # ❌ PROPIEDADES REMOVIDAS - NO EXISTEN EN HUBSPOT:
            # Se removieron 46 propiedades que causaban errores de API:
            # - email_bncr, estado_asociado
            # - Todos los productos de ahorro (tiene_ahorro_*, con_ahorros, etc.)
            # - Todos los productos de crédito (con_creditos, adelanto_de_pension_*, etc.)
            # - Todos los productos de seguros (tiene_seguros, apoyo_funerario, etc.)
            # - Otros productos (tiene_cesantia, tiene_certificados)
        }
        
        # Mapeo de campos SQL a propiedades HubSpot (para compatibilidad)
        self.sql_to_hubspot_mapping = {
            # Información básica
            'CEDULA': 'no__de_cedula',
            'NOMBRE_EMPLEADO': 'firstname',
            'APELLIDO1': 'lastname',
            'APELLIDO2': 'lastname',  # Se concatenará con apellido1
            'EMAIL': 'email',
            'CELULAR': 'phone',
            'TELEFONO': 'phone',
            'NUMERO_EMPLEADO': 'numero_asociado',
            
            # Información adicional
            'INSTITUCION': 'company',
            'DEPARTAMENTO': 'department',
            'PROVINCIA': 'state',
            'CANTON': 'city',
            'DISTRITO': 'address',
            'FECHA_NACIMIENTO': 'date_of_birth',
            'ESTADO_CIVIL': 'marital_status',
            'SALARIO_BRUTO': 'annualrevenue',
            
            # NOTA: Todas las columnas de productos financieros fueron removidas
            # porque las propiedades correspondientes no existen en HubSpot
        }
    
    def map_contact_data(self, sql_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapea los datos de SQL Server al formato requerido por HubSpot
        
        Args:
            sql_data: Diccionario con datos de SQL Server
            
        Returns:
            Diccionario con datos mapeados para HubSpot
        """
        hubspot_properties = {}
        
        # Usar el mapeo SQL a HubSpot
        for sql_field, hubspot_field in self.sql_to_hubspot_mapping.items():
            if sql_field in sql_data:
                value = sql_data[sql_field]
                
                # Procesar el valor según el tipo de campo
                processed_value = self._process_field_value(sql_field, value)
                
                if processed_value is not None:
                    # Manejar apellidos concatenados
                    if hubspot_field == 'lastname' and sql_field == 'APELLIDO1':
                        # Concatenar apellidos si existe APELLIDO2
                        apellido2 = sql_data.get('APELLIDO2', '').strip()
                        if apellido2:
                            processed_value = f"{processed_value} {apellido2}"
                    
                    hubspot_properties[hubspot_field] = processed_value
        
        self.logger.info(f"Campos mapeados: {len(hubspot_properties)} propiedades válidas de {len(sql_data)} campos SQL")
        self.logger.debug(f"Propiedades mapeadas: {list(hubspot_properties.keys())}")
        return hubspot_properties
    
    def _process_field_value(self, field_name: str, value: Any) -> Optional[str]:
        """
        Procesa un valor de campo para HubSpot
        
        Args:
            field_name: Nombre del campo SQL
            value: Valor del campo
            
        Returns:
            Valor procesado como string o None si no es válido
        """
        # Si el valor es None o cadena vacía, retornar None
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
        
        # Procesar según el tipo de campo
        if field_name == 'CEDULA':
            # Limpiar cédula - solo números
            return self._clean_cedula(str(value))
        
        elif field_name == 'EMAIL':
            # Validar formato de email
            return self._validate_email(str(value))
        
        elif field_name in ['CELULAR', 'TELEFONO']:
            # Limpiar número de teléfono
            return self._clean_phone(str(value))
        
        elif field_name == 'FECHA_NACIMIENTO':
            # Formatear fecha de nacimiento
            return self._format_date(value)
        
        elif field_name in ['SALARIO_BRUTO', 'SALARIO_NETO']:
            # Campos numéricos
            return self._format_number(value)
        
        else:
            # Campo de texto general
            return self._clean_text(str(value))
    
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
        return clean_cedula if clean_cedula else None
    
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
