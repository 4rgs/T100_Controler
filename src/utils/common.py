#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilidades y funciones auxiliares para el sistema.
"""

import math
from typing import Tuple


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Limita un valor entre min y max."""
    return max(min_val, min(max_val, value))


def apply_deadzone(value: float, deadzone: float) -> float:
    """Aplica zona muerta a un valor."""
    return 0.0 if abs(value) < deadzone else value


def is_approximately_zero(value: float, tolerance: float = 1e-6) -> bool:
    """Verifica si un valor es aproximadamente cero."""
    return abs(value) < tolerance


def normalize_coordinates(x: float, y: float) -> Tuple[float, float]:
    """Normaliza coordenadas al rango [-1, 1]."""
    magnitude = math.sqrt(x*x + y*y)
    if magnitude > 1.0:
        x /= magnitude
        y /= magnitude
    return x, y


def map_range(value: float, from_min: float, from_max: float, 
              to_min: float, to_max: float) -> float:
    """Mapea un valor de un rango a otro."""
    from_range = from_max - from_min
    to_range = to_max - to_min
    if from_range == 0:
        return to_min
    scaled_value = (value - from_min) / from_range
    return to_min + (scaled_value * to_range)


def calculate_differential_speeds(forward: float, turn: float) -> Tuple[float, float]:
    """
    Calcula las velocidades diferenciales para las ruedas izquierda y derecha.
    
    Args:
        forward: Velocidad hacia adelante (-1.0 a 1.0)
        turn: Giro (-1.0 izquierda, 1.0 derecha)
    
    Returns:
        Tuple con (velocidad_izquierda, velocidad_derecha)
    """
    left = forward - turn
    right = forward + turn
    
    # Normalizar si alguna velocidad excede [-1, 1]
    max_speed = max(abs(left), abs(right))
    if max_speed > 1.0:
        left /= max_speed
        right /= max_speed
    
    return left, right


def format_percentage(value: float, decimals: int = 1) -> str:
    """Formatea un valor como porcentaje."""
    return f"{value:.{decimals}f}%"


def format_temperature(temp_celsius: float) -> str:
    """Formatea temperatura en Celsius."""
    return f"{temp_celsius:.1f}°C"


def is_raspberry_pi() -> bool:
    """Verifica si el sistema es una Raspberry Pi."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except:
        return False
