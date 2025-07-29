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
    Obtiene owners y los formatea como lista de diccionarios para compatibilidad
    """
    owners = fetch_owners()
    
    if not owners:
        print("⚠️ No se encontraron owners")
        return []

    # Formatear datos en tabla estructurada
    tabla = []
    for owner in owners:
        # Construir nombre completo
        first_name = owner.get("firstName", "")
        last_name = owner.get("lastName", "")
        full_name = f"{first_name} {last_name}".strip()
        
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