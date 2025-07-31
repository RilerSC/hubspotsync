#!/usr/bin/env python3
"""
🔍 Verificador de Permisos de API Key de HubSpot
Verifica qué operaciones puede realizar tu API key actual
"""
import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_hubspot_api_permissions():
    """Verifica los permisos de la API key de HubSpot"""
    
    token = os.getenv('HUBSPOT_TOKEN')
    if not token:
        print("❌ ERROR: HUBSPOT_TOKEN no encontrado en .env")
        return
    
    # Headers para las requests
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 VERIFICANDO PERMISOS DE API KEY DE HUBSPOT")
    print("=" * 50)
    
    # 1. Verificar permisos de lectura (ya sabemos que funcionan)
    print("\n📖 PERMISOS DE LECTURA:")
    test_read_permissions(headers)
    
    # 2. Verificar permisos de escritura (lo que necesitamos)
    print("\n✏️ PERMISOS DE ESCRITURA:")
    test_write_permissions(headers)
    
    # 3. Verificar permisos de búsqueda
    print("\n🔍 PERMISOS DE BÚSQUEDA:")
    test_search_permissions(headers)

def test_read_permissions(headers):
    """Prueba permisos de lectura"""
    
    tests = [
        ("Contactos", "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"),
        ("Deals", "https://api.hubapi.com/crm/v3/objects/deals?limit=1"),
        ("Propiedades", "https://api.hubapi.com/crm/v3/properties/contacts")
    ]
    
    for name, url in tests:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"  ✅ {name}: PERMITIDO")
            else:
                print(f"  ❌ {name}: ERROR {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name}: EXCEPCIÓN - {e}")

def test_write_permissions(headers):
    """Prueba permisos de escritura (simulación)"""
    
    # Test 1: Intentar crear un contacto de prueba
    test_contact = {
        "properties": {
            "firstname": "TEST_API_VERIFICATION",
            "lastname": "DELETE_ME",
            "email": f"test-api-{os.urandom(4).hex()}@test-domain-fake.com"
        }
    }
    
    try:
        # Intentar crear contacto
        response = requests.post(
            "https://api.hubapi.com/crm/v3/objects/contacts",
            headers=headers,
            json=test_contact
        )
        
        if response.status_code == 201:
            print("  ✅ CREAR Contactos: PERMITIDO")
            contact_data = response.json()
            contact_id = contact_data.get('id')
            
            # Si pudimos crear, intentar actualizar
            if contact_id:
                test_update_contact(headers, contact_id)
                # Limpiar: eliminar contacto de prueba
                cleanup_test_contact(headers, contact_id)
        else:
            print(f"  ❌ CREAR Contactos: ERROR {response.status_code}")
            print(f"      Respuesta: {response.text[:100]}...")
            
    except Exception as e:
        print(f"  ❌ CREAR Contactos: EXCEPCIÓN - {e}")

def test_update_contact(headers, contact_id):
    """Prueba actualización de contacto"""
    
    update_data = {
        "properties": {
            "lastname": "UPDATED_DELETE_ME"
        }
    }
    
    try:
        response = requests.patch(
            f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            print("  ✅ ACTUALIZAR Contactos: PERMITIDO")
        else:
            print(f"  ❌ ACTUALIZAR Contactos: ERROR {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ ACTUALIZAR Contactos: EXCEPCIÓN - {e}")

def test_search_permissions(headers):
    """Prueba permisos de búsqueda"""
    
    # Test de búsqueda por propiedades
    search_request = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": "nonexistent@test.com"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://api.hubapi.com/crm/v3/objects/contacts/search",
            headers=headers,
            json=search_request
        )
        
        if response.status_code == 200:
            print("  ✅ BÚSQUEDA de Contactos: PERMITIDO")
        else:
            print(f"  ❌ BÚSQUEDA de Contactos: ERROR {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ BÚSQUEDA de Contactos: EXCEPCIÓN - {e}")

def cleanup_test_contact(headers, contact_id):
    """Elimina contacto de prueba creado"""
    
    try:
        response = requests.delete(
            f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
            headers=headers
        )
        
        if response.status_code == 204:
            print("  🧹 Contacto de prueba eliminado correctamente")
        else:
            print(f"  ⚠️ No se pudo eliminar contacto de prueba (ID: {contact_id})")
            
    except Exception as e:
        print(f"  ⚠️ Error eliminando contacto de prueba: {e}")

def show_recommendations():
    """Muestra recomendaciones basadas en los resultados"""
    
    print("\n" + "=" * 50)
    print("📋 RECOMENDACIONES:")
    print("\n🔑 PARA EL MÓDULO DE ESCRITURA necesitas estos permisos:")
    print("   ✅ crm.objects.contacts.read")
    print("   ✅ crm.objects.contacts.write") 
    print("   ✅ crm.schemas.contacts.read")
    print("   ✅ crm.lists.read (opcional)")
    
    print("\n🛡️ MEJORES PRÁCTICAS DE SEGURIDAD:")
    print("   • Usar la misma API key es SEGURO si tiene los permisos correctos")
    print("   • Considera crear una Private App específica para escritura")
    print("   • Habilita solo los permisos mínimos necesarios")
    print("   • Rotar tokens periódicamente")
    
    print("\n🔧 SI LOS PERMISOS FALLAN:")
    print("   1. Ve a HubSpot → Settings → Integrations → Private Apps")
    print("   2. Edita tu app actual")
    print("   3. En 'Scopes', asegúrate de tener marcado:")
    print("      ☑️ Read contacts")
    print("      ☑️ Write contacts") 
    print("   4. Guarda cambios")

if __name__ == "__main__":
    print("🚀 Iniciando verificación de permisos...")
    check_hubspot_api_permissions()
    show_recommendations()
    print("\n✨ Verificación completada!")
