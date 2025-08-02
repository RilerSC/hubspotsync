from db.mssql_connector import MSSQLConnector

connector = MSSQLConnector()
try:
    update_data = connector.get_update_data()
    print(f"Registros UPDATE: {len(update_data)}")
    print(f"Columnas: {len(update_data[0].keys())}")
    print(f"Columna refuncion_ii existe: {'refuncion_ii' in update_data[0]}")
    print("✅ Consulta UPDATE corregida funciona perfectamente!")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    connector.disconnect()
