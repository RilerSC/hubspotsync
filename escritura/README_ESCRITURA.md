# HubSpot Sync - Etapa 2: Escritura de Datos

Este módulo implementa la sincronización de datos desde SQL Server hacia HubSpot usando la API oficial v3.

## 🏗️ Arquitectura del Proyecto

```
escritura/
├── .env                           # Variables de entorno (credenciales)
├── main.py                        # Script principal de sincronización
├── 
├── config/                        # Configuración del sistema
│   ├── __init__.py
│   └── settings.py               # Configuraciones centralizadas
│
├── db/                           # Conectores de base de datos
│   ├── __init__.py
│   └── mssql_connector.py        # Conector SQL Server
│
├── hubspot_client/               # Cliente HubSpot
│   ├── __init__.py
│   ├── field_mapper.py          # Mapeo de campos SQL -> HubSpot
│   └── writer.py                # Cliente API HubSpot v3
│
├── utils/                        # Utilidades del sistema
│   ├── __init__.py
│   └── logger.py                # Sistema de logging con colores
│
├── logs/                         # Directorio de logs del sistema
│
└── consultas SQL/
    ├── HB_INSERT.sql            # Consulta para contactos nuevos
    └── HB_UPDATE.sql            # Consulta para actualizaciones
```

## 🚀 Funcionalidades Principales

### ✅ Sincronización Bidireccional
- **INSERT**: Crea nuevos contactos en HubSpot desde datos de `HB_INSERT.sql`
- **UPDATE**: Actualiza contactos existentes en HubSpot desde datos de `HB_UPDATE.sql`

### ✅ Identificación Única
- Cada contacto se identifica por el campo `no__de_cedula` (número de cédula)
- Validación y limpieza automática de números de cédula
- Detección de duplicados antes de insertar

### ✅ Mapeo Inteligente de Campos
- Mapeo automático de 60+ campos entre SQL Server y HubSpot
- Validación de formatos (emails, teléfonos, fechas)
- Conversión de tipos de datos según requerimientos de HubSpot
- Soporte para campos personalizados de productos financieros

### ✅ Procesamiento por Lotes
- Procesamiento eficiente en lotes de hasta 100 contactos
- Respeto de límites de rate limiting de HubSpot
- Estadísticas detalladas de cada operación

### ✅ Sistema de Logging Avanzado
- Logs con colores en consola para mejor visualización
- Logs detallados en archivos por fecha
- Diferentes niveles de logging (DEBUG, INFO, WARNING, ERROR)
- Tracking completo de operaciones y errores

## 🔧 Configuración

### Variables de Entorno (.env)
```env
# HubSpot API
HUBSPOT_TOKEN=pat-na1-xxxxxxxxx

# SQL Server
SQL_SERVER=52.146.8.210
SQL_DATABASE=PROCE
SQL_USER=sa
SQL_PASSWORD=xxxxxxxxx

# Configuración
DEBUG_MODE=False
BATCH_SIZE=1000
SYNC_TIMEOUT=300
```

### Dependencias Python
```
python-dotenv        # Gestión de variables de entorno
requests            # Peticiones HTTP
pyodbc              # Conector SQL Server
hubspot-api-client  # Cliente oficial HubSpot API v3
colorama            # Colores en terminal
```

## 🎯 Uso del Sistema

### Ejecución Principal
```bash
# Ejecutar sincronización completa
python main.py
```

### Validación de Entorno
```python
import main
success = main.validate_environment()  # Valida configuración
```

### Prueba de Conexiones
```python
import main
success = main.test_connections()  # Prueba SQL Server y HubSpot
```

## 📊 Mapeo de Campos

### Campos de Identificación
| SQL Server | HubSpot | Descripción |
|------------|---------|-------------|
| `no__de_cedula` | `no__de_cedula` | ✅ Campo clave de identificación |
| `numero_asociado` | `numero_asociado` | Número de asociado |

### Campos de Contacto Estándar
| SQL Server | HubSpot | Descripción |
|------------|---------|-------------|
| `firstname` | `firstname` | ✅ Nombre |
| `lastname` | `lastname` | ✅ Apellido |
| `email` | `email` | ✅ Email principal |
| `email_bncr` | `email_bncr` | Email BNCR |
| `telefono_habitacion` | `phone` | ✅ Teléfono principal |
| `telefono_oficina` | `mobilephone` | Teléfono móvil |
| `hs_whatsapp_phone_number` | `hs_whatsapp_phone_number` | WhatsApp |

