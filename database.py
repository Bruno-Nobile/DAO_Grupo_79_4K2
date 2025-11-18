#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de base de datos para el sistema de alquiler de vehículos
Programación Estructurada - Funciones bien organizadas
Compatibilidad - Mantiene funciones legacy para compatibilidad con código existente
"""

import sqlite3
from config import DB_FILE

# Patrón Singleton - Importar la nueva implementación
from persistence.database_connection import DatabaseConnection


def get_connection():
    """
    Obtiene una conexión a la base de datos
    Programación Estructurada - Función de compatibilidad
    Patrón Singleton - Usa la instancia única de DatabaseConnection
    """
    # Patrón Singleton - Obtener instancia única
    db = DatabaseConnection()
    return db.get_connection()


def init_db():
    """
    Inicializa la base de datos con las tablas necesarias
    Programación Estructurada - Función bien organizada
    """
    # Crear conexión temporal para inicialización (no usar Singleton para evitar conflictos)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Activar claves foráneas
    c.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS cliente (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        dni TEXT UNIQUE,
        telefono TEXT,
        direccion TEXT,
        email TEXT
    );

    CREATE TABLE IF NOT EXISTS empleado (
        id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        dni TEXT UNIQUE,
        cargo TEXT,
        telefono TEXT,
        email TEXT
    );

    CREATE TABLE IF NOT EXISTS vehiculo (
        id_vehiculo INTEGER PRIMARY KEY AUTOINCREMENT,
        patente TEXT UNIQUE NOT NULL,
        marca TEXT,
        modelo TEXT,
        tipo TEXT,
        costo_diario REAL NOT NULL DEFAULT 0,
        estado TEXT DEFAULT 'disponible',
        fecha_ultimo_mantenimiento TEXT
    );

    CREATE TABLE IF NOT EXISTS alquiler (
        id_alquiler INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        costo_total REAL NOT NULL,
        id_cliente INTEGER NOT NULL,
        id_vehiculo INTEGER NOT NULL,
        id_empleado INTEGER,
        fecha_registro TEXT NOT NULL DEFAULT (date('now')),
        FOREIGN KEY(id_cliente) REFERENCES cliente(id_cliente) ON DELETE RESTRICT,
        FOREIGN KEY(id_vehiculo) REFERENCES vehiculo(id_vehiculo) ON DELETE RESTRICT,
        FOREIGN KEY(id_empleado) REFERENCES empleado(id_empleado) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS multa (
        id_multa INTEGER PRIMARY KEY AUTOINCREMENT,
        descripcion TEXT,
        monto REAL,
        id_alquiler INTEGER NOT NULL,
        FOREIGN KEY(id_alquiler) REFERENCES alquiler(id_alquiler) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS mantenimiento (
        id_mant INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        fecha TEXT NOT NULL,
        costo REAL,
        id_vehiculo INTEGER NOT NULL,
        observaciones TEXT,
        FOREIGN KEY(id_vehiculo) REFERENCES vehiculo(id_vehiculo) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()


def seed_sample_data():
    """
    Inserta datos de prueba si la base de datos está vacía
    Programación Estructurada - Función bien organizada
    """
    # Crear conexión temporal para seed (no usar Singleton para evitar conflictos)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Insertar clientes de prueba
    c.execute("SELECT COUNT(*) FROM cliente")
    if c.fetchone()[0] == 0:
        clientes = [
            ("Lucas", "González", "12345678", "3415550001", "Córdoba", "lucas@example.com"),
            ("María", "Pérez", "23456789", "3415550002", "Córdoba", "maria@example.com"),
        ]
        c.executemany(
            "INSERT INTO cliente (nombre, apellido, dni, telefono, direccion, email) VALUES (?,?,?,?,?,?)",
            clientes
        )

    # Insertar empleados de prueba
    c.execute("SELECT COUNT(*) FROM empleado")
    if c.fetchone()[0] == 0:
        empleados = [
            ("Admin", "Local", "99999999", "Administrador", "3415551000", "admin@example.com"),
        ]
        c.executemany(
            "INSERT INTO empleado (nombre, apellido, dni, cargo, telefono, email) VALUES (?,?,?,?,?,?)",
            empleados
        )

    # Insertar vehículos de prueba
    c.execute("SELECT COUNT(*) FROM vehiculo")
    if c.fetchone()[0] == 0:
        vehiculos = [
            ("ABC123", "Toyota", "Corolla", "Sedan", 5000.0, "disponible", None),
            ("DEF456", "Volkswagen", "Gol", "Hatchback", 3500.0, "disponible", None),
            ("GHI789", "Ford", "Ranger", "PickUp", 8000.0, "disponible", None),
        ]
        c.executemany(
            "INSERT INTO vehiculo (patente, marca, modelo, tipo, costo_diario, estado, fecha_ultimo_mantenimiento) VALUES (?,?,?,?,?,?,?)",
            vehiculos
        )

    conn.commit()
    conn.close()
