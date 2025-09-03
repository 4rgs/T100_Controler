#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controlador de joystick para mezcla diferencial de motores.
"""

import time
from dataclasses import dataclass
from typing import Tuple

from ..config.settings import JoystickConfig
from ..hardware.motor_interface import DualMotorInterface


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


class JoystickController:
    """Controlador que convierte input de joystick a comandos de motor."""
    
    def __init__(self, motor_controller: DualMotorInterface, config: JoystickConfig):
        self.motors = motor_controller
        self.config = config
        self.joystick_state = JoystickState()
        self.mix_state = MixState()
    
    def _apply_deadzone_and_shaping(self, value: float) -> float:
        """Aplica zona muerta y curva no lineal."""
        if abs(value) < self.config.deadzone:
            return 0.0
        
        # Aplicar curva no lineal
        sign = 1.0 if value > 0 else -1.0
        return sign * (abs(value) ** self.config.non_linear_factor)
    
    def _differential_mix(self, x: float, y: float) -> Tuple[float, float]:
        """
        Mezcla diferencial: convierte x,y del joystick a velocidades left/right.
        
        Args:
            x: Entrada lateral (-1.0 a 1.0, positivo = derecha)
            y: Entrada frontal (-1.0 a 1.0, positivo = adelante)
        
        Returns:
            Tuple con velocidades (left, right) en rango -1.0 a 1.0
        """
        # Mezcla diferencial corregida:
        # Para ir a la derecha (x > 0): motor izquierdo más rápido
        # Para ir a la izquierda (x < 0): motor derecho más rápido
        left = y - x   # Motor izquierdo: adelante - giro derecha
        right = y + x  # Motor derecho: adelante + giro derecha
        
        # Clamp a rango válido
        left = max(-1.0, min(1.0, left))
        right = max(-1.0, min(1.0, right))
        
        return left, right
    
    def _apply_motor_command(self, motor, speed: float) -> None:
        """Aplica comando a un motor individual."""
        from ..utils.common import is_approximately_zero
        
        if is_approximately_zero(speed):
            motor.coast()
        else:
            is_forward = speed > 0.0
            speed_percent = abs(speed) * 100.0
            
            # IMPORTANTE: Establecer dirección ANTES que velocidad
            # Primero parar el motor
            motor.set_speed(0.0)
            # Luego cambiar dirección
            motor.set_direction(is_forward)
            # Finalmente aplicar velocidad
            motor.set_speed(speed_percent)
    
    def update(self, x: float, y: float) -> None:
        """
        Actualiza el estado del joystick y aplica comandos a los motores.
        
        Args:
            x: Posición X del joystick (-1.0 a 1.0)
            y: Posición Y del joystick (-1.0 a 1.0, positivo = adelante)
        """
        # Clamp input
        x = max(-1.0, min(1.0, x))
        y = max(-1.0, min(1.0, y))
        
        # Aplicar zona muerta y shaping
        processed_x = self._apply_deadzone_and_shaping(x)
        processed_y = self._apply_deadzone_and_shaping(y)
        
        # Mezcla diferencial
        left_speed, right_speed = self._differential_mix(processed_x, processed_y)
        
        # Aplicar a motores
        motor_a = self.motors.get_motor_a()  # Motor izquierdo
        motor_b = self.motors.get_motor_b()  # Motor derecho
        
        self._apply_motor_command(motor_a, left_speed)
        self._apply_motor_command(motor_b, right_speed)
        
        # Actualizar estado
        self.joystick_state.x = processed_x
        self.joystick_state.y = processed_y
        self.joystick_state.last_update = time.time()
        
        self.mix_state.left = left_speed
        self.mix_state.right = right_speed
        
        # Log detallado para debug
        print(f"[JOY] x={processed_x:.2f} y={processed_y:.2f} -> "
              f"L={left_speed:.2f} R={right_speed:.2f}")
        print(f"[MOTOR_A] Dir: {motor_a.get_state().direction.value}, Speed: {motor_a.get_state().speed_percent:.0f}%")
        print(f"[MOTOR_B] Dir: {motor_b.get_state().direction.value}, Speed: {motor_b.get_state().speed_percent:.0f}%")
        print("---")
    
    def stop(self) -> None:
        """Detiene todos los motores y resetea el estado."""
        self.motors.stop_all()
        self.joystick_state = JoystickState()
        self.mix_state = MixState()
    
    def get_state(self) -> dict:
        """Obtiene el estado completo del sistema."""
        return {
            "A": self.motors.get_motor_a().get_state().to_dict(),
            "B": self.motors.get_motor_b().get_state().to_dict(),
            "joy": self.joystick_state.to_dict(),
            "mix": self.mix_state.to_dict(),
            "ts": self.joystick_state.last_update
        }
