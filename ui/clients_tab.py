#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de interfaz para la gestión de clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import sys
import os

# Agregar directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection


class ClientesTab(ttk.Frame):
    """Tab para gestión de clientes"""
    
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

        # Treeview
        cols = ("id", "nombre", "apellido", "dni", "telefono", "direccion", "email")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def populate(self):
        """Carga los clientes en la tabla"""
        for r in self.tree.get_children():
            self.tree.delete(r)
        
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM cliente ORDER BY apellido, nombre")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=(
                row["id_cliente"],
                row["nombre"],
                row["apellido"],
                row["dni"],
                row["telefono"],
                row["direccion"],
                row["email"]
            ))
        conn.close()

    def nuevo(self):
        """Abre diálogo para nuevo cliente"""
        DatosClienteDialog(self, "Nuevo Cliente", on_save=self.populate)

    def editar(self):
        """Abre diálogo para editar cliente"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un cliente")
            return
        
        item = self.tree.item(sel[0])["values"]
        idc = item[0]
        DatosClienteDialog(self, "Editar Cliente", id_cliente=idc, on_save=self.populate)

    def eliminar(self):
        """Elimina el cliente seleccionado"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un cliente")
            return
        
        item = self.tree.item(sel[0])["values"]
        idc = item[0]
        
        if messagebox.askyesno("Confirmar", "¿Eliminar cliente seleccionado?"):
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute("DELETE FROM cliente WHERE id_cliente = ?", (idc,))
                conn.commit()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se puede eliminar: {e}")
            conn.close()
            self.populate()


class DatosClienteDialog(simpledialog.Dialog):
    """Diálogo para ingresar/editar datos de cliente"""
    
    def __init__(self, parent, title, id_cliente=None, on_save=None):
        self.id_cliente = id_cliente
        self.on_save = on_save
        super().__init__(parent, title)

    def body(self, frame):
        """Construye el formulario"""
        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W)
        self.nombre = ttk.Entry(frame)
        self.nombre.grid(row=0, column=1)
        
        ttk.Label(frame, text="Apellido:").grid(row=1, column=0, sticky=tk.W)
        self.apellido = ttk.Entry(frame)
        self.apellido.grid(row=1, column=1)
        
        ttk.Label(frame, text="DNI:").grid(row=2, column=0, sticky=tk.W)
        self.dni = ttk.Entry(frame)
        self.dni.grid(row=2, column=1)
        
        ttk.Label(frame, text="Teléfono:").grid(row=3, column=0, sticky=tk.W)
        self.telefono = ttk.Entry(frame)
        self.telefono.grid(row=3, column=1)
        
        ttk.Label(frame, text="Dirección:").grid(row=4, column=0, sticky=tk.W)
        self.direccion = ttk.Entry(frame)
        self.direccion.grid(row=4, column=1)
        
        ttk.Label(frame, text="Email:").grid(row=5, column=0, sticky=tk.W)
        self.email = ttk.Entry(frame)
        self.email.grid(row=5, column=1)

        if self.id_cliente:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM cliente WHERE id_cliente = ?", (self.id_cliente,))
            row = c.fetchone()
            conn.close()
            
            if row:
                self.nombre.insert(0, row["nombre"])
                self.apellido.insert(0, row["apellido"])
                self.dni.insert(0, row["dni"])
                self.telefono.insert(0, row["telefono"])
                self.direccion.insert(0, row["direccion"])
                self.email.insert(0, row["email"])

        return self.nombre

    def validate(self):
        """Valida los datos ingresados"""
        if not self.nombre.get() or not self.apellido.get():
            messagebox.showwarning("Validación", "Nombre y apellido son requeridos")
            return False
        return True

    def apply(self):
        """Guarda los datos en la base de datos"""
        conn = get_connection()
        c = conn.cursor()
        
        if self.id_cliente:
            try:
                c.execute(
                    """UPDATE cliente SET nombre=?, apellido=?, dni=?, telefono=?, direccion=?, email=? 
                       WHERE id_cliente=?""",
                    (self.nombre.get(), self.apellido.get(), self.dni.get(),
                     self.telefono.get(), self.direccion.get(), self.email.get(), self.id_cliente)
                )
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        else:
            try:
                c.execute(
                    """INSERT INTO cliente (nombre, apellido, dni, telefono, direccion, email) 
                       VALUES (?,?,?,?,?,?)""",
                    (self.nombre.get(), self.apellido.get(), self.dni.get(),
                     self.telefono.get(), self.direccion.get(), self.email.get())
                )
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo insertar: {e}")
        
        conn.commit()
        conn.close()
        
        if self.on_save:
            self.on_save()
