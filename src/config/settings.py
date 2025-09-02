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
    pwm_frequency: int = 1000  # Hz


@dataclass
class JoystickConfig:
    """Configuración del joystick virtual."""
    deadzone: float = 0.03
    non_linear_factor: float = 1.0  # 1.0 = lineal


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
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=True),  # Cambiar si gira al revés
        motor_b=MotorPins(enable=26, in1=19, in2=21, invert=False),  # Cambiar si gira al revés
        pwm_frequency=2000
    ),
    "joystick": JoystickConfig(
        deadzone=0.03,
        non_linear_factor=1.0  # Respuesta lineal para diagnóstico
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
