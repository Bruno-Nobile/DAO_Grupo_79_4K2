#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DAO Base - Clase abstracta para DAOs
Persistencia - Patrón DAO (Data Access Object)
Programación Orientada a Objetos - Clase base abstracta
Herencia y Polimorfismo - Clase padre para todos los DAOs
"""

from abc import ABC, abstractmethod
from persistence.database_connection import DatabaseConnection


class DAOBase(ABC):
    """
    Persistencia - Patrón DAO (Data Access Object)
    Programación Orientada a Objetos - Clase base abstracta
    Herencia y Polimorfismo - Clase padre para todos los DAOs
    """
    
    def __init__(self):
        """
        Persistencia - Inicialización del DAO con conexión Singleton
        """
        # Patrón Singleton - Uso de la instancia única de DatabaseConnection
        self._db = DatabaseConnection()
    
    @abstractmethod
    def create(self, entity):
        """
        Persistencia - Método abstracto para crear entidad
        Herencia y Polimorfismo - Debe ser implementado en clases hijas
        """
        pass
    
    @abstractmethod
    def read(self, id):
        """
        Persistencia - Método abstracto para leer entidad
        Herencia y Polimorfismo - Debe ser implementado en clases hijas
        """
        pass
    
    @abstractmethod
    def update(self, entity):
        """
        Persistencia - Método abstracto para actualizar entidad
        Herencia y Polimorfismo - Debe ser implementado en clases hijas
        """
        pass
    
    @abstractmethod
    def delete(self, id):
        """
        Persistencia - Método abstracto para eliminar entidad
        Herencia y Polimorfismo - Debe ser implementado en clases hijas
        """
        pass
    
    @abstractmethod
    def list_all(self):
        """
        Persistencia - Método abstracto para listar todas las entidades
        Herencia y Polimorfismo - Debe ser implementado en clases hijas
        """
        pass

