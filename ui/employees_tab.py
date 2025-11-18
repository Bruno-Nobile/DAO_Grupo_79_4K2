#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de interfaz para la gestión de empleados
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import sys
import os

# Agregar directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection
from validations import validar_dni, validar_telefono, validar_email


class EmpleadosTab(ttk.Frame):
    """Tab para gestión de empleados"""
    
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

        cols = ("id", "nombre", "apellido", "dni", "cargo", "telefono", "email")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=110)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def populate(self):
        """Carga los empleados en la tabla"""
        for r in self.tree.get_children():
            self.tree.delete(r)
        
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM empleado ORDER BY apellido, nombre")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=(
                row["id_empleado"],
                row["nombre"],
                row["apellido"],
                row["dni"],
                row["cargo"],
                row["telefono"],
                row["email"]
            ))
        conn.close()

    def nuevo(self):
        """Abre diálogo para nuevo empleado"""
        DatosEmpleadoDialog(self, "Nuevo Empleado", on_save=self.populate)

    def editar(self):
        """Abre diálogo para editar empleado"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un empleado")
            return
        
        item = self.tree.item(sel[0])["values"]
        ide = item[0]
        DatosEmpleadoDialog(self, "Editar Empleado", id_empleado=ide, on_save=self.populate)

    def eliminar(self):
        """Elimina el empleado seleccionado"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un empleado")
            return
        
        item = self.tree.item(sel[0])["values"]
        ide = item[0]
        
        if messagebox.askyesno("Confirmar", "¿Eliminar empleado seleccionado?"):
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute("DELETE FROM empleado WHERE id_empleado = ?", (ide,))
                conn.commit()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se puede eliminar: {e}")
            conn.close()
            self.populate()


class DatosEmpleadoDialog(simpledialog.Dialog):
    """Diálogo para ingresar/editar datos de empleado"""
    
    def __init__(self, parent, title, id_empleado=None, on_save=None):
        self.id_empleado = id_empleado
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
        
        ttk.Label(frame, text="Cargo:").grid(row=3, column=0, sticky=tk.W)
        self.cargo = ttk.Entry(frame)
        self.cargo.grid(row=3, column=1)
        
        ttk.Label(frame, text="Teléfono:").grid(row=4, column=0, sticky=tk.W)
        self.telefono = ttk.Entry(frame)
        self.telefono.grid(row=4, column=1)
        
        ttk.Label(frame, text="Email:").grid(row=5, column=0, sticky=tk.W)
        self.email = ttk.Entry(frame)
        self.email.grid(row=5, column=1)

        if self.id_empleado:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM empleado WHERE id_empleado = ?", (self.id_empleado,))
            row = c.fetchone()
            conn.close()
            
            if row:
                self.nombre.insert(0, row["nombre"])
                self.apellido.insert(0, row["apellido"])
                self.dni.insert(0, row["dni"])
                self.cargo.insert(0, row["cargo"])
                self.telefono.insert(0, row["telefono"])
                self.email.insert(0, row["email"])
        
        return self.nombre

    def validate(self):
        """Valida los datos ingresados"""
        if not self.nombre.get() or not self.apellido.get():
            messagebox.showwarning("Validación", "Nombre y apellido son requeridos")
            return False
        
        # Validar DNI
        dni = self.dni.get().strip()
        if dni and not validar_dni(dni):
            messagebox.showerror("Validación", "El DNI debe tener exactamente 8 dígitos numéricos")
            return False
        
        # Validar teléfono
        telefono = self.telefono.get().strip()
        if telefono and not validar_telefono(telefono):
            messagebox.showerror("Validación", "El teléfono debe contener solo dígitos numéricos")
            return False
        
        # Validar email
        email = self.email.get().strip()
        if email and not validar_email(email):
            messagebox.showerror("Validación", "El email debe tener el formato x@x.com")
            return False
        
        return True

    def apply(self):
        """Guarda los datos en la base de datos"""
        conn = get_connection()
        c = conn.cursor()
        
        # Limpiar y normalizar datos
        dni = self.dni.get().strip()
        telefono = self.telefono.get().strip()
        email = self.email.get().strip()
        
        if self.id_empleado:
            try:
                c.execute(
                    """UPDATE empleado SET nombre=?, apellido=?, dni=?, cargo=?, telefono=?, 
                       email=? WHERE id_empleado=?""",
                    (self.nombre.get(), self.apellido.get(), dni,
                     self.cargo.get(), telefono, email, self.id_empleado)
                )
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        else:
            try:
                c.execute(
                    """INSERT INTO empleado (nombre, apellido, dni, cargo, telefono, email) 
                       VALUES (?,?,?,?,?,?)""",
                    (self.nombre.get(), self.apellido.get(), dni,
                     self.cargo.get(), telefono, email)
                )
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo insertar: {e}")
        
        conn.commit()
        conn.close()
        
        if self.on_save:
            self.on_save()
