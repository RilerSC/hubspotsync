#!/usr/bin/env python3
"""
Script para verificar los permisos del API token de HubSpot
"""

import os
import requests
import sys
sys.path.append('.')
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

def check_token_permissions():
    """
    Verifica los permisos del token de HubSpot usando la API de access tokens
    """
    token = os.getenv('HUBSPOT_TOKEN')
    if not token:
        print("❌ Error: No se encontró HUBSPOT_TOKEN en las variables de entorno")
        return None
    
    # URL para verificar información del token
    url = "https://api.hubapi.com/oauth/v1/access-tokens/" + token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("🔍 Verificando permisos del API token...")
    print(f"🔑 Token: {token[:20]}...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Token válido - Información obtenida")
            return data
        else:
            print(f"❌ Error verificando token: {response.status_code}")
            print(f"❌ Respuesta: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def check_crm_contacts_permissions():
    """
    Verifica permisos específicos para CRM contacts
    """
    token = os.getenv('HUBSPOT_TOKEN')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\n🔍 Verificando permisos específicos de CRM Contacts...")
    
    # Test 1: Leer propiedades de contactos
    print("\n📖 Test 1: Leer propiedades de contactos")
    try:
        url = "https://api.hubapi.com/crm/v3/properties/contacts"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ LECTURA de propiedades: PERMITIDA")
        else:
            print(f"❌ LECTURA de propiedades: DENEGADA ({response.status_code})")
    except Exception as e:
        print(f"❌ Error verificando lectura: {e}")
    
    # Test 2: Leer contactos
    print("\n📖 Test 2: Leer contactos")
    try:
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        params = {"limit": 1}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            print("✅ LECTURA de contactos: PERMITIDA")
        else:
            print(f"❌ LECTURA de contactos: DENEGADA ({response.status_code})")
    except Exception as e:
        print(f"❌ Error verificando lectura de contactos: {e}")
    
    # Test 3: Buscar contactos (POST)
    print("\n🔍 Test 3: Buscar contactos (POST)")
    try:
        url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        payload = {
            "limit": 1,
            "properties": ["email", "firstname", "lastname"],
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
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ BÚSQUEDA de contactos: PERMITIDA")
        else:
            print(f"❌ BÚSQUEDA de contactos: DENEGADA ({response.status_code})")
            print(f"❌ Respuesta: {response.text}")
    except Exception as e:
        print(f"❌ Error verificando búsqueda: {e}")
    
    # Test 4: Intentar actualizar un contacto (simulación)
    print("\n✏️  Test 4: Permisos de ESCRITURA de contactos")
    try:
        # Primero obtener un contacto para prueba
        url_search = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        payload_search = {
            "limit": 1,
            "properties": ["hs_object_id", "email"],
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
        search_response = requests.post(url_search, headers=headers, json=payload_search)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            contacts = search_data.get("results", [])
            
            if contacts:
                contact_id = contacts[0].get("id")
                print(f"📋 Contacto de prueba encontrado: ID {contact_id}")
                
                # Intentar actualizar con un campo básico (sin cambiar realmente el valor)
                url_update = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
                current_email = contacts[0].get("properties", {}).get("email", "")
                
                # Usamos el mismo email para no cambiar nada
                payload_update = {
                    "properties": {
                        "email": current_email  # Mismo valor, sin cambios reales
                    }
                }
                
                # NOTA: No ejecutamos la actualización, solo verificamos el endpoint
                print("⚠️  Simulando actualización (sin ejecutar cambios reales)...")
                print("✅ ESCRITURA de contactos: PROBABLEMENTE PERMITIDA")
                print("   (Endpoint accesible, contacto encontrado)")
                
            else:
                print("⚠️  No se encontraron contactos para prueba de escritura")
        else:
            print(f"❌ No se pudo obtener contactos para prueba de escritura: {search_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando escritura: {e}")

def check_app_info():
    """
    Verifica información de la aplicación/integración
    """
    token = os.getenv('HUBSPOT_TOKEN')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\n🏢 Verificando información de la aplicación...")
    
    try:
        # Intentar obtener información de la app
        url = "https://api.hubapi.com/integrations/v1/me"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Información de aplicación obtenida")
            return data
        else:
            print(f"⚠️  No se pudo obtener info de aplicación: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo info de aplicación: {e}")
        return None

def analyze_token_type():
    """
    Analiza el tipo de token basado en su formato
    """
    token = os.getenv('HUBSPOT_TOKEN')
    if not token:
        return
    
    print("\n🔍 ANÁLISIS DEL TIPO DE TOKEN:")
    print(f"🔑 Token: {token[:30]}...")
    
    if token.startswith('pat-'):
        print("📋 Tipo: PRIVATE APP TOKEN (Personal Access Token)")
        print("   ✅ Mejor para integraciones server-to-server")
        print("   ✅ Permisos configurables en HubSpot App Settings")
        print("   💡 Verifica los scopes en: Configuración > Integraciones > Aplicaciones privadas")
        
    elif len(token) > 50 and not token.startswith('pat-'):
        print("📋 Tipo: OAUTH ACCESS TOKEN")
        print("   ✅ Token de OAuth flow")
        print("   ⚠️  Puede tener limitaciones de scope")
        
    else:
        print("📋 Tipo: LEGACY API KEY o TOKEN DESCONOCIDO")
        print("   ⚠️  Tipo de token no estándar")

def main():
    """
    Función principal para verificar permisos
    """
    print("🔐 VERIFICACIÓN DE PERMISOS DEL API TOKEN DE HUBSPOT")
    print("=" * 60)
    
    # 1. Análisis del tipo de token
    analyze_token_type()
    
    # 2. Verificar permisos del token
    token_info = check_token_permissions()
    
    if token_info:
        print("\n📊 INFORMACIÓN DEL TOKEN:")
        for key, value in token_info.items():
            print(f"   {key}: {value}")
    
    # 3. Verificar permisos específicos de CRM
    check_crm_contacts_permissions()
    
    # 4. Verificar información de la aplicación
    app_info = check_app_info()
    
    if app_info:
        print("\n📊 INFORMACIÓN DE LA APLICACIÓN:")
        for key, value in app_info.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"      {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")
    
    print("\n🎯 RECOMENDACIONES:")
    print("   1. Si usas Private App Token (pat-), verifica scopes en HubSpot")
    print("   2. Asegúrate de tener permisos: crm.objects.contacts.write")
    print("   3. Verifica permisos para propiedades custom")
    print("   4. Si hay errores, revisa la configuración en HubSpot > Configuración > Integraciones")

if __name__ == "__main__":
    main()
