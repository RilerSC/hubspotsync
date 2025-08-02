#!/usr/bin/env python3
"""
Script para listar todas las propiedades de contactos disponibles en HubSpot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hubspot_client.writer import HubSpotWriter
from utils.logger import get_logger

def list_hubspot_properties():
    """
    Lista todas las propiedades de contactos disponibles en HubSpot
    """
    logger = get_logger('hubspot_properties')
    
    print("📋 LISTADO DE PROPIEDADES DE CONTACTOS EN HUBSPOT")
    print("=" * 70)
    
    try:
        writer = HubSpotWriter(dry_run=False)  # Modo real para consultar propiedades
        
        # Obtener todas las propiedades de contactos
        properties_response = writer.hubspot_client.crm.properties.core_api.get_all(
            object_type="contacts",
            archived=False
        )
        
        all_properties = properties_response.results
        
        print(f"✅ Total de propiedades encontradas: {len(all_properties)}")
        print("=" * 70)
        
        # Separar por categorías
        hubspot_standard = []
        custom_properties = []
        
        # Propiedades problemáticas del error
        problematic_properties = [
            'tiene_ahorro_con_proposito',
            'vehiculos_no_usar', 
            'facilito',
            'con_ahorros',
            'sobre_capital_social',
            'tiene_economias',
            'tiene_ahorro_navideno',
            'tiene_plan_fin_de_ano',
            'tiene_ahorro_fondo_de_inversion',
            'tiene_ahorro_plan_vacacional',
            'tiene_ahorro_plan_aguinaldo',
            'tiene_ahorro_plan_bono_escolar',
            'tiene_ahorro_plan_futuro',
            'con_creditos',
            'adelanto_de_pension_sf',
            'ahorros_credito',
            'consumo_personal',
            'salud',
            'adelanto_de_pension_pf',
            'especiales_al_vencimiento',
            'credito_refinanciamiento',
            'refundicion_de_pasivos',
            'vivienda_patrimonial',
            'credito_capitalizable',
            'capitalizable_2',
            'refuncion_ii',
            'capitalizable_3',
            'tecnologico',
            'credifacil',
            'vivienda_cooperativa',
            'vivienda_adjudicados',
            'multiuso',
            'deuda_unica',
            'vivienda_constructivo',
            'credito_compra_vehiculos',
            'credito_vehiculos_seminuevos',
            'con_back_to_back',
            'tiene_seguros',
            'apoyo_funerario',
            'seguro_su_vida',
            'funeraria_polini',
            'poliza_colectiva',
            'plan_medismart',
            'poliza_vivienda',
            'tiene_cesantia',
            'tiene_certificados'
        ]
        
        found_problematic = []
        missing_problematic = []
        
        # Crear diccionario para búsqueda rápida
        property_names = {prop.name: prop for prop in all_properties}
        
        # Verificar propiedades problemáticas
        print("\n🔍 VERIFICACIÓN DE PROPIEDADES PROBLEMÁTICAS:")
        print("=" * 50)
        
        for prop_name in problematic_properties:
            if prop_name in property_names:
                prop = property_names[prop_name]
                found_problematic.append(prop_name)
                print(f"✅ {prop_name} - EXISTE")
                print(f"   Tipo: {prop.type}")
                print(f"   Etiqueta: {prop.label}")
                print(f"   Grupo: {prop.group_name}")
                print()
            else:
                missing_problematic.append(prop_name)
                print(f"❌ {prop_name} - NO EXISTE")
        
        # Resumen
        print("\n📊 RESUMEN:")
        print("=" * 30)
        print(f"✅ Propiedades que SÍ existen: {len(found_problematic)}")
        print(f"❌ Propiedades que NO existen: {len(missing_problematic)}")
        
        if missing_problematic:
            print(f"\n🚫 PROPIEDADES FALTANTES ({len(missing_problematic)}):")
            for prop in missing_problematic:
                print(f"   - {prop}")
        
        if found_problematic:
            print(f"\n✅ PROPIEDADES EXISTENTES ({len(found_problematic)}):")
            for prop in found_problematic:
                print(f"   - {prop}")
        
        # Mostrar algunas propiedades estándar importantes
        important_standard = ['firstname', 'lastname', 'email', 'phone', 'company']
        print(f"\n📋 PROPIEDADES ESTÁNDAR IMPORTANTES:")
        print("=" * 40)
        for prop_name in important_standard:
            if prop_name in property_names:
                print(f"✅ {prop_name} - Disponible")
            else:
                print(f"❌ {prop_name} - NO encontrada")
        
        # Buscar propiedades personalizadas relacionadas con el negocio
        print(f"\n🏢 PROPIEDADES PERSONALIZADAS RELACIONADAS:")
        print("=" * 45)
        business_keywords = ['numero_asociado', 'no__de_cedula', 'estado_asociado', 'email_bncr']
        for prop_name in business_keywords:
            if prop_name in property_names:
                prop = property_names[prop_name]
                print(f"✅ {prop_name}")
                print(f"   Etiqueta: {prop.label}")
                print(f"   Tipo: {prop.type}")
                print()
            else:
                print(f"❌ {prop_name} - NO encontrada")
        
    except Exception as e:
        logger.error(f"Error al obtener propiedades: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_hubspot_properties()
