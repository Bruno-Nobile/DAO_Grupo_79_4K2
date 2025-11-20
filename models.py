#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de lógica de negocio para el sistema de alquiler de vehículos
"""

from datetime import datetime, date
from database import get_connection


def calcular_costo(costo_diario, fecha_inicio_str, fecha_fin_str):
    """Calcula el costo total basado en los días (inclusive)"""
    fi = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    ff = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    dias = (ff - fi).days + 1
    
    if dias < 1:
        raise ValueError("La fecha de fin debe ser igual o posterior a la fecha de inicio.")
    
    return round(dias * costo_diario, 2)


def vehiculo_en_mantenimiento(id_vehiculo, fecha_inicio_str, fecha_fin_str):
    """
    Verifica si el vehículo está en mantenimiento en el período especificado
    Programación Estructurada - Función bien organizada
    """
    conn = get_connection()
    c = conn.cursor()
    
    query = """
    SELECT COUNT(*) FROM mantenimiento
    WHERE id_vehiculo = ?
      AND NOT (date(fecha_fin) < date(?) OR date(fecha_inicio) > date(?))
    """
    # Si existe un mantenimiento cuyo rango NO está completamente fuera del período deseado => está solapado
    c.execute(query, (id_vehiculo, fecha_inicio_str, fecha_fin_str))
    cnt = c.fetchone()[0]
    
    # No cerrar la conexión aquí - el Singleton la maneja por thread
    # conn.close()  # Removido para evitar cerrar conexión compartida
    return cnt > 0


def vehiculo_disponible(id_vehiculo, fecha_inicio_str, fecha_fin_str):
    """
    Verifica si el vehículo no tiene alquileres solapados ni mantenimientos en ese período
    Programación Estructurada - Función bien organizada
    """
    conn = get_connection()
    c = conn.cursor()
    
    # Verificar alquileres solapados
    query_alquileres = """
    SELECT COUNT(*) FROM alquiler
    WHERE id_vehiculo = ?
      AND NOT (date(fecha_fin) < date(?) OR date(fecha_inicio) > date(?))
    """
    c.execute(query_alquileres, (id_vehiculo, fecha_inicio_str, fecha_fin_str))
    cnt_alquileres = c.fetchone()[0]
    
    # Verificar mantenimientos solapados
    query_mantenimientos = """
    SELECT COUNT(*) FROM mantenimiento
    WHERE id_vehiculo = ?
      AND NOT (date(fecha_fin) < date(?) OR date(fecha_inicio) > date(?))
    """
    c.execute(query_mantenimientos, (id_vehiculo, fecha_inicio_str, fecha_fin_str))
    cnt_mantenimientos = c.fetchone()[0]
    
    # No cerrar la conexión aquí - el Singleton la maneja por thread
    # conn.close()  # Removido para evitar cerrar conexión compartida
    return cnt_alquileres == 0 and cnt_mantenimientos == 0


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
        
        # Verificar disponibilidad temporal (no tiene alquileres solapados ni mantenimientos)
        if not vehiculo_disponible(id_vehiculo, fecha_inicio, fecha_fin):
            # Verificar si es por alquileres o mantenimientos
            if vehiculo_en_mantenimiento(id_vehiculo, fecha_inicio, fecha_fin):
                raise ValueError("Vehículo no disponible en el periodo indicado. "
                               f"El vehículo está en mantenimiento en ese rango de fechas.")
            else:
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
        
        # Actualizar estado del vehículo solo si el alquiler ya comenzó (fecha_inicio <= fecha_actual)
        # Si es una fecha futura, el estado se actualizará automáticamente cuando llegue la fecha
        fecha_inicio_date = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_actual = date.today()
        
        if fecha_inicio_date <= fecha_actual:
            # El alquiler ya comenzó o comienza hoy, marcar como "Alquilado"
            c.execute("UPDATE vehiculo SET estado = 'Alquilado' WHERE id_vehiculo = ?", (id_vehiculo,))
        # Si fecha_inicio_date > fecha_actual, el vehículo permanece "Disponible"
        # y se actualizará automáticamente cuando llegue la fecha de inicio
        
        conn.commit()
        # No cerrar la conexión - el Singleton la maneja por thread
        # conn.close()  # Removido - el Singleton maneja el ciclo de vida
        return True
    except Exception as e:
        # En caso de error, hacer rollback
        conn.rollback()
        raise e


def actualizar_estados_vehiculos(fecha_referencia=None):
    """
    Actualiza el estado de los vehículos basándose en si tienen alquileres activos o mantenimientos activos.
    Si un vehículo tiene mantenimientos que ya terminaron, lo marca como Disponible (si no tiene alquileres).
    Si un vehículo tiene mantenimientos activos, lo marca como Mantenimiento.
    
    Args:
        fecha_referencia: Fecha a usar como referencia (por defecto, fecha actual).
                         Útil para testing. Formato: 'YYYY-MM-DD' o objeto date.
    
    Returns:
        dict: Información sobre los cambios realizados
    """
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # Determinar fecha de referencia
        if fecha_referencia is None:
            fecha_ref = date.today()
        elif isinstance(fecha_referencia, str):
            fecha_ref = datetime.strptime(fecha_referencia, "%Y-%m-%d").date()
        else:
            fecha_ref = fecha_referencia
        
        fecha_ref_str = fecha_ref.strftime("%Y-%m-%d")
        
        cambios = {
            'a_disponible': [],
            'a_alquilado': [],
            'a_mantenimiento': [],
            'sin_cambios': []
        }
        
        # Obtener todos los vehículos
        c.execute("SELECT id_vehiculo, patente, marca, modelo, estado FROM vehiculo")
        vehiculos = c.fetchall()
        
        for vehiculo in vehiculos:
            id_vehiculo = vehiculo["id_vehiculo"]
            patente = vehiculo["patente"]
            marca = vehiculo["marca"]
            modelo = vehiculo["modelo"]
            estado_actual = vehiculo["estado"]
            
            # Verificar si tiene alquileres activos
            # Un alquiler está activo si: fecha_inicio <= fecha_referencia <= fecha_fin
            # Es decir, el alquiler ya comenzó y aún no terminó
            c.execute("""
                SELECT COUNT(*) FROM alquiler 
                WHERE id_vehiculo = ? 
                AND date(fecha_inicio) <= date(?)
                AND date(fecha_fin) >= date(?)
            """, (id_vehiculo, fecha_ref_str, fecha_ref_str))
            
            alquileres_activos = c.fetchone()[0]
            
            # Verificar si está en mantenimiento activo (fecha_fin >= fecha_referencia)
            c.execute("""
                SELECT COUNT(*) FROM mantenimiento 
                WHERE id_vehiculo = ?
                AND date(fecha_fin) >= date(?)
            """, (id_vehiculo, fecha_ref_str))
            mantenimientos_activos = c.fetchone()[0]
            
            # Determinar el estado que debería tener
            if alquileres_activos > 0:
                estado_deberia = "Alquilado"
            elif mantenimientos_activos > 0:
                estado_deberia = "Mantenimiento"
            else:
                estado_deberia = "Disponible"
            
            # Actualizar si es necesario
            if estado_actual != estado_deberia:
                c.execute("UPDATE vehiculo SET estado = ? WHERE id_vehiculo = ?", 
                         (estado_deberia, id_vehiculo))
                
                info_vehiculo = f"{patente} - {marca} {modelo} (ID: {id_vehiculo})"
                cambio = {
                    'vehiculo': info_vehiculo,
                    'estado_anterior': estado_actual,
                    'estado_nuevo': estado_deberia,
                    'alquileres_activos': alquileres_activos,
                    'mantenimientos_activos': mantenimientos_activos
                }
                
                if estado_deberia == "Disponible":
                    cambios['a_disponible'].append(cambio)
                elif estado_deberia == "Alquilado":
                    cambios['a_alquilado'].append(cambio)
                elif estado_deberia == "Mantenimiento":
                    cambios['a_mantenimiento'].append(cambio)
            else:
                info_vehiculo = f"{patente} - {marca} {modelo} (ID: {id_vehiculo})"
                cambios['sin_cambios'].append({
                    'vehiculo': info_vehiculo,
                    'estado': estado_actual,
                    'alquileres_activos': alquileres_activos,
                    'mantenimientos_activos': mantenimientos_activos
                })
        
        conn.commit()
        return cambios
        
    except Exception as e:
        conn.rollback()
        raise e
