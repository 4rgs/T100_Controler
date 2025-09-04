#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JoystickController optimizado para mínimo uso de recursos - Versión producción.
"""

import math
import time
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from ..config.settings import HardwareConfig, JoystickConfig
from ..hardware.motor_interface import MotorInterface


@dataclass
class JoystickState:
    """Estado del joystick virtual."""
    x: float = 0.0  # -1.0 a 1.0
    y: float = 0.0  # -1.0 a 1.0
    last_update: float = 0.0
    
    def to_dict(self) -> dict:
        """Convierte el estado a diccionario."""
        return {"x": self.x, "y": self.y}


@dataclass
class MixState:
    """Estado de la mezcla diferencial."""
    left: float = 0.0   # -1.0 a 1.0
    right: float = 0.0  # -1.0 a 1.0
    
    def to_dict(self) -> dict:
        """Convierte el estado a diccionario."""
        return {"left": self.left, "right": self.right}


class JoystickControllerOptimized:
    """Controlador de joystick optimizado para producción."""
    
    __slots__ = ['motors', 'config', '_last_values', '_threshold', '_debug', 'joystick_state', 'mix_state']
    
    def __init__(self, motor_controller, config: JoystickConfig, debug: bool = False):
        self.motors = motor_controller  # DualMotorInterface como el original
        self.config = config
        self._last_values = (0.0, 0.0, 0.0, 0.0)  # left_speed, left_dir, right_speed, right_dir
        self._threshold = 0.01  # Umbral para evitar cambios menores
        self._debug = debug
        self.joystick_state = JoystickState()
        self.mix_state = MixState()
    
    def process_joystick_input(self, x: float, y: float) -> None:
        """Procesa entrada del joystick con optimización."""
        if self._debug:
            print(f"🎮 JoystickController recibió: x={x:.2f}, y={y:.2f}")
        
        # Normalizar y aplicar deadzone
        processed_x = self._apply_deadzone(x)
        processed_y = self._apply_deadzone(y)
        
        if self._debug and (processed_x != 0 or processed_y != 0):
            print(f"🎮 Después de deadzone: x={processed_x:.2f}, y={processed_y:.2f}")
        
        # Calcular velocidades diferenciales
        left_speed, right_speed = self._differential_mix(processed_x, processed_y)
        
        if self._debug and (abs(left_speed) > 0.01 or abs(right_speed) > 0.01):
            print(f"🎮 Velocidades calculadas: L={left_speed:.2f}, R={right_speed:.2f}")
        
        # Determinar direcciones
        left_forward = left_speed >= 0
        right_forward = right_speed >= 0
        
        # Convertir a valores absolutos
        left_speed_abs = abs(left_speed)
        right_speed_abs = abs(right_speed)
        
        # Crear tupla de valores actuales
        current_values = (left_speed_abs, float(left_forward), right_speed_abs, float(right_forward))
        
        # Solo actualizar si hay cambios significativos
        if self._values_changed(current_values):
            if self._debug:
                print(f"🎮 Actualizando motores: L={left_speed_abs:.2f}({left_forward}), R={right_speed_abs:.2f}({right_forward})")
            self._update_motors(left_speed_abs, left_forward, right_speed_abs, right_forward)
            self._last_values = current_values
        elif self._debug and (processed_x != 0 or processed_y != 0):
            print("🎮 Sin cambios significativos, saltando actualización")
        
        # Actualizar estados para compatibilidad
        self.joystick_state.x = processed_x
        self.joystick_state.y = processed_y
        self.joystick_state.last_update = time.time()
        
        self.mix_state.left = left_speed  # Con signo
        self.mix_state.right = right_speed  # Con signo
    
    def update(self, x: float, y: float) -> None:
        """Alias para compatibilidad con la interfaz original."""
        self.process_joystick_input(x, y)
    
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
        
        # Invertir dirección de giro si está configurado
        if self.config.invert_turn_direction:
            x = -x
        
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
        motor_a = self.motors.get_motor_a()  # Motor izquierdo
        motor_b = self.motors.get_motor_b()  # Motor derecho
        
        # Motor izquierdo (A)
        if left_speed < 0.001:  # Prácticamente cero
            motor_a.coast()
        else:
            motor_a.set_direction(left_forward)
            motor_a.set_speed(left_speed * 100.0)
        
        # Motor derecho (B)
        if right_speed < 0.001:  # Prácticamente cero
            motor_b.coast()
        else:
            motor_b.set_direction(right_forward)
            motor_b.set_speed(right_speed * 100.0)
    
    def stop(self) -> None:
        """Detiene todos los motores."""
        self.motors.get_motor_a().coast()
        self.motors.get_motor_b().coast()
        self._last_values = (0.0, 0.0, 0.0, 0.0)
        self.joystick_state = JoystickState()
        self.mix_state = MixState()
    
    def emergency_stop(self) -> None:
        """Parada de emergencia con freno."""
        motor_a = self.motors.get_motor_a()
        motor_b = self.motors.get_motor_b()
        motor_a.set_direction(True, brake=True)
        motor_b.set_direction(True, brake=True)
        self._last_values = (0.0, 0.0, 0.0, 0.0)
        self.joystick_state = JoystickState()
        self.mix_state = MixState()

# Fin del archivo
