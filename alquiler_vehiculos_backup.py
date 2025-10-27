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
Autor: Generado por ChatGPT (ejemplo para TP)
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import os
import sys

# intentar importar matplotlib (opcional)
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

DB_FILE = "alquiler_vehiculos.db"


# ---------------------------
# Base de datos: creación y helpers
# ---------------------------

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Tablas
    c.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS cliente (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        dni TEXT UNIQUE,
        telefono TEXT,
        direccion TEXT,
        email TEXT
    );

    CREATE TABLE IF NOT EXISTS empleado (
        id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        dni TEXT UNIQUE,
        cargo TEXT,
        telefono TEXT,
        email TEXT
    );

    CREATE TABLE IF NOT EXISTS vehiculo (
        id_vehiculo INTEGER PRIMARY KEY AUTOINCREMENT,
        patente TEXT UNIQUE NOT NULL,
        marca TEXT,
        modelo TEXT,
        tipo TEXT,
        costo_diario REAL NOT NULL DEFAULT 0,
        estado TEXT DEFAULT 'disponible', -- disponible/inactivo/en_mantenimiento
        fecha_ultimo_mantenimiento TEXT
    );

    CREATE TABLE IF NOT EXISTS alquiler (
        id_alquiler INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        costo_total REAL NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_vehiculo INTEGER NOT NULL,
        id_empleado INTEGER,
        fecha_registro TEXT NOT NULL DEFAULT (date('now')),
        FOREIGN KEY(id_cliente) REFERENCES cliente(id_cliente) ON DELETE RESTRICT,
        FOREIGN KEY(id_vehiculo) REFERENCES vehiculo(id_vehiculo) ON DELETE RESTRICT,
        FOREIGN KEY(id_empleado) REFERENCES empleado(id_empleado) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS multa (
        id_multa INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT,
        monto REAL,
        id_alquiler INTEGER NOT NULL,
        FOREIGN KEY(id_alquiler) REFERENCES alquiler(id_alquiler) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS mantenimiento (
        id_mant INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        fecha TEXT NOT NULL,
        costo REAL,
        id_vehiculo INTEGER NOT NULL,
        observaciones TEXT,
        FOREIGN KEY(id_vehiculo) REFERENCES vehiculo(id_vehiculo) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()

def seed_sample_data():
    """Inserta algunos datos de prueba si la DB está vacía"""
    conn = get_connection()
    c = conn.cursor()
    # chequear si hay clientes
    c.execute("SELECT COUNT(*) FROM cliente")
    if c.fetchone()[0] == 0:
        clientes = [
            ("Lucas", "González", "12345678", "3415550001", "Córdoba", "lucas@example.com"),
            ("María", "Pérez", "23456789", "3415550002", "Córdoba", "maria@example.com"),
        ]
        c.executemany("INSERT INTO cliente (nombre, apellido, dni, telefono, direccion, email) VALUES (?,?,?,?,?,?)", clientes)

    c.execute("SELECT COUNT(*) FROM empleado")
    if c.fetchone()[0] == 0:
        empleados = [
            ("Admin", "Local", "99999999", "Administrador", "3415551000", "admin@example.com"),
        ]
        c.executemany("INSERT INTO empleado (nombre, apellido, dni, cargo, telefono, email) VALUES (?,?,?,?,?,?)", empleados)

    c.execute("SELECT COUNT(*) FROM vehiculo")
    if c.fetchone()[0] == 0:
        vehiculos = [
            ("ABC123", "Toyota", "Corolla", "Sedan", 5000.0, "disponible", None),
            ("DEF456", "Volkswagen", "Gol", "Hatchback", 3500.0, "disponible", None),
            ("GHI789", "Ford", "Ranger", "PickUp", 8000.0, "disponible", None),
        ]
        c.executemany("INSERT INTO vehiculo (patente, marca, modelo, tipo, costo_diario, estado, fecha_ultimo_mantenimiento) VALUES (?,?,?,?,?,?,?)", vehiculos)

    conn.commit()
    conn.close()


# ---------------------------
# Lógica de negocio
# ---------------------------

def calcular_costo(costo_diario, fecha_inicio_str, fecha_fin_str):
    """Calcula costo total basado en días (inclusive)"""
    fi = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    ff = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    dias = (ff - fi).days + 1
    if dias < 1:
        raise ValueError("La fecha de fin debe ser igual o posterior a la fecha de inicio.")
    return round(dias * costo_diario, 2)

def vehiculo_disponible(id_vehiculo, fecha_inicio_str, fecha_fin_str):
    """Verifica si el vehículo no tiene alquileres solapados en ese período"""
    conn = get_connection()
    c = conn.cursor()
    query = """
    SELECT COUNT(*) FROM alquiler
    WHERE id_vehiculo = ?
      AND NOT (date(fecha_fin) < date(?) OR date(fecha_inicio) > date(?))
    """
    # si existe un alquiler cuyo rango NO está completamente fuera del interesa => está solapado
    c.execute(query, (id_vehiculo, fecha_inicio_str, fecha_fin_str))
    cnt = c.fetchone()[0]
    conn.close()
    return cnt == 0

def registrar_alquiler(fecha_inicio, fecha_fin, id_cliente, id_vehiculo, id_empleado=None):
    conn = get_connection()
    c = conn.cursor()
    # obtener costo diario del vehículo
    c.execute("SELECT costo_diario FROM vehiculo WHERE id_vehiculo = ?", (id_vehiculo,))
    row = c.fetchone()
    if not row:
        conn.close()
        raise ValueError("Vehículo no encontrado.")
    costo_diario = row["costo_diario"]
    # disponibilidad
    if not vehiculo_disponible(id_vehiculo, fecha_inicio, fecha_fin):
        conn.close()
        raise ValueError("Vehículo no disponible en el periodo indicado.")
    costo_total = calcular_costo(costo_diario, fecha_inicio, fecha_fin)
    c.execute("""INSERT INTO alquiler (fecha_inicio, fecha_fin, costo_total, id_cliente, id_vehiculo, id_empleado)
                 VALUES (?,?,?,?,?,?)""", (fecha_inicio, fecha_fin, costo_total, id_cliente, id_vehiculo, id_empleado))
    conn.commit()
    conn.close()
    return True

# ---------------------------
# UI - Tkinter
# ---------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Alquiler de Vehículos - TP")
        self.geometry("1000x600")
        self.create_widgets()

    def create_widgets(self):
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


# ---------------------------
# Tab Clientes
# ---------------------------
class ClientesTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.build_ui()
        self.populate()

    def build_ui(self):
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
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM cliente ORDER BY apellido, nombre")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=(row["id_cliente"], row["nombre"], row["apellido"], row["dni"], row["telefono"], row["direccion"], row["email"]))
        conn.close()

    def nuevo(self):
        DatosClienteDialog(self, "Nuevo Cliente", on_save=self.populate)

    def editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un cliente")
            return
        item = self.tree.item(sel[0])["values"]
        idc = item[0]
        DatosClienteDialog(self, "Editar Cliente", id_cliente=idc, on_save=self.populate)

    def eliminar(self):
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
    def __init__(self, parent, title, id_cliente=None, on_save=None):
        self.id_cliente = id_cliente
        self.on_save = on_save
        super().__init__(parent, title)

    def body(self, frame):
        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W)
        self.nombre = ttk.Entry(frame); self.nombre.grid(row=0, column=1)
        ttk.Label(frame, text="Apellido:").grid(row=1, column=0, sticky=tk.W)
        self.apellido = ttk.Entry(frame); self.apellido.grid(row=1, column=1)
        ttk.Label(frame, text="DNI:").grid(row=2, column=0, sticky=tk.W)
        self.dni = ttk.Entry(frame); self.dni.grid(row=2, column=1)
        ttk.Label(frame, text="Teléfono:").grid(row=3, column=0, sticky=tk.W)
        self.telefono = ttk.Entry(frame); self.telefono.grid(row=3, column=1)
        ttk.Label(frame, text="Dirección:").grid(row=4, column=0, sticky=tk.W)
        self.direccion = ttk.Entry(frame); self.direccion.grid(row=4, column=1)
        ttk.Label(frame, text="Email:").grid(row=5, column=0, sticky=tk.W)
        self.email = ttk.Entry(frame); self.email.grid(row=5, column=1)

        if self.id_cliente:
            conn = get_connection(); c = conn.cursor()
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
        if not self.nombre.get() or not self.apellido.get():
            messagebox.showwarning("Validación", "Nombre y apellido son requeridos")
            return False
        return True

    def apply(self):
        conn = get_connection(); c = conn.cursor()
        if self.id_cliente:
            try:
                c.execute("""UPDATE cliente SET nombre=?, apellido=?, dni=?, telefono=?, direccion=?, email=? WHERE id_cliente=?""",
                          (self.nombre.get(), self.apellido.get(), self.dni.get(), self.telefono.get(), self.direccion.get(), self.email.get(), self.id_cliente))
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        else:
            try:
                c.execute("""INSERT INTO cliente (nombre, apellido, dni, telefono, direccion, email) VALUES (?,?,?,?,?,?)""",
                          (self.nombre.get(), self.apellido.get(), self.dni.get(), self.telefono.get(), self.direccion.get(), self.email.get()))
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo insertar: {e}")
        conn.commit(); conn.close()
        if self.on_save:
            self.on_save()


# ---------------------------
# Tab Vehículos
# ---------------------------
class VehiculosTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.build_ui()
        self.populate()

    def build_ui(self):
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=5, pady=5)
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
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT * FROM vehiculo ORDER BY marca, modelo")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=(row["id_vehiculo"], row["patente"], row["marca"], row["modelo"], row["tipo"], row["costo_diario"], row["estado"], row["fecha_ultimo_mantenimiento"]))
        conn.close()

    def nuevo(self):
        DatosVehiculoDialog(self, "Nuevo Vehículo", on_save=self.populate)

    def editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un vehículo")
            return
        item = self.tree.item(sel[0])["values"]
        idv = item[0]
        DatosVehiculoDialog(self, "Editar Vehículo", id_vehiculo=idv, on_save=self.populate)

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un vehículo")
            return
        item = self.tree.item(sel[0])["values"]
        idv = item[0]
        if messagebox.askyesno("Confirmar", "¿Eliminar vehículo seleccionado?"):
            conn = get_connection(); c = conn.cursor()
            try:
                c.execute("DELETE FROM vehiculo WHERE id_vehiculo = ?", (idv,))
                conn.commit()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se puede eliminar: {e}")
            conn.close()
            self.populate()


class DatosVehiculoDialog(simpledialog.Dialog):
    def __init__(self, parent, title, id_vehiculo=None, on_save=None):
        self.id_vehiculo = id_vehiculo
        self.on_save = on_save
        super().__init__(parent, title)

    def body(self, frame):
        labels = ["Patente:", "Marca:", "Modelo:", "Tipo:", "Costo diario:", "Estado:", "Fecha último mant (YYYY-MM-DD):"]
        self.entries = {}
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W)
            e = ttk.Entry(frame)
            e.grid(row=i, column=1)
            self.entries[label] = e

        if self.id_vehiculo:
            conn = get_connection(); c = conn.cursor()
            c.execute("SELECT * FROM vehiculo WHERE id_vehiculo = ?", (self.id_vehiculo,))
            row = c.fetchone(); conn.close()
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
        values = {k: v.get() for k, v in self.entries.items()}
        conn = get_connection(); c = conn.cursor()
        if self.id_vehiculo:
            try:
                c.execute("""UPDATE vehiculo SET patente=?, marca=?, modelo=?, tipo=?, costo_diario=?, estado=?, fecha_ultimo_mantenimiento=? WHERE id_vehiculo=?""",
                          (values["Patente:"], values["Marca:"], values["Modelo:"], values["Tipo:"], float(values["Costo diario:"]), values["Estado:"], values["Fecha último mant (YYYY-MM-DD):"] or None, self.id_vehiculo))
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        else:
            try:
                c.execute("""INSERT INTO vehiculo (patente, marca, modelo, tipo, costo_diario, estado, fecha_ultimo_mantenimiento) VALUES (?,?,?,?,?,?,?)""",
                          (values["Patente:"], values["Marca:"], values["Modelo:"], values["Tipo:"], float(values["Costo diario:"]), values["Estado:"], values["Fecha último mant (YYYY-MM-DD):"] or None))
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo insertar: {e}")
        conn.commit(); conn.close()
        if self.on_save:
            self.on_save()


