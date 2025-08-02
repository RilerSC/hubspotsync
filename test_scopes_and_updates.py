#!/usr/bin/env python3
"""
Script para verificar scopes específicos del Private App Token
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

def test_specific_scopes():
    """
    Prueba scopes específicos necesarios para nuestro caso de uso
    """
    token = os.getenv('HUBSPOT_TOKEN')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("🔍 VERIFICANDO SCOPES ESPECÍFICOS REQUERIDOS")
    print("=" * 50)
    
    scopes_to_test = [
        {
            "name": "crm.objects.contacts.read",
            "description": "Leer contactos",
            "test_url": "https://api.hubapi.com/crm/v3/objects/contacts",
            "method": "GET",
            "params": {"limit": 1}
        },
        {
            "name": "crm.objects.contacts.write", 
            "description": "Escribir/actualizar contactos",
            "test_url": "https://api.hubapi.com/crm/v3/objects/contacts/search",
            "method": "POST",
            "payload": {
                "limit": 1,
                "properties": ["hs_object_id", "email"],
                "filterGroups": [{"filters": [{"propertyName": "hs_object_id", "operator": "HAS_PROPERTY"}]}]
            }
        },
        {
            "name": "crm.schemas.contacts.read",
            "description": "Leer esquemas/propiedades de contactos",
            "test_url": "https://api.hubapi.com/crm/v3/properties/contacts",
            "method": "GET"
        }
    ]
    
    results = {}
    
    for scope in scopes_to_test:
        print(f"\n📋 Probando: {scope['name']}")
        print(f"   Descripción: {scope['description']}")
        
        try:
            if scope['method'] == 'GET':
                params = scope.get('params', {})
                response = requests.get(scope['test_url'], headers=headers, params=params)
            else:  # POST
                payload = scope.get('payload', {})
                response = requests.post(scope['test_url'], headers=headers, json=payload)
            
            if response.status_code == 200:
                print(f"   ✅ PERMITIDO - Status: {response.status_code}")
                results[scope['name']] = True
            elif response.status_code == 403:
                print(f"   ❌ DENEGADO - Status: {response.status_code} (Sin permisos)")
                results[scope['name']] = False
            else:
                print(f"   ⚠️  INCIERTO - Status: {response.status_code}")
                print(f"   📝 Respuesta: {response.text[:200]}...")
                results[scope['name']] = "uncertain"
                
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
            results[scope['name']] = False
    
    return results

def test_actual_contact_update():
    """
    Prueba real de actualización de contacto para verificar permisos de escritura
    """
    token = os.getenv('HUBSPOT_TOKEN')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"\n🧪 PRUEBA REAL DE ACTUALIZACIÓN DE CONTACTO")
    print("=" * 50)
    
    try:
        # 1. Buscar un contacto específico (el que usamos en las pruebas)
        search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        search_payload = {
            "limit": 1,
            "properties": ["hs_object_id", "firstname", "lastname", "email", "numero_asociado"],
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "numero_asociado",
                            "operator": "EQ",
                            "value": "06664"  # Nuestro contacto de prueba
                        }
                    ]
                }
            ]
        }
        
        print("🔍 1. Buscando contacto de prueba (numero_asociado: 06664)...")
        search_response = requests.post(search_url, headers=headers, json=search_payload)
        
        if search_response.status_code != 200:
            print(f"❌ Error buscando contacto: {search_response.status_code}")
            return False
        
        search_data = search_response.json()
        contacts = search_data.get("results", [])
        
        if not contacts:
            print("❌ Contacto de prueba no encontrado")
            return False
        
        contact = contacts[0]
        contact_id = contact.get("id")
        current_props = contact.get("properties", {})
        
        print(f"✅ Contacto encontrado: ID {contact_id}")
        print(f"   👤 Nombre: {current_props.get('firstname', 'N/A')} {current_props.get('lastname', 'N/A')}")
        print(f"   📧 Email: {current_props.get('email', 'N/A')}")
        
        # 2. Intentar actualizar con un solo campo estándar
        print(f"\n✏️  2. Probando actualización de campo estándar (firstname)...")
        update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
        
        current_firstname = current_props.get('firstname', '')
        test_firstname = current_firstname + " [TEST]" if current_firstname else "TEST_NAME"
        
        update_payload = {
            "properties": {
                "firstname": test_firstname
            }
        }
        
        update_response = requests.patch(update_url, headers=headers, json=update_payload)
        
        if update_response.status_code == 200:
            print(f"✅ ACTUALIZACIÓN ESTÁNDAR: EXITOSA")
            
            # Revertir el cambio
            revert_payload = {
                "properties": {
                    "firstname": current_firstname
                }
            }
            requests.patch(update_url, headers=headers, json=revert_payload)
            print(f"✅ Campo revertido al valor original")
            
        else:
            print(f"❌ ACTUALIZACIÓN ESTÁNDAR: FALLÓ - Status: {update_response.status_code}")
            print(f"❌ Respuesta: {update_response.text}")
            return False
        
        # 3. Intentar actualizar con un campo custom
        print(f"\n✏️  3. Probando actualización de campo personalizado (con_ahorro)...")
        
        custom_update_payload = {
            "properties": {
                "con_ahorro": "true"  # Campo boolean personalizado
            }
        }
        
        custom_response = requests.patch(update_url, headers=headers, json=custom_update_payload)
        
        if custom_response.status_code == 200:
            print(f"✅ ACTUALIZACIÓN PERSONALIZADA: EXITOSA")
            return True
        else:
            print(f"❌ ACTUALIZACIÓN PERSONALIZADA: FALLÓ - Status: {custom_response.status_code}")
            print(f"❌ Respuesta: {custom_response.text}")
            
            # Verificar si es un problema de formato
            if "INVALID_OPTION" in custom_response.text or "Invalid property value" in custom_response.text:
                print(f"💡 POSIBLE CAUSA: Problema de formato de datos, no de permisos")
                return "format_issue"
            else:
                return False
    
    except Exception as e:
        print(f"❌ Error en prueba de actualización: {e}")
        return False

def analyze_update_failure_reasons():
    """
    Analiza posibles razones por las que las actualizaciones fallan
    """
    print(f"\n🔍 ANÁLISIS DE POSIBLES CAUSAS DE FALLO")
    print("=" * 50)
    
    print(f"🎯 Posibles razones por las que solo 5/55 campos se actualizan:")
    print(f"")
    print(f"1. 📝 FORMATO DE DATOS:")
    print(f"   - Campos boolean: requieren 'true'/'false' (string) o true/false (boolean)")
    print(f"   - Campos enum: requieren valores exactos de la lista permitida")
    print(f"   - Campos date: requieren formato específico (YYYY-MM-DD)")
    print(f"   - Campos number: requieren números, no strings")
    print(f"")
    print(f"2. 🔒 PERMISOS DE ESCRITURA:")
    print(f"   - Algunos campos custom pueden tener restricciones de escritura")
    print(f"   - Campos calculados o de solo lectura")
    print(f"")
    print(f"3. 📋 VALIDACIONES DE NEGOCIO:")
    print(f"   - HubSpot puede tener validaciones específicas por campo")
    print(f"   - Campos requeridos o dependientes")
    print(f"")
    print(f"4. 🎯 CONFIGURACIÓN DE PROPIEDADES:")
    print(f"   - Propiedades marcadas como 'read-only'")
    print(f"   - Propiedades con listas de valores específicas")

def main():
    """
    Función principal
    """
    print("🔐 VERIFICACIÓN DETALLADA DE SCOPES Y PERMISOS")
    print("=" * 60)
    
    # 1. Verificar scopes específicos
    scope_results = test_specific_scopes()
    
    # 2. Prueba real de actualización
    update_result = test_actual_contact_update()
    
    # 3. Análisis de posibles causas
    analyze_update_failure_reasons()
    
    print(f"\n🎯 RESUMEN DE DIAGNÓSTICO:")
    print(f"=" * 40)
    
    for scope, result in scope_results.items():
        status = "✅" if result else ("⚠️" if result == "uncertain" else "❌")
        print(f"   {status} {scope}")
    
    if update_result == True:
        print(f"   ✅ Actualización de campos personalizados: FUNCIONA")
        print(f"   💡 El problema puede ser formato de datos específicos")
    elif update_result == "format_issue":
        print(f"   ⚠️  Actualización de campos personalizados: PROBLEMA DE FORMATO")
        print(f"   💡 Los permisos están bien, revisar formato de datos")
    else:
        print(f"   ❌ Actualización de campos personalizados: PROBLEMA DE PERMISOS")
        print(f"   💡 Verificar configuración de Private App en HubSpot")

if __name__ == "__main__":
    main()
