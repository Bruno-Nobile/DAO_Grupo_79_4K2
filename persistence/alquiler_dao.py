#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DAO para Alquiler
Persistencia - Implementación del patrón DAO
Herencia y Polimorfismo - Hereda de DAOBase
"""

from persistence.dao_base import DAOBase
from entities.alquiler import Alquiler
from datetime import date


class AlquilerDAO(DAOBase):
    """
    Persistencia - DAO para la entidad Alquiler
    Herencia y Polimorfismo - Implementa métodos abstractos de DAOBase
    """
    
    def create(self, alquiler):
        """
        Persistencia - Crea un nuevo alquiler en la base de datos
        Programación Estructurada - Función bien definida
        """
        fecha_inicio_str = alquiler.fecha_inicio.strftime("%Y-%m-%d") if isinstance(alquiler.fecha_inicio, date) else alquiler.fecha_inicio
        fecha_fin_str = alquiler.fecha_fin.strftime("%Y-%m-%d") if isinstance(alquiler.fecha_fin, date) else alquiler.fecha_fin
        
        query = """INSERT INTO alquiler (fecha_inicio, fecha_fin, costo_total, 
                   id_cliente, id_vehiculo, id_empleado) VALUES (?,?,?,?,?,?)"""
        params = (fecha_inicio_str, fecha_fin_str, alquiler.costo_total,
                 alquiler.id_cliente, alquiler.id_vehiculo, alquiler.id_empleado)
        
        cursor = self._db.execute_query(query, params)
        self._db.get_connection().commit()
        alquiler._id_alquiler = cursor.lastrowid
        return alquiler
    
    def read(self, id_alquiler):
        """
        Persistencia - Lee un alquiler por ID
        Programación Estructurada - Función bien definida
        """
        query = "SELECT * FROM alquiler WHERE id_alquiler = ?"
        cursor = self._db.execute_query(query, (id_alquiler,))
        row = cursor.fetchone()
        
        if row:
            return Alquiler.from_dict(dict(row))
        return None
    
    def update(self, alquiler):
        """
        Persistencia - Actualiza un alquiler existente
        Programación Estructurada - Función bien definida
        """
        fecha_inicio_str = alquiler.fecha_inicio.strftime("%Y-%m-%d") if isinstance(alquiler.fecha_inicio, date) else alquiler.fecha_inicio
        fecha_fin_str = alquiler.fecha_fin.strftime("%Y-%m-%d") if isinstance(alquiler.fecha_fin, date) else alquiler.fecha_fin
        
        query = """UPDATE alquiler SET fecha_inicio=?, fecha_fin=?, costo_total=?, 
                   id_cliente=?, id_vehiculo=?, id_empleado=? WHERE id_alquiler=?"""
        params = (fecha_inicio_str, fecha_fin_str, alquiler.costo_total,
                 alquiler.id_cliente, alquiler.id_vehiculo, alquiler.id_empleado,
                 alquiler.id_alquiler)
        
        self._db.execute_query(query, params)
        self._db.get_connection().commit()
        return alquiler
    
    def delete(self, id_alquiler):
        """
        Persistencia - Elimina un alquiler por ID
        Programación Estructurada - Función bien definida
        """
        query = "DELETE FROM alquiler WHERE id_alquiler = ?"
        self._db.execute_query(query, (id_alquiler,))
        self._db.get_connection().commit()
        return True
    
    def list_all(self):
        """
        Persistencia - Lista todos los alquileres
        Programación Funcional - Uso de map para transformar datos
        """
        query = """SELECT * FROM alquiler ORDER BY fecha_inicio DESC"""
        cursor = self._db.execute_query(query)
        rows = cursor.fetchall()
        
        # Programación Funcional - map para transformar filas en objetos Alquiler
        return list(map(lambda row: Alquiler.from_dict(dict(row)), rows))
    
    def verificar_disponibilidad(self, id_vehiculo, fecha_inicio, fecha_fin):
        """
        Persistencia - Verifica si un vehículo está disponible en un período
        Programación Funcional - Uso de filter para verificar solapamientos
        """
        fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d") if isinstance(fecha_inicio, date) else fecha_inicio
        fecha_fin_str = fecha_fin.strftime("%Y-%m-%d") if isinstance(fecha_fin, date) else fecha_fin
        
        query = """SELECT * FROM alquiler 
                   WHERE id_vehiculo = ? 
                   AND NOT (date(fecha_fin) < date(?) OR date(fecha_inicio) > date(?))"""
        cursor = self._db.execute_query(query, (id_vehiculo, fecha_inicio_str, fecha_fin_str))
        rows = cursor.fetchall()
        
        # Programación Funcional - Verificar si hay solapamientos
        return len(rows) == 0

