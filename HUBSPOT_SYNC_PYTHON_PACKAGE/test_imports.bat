@echo off
echo ============================================
echo TEST DE FUNCIONAMIENTO - HUBSPOT_SYNC
echo ============================================

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

REM Test básico de imports
echo 🧪 Probando imports básicos...
echo === TEST DE IMPORTS ===
python -c "import requests; print('✅ requests OK:', requests.__version__)"
python -c "import pyodbc; print('✅ pyodbc OK:', pyodbc.version)"
python -c "import os; print('✅ os OK')"
python -c "from dotenv import load_dotenv; print('✅ dotenv OK')"
python -c "from pathlib import Path; print('✅ pathlib OK')"

echo === TEST DE MÓDULOS HUBSPOT ===
python -c "from hubspot.fetch_deals import fetch_deals_from_hubspot; print('✅ hubspot.fetch_deals OK')"
python -c "from hubspot.fetch_tickets import fetch_tickets_from_hubspot; print('✅ hubspot.fetch_tickets OK')"
python -c "from hubspot.fetch_contacts import fetch_contacts_from_hubspot; print('✅ hubspot.fetch_contacts OK')"

echo === TEST COMPLETO ===

echo ============================================
echo ✅ TEST COMPLETADO
echo ============================================
pause
