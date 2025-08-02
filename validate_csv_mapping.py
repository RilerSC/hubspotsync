#!/usr/bin/env python3
"""
Script para validar el mapeo de propiedades desde el CSV proporcionado
"""

def main():
    # Lista de propiedades que EXISTEN en HubSpot (según la consulta SQL anterior)
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
        'mon_total_ahorros', 'mon_total_seguros', 'refuncion_ii', 'hs_whatsapp_phone_number',
        'telefono_habitacion', 'telefono_oficina', 'date_of_birth', 'marital_status',
        'no_de_personas_dependientes', 'estado_del_asociado', 'fecha_de_tu_ingreso',
        'institucion_en_la_que_labora', 'oficina', 'salario_bruto_semanal_o_quincenal',
        'salario_neto_semanal_o_quincenal', 'hubspot_owner_id'
    }
    
    # Mapeo desde tu CSV
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
    
    print("=== VALIDACIÓN DEL MAPEO CSV ===\n")
    print(f"Total de campos mapeados en CSV: {len(csv_mapping)}")
    print(f"Total de propiedades existentes en HubSpot: {len(existing_hubspot_properties)}")
    
    # Validar cuáles existen y cuáles no
    valid_mappings = []
    invalid_mappings = []
    
    for sql_field, hubspot_field in csv_mapping.items():
        if hubspot_field in existing_hubspot_properties:
            valid_mappings.append((sql_field, hubspot_field))
        else:
            # Buscar posibles alternativas
            possible_matches = [prop for prop in existing_hubspot_properties 
                              if hubspot_field.lower().replace('_', '').replace('__', '') in prop.lower().replace('_', '').replace('__', '')]
            invalid_mappings.append((sql_field, hubspot_field, possible_matches))
    
    print(f"\n=== ✅ MAPEOS VÁLIDOS ({len(valid_mappings)}) ===")
    for sql_field, hubspot_field in valid_mappings:
        print(f"  ✅ {sql_field} -> {hubspot_field}")
    
    print(f"\n=== ❌ MAPEOS INVÁLIDOS ({len(invalid_mappings)}) ===")
    for sql_field, bad_hubspot_field, possible_matches in invalid_mappings:
        print(f"\n❌ {sql_field} -> {bad_hubspot_field} (NO EXISTE)")
        if possible_matches:
            print(f"   💡 Alternativas posibles:")
            for match in possible_matches:
                print(f"      - {match}")
        else:
            print(f"   ⚠️  Sin alternativas obvias encontradas")
    
    print(f"\n=== 📊 RESUMEN ===")
    print(f"Mapeos válidos: {len(valid_mappings)}")
    print(f"Mapeos inválidos: {len(invalid_mappings)}")
    success_rate = (len(valid_mappings) / len(csv_mapping)) * 100
    print(f"Tasa de éxito: {success_rate:.1f}%")

if __name__ == "__main__":
    main()
