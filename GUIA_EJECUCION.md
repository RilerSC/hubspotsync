# 📋 GUÍA DE EJECUCIÓN RÁPIDA - HUBSPOT SYNC

## ⚡ ARCHIVOS PRINCIPALES DE EJECUCIÓN

### 🚨 **IMPORTANTE PARA TODOS LOS EQUIPOS**

Este proyecto tiene **DOS PROCESOS PRINCIPALES** claramente separados:

---

## 📥 **LECTURA**: HubSpot → SQL Server
**ARCHIVO**: `main.py`
**COMANDO**: `python main.py`
**PROPÓSITO**: Sincronizar datos desde HubSpot hacia SQL Server

---

## 📤 **ESCRITURA**: SQL Server → HubSpot  
**ARCHIVO**: `escritura/run_full_sync.py`
**COMANDO**: `python escritura/run_full_sync.py`
**PROPÓSITO**: Enviar contactos desde SQL Server hacia HubSpot

### 🎯 **PARA ESCRITURA - USAR SOLO**:
```bash
cd escritura
python run_full_sync.py
```

### ❌ **NO EJECUTAR DIRECTAMENTE** (ya están incluidos en run_full_sync.py):
- `escritura/production_insert_full.py`
- `escritura/production_update.py`

---

## 🔄 **FLUJO COMPLETO DE TRABAJO**

1. **Lectura**: `python main.py` (HubSpot → SQL Server)
2. **Escritura**: `python escritura/run_full_sync.py` (SQL Server → HubSpot)

---

## 💡 **PARA NUEVOS DESARROLLADORES**

- **✅ main.py**: Para traer datos DE HubSpot
- **✅ escritura/run_full_sync.py**: Para enviar datos A HubSpot
- **📁 Ubicación**: Directorio raíz del proyecto
- **🐍 Python**: Requiere Python 3.9+ con ambiente virtual

---

## 🚨 **RECORDATORIO**
Si trabajas en un equipo nuevo o servidor diferente:
1. Configura el ambiente virtual: `python -m venv venv`
2. Activa: `source venv/bin/activate` (Linux/Mac) o `venv\Scripts\activate` (Windows)
3. Instala dependencias: `pip install -r requirements.txt`
4. Configura archivo `.env` con credenciales
5. Ejecuta procesos con los comandos indicados arriba
