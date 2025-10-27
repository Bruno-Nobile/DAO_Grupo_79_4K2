#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Alquiler de Vehículos - Aplicación simple con Tkinter + SQLite
Funcionalidades:
- ABM Clientes
- ABM Vehículos
- ABM Empleados
- Registro de Alquileres (valida disponibilidad)
- Registro de Mantenimientos
- Registro de Multas/Daños
- Reportes: listado de alquileres, vehículos más alquilados, facturación mensual (gráfico)
"""

from database import init_db, seed_sample_data
from ui.main_window import App


def main():
    """Función principal que inicializa la base de datos y la aplicación"""
    init_db()
    seed_sample_data()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
