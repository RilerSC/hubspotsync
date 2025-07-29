#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script temporal para agregar encabezados profesionales a todos los archivos del proyecto
"""

import os
from pathlib import Path

def get_header(filename, description, functionality):
    """Genera el encabezado estándar para los archivos"""
    return f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                            {description}
================================================================================

Archivo:            {filename}
Descripción:        {functionality}

Dependencias:
    - HubSpot API v3
    - Variables de entorno: HUBSPOT_TOKEN
    - Librerías: requests, dotenv, os, pathlib

Autor:              Ing. Jose Ríler Solórzano Campos
Fecha de Creación:  11 de julio de 2025
Derechos de Autor:  © 2025 Jose Ríler Solórzano Campos. Todos los derechos reservados.
Licencia:           Uso exclusivo del autor. Prohibida la distribución sin autorización.

================================================================================
"""
'''

# Definición de archivos y sus descripciones
files_info = {
    "hubspot/fetch_contacts.py": {
        "title": "HUBSPOT CONTACTS - EXTRACTOR DE CONTACTOS",
        "description": """Módulo especializado para la extracción y procesamiento de
                   contactos desde la API de HubSpot. Incluye análisis dinámico
                   de propiedades, extracción por lotes optimizada y manejo
                   robusto de grandes volúmenes de datos de contactos."""
    },
    
    "hubspot/fetch_tickets.py": {
        "title": "HUBSPOT TICKETS - EXTRACTOR DE TICKETS DE SOPORTE",
        "description": """Módulo especializado para la extracción y procesamiento de
                   tickets de soporte desde la API de HubSpot. Maneja propiedades
                   específicas de tickets, transformaciones de timestamps y
                   análisis estadístico de estados y categorías."""
    },
    
    "hubspot/fetch_owners.py": {
        "title": "HUBSPOT OWNERS - EXTRACTOR DE PROPIETARIOS",
        "description": """Módulo para la extracción de información de owners (propietarios)
                   desde HubSpot API. Procesa datos de usuarios, equipos y estados
                   de actividad, formateando la información como tabla estructurada."""
    },
    
    "hubspot/fetch_deals_pipelines.py": {
        "title": "HUBSPOT DEALS PIPELINES - EXTRACTOR DE ETAPAS DE VENTAS",
        "description": """Módulo para extraer la estructura de pipelines y stages de deals
                   desde HubSpot API. Procesa información de etapas de ventas,
                   probabilidades y configuraciones de pipeline."""
    },
    
    "hubspot/fetch_tickets_pipelines.py": {
        "title": "HUBSPOT TICKETS PIPELINES - EXTRACTOR DE ETAPAS DE SOPORTE",
        "description": """Módulo para extraer la estructura de pipelines y stages de tickets
                   desde HubSpot API. Procesa información de etapas de soporte,
                   estados de resolución y flujos de trabajo."""
    }
}

print("🚀 Agregando encabezados profesionales a archivos del proyecto...")

project_root = Path("/Users/joserilersolorzano/Library/Mobile Documents/com~apple~CloudDocs/PROYECTOS PYTHON/HUBSPOT_SYNC")

for file_path, info in files_info.items():
    full_path = project_root / file_path
    
    if full_path.exists():
        print(f"📝 Procesando {file_path}...")
        
        # Leer contenido actual
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar donde empiezan los imports reales (después de comentarios iniciales)
        lines = content.split('\n')
        start_index = 0
        
        # Encontrar la primera línea que sea un import real
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from ') and not line.startswith('#'):
                start_index = i
                break
        
        # Crear nuevo contenido con header
        header = get_header(file_path, info["title"], info["description"])
        
        # Unir header con el contenido desde los imports
        new_content = header + '\n' + '\n'.join(lines[start_index:])
        
        # Escribir archivo actualizado
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {file_path} actualizado")
    else:
        print(f"⚠️ {file_path} no encontrado")

print("🎉 ¡Encabezados agregados exitosamente!")
