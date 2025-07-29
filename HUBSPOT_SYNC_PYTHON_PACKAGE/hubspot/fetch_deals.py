import os
import requests
from dotenv import load_dotenv
from pathlib import Path
import time

# Cargar variables de entorno
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Lista que se llenará dinámicamente solo con propiedades que tienen datos
DEAL_PROPERTIES = []

def get_all_deal_properties():
    """
    Obtiene todas las propiedades disponibles para deals
    """
    url = "https://api.hubapi.com/crm/v3/properties/deals"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    print("🔍 Obteniendo lista de propiedades disponibles...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error obteniendo propiedades: {response.status_code}")
            return []

        data = response.json()
        properties = [prop.get("name") for prop in data.get("results", []) if prop.get("name")]
        print(f"✅ Propiedades disponibles: {len(properties)}")
        return properties

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def analyze_all_properties_in_chunks():
    """
    Analiza TODAS las propiedades en lotes más grandes para encontrar cuáles tienen datos
    """
    all_properties = get_all_deal_properties()
    
    if not all_properties:
        print("❌ No se pudieron obtener las propiedades")
        return []

    print(f"🎯 Analizando TODAS las {len(all_properties)} propiedades en lotes...")
    
    # Dividir en chunks de 80 propiedades (más agresivo)
    chunk_size = 80
    properties_with_data = []
    
    for i in range(0, len(all_properties), chunk_size):
        chunk = all_properties[i:i+chunk_size]
        print(f"📦 Analizando lote {i//chunk_size + 1}/{(len(all_properties)-1)//chunk_size + 1}: {len(chunk)} propiedades")
        
        chunk_results = analyze_chunk_with_post(chunk, chunk_number=i//chunk_size + 1)
        if chunk_results:
            properties_with_data.extend(chunk_results)
        
        # Pequeña pausa para no sobrecargar la API
        time.sleep(0.5)
    
    # Remover duplicados y ordenar
    properties_with_data = list(set(properties_with_data))
    print(f"🎉 TOTAL de propiedades con datos encontradas: {len(properties_with_data)}")
    
    return properties_with_data

def analyze_chunk_with_post(properties_chunk, chunk_number=1):
    """
    Analiza un lote de propiedades usando POST
    """
    url = "https://api.hubapi.com/crm/v3/objects/deals/search"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    # Payload para POST
    payload = {
        "limit": 100,  # Más deals para análisis más preciso
        "properties": properties_chunk,
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "hs_object_id",
                        "operator": "HAS_PROPERTY"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"❌ Error en lote {chunk_number}: {response.status_code}")
            return []

        data = response.json()
        sample_deals = data.get("results", [])
        
        if not sample_deals:
            print(f"⚠️ Lote {chunk_number}: Sin deals obtenidos")
            return []

        # Analizar qué propiedades de este chunk tienen datos
        chunk_properties_with_data = analyze_properties_in_chunk(sample_deals, properties_chunk)
        
        print(f"✅ Lote {chunk_number}: {len(chunk_properties_with_data)}/{len(properties_chunk)} propiedades con datos")
        
        return chunk_properties_with_data

    except Exception as e:
        print(f"❌ Error en lote {chunk_number}: {str(e)}")
        return []

def analyze_properties_in_chunk(sample_deals, properties_chunk):
    """
    Analiza un lote específico de deals para ver qué propiedades tienen datos - SIN PANDAS
    """
    if not sample_deals:
        return []

    # Contar propiedades que tienen valores no vacíos - SIN PANDAS
    property_stats = {}
    
    for deal in sample_deals:
        props = deal.get("properties", {})
        for prop_name in properties_chunk:
            prop_value = props.get(prop_name)
            
            if prop_name not in property_stats:
                property_stats[prop_name] = {"total": 0, "with_data": 0}
            
            property_stats[prop_name]["total"] += 1
            
            # Verificar si tiene datos reales
            if prop_value and str(prop_value).strip() and str(prop_value) not in ["None", "null", ""]:
                property_stats[prop_name]["with_data"] += 1

    # Filtrar propiedades que tienen datos en al menos el 1% de los registros
    properties_with_data = []
    for prop_name, stats in property_stats.items():
        if stats["with_data"] > 0:  # Al menos 1 registro con datos
            percentage = (stats["with_data"] / stats["total"]) * 100
            if percentage >= 1.0:  # Al menos 1% de los deals tienen esta propiedad
                properties_with_data.append(prop_name)

    return properties_with_data

def fetch_deals_from_hubspot():
    """
    Obtiene todos los deals con TODAS las propiedades que tienen datos
    """
    # Analizar TODAS las propiedades
    print("🚀 Iniciando análisis COMPLETO de propiedades...")
    properties_with_data = analyze_all_properties_in_chunks()
    
    if not properties_with_data:
        print("⚠️ No se pudo analizar propiedades. Usando básicas...")
        properties_with_data = [
            "hs_object_id", "dealname", "amount", "dealstage", "pipeline", 
            "closedate", "createdate", "hubspot_owner_id", "dealtype"
        ]
    
    # Actualizar la lista global
    global DEAL_PROPERTIES
    DEAL_PROPERTIES = properties_with_data
    
    print(f"\n🎯 Obteniendo TODOS los deals con {len(properties_with_data)} propiedades útiles...")
    print(f"📊 Esto representa {len(properties_with_data)/905*100:.1f}% de todas las propiedades disponibles")
    
    # Usar POST para obtener todos los deals
    return fetch_all_deals_with_post(properties_with_data)

def fetch_all_deals_with_post(properties_list):
    """
    Obtiene todos los deals usando POST dividiendo las propiedades si es necesario
    """
    # Si hay demasiadas propiedades, hacer múltiples calls
    if len(properties_list) > 100:
        print(f"⚠️ Demasiadas propiedades ({len(properties_list)}), dividiendo en lotes...")
        return fetch_deals_in_property_batches(properties_list)
    
    url = "https://api.hubapi.com/crm/v3/objects/deals/search"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    all_deals = []
    after = None
    page_count = 0

    while True:
        # Payload para POST
        payload = {
            "limit": 100,
            "properties": properties_list,
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "hs_object_id",
                            "operator": "HAS_PROPERTY"
                        }
                    ]
                }
            ]
        }
        
        # Agregar paginación si existe
        if after:
            payload["after"] = after

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code}")
                print(f"❌ Respuesta: {response.text}")
                break

            data = response.json()
            deals = data.get("results", [])
            all_deals.extend(deals)
            page_count += 1
            
            print(f"📄 Página {page_count}: {len(deals)} deals obtenidos (Total: {len(all_deals)})")

            # Verificar si hay más páginas
            paging = data.get("paging")
            if paging and paging.get("next") and paging["next"].get("after"):
                after = paging["next"]["after"]
            else:
                break

        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la petición: {str(e)}")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            break

    print(f"✅ Total de deals obtenidos: {len(all_deals)}")
    return all_deals

