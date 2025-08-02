#!/usr/bin/env python3
"""
Script simple para identificar propiedades que no existen en HubSpot
"""

def main():
    # Lista de propiedades que EXISTEN en HubSpot (según la consulta SQL que proporcionaste)
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
    
    # Lista de propiedades que están MAPEADAS en field_mapper (las problemáticas)
    mapped_properties_in_field_mapper = {
        # Campos básicos de identificación
        'no__de_cedula', 'numero_asociado',
        
        # Campos de contacto estándar de HubSpot
        'firstname', 'lastname', 'email', 'email_bncr',
        
        # Teléfonos
        'hs_whatsapp_phone_number', 'phone', 'mobilephone',
        
        # Información personal
        'date_of_birth', 'marital_status', 'numemployees',
        
        # Estado y fechas
        'lifecyclestage', 'createdate',
        
        # Información laboral
        'company', 'department', 'annualrevenue', 'hs_additional_emails',
        
        # Ubicación
        'state', 'city', 'address',
        
        # Productos financieros - Ahorros (PROBLEMÁTICOS)
        'con_ahorros', 'tiene_economias', 'tiene_ahorro_navideno', 'tiene_plan_fin_de_ano',
        'tiene_ahorro_fondo_de_inversion', 'tiene_ahorro_plan_vacacional', 'tiene_ahorro_plan_aguinaldo',
        'tiene_ahorro_plan_bono_escolar', 'tiene_ahorro_con_proposito', 'tiene_ahorro_plan_futuro',
        
        # Productos financieros - Créditos (PROBLEMÁTICOS)
        'con_credito', 'sobre_capital_social', 'adelanto_de_pension_sf', 'ahorros_credito',
        'consumo_personal', 'salud', 'adelanto_de_pension_pf', 'especiales_al_vencimiento',
        'facilito', 'vehiculos_no_usar', 'credito_refinanciamiento', 'refundicion_de_pasivos',
        'vivienda_patrimonial', 'credito_capitalizable', 'capitalizable_2'
    }
    
    print("=== ANÁLISIS DE PROPIEDADES MAPEADAS ===\n")
    print(f"Total de propiedades existentes en HubSpot: {len(existing_hubspot_properties)}")
    print(f"Total de propiedades mapeadas en field_mapper: {len(mapped_properties_in_field_mapper)}")
    
    # Encontrar propiedades que NO existen en HubSpot
    missing_properties = mapped_properties_in_field_mapper - existing_hubspot_properties
    
    # Encontrar propiedades que existen pero no están mapeadas
    unmapped_properties = existing_hubspot_properties - mapped_properties_in_field_mapper
    
    print(f"\n=== ❌ PROPIEDADES QUE NO EXISTEN EN HUBSPOT ({len(missing_properties)}) ===")
    if missing_properties:
        for prop in sorted(missing_properties):
            print(f"  ❌ {prop}")
    else:
        print("  ✅ Todas las propiedades mapeadas existen en HubSpot")
    
    print(f"\n=== ⚠️ PROPIEDADES DE HUBSPOT NO MAPEADAS ({len(unmapped_properties)}) ===")
    print("(Estas existen en HubSpot pero no las estamos usando)")
    if unmapped_properties:
        for prop in sorted(unmapped_properties):
            print(f"  ⚠️  {prop}")
    
    # Encontrar propiedades que SÍ coinciden
    matching_properties = mapped_properties_in_field_mapper & existing_hubspot_properties
    print(f"\n=== ✅ PROPIEDADES QUE SÍ COINCIDEN ({len(matching_properties)}) ===")
    for prop in sorted(matching_properties):
        print(f"  ✅ {prop}")
    
    # Análisis específico de mapeos problemáticos
    print(f"\n=== 🔍 ANÁLISIS DETALLADO DE MAPEOS PROBLEMÁTICOS ===")
    
    # Problemas específicos identificados
    problematic_mappings = {
        # Campos que no existen en HubSpot pero están mapeados
        'salud': ['con_cred__emergencia_salud', 'con_seg__gastos_medicos'],
        'facilito': ['con_cred__facilito'],
        'con_ahorros': ['con_ahorro'],
        'con_credito': ['con_credito__navidad', 'con_cred__personal', 'con_cred__especial'],
        'tiene_economias': 'NO ENCONTRADA',
        'tiene_ahorro_navideno': 'NO ENCONTRADA',
        'sobre_capital_social': 'NO ENCONTRADA',
        'adelanto_de_pension_sf': 'NO ENCONTRADA',
        'ahorros_credito': 'NO ENCONTRADA',
        'consumo_personal': 'NO ENCONTRADA',
        'adelanto_de_pension_pf': 'NO ENCONTRADA',
        'especiales_al_vencimiento': 'NO ENCONTRADA',
        'vehiculos_no_usar': 'NO ENCONTRADA',
        'credito_refinanciamiento': 'NO ENCONTRADA',
        'refundicion_de_pasivos': ['refuncion_ii'],  # Nombre similar
        'vivienda_patrimonial': ['con_cred__vivienda'],
        'credito_capitalizable': 'NO ENCONTRADA',
        'capitalizable_2': 'NO ENCONTRADA'
    }
    
    for mapped_field, possible_matches in problematic_mappings.items():
        if mapped_field in missing_properties:
            print(f"\n❌ MAPEADO: {mapped_field} -> NO EXISTE EN HUBSPOT")
            if isinstance(possible_matches, list):
                print(f"   💡 Posibles alternativas en HubSpot:")
                for match in possible_matches:
                    print(f"      - {match}")
            else:
                print(f"   💡 {possible_matches}")

if __name__ == "__main__":
    main()
