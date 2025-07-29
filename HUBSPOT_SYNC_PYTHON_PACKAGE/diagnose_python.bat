@echo off
echo =============================================
echo DIAGNÓSTICO DE PYTHON - HUBSPOT_SYNC
echo =============================================

echo.
echo 🔍 Verificando comandos de Python disponibles...
echo.

echo Probando comando: python
python --version 2>nul
if %errorlevel% equ 0 (
    echo ✅ python funciona
    python --version
) else (
    echo ❌ python no está disponible
)

echo.
echo Probando comando: python3
python3 --version 2>nul
if %errorlevel% equ 0 (
    echo ✅ python3 funciona
    python3 --version
) else (
    echo ❌ python3 no está disponible
)

echo.
echo Probando comando: py
py --version 2>nul
if %errorlevel% equ 0 (
    echo ✅ py funciona
    py --version
) else (
    echo ❌ py no está disponible
)

echo.
echo =============================================
echo 📋 INFORMACIÓN DEL SISTEMA
echo =============================================
echo Sistema operativo: %OS%
echo Versión: %OS%
echo Arquitectura: %PROCESSOR_ARCHITECTURE%
echo Usuario: %USERNAME%
echo Directorio actual: %CD%

echo.
echo =============================================
echo 🔧 VARIABLES DE ENTORNO (PATH)
echo =============================================
echo Buscando Python en PATH...
echo.
for %%i in (python.exe python3.exe py.exe) do (
    where %%i 2>nul
    if %errorlevel% equ 0 (
        echo ✅ Encontrado: %%i
    ) else (
        echo ❌ No encontrado: %%i
    )
)

echo.
echo =============================================
echo 📝 RECOMENDACIONES
echo =============================================
echo.
echo Si ningún comando funciona:
echo 1. Reinstala Python desde: https://www.python.org/downloads/
echo 2. ¡IMPORTANTE! Marca "Add Python to PATH" durante la instalación
echo 3. Reinicia el símbolo del sistema después de la instalación
echo.
echo Si solo funciona "py":
echo - Usa "py" en lugar de "python" en todos los comandos
echo - El script install.bat actualizado debería detectarlo automáticamente
echo.
echo Si solo funciona "python3":
echo - Usa "python3" en lugar de "python" en todos los comandos
echo - El script install.bat actualizado debería detectarlo automáticamente
echo.
echo =============================================
pause
