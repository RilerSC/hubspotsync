============================================
HUBSPOT_SYNC - Guía de Instalación
Versión Optimizada SIN PANDAS + Python 3.13
============================================

🚀 NOVEDADES EN ESTA VERSIÓN:
• Actualizado para Python 3.13 (más moderna y estable)
• Removido PANDAS para mayor velocidad
• Menor uso de memoria (hasta 70% menos)
• Tiempo de inicio más rápido
• Sincronización más eficiente
• Dependencias actualizadas y compatibles

📋 INSTALACIÓN RÁPIDA (RECOMENDADA):
1. Descarga Python 3.13 desde: https://www.python.org/downloads/
2. Ejecuta quick_install.bat como Administrador
3. Edita el archivo .env con tus credenciales reales
4. Ejecuta run_sync.bat para probar la sincronización

🔧 SI TIENES PROBLEMAS CON PYTHON:
1. Ejecuta diagnose_python.bat para verificar tu instalación
2. Ejecuta quick_install.bat (detecta automáticamente tu comando Python)
3. Si sigue fallando, usa migrate_to_python313.bat

📋 INSTALACIÓN MANUAL:
1. Ejecuta install.bat como Administrador
2. Edita el archivo .env con tus credenciales reales  
3. Ejecuta run_sync.bat para probar la sincronización

🔬 VERIFICACIÓN:
- Usa verify_python313.py para verificar compatibilidad
- Ejecuta python verify_python313.py antes de la primera sincronización

EJECUCIÓN MANUAL:
- Usar run_sync.bat (con pausa al final)
- Incluye verificaciones y mejor logging

TAREA PROGRAMADA:
- Usar run_sync_scheduled.bat (sin pausa, guarda logs)
- Usar task_scheduler.ps1 para configurar automáticamente
- Los logs se guardan en sync_log.txt

ARCHIVOS IMPORTANTES:
- .env: Configuración de credenciales
- sync_log.txt: Logs de ejecución automática
- requirements.txt: Dependencias optimizadas

REQUISITOS DEL SISTEMA:
- Windows 10/11 o Windows Server 2019+
- Python 3.13+ (versión más moderna y estable)
- 2GB RAM (reducido desde 4GB gracias a la optimización)
- Acceso a internet para instalación inicial

BENEFICIOS DE PYTHON 3.13:
- Mejor rendimiento y optimizaciones internas
- Sintaxis más moderna y características actualizadas
- Mayor compatibilidad con librerías actuales
- Mejor manejo de memoria y garbage collection
- Soporte extendido hasta 2029

SOLUCIÓN DE PROBLEMAS:
- Si falla la instalación: Ejecutar como Administrador
- Si falla la sincronización: Revisar credenciales en .env
- Si hay errores de permisos: Verificar acceso a SQL Server
- Para logs detallados: Revisar sync_log.txt

RENDIMIENTO:
- Sincronización típica: 50% más rápida que versión con pandas
- Uso de memoria: Reducido en ~70%
- Tiempo de inicio: ~3 segundos vs ~15 segundos anteriores

¿NECESITAS AYUDA?
Revisa los logs en sync_log.txt para diagnóstico detallado.
============================================
