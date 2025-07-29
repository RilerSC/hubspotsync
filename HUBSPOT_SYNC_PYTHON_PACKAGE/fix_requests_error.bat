@echo off
echo ====================================
echo SOLUCIONANDO PROBLEMA DE REQUESTS
echo ====================================

echo.
echo 🔍 Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo 📦 Verificando dependencias instaladas...
pip list

echo.
echo 🔄 Reinstalando dependencias...
pip install -r requirements.txt

echo.
echo 🧪 Verificando imports...
python -c "
try:
    import requests
    print('✅ requests importado correctamente')
except ImportError as e:
    print(f'❌ Error con requests: {e}')

try:
    import pyodbc
    print('✅ pyodbc importado correctamente')
except ImportError as e:
    print(f'❌ Error con pyodbc: {e}')

try:
    import dotenv
    print('✅ dotenv importado correctamente')
except ImportError as e:
    print(f'❌ Error con dotenv: {e}')

try:
    from hubspot.fetch_deals import fetch_deals_from_hubspot
    print('✅ Módulos hubspot importados correctamente')
except ImportError as e:
    print(f'❌ Error con módulos hubspot: {e}')
"

echo.
echo 🚀 Probando ejecución...
python main.py

echo.
echo ====================================
pause
