#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DAO para Empleado
Persistencia - Implementación del patrón DAO
Herencia y Polimorfismo - Hereda de DAOBase
"""

from persistence.dao_base import DAOBase
from entities.empleado import Empleado


class EmpleadoDAO(DAOBase):
    """
    Persistencia - DAO para la entidad Empleado
    Herencia y Polimorfismo - Implementa métodos abstractos de DAOBase
    """
    
    def create(self, empleado):
        """
        Persistencia - Crea un nuevo empleado en la base de datos
        Programación Estructurada - Función bien definida
        """
        query = """INSERT INTO empleado (nombre, apellido, dni, cargo, telefono, email) 
                   VALUES (?,?,?,?,?,?)"""
        params = (empleado.nombre, empleado.apellido, empleado.dni,
                 empleado.cargo, empleado.telefono, empleado.email)
        
        cursor = self._db.execute_query(query, params)
        self._db.get_connection().commit()
        empleado._id_empleado = cursor.lastrowid
        return empleado
    
    def read(self, id_empleado):
        """
        Persistencia - Lee un empleado por ID
        Programación Estructurada - Función bien definida
        """
        query = "SELECT * FROM empleado WHERE id_empleado = ?"
        cursor = self._db.execute_query(query, (id_empleado,))
        row = cursor.fetchone()
        
        if row:
            return Empleado.from_dict(dict(row))
        return None
    
    def update(self, empleado):
        """
        Persistencia - Actualiza un empleado existente
        Programación Estructurada - Función bien definida
        """
        query = """UPDATE empleado SET nombre=?, apellido=?, dni=?, cargo=?, 
                   telefono=?, email=? WHERE id_empleado=?"""
        params = (empleado.nombre, empleado.apellido, empleado.dni,
                 empleado.cargo, empleado.telefono, empleado.email, empleado.id_empleado)
        
        self._db.execute_query(query, params)
        self._db.get_connection().commit()
        return empleado
    
    def delete(self, id_empleado):
        """
        Persistencia - Elimina un empleado por ID
        Programación Estructurada - Función bien definida
        """
        query = "DELETE FROM empleado WHERE id_empleado = ?"
        self._db.execute_query(query, (id_empleado,))
        self._db.get_connection().commit()
        return True
    
    def list_all(self):
        """
        Persistencia - Lista todos los empleados
        Programación Funcional - Uso de map para transformar datos
        """
        query = "SELECT * FROM empleado ORDER BY apellido, nombre"
        cursor = self._db.execute_query(query)
        rows = cursor.fetchall()
        
        # Programación Funcional - map para transformar filas en objetos Empleado
        return list(map(lambda row: Empleado.from_dict(dict(row)), rows))

