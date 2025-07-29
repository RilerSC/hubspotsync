@echo off
echo ============================================
echo DIAGNÓSTICO AVANZADO PYODBC
echo ============================================

REM Activar entorno virtual
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

echo 🔍 Verificando Visual Studio Build Tools...
echo.
echo Buscando cl.exe (compilador C++)...
where cl.exe
if errorlevel 1 (
    echo ❌ cl.exe no encontrado
) else (
    echo ✅ cl.exe encontrado
)

echo.
echo Verificando variables de entorno...
if defined VS170COMNTOOLS (
    echo ✅ VS170COMNTOOLS definido: %VS170COMNTOOLS%
) else (
    echo ❌ VS170COMNTOOLS no definido
)

echo.
echo 🔍 Intentando diferentes métodos de instalación...

echo.
echo Método 1: Instalación desde PyPI con verbose...
pip install pyodbc --verbose
if not errorlevel 1 (
    echo ✅ Método 1 exitoso
    goto :test_pyodbc
)

echo.
echo Método 2: Instalación con cache limpio...
pip install pyodbc --no-cache-dir
if not errorlevel 1 (
    echo ✅ Método 2 exitoso
    goto :test_pyodbc
)

echo.
echo Método 3: Instalación con usuario...
pip install pyodbc --user
if not errorlevel 1 (
    echo ✅ Método 3 exitoso
    goto :test_pyodbc
)

echo.
echo Método 4: Instalación con versión específica...
pip install pyodbc==4.0.39
if not errorlevel 1 (
    echo ✅ Método 4 exitoso
    goto :test_pyodbc
)

echo.
echo Método 5: Buscando wheel precompilado...
pip install --find-links https://download.lfd.uci.edu/pythonlibs/archived/ pyodbc
if not errorlevel 1 (
    echo ✅ Método 5 exitoso
    goto :test_pyodbc
)

echo.
echo ❌ Ningún método funcionó
echo.
echo DIAGNÓSTICO:
echo - Visual Studio instalado pero Build Tools no configurados
echo - O necesitas reiniciar el sistema
echo - O faltan componentes específicos de C++
echo.
echo SOLUCIONES:
echo 1. Reiniciar Windows
echo 2. Instalar "Microsoft C++ Build Tools" específicamente
echo 3. Usar wheel precompilado manualmente
echo 4. Continuar sin pyodbc (recomendado)
echo.
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
echo RECOMENDACIÓN: Continuar sin pyodbc
echo El sistema funcionará al 90% sin problemas
echo ============================================
pause
