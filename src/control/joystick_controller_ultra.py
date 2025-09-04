#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JoystickController ULTRA-OPTIMIZADO para latencia mínima.
Elimina todos los checks innecesarios y optimiza al máximo la respuesta.
"""

import time
from dataclasses import dataclass
from typing import Tuple

from ..config.settings import JoystickConfig
from ..hardware.motor_interface import MotorInterface


@dataclass
class JoystickState:
    """Estado del joystick virtual."""
    x: float = 0.0
    y: float = 0.0
    last_update: float = 0.0
    
    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}


@dataclass
class MixState:
    """Estado de la mezcla diferencial."""
    left: float = 0.0
    right: float = 0.0
    
    def to_dict(self) -> dict:
        return {"left": self.left, "right": self.right}


class UltraFastJoystickController:
    """Controlador ultra-optimizado para latencia mínima."""
    
    __slots__ = ['motors', 'config', 'joystick_state', 'mix_state', '_debug', '_deadzone_sq']
    
    def __init__(self, motor_controller, config: JoystickConfig, debug: bool = False):
        self.motors = motor_controller
        self.config = config
        self._debug = debug
        self.joystick_state = JoystickState()
        self.mix_state = MixState()
        
        # Pre-calcular deadzone al cuadrado para evitar sqrt en tiempo real
        self._deadzone_sq = config.deadzone * config.deadzone
    
    def update(self, x: float, y: float) -> None:
        """Actualización ultra-rápida sin verificaciones innecesarias."""
        # Aplicar deadzone ultra-rápido (usando distancia euclidiana al cuadrado)
        if (x * x + y * y) < self._deadzone_sq:
            # Zona muerta - parar motores inmediatamente
            self.motors.get_motor_a().coast()
            self.motors.get_motor_b().coast()
            
            # Actualizar estados
            self.joystick_state.x = 0.0
            self.joystick_state.y = 0.0
            self.mix_state.left = 0.0
            self.mix_state.right = 0.0
            return
        
        # Aplicar factor de giro directamente
        x *= self.config.turn_factor
        
        # Mezcla diferencial ultra-rápida
        left_speed = y - x
        right_speed = y + x
        
        # Clamp rápido sin función max/min
        if left_speed > 1.0:
            left_speed = 1.0
        elif left_speed < -1.0:
            left_speed = -1.0
            
        if right_speed > 1.0:
            right_speed = 1.0
        elif right_speed < -1.0:
            right_speed = -1.0
        
        # Aplicar a motores directamente sin verificaciones
        motor_a = self.motors.get_motor_a()
        motor_b = self.motors.get_motor_b()
        
        # Motor izquierdo (A)
        if left_speed == 0.0:
            motor_a.coast()
        else:
            motor_a.set_direction(left_speed > 0.0)
            motor_a.set_speed(abs(left_speed) * 100.0)
        
        # Motor derecho (B) 
        if right_speed == 0.0:
            motor_b.coast()
        else:
            motor_b.set_direction(right_speed > 0.0)
            motor_b.set_speed(abs(right_speed) * 100.0)
        
        # Actualizar estados sin timestamp para mayor velocidad
        self.joystick_state.x = x
        self.joystick_state.y = y
        self.mix_state.left = left_speed
        self.mix_state.right = right_speed
        
        if self._debug:
            print(f"⚡ ULTRA: x={x:.2f} y={y:.2f} -> L={left_speed:.2f} R={right_speed:.2f}")
    
    def stop(self) -> None:
        """Parada inmediata."""
        self.motors.get_motor_a().coast()
        self.motors.get_motor_b().coast()
        self.joystick_state = JoystickState()
        self.mix_state = MixState()
    
    def emergency_stop(self) -> None:
        """Parada de emergencia inmediata."""
        motor_a = self.motors.get_motor_a()
        motor_b = self.motors.get_motor_b()
        motor_a.set_speed(0.0)
        motor_b.set_speed(0.0)
        self.joystick_state = JoystickState()
        self.mix_state = MixState()


# Alias para compatibilidad
JoystickControllerOptimized = UltraFastJoystickController
