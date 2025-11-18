#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clase base Persona - Demuestra Herencia y Polimorfismo
Programación Orientada a Objetos - Clase abstracta/base
"""

from abc import ABC, abstractmethod


class Persona(ABC):
    """
    Programación Orientada a Objetos - Clase base abstracta
    Herencia y Polimorfismo - Clase padre para Cliente y Empleado
    """
    
    def __init__(self, nombre, apellido, dni=None, telefono=None, email=None):
        """
        Programación Orientada a Objetos - Constructor
        """
        self._nombre = nombre
        self._apellido = apellido
        self._dni = dni
        self._telefono = telefono
        self._email = email
    
    # Programación Orientada a Objetos - Encapsulación con propiedades
    @property
    def nombre(self):
        return self._nombre
    
    @nombre.setter
    def nombre(self, value):
        self._nombre = value
    
    @property
    def apellido(self):
        return self._apellido
    
    @apellido.setter
    def apellido(self, value):
        self._apellido = value
    
    @property
    def dni(self):
        return self._dni
    
    @dni.setter
    def dni(self, value):
        self._dni = value
    
    @property
    def telefono(self):
        return self._telefono
    
    @telefono.setter
    def telefono(self, value):
        self._telefono = value
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, value):
        self._email = value
    
    def nombre_completo(self):
        """
        Programación Orientada a Objetos - Método polimórfico
        Polimorfismo - Puede ser sobrescrito en clases hijas
        """
        return f"{self._nombre} {self._apellido}"
    
    @abstractmethod
    def tipo_persona(self):
        """
        Herencia y Polimorfismo - Método abstracto que debe implementarse en clases hijas
        """
        pass
    
    def __str__(self):
        """
        Programación Orientada a Objetos - Representación como string
        Polimorfismo - Cada clase puede tener su propia representación
        """
        return f"{self.tipo_persona()}: {self.nombre_completo()}"

