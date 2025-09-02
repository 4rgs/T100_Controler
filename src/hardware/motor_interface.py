#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interfaz abstracta para motores.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol


class MotorDirection(Enum):
    """Estados posibles de un motor."""
    COAST = "coast"
    FORWARD = "fwd"
    BACKWARD = "back"
    BRAKE = "brake"


class MotorState:
    """Estado actual de un motor."""
    
    def __init__(self):
        self.direction = MotorDirection.COAST
        self.speed_percent = 0.0
    
    def to_dict(self) -> dict:
        """Convierte el estado a diccionario."""
        return {
            "dir": self.direction.value,
            "speed": self.speed_percent
        }


class MotorInterface(ABC):
    """Interfaz abstracta para control de motores."""
    
    @abstractmethod
    def set_direction(self, forward: bool, brake: bool = False) -> None:
        """Establece la dirección del motor."""
        pass
    
    @abstractmethod
    def set_speed(self, speed_percent: float) -> None:
        """Establece la velocidad del motor (0-100%)."""
        pass
    
    @abstractmethod
    def coast(self) -> None:
        """Pone el motor en modo coast (libre)."""
        pass
    
    @abstractmethod
    def get_state(self) -> MotorState:
        """Obtiene el estado actual del motor."""
        pass


class DualMotorInterface(Protocol):
    """Protocolo para controladores de dos motores."""
    
    def get_motor_a(self) -> MotorInterface:
        """Obtiene el motor A (izquierdo)."""
        ...
    
    def get_motor_b(self) -> MotorInterface:
        """Obtiene el motor B (derecho)."""
        ...
    
    def stop_all(self) -> None:
        """Detiene todos los motores."""
        ...
