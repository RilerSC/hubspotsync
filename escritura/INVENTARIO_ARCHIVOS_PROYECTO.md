# 📋 INVENTARIO DE ARCHIVOS DEL PROYECTO HUBSPOT SYNC

**Fecha de inventario:** 1 de agosto de 2025  
**Estado del proyecto:** Productivo y funcional  
**Autor:** Sistema de sincronización SQL Server ↔ HubSpot

---

## 🚀 ARCHIVOS VITALES DE PRODUCCIÓN

### 📁 **Scripts de Producción Principal**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `production_update.py` | **SCRIPT PRINCIPAL** - UPDATE masivo de contactos existentes | ✅ **CRÍTICO** |
| `production_insert_full.py` | **SCRIPT PRINCIPAL** - INSERT masivo de contactos nuevos | ✅ **CRÍTICO** |
| `main.py` | Script de entrada principal del sistema | ✅ **VITAL** |

### 📁 **Archivos de Configuración**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `.env` | Variables de entorno (tokens, credenciales DB) | ✅ **CRÍTICO** |
| `config.yaml` | Configuración general del sistema | ✅ **VITAL** |
| `requirements_escritura.txt` | Dependencias Python del proyecto | ✅ **VITAL** |

### 📁 **Consultas SQL de Producción**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `HB_UPDATE.sql` | Consulta SQL para obtener datos de UPDATE | ✅ **CRÍTICO** |
| `HB_INSERT.sql` | Consulta SQL para obtener datos de INSERT | ✅ **CRÍTICO** |
| `sp_hubspot_update.sql` | Stored procedure para UPDATE (opcional) | ⚠️ **OPCIONAL** |
| `sp_hubspot_insert.sql` | Stored procedure para INSERT (opcional) | ⚠️ **OPCIONAL** |

### 📁 **Mapeos de Campos**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `MAPEO_COLUMNAS.csv` | Mapeo de campos SQL → HubSpot (UPDATE - 39 campos) | ✅ **CRÍTICO** |
| `MAPEO_INSERT.csv` | Mapeo de campos SQL → HubSpot (INSERT - 55 campos) | ✅ **CRÍTICO** |

### 📁 **Módulos del Sistema (`config/`)**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `config/settings.py` | Configuración y variables del sistema | ✅ **CRÍTICO** |
| `config/__init__.py` | Inicializador del módulo config | ✅ **VITAL** |

### 📁 **Conectores de Base de Datos (`db/`)**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `db/mssql_connector.py` | Conector a SQL Server para obtener datos | ✅ **CRÍTICO** |
| `db/__init__.py` | Inicializador del módulo db | ✅ **VITAL** |

### 📁 **Cliente HubSpot (`hubspot_client/`)**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `hubspot_client/writer.py` | **CORE** - Cliente para escribir en HubSpot API | ✅ **CRÍTICO** |
| `hubspot_client/field_mapper.py` | Mapeador de campos para UPDATE (39 campos) | ✅ **CRÍTICO** |
| `hubspot_client/field_mapper_insert.py` | Mapeador de campos para INSERT (55 campos) | ✅ **CRÍTICO** |
| `hubspot_client/__init__.py` | Inicializador del módulo hubspot_client | ✅ **VITAL** |

### 📁 **Utilidades (`utils/`)**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `utils/logger.py` | Sistema de logging del proyecto | ✅ **CRÍTICO** |
| `utils/__init__.py` | Inicializador del módulo utils | ✅ **VITAL** |

### 📁 **Logs de Producción (`logs/`)**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `logs/hubspot_sync_2025-08-01.log` | **LOG VITAL** - Ejecución UPDATE masivo exitoso | ✅ **HISTÓRICO** |
| `logs/hubspot_sync_2025-07-31.log` | Log de desarrollo y pruebas finales | ✅ **HISTÓRICO** |
| `logs/hubspot_sync_2025-07-30.log` | Log de desarrollo inicial | ✅ **HISTÓRICO** |
| `logs/.gitkeep` | Mantiene la carpeta logs en git | ✅ **VITAL** |

