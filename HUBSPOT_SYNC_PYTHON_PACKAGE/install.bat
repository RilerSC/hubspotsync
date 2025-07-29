@echo off
echo =========================================
echo HUBSPOT_SYNC - Instalación Optimizada
echo Versión: SIN PANDAS (Más rápido)
echo =========================================

echo Verificando Python...
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

echo Verificando versión de Python...
%PYTHON_CMD% -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Se requiere Python 3.13 o superior
    echo Versión actual detectada:
    %PYTHON_CMD% --version
    echo Descarga Python 3.13 desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Versión de Python compatible
%PYTHON_CMD% --version

echo Creando entorno virtual...
if not exist "venv" (
    %PYTHON_CMD% -m venv venv
    echo ✅ Entorno virtual creado
) else (
    echo ℹ️ Entorno virtual ya existe
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Actualizando pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo Instalando dependencias optimizadas (SIN PANDAS)...
pip install -r requirements.txt

echo Verificando instalación...
%PYTHON_CMD% -c "import requests, pyodbc, tabulate, dotenv; print('✅ Todas las dependencias instaladas correctamente')"

echo Configurando variables de entorno...
if not exist ".env" (
    if exist ".env.template" (
        copy ".env.template" ".env"
        echo ✅ Archivo .env creado desde template
    ) else (
        echo # Configuración HubSpot > .env
        echo HUBSPOT_TOKEN=tu_token_aqui >> .env
        echo. >> .env
        echo # Configuración SQL Server >> .env
        echo SQL_SERVER=tu_servidor.database.windows.net >> .env
        echo SQL_DATABASE=tu_base_de_datos >> .env
        echo SQL_USER=tu_usuario >> .env
        echo SQL_PASSWORD=tu_contraseña >> .env
        echo ✅ Archivo .env creado con template básico
    )
    echo ¡IMPORTANTE! Edita el archivo .env con tus credenciales reales
) else (
    echo ℹ️ Archivo .env ya existe
)

echo =========================================
echo ✅ Instalación completada exitosamente
echo =========================================
echo OPTIMIZACIONES APLICADAS:
echo • Removido PANDAS para mayor velocidad
echo • Menor uso de memoria
echo • Tiempo de inicio más rápido
echo • Menor tamaño del ejecutable
echo =========================================
echo Próximos pasos:
echo 1. Edita el archivo .env con tus credenciales
echo 2. Ejecuta run_sync.bat para probar
echo 3. Programa como tarea usando task_scheduler.ps1
echo =========================================
pause
