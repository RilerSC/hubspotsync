#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                           HUBSPOT MODULE - PAQUETE PRINCIPAL
================================================================================

Archivo:            hubspot/__init__.py
Descripción:        Módulo principal del paquete HubSpot que agrupa todos los
                   extractores especializados para diferentes entidades de
                   HubSpot (deals, tickets, contacts, owners, pipelines).

Estructura del Módulo:
    - fetch_deals.py: Extracción de deals/negocios
    - fetch_tickets.py: Extracción de tickets de soporte
    - fetch_contacts.py: Extracción de contactos
    - fetch_owners.py: Extracción de propietarios/usuarios
    - fetch_deals_pipelines.py: Extracción de etapas de ventas
    - fetch_tickets_pipelines.py: Extracción de etapas de soporte

Funcionalidades Comunes:
    - Análisis dinámico de propiedades
    - Extracción por lotes optimizada
    - Manejo robusto de errores
    - Resúmenes estadísticos detallados
    - Deduplicación automática

Dependencias Globales:
    - HubSpot API v3
    - Token de autenticación en .env
    - Librerías: requests, dotenv, os, pathlib

Autor:              Ing. Jose Ríler Solórzano Campos
Fecha de Creación:  11 de julio de 2025
Derechos de Autor:  © 2025 Jose Ríler Solórzano Campos. Todos los derechos reservados.
Licencia:           Uso exclusivo del autor. Prohibida la distribución sin autorización.

================================================================================
"""

# ==================== MÓDULO HUBSPOT PACKAGE ====================
# Este archivo inicializa el paquete hubspot como módulo de Python.
# Permite importar funciones desde main.py usando:
# from hubspot.fetch_deals import fetch_deals_from_hubspot
#
# El módulo está diseñado como un conjunto de extractores especializados
# que trabajan de manera independiente pero coordinada para obtener
# todos los datos necesarios desde la API de HubSpot.