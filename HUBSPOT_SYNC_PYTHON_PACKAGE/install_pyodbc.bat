@echo off
echo ============================================
echo INSTALACIÓN DE PYODBC PARA WINDOWS
echo ============================================

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

REM Intentar diferentes métodos de instalación de pyodbc
echo 📦 Método 1: Instalación directa...
pip install pyodbc
if not errorlevel 1 (
    echo ✅ pyodbc instalado exitosamente
    goto :test_pyodbc
)

echo 📦 Método 2: Instalación con wheel precompilado...
pip install --only-binary=all pyodbc
if not errorlevel 1 (
    echo ✅ pyodbc instalado exitosamente
    goto :test_pyodbc
)

echo 📦 Método 3: Instalación con upgrade...
pip install --upgrade pyodbc
if not errorlevel 1 (
    echo ✅ pyodbc instalado exitosamente
    goto :test_pyodbc
)

echo 📦 Método 4: Instalación forzada...
pip install --force-reinstall pyodbc
if not errorlevel 1 (
    echo ✅ pyodbc instalado exitosamente
    goto :test_pyodbc
)

echo ❌ No se pudo instalar pyodbc
echo Esto puede deberse a falta de Visual C++ Build Tools
echo.
echo Opciones:
echo 1. Instalar Microsoft C++ Build Tools
echo 2. Usar una versión precompilada
echo 3. Continuar sin pyodbc (solo para testing)
echo.
goto :end

:test_pyodbc
echo 🧪 Verificando pyodbc...
python -c "import pyodbc; print('✅ pyodbc version:', pyodbc.version)"
if errorlevel 1 (
    echo ❌ pyodbc instalado pero no funciona
) else (
    echo ✅ pyodbc funciona correctamente
)

:end
echo.
echo ============================================
echo Si pyodbc no funciona, el sync funcionará
echo parcialmente (sin conexión a SQL Server)
echo ============================================
pause
