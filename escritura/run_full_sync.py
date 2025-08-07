# run_full_sync.py
"""
Coordinador para ejecutar ambos procesos de sincronización:
1. Primero INSERT (contactos nuevos)
2. Después UPDATE (contactos existentes)

No modifica ningún proceso existente, solo los ejecuta en secuencia.
"""
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def print_separator(message):
    """Imprime un separador visual para claridad en logs"""
    print("\n" + "="*80)
    print(f" {message}")
    print("="*80 + "\n")

def run_script(script_name):
    """Ejecuta un script Python y retorna si fue exitoso"""
    print(f"🚀 Iniciando {script_name}...")
    start_time = datetime.now()
    
    try:
        # Ejecutar el script
        result = subprocess.run([
            sys.executable, script_name
        ], cwd=Path(__file__).parent, capture_output=False, text=True)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {script_name} completado exitosamente")
            print(f"⏱️  Duración: {duration}")
            return True
        else:
            print(f"❌ {script_name} falló con código: {result.returncode}")
            print(f"⏱️  Duración: {duration}")
            return False
            
    except Exception as e:
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"💥 Error ejecutando {script_name}: {str(e)}")
        print(f"⏱️  Duración: {duration}")
        return False

def main():
    """Función principal que coordina la ejecución completa"""
    print_separator("INICIO DE SINCRONIZACIÓN COMPLETA HUBSPOT")
    print(f"📅 Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    overall_start = datetime.now()
    
    # Fase 1: INSERT (contactos nuevos)
    print_separator("FASE 1: INSERT - CONTACTOS NUEVOS")
    insert_success = run_script("production_insert_full.py")
    
    # Fase 2: UPDATE (contactos existentes)
    print_separator("FASE 2: UPDATE - CONTACTOS EXISTENTES")
    update_success = run_script("production_update.py")
    
    # Resumen final
    overall_end = datetime.now()
    total_duration = overall_end - overall_start
    
    print_separator("RESUMEN FINAL")
    print(f"📊 INSERT: {'✅ EXITOSO' if insert_success else '❌ FALLÓ'}")
    print(f"📊 UPDATE: {'✅ EXITOSO' if update_success else '❌ FALLÓ'}")
    print(f"⏱️  Duración total: {total_duration}")
    
    if insert_success and update_success:
        print("🎉 SINCRONIZACIÓN COMPLETA EXITOSA")
        return 0
    elif insert_success or update_success:
        print("⚠️  SINCRONIZACIÓN PARCIALMENTE EXITOSA")
        return 1
    else:
        print("💀 SINCRONIZACIÓN FALLÓ COMPLETAMENTE")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
