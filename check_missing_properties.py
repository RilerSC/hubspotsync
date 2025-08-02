#!/usr/bin/env python3
"""
Script para identificar propiedades que no existen en HubSpot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('escritura')

from hubspot_client.field_mapper import HubSpotFieldMapper

def main():
    # Lista de propiedades que EXISTEN en HubSpot (según la consulta SQL)
    existing_hubspot_properties = {
        'numero_asociado', 'firstname', 'lastname', 'email', 'email_bncr', 'phone', 'mobilephone',
        'fecha_ingreso_asociado', 'fecha_nacimiento', 'estado_asociado', 'provincia', 'canton',
        'distrito', 'direccion_exacta', 'lugar_trabajo', 'categoria_pcp', 'cuenta_banco',
        'sucursal_asociado', 'oficina_cuenta', 'genero', 'estado_civil', 'numero_hijos',
        'numero_cargas_adultos', 'actividad_economica', 'ingresos_mensuales', 'egresos_mensuales',
        'activos', 'pasivos', 'patrimonio', 'pep', 'senior', 'referencias_personales',
        'referencias_comerciales', 'con_ahorro', 'saldo_ahorro', 'con_certif_ahorro_plazo',
        'saldo_certif_ahorro_plazo', 'con_credito__navidad', 'saldo_credito__navidad',
        'con_cred__adelanto_cesantia', 'saldo_cred__adelanto_cesantia', 'con_cred__beca',
        'saldo_cred__beca', 'con_cred__desp_medica', 'saldo_cred__desp_medica',
        'con_cred__emergencia', 'saldo_cred__emergencia', 'con_cred__emergencia_salud',
        'saldo_cred__emergencia_salud', 'con_cred__especial', 'saldo_cred__especial',
        'con_cred__facilito', 'saldo_cred__facilito', 'con_cred__personal', 'saldo_cred__personal',
        'con_cred__pignoracion', 'saldo_cred__pignoracion', 'con_cred__suplementario',
        'saldo_cred__suplementario', 'con_cred__vivienda', 'saldo_cred__vivienda',
        'con_cred__linea_credito', 'saldo_cred__linea_credito', 'con_tarj__debito',
        'con_tarj_cred__clasica', 'saldo_tarj_cred__clasica', 'con_tarj_cred__oro',
        'saldo_tarj_cred__oro', 'con_tarj_cred__titanium', 'saldo_tarj_cred__titanium',
        'con_seg__vida_asociado', 'con_seg__gastos_medicos', 'con_seg__hogar',
        'con_seg__automovil', 'con_seg__integral_familiar', 'con_seg__su_vida',
        'con_seg__accidentes_personales', 'con_seg__desgravamen', 'con_seg__desempleo',
        'con_seg__credito_protegido', 'con_seg__proteccion_familiar', 'con_seg__exequial',
        'con_seg__invalidez_total', 'con_seg__vida_grupo', 'con_seg__gastos_funerarios',
        'con_seg__vida_grupo_desgravamen', 'con_seg__riesgo_profesional', 'con_seg__vida_it',
        'con_otros__exceso_ahorro_corriente', 'con_otros__exceso_certif_deposito',
        'con_otros__descuento_planilla', 'con_otros__deposito_garantia', 'con_otros__fondo_social',
        'con_otros__cuentas_por_cobrar', 'mon_total_productos', 'mon_total_creditos',
        'mon_total_ahorros', 'mon_total_seguros', 'refuncion_ii'
    }
    
    # Obtener propiedades mapeadas
    mapper = HubSpotFieldMapper()
    mapped_properties = set()
    
    # Recopilar todas las propiedades del mapping
    for sql_field, hubspot_field in mapper.field_mapping.items():
        if hubspot_field:  # Solo si no es None
            mapped_properties.add(hubspot_field)
    
    print("=== ANÁLISIS DE PROPIEDADES MAPEADAS ===\n")
    print(f"Total de propiedades existentes en HubSpot: {len(existing_hubspot_properties)}")
    print(f"Total de propiedades mapeadas en field_mapper: {len(mapped_properties)}")
    
    # Encontrar propiedades que NO existen en HubSpot
    missing_properties = mapped_properties - existing_hubspot_properties
    
    # Encontrar propiedades que existen pero no están mapeadas
    unmapped_properties = existing_hubspot_properties - mapped_properties
    
    print(f"\n=== PROPIEDADES QUE NO EXISTEN EN HUBSPOT ({len(missing_properties)}) ===")
    if missing_properties:
        for prop in sorted(missing_properties):
            print(f"  ❌ {prop}")
    else:
        print("  ✅ Todas las propiedades mapeadas existen en HubSpot")
    
    print(f"\n=== PROPIEDADES DE HUBSPOT NO MAPEADAS ({len(unmapped_properties)}) ===")
    if unmapped_properties:
        for prop in sorted(unmapped_properties):
            print(f"  ⚠️  {prop}")
    
    # Encontrar propiedades que SÍ coinciden
    matching_properties = mapped_properties & existing_hubspot_properties
    print(f"\n=== PROPIEDADES QUE SÍ COINCIDEN ({len(matching_properties)}) ===")
    for prop in sorted(matching_properties):
        print(f"  ✅ {prop}")
    
    # Mostrar mapeos específicos problemáticos
    print(f"\n=== ANÁLISIS DETALLADO DE MAPEOS PROBLEMÁTICOS ===")
    problematic_mappings = []
    
    for sql_field, hubspot_field in mapper.field_mapping.items():
        if hubspot_field and hubspot_field not in existing_hubspot_properties:
            # Buscar posibles coincidencias parciales
            possible_matches = [prop for prop in existing_hubspot_properties 
                              if sql_field.lower().replace('_', '') in prop.lower().replace('_', '')]
            problematic_mappings.append((sql_field, hubspot_field, possible_matches))
    
    for sql_field, bad_hubspot_field, possible_matches in problematic_mappings:
        print(f"\n❌ SQL: {sql_field} -> HubSpot: {bad_hubspot_field} (NO EXISTE)")
        if possible_matches:
            print(f"   💡 Posibles coincidencias:")
            for match in possible_matches:
                print(f"      - {match}")

if __name__ == "__main__":
    main()
