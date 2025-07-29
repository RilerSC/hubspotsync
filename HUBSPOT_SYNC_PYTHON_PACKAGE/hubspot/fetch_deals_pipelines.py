import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def fetch_deal_pipelines_as_table():
    """
    Obtiene todos los pipelines de deals y sus stages en formato de lista de diccionarios
    """
    url = "https://api.hubapi.com/crm/v3/pipelines/deals"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    print("🔄 Obteniendo pipelines de deals...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error obteniendo pipelines: {response.status_code}")
            print(f"❌ Respuesta: {response.text}")
            return []

        data = response.json()
        pipelines = data.get("results", [])
        
        if not pipelines:
            print("⚠️ No se encontraron pipelines de deals")
            return []

        print(f"✅ Pipelines de deals encontrados: {len(pipelines)}")

        # Construir tabla con información detallada
        tabla = []
        total_stages = 0
        
        for pipeline in pipelines:
            pipeline_id = pipeline.get("id")
            pipeline_label = pipeline.get("label", "Sin nombre")
            pipeline_display_order = pipeline.get("displayOrder", 0)
            pipeline_created = pipeline.get("createdAt", "")
            pipeline_updated = pipeline.get("updatedAt", "")
            
            stages = pipeline.get("stages", [])
            total_stages += len(stages)
            
            if not stages:
                # Pipeline sin stages - agregar fila con info del pipeline
                tabla.append({
                    "pipeline_id": pipeline_id,
                    "pipeline_label": pipeline_label,
                    "pipeline_display_order": pipeline_display_order,
                    "pipeline_created_at": pipeline_created,
                    "pipeline_updated_at": pipeline_updated,
                    "stage_id": None,
                    "stage_label": "Sin stages",
                    "stage_display_order": None,
                    "stage_created_at": None,
                    "stage_updated_at": None,
                    "stage_probability": 0.0
                })
            else:
                # Pipeline con stages
                for stage in stages:
                    # Obtener probabilidad y convertir a float
                    probability = stage.get("metadata", {}).get("probability", 0)
                    try:
                        probability = float(probability) if probability is not None else 0.0
                    except (ValueError, TypeError):
                        probability = 0.0
                    
                    tabla.append({
                        "pipeline_id": pipeline_id,
                        "pipeline_label": pipeline_label,
                        "pipeline_display_order": pipeline_display_order,
                        "pipeline_created_at": pipeline_created,
                        "pipeline_updated_at": pipeline_updated,
                        "stage_id": stage.get("id"),
                        "stage_label": stage.get("label", "Sin nombre"),
                        "stage_display_order": stage.get("displayOrder", 0),
                        "stage_created_at": stage.get("createdAt", ""),
                        "stage_updated_at": stage.get("updatedAt", ""),
                        "stage_probability": probability
                    })

        print(f"📊 Pipelines procesados: {len(pipelines)}")
        print(f"📊 Total de stages: {total_stages}")
        print(f"📊 Filas en tabla: {len(tabla)}")
        
        return tabla

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return []

def display_pipelines_summary(pipelines_data):
    """
    Muestra un resumen de los pipelines de deals
    """
    if not pipelines_data:
        print("⚠️ No hay datos de pipelines para mostrar")
        return

    print("\n📊 RESUMEN DE PIPELINES DE DEALS")
    print("=" * 50)
    
    # Contar pipelines únicos
    unique_pipelines = {}
    for row in pipelines_data:
        pipeline_id = row['pipeline_id']
        if pipeline_id not in unique_pipelines:
            unique_pipelines[pipeline_id] = {
                'name': row['pipeline_label'],
                'stages': 0,
                'total_probability': 0,
                'valid_stages': 0
            }
        
        if row['stage_id'] is not None:
            unique_pipelines[pipeline_id]['stages'] += 1
            if row['stage_probability'] > 0:
                unique_pipelines[pipeline_id]['total_probability'] += row['stage_probability']
                unique_pipelines[pipeline_id]['valid_stages'] += 1
    
    total_pipelines = len(unique_pipelines)
    total_stages = sum(p['stages'] for p in unique_pipelines.values())
    
    print(f"🔹 Total de pipelines: {total_pipelines}")
    print(f"🔹 Total de stages: {total_stages}")
    
    if total_pipelines > 0 and total_stages > 0:
        print(f"🔹 Promedio stages por pipeline: {total_stages/total_pipelines:.1f}")
    
    # Mostrar cada pipeline
    print("\n📋 PIPELINES Y SUS STAGES:")
    
    for idx, (pipeline_id, info) in enumerate(unique_pipelines.items(), 1):
        avg_prob = (info['total_probability'] / info['valid_stages']) if info['valid_stages'] > 0 else 0.0
        print(f"   {idx}. {info['name']} (ID: {pipeline_id})")
        print(f"      └─ Stages: {info['stages']}, Probabilidad promedio: {avg_prob:.1f}%")

def get_pipelines_metadata():
    """
    Función para obtener metadata de los pipelines (para compatibilidad)
    """
    pipelines_data = fetch_deal_pipelines_as_table()
    if not pipelines_data:
        return {}
    
    unique_pipelines = set(row['pipeline_id'] for row in pipelines_data)
    unique_stages = set(row['stage_id'] for row in pipelines_data if row['stage_id'] is not None)
    pipeline_names = list(set(row['pipeline_label'] for row in pipelines_data))
    
    metadata = {
        "total_pipelines": len(unique_pipelines),
        "total_stages": len(unique_stages),
        "pipeline_names": pipeline_names,
        "columns": list(pipelines_data[0].keys()) if pipelines_data else []
    }
    
    return metadata

def main():
    """
    Función principal para ejecutar el script directamente
    """
    print("🚀 HUBSPOT DEALS PIPELINES FETCHER")
    print("=" * 50)
    
    # Verificar token
    token = os.getenv('HUBSPOT_TOKEN')
    if not token:
        print("❌ Error: No se encontró HUBSPOT_TOKEN en las variables de entorno")
        return

    # Obtener pipelines
    pipelines_data = fetch_deal_pipelines_as_table()
    
    if not pipelines_data:
        print("⚠️ No se obtuvieron pipelines")
        return

    # Mostrar resumen
    display_pipelines_summary(pipelines_data)
    
    # Mostrar algunos registros
    print("\n📋 MUESTRA DE DATOS (primeros 5):")
    for i, row in enumerate(pipelines_data[:5], 1):
        print(f"\n   {i}. Pipeline: {row['pipeline_label']}")
        print(f"      Stage: {row['stage_label']}")
        print(f"      Probabilidad: {row['stage_probability']}%")

if __name__ == "__main__":
    main()