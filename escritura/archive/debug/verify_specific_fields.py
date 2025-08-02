# verify_specific_fields.py
"""
Script para verificar valores específicos de campos en HubSpot
"""
import os
import sys
sys.path.append('.')

from hubspot_client.writer import HubSpotWriter
from dotenv import load_dotenv

def verify_specific_fields():
    """
    Verifica los valores actuales de campos específicos en HubSpot
    """
    print("🔍 VERIFICACIÓN DE CAMPOS ESPECÍFICOS EN HUBSPOT")
    print("=" * 60)
    
    writer = HubSpotWriter(dry_run=False)
    
    # Buscar el contacto por cédula
    cedula = '107150612'
    contact = writer.find_contact_by_cedula(cedula)
    
    if not contact:
        print(f"❌ Contacto con cédula {cedula} no encontrado")
        return
    
    print(f"✅ Contacto encontrado: {contact.id}")
    
    # Campos específicos que queremos verificar
    fields_to_check = [
        'work_email',
        'estado_del_asociado', 
        'con_ahorro',
        'con_ahorro_economias',
        'con_credito',
        'hubspot_owner_id'
    ]
    
    print(f"\n📋 VALORES ACTUALES EN HUBSPOT:")
    for field in fields_to_check:
        value = contact.properties.get(field, 'FIELD_NOT_FOUND')
        print(f"   🔍 {field}: {value}")
    
    # También mostrar TODOS los campos personalizados
    print(f"\n📋 TODOS LOS CAMPOS PERSONALIZADOS (que empiecen con 'con_'):")
    custom_fields = {k: v for k, v in contact.properties.items() 
                    if k.startswith('con_') and v is not None}
    
    for field, value in sorted(custom_fields.items()):
        print(f"   ✅ {field}: {value}")
    
    print(f"\n📊 Total campos personalizados con valor: {len(custom_fields)}")

if __name__ == "__main__":
    load_dotenv()
    verify_specific_fields()
