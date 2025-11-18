#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clase Alquiler - Modelo de dominio
Programación Orientada a Objetos - Encapsulación y comportamiento
"""

from datetime import datetime, date


class Alquiler:
    """
    Programación Orientada a Objetos - Clase de entidad
    """
    
    def __init__(self, fecha_inicio, fecha_fin, id_cliente, id_vehiculo,
                 id_empleado=None, costo_total=None, id_alquiler=None, 
                 fecha_registro=None):
        """
        Programación Orientada a Objetos - Constructor
        """
        self._id_alquiler = id_alquiler
        self._fecha_inicio = fecha_inicio if isinstance(fecha_inicio, date) else datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        self._fecha_fin = fecha_fin if isinstance(fecha_fin, date) else datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        self._id_cliente = id_cliente
        self._id_vehiculo = id_vehiculo
        self._id_empleado = id_empleado
        self._costo_total = costo_total
        self._fecha_registro = fecha_registro or date.today()
    
    # Programación Orientada a Objetos - Encapsulación con propiedades
    @property
    def id_alquiler(self):
        return self._id_alquiler
    
    @property
    def fecha_inicio(self):
        return self._fecha_inicio
    
    @property
    def fecha_fin(self):
        return self._fecha_fin
    
    @property
    def id_cliente(self):
        return self._id_cliente
    
    @property
    def id_vehiculo(self):
        return self._id_vehiculo
    
    @property
    def id_empleado(self):
        return self._id_empleado
    
    @property
    def costo_total(self):
        return self._costo_total
    
    @property
    def fecha_registro(self):
        return self._fecha_registro
    
    def calcular_dias(self):
        """
        Programación Orientada a Objetos - Método de comportamiento
        """
        return (self._fecha_fin - self._fecha_inicio).days + 1
    
    def calcular_costo(self, costo_diario):
        """
        Programación Orientada a Objetos - Método de comportamiento
        """
        dias = self.calcular_dias()
        return round(dias * costo_diario, 2)
    
    @classmethod
    def from_dict(cls, data):
        """
        Programación Orientada a Objetos - Método de clase (factory method)
        """
        return cls(
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin=data.get('fecha_fin'),
            id_cliente=data.get('id_cliente'),
            id_vehiculo=data.get('id_vehiculo'),
            id_empleado=data.get('id_empleado'),
            costo_total=data.get('costo_total'),
            id_alquiler=data.get('id_alquiler'),
            fecha_registro=data.get('fecha_registro')
        )
    
    def to_dict(self):
        """
        Programación Orientada a Objetos - Serialización a diccionario
        """
        return {
            'id_alquiler': self._id_alquiler,
            'fecha_inicio': self._fecha_inicio.strftime("%Y-%m-%d") if isinstance(self._fecha_inicio, date) else self._fecha_inicio,
            'fecha_fin': self._fecha_fin.strftime("%Y-%m-%d") if isinstance(self._fecha_fin, date) else self._fecha_fin,
            'id_cliente': self._id_cliente,
            'id_vehiculo': self._id_vehiculo,
            'id_empleado': self._id_empleado,
            'costo_total': self._costo_total,
            'fecha_registro': self._fecha_registro.strftime("%Y-%m-%d") if isinstance(self._fecha_registro, date) else self._fecha_registro
        }

