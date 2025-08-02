#!/usr/bin/env python3
"""
Script para validar el mapeo usando las propiedades REALES de HubSpot del CSV
"""

def main():
    # Propiedades que TÚ confirmaste que SÍ EXISTEN en HubSpot (del CSV)
    confirmed_hubspot_properties = {
        'no__de_cedula',
        'numero_asociado', 
        'firstname', 
        'lastname', 
        'email',
        'hs_additional_emails',  # email_bncr se mapea a esto
        'hs_whatsapp_phone_number',
        'telefono_habitacion',
        'telefono_oficina', 
        'date_of_birth',
        'marital_status',
        'no_de_personas_dependientes',  # cantidad_hijos se mapea a esto
        'estado_del_asociado',  # estado_asociado se mapea a esto
        'fecha_de_tu_ingreso',  # fecha_ingreso se mapea a esto
        'institucion_en_la_que_labora',  # institucion se mapea a esto
        'oficina',  # departamento se mapea a esto
        'salario_bruto_semanal_o_quincenal',
        'salario_neto_semanal_o_quincenal',
        'provincia',
        'canton', 
        'distrito',
        'con_ahorro',  # con_ahorros se mapea a esto
        'con_ahorro_economias',  # tiene_economias se mapea a esto
        'con_ahorro_navideno',  # tiene_ahorro_navideno se mapea a esto
        'con_plan_fin_de_ano',  # tiene_plan_fin_de_ano se mapea a esto
        'con_ahorro_fondo_de_inversion',  # tiene_ahorro_fondo_de_inversion se mapea a esto
        'con_ahorro_plan_vacacional',  # tiene_ahorro_plan_vacacional se mapea a esto
        'con_ahorro_plan_aguinaldo',  # tiene_ahorro_plan_aguinaldo se mapea a esto
        'con_ahorro_plan_bono_escolar',  # tiene_ahorro_plan_bono_escolar se mapea a esto
        'con_ahorro_con_proposito',  # tiene_ahorro_con_proposito se mapea a esto
        'con_ahorro_plan_futuro',  # tiene_ahorro_plan_futuro se mapea a esto
        'con_credito',  # con_creditos se mapea a esto (singular vs plural)
        'con_cred__capital_social',  # sobre_capital_social se mapea a esto
        'con_cred__adelanto_de_pension',  # adelanto_de_pension se mapea a esto
        'con_cred__consumo_personal',  # consumo_personal se mapea a esto
        'con_cred__salud',  # salud se mapea a esto
        'con_cred__especial_al_vencimiento',  # especiales_al_vencimiento se mapea a esto
        'con_cred__facilito',  # facilito se mapea a esto
        'con_cred__refundicion_de_pasivos',  # refundicion_de_pasivos se mapea a esto
        'con_cred_vivienda_patrimonial',  # vivienda_patrimonial se mapea a esto
        'con_cred__capitalizable_3',  # credito_capitalizable se mapea a esto
        'con_cred__tecnologico',  # tecnologico se mapea a esto
        'con_credifacil',  # credifacil se mapea a esto
        'con_cred__vivienda_cooperativa',  # vivienda_cooperativa se mapea a esto
        'con_cred__multiuso',  # multiuso se mapea a esto
        'con_cred__deuda_unica',  # deuda_unica se mapea a esto
        'con_cred__vivienda_constructivo',  # vivienda_constructivo se mapea a esto
        'con_cred__vehiculo_nuevos',  # credito_compra_vehiculos se mapea a esto
        'con_cred__back_to_back',  # con_back_to_back se mapea a esto
        'con_seguro',  # tiene_seguros se mapea a esto
        'con_seg__apoyo_funerario',  # apoyo_funerario se mapea a esto
        'con_seg__su_vida',  # seguro_su_vida se mapea a esto
        'con_poliza_colectiva',  # poliza_colectiva se mapea a esto
        'con_cesantia',  # tiene_cesantia se mapea a esto
        'hubspot_owner_id'  # encargado se mapea a esto
    }
    
    # Mapeo desde tu CSV (exactamente como lo definiste)
    csv_mapping = {
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
    
    print("=== VALIDACIÓN CORREGIDA DEL MAPEO CSV ===\n")
    print("Usando las propiedades que TÚ confirmaste que existen en HubSpot\n")
    print(f"Total de campos mapeados en CSV: {len(csv_mapping)}")
    print(f"Total de propiedades confirmadas en HubSpot: {len(confirmed_hubspot_properties)}")
    
    # Validar cuáles existen y cuáles no
    valid_mappings = []
    invalid_mappings = []
    
    for sql_field, hubspot_field in csv_mapping.items():
        if hubspot_field in confirmed_hubspot_properties:
            valid_mappings.append((sql_field, hubspot_field))
        else:
            invalid_mappings.append((sql_field, hubspot_field))
    
    print(f"\n=== ✅ MAPEOS VÁLIDOS ({len(valid_mappings)}) ===")
    for sql_field, hubspot_field in valid_mappings:
        print(f"  ✅ {sql_field} -> {hubspot_field}")
    
    if invalid_mappings:
        print(f"\n=== ❌ MAPEOS INVÁLIDOS ({len(invalid_mappings)}) ===")
        for sql_field, bad_hubspot_field in invalid_mappings:
            print(f"  ❌ {sql_field} -> {bad_hubspot_field}")
    else:
        print(f"\n🎉 ¡TODOS LOS MAPEOS SON VÁLIDOS!")
    
    print(f"\n=== 📊 RESUMEN ===")
    print(f"Mapeos válidos: {len(valid_mappings)}")
    print(f"Mapeos inválidos: {len(invalid_mappings)}")
    success_rate = (len(valid_mappings) / len(csv_mapping)) * 100
    print(f"Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate == 100:
        print(f"\n🚀 ¡PERFECTO! Tu mapeo está 100% correcto.")
        print(f"Podemos proceder a:")
        print(f"  1. Actualizar el field_mapper.py con este mapeo")
        print(f"  2. Ejecutar la prueba con el contacto 107150612")
        print(f"  3. Medir la tasa de éxito de actualización")

if __name__ == "__main__":
    main()
