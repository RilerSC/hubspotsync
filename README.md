# HubSpot Sync

🚀 **Sistema de Sincronización Empresarial HubSpot ↔ SQL Server**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)

## 📋 Descripción

Sistema empresarial avanzado para la sincronización automatizada de datos entre **HubSpot CRM** y **SQL Server**. Optimizado para máximo rendimiento con análisis dinámico de propiedades y procesamiento en lotes.

### ✨ Características Destacadas

- **🚀 70% menos uso de memoria** - Sistema optimizado sin pandas
- **⚡ 50% más rápido** que versiones anteriores  
- **🔍 Análisis dinámico** de propiedades HubSpot
- **📊 Sincronización completa** de todas las entidades
- **🛡️ Manejo robusto de errores** con fallbacks automáticos
- **📦 Paquete completo** para Windows Server

## 🎯 Entidades Sincronizadas

### 📥 Lectura: HubSpot → SQL Server (main.py)
Ejecutar: `python main.py`

| Entidad | Descripción | Volumen Típico |
|---------|-------------|----------------|
| **Deals** | Negocios y oportunidades de venta | ~2,000 registros |
| **Tickets** | Tickets de soporte y servicio | ~1,100 registros |
| **Contacts** | Contactos y leads | ~5,000 registros |
| **Owners** | Propietarios y usuarios | ~25 registros |
| **Pipelines** | Estructuras de procesos | ~155 registros |

### 📤 Escritura: SQL Server → HubSpot (escritura/)
**⚡ EJECUTAR**: `python escritura/run_full_sync.py`

| Proceso | Script | Descripción |
|---------|---------|-------------|
| **Coordinador Principal** | `run_full_sync.py` | 🎯 **USAR ESTE ARCHIVO** - Ejecuta todo automáticamente |
| INSERT | `production_insert_full.py` | Contactos nuevos (ejecutado automáticamente) |
| UPDATE | `production_update.py` | Contactos existentes (ejecutado automáticamente) |

> 🚨 **IMPORTANTE**: Para escritura a HubSpot, usar SOLO `run_full_sync.py` que coordina ambos procesos en el orden correcto.

## 📊 Rendimiento

- **Tiempo total de sincronización**: 6-8 minutos
- **Propiedades analizadas**: 500+ automáticamente
- **Tablas SQL generadas**: 6 tablas optimizadas
- **Compatibilidad**: Python 3.9+ / SQL Server 2016+

## 🚀 Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/RilerSC/hubspotsync.git
cd hubspotsync
```

### 2. Configurar ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar credenciales
```bash
cp .env.example .env
# Editar .env con tus credenciales de HubSpot y SQL Server
```

### 5. Ejecutar sincronización
```bash
python main.py
```

## ⚙️ Configuración

### Variables de Entorno Requeridas

```env
# HubSpot API
HUBSPOT_TOKEN=tu_token_de_hubspot_aqui

# SQL Server
SQL_SERVER=tu_servidor_sql.ejemplo.com
SQL_DATABASE=nombre_de_tu_base_de_datos
SQL_USER=tu_usuario_sql
SQL_PASSWORD=tu_contraseña_sql
```

### Requisitos del Sistema

- **Python**: 3.9 o superior
- **SQL Server**: 2016 o superior con ODBC Driver 17
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB)
- **Espacio en disco**: 500MB libres

## 📁 Estructura del Proyecto

```
hubspotsync/
├── main.py                     # Script principal
├── requirements.txt            # Dependencias
├── .env.example               # Plantilla de configuración
├── hubspot/                   # Módulos de extracción
│   ├── fetch_deals.py        # Sincronización de deals
│   ├── fetch_tickets.py      # Sincronización de tickets
│   ├── fetch_contacts.py     # Sincronización de contactos
│   ├── fetch_owners.py       # Sincronización de owners
│   └── fetch_*_pipelines.py  # Sincronización de pipelines
├── HUBSPOT_SYNC_PYTHON_PACKAGE/  # Paquete para Windows
└── docs/                      # Documentación técnica
```

## 🛠️ Uso Avanzado

### Para Windows Server
Utiliza el paquete completo en `HUBSPOT_SYNC_PYTHON_PACKAGE/` con scripts de instalación automatizados.

### Programación Automática
```bash
# Ejecutar cada hora
0 * * * * /path/to/.venv/bin/python /path/to/main.py

# Ejecutar diariamente a las 6 AM
0 6 * * * /path/to/.venv/bin/python /path/to/main.py
```

## 📊 Tablas SQL Generadas

| Tabla | Descripción |
|-------|-------------|
| `hb_deals` | Datos completos de deals |
| `hb_tickets` | Datos completos de tickets |
| `hb_contacts` | Datos completos de contactos |
| `hb_owners` | Información de owners |
| `hb_deals_pipeline` | Estructura de pipelines de deals |
| `hb_tickets_pipeline` | Estructura de pipelines de tickets |

## 🔧 Solución de Problemas

### Error de Conexión SQL Server
- Verificar ODBC Driver 17 instalado
- Confirmar credenciales y permisos
- Validar conectividad de red

### Error de Token HubSpot
- Verificar token válido en HubSpot Settings
- Confirmar permisos de API necesarios
- Revisar límites de rate limiting

## 👨‍💻 Autor

**Ing. Jose Ríler Solórzano Campos**
- 🏢 Especialista en Integración de Sistemas CRM
- 📧 Contacto: [Información disponible en el código fuente]
- 📅 Proyecto iniciado: Julio 2025

## 📄 Licencia

© 2025 Jose Ríler Solórzano Campos. Todos los derechos reservados.  
**Uso exclusivo del autor. Prohibida la distribución sin autorización.**

---

⭐ **¿Te gusta este proyecto?** ¡Dale una estrella en GitHub!
