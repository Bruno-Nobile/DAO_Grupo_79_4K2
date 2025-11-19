#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de base de datos para el sistema de alquiler de vehículos
Programación Estructurada - Funciones bien organizadas
Compatibilidad - Mantiene funciones legacy para compatibilidad con código existente
"""

import sqlite3
from datetime import datetime, timedelta
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
    Inserta datos de prueba si la base de datos está vacía o tiene pocos datos
    Programación Estructurada - Función bien organizada
    """
    # Crear conexión temporal para seed (no usar Singleton para evitar conflictos)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Insertar clientes de prueba (si hay menos de 8)
    c.execute("SELECT COUNT(*) FROM cliente")
    count_clientes = c.fetchone()[0]
    if count_clientes < 8:
        todos_clientes = [
            ("Lucas", "González", "12345678", "3415550001", "Av. Colón 1234, Córdoba", "lucas@example.com"),
            ("María", "Pérez", "23456789", "3415550002", "San Martín 567, Córdoba", "maria@example.com"),
            ("Juan", "Martínez", "34567890", "3415550003", "Belgrano 890, Córdoba", "juan@example.com"),
            ("Ana", "Rodríguez", "45678901", "3415550004", "Rivadavia 234, Córdoba", "ana@example.com"),
            ("Carlos", "López", "56789012", "3415550005", "Mitre 456, Córdoba", "carlos@example.com"),
            ("Laura", "Fernández", "67890123", "3415550006", "25 de Mayo 789, Córdoba", "laura@example.com"),
            ("Pedro", "García", "78901234", "3415550007", "Independencia 321, Córdoba", "pedro@example.com"),
            ("Sofía", "Torres", "89012345", "3415550008", "Chacabuco 654, Córdoba", "sofia@example.com"),
        ]
        # Solo insertar los que faltan
        clientes_a_insertar = todos_clientes[count_clientes:]
        if clientes_a_insertar:
            c.executemany(
                "INSERT INTO cliente (nombre, apellido, dni, telefono, direccion, email) VALUES (?,?,?,?,?,?)",
                clientes_a_insertar
            )

    # Insertar empleados de prueba (si hay menos de 4)
    c.execute("SELECT COUNT(*) FROM empleado")
    count_empleados = c.fetchone()[0]
    if count_empleados < 4:
        todos_empleados = [
            ("Admin", "Local", "99999999", "Administrador", "3415551000", "admin@example.com"),
            ("Roberto", "Sánchez", "11111111", "Vendedor", "3415551001", "roberto@example.com"),
            ("Carmen", "Díaz", "22222222", "Vendedor", "3415551002", "carmen@example.com"),
            ("Miguel", "Ruiz", "33333333", "Gerente", "3415551003", "miguel@example.com"),
        ]
        # Solo insertar los que faltan
        empleados_a_insertar = todos_empleados[count_empleados:]
        if empleados_a_insertar:
            c.executemany(
                "INSERT INTO empleado (nombre, apellido, dni, cargo, telefono, email) VALUES (?,?,?,?,?,?)",
                empleados_a_insertar
            )

    # Insertar vehículos de prueba (si hay menos de 10)
    c.execute("SELECT COUNT(*) FROM vehiculo")
    count_vehiculos = c.fetchone()[0]
    if count_vehiculos < 10:
        todos_vehiculos = [
            ("ABC123", "Toyota", "Corolla", "Sedan", 5000.0, "disponible", "2024-10-15"),
            ("DEF456", "Volkswagen", "Gol", "Hatchback", 3500.0, "disponible", "2024-11-01"),
            ("GHI789", "Ford", "Ranger", "PickUp", 8000.0, "disponible", "2024-09-20"),
            ("JKL012", "Chevrolet", "Onix", "Sedan", 4500.0, "disponible", "2024-10-05"),
            ("MNO345", "Fiat", "Cronos", "Sedan", 4200.0, "disponible", "2024-11-10"),
            ("PQR678", "Renault", "Kwid", "Hatchback", 3200.0, "disponible", "2024-10-25"),
            ("STU901", "Peugeot", "208", "Hatchback", 4800.0, "disponible", "2024-09-15"),
            ("VWX234", "Nissan", "Frontier", "PickUp", 7500.0, "disponible", "2024-11-05"),
            ("YZA567", "Honda", "Civic", "Sedan", 5500.0, "disponible", "2024-10-20"),
            ("BCD890", "Hyundai", "HB20", "Hatchback", 4000.0, "disponible", "2024-09-30"),
        ]
        # Solo insertar los que faltan
        vehiculos_a_insertar = todos_vehiculos[count_vehiculos:]
        if vehiculos_a_insertar:
            c.executemany(
                "INSERT INTO vehiculo (patente, marca, modelo, tipo, costo_diario, estado, fecha_ultimo_mantenimiento) VALUES (?,?,?,?,?,?,?)",
                vehiculos_a_insertar
            )

    # Insertar alquileres de prueba (distribuidos en varios meses) si hay menos de 30
    c.execute("SELECT COUNT(*) FROM alquiler")
    count_alquileres = c.fetchone()[0]
    if count_alquileres < 30:
        # Obtener IDs de clientes, vehículos y empleados
        c.execute("SELECT id_cliente FROM cliente")
        cliente_ids = [row[0] for row in c.fetchall()]
        
        c.execute("SELECT id_vehiculo FROM vehiculo")
        vehiculo_ids = [row[0] for row in c.fetchall()]
        
        c.execute("SELECT id_empleado FROM empleado")
        empleado_ids = [row[0] for row in c.fetchall()]
        
        # Generar alquileres en diferentes meses
        hoy = datetime.now()
        alquileres = []
        alquileres_necesarios = 30 - count_alquileres
        
        # Alquileres en meses anteriores (para reportes históricos)
        contador = 0
        for mes_offset in range(6, 0, -1):  # Últimos 6 meses
            if contador >= alquileres_necesarios:
                break
            fecha_base = hoy - timedelta(days=30 * mes_offset)
            
            # Varios alquileres por mes
            for i in range(3, 8):  # 3-7 alquileres por mes
                if contador >= alquileres_necesarios:
                    break
                fecha_inicio = fecha_base + timedelta(days=i*4)
                fecha_fin = fecha_inicio + timedelta(days=2 + (i % 4))  # 2-5 días de alquiler
                
                cliente_id = cliente_ids[contador % len(cliente_ids)]
                vehiculo_id = vehiculo_ids[contador % len(vehiculo_ids)]
                empleado_id = empleado_ids[contador % len(empleado_ids)] if empleado_ids else None
                
                dias = (fecha_fin - fecha_inicio).days
                c.execute("SELECT costo_diario FROM vehiculo WHERE id_vehiculo = ?", (vehiculo_id,))
                costo_diario = c.fetchone()[0]
                costo_total = dias * costo_diario
                
                alquileres.append((
                    fecha_inicio.strftime("%Y-%m-%d"),
                    fecha_fin.strftime("%Y-%m-%d"),
                    costo_total,
                    cliente_id,
                    vehiculo_id,
                    empleado_id
                ))
                contador += 1
        
        # Algunos alquileres futuros (para pruebas) si aún faltan
        for i in range(min(5, alquileres_necesarios - contador)):
            fecha_inicio = hoy + timedelta(days=5 + i*7)
            fecha_fin = fecha_inicio + timedelta(days=3)
            
            cliente_id = cliente_ids[contador % len(cliente_ids)]
            vehiculo_id = vehiculo_ids[(contador+2) % len(vehiculo_ids)]
            empleado_id = empleado_ids[contador % len(empleado_ids)] if empleado_ids else None
            
            dias = 3
            c.execute("SELECT costo_diario FROM vehiculo WHERE id_vehiculo = ?", (vehiculo_id,))
            costo_diario = c.fetchone()[0]
            costo_total = dias * costo_diario
            
            alquileres.append((
                fecha_inicio.strftime("%Y-%m-%d"),
                fecha_fin.strftime("%Y-%m-%d"),
                costo_total,
                cliente_id,
                vehiculo_id,
                empleado_id
            ))
            contador += 1
        
        if alquileres:
            c.executemany(
                "INSERT INTO alquiler (fecha_inicio, fecha_fin, costo_total, id_cliente, id_vehiculo, id_empleado) VALUES (?,?,?,?,?,?)",
                alquileres
            )

    conn.commit()
    conn.close()
