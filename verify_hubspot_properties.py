#!/usr/bin/env python3
"""
Script para verificar todas las propiedades disponibles en HubSpot
y compararlas con nuestro mapeo CSV
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

def get_all_hubspot_contact_properties():
    """
    Obtiene TODAS las propiedades disponibles para contacts usando la API de HubSpot
    (Basado en fetch_contacts.py)
    """
    url = "https://api.hubapi.com/crm/v3/properties/contacts"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    print("🔍 Obteniendo TODAS las propiedades de contactos desde HubSpot API...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error obteniendo propiedades: {response.status_code}")
            print(f"❌ Respuesta: {response.text}")
            return []

        data = response.json()
        properties_info = []
        
        for prop in data.get("results", []):
            prop_name = prop.get("name")
            prop_type = prop.get("type", "unknown")
            prop_label = prop.get("label", "")
            field_type = prop.get("fieldType", "")
            
            if prop_name:
                properties_info.append({
                    'name': prop_name,
                    'type': prop_type,
                    'label': prop_label,
                    'fieldType': field_type
                })
        
        print(f"✅ Propiedades de contactos disponibles: {len(properties_info)}")
        return properties_info

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def compare_with_our_mapping():
    """
    Compara las propiedades de HubSpot con nuestro mapeo del CSV
    """
    # Nuestro mapeo del CSV (55 campos)
    our_mapping = {
        'no__de_cedula': 'no__de_cedula',
        'numero_asociado': 'numero_asociado',
        'firstname': 'firstname',
        'lastname': 'lastname',
        'email': 'email',
        'email_bncr': 'hs_additional_emails',
        'hs_whatsapp_phone_number': 'hs_whatsapp_phone_number',
        'telefono_habitacion': 'telefono_habitacion',
        'telefono_oficina': 'telefono_oficina',
        'date_of_birth': 'date_of_birth',
        'marital_status': 'marital_status',
        'cantidad_hijos': 'no_de_personas_dependientes',
        'estado_asociado': 'estado_del_asociado',
        'fecha_ingreso': 'fecha_de_tu_ingreso',
        'institucion': 'institucion_en_la_que_labora',
        'departamento': 'oficina',
        'salario_bruto_semanal_o_quincenal': 'salario_bruto_semanal_o_quincenal',
        'salario_neto_semanal_o_quincenal': 'salario_neto_semanal_o_quincenal',
        'provincia': 'provincia',
        'canton': 'canton',
        'distrito': 'distrito',
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
        'tiene_seguros': 'con_seguro',
        'apoyo_funerario': 'con_seg__apoyo_funerario',
        'seguro_su_vida': 'con_seg__su_vida',
        'poliza_colectiva': 'con_poliza_colectiva',
        'tiene_cesantia': 'con_cesantia',
        'encargado': 'hubspot_owner_id'
    }
    
    # Obtener propiedades reales de HubSpot
    hubspot_properties = get_all_hubspot_contact_properties()
    if not hubspot_properties:
        print("❌ No se pudieron obtener las propiedades de HubSpot")
        return
    
    # Crear set de nombres de propiedades para comparación rápida
    hubspot_property_names = {prop['name'] for prop in hubspot_properties}
    
    print(f"\n=== 📊 COMPARACIÓN DETALLADA ===")
    print(f"Propiedades en HubSpot: {len(hubspot_property_names)}")
    print(f"Propiedades en nuestro mapeo: {len(our_mapping)}")
    
    # Analizar nuestro mapeo
    valid_mappings = []
    invalid_mappings = []
    
    for sql_field, hubspot_field in our_mapping.items():
        if hubspot_field in hubspot_property_names:
            # Encontrar detalles de la propiedad
            prop_details = next((p for p in hubspot_properties if p['name'] == hubspot_field), {})
            valid_mappings.append((sql_field, hubspot_field, prop_details))
        else:
            # Buscar propiedades similares
            similar_props = [prop['name'] for prop in hubspot_properties 
                           if hubspot_field.lower().replace('_', '').replace('__', '') in prop['name'].lower().replace('_', '').replace('__', '')]
            invalid_mappings.append((sql_field, hubspot_field, similar_props))
    
    print(f"\n=== ✅ MAPEOS VÁLIDOS ({len(valid_mappings)}) ===")
    for sql_field, hubspot_field, details in valid_mappings:
        prop_type = details.get('type', 'unknown')
        prop_label = details.get('label', 'N/A')
        field_type = details.get('fieldType', 'unknown')
        print(f"  ✅ {sql_field} → {hubspot_field}")
        print(f"     📋 Tipo: {prop_type} | Campo: {field_type} | Label: {prop_label}")
    
    print(f"\n=== ❌ MAPEOS INVÁLIDOS ({len(invalid_mappings)}) ===")
    for sql_field, bad_hubspot_field, similar_props in invalid_mappings:
        print(f"\n❌ {sql_field} → {bad_hubspot_field} (NO EXISTE)")
        if similar_props:
            print(f"   💡 Propiedades similares encontradas:")
            for similar in similar_props[:5]:  # Mostrar máximo 5
                print(f"      - {similar}")
        else:
            print(f"   ⚠️  Sin propiedades similares encontradas")
    
    print(f"\n=== 📈 ESTADÍSTICAS ===")
    success_rate = (len(valid_mappings) / len(our_mapping)) * 100
    print(f"Tasa de éxito del mapeo: {success_rate:.1f}%")
    print(f"Campos válidos: {len(valid_mappings)}")
    print(f"Campos inválidos: {len(invalid_mappings)}")
    
    # Mostrar propiedades de HubSpot que NO estamos usando
    mapped_hubspot_fields = {hubspot_field for _, hubspot_field in our_mapping.items()}
    unused_properties = hubspot_property_names - mapped_hubspot_fields
    
    print(f"\n=== 💡 PROPIEDADES DE HUBSPOT NO UTILIZADAS ({len(unused_properties)}) ===")
    print("(Estas propiedades existen en HubSpot pero no las estamos mapeando)")
    
    # Filtrar propiedades personalizadas (que empiecen con con_, con_cred_, etc.)
    custom_unused = [prop for prop in unused_properties if any(prefix in prop for prefix in ['con_', 'saldo_', 'mon_', 'numero_', 'fecha_', 'estado_', 'provincia', 'canton', 'distrito'])]
    
    if custom_unused:
        print(f"\n🎯 PROPIEDADES PERSONALIZADAS NO UTILIZADAS ({len(custom_unused)}):")
        for prop in sorted(custom_unused)[:20]:  # Mostrar primeras 20
            print(f"  💡 {prop}")
        if len(custom_unused) > 20:
            print(f"  ... y {len(custom_unused) - 20} más")
    
    return valid_mappings, invalid_mappings

def main():
    """
    Función principal
    """
    print("🔍 VERIFICACIÓN COMPLETA DE PROPIEDADES DE HUBSPOT")
    print("=" * 60)
    print("Usando la metodología avanzada de fetch_contacts.py")
    print("=" * 60)
    
    # Verificar token
    token = os.getenv('HUBSPOT_TOKEN')
    if not token:
        print("❌ Error: No se encontró HUBSPOT_TOKEN en las variables de entorno")
        return
    
    print(f"✅ Token encontrado: {token[:20]}...")
    
    # Ejecutar comparación
    valid_mappings, invalid_mappings = compare_with_our_mapping()
    
    print(f"\n🎯 RESUMEN FINAL:")
    print(f"   ✅ Propiedades que funcionan: {len(valid_mappings)}")
    print(f"   ❌ Propiedades que NO funcionan: {len(invalid_mappings)}")
    print(f"   📊 Tasa de éxito: {(len(valid_mappings)/(len(valid_mappings)+len(invalid_mappings)))*100:.1f}%")

if __name__ == "__main__":
    main()
