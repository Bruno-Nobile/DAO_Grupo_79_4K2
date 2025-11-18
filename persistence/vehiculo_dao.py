#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DAO para Vehiculo
Persistencia - Implementación del patrón DAO
Herencia y Polimorfismo - Hereda de DAOBase
"""

from persistence.dao_base import DAOBase
from entities.vehiculo import Vehiculo


class VehiculoDAO(DAOBase):
    """
    Persistencia - DAO para la entidad Vehiculo
    Herencia y Polimorfismo - Implementa métodos abstractos de DAOBase
    """
    
    def create(self, vehiculo):
        """
        Persistencia - Crea un nuevo vehículo en la base de datos
        Programación Estructurada - Función bien definida
        """
        query = """INSERT INTO vehiculo (patente, marca, modelo, tipo, costo_diario, 
                   estado, fecha_ultimo_mantenimiento) VALUES (?,?,?,?,?,?,?)"""
        params = (vehiculo.patente, vehiculo.marca, vehiculo.modelo, vehiculo.tipo,
                 vehiculo.costo_diario, vehiculo.estado, vehiculo._fecha_ultimo_mantenimiento)
        
        cursor = self._db.execute_query(query, params)
        self._db.get_connection().commit()
        vehiculo._id_vehiculo = cursor.lastrowid
        return vehiculo
    
    def read(self, id_vehiculo):
        """
        Persistencia - Lee un vehículo por ID
        Programación Estructurada - Función bien definida
        """
        query = "SELECT * FROM vehiculo WHERE id_vehiculo = ?"
        cursor = self._db.execute_query(query, (id_vehiculo,))
        row = cursor.fetchone()
        
        if row:
            return Vehiculo.from_dict(dict(row))
        return None
    
    def update(self, vehiculo):
        """
        Persistencia - Actualiza un vehículo existente
        Programación Estructurada - Función bien definida
        """
        query = """UPDATE vehiculo SET patente=?, marca=?, modelo=?, tipo=?, 
                   costo_diario=?, estado=?, fecha_ultimo_mantenimiento=? 
                   WHERE id_vehiculo=?"""
        params = (vehiculo.patente, vehiculo.marca, vehiculo.modelo, vehiculo.tipo,
                 vehiculo.costo_diario, vehiculo.estado, vehiculo._fecha_ultimo_mantenimiento,
                 vehiculo.id_vehiculo)
        
        self._db.execute_query(query, params)
        self._db.get_connection().commit()
        return vehiculo
    
    def delete(self, id_vehiculo):
        """
        Persistencia - Elimina un vehículo por ID
        Programación Estructurada - Función bien definida
        """
        query = "DELETE FROM vehiculo WHERE id_vehiculo = ?"
        self._db.execute_query(query, (id_vehiculo,))
        self._db.get_connection().commit()
        return True
    
    def list_all(self):
        """
        Persistencia - Lista todos los vehículos
        Programación Funcional - Uso de map para transformar datos
        """
        query = "SELECT * FROM vehiculo ORDER BY marca, modelo"
        cursor = self._db.execute_query(query)
        rows = cursor.fetchall()
        
        # Programación Funcional - map para transformar filas en objetos Vehiculo
        return list(map(lambda row: Vehiculo.from_dict(dict(row)), rows))
    
    def buscar_por_patente(self, patente):
        """
        Persistencia - Busca un vehículo por patente
        Programación Estructurada - Función bien definida
        """
        query = "SELECT * FROM vehiculo WHERE patente = ?"
        cursor = self._db.execute_query(query, (patente.upper(),))
        row = cursor.fetchone()
        
        if row:
            return Vehiculo.from_dict(dict(row))
        return None
    
    def listar_disponibles(self):
        """
        Persistencia - Lista vehículos disponibles
        Programación Funcional - Uso de filter para filtrar datos
        """
        todos = self.list_all()
        # Programación Funcional - filter para obtener solo disponibles
        return list(filter(lambda v: v.esta_disponible(), todos))

