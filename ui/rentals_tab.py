#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de interfaz para la gestión de alquileres
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import sys
import os

# Agregar directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection
from models import registrar_alquiler


class AlquileresTab(ttk.Frame):
    """Tab para gestión de alquileres"""
    
    def __init__(self, container):
        super().__init__(container)
        self.build_ui()
        self.populate()

    def build_ui(self):
        """Construye la interfaz de usuario"""
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=5, pady=5)
        
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
        """Carga los alquileres en la tabla"""
        for r in self.tree.get_children():
            self.tree.delete(r)
        
        conn = get_connection()
        c = conn.cursor()
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
            self.tree.insert("", tk.END, values=(
                row["id_alquiler"],
                row["fecha_inicio"],
                row["fecha_fin"],
                row["cliente"],
                row["vehiculo"],
                row["empleado"],
                row["costo_total"]
            ))
        conn.close()

    def nuevo_alquiler(self):
        """Abre diálogo para nuevo alquiler"""
        DialogNuevoAlquiler(self, on_save=self.populate)

    def ver_detalle(self):
        """Muestra los detalles del alquiler seleccionado"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un alquiler")
            return
        
        item = self.tree.item(sel[0])["values"]
        id_alq = item[0]
        
        conn = get_connection()
        c = conn.cursor()
        
        c.execute("""SELECT a.*, c.nombre||' '||c.apellido as cliente, v.patente, v.marca, v.modelo, 
                            e.nombre||' '||e.apellido as empleado
                     FROM alquiler a
                     JOIN cliente c ON a.id_cliente=c.id_cliente
                     JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo
                     LEFT JOIN empleado e ON a.id_empleado=e.id_empleado
                     WHERE a.id_alquiler = ?""", (id_alq,))
        row = c.fetchone()
        
        c.execute("SELECT * FROM multa WHERE id_alquiler = ?", (id_alq,))
        multas = c.fetchall()
        conn.close()
        
        txt = (f"Alquiler #{id_alq}\n"
               f"Cliente: {row['cliente']}\n"
               f"Vehículo: {row['patente']} - {row['marca']} {row['modelo']}\n"
               f"Inicio: {row['fecha_inicio']}\n"
               f"Fin: {row['fecha_fin']}\n"
               f"Costo: {row['costo_total']}\n"
               f"Empleado: {row['empleado']}\n\n"
               f"Multas/Daños:\n")
        
        if multas:
            for m in multas:
                txt += f"- {m['descripcion']} : ${m['monto']}\n"
        else:
            txt += "Ninguna\n"
        
        messagebox.showinfo("Detalle Alquiler", txt)

    def registrar_multa(self):
        """Registra una multa o daño para el alquiler seleccionado"""
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
        
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO multa (descripcion, monto, id_alquiler) VALUES (?,?,?)", (desc, monto, id_alq))
        conn.commit()
        conn.close()
        messagebox.showinfo("OK", "Multa registrada")

    def registrar_mantenimiento(self):
        """Registra un mantenimiento para un vehículo"""
        veh = simpledialog.askstring("Mantenimiento", "Patente del vehículo:")
        if not veh:
            return
        
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id_vehiculo FROM vehiculo WHERE patente = ?", (veh.strip().upper(),))
        r = c.fetchone()
        
        if not r:
            messagebox.showerror("Error", "Patente no encontrada")
            conn.close()
            return
        
        idv = r["id_vehiculo"]
        
        tipo = simpledialog.askstring("Mantenimiento", "Tipo (preventivo/correctivo):")
        fecha = simpledialog.askstring("Mantenimiento", "Fecha (YYYY-MM-DD):", initialvalue=str(date.today()))
        
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except Exception:
            messagebox.showerror("Error", "Fecha inválida")
            conn.close()
            return
        
        costo = simpledialog.askfloat("Mantenimiento", "Costo:")
        obs = simpledialog.askstring("Mantenimiento", "Observaciones (opcional):")
        
        c.execute(
            "INSERT INTO mantenimiento (tipo, fecha, costo, id_vehiculo, observaciones) VALUES (?,?,?,?,?)",
            (tipo, fecha, costo or 0.0, idv, obs)
        )
        c.execute("UPDATE vehiculo SET fecha_ultimo_mantenimiento = ? WHERE id_vehiculo = ?", (fecha, idv))
        conn.commit()
        conn.close()
        messagebox.showinfo("OK", "Mantenimiento registrado")


class DialogNuevoAlquiler(simpledialog.Dialog):
    """Diálogo para crear un nuevo alquiler"""
    
    def __init__(self, parent, on_save=None):
        self.on_save = on_save
        super().__init__(parent, "Nuevo Alquiler")

    def body(self, frame):
        """Construye el formulario"""
        ttk.Label(frame, text="Cliente (ID):").grid(row=0, column=0, sticky=tk.W)
        self.id_cliente = ttk.Entry(frame)
        self.id_cliente.grid(row=0, column=1)
        
        ttk.Label(frame, text="Vehículo (ID):").grid(row=1, column=0, sticky=tk.W)
        self.id_vehiculo = ttk.Entry(frame)
        self.id_vehiculo.grid(row=1, column=1)
        
        ttk.Label(frame, text="Empleado (ID) opcional:").grid(row=2, column=0, sticky=tk.W)
        self.id_empleado = ttk.Entry(frame)
        self.id_empleado.grid(row=2, column=1)
        
        ttk.Label(frame, text="Fecha inicio (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W)
        self.fecha_inicio = ttk.Entry(frame)
        self.fecha_inicio.grid(row=3, column=1)
        
        ttk.Label(frame, text="Fecha fin (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W)
        self.fecha_fin = ttk.Entry(frame)
        self.fecha_fin.grid(row=4, column=1)
        
        ttk.Label(
            frame,
            text="(También puedes ver IDs en las pestañas Clientes/Vehículos/Empleados)"
        ).grid(row=5, column=0, columnspan=2, pady=5)
        
        return self.id_cliente

    def validate(self):
        """Valida los datos ingresados"""
        try:
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
        """Guarda el alquiler en la base de datos"""
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
