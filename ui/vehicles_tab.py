#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de interfaz para la gestión de vehículos
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import sys
import os

# Agregar directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class VehiculosTab(ttk.Frame):
    """Tab para gestión de vehículos"""
    
    def __init__(self, container):
        super().__init__(container)
        self.build_ui()
        self.populate()

    def build_ui(self):
        """Construye la interfaz de usuario"""
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(top, text="Nuevo", command=self.nuevo).pack(side=tk.LEFT)
        ttk.Button(top, text="Editar", command=self.editar).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Eliminar", command=self.eliminar).pack(side=tk.LEFT)
        ttk.Button(top, text="Refrescar", command=self.populate).pack(side=tk.RIGHT)

        cols = ("id", "patente", "marca", "modelo", "tipo", "costo_diario", "estado", "fecha_mant")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=110)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def populate(self):
        """Carga los vehículos en la tabla"""
        for r in self.tree.get_children():
            self.tree.delete(r)
        
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM vehiculo ORDER BY marca, modelo")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=(
                row["id_vehiculo"],
                row["patente"],
                row["marca"],
                row["modelo"],
                row["tipo"],
                row["costo_diario"],
                row["estado"],
                row["fecha_ultimo_mantenimiento"]
            ))
        conn.close()

    def nuevo(self):
        """Abre diálogo para nuevo vehículo"""
        DatosVehiculoDialog(self, "Nuevo Vehículo", on_save=self.populate)

    def editar(self):
        """Abre diálogo para editar vehículo"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un vehículo")
            return
        
        item = self.tree.item(sel[0])["values"]
        idv = item[0]
        DatosVehiculoDialog(self, "Editar Vehículo", id_vehiculo=idv, on_save=self.populate)

    def eliminar(self):
        """Elimina el vehículo seleccionado"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un vehículo")
            return
        
        item = self.tree.item(sel[0])["values"]
        idv = item[0]
        
        if messagebox.askyesno("Confirmar", "¿Eliminar vehículo seleccionado?"):
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute("DELETE FROM vehiculo WHERE id_vehiculo = ?", (idv,))
                conn.commit()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se puede eliminar: {e}")
            conn.close()
            self.populate()


class DatosVehiculoDialog(simpledialog.Dialog):
    """Diálogo para ingresar/editar datos de vehículo"""
    
    def __init__(self, parent, title, id_vehiculo=None, on_save=None):
        self.id_vehiculo = id_vehiculo
        self.on_save = on_save
        super().__init__(parent, title)

    def body(self, frame):
        """Construye el formulario"""
        labels = [
            "Patente:", "Marca:", "Modelo:", "Tipo:", "Costo diario:",
            "Estado:", "Fecha último mant (YYYY-MM-DD):"
        ]
        self.entries = {}
        
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W)
            e = ttk.Entry(frame)
            e.grid(row=i, column=1)
            self.entries[label] = e

        if self.id_vehiculo:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM vehiculo WHERE id_vehiculo = ?", (self.id_vehiculo,))
            row = c.fetchone()
            conn.close()
            
            if row:
                self.entries["Patente:"].insert(0, row["patente"])
                self.entries["Marca:"].insert(0, row["marca"])
                self.entries["Modelo:"].insert(0, row["modelo"])
                self.entries["Tipo:"].insert(0, row["tipo"])
                self.entries["Costo diario:"].insert(0, str(row["costo_diario"]))
                self.entries["Estado:"].insert(0, row["estado"])
                if row["fecha_ultimo_mantenimiento"]:
                    self.entries["Fecha último mant (YYYY-MM-DD):"].insert(0, row["fecha_ultimo_mantenimiento"])
        
        return self.entries["Patente:"]

    def validate(self):
        """Valida los datos ingresados"""
        if not self.entries["Patente:"].get():
            messagebox.showwarning("Validación", "Patente requerida")
            return False
        try:
            float(self.entries["Costo diario:"].get())
        except Exception:
            messagebox.showwarning("Validación", "Costo diario inválido")
            return False
        return True

    def apply(self):
        """Guarda los datos en la base de datos"""
        values = {k: v.get() for k, v in self.entries.items()}
        conn = get_connection()
        c = conn.cursor()
        
        if self.id_vehiculo:
            try:
                c.execute(
                    """UPDATE vehiculo SET patente=?, marca=?, modelo=?, tipo=?, 
                       costo_diario=?, estado=?, fecha_ultimo_mantenimiento=? 
                       WHERE id_vehiculo=?""",
                    (values["Patente:"], values["Marca:"], values["Modelo:"],
                     values["Tipo:"], float(values["Costo diario:"]), values["Estado:"],
                     values["Fecha último mant (YYYY-MM-DD):"] or None, self.id_vehiculo)
                )
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        else:
            try:
                c.execute(
                    """INSERT INTO vehiculo (patente, marca, modelo, tipo, costo_diario, 
                       estado, fecha_ultimo_mantenimiento) VALUES (?,?,?,?,?,?,?)""",
                    (values["Patente:"], values["Marca:"], values["Modelo:"],
                     values["Tipo:"], float(values["Costo diario:"]), values["Estado:"],
                     values["Fecha último mant (YYYY-MM-DD):"] or None)
                )
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo insertar: {e}")
        
        conn.commit()
        conn.close()
        
        if self.on_save:
            self.on_save()
