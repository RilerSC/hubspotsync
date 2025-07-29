@echo off
echo ============================================
echo VERIFICACIÓN RÁPIDA - HUBSPOT_SYNC
echo ============================================

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

REM Test simple de Python
echo 🧪 Verificando Python...
python --version

REM Test de módulos uno por uno
echo.
echo 🧪 Verificando requests...
python -c "import requests; print('OK - requests version:', requests.__version__)"

echo.
echo 🧪 Verificando pyodbc...
python -c "import pyodbc; print('OK - pyodbc version:', pyodbc.version)"

echo.
echo 🧪 Verificando dotenv...
python -c "from dotenv import load_dotenv; print('OK - dotenv')"

echo.
echo 🧪 Verificando módulos hubspot...
python -c "from hubspot.fetch_deals import fetch_deals_from_hubspot; print('OK - hubspot.fetch_deals')"

echo.
echo ============================================
echo ✅ VERIFICACIÓN COMPLETA
echo ============================================
echo Si no hubo errores, el sistema está listo
echo Ejecuta run_sync.bat para sincronizar
echo ============================================
pause
