@echo off
echo ============================================
echo HUBSPOT_SYNC - Ejecución Manual
echo Versión Optimizada SIN PANDAS
echo ============================================
echo Fecha inicio: %date% %time%

REM Verificar que existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Entorno virtual no encontrado
    echo Ejecuta install.bat primero
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

REM Verificar archivo .env
if not exist ".env" (
    echo ❌ Archivo .env no encontrado
    echo Ejecuta install.bat primero y configura tus credenciales
    pause
    exit /b 1
)

echo 🚀 Iniciando sincronización HubSpot...
echo ============================================

REM Ejecutar sincronización con manejo de errores
python main.py
if errorlevel 1 (
    echo ❌ Error durante la ejecución
    echo Revisa los logs anteriores
    pause
    exit /b 1
)

echo ============================================
echo ✅ Sincronización completada
echo Fecha fin: %date% %time%
echo ============================================
echo Presiona cualquier tecla para cerrar...
pause
