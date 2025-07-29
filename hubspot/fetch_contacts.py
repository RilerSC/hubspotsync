#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                            HUBSPOT CONTACTS - EXTRACTOR DE CONTACTOS
================================================================================

Archivo:            hubspot/fetch_contacts.py
Descripción:        Módulo especializado para la extracción y procesamiento de
                   contactos desde la API de HubSpot. Incluye análisis dinámico
                   de propiedades, extracción por lotes optimizada y manejo
                   robusto de grandes volúmenes de datos de contactos.

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
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from tabulate import tabulate
import time

# Cargar variables de entorno
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Lista que se llenará dinámicamente solo con propiedades que tienen datos
CONTACT_PROPERTIES = []

def get_all_contact_properties():
    """
    Obtiene todas las propiedades disponibles para contacts
    """
    url = "https://api.hubapi.com/crm/v3/properties/contacts"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    print("🔍 Obteniendo lista de propiedades de contactos...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Error obteniendo propiedades: {response.status_code}")
            return []

        data = response.json()
        properties = [prop.get("name") for prop in data.get("results", []) if prop.get("name")]
        print(f"✅ Propiedades de contactos disponibles: {len(properties)}")
        return properties

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

def analyze_all_contact_properties_in_chunks():
    """
    Analiza TODAS las propiedades de contactos en lotes para encontrar cuáles tienen datos
    """
    all_properties = get_all_contact_properties()
    
    if not all_properties:
        print("❌ No se pudieron obtener las propiedades")
        return []

    print(f"🎯 Analizando TODAS las {len(all_properties)} propiedades de contactos en lotes...")
    
    # Dividir en chunks de 80 propiedades
    chunk_size = 80
    properties_with_data = []
    
    for i in range(0, len(all_properties), chunk_size):
        chunk = all_properties[i:i+chunk_size]
        print(f"📦 Analizando lote {i//chunk_size + 1}/{(len(all_properties)-1)//chunk_size + 1}: {len(chunk)} propiedades")
        
        chunk_results = analyze_contact_chunk_with_post(chunk, chunk_number=i//chunk_size + 1)
        if chunk_results:
            properties_with_data.extend(chunk_results)
        
        # Pequeña pausa para no sobrecargar la API
        time.sleep(0.5)
    
    # Remover duplicados y ordenar
    properties_with_data = list(set(properties_with_data))
    print(f"🎉 TOTAL de propiedades de contactos con datos: {len(properties_with_data)}")
    
    return properties_with_data

def analyze_contact_chunk_with_post(properties_chunk, chunk_number=1):
    """
    Analiza un lote de propiedades de contactos usando POST
    """
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    # Payload para POST
    payload = {
        "limit": 100,  # Más contactos para análisis más preciso
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
        sample_contacts = data.get("results", [])
        
        if not sample_contacts:
            print(f"⚠️ Lote {chunk_number}: Sin contactos obtenidos")
            return []

        # Analizar qué propiedades de este chunk tienen datos
        chunk_properties_with_data = analyze_contact_properties_in_chunk(sample_contacts, properties_chunk)
        
        print(f"✅ Lote {chunk_number}: {len(chunk_properties_with_data)}/{len(properties_chunk)} propiedades con datos")
        
        return chunk_properties_with_data

    except Exception as e:
        print(f"❌ Error en lote {chunk_number}: {str(e)}")
        return []

def analyze_contact_properties_in_chunk(sample_contacts, properties_chunk):
    """
    Analiza un lote específico de contactos para ver qué propiedades tienen datos
    """
    if not sample_contacts:
        return []

    # Contar propiedades que tienen valores no vacíos
    property_stats = {}
    
    for contact in sample_contacts:
        props = contact.get("properties", {})
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
            if percentage >= 1.0:  # Al menos 1% de los contactos tienen esta propiedad
                properties_with_data.append(prop_name)

    return properties_with_data

def fetch_contacts_from_hubspot():
    """
    Función principal para extracción completa de contactos desde HubSpot API.
    
    Descripción:
        Coordina el proceso completo de extracción de contactos, desde el análisis
        dinámico de propiedades hasta la obtención de datos completos. Esta función
        maneja grandes volúmenes de contactos (típicamente 5000+) de manera optimizada.
        
    Flujo de Procesamiento:
        1. Ejecuta análisis completo de propiedades con analyze_all_contact_properties_in_chunks()
        2. Identifica ~260 propiedades útiles de ~568 disponibles (46% optimización)
        3. Actualiza variable global CONTACT_PROPERTIES con propiedades filtradas
        4. Ejecuta extracción masiva usando fetch_all_contacts_with_post()
        5. Retorna lista completa de contactos con propiedades optimizadas
        
    Estrategia de Optimización:
        - Análisis dinámico: Solo extrae propiedades que contienen datos reales
        - Fallback robusto: Usa propiedades básicas si falla el análisis
        - Procesamiento por lotes: Maneja eficientemente grandes volúmenes
        
    Dependencias:
        - analyze_all_contact_properties_in_chunks(): Para análisis de propiedades
        - fetch_all_contacts_with_post(): Para extracción masiva optimizada
        - Variable global CONTACT_PROPERTIES: Para almacenar propiedades útiles
        
    Retorna:
        list: Lista de diccionarios con contactos y sus propiedades
        list vacía: En caso de error o no encontrar datos
        
    Efectos Secundarios:
        - Actualiza CONTACT_PROPERTIES global
        - Imprime estadísticas de progreso en consola
        
    Uso desde main.py:
        contacts = fetch_contacts_from_hubspot()
        
    Performance:
        Tiempo estimado: 3-4 minutos para ~5000 contactos con ~260 propiedades
        
    Volumen Típico:
        - Contactos: ~5000 registros
        - Propiedades analizadas: ~260 de 568 disponibles
        - Eficiencia: ~54% de optimización en propiedades
    """
    # ==================== FASE 1: ANÁLISIS DE PROPIEDADES ====================
    # Analizar TODAS las propiedades disponibles para encontrar las útiles
    print("🚀 Iniciando análisis COMPLETO de propiedades de CONTACTOS...")
    properties_with_data = analyze_all_contact_properties_in_chunks()
    
    # ==================== FALLBACK: PROPIEDADES BÁSICAS ====================
    # Si falla el análisis, usar conjunto mínimo de propiedades esenciales para contactos
    if not properties_with_data:
        print("⚠️ No se pudo analizar propiedades. Usando básicas...")
        properties_with_data = [
            "hs_object_id", "email", "firstname", "lastname", "phone", 
            "company", "createdate", "lastmodifieddate", "hubspot_owner_id"
        ]
    
    # ==================== ACTUALIZACIÓN DE VARIABLE GLOBAL ====================
    # Actualizar la lista global para uso en otras funciones del módulo
    global CONTACT_PROPERTIES
    CONTACT_PROPERTIES = properties_with_data
    
    print(f"\n🎯 Obteniendo TODOS los contactos con {len(properties_with_data)} propiedades útiles...")
    
    # Usar POST para obtener todos los contactos
    return fetch_all_contacts_with_post(properties_with_data)

def fetch_all_contacts_with_post(properties_list):
    """
    Obtiene todos los contactos usando POST dividiendo las propiedades si es necesario
    """
    # Si hay demasiadas propiedades, hacer múltiples calls
    if len(properties_list) > 100:
        print(f"⚠️ Demasiadas propiedades ({len(properties_list)}), dividiendo en lotes...")
        return fetch_contacts_in_property_batches(properties_list)
    
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }

    all_contacts = []
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
            contacts = data.get("results", [])
            all_contacts.extend(contacts)
            page_count += 1
            
            print(f"📄 Página {page_count}: {len(contacts)} contactos obtenidos (Total: {len(all_contacts)})")

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

    print(f"✅ Total de contactos obtenidos: {len(all_contacts)}")
    return all_contacts

def fetch_contacts_in_property_batches(properties_list):
    """
    Obtiene contactos en lotes de propiedades y luego los combina
    """
    print(f"📦 Dividiendo {len(properties_list)} propiedades en lotes de 80...")
    
    # Propiedades esenciales que deben estar en todos los lotes
    essential_props = ["hs_object_id"]
    
    # Dividir propiedades no esenciales en lotes
    non_essential = [p for p in properties_list if p not in essential_props]
    batch_size = 80
    
    all_contacts_data = {}  # Diccionario para combinar datos por ID
    
    for i in range(0, len(non_essential), batch_size):
        batch_props = essential_props + non_essential[i:i+batch_size]
        batch_num = i//batch_size + 1
        total_batches = (len(non_essential)-1)//batch_size + 1
        
        print(f"📦 Procesando lote {batch_num}/{total_batches} con {len(batch_props)} propiedades...")
        
        batch_contacts = fetch_all_contacts_with_post(batch_props)
        
        # Combinar datos por ID
        for contact in batch_contacts:
            contact_id = contact.get("properties", {}).get("hs_object_id")
            if contact_id:
                if contact_id not in all_contacts_data:
                    all_contacts_data[contact_id] = {"properties": {}}
                
                # Combinar propiedades
                all_contacts_data[contact_id]["properties"].update(contact.get("properties", {}))
        
        print(f"✅ Lote {batch_num} procesado. Contactos únicos acumulados: {len(all_contacts_data)}")
    
    # Convertir diccionario de vuelta a lista
    combined_contacts = list(all_contacts_data.values())
    print(f"🎯 Combinación completa: {len(combined_contacts)} contactos con datos completos")
    
    return combined_contacts

def get_all_contact_properties_list():
    """
    Función para obtener la lista de propiedades que tienen datos
    """
    return CONTACT_PROPERTIES

def display_contacts_summary(contacts):
    """
    Muestra un resumen extendido de contactos
    """
    if not contacts:
        print("⚠️ No hay contactos para mostrar")
        return

    print(f"\n📊 RESUMEN EXTENDIDO DE CONTACTOS ({len(contacts)} total)")
    print("=" * 60)
    
    # Crear DataFrame para análisis
    all_props_data = []
    for contact in contacts:
        all_props_data.append(contact.get("properties", {}))
    
    df = pd.DataFrame(all_props_data)
    
    # Mostrar estadísticas de completitud de datos
    print("\n📈 ESTADÍSTICAS DE COMPLETITUD DE DATOS:")
    prop_stats = []
    for col in df.columns:
        actual_data_count = ((df[col].notna()) & (df[col] != "") & (df[col] != "None")).sum()
        
        if actual_data_count > 0:
            prop_stats.append({
                "propiedad": col,
                "con_datos": actual_data_count,
                "porcentaje": (actual_data_count / len(df)) * 100
            })
    
    # Ordenar por porcentaje
    prop_stats.sort(key=lambda x: x["porcentaje"], reverse=True)
    
    # Mostrar top 15
    print("\n🔝 TOP 15 PROPIEDADES DE CONTACTOS CON MÁS DATOS:")
    for i, stat in enumerate(prop_stats[:15], 1):
        print(f"   {i:2d}. {stat['propiedad']:<30} {stat['porcentaje']:5.1f}% ({stat['con_datos']}/{len(df)})")
    
    # Estadísticas generales
    total_props = len(CONTACT_PROPERTIES)
    props_with_50_percent = len([p for p in prop_stats if p["porcentaje"] >= 50])
    props_with_10_percent = len([p for p in prop_stats if p["porcentaje"] >= 10])
    
    print(f"\n📊 RESUMEN DE PROPIEDADES:")
    print(f"   🎯 Total de propiedades útiles: {total_props}")
    print(f"   💪 Con datos en >50% de contactos: {props_with_50_percent}")
    print(f"   📈 Con datos en >10% de contactos: {props_with_10_percent}")
    print(f"   📉 Con datos en <10% de contactos: {total_props - props_with_10_percent}")

def main():
    """
    Función principal para ejecutar el script directamente
    """
    print("🚀 HUBSPOT CONTACTS FETCHER - ANÁLISIS COMPLETO DE TODAS LAS PROPIEDADES")
    print("=" * 80)
    
    # Verificar token
    token = os.getenv('HUBSPOT_TOKEN')
    if not token:
        print("❌ Error: No se encontró HUBSPOT_TOKEN en las variables de entorno")
        return

    # Obtener contactos con análisis completo
    contacts = fetch_contacts_from_hubspot()
    
    if not contacts:
        print("⚠️ No se obtuvieron contactos")
        return

    # Mostrar resumen extendido
    display_contacts_summary(contacts)

if __name__ == "__main__":
    main()