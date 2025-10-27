#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuración del sistema de alquiler de vehículos
"""

# Configuración de base de datos
DB_FILE = "alquiler_vehiculos.db"

# Verificar disponibilidad de matplotlib
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False
