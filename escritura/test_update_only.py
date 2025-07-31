#!/usr/bin/env python3
"""
Test específico para validar la consulta HB_UPDATE corregida
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.mssql_connector import MSSQLConnector
from config.settings import settings

def test_update_query():
    print("🧪 Test específico para consulta HB_UPDATE")
    print("=" * 50)
    
    # Inicializar conector
    connector = MSSQLConnector()
    
    try:
        # Probar consulta UPDATE
        print("📥 Probando consulta HB_UPDATE...")
        update_data = connector.get_update_data()
        
        if update_data:
            print(f"✅ Consulta HB_UPDATE exitosa: {len(update_data)} registros")
            print(f"✅ Columnas encontradas: {len(update_data[0].keys()) if update_data else 0}")
            
            # Mostrar algunas columnas de muestra
            if update_data:
                sample_record = update_data[0]
                print("\n📊 Columnas en el primer registro:")
                for i, (key, value) in enumerate(sample_record.items()):
                    if i < 10:  # Mostrar primeras 10 columnas
                        print(f"   {key}: {value}")
                    elif i == 10:
                        print(f"   ... y {len(sample_record) - 10} columnas más")
                        break
                        
                # Verificar específicamente la columna problemática
                if 'refuncion_ii' in sample_record:
                    print(f"✅ Columna 'refuncion_ii' encontrada: {sample_record['refuncion_ii']}")
                else:
                    print("❌ Columna 'refuncion_ii' NO encontrada")
        else:
            print("❌ No se obtuvieron datos de la consulta UPDATE")
            
    except Exception as e:
        print(f"❌ Error en consulta UPDATE: {e}")
    finally:
        connector.disconnect()

if __name__ == "__main__":
    test_update_query()
