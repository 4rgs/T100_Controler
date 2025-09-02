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
    """Verifica si un valor flotante es aproximadamente cero."""
    return abs(value) < tolerance


def normalize_angle(angle_rad: float) -> float:
    """Normaliza un ángulo a rango [-π, π]."""
    while angle_rad > math.pi:
        angle_rad -= 2 * math.pi
    while angle_rad < -math.pi:
        angle_rad += 2 * math.pi
    return angle_rad


def cartesian_to_polar(x: float, y: float) -> Tuple[float, float]:
    """Convierte coordenadas cartesianas a polares (magnitud, ángulo)."""
    magnitude = math.sqrt(x*x + y*y)
    angle = math.atan2(y, x)
    return magnitude, angle


def polar_to_cartesian(magnitude: float, angle_rad: float) -> Tuple[float, float]:
    """Convierte coordenadas polares a cartesianas (x, y)."""
    x = magnitude * math.cos(angle_rad)
    y = magnitude * math.sin(angle_rad)
    return x, y


def interpolate(start: float, end: float, factor: float) -> float:
    """Interpolación lineal entre dos valores."""
    factor = clamp(factor, 0.0, 1.0)
    return start + (end - start) * factor


class MovingAverage:
    """Filtro de media móvil para suavizar valores."""
    
    def __init__(self, window_size: int = 5):
        self.window_size = max(1, window_size)
        self.values = []
    
    def add_value(self, value: float) -> float:
        """Agrega un valor y retorna la media móvil actualizada."""
        self.values.append(value)
        if len(self.values) > self.window_size:
            self.values.pop(0)
        return sum(self.values) / len(self.values)
    
    def reset(self) -> None:
        """Resetea el filtro."""
        self.values.clear()
