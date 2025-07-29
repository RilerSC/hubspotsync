@echo off
REM HUBSPOT_SYNC - Script para tarea programada
REM Versión optimizada SIN PANDAS

echo [%date% %time%] ==================== >> sync_log.txt
echo [%date% %time%] Iniciando HUBSPOT_SYNC >> sync_log.txt
echo [%date% %time%] Versión: SIN PANDAS (Optimizada) >> sync_log.txt

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [%date% %time%] ERROR: Entorno virtual no encontrado >> sync_log.txt
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar archivo .env
if not exist ".env" (
    echo [%date% %time%] ERROR: Archivo .env no encontrado >> sync_log.txt
    exit /b 1
)

REM Ejecutar sincronización con logs
echo [%date% %time%] Ejecutando main.py... >> sync_log.txt
python main.py >> sync_log.txt 2>&1

REM Verificar código de salida
if %errorlevel% equ 0 (
    echo [%date% %time%] SUCCESS: Sincronización completada >> sync_log.txt
) else (
    echo [%date% %time%] ERROR: Falló la sincronización (código %errorlevel%) >> sync_log.txt
)

echo [%date% %time%] ==================== >> sync_log.txt
