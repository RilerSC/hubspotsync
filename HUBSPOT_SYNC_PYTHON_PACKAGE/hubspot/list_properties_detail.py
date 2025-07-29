import pandas as pd
import requests
import os
from dotenv import load_dotenv
from tabulate import tabulate

# Cargar variables desde .env
load_dotenv()
ACCESS_TOKEN = os.getenv('HUBSPOT_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("No se encontró HUBSPOT_TOKEN en el archivo .env")

# Lista de propiedades deseadas
mis_propiedades = ["hubspot_owner_id",
"hubspot_owner_assigneddate",
"hubspot_owner_id",
"numero_asociado",
"no__de_cedula",
"firstname",
"lastname",
"nombre_y_apellidos",
"estado_del_asociado",
"date_of_birth",
"email",
"work_email",
"hs_whatsapp_phone_number",
"telefono_de_habitacion",
"telefono_de_oficina",
"puesto",
"salario_bruto_semanal_o_quincenal",
"salario_neto_semanal_o_quincenal",
"estado_civil",
"marital_status",
"cantidad_de_hijos",
"institucion_en_la_que_labora",
"oficina",
"provincia",
"canton",
"distrito",
"fecha_de_tu_ingreso",
"con_ahorro",
"con_ahorro_economias",
"con_ahorro_navideno",
"con_plan_fin_de_ano",
"con_ahorro_fondo_de_inversion",
"con_ahorro_plan_vacacional",
"con_ahorro_plan_aguinaldo",
"con_ahorro_plan_bono_escolar",
"con_ahorro_con_proposito",
"con_ahorro_plan_futuro",
"con_credito",
"con_cred__capital_social",
"con_cred__adelanto_de_pension",
"con_cred__consumo_personal",
"con_cred__salud",
"con_cred__especial_al_vencimiento",
"con_cred__facilito",
"con_cred__refundicion_de_pasivos",
"con_cred_vivienda_patrimonial",
"con_cred__refuncion_2",
"con_cred__capitalizable_3",
"con_cred__tecnologico",
"con_credifacil",
"con_cred__vivienda_cooperativa",
"con_cred__multiuso",
"con_cred__deuda_unica",
"con_cred__vivienda_constructivo",
"con_cred__vehiculo_nuevos",
"con_cred__back_to_back",
"con_seguro",
"con_seg__apoyo_funerario",
"con_seg__su_vida",
"con_poliza_colectiva",
"con_cesantia",
"con_cip", #aquí termina la consulta útil
"detalles_de_la_direccion",
"numero_de_cuenta_bancaria",
"address",
"periodiciadad_de_la_deduccion",
"nombre_y_apellidos__beneficiario_1_apoyo_funerario_",
"nombre_y_apellidos__beneficiario_2_",
"nombre_y_apellidos__beneficiario_2_apoyo_funerario_",
"nombre_y_apellidos__beneficiario_3_",
"nombre_y_apellidos__beneficiario_3_apoyo_funerario_",
"nombre_y_apellidos__beneficiario_4_apoyo_funerario_",
"nombre_y_apellidos__beneficiario_5_apoyo_funerario_",
"nombre_y_apellidos__beneficiario_6_apoyo_funerario_",
"nombre_y_apellidos__beneficiario_7_apoyo_funerario_",
"numero_de_cedula__beneficiario_1_",
"numero_de_cedula__beneficiario_2_",
"numero_de_cedula__beneficiario_3_",
"numero_de_cuenta_bancaria",
"plan_seguro_apoyo_funerario",
"plan_seguro_su_vida",
"plazo_del_ahorro_en_meses",
"plazo_del_tu_certificado",
"porcentaje__beneficiario_1_",
"porcentaje__beneficiario_2_",
"porcentaje__beneficiario_3_"
]

# Consultar propiedades desde HubSpot
url = 'https://api.hubapi.com/crm/v3/properties/contacts'
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    propiedades = response.json().get('results', [])

    # Filtrar solo las que están en la lista deseada
    tabla = []
    for prop in propiedades:
        if prop.get('name') in mis_propiedades:
            tabla.append({
                'Nombre de Propiedad': prop.get('name', ''),
                'Tipo': prop.get('type', '')
            })

    print(f"✅ Propiedades encontradas: {len(tabla)}\n")
    print(tabulate(tabla, headers="keys", tablefmt="fancy_grid", showindex=True))


    # Exportar a CSV
    df= pd.DataFrame(tabla)
    df.to_csv("hubspot_detailExport_properties.csv", index=False, encoding="utf-8-sig")
    print("\n Archivo exportado como 'hubspot_detailExport_properties.csv'")

else:
    print(f"❌ Error {response.status_code}: {response.text}")