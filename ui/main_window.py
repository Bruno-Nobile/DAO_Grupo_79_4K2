#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de la ventana principal de la aplicación
"""

import tkinter as tk
from tkinter import ttk
from .management_tab import GestionTab
from .rentals_tab import AlquileresTab
from .reports_tab import ReportesTab


class App(tk.Tk):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.title("Gestion de alquileres")
        self.geometry("1000x600")
        self.configure(bg="#f4f6fb")
        self.configure_styles()
        self.create_widgets()

    def configure_styles(self):
        """Define estilos personalizados para la interfaz"""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Encabezado
        style.configure(
            "Header.TFrame",
            background="#0d47a1"
        )
        style.configure(
            "Header.TLabel",
            background="#0d47a1",
            foreground="white",
            font=("Segoe UI", 16, "bold")
        )

        # Notebook sobre fondo claro
        style.configure("TNotebook", background="#f4f6fb", borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            padding=(8, 4),
            background="#c5cae9",
            foreground="#1a237e"
        )
        style.map(
            "TNotebook.Tab",
            padding=[("selected", (14, 6))],
            background=[("selected", "#fdfbff")],
            foreground=[("selected", "#0d47a1")]
        )

        # Treeview personalizado
        style.configure(
            "Colored.Treeview",
            background="white",
            fieldbackground="white",
            bordercolor="#c5cae9",
            rowheight=24
        )
        style.configure(
            "Colored.Treeview.Heading",
            background="#dbe2ff",
            foreground="#1a237e",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=(4, 6)
        )
        style.map(
            "Colored.Treeview.Heading",
            background=[("active", "#c0ccff")]
        )

    def create_widgets(self):
        """Crea los widgets principales (notebook con pestañas)"""
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill=tk.X)
        ttk.Label(header, text="Sistema de Alquiler de Vehículos", style="Header.TLabel").pack(
            anchor=tk.W, padx=20, pady=12
        )

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

        # Pestañas
        self.tab_gestion = GestionTab(nb)
        self.tab_alquileres = AlquileresTab(nb)
        self.tab_reportes = ReportesTab(nb)

        nb.add(self.tab_gestion, text="Gestión")
        nb.add(self.tab_alquileres, text="Alquileres")
        nb.add(self.tab_reportes, text="Reportes")
