#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de entidades del dominio
Programación Orientada a Objetos - Modelado de entidades del negocio
"""

from .persona import Persona
from .cliente import Cliente
from .empleado import Empleado
from .vehiculo import Vehiculo
from .alquiler import Alquiler

__all__ = ['Persona', 'Cliente', 'Empleado', 'Vehiculo', 'Alquiler']

