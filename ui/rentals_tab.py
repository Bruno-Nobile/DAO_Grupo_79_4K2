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
from models import registrar_alquiler, actualizar_estados_vehiculos
from validations import validar_fecha_inicio_alquiler
from .ui_utils import enable_treeview_sorting


class AlquileresTab(ttk.Frame):
    """Tab para gestión de alquileres"""
    
    def __init__(self, container):
        super().__init__(container)
        self.build_ui()
        self.populate()
        self.populate_mantenimientos()  # Cargar mantenimientos al iniciar

    def build_ui(self):
        """
        Construye la interfaz de usuario
        Programación Orientada a Objetos - Método de construcción de UI
        """
        # Notebook para pestañas (Alquileres y Mantenimientos)
        # Programación Orientada a Objetos - Uso de Notebook para organización
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de Alquileres
        frame_alquileres = ttk.Frame(self.notebook)
        self.notebook.add(frame_alquileres, text="Alquileres")
        
        # Botones dentro de la pestaña Alquileres
        # Programación Estructurada - Organización de botones por funcionalidad
        top_alq = ttk.Frame(frame_alquileres)
        top_alq.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(top_alq, text="Nuevo Alquiler", command=self.nuevo_alquiler).pack(side=tk.LEFT)
        ttk.Button(top_alq, text="Ver Detalle", command=self.ver_detalle).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_alq, text="Eliminar", command=self.eliminar_alquiler).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_alq, text="Registrar Multa/Daño", command=self.registrar_multa).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_alq, text="Refrescar", command=self.populate).pack(side=tk.RIGHT)
        
        cols = ("id", "inicio", "fin", "cliente", "vehiculo", "empleado", "costo")
        self.tree = ttk.Treeview(frame_alquileres, columns=cols, show="headings", style="Colored.Treeview")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=130)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        enable_treeview_sorting(self.tree)
        
        # Pestaña de Mantenimientos
        frame_mantenimientos = ttk.Frame(self.notebook)
        self.notebook.add(frame_mantenimientos, text="Mantenimientos")
        
        # Botones dentro de la pestaña Mantenimientos
        # Programación Estructurada - Organización de botones por funcionalidad
        top_mant = ttk.Frame(frame_mantenimientos)
        top_mant.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(top_mant, text="Registrar Mantenimiento", command=self.registrar_mantenimiento).pack(side=tk.LEFT)
        ttk.Button(top_mant, text="Eliminar", command=self.eliminar_mantenimiento).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_mant, text="Refrescar", command=self.populate_mantenimientos).pack(side=tk.RIGHT)
        
        cols_mant = ("id", "tipo", "fechas", "costo", "vehiculo", "observaciones")
        self.tree_mantenimientos = ttk.Treeview(frame_mantenimientos, columns=cols_mant, show="headings")
        for c in cols_mant:
            self.tree_mantenimientos.heading(c, text=c.capitalize())
            self.tree_mantenimientos.column(c, width=150)
        self.tree_mantenimientos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        enable_treeview_sorting(self.tree_mantenimientos)

    def populate(self):
        """
        Carga los alquileres en la tabla
        Programación Estructurada - Función bien organizada
        Actualiza automáticamente los estados de vehículos antes de mostrar los datos
        """
        # Actualizar estados de vehículos antes de mostrar (para reflejar cambios de fechas)
        try:
            actualizar_estados_vehiculos()
        except Exception:
            # Si hay error, continuar de todas formas
            pass
        
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
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido para evitar cerrar conexión compartida

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
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido para evitar cerrar conexión compartida
        
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

    def eliminar_alquiler(self):
        """
        Elimina el alquiler seleccionado
        Programación Orientada a Objetos - Método de la clase
        Programación Estructurada - Función bien organizada
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un alquiler para eliminar")
            return
        
        item = self.tree.item(sel[0])["values"]
        id_alq = item[0]
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el alquiler #{id_alq}?\n\n"
            f"Esta acción también eliminará todas las multas asociadas."
        )
        
        if not respuesta:
            return
        
        conn = get_connection()
        c = conn.cursor()
        
        try:
            # Obtener información del vehículo antes de eliminar el alquiler
            c.execute("SELECT id_vehiculo FROM alquiler WHERE id_alquiler = ?", (id_alq,))
            row = c.fetchone()
            
            if not row:
                messagebox.showerror("Error", "Alquiler no encontrado")
                return
            
            id_vehiculo = row["id_vehiculo"]
            
            # Eliminar el alquiler (las multas se eliminarán automáticamente por CASCADE)
            c.execute("DELETE FROM alquiler WHERE id_alquiler = ?", (id_alq,))
            
            # Verificar si el vehículo tiene otros alquileres activos
            # Un alquiler está activo si: fecha_inicio <= fecha_actual <= fecha_fin
            from datetime import date as date_class
            fecha_actual = date_class.today().strftime("%Y-%m-%d")
            c.execute("""
                SELECT COUNT(*) FROM alquiler 
                WHERE id_vehiculo = ? 
                AND date(fecha_inicio) <= date(?)
                AND date(fecha_fin) >= date(?)
            """, (id_vehiculo, fecha_actual, fecha_actual))
            otros_alquileres = c.fetchone()[0]
            
            # Si no hay otros alquileres y el vehículo estaba "Alquilado", cambiar a "Disponible"
            if otros_alquileres == 0:
                c.execute("SELECT estado FROM vehiculo WHERE id_vehiculo = ?", (id_vehiculo,))
                estado_actual = c.fetchone()
                if estado_actual and estado_actual["estado"] == "Alquilado":
                    c.execute("UPDATE vehiculo SET estado = 'Disponible' WHERE id_vehiculo = ?", (id_vehiculo,))
            
            conn.commit()
            messagebox.showinfo("Éxito", f"Alquiler #{id_alq} eliminado correctamente")
            
            # Refrescar la lista
            self.populate()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al eliminar alquiler: {str(e)}")
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido para evitar cerrar conexión compartida

    def registrar_multa(self):
        """
        Registra una multa o daño para el alquiler seleccionado
        Programación Orientada a Objetos - Abre diálogo completo
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un alquiler")
            return
        
        item = self.tree.item(sel[0])["values"]
        id_alq = item[0]
        
        DialogMulta(self, id_alquiler=id_alq, on_save=self.populate)
    
    def populate_mantenimientos(self):
        """
        Carga los mantenimientos en la tabla
        Programación Estructurada - Función bien organizada
        """
        for r in self.tree_mantenimientos.get_children():
            self.tree_mantenimientos.delete(r)
        
        conn = get_connection()
        c = conn.cursor()
        query = """SELECT m.id_mant, m.tipo, m.fecha_inicio, m.fecha_fin, m.costo, m.observaciones,
                          v.patente || ' - ' || v.marca || ' ' || v.modelo AS vehiculo
                   FROM mantenimiento m
                   JOIN vehiculo v ON m.id_vehiculo = v.id_vehiculo
                   ORDER BY m.fecha_inicio DESC
                """
        c.execute(query)
        for row in c.fetchall():
            self.tree_mantenimientos.insert("", tk.END, values=(
                row["id_mant"],
                row["tipo"],
                f"{row['fecha_inicio']} - {row['fecha_fin']}",
                row["costo"],
                row["vehiculo"],
                row["observaciones"] or ""
            ))
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido para evitar cerrar conexión compartida

    def registrar_mantenimiento(self):
        """
        Registra un mantenimiento para un vehículo
        Programación Orientada a Objetos - Abre diálogo completo
        """
        DialogMantenimiento(self, on_save=self.populate_mantenimientos)
    
    def eliminar_mantenimiento(self):
        """
        Elimina el mantenimiento seleccionado
        Programación Orientada a Objetos - Método de la clase
        Programación Estructurada - Función bien organizada
        """
        sel = self.tree_mantenimientos.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un mantenimiento para eliminar")
            return
        
        item = self.tree_mantenimientos.item(sel[0])["values"]
        id_mant = item[0]
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el mantenimiento #{id_mant}?"
        )
        
        if not respuesta:
            return
        
        conn = get_connection()
        c = conn.cursor()
        
        try:
            # Obtener información del vehículo antes de eliminar el mantenimiento
            c.execute("SELECT id_vehiculo FROM mantenimiento WHERE id_mant = ?", (id_mant,))
            row = c.fetchone()
            
            if not row:
                messagebox.showerror("Error", "Mantenimiento no encontrado")
                return
            
            id_vehiculo = row["id_vehiculo"]
            
            # Eliminar el mantenimiento
            c.execute("DELETE FROM mantenimiento WHERE id_mant = ?", (id_mant,))
            
            # Verificar si el vehículo tiene otros mantenimientos activos
            # Si no tiene más mantenimientos activos y estaba en "Mantenimiento", actualizar estado
            from datetime import date as date_class
            fecha_actual = date_class.today().strftime("%Y-%m-%d")
            
            c.execute("""
                SELECT COUNT(*) FROM mantenimiento 
                WHERE id_vehiculo = ? 
                AND date(fecha_fin) >= date(?)
            """, (id_vehiculo, fecha_actual))
            otros_mantenimientos_activos = c.fetchone()[0]
            
            if otros_mantenimientos_activos == 0:
                c.execute("SELECT estado FROM vehiculo WHERE id_vehiculo = ?", (id_vehiculo,))
                estado_actual = c.fetchone()
                if estado_actual and estado_actual["estado"] == "Mantenimiento":
                    # Verificar si tiene alquileres activos antes de cambiar a Disponible
                    # Un alquiler está activo si: fecha_inicio <= fecha_actual <= fecha_fin
                    c.execute("""
                        SELECT COUNT(*) FROM alquiler 
                        WHERE id_vehiculo = ? 
                        AND date(fecha_inicio) <= date(?)
                        AND date(fecha_fin) >= date(?)
                    """, (id_vehiculo, fecha_actual, fecha_actual))
                    alquileres_activos = c.fetchone()[0]
                    
                    if alquileres_activos == 0:
                        c.execute("UPDATE vehiculo SET estado = 'Disponible' WHERE id_vehiculo = ?", (id_vehiculo,))
                    else:
                        c.execute("UPDATE vehiculo SET estado = 'Alquilado' WHERE id_vehiculo = ?", (id_vehiculo,))
            
            conn.commit()
            messagebox.showinfo("Éxito", f"Mantenimiento #{id_mant} eliminado correctamente")
            
            # Refrescar la lista
            self.populate_mantenimientos()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al eliminar mantenimiento: {str(e)}")
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido para evitar cerrar conexión compartida