def fetch_deals_in_property_batches(properties_list):
    """
    Obtiene deals en lotes de propiedades y luego los combina - SIN PANDAS
    """
    print(f"📦 Dividiendo {len(properties_list)} propiedades en lotes de 80...")
    
    # Propiedades esenciales que deben estar en todos los lotes
    essential_props = ["hs_object_id"]
    
    # Dividir propiedades no esenciales en lotes
    non_essential = [p for p in properties_list if p not in essential_props]
    batch_size = 80
    
    all_deals_data = {}  # Diccionario para combinar datos por ID
    
    for i in range(0, len(non_essential), batch_size):
        batch_props = essential_props + non_essential[i:i+batch_size]
        batch_num = i//batch_size + 1
        total_batches = (len(non_essential)-1)//batch_size + 1
        
        print(f"📦 Procesando lote {batch_num}/{total_batches} con {len(batch_props)} propiedades...")
        
        batch_deals = fetch_all_deals_with_post(batch_props)
        
        # Combinar datos por ID - SIN PANDAS
        for deal in batch_deals:
            deal_id = deal.get("properties", {}).get("hs_object_id")
            if deal_id:
                if deal_id not in all_deals_data:
                    all_deals_data[deal_id] = {"properties": {}}
                
                # Combinar propiedades
                all_deals_data[deal_id]["properties"].update(deal.get("properties", {}))
        
        print(f"✅ Lote {batch_num} procesado. Deals únicos acumulados: {len(all_deals_data)}")
    
    # Convertir diccionario de vuelta a lista
    combined_deals = list(all_deals_data.values())
    print(f"🎯 Combinación completa: {len(combined_deals)} deals con datos completos")
    
    return combined_deals

def get_all_deal_properties_list():
    """
    Función para obtener la lista de propiedades que tienen datos
    """
    return DEAL_PROPERTIES

