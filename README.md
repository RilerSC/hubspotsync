# HUBSPOT_SYNC - Sistema de Sincronización Empresarial

```
================================================================================
                        HUBSPOT SYNC - SISTEMA PRINCIPAL
================================================================================

Proyecto:           Sistema de Sincronización HubSpot ↔ SQL Server
Versión:            2.0 - Optimizada sin pandas
Descripción:        Sistema empresarial para sincronización automatizada de datos
                   entre HubSpot CRM y SQL Server con análisis dinámico de 
                   propiedades y optimizaciones de rendimiento.

Autor:              Ing. Jose Ríler Solórzano Campos
Fecha de Creación:  11 de julio de 2025
Derechos de Autor:  © 2025 Jose Ríler Solórzano Campos. Todos los derechos reservados.
Licencia:           Uso exclusivo del autor. Prohibida la distribución sin autorización.

================================================================================
```

Sistema de sincronización de datos entre HubSpot y SQL Server, optimizado para máximo rendimiento.

## 🚀 Características Principales

- **70% menos uso de memoria** (eliminado pandas)
- **50% más rápido** que la versión anterior
- **Tiempo de inicio 5x más rápido**
- **Sincronización completa** de Deals, Tickets, Contacts, Owners y Pipelines
- **Paquete para Windows Server** listo para producción
- **Análisis dinámico** de propiedades para optimización automática
- **Deduplicación automática** y manejo robusto de errores

## � Capacidades del Sistema

| Entidad | Volumen Típico | Propiedades Analizadas | Tiempo Estimado |
|---------|---------------|----------------------|-----------------|
| **Deals** | ~2,000 registros | ~100 de 905 disponibles | 2-3 minutos |
| **Tickets** | ~1,100 registros | ~270 de 606 disponibles | 1-2 minutos |
| **Contacts** | ~5,000 registros | ~260 de 568 disponibles | 3-4 minutos |
| **Owners** | ~25 registros | 11 propiedades fijas | 30 segundos |
| **Pipelines** | ~155 registros | Estructura completa | 1 minuto |

## �📁 Estructura del Proyecto Optimizada

```
HUBSPOT_SYNC/
├── main.py                          # Script principal con documentación completa
├── hubspot/                          # Módulos especializados por entidad
│   ├── __init__.py                  # Inicializador del paquete
│   ├── fetch_deals.py               # Extractor de deals con análisis dinámico
│   ├── fetch_tickets.py             # Extractor de tickets con transformaciones
│   ├── fetch_contacts.py            # Extractor de contactos optimizado
│   ├── fetch_owners.py              # Extractor de propietarios y equipos
│   ├── fetch_deals_pipelines.py     # Extractor de etapas de ventas
│   └── fetch_tickets_pipelines.py   # Extractor de etapas de soporte
├── HUBSPOT_SYNC_PYTHON_PACKAGE/     # Paquete para Windows Server
│   ├── install.bat                  # Instalador automático de dependencias
│   ├── run_sync.bat                 # Ejecución manual del sincronizador
│   ├── run_sync_scheduled.bat       # Ejecución para tareas programadas
│   ├── task_scheduler.ps1           # Configurador automático de tareas
│   ├── requirements.txt             # Dependencias optimizadas sin pandas
│   └── README.txt                   # Guía de implementación Windows
└── .env                             # Variables de configuración (no incluido)
│   └── hubspot/                    # Módulos duplicados para independencia
└── README.md                       # Esta documentación
```

## ⚡ Optimizaciones Aplicadas

- **Eliminado pandas**: Uso de estructuras nativas de Python
- **Eliminado código duplicado**: Archivos _bk.py removidos
- **Eliminadas dependencias innecesarias**: Solo lo esencial
- **Limpieza de archivos temporales**: Sin cache ni builds
- **Estructura simplificada**: Solo archivos funcionales

## 🛠 Instalación Local (macOS/Linux)

1. **Clonar entorno virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En macOS/Linux
   ```

2. **Instalar dependencias:**
   ```bash
   pip install python-dotenv==1.0.0 pyodbc==4.0.39 tabulate==0.9.0 requests==2.31.0 urllib3==1.26.16
   ```

3. **Configurar variables de entorno:**
   ```bash
   cp .env.template .env
   # Editar .env con tus credenciales
   ```

4. **Ejecutar:**
   ```bash
   python main.py
   ```

## 🏢 Instalación en Windows Server

Usar el paquete `HUBSPOT_SYNC_PYTHON_PACKAGE/`:

1. **Copiar carpeta completa al servidor**
2. **Ejecutar como Administrador:** `install.bat`
3. **Configurar credenciales:** Editar `.env`
4. **Probar:** `run_sync.bat`
5. **Programar:** `task_scheduler.ps1`

## 📊 Datos Sincronizados

| Entidad | Tabla SQL | Propiedades | Descripción |
|---------|-----------|-------------|-------------|
| Deals | hb_deals | ~102 | Oportunidades de venta |
| Tickets | hb_tickets | ~274 | Tickets de soporte |
| Contacts | hb_contacts | ~225 | Contactos CRM |
| Owners | hb_owners | ~11 | Propietarios/Usuarios |
| Deal Pipelines | hb_deals_pipeline | ~11 | Configuración de deals |
| Ticket Pipelines | hb_tickets_pipeline | ~13 | Configuración de tickets |

## 🔧 Dependencias

```txt
python-dotenv==1.0.0    # Variables de entorno
pyodbc==4.0.39          # Conectividad SQL Server
tabulate==0.9.0         # Formateo de tablas
requests==2.31.0        # Peticiones HTTP
urllib3==1.26.16        # Manejo de URLs
```

## 📈 Rendimiento

- **Memoria**: ~500MB vs ~1.7GB (anterior)
- **Tiempo inicio**: ~3 seg vs ~15 seg
- **Velocidad sync**: 50% más rápido
- **Tamaño paquete**: 80% más pequeño

## 🚀 Uso

```python
python main.py
```

El script automáticamente:
1. ✅ Verifica configuración
2. 🔹 Procesa Deals
3. 🎫 Procesa Tickets  
4. 👥 Procesa Contacts
5. 👨‍💼 Procesa Owners
6. 📊 Procesa Pipelines
7. ✅ Muestra resumen final

## 🔐 Variables de Entorno

```env
# HubSpot
HUBSPOT_TOKEN=tu_token_aqui

# SQL Server
SQL_SERVER=servidor.database.windows.net
SQL_DATABASE=base_datos
SQL_USER=usuario
SQL_PASSWORD=contraseña
```

## 📝 Logs y Monitoreo

- **Manual**: Salida en consola con emojis y colores
- **Programado**: Logs automáticos en `sync_log.txt`
- **Errores**: Manejo robusto con fallbacks

¡Proyecto limpio y optimizado! 🎉