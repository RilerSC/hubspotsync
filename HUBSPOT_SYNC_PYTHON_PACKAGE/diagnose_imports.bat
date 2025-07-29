@echo off
echo ====================================
echo DIAGNOSTICO DETALLADO DEL PROBLEMA
echo ====================================

echo.
echo 🔍 Ubicación actual:
cd

echo.
echo 🐍 Versión de Python:
py --version

echo.
echo 📁 Verificando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    echo ✅ Entorno virtual encontrado
) else (
    echo ❌ Entorno virtual NO encontrado
    echo Creando entorno virtual...
    py -m venv venv
)

echo.
echo 🔄 Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo 📦 Verificando ubicación de pip:
where pip

echo.
echo 📦 Verificando ubicación de Python:
where python

echo.
echo 🔎 Verificando paquetes instalados:
pip list | findstr requests
pip list | findstr pyodbc
pip list | findstr dotenv

echo.
echo 🧪 Test de import directo:
python -c "
import sys
print('Python path:', sys.executable)
print('Python version:', sys.version)
print('---')
try:
    import requests
    print('✅ requests:', requests.__version__)
except Exception as e:
    print('❌ requests error:', e)
    
try:
    import pyodbc
    print('✅ pyodbc:', pyodbc.version)
except Exception as e:
    print('❌ pyodbc error:', e)
    
try:
    import dotenv
    print('✅ dotenv importado')
except Exception as e:
    print('❌ dotenv error:', e)
"

echo.
echo ====================================
pause
