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
    """
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # Obtener costo diario del vehículo
        c.execute("SELECT costo_diario FROM vehiculo WHERE id_vehiculo = ?", (id_vehiculo,))
        row = c.fetchone()
        
        if not row:
            raise ValueError("Vehículo no encontrado.")
        
        costo_diario = row["costo_diario"]
        
        # Verificar disponibilidad (no cierra la conexión)
        if not vehiculo_disponible(id_vehiculo, fecha_inicio, fecha_fin):
            raise ValueError("Vehículo no disponible en el periodo indicado.")
        
        # Calcular costo total
        costo_total = calcular_costo(costo_diario, fecha_inicio, fecha_fin)
        
        # Insertar alquiler
        c.execute(
            """INSERT INTO alquiler (fecha_inicio, fecha_fin, costo_total, id_cliente, id_vehiculo, id_empleado)
               VALUES (?,?,?,?,?,?)""",
            (fecha_inicio, fecha_fin, costo_total, id_cliente, id_vehiculo, id_empleado)
        )
        
        conn.commit()
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido - el Singleton maneja el ciclo de vida
        return True
    except Exception as e:
        # En caso de error, hacer rollback
        conn.rollback()
        raise e
