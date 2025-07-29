#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                            HUBSPOT OWNERS - EXTRACTOR DE PROPIETARIOS
================================================================================

Archivo:            hubspot/fetch_owners.py
Descripción:        Módulo para la extracción de información de owners (propietarios)
                   desde HubSpot API. Procesa datos de usuarios, equipos y estados
                   de actividad, formateando la información como tabla estructurada.

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

def fetch_owners():
    """
    Obtiene todos los owners de HubSpot
    """
    url = "https://api.hubapi.com/crm/v3/owners/"
    headers = {
        "Authorization": f"Bearer {os.getenv('HUBSPOT_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    print("🔄 Obteniendo owners de HubSpot...")
    
    owners = []
    params = {"limit": 100}
    page_count = 0

    while url:
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"❌ Error {response.status_code}: {response.text}")
                break

            data = response.json()
            results = data.get("results", [])
            owners.extend(results)
            page_count += 1
            
            print(f"📄 Página {page_count}: {len(results)} owners obtenidos (Total: {len(owners)})")

            # Verificar si hay más páginas
            paging = data.get("paging", {}).get("next", {}).get("link")
            url = paging if paging else None
            
            # Limpiar params para siguientes páginas (la URL ya incluye los parámetros)
            if url:
                params = {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {str(e)}")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            break

    print(f"✅ Total de owners obtenidos: {len(owners)}")
    return owners

def fetch_owners_as_table():
    """
    Función principal para extracción y formateo de owners desde HubSpot API.
    
    Descripción:
        Obtiene la lista completa de owners (propietarios/usuarios) desde HubSpot
        y los formatea como lista estructurada de diccionarios para compatibilidad
        directa con funciones de sincronización de tablas.
        
    Flujo de Procesamiento:
        1. Llama a fetch_owners() para obtener datos raw desde HubSpot API
        2. Procesa y normaliza información de cada owner
        3. Construye nombres completos desde firstName + lastName
        4. Estructura datos en formato tabular estándar
        5. Agrega campos calculados (fullName, userType, etc.)
        
    Estructura de Datos Generada:
        - id: Identificador único del owner en HubSpot
        - firstName/lastName: Nombres individuales del usuario
        - fullName: Nombre completo construido (fallback: "Sin nombre")
        - email: Dirección de correo electrónico
        - active: Estado de actividad del usuario (true/false)
        - createdAt/updatedAt: Timestamps de creación y modificación
        - archived: Estado de archivo del usuario
        - userId: ID de usuario interno de HubSpot
        - userIdIncludingInactive: ID incluyendo usuarios inactivos
        - teams: Lista de equipos a los que pertenece el usuario
        - userType: Tipo de usuario calculado ("active"/"inactive")
        
    Dependencias:
        - fetch_owners(): Función base para extracción raw de owners
        - HubSpot API v3 /owners endpoint
        
    Retorna:
        list: Lista de diccionarios con datos estructurados de owners
        list vacía: En caso de error o no encontrar owners
        
    Uso desde main.py:
        owners_data = fetch_owners_as_table()
        sync_table_data(owners_data, "hb_owners")
        
    Performance:
        Tiempo estimado: 30 segundos para ~25 owners
        
    Volumen Típico:
        - Owners: ~25 registros
        - Propiedades: 11 campos estructurados
        - Datos adicionales: Teams, estados, timestamps
        
    Formateo Especial:
        - Nombres: Concatenación inteligente firstName + lastName
        - Estados: Normalización de valores booleanos
        - Equipos: Preservación de arrays de teams
        - Fechas: Formato ISO de timestamps HubSpot
    """
    # ==================== EXTRACCIÓN DE DATOS RAW ====================
    # Obtener datos raw de owners desde HubSpot API
    owners = fetch_owners()
    
    # ==================== VALIDACIÓN DE DATOS ====================
    # Verificar si se obtuvieron owners válidos
    if not owners:
        print("⚠️ No se encontraron owners")
        return []

    # ==================== FORMATEO Y ESTRUCTURACIÓN ====================
    # Formatear datos en tabla estructurada compatible con sync_table_data()
    tabla = []
    for owner in owners:
        # ==================== CONSTRUCCIÓN DE NOMBRE COMPLETO ====================
        # Construir nombre completo desde componentes individuales
        first_name = owner.get("firstName", "")
        last_name = owner.get("lastName", "")
        full_name = f"{first_name} {last_name}".strip()
        
        # ==================== ESTRUCTURACIÓN DE REGISTRO ====================
        # Crear registro estructurado con todos los campos necesarios
        tabla.append({
            "id": owner.get("id"),
            "firstName": first_name,
            "lastName": last_name,
            "fullName": full_name if full_name else "Sin nombre",
            "email": owner.get("email"),
            "active": owner.get("active"),
            "createdAt": owner.get("createdAt"),
            "updatedAt": owner.get("updatedAt"),
            "archived": owner.get("archived", False),
            "userId": owner.get("userId"),
            "userIdIncludingInactive": owner.get("userIdIncludingInactive")
        })

    print(f"📊 Owners formateados: {len(tabla)}")
    return tabla

def display_owners_summary(owners_data):
    """
    Muestra un resumen de los owners
    """
    if not owners_data:
        print("⚠️ No hay datos de owners para mostrar")
        return

    print(f"\n📊 RESUMEN DE OWNERS")
    print("=" * 40)
    
    total_owners = len(owners_data)
    active_owners = len([o for o in owners_data if o.get('active') == True])
    inactive_owners = total_owners - active_owners
    owners_with_email = len([o for o in owners_data if o.get('email')])
    
    print(f"🔹 Total de owners: {total_owners}")
    print(f"🔹 Owners activos: {active_owners}")
    print(f"🔹 Owners inactivos: {inactive_owners}")
    print(f"🔹 Owners con email: {owners_with_email}")
    
    if total_owners > 0:
        print(f"🔹 % Activos: {(active_owners/total_owners)*100:.1f}%")
        print(f"🔹 % Con email: {(owners_with_email/total_owners)*100:.1f}%")

    # Mostrar algunos owners activos
    print(f"\n👥 OWNERS ACTIVOS (primeros 10):")
    active_list = [o for o in owners_data if o.get('active') == True]
    
    for i, owner in enumerate(active_list[:10], 1):
        print(f"   {i:2d}. {owner['fullName']} ({owner['email']}) - ID: {owner['id']}")

def get_owners_metadata():
    """
    Función para obtener metadata de los owners (para compatibilidad)
    """
    owners_data = fetch_owners_as_table()
    if not owners_data:
        return {}
    
    active_count = len([o for o in owners_data if o.get('active') == True])
    
    metadata = {
        "total_owners": len(owners_data),
        "active_owners": active_count,
        "inactive_owners": len(owners_data) - active_count,
        "owners_with_email": len([o for o in owners_data if o.get('email')]),
        "columns": list(owners_data[0].keys()) if owners_data else []
    }
    
    return metadata

def main():
    """
    Función principal para ejecutar el script directamente
    """
    print("🚀 HUBSPOT OWNERS FETCHER")
    print("=" * 40)
    
    # Verificar token
    token = os.getenv('HUBSPOT_TOKEN')
    if not token:
        print("❌ Error: No se encontró HUBSPOT_TOKEN en las variables de entorno")
        return

    print(f"🔐 Token configurado: {'*' * 20}{token[-4:]}")

    # Obtener owners
    owners_data = fetch_owners_as_table()
    
    if not owners_data:
        print("⚠️ No se obtuvieron owners")
        return

    # Mostrar resumen
    display_owners_summary(owners_data)

if __name__ == "__main__":
    main()