# ---------------------------
# Tab Empleados
# ---------------------------
class EmpleadosTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.build_ui()
        self.populate()

    def build_ui(self):
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=5, pady=5)
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
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM empleado ORDER BY apellido, nombre")
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=(row["id_empleado"], row["nombre"], row["apellido"], row["dni"], row["cargo"], row["telefono"], row["email"]))
        conn.close()

    def nuevo(self):
        DatosEmpleadoDialog(self, "Nuevo Empleado", on_save=self.populate)

    def editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un empleado")
            return
        item = self.tree.item(sel[0])["values"]
        ide = item[0]
        DatosEmpleadoDialog(self, "Editar Empleado", id_empleado=ide, on_save=self.populate)

    def eliminar(self):
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
    def __init__(self, parent, title, id_empleado=None, on_save=None):
        self.id_empleado = id_empleado
        self.on_save = on_save
        super().__init__(parent, title)

    def body(self, frame):
        ttk.Label(frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W)
        self.nombre = ttk.Entry(frame); self.nombre.grid(row=0, column=1)
        ttk.Label(frame, text="Apellido:").grid(row=1, column=0, sticky=tk.W)
        self.apellido = ttk.Entry(frame); self.apellido.grid(row=1, column=1)
        ttk.Label(frame, text="DNI:").grid(row=2, column=0, sticky=tk.W)
        self.dni = ttk.Entry(frame); self.dni.grid(row=2, column=1)
        ttk.Label(frame, text="Cargo:").grid(row=3, column=0, sticky=tk.W)
        self.cargo = ttk.Entry(frame); self.cargo.grid(row=3, column=1)
        ttk.Label(frame, text="Teléfono:").grid(row=4, column=0, sticky=tk.W)
        self.telefono = ttk.Entry(frame); self.telefono.grid(row=4, column=1)
        ttk.Label(frame, text="Email:").grid(row=5, column=0, sticky=tk.W)
        self.email = ttk.Entry(frame); self.email.grid(row=5, column=1)

        if self.id_empleado:
            conn = get_connection(); c = conn.cursor()
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
        if not self.nombre.get() or not self.apellido.get():
            messagebox.showwarning("Validación", "Nombre y apellido son requeridos")
            return False
        return True

    def apply(self):
        conn = get_connection(); c = conn.cursor()
        if self.id_empleado:
            try:
                c.execute("""UPDATE empleado SET nombre=?, apellido=?, dni=?, cargo=?, telefono=?, email=? WHERE id_empleado=?""",
                          (self.nombre.get(), self.apellido.get(), self.dni.get(), self.cargo.get(), self.telefono.get(), self.email.get(), self.id_empleado))
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
        else:
            try:
                c.execute("""INSERT INTO empleado (nombre, apellido, dni, cargo, telefono, email) VALUES (?,?,?,?,?,?)""",
                          (self.nombre.get(), self.apellido.get(), self.dni.get(), self.cargo.get(), self.telefono.get(), self.email.get()))
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"No se pudo insertar: {e}")
        conn.commit(); conn.close()
        if self.on_save:
            self.on_save()


