#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clase Cliente - Demuestra Herencia
Programación Orientada a Objetos - Clase hija de Persona
"""

from .persona import Persona


class Cliente(Persona):
    """
    Programación Orientada a Objetos - Clase hija
    Herencia y Polimorfismo - Hereda de Persona y sobrescribe métodos
    """
    
    def __init__(self, nombre, apellido, dni=None, telefono=None, direccion=None, email=None, id_cliente=None):
        """
        Herencia y Polimorfismo - Constructor que llama al padre
        """
        super().__init__(nombre, apellido, dni, telefono, email)
        self._direccion = direccion
        self._id_cliente = id_cliente
    
    @property
    def id_cliente(self):
        return self._id_cliente
    
    @property
    def direccion(self):
        return self._direccion
    
    @direccion.setter
    def direccion(self, value):
        self._direccion = value
    
    def tipo_persona(self):
        """
        Herencia y Polimorfismo - Implementación del método abstracto
        Polimorfismo - Cada clase hija implementa su propia versión
        """
        return "Cliente"
    
    @classmethod
    def from_dict(cls, data):
        """
        Programación Orientada a Objetos - Método de clase (factory method)
        """
        return cls(
            nombre=data.get('nombre'),
            apellido=data.get('apellido'),
            dni=data.get('dni'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            email=data.get('email'),
            id_cliente=data.get('id_cliente')
        )
    
    def to_dict(self):
        """
        Programación Orientada a Objetos - Serialización a diccionario
        """
        return {
            'id_cliente': self._id_cliente,
            'nombre': self._nombre,
            'apellido': self._apellido,
            'dni': self._dni,
            'telefono': self._telefono,
            'direccion': self._direccion,
            'email': self._email
        }

