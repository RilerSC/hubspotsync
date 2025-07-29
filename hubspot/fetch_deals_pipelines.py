#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                            HUBSPOT DEALS PIPELINES - EXTRACTOR DE ETAPAS DE VENTAS
================================================================================

Archivo:            hubspot/fetch_deals_pipelines.py
Descripción:        Módulo para extraer la estructura de pipelines y stages de deals
                   desde HubSpot API. Procesa información de etapas de ventas,
                   probabilidades y configuraciones de pipeline.

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

def fetch_deal_pipelines_as_table():
    """
    Función principal para extracción de pipelines y stages de deals desde HubSpot API.
    
    Descripción:
        Obtiene la estructura completa de pipelines de deals desde HubSpot, incluyendo
        todas las etapas (stages) de cada pipeline con sus configuraciones y
        probabilidades de cierre. Formatea los datos como lista de diccionarios
        para compatibilidad directa con funciones de sincronización.
        
    Flujo de Procesamiento:
        1. Consulta endpoint /crm/v3/pipelines/deals de HubSpot API
        2. Extrae información de cada pipeline (id, nombre, orden)
        3. Procesa stages individuales dentro de cada pipeline
        4. Calcula probabilidades de cierre por stage
        5. Estructura datos en formato tabular para base de datos
        
    Estructura de Datos Generada:
        - pipeline_id: ID único del pipeline
        - pipeline_label: Nombre descriptivo del pipeline
        - pipeline_displayOrder: Orden de visualización del pipeline
        - stage_id: ID único del stage dentro del pipeline
        - stage_label: Nombre descriptivo del stage
        - stage_displayOrder: Orden del stage dentro del pipeline
        - stage_probability: Probabilidad de cierre (0.0 - 1.0)
        - stage_closed: Indica si el stage representa cierre
        - stage_metadata: Metadatos adicionales del stage
        - createdAt: Timestamp de creación del pipeline
        - updatedAt: Timestamp de última modificación
        
    Endpoint API:
        GET /crm/v3/pipelines/deals
        
    Dependencias:
        - HubSpot API v3 Pipelines endpoint
        - Variable de entorno: HUBSPOT_TOKEN
        - Librerías: requests para HTTP, os para variables de entorno
        
    Retorna:
        list: Lista de diccionarios con estructura de pipelines y stages
        list vacía: En caso de error o no encontrar pipelines
        
    Uso desde main.py:
        deals_pipelines_data = fetch_deal_pipelines_as_table()
        sync_table_data(deals_pipelines_data, "hb_deals_pipeline")
        
    Performance:
        Tiempo estimado: 1 minuto para ~12 pipelines con ~100 stages totales
        
    Volumen Típico:
        - Pipelines: ~12 pipelines de deals
        - Stages: ~100 stages totales (8-10 por pipeline)
        - Filas generadas: 100 registros en tabla hb_deals_pipeline
        
    Manejo de Errores:
        - Códigos HTTP diferentes a 200
        - Respuestas vacías o malformadas
        - Pipelines sin stages
        - Errores de conexión o timeout
        
    Casos Especiales:
        - Pipelines sin stages: Se omiten del resultado
        - Stages sin probabilidad: Se asigna 0.0 por defecto
        - Metadatos vacíos: Se preservan como campos vacíos
    """
    # ==================== CONFIGURACIÓN DE API ====================
    # Configurar endpoint y headers para consulta de pipelines de deals
    url = "https://api.hubapi.com/crm/v3/pipelines/deals"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    print("🔄 Obteniendo pipelines de deals...")
    
    try:
        # ==================== CONSULTA A HUBSPOT API ====================
        # Realizar petición HTTP para obtener pipelines de deals
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error obteniendo pipelines: {response.status_code}")
            print(f"❌ Respuesta: {response.text}")
            return []

        # ==================== PROCESAMIENTO DE RESPUESTA ====================
        # Extraer pipelines desde la respuesta JSON
        data = response.json()
        pipelines = data.get("results", [])
        
        # ==================== VALIDACIÓN DE DATOS ====================
        # Verificar que se encontraron pipelines válidos
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