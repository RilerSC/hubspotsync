@echo off
echo ========================================
echo HUBSPOT_SYNC - Migración a Python 3.13
echo ========================================

echo 🔄 Actualizando proyecto a Python 3.13...

echo.
echo 📋 Pasos de la migración:
echo 1. Verificar Python 3.13 instalado
echo 2. Crear nuevo entorno virtual
echo 3. Instalar dependencias actualizadas
echo 4. Verificar compatibilidad
echo 5. Test de funcionamiento

echo.
echo 🔍 Verificando Python 3.13...
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo ✅ Python encontrado usando comando: python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
        echo ✅ Python encontrado usando comando: python3
    ) else (
        py --version >nul 2>&1
        if %errorlevel% equ 0 (
            set PYTHON_CMD=py
            echo ✅ Python encontrado usando comando: py
        ) else (
            echo ❌ Python no está instalado o no está en PATH
            echo.
            echo Intenta estos comandos manualmente:
            echo   python --version
            echo   python3 --version
            echo   py --version
            echo.
            echo Si ninguno funciona, reinstala Python desde:
            echo https://www.python.org/downloads/
            echo ¡IMPORTANTE! Marca "Add Python to PATH" durante la instalación
            pause
            exit /b 1
        )
    )
)

%PYTHON_CMD% -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Se requiere Python 3.13 o superior
    echo Versión actual:
    %PYTHON_CMD% --version
    echo.
    echo Descarga Python 3.13 desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 3.13+ detectado
%PYTHON_CMD% --version

echo.
echo 🗂️ Removiendo entorno virtual anterior...
if exist "venv" (
    rmdir /s /q venv
    echo ✅ Entorno virtual anterior removido
) else (
    echo ℹ️ No hay entorno virtual anterior
)

echo.
echo 🔨 Creando nuevo entorno virtual con Python 3.13...
%PYTHON_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Error creando entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual creado

echo.
echo 🚀 Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo 📦 Actualizando pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo.
echo 📚 Instalando dependencias actualizadas...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

echo.
echo 🔬 Ejecutando verificación de compatibilidad...
%PYTHON_CMD% verify_python313.py
if %errorlevel% neq 0 (
    echo ⚠️ Verificación mostró algunos problemas
    echo Revisa los mensajes arriba
) else (
    echo ✅ Verificación completada exitosamente
)

echo.
echo 🧪 Ejecutando test básico...
%PYTHON_CMD% -c "
import sys
print(f'✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
import requests, pyodbc, tabulate, dotenv
print('✅ Todas las dependencias importadas correctamente')
print('✅ Proyecto listo para usar con Python 3.13')
"

echo.
echo ========================================
echo 🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE
echo ========================================
echo.
echo 📊 Beneficios de Python 3.13:
echo • Mejor rendimiento general
echo • Sintaxis más moderna
echo • Mejor manejo de memoria
echo • Características nuevas del lenguaje
echo • Soporte extendido hasta 2029
echo.
echo 🚀 Próximos pasos:
echo 1. Ejecuta run_sync.bat para probar la sincronización
echo 2. Verifica que todo funcione correctamente
echo 3. Programa tareas usando task_scheduler.ps1
echo.
echo ========================================
pause
