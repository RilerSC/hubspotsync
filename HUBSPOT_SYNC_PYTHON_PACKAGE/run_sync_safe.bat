@echo off
echo ============================================
echo HUBSPOT_SYNC - Ejecución con Manejo de Errores
echo Versión Optimizada SIN PANDAS
echo ============================================
echo Fecha inicio: %date% %time%

REM Verificar que existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Entorno virtual no encontrado
    echo Ejecuta complete_install.bat primero
    pause
    exit /b 1
)

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar que el entorno virtual está activo
echo 🔍 Verificando entorno virtual...
where python
python --version

REM Verificar dependencias críticas
echo 🔍 Verificando dependencias críticas...
python -c "import requests; print('✅ requests OK')"
if errorlevel 1 (
    echo ❌ requests no funciona - ejecuta force_install.bat
    pause
    exit /b 1
)

python -c "from dotenv import load_dotenv; print('✅ dotenv OK')"
if errorlevel 1 (
    echo ❌ dotenv no funciona - ejecuta force_install.bat
    pause
    exit /b 1
)

REM Verificar archivo .env
if not exist ".env" (
    echo ❌ Archivo .env no encontrado
    echo Crea el archivo .env con tus credenciales:
    echo.
    echo HUBSPOT_TOKEN=tu_token_aqui
    echo SQL_SERVER=tu_servidor
    echo SQL_DATABASE=tu_base_datos
    echo SQL_USER=tu_usuario
    echo SQL_PASSWORD=tu_contraseña
    echo.
    pause
    exit /b 1
)

REM Verificar pyodbc (opcional)
echo 🔍 Verificando pyodbc...
python -c "import pyodbc; print('✅ pyodbc OK')"
if errorlevel 1 (
    echo ⚠️ pyodbc no disponible - el sync funcionará parcialmente
    echo Ver PYODBC_INFO.txt para más información
    echo.
    echo ¿Continuar sin conexión SQL Server? (S/N)
    set /p continuar=
    if /i not "%continuar%"=="S" (
        echo Operación cancelada
        pause
        exit /b 1
    )
)

echo 🚀 Iniciando sincronización HubSpot...
echo ============================================

REM Ejecutar sincronización con manejo de errores
python main.py
if errorlevel 1 (
    echo ❌ Error durante la ejecución
    echo.
    echo Posibles causas:
    echo - Credenciales incorrectas en .env
    echo - Token HubSpot inválido
    echo - Problemas de conectividad
    echo - pyodbc no instalado (para SQL Server)
    echo.
    echo Revisa los logs anteriores para más detalles
    pause
    exit /b 1
)

echo ============================================
echo ✅ Sincronización completada exitosamente
echo Fecha fin: %date% %time%
echo ============================================
echo Presiona cualquier tecla para cerrar...
pause
