#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                            HUBSPOT TICKETS PIPELINES - EXTRACTOR DE ETAPAS DE SOPORTE
================================================================================

Archivo:            hubspot/fetch_tickets_pipelines.py
Descripción:        Módulo para extraer la estructura de pipelines y stages de tickets
                   desde HubSpot API. Procesa información de etapas de soporte,
                   estados de resolución y flujos de trabajo.

Dependencias:
    - HubSpot API v3
    - Variables de entorno: HUBSPOT_TOKEN
    - Librerías: requests, dotenv, os, pathlib

Autor:              Ing. Jose Ríler Solórzano Campos
Fecha de Creación:  11 de julio de 2025
Derechos de Autor:  © 2025 Jose Ríler Solórzano Campos. Todos los derechos reservados.
Licencia:           Uso exclusivo del autor. Prohibida la distribución sin autorización.

================================================================================
"""

import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def fetch_ticket_pipelines_as_table():
    """
    Obtiene todos los pipelines de tickets y sus stages en formato de lista de diccionarios
    """
    url = "https://api.hubapi.com/crm/v3/pipelines/tickets"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    print("🔄 Obteniendo pipelines de tickets...")
    
    try:
        # ==================== CONSULTA A HUBSPOT API ====================
        # Realizar petición HTTP para obtener pipelines de tickets de soporte
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error obteniendo pipelines de tickets: {response.status_code}")
            print(f"❌ Respuesta: {response.text}")
            return []

        # ==================== PROCESAMIENTO DE RESPUESTA ====================
        # Extraer pipelines de tickets desde la respuesta JSON
        data = response.json()
        pipelines = data.get("results", [])
        
        # ==================== VALIDACIÓN DE DATOS ====================
        # Verificar que se encontraron pipelines de tickets válidos
        if not pipelines:
            print("⚠️ No se encontraron pipelines de tickets")
            return []

        print(f"✅ Pipelines de tickets encontrados: {len(pipelines)}")

        # Construir tabla con información detallada
        tabla = []
        total_stages = 0
        
        for pipeline in pipelines:
            pipeline_id = pipeline.get("id")
            pipeline_label = pipeline.get("label", "Sin nombre")
            pipeline_display_order = pipeline.get("displayOrder", 0)
            pipeline_created = pipeline.get("createdAt", "")
            pipeline_updated = pipeline.get("updatedAt", "")
            pipeline_archived = pipeline.get("archived", False)
            
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
                    "pipeline_archived": pipeline_archived,
                    "stage_id": None,
                    "stage_label": "Sin stages",
                    "stage_display_order": None,
                    "stage_created_at": None,
                    "stage_updated_at": None,
                    "stage_archived": False,
                    "stage_metadata": None
                })
            else:
                # Pipeline con stages
                for stage in stages:
                    # Obtener metadata del stage
                    metadata = stage.get("metadata", {})
                    metadata_str = str(metadata) if metadata else None
                    
                    tabla.append({
                        "pipeline_id": pipeline_id,
                        "pipeline_label": pipeline_label,
                        "pipeline_display_order": pipeline_display_order,
                        "pipeline_created_at": pipeline_created,
                        "pipeline_updated_at": pipeline_updated,
                        "pipeline_archived": pipeline_archived,
                        "stage_id": stage.get("id"),
                        "stage_label": stage.get("label", "Sin nombre"),
                        "stage_display_order": stage.get("displayOrder", 0),
                        "stage_created_at": stage.get("createdAt", ""),
                        "stage_updated_at": stage.get("updatedAt", ""),
                        "stage_archived": stage.get("archived", False),
                        "stage_metadata": metadata_str
                    })

        print(f"📊 Pipelines de tickets procesados: {len(pipelines)}")
        print(f"📊 Total de stages de tickets: {total_stages}")
        print(f"📊 Filas en tabla: {len(tabla)}")
        
        return tabla

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return []

def display_ticket_pipelines_summary(pipelines_data):
    """
    Muestra un resumen de los pipelines de tickets
    """
    if not pipelines_data:
        print("⚠️ No hay datos de pipelines de tickets para mostrar")
        return

    print("\n📊 RESUMEN DE PIPELINES DE TICKETS")
    print("=" * 55)
    
    # Contar pipelines únicos
    unique_pipelines = {}
    for row in pipelines_data:
        pipeline_id = row['pipeline_id']
        if pipeline_id not in unique_pipelines:
            unique_pipelines[pipeline_id] = {
                'name': row['pipeline_label'],
                'stages': 0,
                'archived': row.get('pipeline_archived', False),
                'display_order': row.get('pipeline_display_order', 0)
            }
        
        if row['stage_id'] is not None:
            unique_pipelines[pipeline_id]['stages'] += 1
    
    total_pipelines = len(unique_pipelines)
    total_stages = sum(p['stages'] for p in unique_pipelines.values())
    active_pipelines = len([p for p in unique_pipelines.values() if not p['archived']])
    archived_pipelines = total_pipelines - active_pipelines
    
    print(f"🔹 Total de pipelines de tickets: {total_pipelines}")
    print(f"🔹 Pipelines activos: {active_pipelines}")
    print(f"🔹 Pipelines archivados: {archived_pipelines}")
    print(f"🔹 Total de stages: {total_stages}")
    
    if total_pipelines > 0 and total_stages > 0:
        print(f"🔹 Promedio stages por pipeline: {total_stages/total_pipelines:.1f}")
    
    # Mostrar cada pipeline
    print("\n📋 PIPELINES DE TICKETS Y SUS STAGES:")
    
    # Ordenar por display_order
    sorted_pipelines = sorted(unique_pipelines.items(), 
                            key=lambda x: x[1]['display_order'])
    
    for idx, (pipeline_id, info) in enumerate(sorted_pipelines, 1):
        status = "📦" if info['archived'] else "✅"
        print(f"   {idx}. {status} {info['name']} (ID: {pipeline_id})")
        print(f"      └─ Stages: {info['stages']}, Orden: {info['display_order']}")

def get_ticket_pipelines_metadata():
    """
    Función para obtener metadata de los pipelines de tickets (para compatibilidad)
    """
    pipelines_data = fetch_ticket_pipelines_as_table()
    if not pipelines_data:
        return {}
    
    unique_pipelines = set(row['pipeline_id'] for row in pipelines_data)
    unique_stages = set(row['stage_id'] for row in pipelines_data if row['stage_id'] is not None)
    pipeline_names = list(set(row['pipeline_label'] for row in pipelines_data))
    active_pipelines = len([row for row in pipelines_data 
                           if not row.get('pipeline_archived', False)])
    
    metadata = {
        "total_pipelines": len(unique_pipelines),
        "active_pipelines": active_pipelines,
        "archived_pipelines": len(unique_pipelines) - active_pipelines,
        "total_stages": len(unique_stages),
        "pipeline_names": pipeline_names,
        "columns": list(pipelines_data[0].keys()) if pipelines_data else []
    }
    
    return metadata

def analyze_ticket_stages_distribution(pipelines_data):
    """
    Analiza la distribución de stages por pipeline
    """
    if not pipelines_data:
        return {}
    
    pipeline_stage_count = {}
    
    for row in pipelines_data:
        pipeline_id = row['pipeline_id']
        pipeline_name = row['pipeline_label']
        
        if pipeline_id not in pipeline_stage_count:
            pipeline_stage_count[pipeline_id] = {
                'name': pipeline_name,
                'stages': 0,
                'archived': row.get('pipeline_archived', False)
            }
        
        if row['stage_id'] is not None:
            pipeline_stage_count[pipeline_id]['stages'] += 1
    
    return pipeline_stage_count

def main():
    """
    Función principal para ejecutar el script directamente
    """
    print("🚀 HUBSPOT TICKET PIPELINES FETCHER")
    print("=" * 55)
    
    # Verificar token
    token = os.getenv('HUBSPOT_TOKEN')
    if not token:
        print("❌ Error: No se encontró HUBSPOT_TOKEN en las variables de entorno")
        return

    print(f"🔐 Token configurado: {'*' * 20}{token[-4:]}")

    # Obtener pipelines de tickets
    pipelines_data = fetch_ticket_pipelines_as_table()
    
    if not pipelines_data:
        print("⚠️ No se obtuvieron pipelines de tickets")
        return

    # Mostrar resumen
    display_ticket_pipelines_summary(pipelines_data)
    
    # Análisis adicional
    stage_distribution = analyze_ticket_stages_distribution(pipelines_data)
    
    print(f"\n📈 DISTRIBUCIÓN DE STAGES POR PIPELINE:")
    for pipeline_id, info in stage_distribution.items():
        status = "📦" if info['archived'] else "🎫"
        print(f"   {status} {info['name']}: {info['stages']} stages")
    
    # Mostrar algunos registros de ejemplo
    print("\n📋 MUESTRA DE DATOS (primeros 3):")
    for i, row in enumerate(pipelines_data[:3], 1):
        status = "📦" if row.get('pipeline_archived') else "🎫"
        print(f"\n   {i}. {status} Pipeline: {row['pipeline_label']}")
        if row['stage_id']:
            print(f"      Stage: {row['stage_label']} (ID: {row['stage_id']})")
        else:
            print(f"      Stage: {row['stage_label']}")

if __name__ == "__main__":
    main()