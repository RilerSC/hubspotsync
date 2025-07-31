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
        
        # Mapeo de campos SQL Server -> HubSpot
        self.field_mapping = {
            # Campos básicos de identificación
            'no__de_cedula': 'no__de_cedula',  # Campo personalizado clave
            'numero_asociado': 'numero_asociado',
            
            # Campos de contacto estándar de HubSpot
            'firstname': 'firstname',
            'lastname': 'lastname', 
            'email': 'email',
            'email_bncr': 'email_bncr',
            
            # Teléfonos
            'hs_whatsapp_phone_number': 'hs_whatsapp_phone_number',
            'telefono_habitacion': 'phone',  # Teléfono principal de HubSpot
            'telefono_oficina': 'mobilephone',
            
            # Información personal
            'date_of_birth': 'date_of_birth',
            'marital_status': 'marital_status',
            'cantidad_hijos': 'numemployees',  # Reutilizamos campo existente
            
            # Estado y fechas
            'estado_asociado': 'lifecyclestage',
            'fecha_ingreso': 'createdate',
            
            # Información laboral
            'institucion': 'company',
            'departamento': 'department',
            'salario_bruto_semanal_o_quincenal': 'annualrevenue',
            'salario_neto_semanal_o_quincenal': 'hs_additional_emails',
            
            # Ubicación
            'provincia': 'state',
            'canton': 'city',
            'distrito': 'address',
            
            # Productos financieros - Ahorros
            'con_ahorros': 'con_ahorros',
            'tiene_economias': 'tiene_economias',
            'tiene_ahorro_navideno': 'tiene_ahorro_navideno',
            'tiene_plan_fin_de_ano': 'tiene_plan_fin_de_ano',
            'tiene_ahorro_fondo_de_inversion': 'tiene_ahorro_fondo_de_inversion',
            'tiene_ahorro_plan_vacacional': 'tiene_ahorro_plan_vacacional',
            'tiene_ahorro_plan_aguinaldo': 'tiene_ahorro_plan_aguinaldo',
            'tiene_ahorro_plan_bono_escolar': 'tiene_ahorro_plan_bono_escolar',
            'tiene_ahorro_con_proposito': 'tiene_ahorro_con_proposito',
            'tiene_ahorro_plan_futuro': 'tiene_ahorro_plan_futuro',
            
            # Productos financieros - Créditos
            'con_credito': 'con_credito',
            'sobre_capital_social': 'sobre_capital_social',
            'adelanto_de_pension_sf': 'adelanto_de_pension_sf',
            'ahorros_credito': 'ahorros_credito',
            'consumo_personal': 'consumo_personal',
            'salud': 'salud',
            'adelanto_de_pension_pf': 'adelanto_de_pension_pf',
            'especiales_al_vencimiento': 'especiales_al_vencimiento',
            'facilito': 'facilito',
            'vehiculos_no_usar': 'vehiculos_no_usar',
            'credito_refinanciamiento': 'credito_refinanciamiento',
            'refundicion_de_pasivos': 'refundicion_de_pasivos',
            'vivienda_patrimonial': 'vivienda_patrimonial',
            'credito_capitalizable': 'credito_capitalizable',
            'capitalizable_2': 'capitalizable_2',
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
        
        for sql_field, hubspot_field in self.field_mapping.items():
            if sql_field in sql_data:
                value = sql_data[sql_field]
                
                # Procesar el valor según el tipo de campo
                processed_value = self._process_field_value(sql_field, value)
                
                if processed_value is not None:
                    hubspot_properties[hubspot_field] = processed_value
        
        self.logger.debug(f"Campos mapeados: {len(hubspot_properties)} de {len(sql_data)}")
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
        if field_name == 'no__de_cedula':
            # Limpiar cédula - solo números
            return self._clean_cedula(str(value))
        
        elif field_name in ['email', 'email_bncr']:
            # Validar formato de email
            return self._validate_email(str(value))
        
        elif field_name in ['telefono_habitacion', 'telefono_oficina', 'hs_whatsapp_phone_number']:
            # Limpiar número de teléfono
            return self._clean_phone(str(value))
        
        elif field_name == 'date_of_birth':
            # Formatear fecha de nacimiento
            return self._format_date(value)
        
        elif field_name in ['con_ahorros', 'tiene_economias', 'con_credito'] or field_name.startswith('tiene_'):
            # Campos booleanos
            return self._format_boolean(value)
        
        elif field_name in ['salario_bruto_semanal_o_quincenal', 'salario_neto_semanal_o_quincenal']:
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
