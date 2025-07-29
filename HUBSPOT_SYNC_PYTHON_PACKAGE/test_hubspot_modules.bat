@echo off
echo ============================================
echo TEST DE MÓDULOS HUBSPOT
echo ============================================

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

echo 🧪 Probando módulos hubspot...
echo.

echo 📝 Probando hubspot.fetch_deals...
python -c "from hubspot.fetch_deals import fetch_deals_from_hubspot; print('✅ hubspot.fetch_deals OK')"

echo.
echo 📝 Probando hubspot.fetch_tickets...
python -c "from hubspot.fetch_tickets import fetch_tickets_from_hubspot; print('✅ hubspot.fetch_tickets OK')"

echo.
echo 📝 Probando hubspot.fetch_contacts...
python -c "from hubspot.fetch_contacts import fetch_contacts_from_hubspot; print('✅ hubspot.fetch_contacts OK')"

echo.
echo 📝 Probando hubspot.fetch_owners...
python -c "from hubspot.fetch_owners import fetch_owners_as_table; print('✅ hubspot.fetch_owners OK')"

echo.
echo 📝 Probando hubspot.fetch_deals_pipelines...
python -c "from hubspot.fetch_deals_pipelines import fetch_deal_pipelines_as_table; print('✅ hubspot.fetch_deals_pipelines OK')"

echo.
echo 📝 Probando hubspot.fetch_tickets_pipelines...
python -c "from hubspot.fetch_tickets_pipelines import fetch_ticket_pipelines_as_table; print('✅ hubspot.fetch_tickets_pipelines OK')"

echo.
echo 📝 Probando dotenv...
python -c "from dotenv import load_dotenv; from pathlib import Path; print('✅ dotenv y pathlib OK')"

echo.
echo ============================================
echo ✅ TEST DE MÓDULOS HUBSPOT COMPLETO
echo ============================================
echo Si todos están OK, el sistema está listo
echo para sincronizar (excepto conexión SQL)
echo ============================================
pause
