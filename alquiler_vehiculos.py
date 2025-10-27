#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Alquiler de Vehículos - Archivo principal
================================================================

ESTE ARCHIVO HA SIDO MODULARIZADO

La aplicación ahora está dividida en los siguientes módulos:

Estructura del Proyecto:
├── config.py                    # Configuración y constantes
├── database.py                  # Funciones de base de datos
├── models.py                    # Lógica de negocio
├── main.py                      # Punto de entrada de la aplicación
├── ui/
│   ├── __init__.py             # Inicialización del paquete UI
│   ├── main_window.py          # Ventana principal (App class)
│   ├── clients_tab.py          # Gestión de clientes
│   ├── vehicles_tab.py          # Gestión de vehículos
│   ├── employees_tab.py        # Gestión de empleados
│   ├── rentals_tab.py          # Gestión de alquileres
│   └── reports_tab.py          # Reportes y análisis
└── alquiler_vehiculos_backup.py # Backup del archivo original

PARA EJECUTAR LA APLICACIÓN:
    python main.py

O usando el módulo directamente:
    python -m main

La base de datos se crea automáticamente en: alquiler_vehiculos.db
Los datos de ejemplo se insertan automáticamente si la BD está vacía.

===============================================================
"""

# Redirigir a main.py para mantener compatibilidad
if __name__ == "__main__":
    import main
    main.main()