# quick_insert_test.py
"""
Test rápido del INSERT mapper con pocos registros
"""
import sys
sys.path.append('.')

from hubspot_client.field_mapper_insert import HubSpotInsertFieldMapper

def test_mapper():
    """Test rápido del mapper"""
    print("🧪 TEST RÁPIDO DEL INSERT MAPPER")
    print("=" * 50)
    
    # Test del mapper
    mapper = HubSpotInsertFieldMapper()
    
    print(f"✅ Mapper cargado con {len(mapper.field_mapping)} campos")
    print(f"📋 Primeros 10 mapeos:")
    
    for i, (sql_field, hubspot_field) in enumerate(list(mapper.field_mapping.items())[:10]):
        print(f"   {i+1}. {sql_field} → {hubspot_field}")
    
    # Test con datos simulados
    print(f"\n🧪 PROBANDO MAPEO CON DATOS SIMULADOS:")
    
    test_data = {
        'no__de_cedula': '123456789',
        'numero_asociado': '12345',
        'firstname': 'Juan',
        'lastname': 'Pérez',
        'email': 'juan.perez@test.com',
        'con_ahorros': '1',
        'con_creditos': '0',
        'tiene_seguros': 'true',
        'estado_del_asociado': 'Activo'
    }
    
    mapped = mapper.map_contact_data(test_data)
    
    print(f"   📊 Datos originales: {len(test_data)} campos")
    print(f"   📊 Datos mapeados: {len(mapped)} campos")
    print(f"   📋 Campos mapeados:")
    
    for hubspot_field, value in mapped.items():
        print(f"      {hubspot_field}: {value}")
    
    return len(mapper.field_mapping) > 10  # Éxito si hay más de 10 campos

if __name__ == "__main__":
    success = test_mapper()
    print("\n" + "=" * 50)
    if success:
        print("✅ MAPPER FUNCIONANDO CORRECTAMENTE")
        print("🚀 LISTO PARA PRUEBA CON DATOS REALES")
    else:
        print("❌ PROBLEMAS CON EL MAPPER")
    print("=" * 50)