# ---------------------------
# Tab Alquileres
# ---------------------------
class AlquileresTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.build_ui()
        self.populate()

    def build_ui(self):
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(top, text="Nuevo Alquiler", command=self.nuevo_alquiler).pack(side=tk.LEFT)
        ttk.Button(top, text="Ver Detalle", command=self.ver_detalle).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Registrar Multa/Damage", command=self.registrar_multa).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Registrar Mantenimiento", command=self.registrar_mantenimiento).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Refrescar", command=self.populate).pack(side=tk.RIGHT)

        cols = ("id", "inicio", "fin", "cliente", "vehiculo", "empleado", "costo")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=130)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def populate(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        conn = get_connection(); c = conn.cursor()
        query = """SELECT a.id_alquiler, a.fecha_inicio, a.fecha_fin, a.costo_total,
                          c.apellido || ', ' || c.nombre AS cliente,
                          v.patente || ' - ' || v.marca || ' ' || v.modelo AS vehiculo,
                          e.apellido || ', ' || e.nombre AS empleado
                   FROM alquiler a
                   JOIN cliente c ON a.id_cliente = c.id_cliente
                   JOIN vehiculo v ON a.id_vehiculo = v.id_vehiculo
                   LEFT JOIN empleado e ON a.id_empleado = e.id_empleado
                   ORDER BY a.fecha_inicio DESC
                """
        c.execute(query)
        for row in c.fetchall():
            self.tree.insert("", tk.END, values=(row["id_alquiler"], row["fecha_inicio"], row["fecha_fin"], row["cliente"], row["vehiculo"], row["empleado"], row["costo_total"]))
        conn.close()

    def nuevo_alquiler(self):
        DialogNuevoAlquiler(self, on_save=self.populate)

    def ver_detalle(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un alquiler")
            return
        item = self.tree.item(sel[0])["values"]
        id_alq = item[0]
        conn = get_connection(); c = conn.cursor()
        c.execute("""SELECT a.*, c.nombre||' '||c.apellido as cliente, v.patente, v.marca, v.modelo, e.nombre||' '||e.apellido as empleado
                     FROM alquiler a
                     JOIN cliente c ON a.id_cliente=c.id_cliente
                     JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo
                     LEFT JOIN empleado e ON a.id_empleado=e.id_empleado
                     WHERE a.id_alquiler = ?""", (id_alq,))
        row = c.fetchone()
        c.execute("SELECT * FROM multa WHERE id_alquiler = ?", (id_alq,))
        multas = c.fetchall()
        conn.close()
        txt = f"Alquiler #{id_alq}\nCliente: {row['cliente']}\nVehículo: {row['patente']} - {row['marca']} {row['modelo']}\nInicio: {row['fecha_inicio']}\nFin: {row['fecha_fin']}\nCosto: {row['costo_total']}\nEmpleado: {row['empleado']}\n\nMultas/Daños:\n"
        if multas:
            for m in multas:
                txt += f"- {m['descripcion']} : ${m['monto']}\n"
        else:
            txt += "Ninguna\n"
        messagebox.showinfo("Detalle Alquiler", txt)

    def registrar_multa(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un alquiler")
            return
        item = self.tree.item(sel[0])["values"]
        id_alq = item[0]
        desc = simpledialog.askstring("Multa/Daño", "Descripción:")
        if not desc:
            return
        monto = simpledialog.askfloat("Multa/Daño", "Monto:")
        if monto is None:
            return
        conn = get_connection(); c = conn.cursor()
        c.execute("INSERT INTO multa (descripcion, monto, id_alquiler) VALUES (?,?,?)", (desc, monto, id_alq))
        conn.commit(); conn.close()
        messagebox.showinfo("OK", "Multa registrada")

    def registrar_mantenimiento(self):
        # Pedir vehículo y datos
        veh = simpledialog.askstring("Mantenimiento", "Patente del vehículo:")
        if not veh:
            return
        conn = get_connection(); c = conn.cursor()
        c.execute("SELECT id_vehiculo FROM vehiculo WHERE patente = ?", (veh.strip().upper(),))
        r = c.fetchone()
        if not r:
            messagebox.showerror("Error", "Patente no encontrada")
            conn.close(); return
        idv = r["id_vehiculo"]
        tipo = simpledialog.askstring("Mantenimiento", "Tipo (preventivo/correctivo):")
        fecha = simpledialog.askstring("Mantenimiento", "Fecha (YYYY-MM-DD):", initialvalue=str(date.today()))
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except Exception:
            messagebox.showerror("Error", "Fecha inválida")
            conn.close(); return
        costo = simpledialog.askfloat("Mantenimiento", "Costo:")
        obs = simpledialog.askstring("Mantenimiento", "Observaciones (opcional):")
        c.execute("INSERT INTO mantenimiento (tipo, fecha, costo, id_vehiculo, observaciones) VALUES (?,?,?,?,?)", (tipo, fecha, costo or 0.0, idv, obs))
        c.execute("UPDATE vehiculo SET fecha_ultimo_mantenimiento = ? WHERE id_vehiculo = ?", (fecha, idv))
        conn.commit(); conn.close()
        messagebox.showinfo("OK", "Mantenimiento registrado")


class DialogNuevoAlquiler(simpledialog.Dialog):
    def __init__(self, parent, on_save=None):
        self.on_save = on_save
        super().__init__(parent, "Nuevo Alquiler")

    def body(self, frame):
        ttk.Label(frame, text="Cliente (ID):").grid(row=0, column=0, sticky=tk.W)
        self.id_cliente = ttk.Entry(frame); self.id_cliente.grid(row=0, column=1)
        ttk.Label(frame, text="Vehículo (ID):").grid(row=1, column=0, sticky=tk.W)
        self.id_vehiculo = ttk.Entry(frame); self.id_vehiculo.grid(row=1, column=1)
        ttk.Label(frame, text="Empleado (ID) opcional:").grid(row=2, column=0, sticky=tk.W)
        self.id_empleado = ttk.Entry(frame); self.id_empleado.grid(row=2, column=1)
        ttk.Label(frame, text="Fecha inicio (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W)
        self.fecha_inicio = ttk.Entry(frame); self.fecha_inicio.grid(row=3, column=1)
        ttk.Label(frame, text="Fecha fin (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W)
        self.fecha_fin = ttk.Entry(frame); self.fecha_fin.grid(row=4, column=1)
        ttk.Label(frame, text="(También puedes ver IDs en las pestañas Clientes/Vehículos/Empleados)").grid(row=5, column=0, columnspan=2, pady=5)
        return self.id_cliente

    def validate(self):
        try:
            # validar formatos
            datetime.strptime(self.fecha_inicio.get(), "%Y-%m-%d")
            datetime.strptime(self.fecha_fin.get(), "%Y-%m-%d")
        except Exception:
            messagebox.showwarning("Validación", "Fechas en formato inválido (usar YYYY-MM-DD)")
            return False
        if not self.id_cliente.get() or not self.id_vehiculo.get():
            messagebox.showwarning("Validación", "Cliente y Vehículo son requeridos (ID numérico)")
            return False
        return True

    def apply(self):
        try:
            id_cliente = int(self.id_cliente.get())
            id_vehiculo = int(self.id_vehiculo.get())
            id_empleado = int(self.id_empleado.get()) if self.id_empleado.get() else None
            registrar_alquiler(self.fecha_inicio.get(), self.fecha_fin.get(), id_cliente, id_vehiculo, id_empleado)
            messagebox.showinfo("OK", "Alquiler registrado")
            if self.on_save:
                self.on_save()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ---------------------------
# Tab Reportes
# ---------------------------
class ReportesTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.build_ui()

    def build_ui(self):
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(top, text="Listar alquileres por cliente", command=self.listar_alquileres_por_cliente).pack(side=tk.LEFT)
        ttk.Button(top, text="Vehículos más alquilados", command=self.vehiculos_mas_alquilados).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Facturación mensual (gráfico)", command=self.facturacion_mensual).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Exportar lista alquileres (CSV)", command=self.exportar_alquileres_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Refrescar", command=lambda: None).pack(side=tk.RIGHT)

        self.txt = tk.Text(self); self.txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def listar_alquileres_por_cliente(self):
        cliente_id = simpledialog.askinteger("Listado", "ID de cliente (vacío = todos):", parent=self)
        conn = get_connection(); c = conn.cursor()
        if cliente_id:
            c.execute("""SELECT a.*, c.apellido||', '||c.nombre as cliente, v.patente FROM alquiler a JOIN cliente c ON a.id_cliente=c.id_cliente JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo WHERE a.id_cliente=? ORDER BY a.fecha_inicio DESC""", (cliente_id,))
        else:
            c.execute("""SELECT a.*, c.apellido||', '||c.nombre as cliente, v.patente FROM alquiler a JOIN cliente c ON a.id_cliente=c.id_cliente JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo ORDER BY a.fecha_inicio DESC""")
        rows = c.fetchall(); conn.close()
        self.txt.delete("1.0", tk.END)
        for r in rows:
            self.txt.insert(tk.END, f"#{r['id_alquiler']} - {r['cliente']} - {r['patente']} - {r['fecha_inicio']} -> {r['fecha_fin']} - ${r['costo_total']}\n")

    def vehiculos_mas_alquilados(self):
        conn = get_connection(); c = conn.cursor()
        c.execute("""SELECT v.id_vehiculo, v.patente, v.marca||' '||v.modelo as desc, COUNT(a.id_alquiler) as veces
                     FROM vehiculo v LEFT JOIN alquiler a ON v.id_vehiculo = a.id_vehiculo
                     GROUP BY v.id_vehiculo
                     ORDER BY veces DESC
                  """)
        rows = c.fetchall(); conn.close()
        self.txt.delete("1.0", tk.END)
        for r in rows:
            self.txt.insert(tk.END, f"{r['patente']} - {r['desc']} : {r['veces']} alquileres\n")

    def facturacion_mensual(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("Error", "matplotlib no está instalado. Instale con 'pip install matplotlib' para ver gráficos.")
            return
        # obtener facturación por mes (YYYY-MM)
        conn = get_connection(); c = conn.cursor()
        c.execute("""SELECT substr(fecha_inicio,1,7) as mes, SUM(costo_total) as total
                     FROM alquiler
                     GROUP BY mes
                     ORDER BY mes""")
        rows = c.fetchall(); conn.close()
        meses = [r["mes"] for r in rows]
        import numpy as np
        tot = [r["total"] for r in rows]
        if not meses:
            messagebox.showinfo("Info", "No hay datos de facturación")
            return
        plt.figure(figsize=(8,4))
        plt.bar(meses, tot)
        plt.title("Facturación mensual")
        plt.xlabel("Mes")
        plt.ylabel("Total ($)")
        plt.tight_layout()
        plt.show()

    def exportar_alquileres_csv(self):
        import csv
        fname = "alquileres_export.csv"
        conn = get_connection(); c = conn.cursor()
        c.execute("""SELECT a.id_alquiler, a.fecha_inicio, a.fecha_fin, a.costo_total,
                            c.nombre||' '||c.apellido as cliente, v.patente as vehiculo
                     FROM alquiler a JOIN cliente c ON a.id_cliente=c.id_cliente JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo
                     ORDER BY a.fecha_inicio DESC""")
        rows = c.fetchall(); conn.close()
        with open(fname, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["id_alquiler","fecha_inicio","fecha_fin","costo_total","cliente","vehiculo"])
            for r in rows:
                writer.writerow([r["id_alquiler"], r["fecha_inicio"], r["fecha_fin"], r["costo_total"], r["cliente"], r["vehiculo"]])
        messagebox.showinfo("Exportar", f"Exportado a {fname}")


# ---------------------------
# Main
# ---------------------------

def main():
    init_db()
    seed_sample_data()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
