@echo off
echo =============================================
echo INSTALACIÓN RÁPIDA - HUBSPOT_SYNC
echo (Detecta automáticamente tu comando Python)
echo =============================================

echo.
echo 🔍 Detectando Python...

:: Detectar qué comando de Python usar
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo ✅ Usando comando: python
    python --version
    goto :found_python
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    echo ✅ Usando comando: python3
    python3 --version
    goto :found_python
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    echo ✅ Usando comando: py
    py --version
    goto :found_python
)

echo ❌ No se encontró Python
echo.
echo Descarga Python 3.13 desde: https://www.python.org/downloads/
echo ¡IMPORTANTE! Marca "Add Python to PATH" durante la instalación
pause
exit /b 1

:found_python
echo.
echo 🚀 Creando entorno virtual...
%PYTHON_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Error creando entorno virtual
    pause
    exit /b 1
)

echo.
echo 📦 Activando entorno e instalando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo ✅ INSTALACIÓN COMPLETADA
echo.
echo Prueba ejecutar: run_sync.bat
echo.
pause
