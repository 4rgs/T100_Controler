#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuración para el T100 Controller - Versión simplificada
Hardware: L298N + RPi Zero 2W
Comunicación: WebSocket API
"""

from dataclasses import dataclass


@dataclass
class MotorPins:
    """Configuración de pines para un motor ZK-5AD (TA6586)."""
    in1: int  # Pin IN1 - PWM para control de velocidad/dirección
    in2: int  # Pin IN2 - PWM para control de velocidad/dirección
    invert: bool = False
    power_factor: float = 1.0  # Factor de calibración de potencia (0.5 - 1.5)


@dataclass
class HardwareConfig:
    """Configuración del hardware ZK-5AD (TA6586)."""
    motor_a: MotorPins  # Motor izquierdo
    motor_b: MotorPins  # Motor derecho
    pwm_frequency: int = 1000
    max_pwm_percent: float = 100  # Límite máximo PWM en porcentaje (0-100)
    
    # Protección contra picos de corriente
    direction_change_delay: float = 0.075  # 75ms pausa antes de invertir dirección
    enable_direction_protection: bool = True  # Activar protección automática



# Configuración por defecto para ZK-5AD (TA6586)
# 
# CONFIGURACIÓN FÍSICA DEL TANQUE:
#
#     ORUGA IZQ        ORUGA DER
#         ▲               ▲
#    [MOTOR A]  ◄─H─►  [MOTOR B]
#         │               │
#    (GPIO 12,16)    (GPIO 13,26)
#
# PWM OPTIMIZADO:
# - Motor A: GPIO 12 (PWM0) + GPIO 16 (digital) 
# - Motor B: GPIO 13 (PWM1) + GPIO 26 (digital)
# - Evita conflictos PWM entre motores
#
# Los motores están físicamente orientados de manera opuesta (configuración H)
# Para moverse ADELANTE: Motor A gira normal, Motor B gira invertido
# Para GIRAR DERECHA: Motor A más rápido, Motor B más lento
# Para GIRAR IZQUIERDA: Motor A más lento, Motor B más rápido
#
DEFAULT_CONFIG = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(in1=12, in2=16, invert=False, power_factor=1.0), # Motor A: PWM0 + GPIO16 (evitar conflicto PWM1)
        motor_b=MotorPins(in1=13, in2=26, invert=True, power_factor=1.0),  # Motor B: PWM1 + GPIO26 (evitar conflicto PWM0)
        pwm_frequency=20000,
        max_pwm_percent=100.0  # Sin límite PWM - potencia completa
    )
}
