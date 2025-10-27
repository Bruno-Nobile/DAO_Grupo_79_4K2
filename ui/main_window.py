#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de la ventana principal de la aplicación
"""

import tkinter as tk
from tkinter import ttk
from .clients_tab import ClientesTab
from .vehicles_tab import VehiculosTab
from .employees_tab import EmpleadosTab
from .rentals_tab import AlquileresTab
from .reports_tab import ReportesTab


class App(tk.Tk):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.title("Sistema de Alquiler de Vehículos - TP")
        self.geometry("1000x600")
        self.create_widgets()

    def create_widgets(self):
        """Crea los widgets principales (notebook con pestañas)"""
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

        # Pestañas
        self.tab_clientes = ClientesTab(nb)
        self.tab_vehiculos = VehiculosTab(nb)
        self.tab_empleados = EmpleadosTab(nb)
        self.tab_alquileres = AlquileresTab(nb)
        self.tab_reportes = ReportesTab(nb)

        nb.add(self.tab_clientes, text="Clientes")
        nb.add(self.tab_vehiculos, text="Vehículos")
        nb.add(self.tab_empleados, text="Empleados")
        nb.add(self.tab_alquileres, text="Alquileres")
        nb.add(self.tab_reportes, text="Reportes")
