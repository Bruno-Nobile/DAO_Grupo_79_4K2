#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Patrón Factory - Creación de objetos
Programación Orientada a Objetos - Patrón creacional
"""

from entities.cliente import Cliente
from entities.empleado import Empleado
from entities.vehiculo import Vehiculo
from entities.alquiler import Alquiler
from persistence.cliente_dao import ClienteDAO
from persistence.dao_base import DAOBase


class EntityFactory:
    """
    Patrón Factory - Factory para crear entidades
    Programación Orientada a Objetos - Encapsula la creación de objetos
    """
    
    @staticmethod
    def create_cliente(nombre, apellido, dni=None, telefono=None, direccion=None, email=None):
        """
        Patrón Factory - Crea una instancia de Cliente
        Programación Orientada a Objetos - Método estático
        """
        return Cliente(nombre, apellido, dni, telefono, direccion, email)
    
    @staticmethod
    def create_empleado(nombre, apellido, dni=None, cargo=None, telefono=None, email=None):
        """
        Patrón Factory - Crea una instancia de Empleado
        Programación Orientada a Objetos - Método estático
        """
        return Empleado(nombre, apellido, dni, cargo, telefono, email)
    
    @staticmethod
    def create_vehiculo(patente, marca=None, modelo=None, tipo=None, 
                       costo_diario=0.0, estado='disponible', 
                       fecha_ultimo_mantenimiento=None):
        """
        Patrón Factory - Crea una instancia de Vehiculo
        Programación Orientada a Objetos - Método estático
        """
        return Vehiculo(patente, marca, modelo, tipo, costo_diario, 
                        estado, fecha_ultimo_mantenimiento)
    
    @staticmethod
    def create_alquiler(fecha_inicio, fecha_fin, id_cliente, id_vehiculo, 
                       id_empleado=None, costo_total=None):
        """
        Patrón Factory - Crea una instancia de Alquiler
        Programación Orientada a Objetos - Método estático
        """
        return Alquiler(fecha_inicio, fecha_fin, id_cliente, id_vehiculo, 
                       id_empleado, costo_total)


class DAOFactory:
    """
    Patrón Factory - Factory para crear DAOs
    Programación Orientada a Objetos - Encapsula la creación de DAOs
    """
    
    _daos = {}
    
    @staticmethod
    def get_cliente_dao():
        """
        Patrón Factory - Obtiene instancia de ClienteDAO (con singleton implícito)
        Programación Orientada a Objetos - Método estático
        """
        if 'cliente' not in DAOFactory._daos:
            DAOFactory._daos['cliente'] = ClienteDAO()
        return DAOFactory._daos['cliente']
    
    @staticmethod
    def get_dao(entity_type):
        """
        Patrón Factory - Obtiene DAO según el tipo de entidad
        Programación Orientada a Objetos - Método genérico
        """
        if entity_type == 'cliente':
            return DAOFactory.get_cliente_dao()
        # Aquí se pueden agregar más tipos de DAOs
        raise ValueError(f"Tipo de DAO no soportado: {entity_type}")

