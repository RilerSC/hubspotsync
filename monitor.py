#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Estado - HubSpot Sync
Utilidad para verificar el estado de la sincronización
"""

import os
import sys
from datetime import datetime

def monitor_hubspot_sync():
    """Monitorea el estado del proceso de sincronización"""
    
    print("🔍 MONITOR DE ESTADO - HUBSPOT SYNC")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar Python y versión
    print(f"🐍 Python: {sys.version}")
    print(f"📍 Ejecutable: {sys.executable}")
    print()
    
    # Verificar entorno virtual
    venv_path = ".venv/Scripts/python.exe"
    if os.path.exists(venv_path):
        print("✅ Entorno virtual activo")
    else:
        print("❌ Entorno virtual no encontrado")
    
    # Verificar archivo .env
    if os.path.exists('.env'):
        print("✅ Archivo de configuración .env encontrado")
        
        # Leer configuración sin mostrar credenciales
        try:
            with open('.env', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('SQL_SERVER=') and not line.strip().endswith('='):
                        print("✅ SQL Server configurado")
                    elif line.startswith('HUBSPOT_TOKEN=') and not line.strip().endswith('='):
                        print("✅ HubSpot Token configurado")
        except:
            pass
    else:
        print("❌ Archivo .env no encontrado")
    
    # Verificar estructura del proyecto
    required_files = ['main.py', 'requirements.txt', 'hubspot/']
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} encontrado")
        else:
            missing_files.append(file)
            print(f"❌ {file} no encontrado")
    
    if not missing_files:
        print("\n🎉 ¡Proyecto configurado correctamente!")
    else:
        print(f"\n⚠️ Archivos faltantes: {', '.join(missing_files)}")
    
    print("\n" + "=" * 50)
    print("✅ Monitoreo completado")

if __name__ == "__main__":
    try:
        monitor_hubspot_sync()
    except KeyboardInterrupt:
        print("\n❌ Monitoreo interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error en el monitor: {e}")
