#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Patrón Observer - Sistema de notificaciones
Programación Orientada a Objetos - Implementación del patrón Observer
"""

from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):
    """
    Patrón Observer - Interfaz para observadores
    Programación Orientada a Objetos - Clase abstracta
    Herencia y Polimorfismo - Clase base para observadores
    """
    
    @abstractmethod
    def update(self, event_type, data):
        """
        Patrón Observer - Método que se llama cuando ocurre un evento
        Herencia y Polimorfismo - Debe ser implementado en clases hijas
        """
        pass


class Subject:
    """
    Patrón Observer - Sujeto observable
    Programación Orientada a Objetos - Mantiene lista de observadores
    """
    
    def __init__(self):
        """
        Patrón Observer - Inicialización con lista vacía de observadores
        """
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer):
        """
        Patrón Observer - Agrega un observador
        Programación Orientada a Objetos - Método de comportamiento
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """
        Patrón Observer - Remueve un observador
        Programación Orientada a Objetos - Método de comportamiento
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_type, data):
        """
        Patrón Observer - Notifica a todos los observadores
        Programación Funcional - Uso de map para notificar a todos
        """
        # Programación Funcional - map para notificar a todos los observadores
        list(map(lambda obs: obs.update(event_type, data), self._observers))


class AlquilerNotifier(Subject):
    """
    Patrón Observer - Sujeto específico para notificaciones de alquileres
    Programación Orientada a Objetos - Especialización de Subject
    """
    
    def alquiler_creado(self, alquiler):
        """
        Patrón Observer - Notifica cuando se crea un alquiler
        """
        self.notify("alquiler_creado", alquiler)
    
    def alquiler_actualizado(self, alquiler):
        """
        Patrón Observer - Notifica cuando se actualiza un alquiler
        """
        self.notify("alquiler_actualizado", alquiler)


class LogObserver(Observer):
    """
    Patrón Observer - Observador que registra eventos en log
    Herencia y Polimorfismo - Implementa Observer
    """
    
    def update(self, event_type, data):
        """
        Patrón Observer - Implementación del método update
        Herencia y Polimorfismo - Implementa método abstracto
        """
        print(f"[LOG] Evento: {event_type}, Datos: {data}")


class EmailObserver(Observer):
    """
    Patrón Observer - Observador que envía emails (simulado)
    Herencia y Polimorfismo - Implementa Observer
    """
    
    def update(self, event_type, data):
        """
        Patrón Observer - Implementación del método update
        Herencia y Polimorfismo - Implementa método abstracto
        """
        if event_type == "alquiler_creado":
            print(f"[EMAIL] Notificación: Nuevo alquiler creado - ID: {data.id_alquiler if hasattr(data, 'id_alquiler') else 'N/A'}")

