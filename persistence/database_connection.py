#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Patrón Singleton - Conexión única a la base de datos
Programación Orientada a Objetos - Encapsulación de la conexión
Thread-Safe - Maneja conexiones por thread para entornos multi-thread
"""

import sqlite3
import threading
import sys
import os

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_FILE


class DatabaseConnection:
    """
    Patrón Singleton - Garantiza una única instancia de la clase
    Thread-Safe - Cada thread tiene su propia conexión usando threading.local()
    Programación Orientada a Objetos - Encapsula la lógica de conexión
    """
    
    _instance = None
    _lock = threading.Lock()
    _local = threading.local()  # Thread-Safe - Almacena conexión por thread
    
    def __new__(cls):
        """Patrón Singleton - Implementación del patrón creacional"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def get_connection(self):
        """
        Obtiene la conexión a la base de datos
        Thread-Safe - Cada thread obtiene su propia conexión
        """
        # Thread-Safe - Verificar si este thread ya tiene una conexión
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            # Thread-Safe - Crear nueva conexión para este thread
            self._local.connection = sqlite3.connect(DB_FILE, check_same_thread=False)
            self._local.connection.row_factory = sqlite3.Row
            # Activar claves foráneas
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        return self._local.connection
    
    def close(self):
        """
        Cierra la conexión del thread actual
        Thread-Safe - Solo cierra la conexión del thread actual
        """
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def execute_query(self, query, params=None):
        """
        Programación Estructurada - Función para ejecutar consultas
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    
    def execute_transaction(self, queries_with_params):
        """
        Programación Estructurada - Función para ejecutar transacciones
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            for query, params in queries_with_params:
                cursor.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e

