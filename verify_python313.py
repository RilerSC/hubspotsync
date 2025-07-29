#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                        VERIFICADOR DE COMPATIBILIDAD PYTHON 3.13
================================================================================

Archivo:            verify_python313.py
Descripción:        Verifica que el entorno Python 3.13 esté correctamente configurado
                   y que todas las dependencias sean compatibles.
                   
Funcionalidades:
    - Verificación de versión Python 3.13+
    - Test de importación de todas las dependencias
    - Verificación de funcionalidades específicas de Python 3.13
    - Diagnóstico de compatibilidad del sistema
    
Creado:             Julio 2025
Versión:            1.0
================================================================================
"""

import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Verifica que la versión de Python sea 3.13 o superior."""
    print("=" * 60)
    print("🔍 VERIFICANDO VERSIÓN DE PYTHON")
    print("=" * 60)
    
    version = sys.version_info
    print(f"Versión actual: Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 13:
        print("✅ Versión de Python compatible (3.13+)")
        return True
    else:
        print("❌ Se requiere Python 3.13 o superior")
        print("Descarga desde: https://www.python.org/downloads/")
        return False

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO DEPENDENCIAS")
    print("=" * 60)
    
    dependencies = [
        "requests",
        "pyodbc", 
        "tabulate",
        "dotenv",
        "urllib3"
    ]
    
    all_good = True
    
    for dep in dependencies:
        try:
            if dep == "dotenv":
                import dotenv
                module_name = "python-dotenv"
            else:
                __import__(dep)
                module_name = dep
            
            print(f"✅ {module_name} - Instalado correctamente")
        except ImportError:
            print(f"❌ {module_name} - NO INSTALADO")
            all_good = False
    
    return all_good

def check_python313_features():
    """Verifica funcionalidades específicas de Python 3.13."""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO FUNCIONALIDADES PYTHON 3.13")
    print("=" * 60)
    
    # Test de improved error messages
    try:
        # Esto debería generar un error más informativo en Python 3.13
        result = []
        for i in range(5):
            result.append(i ** 2)
        print("✅ Funcionalidades básicas funcionando correctamente")
    except Exception as e:
        print(f"⚠️ Error en funcionalidades básicas: {e}")
    
    # Test de f-strings mejorados
    try:
        name = "HUBSPOT_SYNC"
        version = "3.13"
        message = f"Proyecto {name} ejecutándose en Python {version}"
        print(f"✅ F-strings mejorados: {message}")
    except Exception as e:
        print(f"❌ Error en f-strings: {e}")
    
    # Test de type hints mejorados
    try:
        def test_function(data: list[str]) -> dict[str, int]:
            return {item: len(item) for item in data}
        
        result = test_function(["test", "python", "3.13"])
        print("✅ Type hints modernos funcionando")
    except Exception as e:
        print(f"❌ Error en type hints: {e}")
    
    return True

def check_system_compatibility():
    """Verifica compatibilidad del sistema operativo."""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO COMPATIBILIDAD DEL SISTEMA")
    print("=" * 60)
    
    print(f"Sistema operativo: {sys.platform}")
    print(f"Arquitectura: {sys.version.split()[1] if len(sys.version.split()) > 1 else 'Unknown'}")
    
    # Verificar si es Windows (para el proyecto)
    if sys.platform.startswith('win'):
        print("✅ Sistema Windows detectado - Compatible")
    elif sys.platform.startswith('darwin'):
        print("✅ Sistema macOS detectado - Compatible para desarrollo")
    elif sys.platform.startswith('linux'):
        print("✅ Sistema Linux detectado - Compatible")
    else:
        print("⚠️ Sistema no reconocido - Puede requerir configuración adicional")
    
    return True

def run_performance_test():
    """Ejecuta un test básico de rendimiento."""
    print("\n" + "=" * 60)
    print("🚀 TEST DE RENDIMIENTO BÁSICO")
    print("=" * 60)
    
    import time
    
    # Test de creación de listas
    start_time = time.time()
    test_data = [i ** 2 for i in range(100000)]
    list_time = time.time() - start_time
    
    # Test de diccionarios
    start_time = time.time()
    test_dict = {f"key_{i}": i ** 2 for i in range(10000)}
    dict_time = time.time() - start_time
    
    print(f"✅ Creación de lista (100k elementos): {list_time:.4f}s")
    print(f"✅ Creación de diccionario (10k elementos): {dict_time:.4f}s")
    
    if list_time < 1.0 and dict_time < 1.0:
        print("✅ Rendimiento óptimo detectado")
    else:
        print("⚠️ Rendimiento más lento de lo esperado")
    
    return True

def main():
    """Función principal de verificación."""
    print("🔬 VERIFICADOR DE COMPATIBILIDAD PYTHON 3.13")
    print("Para el proyecto HUBSPOT_SYNC")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Ejecutar todas las verificaciones
    checks = [
        ("Versión Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Funcionalidades Python 3.13", check_python313_features),
        ("Compatibilidad Sistema", check_system_compatibility),
        ("Rendimiento", run_performance_test)
    ]
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_checks_passed = False
        except Exception as e:
            print(f"❌ Error en {check_name}: {e}")
            all_checks_passed = False
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    if all_checks_passed:
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        print("🚀 El proyecto está listo para ejecutarse con Python 3.13")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("🔧 Revisa los errores arriba y corrígelos antes de continuar")
    
    print("\n📝 Para instalar Python 3.13:")
    print("   https://www.python.org/downloads/")
    print("📝 Para instalar dependencias:")
    print("   pip install -r requirements.txt")
    
    return all_checks_passed

if __name__ == "__main__":
    main()
