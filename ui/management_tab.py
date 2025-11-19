#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pestaña agrupada para la gestión de clientes, vehículos y empleados.
"""

import tkinter as tk
from tkinter import ttk

from .clients_tab import ClientesTab
from .vehicles_tab import VehiculosTab
from .employees_tab import EmpleadosTab


class GestionTab(ttk.Frame):
    """
    Tab contenedor que agrupa los ABM de clientes, vehículos y empleados.
    Utiliza un Notebook interno para mantener cada sección organizada
    dentro de una única pestaña principal.
    """

    def __init__(self, container):
        super().__init__(container)
        self._build_ui()

    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

        self.tab_clientes = ClientesTab(nb)
        self.tab_vehiculos = VehiculosTab(nb)
        self.tab_empleados = EmpleadosTab(nb)

        nb.add(self.tab_clientes, text="Clientes")
        nb.add(self.tab_vehiculos, text="Vehículos")
        nb.add(self.tab_empleados, text="Empleados")

