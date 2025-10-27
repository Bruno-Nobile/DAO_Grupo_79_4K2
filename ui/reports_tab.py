#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de interfaz para reportes
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# Agregar directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection
from config import MATPLOTLIB_AVAILABLE


class ReportesTab(ttk.Frame):
    """Tab para reportes y análisis"""
    
    def __init__(self, container):
        super().__init__(container)
        self.build_ui()

    def build_ui(self):
        """Construye la interfaz de usuario"""
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(top, text="Listar alquileres por cliente", command=self.listar_alquileres_por_cliente).pack(side=tk.LEFT)
        ttk.Button(top, text="Vehículos más alquilados", command=self.vehiculos_mas_alquilados).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Facturación mensual (gráfico)", command=self.facturacion_mensual).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Exportar lista alquileres (CSV)", command=self.exportar_alquileres_csv).pack(side=tk.LEFT, padx=5)

        self.txt = tk.Text(self)
        self.txt.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def listar_alquileres_por_cliente(self):
        """Lista los alquileres por cliente"""
        cliente_id = simpledialog.askinteger("Listado", "ID de cliente (vacío = todos):", parent=self)
        conn = get_connection()
        c = conn.cursor()
        
        if cliente_id:
            c.execute("""SELECT a.*, c.apellido||', '||c.nombre as cliente, v.patente
                         FROM alquiler a
                         JOIN cliente c ON a.id_cliente=c.id_cliente
                         JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo
                         WHERE a.id_cliente=?
                         ORDER BY a.fecha_inicio DESC""", (cliente_id,))
        else:
            c.execute("""SELECT a.*, c.apellido||', '||c.nombre as cliente, v.patente
                         FROM alquiler a
                         JOIN cliente c ON a.id_cliente=c.id_cliente
                         JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo
                         ORDER BY a.fecha_inicio DESC""")
        
        rows = c.fetchall()
        conn.close()
        
        self.txt.delete("1.0", tk.END)
        for r in rows:
            self.txt.insert(tk.END, f"#{r['id_alquiler']} - {r['cliente']} - {r['patente']} - "
                           f"{r['fecha_inicio']} -> {r['fecha_fin']} - ${r['costo_total']}\n")

    def vehiculos_mas_alquilados(self):
        """Lista los vehículos más alquilados"""
        conn = get_connection()
        c = conn.cursor()
        
        c.execute("""SELECT v.id_vehiculo, v.patente, v.marca||' '||v.modelo as desc, COUNT(a.id_alquiler) as veces
                     FROM vehiculo v
                     LEFT JOIN alquiler a ON v.id_vehiculo = a.id_vehiculo
                     GROUP BY v.id_vehiculo
                     ORDER BY veces DESC""")
        
        rows = c.fetchall()
        conn.close()
        
        self.txt.delete("1.0", tk.END)
        for r in rows:
            self.txt.insert(tk.END, f"{r['patente']} - {r['desc']} : {r['veces']} alquileres\n")

    def facturacion_mensual(self):
        """Muestra un gráfico de facturación mensual"""
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror(
                "Error",
                "matplotlib no está instalado. Instale con 'pip install matplotlib' para ver gráficos."
            )
            return
        
        import matplotlib.pyplot as plt
        
        conn = get_connection()
        c = conn.cursor()
        
        c.execute("""SELECT substr(fecha_inicio,1,7) as mes, SUM(costo_total) as total
                     FROM alquiler
                     GROUP BY mes
                     ORDER BY mes""")
        
        rows = c.fetchall()
        conn.close()
        
        meses = [r["mes"] for r in rows]
        tot = [r["total"] for r in rows]
        
        if not meses:
            messagebox.showinfo("Info", "No hay datos de facturación")
            return
        
        plt.figure(figsize=(8, 4))
        plt.bar(meses, tot)
        plt.title("Facturación mensual")
        plt.xlabel("Mes")
        plt.ylabel("Total ($)")
        plt.tight_layout()
        plt.show()

    def exportar_alquileres_csv(self):
        """Exporta la lista de alquileres a un archivo CSV"""
        import csv
        
        fname = "alquileres_export.csv"
        conn = get_connection()
        c = conn.cursor()
        
        c.execute("""SELECT a.id_alquiler, a.fecha_inicio, a.fecha_fin, a.costo_total,
                            c.nombre||' '||c.apellido as cliente, v.patente as vehiculo
                     FROM alquiler a
                     JOIN cliente c ON a.id_cliente=c.id_cliente
                     JOIN vehiculo v ON a.id_vehiculo=v.id_vehiculo
                     ORDER BY a.fecha_inicio DESC""")
        
        rows = c.fetchall()
        conn.close()
        
        with open(fname, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["id_alquiler", "fecha_inicio", "fecha_fin", "costo_total", "cliente", "vehiculo"])
            for r in rows:
                writer.writerow([
                    r["id_alquiler"], r["fecha_inicio"], r["fecha_fin"],
                    r["costo_total"], r["cliente"], r["vehiculo"]
                ])
        
        messagebox.showinfo("Exportar", f"Exportado a {fname}")
