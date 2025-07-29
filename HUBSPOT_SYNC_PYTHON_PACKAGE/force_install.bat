@echo off
echo ============================================
echo INSTALACIÓN FORZADA DE DEPENDENCIAS
echo ============================================

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar pip
echo 🔍 Verificando pip...
pip --version

REM Actualizar pip
echo 📦 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias una por una
echo 📦 Instalando requests...
pip install requests==2.31.0

echo 📦 Instalando pyodbc...
pip install pyodbc==5.0.1

echo 📦 Instalando python-dotenv...
pip install python-dotenv==1.0.1

echo 📦 Instalando tabulate...
pip install tabulate==0.9.0

echo 📦 Instalando urllib3...
pip install urllib3==2.2.2

REM Verificar instalación
echo 🧪 Verificando instalación...
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
echo Verificando tabulate...
python -c "import tabulate; print('✅ tabulate OK')"

echo.
echo Verificando urllib3...
python -c "import urllib3; print('✅ urllib3 OK')"

echo.
echo ============================================
echo ✅ INSTALACIÓN FORZADA COMPLETA
echo ============================================
pause
