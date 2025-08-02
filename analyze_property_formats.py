#!/usr/bin/env python3
"""
Script para analizar los formatos correctos de cada propiedad en HubSpot
"""

import os
import requests
import sys
sys.path.append('.')
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_property_details():
    """
    Obtiene detalles específicos de las propiedades que estamos mapeando
    """
    token = os.getenv('HUBSPOT_TOKEN')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Nuestras propiedades mapeadas
    our_properties = [
        'no__de_cedula', 'numero_asociado', 'firstname', 'lastname', 'email',
        'hs_additional_emails', 'hs_whatsapp_phone_number', 'telefono_habitacion',
        'telefono_oficina', 'date_of_birth', 'marital_status', 'no_de_personas_dependientes',
        'estado_del_asociado', 'fecha_de_tu_ingreso', 'institucion_en_la_que_labora',
        'oficina', 'salario_bruto_semanal_o_quincenal', 'salario_neto_semanal_o_quincenal',
        'provincia', 'canton', 'distrito', 'con_ahorro', 'con_ahorro_economias',
        'con_ahorro_navideno', 'con_plan_fin_de_ano', 'con_ahorro_fondo_de_inversion',
        'con_ahorro_plan_vacacional', 'con_ahorro_plan_aguinaldo', 'con_ahorro_plan_bono_escolar',
        'con_ahorro_con_proposito', 'con_ahorro_plan_futuro', 'con_credito',
        'con_cred__capital_social', 'con_cred__adelanto_de_pension', 'con_cred__consumo_personal',
        'con_cred__salud', 'con_cred__especial_al_vencimiento', 'con_cred__facilito',
        'con_cred__refundicion_de_pasivos', 'con_cred_vivienda_patrimonial',
        'con_cred__capitalizable_3', 'con_cred__tecnologico', 'con_credifacil',
        'con_cred__vivienda_cooperativa', 'con_cred__multiuso', 'con_cred__deuda_unica',
        'con_cred__vivienda_constructivo', 'con_cred__vehiculo_nuevos', 'con_cred__back_to_back',
        'con_seguro', 'con_seg__apoyo_funerario', 'con_seg__su_vida', 'con_poliza_colectiva',
        'con_cesantia', 'hubspot_owner_id'
    ]

    print("🔍 ANALIZANDO FORMATOS REQUERIDOS PARA NUESTRAS PROPIEDADES")
    print("=" * 60)

    property_details = {}
    
    for prop_name in our_properties:
        print(f"\n📋 Analizando: {prop_name}")
        
        url = f"https://api.hubapi.com/crm/v3/properties/contacts/{prop_name}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                property_details[prop_name] = data
                
                # Extraer información clave
                field_type = data.get('fieldType', 'unknown')
                data_type = data.get('type', 'unknown')
                options = data.get('options', [])
                
                print(f"   ✅ Tipo: {data_type} | Campo: {field_type}")
                
                if options:
                    print(f"   📝 Opciones disponibles:")
                    for option in options[:5]:  # Mostrar primeras 5
                        label = option.get('label', 'N/A')
                        value = option.get('value', 'N/A')
                        print(f"      - {label}: '{value}'")
                    if len(options) > 5:
                        print(f"      ... y {len(options) - 5} más")
                        
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

    return property_details

def analyze_data_formats(property_details):
    """
    Analiza y agrupa propiedades por tipo de formato requerido
    """
    print(f"\n🎯 ANÁLISIS DE FORMATOS POR TIPO")
    print("=" * 40)
    
    format_groups = {
        'boolean_checkbox': [],
        'select_enum': [],
        'text': [],
        'number': [],
        'date': [],
        'phonenumber': [],
        'otros': []
    }
    
    for prop_name, details in property_details.items():
        field_type = details.get('fieldType', 'unknown')
        data_type = details.get('type', 'unknown')
        
        if field_type == 'booleancheckbox':
            format_groups['boolean_checkbox'].append(prop_name)
        elif field_type == 'select' or data_type == 'enumeration':
            format_groups['select_enum'].append(prop_name)
        elif data_type == 'string' and field_type == 'text':
            format_groups['text'].append(prop_name)
        elif data_type == 'number':
            format_groups['number'].append(prop_name)
        elif data_type == 'date':
            format_groups['date'].append(prop_name)
        elif field_type == 'phonenumber':
            format_groups['phonenumber'].append(prop_name)
        else:
            format_groups['otros'].append(prop_name)
    
    for format_type, properties in format_groups.items():
        if properties:
            print(f"\n📋 {format_type.upper()} ({len(properties)} campos):")
            for prop in properties:
                print(f"   - {prop}")
    
    return format_groups

def generate_format_recommendations(format_groups, property_details):
    """
    Genera recomendaciones específicas de formato para cada tipo
    """
    print(f"\n💡 RECOMENDACIONES DE FORMATO")
    print("=" * 40)
    
    print(f"\n1. 📝 CAMPOS BOOLEAN CHECKBOX:")
    print(f"   Formato requerido: 'true' o 'false' (string)")
    print(f"   Ejemplo: {{'con_ahorro': 'true'}}")
    
    print(f"\n2. 📋 CAMPOS SELECT/ENUM:")
    print(f"   Formato requerido: Valor exacto de la lista de opciones")
    print(f"   Verificar opciones disponibles para cada campo")
    
    print(f"\n3. 🔢 CAMPOS NUMBER:")
    print(f"   Formato requerido: Número (int o float), no string")
    print(f"   Ejemplo: {{'numero_asociado': 12345}}")
    
    print(f"\n4. 📅 CAMPOS DATE:")
    print(f"   Formato requerido: 'YYYY-MM-DD' (string)")
    print(f"   Ejemplo: {{'date_of_birth': '1990-01-15'}}")
    
    print(f"\n5. 📞 CAMPOS PHONE:")
    print(f"   Formato requerido: String con formato internacional")
    print(f"   Ejemplo: {{'telefono_habitacion': '+50625555555'}}")

def main():
    """
    Función principal
    """
    print("🔍 ANÁLISIS DETALLADO DE FORMATOS DE PROPIEDADES")
    print("=" * 60)
    
    # 1. Obtener detalles de propiedades
    property_details = get_property_details()
    
    # 2. Analizar formatos por tipo
    format_groups = analyze_data_formats(property_details)
    
    # 3. Generar recomendaciones
    generate_format_recommendations(format_groups, property_details)
    
    print(f"\n🎯 SIGUIENTE PASO:")
    print(f"   ✅ Corregir field_mapper.py para manejar estos formatos")
    print(f"   ✅ Implementar conversión de tipos en _process_field_value()")
    print(f"   ✅ Probar actualización con formatos corregidos")

if __name__ == "__main__":
    main()
