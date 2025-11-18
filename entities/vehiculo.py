#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clase Vehiculo - Modelo de dominio
Programación Orientada a Objetos - Encapsulación y comportamiento
"""

from datetime import date


class Vehiculo:
    """
    Programación Orientada a Objetos - Clase de entidad
    """
    
    ESTADOS = ['disponible', 'en_mantenimiento', 'inactivo']
    
    def __init__(self, patente, marca=None, modelo=None, tipo=None, 
                 costo_diario=0.0, estado='disponible', 
                 fecha_ultimo_mantenimiento=None, id_vehiculo=None):
        """
        Programación Orientada a Objetos - Constructor
        """
        self._id_vehiculo = id_vehiculo
        self._patente = patente.upper() if patente else None
        self._marca = marca
        self._modelo = modelo
        self._tipo = tipo
        self._costo_diario = float(costo_diario)
        self._estado = estado if estado in self.ESTADOS else 'disponible'
        self._fecha_ultimo_mantenimiento = fecha_ultimo_mantenimiento
    
    # Programación Orientada a Objetos - Encapsulación con propiedades
    @property
    def id_vehiculo(self):
        return self._id_vehiculo
    
    @property
    def patente(self):
        return self._patente
    
    @patente.setter
    def patente(self, value):
        self._patente = value.upper() if value else None
    
    @property
    def marca(self):
        return self._marca
    
    @marca.setter
    def marca(self, value):
        self._marca = value
    
    @property
    def modelo(self):
        return self._modelo
    
    @modelo.setter
    def modelo(self, value):
        self._modelo = value
    
    @property
    def descripcion(self):
        """
        Programación Orientada a Objetos - Propiedad calculada
        """
        return f"{self._patente} - {self._marca} {self._modelo}"
    
    @property
    def costo_diario(self):
        return self._costo_diario
    
    @costo_diario.setter
    def costo_diario(self, value):
        self._costo_diario = float(value)
    
    @property
    def estado(self):
        return self._estado
    
    @estado.setter
    def estado(self, value):
        if value in self.ESTADOS:
            self._estado = value
        else:
            raise ValueError(f"Estado inválido. Debe ser uno de: {self.ESTADOS}")
    
    def esta_disponible(self):
        """
        Programación Orientada a Objetos - Método de comportamiento
        """
        return self._estado == 'disponible'
    
    @classmethod
    def from_dict(cls, data):
        """
        Programación Orientada a Objetos - Método de clase (factory method)
        """
        return cls(
            patente=data.get('patente'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            tipo=data.get('tipo'),
            costo_diario=data.get('costo_diario', 0.0),
            estado=data.get('estado', 'disponible'),
            fecha_ultimo_mantenimiento=data.get('fecha_ultimo_mantenimiento'),
            id_vehiculo=data.get('id_vehiculo')
        )
    
    def to_dict(self):
        """
        Programación Orientada a Objetos - Serialización a diccionario
        """
        return {
            'id_vehiculo': self._id_vehiculo,
            'patente': self._patente,
            'marca': self._marca,
            'modelo': self._modelo,
            'tipo': self._tipo,
            'costo_diario': self._costo_diario,
            'estado': self._estado,
            'fecha_ultimo_mantenimiento': self._fecha_ultimo_mantenimiento
        }
    
    def __str__(self):
        """
        Programación Orientada a Objetos - Representación como string
        """
        return self.descripcion