def display_extended_summary(deals):
    """
    Muestra un resumen extendido con más detalles - SIN PANDAS
    """
    if not deals:
        print("⚠️ No hay deals para mostrar")
        return

    print(f"\n📊 RESUMEN EXTENDIDO DE DEALS ({len(deals)} total)")
    print("=" * 60)
    
    # Análisis manual SIN PANDAS
    all_properties = set()
    deals_data = []
    
    for deal in deals:
        props = deal.get("properties", {})
        deals_data.append(props)
        all_properties.update(props.keys())
    
    print(f"\n📈 ESTADÍSTICAS DE COMPLETITUD DE DATOS:")
    
    # Calcular estadísticas manualmente
    prop_stats = []
    for prop_name in all_properties:
        total_count = len(deals_data)
        with_data_count = 0
        
        for props in deals_data:
            value = props.get(prop_name)
            if value and str(value).strip() and str(value) not in ["None", "null", ""]:
                with_data_count += 1
        
        if with_data_count > 0:
            percentage = (with_data_count / total_count) * 100
            prop_stats.append({
                "propiedad": prop_name,
                "con_datos": with_data_count,
                "porcentaje": percentage
            })
    
    # Ordenar por porcentaje
    prop_stats.sort(key=lambda x: x["porcentaje"], reverse=True)
    
    # Mostrar top 15
    print("\n🔝 TOP 15 PROPIEDADES CON MÁS DATOS:")
    for i, stat in enumerate(prop_stats[:15], 1):
        print(f"   {i:2d}. {stat['propiedad']:<30} {stat['porcentaje']:5.1f}% ({stat['con_datos']}/{len(deals_data)})")
    
    # Estadísticas generales
    total_props = len(DEAL_PROPERTIES)
    props_with_50_percent = len([p for p in prop_stats if p["porcentaje"] >= 50])
    props_with_10_percent = len([p for p in prop_stats if p["porcentaje"] >= 10])
    
    print(f"\n📊 RESUMEN DE PROPIEDADES:")
    print(f"   🎯 Total de propiedades útiles: {total_props}")
    print(f"   💪 Con datos en >50% de deals: {props_with_50_percent}")
    print(f"   📈 Con datos en >10% de deals: {props_with_10_percent}")
    print(f"   📉 Con datos en <10% de deals: {total_props - props_with_10_percent}")

    # Agregar estadísticas específicas de deals
    deals_by_stage = {}
    deals_by_pipeline = {}
    total_amount = 0
    deals_with_amount = 0
    
    for props in deals_data:
        # Analizar por stage
        stage = props.get("dealstage", "Sin stage")
        deals_by_stage[stage] = deals_by_stage.get(stage, 0) + 1
        
        # Analizar por pipeline
        pipeline = props.get("pipeline", "Sin pipeline")
        deals_by_pipeline[pipeline] = deals_by_pipeline.get(pipeline, 0) + 1
        
        # Analizar amounts
        amount = props.get("amount")
        if amount and str(amount).replace(".", "").replace(",", "").isdigit():
            try:
                total_amount += float(amount)
                deals_with_amount += 1
            except (ValueError, TypeError):
                pass
    
    print(f"\n💰 ESTADÍSTICAS DE DEALS:")
    print(f"   📊 Total de deals: {len(deals_data)}")
    print(f"   💵 Deals con monto: {deals_with_amount}")
    if deals_with_amount > 0:
        avg_amount = total_amount / deals_with_amount
        print(f"   💰 Monto total: ${total_amount:,.2f}")
        print(f"   📈 Monto promedio: ${avg_amount:,.2f}")
    
    print(f"   🎯 Stages únicos: {len(deals_by_stage)}")
    print(f"   📋 Pipelines únicos: {len(deals_by_pipeline)}")

def main():
    """
    Función principal para ejecutar el script directamente
    """
    print("🚀 HUBSPOT DEALS FETCHER - ANÁLISIS COMPLETO SIN PANDAS")
    print("=" * 70)
    
    # Verificar token
    token = os.getenv('HUBSPOT_TOKEN')
    if not token:
        print("❌ Error: No se encontró HUBSPOT_TOKEN en las variables de entorno")
        return

    print(f"🔐 Token configurado: {'*' * 20}{token[-4:]}")

    # Obtener deals con análisis completo
    deals = fetch_deals_from_hubspot()
    
    if not deals:
        print("⚠️ No se obtuvieron deals")
        return

    # Mostrar resumen extendido
    display_extended_summary(deals)

if __name__ == "__main__":
    main()