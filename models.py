#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de lógica de negocio para el sistema de alquiler de vehículos
"""

from datetime import datetime
from database import get_connection


def calcular_costo(costo_diario, fecha_inicio_str, fecha_fin_str):
    """Calcula el costo total basado en los días (inclusive)"""
    fi = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    ff = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    dias = (ff - fi).days + 1
    
    if dias < 1:
        raise ValueError("La fecha de fin debe ser igual o posterior a la fecha de inicio.")
    
    return round(dias * costo_diario, 2)


def vehiculo_disponible(id_vehiculo, fecha_inicio_str, fecha_fin_str):
    """
    Verifica si el vehículo no tiene alquileres solapados en ese período
    Programación Estructurada - Función bien organizada
    """
    conn = get_connection()
    c = conn.cursor()
    
    query = """
    SELECT COUNT(*) FROM alquiler
    WHERE id_vehiculo = ?
      AND NOT (date(fecha_fin) < date(?) OR date(fecha_inicio) > date(?))
    """
    # Si existe un alquiler cuyo rango NO está completamente fuera del período deseado => está solapado
    c.execute(query, (id_vehiculo, fecha_inicio_str, fecha_fin_str))
    cnt = c.fetchone()[0]
    
    # No cerrar la conexión aquí - el Singleton la maneja por thread
    # conn.close()  # Removido para evitar cerrar conexión compartida
    return cnt == 0


def registrar_alquiler(fecha_inicio, fecha_fin, id_cliente, id_vehiculo, id_empleado=None):
    """
    Registra un nuevo alquiler en la base de datos
    Programación Estructurada - Función bien organizada
    Valida que el vehículo esté disponible y actualiza su estado
    """
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # Validar que el cliente exista
        # Programación Estructurada - Validación de cliente
        c.execute("SELECT id_cliente FROM cliente WHERE id_cliente = ?", (id_cliente,))
        if not c.fetchone():
            raise ValueError("Cliente no encontrado.")
        
        # Validar que el empleado exista (si se proporcionó)
        # Programación Estructurada - Validación de empleado
        if id_empleado is not None:
            c.execute("SELECT id_empleado FROM empleado WHERE id_empleado = ?", (id_empleado,))
            if not c.fetchone():
                raise ValueError("Empleado no encontrado.")
        
        # Obtener información del vehículo (costo diario y estado)
        c.execute("SELECT costo_diario, estado FROM vehiculo WHERE id_vehiculo = ?", (id_vehiculo,))
        row = c.fetchone()
        
        if not row:
            raise ValueError("Vehículo no encontrado.")
        
        costo_diario = row["costo_diario"]
        estado_vehiculo = row["estado"]
        
        # Validar que el vehículo esté en estado "Disponible" (comparación case-insensitive)
        # Programación Estructurada - Validación de estado
        if estado_vehiculo and estado_vehiculo.upper() != "DISPONIBLE":
            raise ValueError(f"El vehículo no está disponible para alquilar. Estado actual: {estado_vehiculo}. "
                           f"Solo se pueden alquilar vehículos en estado 'Disponible'.")
        
        # Verificar disponibilidad temporal (no tiene alquileres solapados)
        if not vehiculo_disponible(id_vehiculo, fecha_inicio, fecha_fin):
            raise ValueError("Vehículo no disponible en el periodo indicado. "
                           f"Ya existe un alquiler activo en ese rango de fechas.")
        
        # Calcular costo total
        costo_total = calcular_costo(costo_diario, fecha_inicio, fecha_fin)
        
        # Insertar alquiler
        c.execute(
            """INSERT INTO alquiler (fecha_inicio, fecha_fin, costo_total, id_cliente, id_vehiculo, id_empleado)
               VALUES (?,?,?,?,?,?)""",
            (fecha_inicio, fecha_fin, costo_total, id_cliente, id_vehiculo, id_empleado)
        )
        
        # Actualizar estado del vehículo a "Alquilado"
        c.execute("UPDATE vehiculo SET estado = 'Alquilado' WHERE id_vehiculo = ?", (id_vehiculo,))
        
        conn.commit()
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido - el Singleton maneja el ciclo de vida
        return True
    except Exception as e:
        # En caso de error, hacer rollback
        conn.rollback()
        raise e
