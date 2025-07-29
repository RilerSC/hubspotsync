@echo off
echo ============================================
echo INSTALACIÓN PYODBC CON WHEEL PRECOMPILADO
echo ============================================

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

echo 🔍 Verificando arquitectura...
python -c "import platform; print('Arquitectura:', platform.machine()); print('Sistema:', platform.system())"

echo.
echo 📦 Descargando wheel precompilado...
echo Buscando pyodbc para Python 3.13 Windows...

REM Crear directorio temporal
if not exist "temp_wheels" mkdir temp_wheels
cd temp_wheels

echo.
echo 🌐 Descargando desde repositorio confiable...
echo Esto puede tomar unos minutos...

REM Intentar descargar wheel compatible
curl -L -o pyodbc-4.0.39-cp313-cp313-win_amd64.whl "https://files.pythonhosted.org/packages/b8/9f/4c82d6a9b5c4d6e5b8a2e5c8c3d2c3c1b8a6f/pyodbc-4.0.39-cp313-cp313-win_amd64.whl"

if exist "pyodbc-4.0.39-cp313-cp313-win_amd64.whl" (
    echo ✅ Wheel descargado exitosamente
    echo 📦 Instalando wheel...
    pip install pyodbc-4.0.39-cp313-cp313-win_amd64.whl
    if not errorlevel 1 (
        echo ✅ pyodbc instalado desde wheel
        cd ..
        goto :test_pyodbc
    )
)

echo.
echo ❌ Descarga automática falló
echo.
echo INSTRUCCIONES MANUALES:
echo 1. Ir a: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyodbc
echo 2. Descargar: pyodbc-X.X.X-cp313-cp313-win_amd64.whl
echo 3. Colocar archivo en esta carpeta
echo 4. Ejecutar: pip install archivo.whl
echo.
cd ..
goto :end

:test_pyodbc
echo.
echo 🧪 Probando pyodbc...
python -c "import pyodbc; print('✅ pyodbc version:', pyodbc.version)"
if errorlevel 1 (
    echo ❌ pyodbc instalado pero no funciona
) else (
    echo ✅ pyodbc funciona perfectamente
)

:end
echo.
echo ============================================
echo Si no funciona, el sistema puede continuar
echo sin pyodbc para extraer datos de HubSpot
echo ============================================
pause
