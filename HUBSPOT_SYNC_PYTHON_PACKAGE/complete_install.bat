@echo off
echo ============================================
echo INSTALACIÓN COMPLETA - HUBSPOT_SYNC
echo Versión Python 3.13 - Optimizada
echo ============================================

REM Verificar que Python está disponible
echo 🔍 Verificando Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en PATH
    echo Instala Python 3.13 desde https://python.org
    pause
    exit /b 1
)

py --version

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    py -m venv venv
    if errorlevel 1 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ℹ️ Entorno virtual ya existe
)

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar activación
echo 🔍 Verificando activación...
where python
python --version

REM Actualizar pip
echo 📦 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt

REM Verificar instalación
echo 🧪 Verificando instalación...
python -c "import sys; print('Python:', sys.version)"
echo Verificando módulos...
python -c "import requests; print('✅ requests:', requests.__version__)"
python -c "import pyodbc; print('✅ pyodbc:', pyodbc.version)"
python -c "import dotenv; print('✅ python-dotenv importado')"
python -c "import tabulate; print('✅ tabulate importado')"
python -c "import urllib3; print('✅ urllib3 importado')"

REM Verificar estructura de archivos
echo 🔍 Verificando archivos necesarios...
if exist "main.py" (
    echo ✅ main.py encontrado
) else (
    echo ❌ main.py no encontrado
)

if exist "hubspot" (
    echo ✅ Carpeta hubspot encontrada
) else (
    echo ❌ Carpeta hubspot no encontrada
)

if exist ".env" (
    echo ✅ Archivo .env encontrado
) else (
    echo ⚠️ Archivo .env no encontrado
    echo Crea el archivo .env con tus credenciales:
    echo.
    echo HUBSPOT_TOKEN=tu_token_aqui
    echo SQL_SERVER=tu_servidor
    echo SQL_DATABASE=tu_base_datos
    echo SQL_USER=tu_usuario
    echo SQL_PASSWORD=tu_contraseña
    echo.
)

echo ============================================
echo ✅ INSTALACIÓN COMPLETA
echo ============================================
echo Para ejecutar el sync, usa: run_sync.bat
echo Para configurar credenciales, edita el archivo .env
echo ============================================
pause