### 📁 **Reportes de Producción**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `insert_conflicts_20250801_011406.csv` | Reporte de conflictos del INSERT masivo | ✅ **HISTÓRICO** |
| `insert_success_20250801_011406.csv` | Reporte de éxitos del INSERT masivo | ✅ **HISTÓRICO** |

### 📁 **Documentación Vital**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `README_PRODUCTION.md` | **MANUAL DE PRODUCCIÓN** - Guía de uso | ✅ **CRÍTICO** |
| `README_ESCRITURA.md` | Documentación técnica del desarrollo | ✅ **VITAL** |
| `README.md` | Documentación general del proyecto | ✅ **VITAL** |

---

## 🧪 ARCHIVOS DE DESARROLLO Y PRUEBAS

### 📁 **Scripts de Pruebas Unitarias**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `test_cedula_110100747.py` | **PRUEBA CLAVE** - Validó estrategia exitosa | 🧪 **REFERENCIA** |
| `test_production_ready.py` | Pruebas finales antes de producción | 🧪 **REFERENCIA** |
| `test_force_properties.py` | Prueba de force_all_properties (estrategia exitosa) | 🧪 **REFERENCIA** |
| `test_single_update.py` | Pruebas de actualización individual | 🧪 **DESARROLLO** |
| `test_single_insert.py` | Pruebas de inserción individual | 🧪 **DESARROLLO** |
| `test_dry_run.py` | Pruebas en modo simulación | 🧪 **DESARROLLO** |
| `test_direct_update.py` | Pruebas de actualización directa | 🧪 **DESARROLLO** |
| `test_hubspot_direct_update.py` | Pruebas directas de HubSpot API | 🧪 **DESARROLLO** |
| `test_auto_update.py` | Pruebas de actualización automática | 🧪 **DESARROLLO** |
| `test_forced_update_sql.py` | Pruebas con SQL forzado | 🧪 **DESARROLLO** |
| `test_force_simple.py` | Pruebas simples de forzado | 🧪 **DESARROLLO** |
| `test_insert_dry_run.py` | Pruebas INSERT en modo simulación | 🧪 **DESARROLLO** |
| `test_insert_process.py` | Pruebas del proceso de INSERT | 🧪 **DESARROLLO** |
| `test_simple.py` | Pruebas básicas del sistema | 🧪 **DESARROLLO** |
| `test_single_field.py` | Pruebas de campos individuales | 🧪 **DESARROLLO** |
| `test_specific_insert.py` | Pruebas de INSERT específico | 🧪 **DESARROLLO** |
| `test_update_only.py` | Pruebas solo de UPDATE | 🧪 **DESARROLLO** |

### 📁 **Scripts de Verificación y Debug**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `check_final_result.py` | Verificación de resultados finales | 🧪 **DESARROLLO** |
| `check_all_properties.py` | Verificación de todas las propiedades | 🧪 **DESARROLLO** |
| `check_properties_hubspot.py` | Verificación de propiedades en HubSpot | 🧪 **DESARROLLO** |
| `check_property_names.py` | Verificación de nombres de propiedades | 🧪 **DESARROLLO** |
| `check_field_options.py` | Verificación de opciones de campos | 🧪 **DESARROLLO** |
| `check_contact_location.py` | Verificación de ubicación de contactos | 🧪 **DESARROLLO** |
| `check_result.py` | Verificación general de resultados | 🧪 **DESARROLLO** |
| `debug_csv.py` | Debug de archivos CSV | 🧪 **DESARROLLO** |
| `debug_field_mapping.py` | Debug del mapeo de campos | 🧪 **DESARROLLO** |
| `debug_update_detailed.py` | Debug detallado de actualizaciones | 🧪 **DESARROLLO** |