class DialogNuevoAlquiler(simpledialog.Dialog):
    """
    Diálogo para crear un nuevo alquiler
    Programación Orientada a Objetos - Clase de diálogo personalizada
    """
    
    def __init__(self, parent, on_save=None):
        self.on_save = on_save
        self._error_occurred = False  # Flag para indicar si hubo error
        super().__init__(parent, "Nuevo Alquiler")
    
    def ok(self):
        """
        Sobrescribe el método ok para evitar cerrar el diálogo cuando hay errores
        Programación Orientada a Objetos - Polimorfismo
        """
        if not self.validate():
            return
        
        self.apply()
        
        # Solo cerrar el diálogo si no hubo error
        if not self._error_occurred:
            self.destroy()

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
        """
        Valida los datos ingresados
        Programación Estructurada - Validación completa
        """
        # Validar formato de fechas
        try:
            datetime.strptime(self.fecha_inicio.get(), "%Y-%m-%d")
            datetime.strptime(self.fecha_fin.get(), "%Y-%m-%d")
        except Exception:
            messagebox.showwarning("Validación", "Fechas en formato inválido (usar YYYY-MM-DD)")
            return False
        
        # Validar que la fecha de inicio sea mayor o igual a la fecha actual
        fecha_inicio = self.fecha_inicio.get().strip()
        if not validar_fecha_inicio_alquiler(fecha_inicio):
            messagebox.showerror("Validación", "La fecha de inicio debe ser mayor o igual a la fecha actual")
            return False
        
        # Validar que cliente y vehículo estén presentes
        if not self.id_cliente.get() or not self.id_vehiculo.get():
            messagebox.showwarning("Validación", "Cliente y Vehículo son requeridos (ID numérico)")
            return False
        
        # Validar estado del vehículo antes de permitir el alquiler
        # Programación Estructurada - Validación de estado
        try:
            id_vehiculo = int(self.id_vehiculo.get())
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT estado FROM vehiculo WHERE id_vehiculo = ?", (id_vehiculo,))
            row = c.fetchone()
            
            if not row:
                messagebox.showerror("Validación", "Vehículo no encontrado")
                return False
            
            estado = row["estado"]
            # Comparación case-insensitive para el estado
            # Programación Estructurada - Validación de estado
            if not estado or estado.upper() != "DISPONIBLE":
                messagebox.showerror("Validación", 
                                  f"El vehículo no está disponible para alquilar. "
                                  f"Estado actual: {estado}. "
                                  f"Solo se pueden alquilar vehículos en estado 'Disponible'.")
                return False
        except ValueError:
            messagebox.showerror("Validación", "ID de vehículo inválido")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error al validar vehículo: {str(e)}")
            return False
        
        return True

    def apply(self):
        """
        Guarda el alquiler en la base de datos
        Programación Estructurada - Manejo de errores
        No cierra el diálogo si hay errores
        """
        self._error_occurred = False  # Resetear flag de error
        
        try:
            id_cliente = int(self.id_cliente.get())
            id_vehiculo = int(self.id_vehiculo.get())
            id_empleado = int(self.id_empleado.get()) if self.id_empleado.get() else None
            
            registrar_alquiler(self.fecha_inicio.get(), self.fecha_fin.get(), id_cliente, id_vehiculo, id_empleado)
            messagebox.showinfo("OK", "Alquiler registrado")
            
            if self.on_save:
                self.on_save()
            
            # Si llegamos aquí, no hubo error, el diálogo se cerrará
            self._error_occurred = False
            
        except ValueError as e:
            # Los mensajes de ValueError ya son claros (Cliente no encontrado, Empleado no encontrado, etc.)
            self._error_occurred = True  # Marcar que hubo error
            messagebox.showerror("Error", str(e))
        except Exception as e:
            # Capturar errores de FOREIGN KEY y mostrar mensajes más claros
            self._error_occurred = True  # Marcar que hubo error
            error_msg = str(e)
            if "FOREIGN KEY" in error_msg or "constraint" in error_msg.lower():
                # Intentar determinar qué entidad falta
                if "cliente" in error_msg.lower() or "id_cliente" in error_msg.lower():
                    messagebox.showerror("Error", "Cliente no encontrado.")
                elif "empleado" in error_msg.lower() or "id_empleado" in error_msg.lower():
                    messagebox.showerror("Error", "Empleado no encontrado.")
                elif "vehiculo" in error_msg.lower() or "id_vehiculo" in error_msg.lower():
                    messagebox.showerror("Error", "Vehículo no encontrado.")
                else:
                    messagebox.showerror("Error", "Error de referencia: Verifique que el cliente, vehículo y empleado (si se especificó) existan.")
            else:
                messagebox.showerror("Error", str(e))


