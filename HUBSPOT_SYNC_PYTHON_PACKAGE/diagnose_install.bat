@echo off
echo ============================================
echo DIAGNÓSTICO DE INSTALACIÓN
echo ============================================

REM Verificar archivos
echo 🔍 Verificando archivos...
echo.
if exist "requirements.txt" (
    echo ✅ requirements.txt encontrado
    echo Contenido:
    type requirements.txt
) else (
    echo ❌ requirements.txt NO encontrado
)

echo.
if exist "venv" (
    echo ✅ Carpeta venv encontrada
) else (
    echo ❌ Carpeta venv NO encontrada
)

echo.
if exist "venv\Scripts\activate.bat" (
    echo ✅ activate.bat encontrado
) else (
    echo ❌ activate.bat NO encontrado
)

REM Activar entorno virtual
echo.
echo ⚡ Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar ubicación
echo 🔍 Verificando ubicación...
echo Directorio actual: %cd%
echo.
echo Ubicación de python:
where python
echo.
echo Ubicación de pip:
where pip

REM Listar paquetes instalados
echo.
echo 📦 Paquetes instalados:
pip list

echo.
echo ============================================
pause