### 📁 **Scripts de Análisis y Exploración**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `analyze_field_formats_detailed.py` | Análisis detallado de formatos | 🧪 **DESARROLLO** |
| `list_hubspot_properties.py` | Listado de propiedades de HubSpot | 🧪 **DESARROLLO** |
| `find_contact.py` | Búsqueda de contactos específicos | 🧪 **DESARROLLO** |
| `verify_properties_exist.py` | Verificación de existencia de propiedades | 🧪 **DESARROLLO** |
| `verify_specific_fields.py` | Verificación de campos específicos | 🧪 **DESARROLLO** |

### 📁 **Scripts de Testing Rápido**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `quick_test.py` | Pruebas rápidas generales | 🧪 **DESARROLLO** |
| `quick_check_110100747.py` | Prueba rápida con cédula específica | 🧪 **DESARROLLO** |
| `quick_insert_check.py` | Verificación rápida de INSERT | 🧪 **DESARROLLO** |
| `quick_insert_test.py` | Prueba rápida de INSERT | 🧪 **DESARROLLO** |
| `update_110100747.py` | Actualización de contacto específico | 🧪 **DESARROLLO** |

### 📁 **Archivos de Desarrollo Específico**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `create_correct_mapping.py` | Creación de mapeo correcto | 🧪 **DESARROLLO** |
| `test_conflict_capture.py` | Prueba de captura de conflictos | 🧪 **DESARROLLO** |
| `hubspot_client/field_mapper_fixed.py` | Versión corregida del mapper (no usada) | 🧪 **DESCARTADO** |

### 📁 **Reportes de Pruebas**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `test_conflicts_20250801_014041.csv` | Reporte de conflictos de prueba | 🧪 **DESARROLLO** |
| `test_success_20250801_014041.csv` | Reporte de éxitos de prueba | 🧪 **DESARROLLO** |

### 📁 **Documentación de Desarrollo**
| Archivo | Propósito | Estado |
|---------|-----------|---------|
| `PROYECTO_ESCRITURA_HUBSPOT.md` | Documentación del desarrollo del proyecto | 🧪 **DESARROLLO** |

---

## 📊 RESUMEN DE CLASIFICACIÓN

### ✅ **ARCHIVOS CRÍTICOS DE PRODUCCIÓN** (No eliminar nunca)
- **24 archivos** esenciales para el funcionamiento
- Scripts principales, configuración, mapeos, conectores, logs

### ⚠️ **ARCHIVOS DE REFERENCIA** (Mantener por documentación)
- **3 archivos** que validaron las estrategias exitosas
- Útiles para futuras modificaciones o troubleshooting

### 🧪 **ARCHIVOS DE DESARROLLO** (Candidatos a limpieza)
- **35+ archivos** de pruebas, debug y desarrollo
- Pueden ser movidos a carpeta de archive o eliminados

### 📈 **ESTADÍSTICAS**
- **Total de archivos:** ~65 archivos
- **Productivo:** 37% (24 archivos críticos + logs + reportes)
- **Desarrollo:** 63% (archivos de prueba y desarrollo)

---

## 🎯 **RECOMENDACIONES**

### 💡 **Para limpieza del proyecto:**
1. **MANTENER:** Todos los archivos críticos y de referencia
2. **ARCHIVAR:** Scripts de desarrollo en subcarpeta `archive/`
3. **DOCUMENTAR:** Este inventario como guía permanente

### 📁 **Estructura recomendada:**
```
escritura/
├── 🚀 PRODUCCIÓN/          # Solo archivos críticos
├── 📚 DOCUMENTACIÓN/       # READMEs y guías
├── 📊 LOGS/               # Logs históricos
├── 🧪 ARCHIVE/            # Scripts de desarrollo
└── 📋 INVENTARIOS/        # Este documento
```

---

**🎉 PROYECTO COMPLETAMENTE FUNCIONAL**  
**Sistema de sincronización bidireccional SQL Server ↔ HubSpot operativo**
