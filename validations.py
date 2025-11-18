#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de validaciones compartido para el sistema de alquiler de vehículos
"""

import re
from datetime import datetime, date


def validar_dni(dni):
    """Valida que el DNI tenga exactamente 8 dígitos y sean solo números naturales"""
    if not dni:
        return True  # DNI es opcional
    dni_limpio = dni.strip()
    return bool(re.match(r'^\d{8}$', dni_limpio))


def validar_telefono(telefono):
    """Valida que el teléfono contenga solo dígitos naturales"""
    if not telefono:
        return True  # Teléfono es opcional
    telefono_limpio = telefono.strip()
    return bool(re.match(r'^\d+$', telefono_limpio))


def validar_email(email):
    """Valida que el email tenga el formato x@x.com"""
    if not email:
        return True  # Email es opcional
    email_limpio = email.strip()
    return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', email_limpio))


def validar_patente(patente):
    """Valida que la patente siga el formato ABC-123 o AB-123-CD"""
    if not patente:
        return False
    patente_limpia = patente.strip().upper()
    # Formato ABC-123 (3 letras, guión, 3 números)
    formato1 = re.match(r'^[A-Z]{3}-\d{3}$', patente_limpia)
    # Formato AB-123-CD (2 letras, guión, 3 números, guión, 2 letras)
    formato2 = re.match(r'^[A-Z]{2}-\d{3}-[A-Z]{2}$', patente_limpia)
    return bool(formato1 or formato2)


def validar_fecha_mantenimiento(fecha_str):
    """Valida que la fecha de mantenimiento no supere la fecha actual"""
    if not fecha_str:
        return True  # Fecha es opcional
    fecha_limpia = fecha_str.strip()
    try:
        fecha_mant = datetime.strptime(fecha_limpia, '%Y-%m-%d').date()
        fecha_actual = date.today()
        return fecha_mant <= fecha_actual
    except ValueError:
        return False


def validar_fecha_inicio_alquiler(fecha_str):
    """Valida que la fecha de inicio sea mayor a la fecha actual"""
    if not fecha_str:
        return False
    fecha_limpia = fecha_str.strip()
    try:
        fecha_inicio = datetime.strptime(fecha_limpia, '%Y-%m-%d').date()
        fecha_actual = date.today()
        return fecha_inicio > fecha_actual
    except ValueError:
        return False