### Campos de Productos Financieros
| SQL Server | HubSpot | Descripción |
|------------|---------|-------------|
| `con_ahorros` | `con_ahorros` | Tiene productos de ahorro |
| `con_credito` | `con_credito` | Tiene productos de crédito |
| `tiene_economias` | `tiene_economias` | Cuenta de economías |
| `consumo_personal` | `consumo_personal` | Crédito personal |
| ... | ... | +40 campos más de productos |

## 🔍 Proceso de Sincronización

### Fase 1: INSERT (Contactos Nuevos)
1. **Extracción**: Ejecuta consulta `HB_INSERT.sql`
2. **Validación**: Verifica que contactos no existan en HubSpot
3. **Mapeo**: Convierte datos SQL Server → formato HubSpot
4. **Creación**: Crea contactos en lotes de 100
5. **Logging**: Registra estadísticas detalladas

### Fase 2: UPDATE (Contactos Existentes)
1. **Extracción**: Ejecuta consulta `HB_UPDATE.sql`
2. **Búsqueda**: Encuentra contactos existentes por cédula
3. **Mapeo**: Convierte datos actualizados
4. **Actualización**: Actualiza contactos uno por uno
5. **Logging**: Registra cambios y estadísticas

## 📈 Estadísticas y Monitoreo

### Métricas de INSERT
- `total`: Total de registros procesados
- `processed`: Registros procesados
- `created`: Contactos creados exitosamente
- `skipped`: Contactos omitidos (ya existían)
- `errors`: Errores durante la creación

### Métricas de UPDATE
- `total`: Total de registros para actualizar
- `processed`: Registros procesados
- `updated`: Contactos actualizados exitosamente
- `not_found`: Contactos no encontrados en HubSpot
- `errors`: Errores durante la actualización

## 🛡️ Validaciones y Seguridad

### Validación de Datos
- ✅ Formato de emails (RFC 5322)
- ✅ Limpieza de números de teléfono (+506 para Costa Rica)
- ✅ Validación de cédulas (8-12 dígitos)
- ✅ Conversión de fechas a timestamp milisegundos
- ✅ Normalización de valores booleanos

### Manejo de Errores
- Reconexión automática a SQL Server
- Retry logic para errores temporales de API
- Logging detallado de todos los errores
- Continuación del proceso ante errores aislados

### Rate Limiting
- Respeto de límites de HubSpot (100 requests/10 segundos)
- Pausas automáticas entre lotes
- Monitoreo de límites de API

## 🎛️ Configuración Avanzada

### Logging Personalizado
```python
from utils.logger import setup_logging

# Configurar logging personalizado
logger_system = setup_logging(log_dir='custom_logs', log_level='DEBUG')
logger = logger_system.get_sync_logger()
```

### Mapeo de Campos Personalizado
```python
from hubspot_client.field_mapper import HubSpotFieldMapper

mapper = HubSpotFieldMapper()
# Agregar mapeos personalizados al diccionario field_mapping
```

### Conexión SQL Personalizada
```python
from db.mssql_connector import MSSQLConnector

with MSSQLConnector() as db:
    data = db.execute_query("SELECT * FROM custom_table")
```

## 🚦 Estados del Sistema

### ✅ Operacional
- Todas las validaciones pasan
- Conexiones SQL Server y HubSpot activas
- Consultas SQL disponibles

### ⚠️ Advertencias
- Algunos contactos omitidos por datos inválidos
- Rate limiting activado
- Errores menores en campos específicos

### ❌ Error Crítico
- Falla en conexión a SQL Server o HubSpot
- Archivos de consulta SQL no encontrados
- Configuraciones requeridas faltantes

## 📝 Notas Técnicas

### Optimizaciones de Rendimiento
- Uso de prepared statements en SQL Server
- Conexiones persistentes cuando es posible
- Procesamiento en memoria para lotes pequeños
- Lazy loading de configuraciones

### Compatibilidad
- Python 3.8+
- SQL Server 2016+
- HubSpot API v3
- Windows/Linux/macOS

### Limitaciones Conocidas
- Máximo 100 contactos por lote (limitación HubSpot)
- Rate limit de 100 requests/10 segundos
- Campos de texto limitados a 1000 caracteres
- Dependencia de conexión estable a Internet

---

**Desarrollado para HUBSPOT_SYNC - Integración SQL Server ↔ HubSpot**
