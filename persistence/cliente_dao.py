#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DAO para Cliente
Persistencia - Implementación del patrón DAO
Herencia y Polimorfismo - Hereda de DAOBase
"""

from persistence.dao_base import DAOBase
from entities.cliente import Cliente


class ClienteDAO(DAOBase):
    """
    Persistencia - DAO para la entidad Cliente
    Herencia y Polimorfismo - Implementa métodos abstractos de DAOBase
    """
    
    def create(self, cliente):
        """
        Persistencia - Crea un nuevo cliente en la base de datos
        Programación Estructurada - Función bien definida
        """
        query = """INSERT INTO cliente (nombre, apellido, dni, telefono, direccion, email) 
                   VALUES (?,?,?,?,?,?)"""
        params = (cliente.nombre, cliente.apellido, cliente.dni, 
                 cliente.telefono, cliente.direccion, cliente.email)
        
        cursor = self._db.execute_query(query, params)
        self._db.get_connection().commit()
        cliente._id_cliente = cursor.lastrowid
        return cliente
    
    def read(self, id_cliente):
        """
        Persistencia - Lee un cliente por ID
        Programación Estructurada - Función bien definida
        """
        query = "SELECT * FROM cliente WHERE id_cliente = ?"
        cursor = self._db.execute_query(query, (id_cliente,))
        row = cursor.fetchone()
        
        if row:
            return Cliente.from_dict(dict(row))
        return None
    
    def update(self, cliente):
        """
        Persistencia - Actualiza un cliente existente
        Programación Estructurada - Función bien definida
        """
        query = """UPDATE cliente SET nombre=?, apellido=?, dni=?, telefono=?, 
                   direccion=?, email=? WHERE id_cliente=?"""
        params = (cliente.nombre, cliente.apellido, cliente.dni,
                 cliente.telefono, cliente.direccion, cliente.email, cliente.id_cliente)
        
        self._db.execute_query(query, params)
        self._db.get_connection().commit()
        return cliente
    
    def delete(self, id_cliente):
        """
        Persistencia - Elimina un cliente por ID
        Programación Estructurada - Función bien definida
        """
        query = "DELETE FROM cliente WHERE id_cliente = ?"
        self._db.execute_query(query, (id_cliente,))
        self._db.get_connection().commit()
        return True
    
    def list_all(self):
        """
        Persistencia - Lista todos los clientes
        Programación Funcional - Uso de map para transformar datos
        """
        query = "SELECT * FROM cliente ORDER BY apellido, nombre"
        cursor = self._db.execute_query(query)
        rows = cursor.fetchall()
        
        # Programación Funcional - map para transformar filas en objetos Cliente
        return list(map(lambda row: Cliente.from_dict(dict(row)), rows))

