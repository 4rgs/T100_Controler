#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JoystickController optimizado para mínimo uso de recursos.
"""

import math
from typing import Callable, Optional, Tuple

from ..config.settings import HardwareConfig, JoystickConfig
from ..hardware.motor_interface import MotorInterface


class JoystickControllerOptimized:
    """Controlador de joystick optimizado."""
    
    __slots__ = ['motor_a', 'motor_b', 'config', '_last_values', '_threshold']
    
    def __init__(self, motor_a: MotorInterface, motor_b: MotorInterface, config: JoystickConfig):
        self.motor_a = motor_a
        self.motor_b = motor_b
        self.config = config
        self._last_values = (0.0, 0.0, 0.0, 0.0)  # left_speed, left_dir, right_speed, right_dir
        self._threshold = 0.01  # Umbral para evitar cambios menores
    
    def process_joystick_input(self, x: float, y: float) -> None:
        """Procesa entrada del joystick con optimización."""
        # Normalizar y aplicar deadzone
        x = self._apply_deadzone(x)
        y = self._apply_deadzone(y)
        
        # Calcular velocidades diferenciales
        left_speed, right_speed = self._differential_mix(x, y)
        
        # Determinar direcciones
        left_forward = left_speed >= 0
        right_forward = right_speed >= 0
        
        # Convertir a valores absolutos
        left_speed = abs(left_speed)
        right_speed = abs(right_speed)
        
        # Crear tupla de valores actuales
        current_values = (left_speed, float(left_forward), right_speed, float(right_forward))
        
        # Solo actualizar si hay cambios significativos
        if self._values_changed(current_values):
            self._update_motors(left_speed, left_forward, right_speed, right_forward)
            self._last_values = current_values
    
    def _apply_deadzone(self, value: float) -> float:
        """Aplica zona muerta optimizada."""
        abs_value = abs(value)
        if abs_value < self.config.deadzone:
            return 0.0
        
        # Escalar linealmente desde deadzone hasta 1.0
        scale = (abs_value - self.config.deadzone) / (1.0 - self.config.deadzone)
        return math.copysign(scale, value)
    
    def _differential_mix(self, x: float, y: float) -> Tuple[float, float]:
        """Mezcla diferencial optimizada."""
        # Aplicar factor de giro
        x *= self.config.turn_factor
        
        # Calcular velocidades de ruedas
        left = y - x
        right = y + x
        
        # Normalizar si alguna velocidad excede 1.0
        max_value = max(abs(left), abs(right))
        if max_value > 1.0:
            left /= max_value
            right /= max_value
        
        return left, right
    
    def _values_changed(self, new_values: Tuple[float, float, float, float]) -> bool:
        """Verifica si los valores han cambiado significativamente."""
        for i in range(4):
            if abs(new_values[i] - self._last_values[i]) > self._threshold:
                return True
        return False
    
    def _update_motors(self, left_speed: float, left_forward: bool, 
                      right_speed: float, right_forward: bool) -> None:
        """Actualiza los motores con los nuevos valores."""
        # Motor izquierdo (A)
        if left_speed < 0.001:  # Prácticamente cero
            self.motor_a.coast()
        else:
            self.motor_a.set_direction(left_forward)
            self.motor_a.set_speed(left_speed * 100.0)
        
        # Motor derecho (B)
        if right_speed < 0.001:  # Prácticamente cero
            self.motor_b.coast()
        else:
            self.motor_b.set_direction(right_forward)
            self.motor_b.set_speed(right_speed * 100.0)
    
    def stop(self) -> None:
        """Detiene todos los motores."""
        self.motor_a.coast()
        self.motor_b.coast()
        self._last_values = (0.0, 0.0, 0.0, 0.0)
    
    def emergency_stop(self) -> None:
        """Parada de emergencia con freno."""
        self.motor_a.set_direction(True, brake=True)
        self.motor_b.set_direction(True, brake=True)
        self._last_values = (0.0, 0.0, 0.0, 0.0)
