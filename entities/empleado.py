#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clase Empleado - Demuestra Herencia
Programación Orientada a Objetos - Clase hija de Persona
"""

from .persona import Persona


class Empleado(Persona):
    """
    Programación Orientada a Objetos - Clase hija
    Herencia y Polimorfismo - Hereda de Persona y sobrescribe métodos
    """
    
    def __init__(self, nombre, apellido, dni=None, cargo=None, telefono=None, email=None, id_empleado=None):
        """
        Herencia y Polimorfismo - Constructor que llama al padre
        """
        super().__init__(nombre, apellido, dni, telefono, email)
        self._cargo = cargo
        self._id_empleado = id_empleado
    
    @property
    def id_empleado(self):
        return self._id_empleado
    
    @property
    def cargo(self):
        return self._cargo
    
    @cargo.setter
    def cargo(self, value):
        self._cargo = value
    
    def tipo_persona(self):
        """
        Herencia y Polimorfismo - Implementación del método abstracto
        Polimorfismo - Cada clase hija implementa su propia versión
        """
        return "Empleado"
    
    @classmethod
    def from_dict(cls, data):
        """
        Programación Orientada a Objetos - Método de clase (factory method)
        """
        return cls(
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            dni=data.get('dni'),
            cargo=data.get('cargo'),
            telefono=data.get('telefono'),
            email=data.get('email'),
            id_empleado=data.get('id_empleado')
        )
    
    def to_dict(self):
        """
        Programación Orientada a Objetos - Serialización a diccionario
        """
        return {
            'id_empleado': self._id_empleado,
            'nombre': self._nombre,
            'apellido': self._apellido,
            'dni': self._dni,
            'cargo': self._cargo,
            'telefono': self._telefono,
            'email': self._email
        }

