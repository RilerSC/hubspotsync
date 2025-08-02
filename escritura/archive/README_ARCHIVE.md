# 📁 ARCHIVO DE ARCHIVOS NO PRODUCTIVOS

Este directorio contiene todos los archivos que fueron parte del desarrollo y debugging del proyecto HubSpot Sync, pero que NO son necesarios para la operación en producción.

## 📂 **Estructura del Archivo:**

### 🧪 `tests/` - Scripts de Pruebas
- **25 archivos** de pruebas unitarias, de integración y validación
- Scripts que fueron fundamentales para validar la funcionalidad
- Incluye el histórico `test_cedula_110100747.py` que validó la estrategia exitosa
- Reportes CSV de pruebas

### 🔍 `debug/` - Scripts de Debugging y Verificación  
- **14 archivos** de debugging, verificación y análisis
- Scripts para revisar propiedades, campos, contactos específicos
- Herramientas de diagnóstico utilizadas durante el desarrollo

### 🛠️ `development/` - Archivos de Desarrollo
- **4 archivos** de desarrollo específico
- Versiones experimentales de mappers
- Documentación de desarrollo
- Scripts de creación de mapeos

## 🎯 **Propósito del Archivo:**

1. **Mantener historia del desarrollo** para futuras referencias
2. **Limpieza del directorio principal** para mejor organización
3. **Conservar scripts de debugging** por si son necesarios en el futuro
4. **Documentar el proceso de desarrollo** completo

## ⚠️ **IMPORTANTE:**

- **NO eliminar estos archivos** - contienen historia valiosa del proyecto
- **NO son necesarios para producción** - el sistema funciona sin ellos
- **Pueden ser útiles para troubleshooting** futuro
- **Documentan el proceso de desarrollo** y validación

## 📊 **Total de Archivos Archivados:**

- **Tests:** 25 archivos
- **Debug:** 14 archivos  
- **Development:** 4 archivos
- **Total:** 43 archivos movidos del directorio principal

---

**Fecha de archivo:** 1 de agosto de 2025  
**Estado del proyecto principal:** Limpio y productivo  
**Sistema:** 100% funcional sin estos archivos

---

## 🛠️ Tecnologías Utilizadas
- **Python 3.13.5**
- **hubspot-api-client** (API oficial HubSpot v3)
- **pyodbc** (conexión SQL Server)
- **dotenv** (manejo de variables de entorno)
- **SQL Server** (extracción de datos con HB_UPDATE.sql y HB_INSERT.sql)
- **CSV** (mapeos y reportes)
- **Windows PowerShell** (automatización y manejo de archivos)

## 📈 Estadísticas de Procesos Masivos

### UPDATE masivo
- **Total de contactos procesados:** 8,800
- **Contactos actualizados exitosamente:** 4,393
- **Tasa de éxito:** 49.9%
- **Estrategia:** force_all_properties, mapeo por MAPEO_COLUMNAS.csv
- **Reporte generado:** logs/update_results.csv

### INSERT masivo
- **Total de registros procesados:** 2,100
- **Contactos insertados exitosamente:** 2
- **Conflictos detectados (emails existentes):** 2,098
- **Estrategia:** mapeo por MAPEO_INSERT.csv, detección de duplicados
- **Reporte generado:** logs/insert_results.csv

---

**Este archivo resume la historia técnica y operativa del proyecto, permitiendo trazabilidad y auditoría futura.**