class DialogMulta(simpledialog.Dialog):
    """
    Diálogo completo para registrar multa/daño
    Programación Orientada a Objetos - Clase de diálogo
    """
    
    def __init__(self, parent, id_alquiler, on_save=None):
        self.id_alquiler = id_alquiler
        self.on_save = on_save
        super().__init__(parent, "Registrar Multa/Daño")
    
    def body(self, frame):
        """
        Construye el formulario completo
        Programación Estructurada - Formulario bien organizado
        """
        ttk.Label(frame, text="Descripción:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.descripcion = tk.Text(frame, height=4, width=40)
        self.descripcion.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Monto ($):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.monto = ttk.Entry(frame)
        self.monto.grid(row=1, column=1, pady=5, padx=5, sticky=tk.EW)
        
        frame.columnconfigure(1, weight=1)
        return self.descripcion
    
    def validate(self):
        """
        Valida los datos ingresados
        Programación Estructurada - Validación
        """
        if not self.descripcion.get("1.0", tk.END).strip():
            messagebox.showwarning("Validación", "La descripción es requerida")
            return False
        
        try:
            monto = float(self.monto.get())
            if monto < 0:
                messagebox.showwarning("Validación", "El monto debe ser mayor o igual a 0")
                return False
        except ValueError:
            messagebox.showwarning("Validación", "El monto debe ser un número válido")
            return False
        
        return True
    
    def apply(self):
        """
        Guarda la multa en la base de datos
        Programación Estructurada - Persistencia
        """
        conn = get_connection()
        c = conn.cursor()
        descripcion = self.descripcion.get("1.0", tk.END).strip()
        monto = float(self.monto.get())
        
        c.execute("INSERT INTO multa (descripcion, monto, id_alquiler) VALUES (?,?,?)", 
                 (descripcion, monto, self.id_alquiler))
        conn.commit()
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido para evitar cerrar conexión compartida
        
        messagebox.showinfo("OK", "Multa registrada exitosamente")
        
        if self.on_save:
            self.on_save()


class DialogMantenimiento(simpledialog.Dialog):
    """
    Diálogo completo para registrar mantenimiento
    Programación Orientada a Objetos - Clase de diálogo
    """
    
    def __init__(self, parent, on_save=None):
        self.on_save = on_save
        super().__init__(parent, "Registrar Mantenimiento")
    
    def body(self, frame):
        """
        Construye el formulario completo
        Programación Estructurada - Formulario bien organizado
        """
        ttk.Label(frame, text="Patente del vehículo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.patente = ttk.Entry(frame)
        self.patente.grid(row=0, column=1, pady=5, padx=5, sticky=tk.EW)
        
        ttk.Label(frame, text="Tipo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tipo = ttk.Combobox(frame, values=["preventivo", "correctivo"], state="readonly")
        self.tipo.grid(row=1, column=1, pady=5, padx=5, sticky=tk.EW)
        self.tipo.current(0)
        
        ttk.Label(frame, text="Fecha inicio (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.fecha_inicio = ttk.Entry(frame)
        self.fecha_inicio.insert(0, str(date.today()))
        self.fecha_inicio.grid(row=2, column=1, pady=5, padx=5, sticky=tk.EW)
        
        ttk.Label(frame, text="Fecha fin (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.fecha_fin = ttk.Entry(frame)
        self.fecha_fin.insert(0, str(date.today()))
        self.fecha_fin.grid(row=3, column=1, pady=5, padx=5, sticky=tk.EW)
        
        ttk.Label(frame, text="Costo ($):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.costo = ttk.Entry(frame)
        self.costo.insert(0, "0.0")
        self.costo.grid(row=4, column=1, pady=5, padx=5, sticky=tk.EW)
        
        ttk.Label(frame, text="Observaciones:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.observaciones = tk.Text(frame, height=4, width=40)
        self.observaciones.grid(row=5, column=1, pady=5, padx=5)
        
        frame.columnconfigure(1, weight=1)
        return self.patente
    
    def validate(self):
        """
        Valida los datos ingresados
        Programación Estructurada - Validación completa
        """
        if not self.patente.get().strip():
            messagebox.showwarning("Validación", "La patente es requerida")
            return False
        
        if not self.tipo.get():
            messagebox.showwarning("Validación", "El tipo es requerido")
            return False
        
        try:
            fecha_inicio = datetime.strptime(self.fecha_inicio.get(), "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(self.fecha_fin.get(), "%Y-%m-%d").date()
            
            if fecha_fin < fecha_inicio:
                messagebox.showerror("Validación", "La fecha de fin debe ser igual o posterior a la fecha de inicio")
                return False
        except Exception:
            messagebox.showerror("Validación", "Fechas inválidas (usar formato YYYY-MM-DD)")
            return False
        
        try:
            costo = float(self.costo.get())
            if costo < 0:
                messagebox.showwarning("Validación", "El costo debe ser mayor o igual a 0")
                return False
        except ValueError:
            messagebox.showwarning("Validación", "El costo debe ser un número válido")
            return False
        
        # Validar que el vehículo no esté alquilado
        # Programación Estructurada - Validación de estado del vehículo
        conn = get_connection()
        c = conn.cursor()
        
        patente = self.patente.get().strip().upper()
        c.execute("SELECT id_vehiculo, estado FROM vehiculo WHERE patente = ?", (patente,))
        row = c.fetchone()
        
        if not row:
            messagebox.showerror("Validación", "Patente no encontrada")
            return False
        
        id_vehiculo = row["id_vehiculo"]
        estado = row["estado"]
        
        # Verificar que el vehículo no esté en estado "Alquilado"
        if estado and estado.upper() == "ALQUILADO":
            messagebox.showerror("Validación", 
                                f"No se puede realizar mantenimiento en un vehículo que está alquilado. "
                                f"Estado actual: {estado}. "
                                f"El vehículo debe estar disponible o en mantenimiento.")
            return False
        
        # Verificar que no tenga alquileres activos (por si acaso el estado no está actualizado)
        # Programación Estructurada - Validación de alquileres activos
        # Un alquiler está activo si: fecha_inicio <= fecha_actual <= fecha_fin
        fecha_actual = date.today().strftime("%Y-%m-%d")
        c.execute("""
            SELECT COUNT(*) FROM alquiler 
            WHERE id_vehiculo = ? 
            AND date(fecha_inicio) <= date(?)
            AND date(fecha_fin) >= date(?)
        """, (id_vehiculo, fecha_actual, fecha_actual))
        
        alquileres_activos = c.fetchone()[0]
        if alquileres_activos > 0:
            messagebox.showerror("Validación", 
                                f"No se puede realizar mantenimiento en un vehículo que tiene alquileres activos. "
                                f"El vehículo tiene {alquileres_activos} alquiler(es) activo(s). "
                                f"Espere a que finalicen los alquileres antes de realizar el mantenimiento.")
            return False
        
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido para evitar cerrar conexión compartida
        
        return True
    
    def apply(self):
        """
        Guarda el mantenimiento en la base de datos
        Programación Estructurada - Persistencia
        """
        conn = get_connection()
        c = conn.cursor()
        
        # Buscar vehículo por patente
        patente = self.patente.get().strip().upper()
        c.execute("SELECT id_vehiculo FROM vehiculo WHERE patente = ?", (patente,))
        r = c.fetchone()
        
        if not r:
            messagebox.showerror("Error", "Patente no encontrada")
            # No cerrar la conexión - el Singleton la maneja por thread
            # conn.close()  # Removido para evitar cerrar conexión compartida
            return
        
        id_vehiculo = r["id_vehiculo"]
        tipo = self.tipo.get()
        fecha_inicio = self.fecha_inicio.get()
        fecha_fin = self.fecha_fin.get()
        costo = float(self.costo.get())
        observaciones = self.observaciones.get("1.0", tk.END).strip()
        
        # Verificar que no haya alquileres en el período de mantenimiento
        from datetime import date as date_class
        fecha_actual = date_class.today().strftime("%Y-%m-%d")
        c.execute("""
            SELECT COUNT(*) FROM alquiler 
            WHERE id_vehiculo = ? 
            AND NOT (date(fecha_fin) < date(?) OR date(fecha_inicio) > date(?))
        """, (id_vehiculo, fecha_inicio, fecha_fin))
        
        alquileres_solapados = c.fetchone()[0]
        if alquileres_solapados > 0:
            messagebox.showerror("Validación", 
                                f"No se puede programar mantenimiento en un vehículo que tiene alquileres en ese período. "
                                f"El vehículo tiene {alquileres_solapados} alquiler(es) que se solapan con el mantenimiento.")
            return
        
        # Insertar mantenimiento
        c.execute(
            "INSERT INTO mantenimiento (tipo, fecha_inicio, fecha_fin, costo, id_vehiculo, observaciones) VALUES (?,?,?,?,?,?)",
            (tipo, fecha_inicio, fecha_fin, costo, id_vehiculo, observaciones if observaciones else None)
        )
        
        # Verificar si el vehículo está en mantenimiento activo (fecha_fin >= fecha_actual)
        # Si está en mantenimiento activo, actualizar estado a "Mantenimiento"
        fecha_fin_date = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        if fecha_fin_date >= date_class.today():
            c.execute("UPDATE vehiculo SET fecha_ultimo_mantenimiento = ?, estado = 'Mantenimiento' WHERE id_vehiculo = ?", 
                     (fecha_fin, id_vehiculo))
        else:
            # Si el mantenimiento ya terminó, solo actualizar fecha_ultimo_mantenimiento
            c.execute("UPDATE vehiculo SET fecha_ultimo_mantenimiento = ? WHERE id_vehiculo = ?", 
                     (fecha_fin, id_vehiculo))
        
        conn.commit()
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido para evitar cerrar conexión compartida
        
        messagebox.showinfo("OK", "Mantenimiento registrado exitosamente. El vehículo ahora está en estado 'Mantenimiento'.")
        
        if self.on_save:
            self.on_save()
