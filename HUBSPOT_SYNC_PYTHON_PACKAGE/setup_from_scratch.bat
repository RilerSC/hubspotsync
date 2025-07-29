@echo off
echo ============================================
echo CREACIÓN Y CONFIGURACIÓN COMPLETA
echo ============================================

REM Verificar Python global
echo 🔍 Verificando Python global...
py --version
if errorlevel 1 (
    echo ❌ Python no está disponible
    pause
    exit /b 1
)

REM Eliminar entorno virtual existente si hay problemas
if exist "venv" (
    echo 🗑️ Eliminando entorno virtual problemático...
    rmdir /s /q venv
)

REM Crear entorno virtual desde cero
echo 📦 Creando entorno virtual nuevo...
py -m venv venv
if errorlevel 1 (
    echo ❌ Error creando entorno virtual
    pause
    exit /b 1
)

echo ✅ Entorno virtual creado exitosamente

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar activación
echo 🔍 Verificando entorno virtual...
echo Ubicación de python:
where python
echo Versión de python:
python --version

REM Actualizar pip
echo 📦 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias desde requirements.txt
echo 📦 Instalando desde requirements.txt...
pip install -r requirements.txt

echo 🧪 Verificando instalación final...
echo.
echo Verificando requests...
python -c "import requests; print('✅ requests version:', requests.__version__)"

echo.
echo Verificando pyodbc...
python -c "import pyodbc; print('✅ pyodbc version:', pyodbc.version)"

echo.
echo Verificando dotenv...
python -c "from dotenv import load_dotenv; print('✅ dotenv OK')"

echo.
echo Verificando hubspot módulos...
python -c "from hubspot.fetch_deals import fetch_deals_from_hubspot; print('✅ hubspot.fetch_deals OK')"

echo.
echo ============================================
echo ✅ CONFIGURACIÓN COMPLETA EXITOSA
echo ============================================
echo El entorno virtual está listo para usar
echo Ejecuta run_sync.bat para sincronizar
echo ============================================
pause
