#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuración centralizada para el sistema de control de motores.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class MotorPins:
    """Configuración de pines para un motor."""
    enable: int
    in1: int
    in2: int
    invert: bool = False


@dataclass
class HardwareConfig:
    """Configuración del hardware L298N."""
    motor_a: MotorPins
    motor_b: MotorPins
    pwm_frequency: int = 1000


@dataclass
class JoystickConfig:
    """Configuración del joystick virtual."""
    deadzone: float = 0.03
    non_linear_factor: float = 1.0
    turn_factor: float = 1.0  # Factor de multiplicación para giros


@dataclass
class GamepadConfig:
    """Configuración del gamepad físico."""
    deadzone: float = 0.06
    invert_y_axis: bool = True  # True para comportamiento tipo drone
    non_linear_factor: float = 1.0


@dataclass
class ServerConfig:
    """Configuración del servidor web."""
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False


# Configuración por defecto del usuario
# IMPORTANTE: Ajustar según el comportamiento real de tus motores
DEFAULT_CONFIG = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False),  # Motor A (izq) - OK
        motor_b=MotorPins(enable=26, in1=21, in2=19, invert=True),  # Motor B (der) - PROBLEMA COAST
        pwm_frequency=4000
    ),
    "joystick": JoystickConfig(
        deadzone=0.10,
        non_linear_factor=1.3
    ),
    "gamepad": GamepadConfig(
        deadzone=0.06,
        invert_y_axis=True,  # Comportamiento tipo drone
        non_linear_factor=1.0
    ),
    "server": ServerConfig(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
}

# Configuración alternativa para probar si el problema es de pines intercambiados
ALT_CONFIG_PINS_SWAPPED = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False),  # Motor A sin cambios
        motor_b=MotorPins(enable=26, in1=21, in2=19, invert=False),  # Motor B con IN3/IN4 intercambiados
        pwm_frequency=15000
    ),
    "joystick": JoystickConfig(
        deadzone=0.03,
        non_linear_factor=1.0
    ),
    "gamepad": GamepadConfig(
        deadzone=0.06,
        invert_y_axis=True,  # Comportamiento tipo drone
        non_linear_factor=1.0
    ),
    
    "server": ServerConfig(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
}


def get_config() -> dict:
    """Retorna la configuración actual del sistema."""
    return DEFAULT_CONFIG


def get_alt_config() -> dict:
    """Retorna configuración alternativa con pines intercambiados para Motor B."""
    return ALT_CONFIG_PINS_SWAPPED
