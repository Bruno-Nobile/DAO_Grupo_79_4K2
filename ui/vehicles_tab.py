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
from validations import validar_patente, validar_fecha_mantenimiento
from .ui_utils import enable_treeview_sorting


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
        self.tree = ttk.Treeview(self, columns=cols, show="headings", style="Colored.Treeview")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=110)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        enable_treeview_sorting(self.tree)

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
        
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("SELECT COUNT(*) AS total FROM alquiler WHERE id_vehiculo = ?", (idv,))
            alquileres = c.fetchone()["total"]
            c.execute("SELECT COUNT(*) AS total FROM mantenimiento WHERE id_vehiculo = ?", (idv,))
            mantenimientos = c.fetchone()["total"]
        except Exception:
            alquileres = 0
            mantenimientos = 0

        mensaje = "¿Eliminar vehículo seleccionado?"
        if alquileres:
            mensaje += f"\nSe eliminarán {alquileres} alquiler(es) vinculados."
        if mantenimientos:
            mensaje += f"\nSe eliminarán {mantenimientos} mantenimiento(s) registrados."

        if not messagebox.askyesno("Confirmar", mensaje):
            conn.close()
            return

        try:
            if alquileres:
                c.execute("DELETE FROM alquiler WHERE id_vehiculo = ?", (idv,))
            if mantenimientos:
                c.execute("DELETE FROM mantenimiento WHERE id_vehiculo = ?", (idv,))
            c.execute("DELETE FROM vehiculo WHERE id_vehiculo = ?", (idv,))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            messagebox.showerror("Error", f"No se puede eliminar: {e}")
        finally:
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
        # Validar patente
        patente = self.entries["Patente:"].get().strip()
        if not patente:
            messagebox.showwarning("Validación", "Patente requerida")
            return False
        
        if not validar_patente(patente):
            messagebox.showerror("Validación", "La patente debe seguir el formato ABC-123 o AB-123-CD")
            return False
        
        # Validar fecha de mantenimiento
        fecha_mant = self.entries["Fecha último mant (YYYY-MM-DD):"].get().strip()
        if fecha_mant and not validar_fecha_mantenimiento(fecha_mant):
            messagebox.showerror("Validación", "La fecha de último mantenimiento no puede ser mayor a la fecha actual")
            return False
        
        # Validar costo diario
        try:
            float(self.entries["Costo diario:"].get())
        except Exception:
            messagebox.showwarning("Validación", "Costo diario inválido")
            return False
        
        return True

    def apply(self):
        """Guarda los datos en la base de datos"""
        values = {k: v.get().strip() for k, v in self.entries.items()}
        
        # Normalizar patente a mayúsculas
        patente = values["Patente:"].upper()
        fecha_mant = values["Fecha último mant (YYYY-MM-DD):"] or None
        
        conn = get_connection()
        c = conn.cursor()
        
        if self.id_vehiculo:
            try:
                c.execute(
                    """UPDATE vehiculo SET patente=?, marca=?, modelo=?, tipo=?, 
                       costo_diario=?, estado=?, fecha_ultimo_mantenimiento=? 
                       WHERE id_vehiculo=?""",
                    (patente, values["Marca:"], values["Modelo:"],
                     values["Tipo:"], float(values["Costo diario:"]), values["Estado:"],
                     fecha_mant, self.id_vehiculo)
                )
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        else:
            try:
                c.execute(
                    """INSERT INTO vehiculo (patente, marca, modelo, tipo, costo_diario, 
                       estado, fecha_ultimo_mantenimiento) VALUES (?,?,?,?,?,?,?)""",
                    (patente, values["Marca:"], values["Modelo:"],
                     values["Tipo:"], float(values["Costo diario:"]), values["Estado:"],
                     fecha_mant)
                )
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo insertar: {e}")
        
        conn.commit()
        conn.close()
        
        if self.on_save:
            self.on_save()
