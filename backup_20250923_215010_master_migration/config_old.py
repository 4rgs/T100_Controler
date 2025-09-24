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
class ServoConfig:
    """Configuración para servo MG90S."""
    gpio_pin: int  # Pin GPIO para control PWM del servo
    center_pulse: int = 1500  # Pulso central en microsegundos (1500µs = 90°)
    min_pulse: int = 500      # Pulso mínimo en microsegundos (~0°)
    max_pulse: int = 2500     # Pulso máximo en microsegundos (~180°)
    invert: bool = False      # Invertir dirección del servo
    name: str = "servo"       # Nombre descriptivo


@dataclass
class HardwareConfig:
    """Configuración del hardware ZK-5AD (TA6586) + Servos MG90S."""
    # Motores para tank drive (campos requeridos primero)
    motor_a: MotorPins  # Motor izquierdo
    motor_b: MotorPins  # Motor derecho
    servo_pan: ServoConfig   # Servo horizontal (CH1 - joystick izquierdo horizontal)
    servo_tilt: ServoConfig  # Servo vertical (CH3 - joystick izquierdo vertical)
    
    # Campos con valores por defecto (deben ir al final)
    pwm_frequency: int = 1000
    max_pwm_percent: float = 100  # Límite máximo PWM en porcentaje (0-100)
    direction_change_delay: float = 0.075  # 75ms pausa antes de invertir dirección
    enable_direction_protection: bool = True  # Activar protección automática


@dataclass
class ServerConfig:
    """Configuración del servidor WebSocket."""
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False


# Configuración por defecto para ZK-5AD (TA6586)
# 
# CONFIGURACIÓN FÍSICA DEL TANQUE + CÁMARA:
#
#     [SERVO TILT]    <- GPIO 20 (CH3 tilt cámara)
#         │
#     [SERVO PAN]     <- GPIO 21 (CH4 pan cámara)
#         │
#     ORUGA IZQ        ORUGA DER
#         ▲               ▲
#    [MOTOR A]  ◄─H─►  [MOTOR B]
#         │               │  
#    (GPIO 12,16)    (GPIO 13,26)
#
# CONTROLES ELRS:
# - CH1: Rotación tank (izquierda/derecha)
# - CH2: Aceleración tank (adelante/atrás)
# - CH3: Tilt cámara (arriba/abajo)
# - CH4: Pan cámara (izquierda/derecha)
#
# PWM OPTIMIZADO:
# - Motor A: GPIO 12 (PWM0) + GPIO 16 (digital) 
# - Motor B: GPIO 13 (PWM1) + GPIO 26 (digital)
# - Servo Pan: GPIO 21 (PWM software) ← CH4
# - Servo Tilt: GPIO 20 (PWM software) ← CH3
#
# Los motores están físicamente orientados de manera opuesta (configuración H)
# Para moverse ADELANTE: Motor A gira normal, Motor B gira invertido
# Para GIRAR DERECHA: Motor A más rápido, Motor B más lento
# Para GIRAR IZQUIERDA: Motor A más lento, Motor B más rápido
#
DEFAULT_CONFIG = {
    "hardware": HardwareConfig(
        # Motores para tank drive
        motor_a=MotorPins(in1=12, in2=16, invert=False, power_factor=1.0), # Motor A: PWM0 + GPIO16
        motor_b=MotorPins(in1=13, in2=26, invert=True, power_factor=1.0),  # Motor B: PWM1 + GPIO26 (invertido por orientación)
        pwm_frequency=4000,
        max_pwm_percent=100.0,
        
        # Servos MG90S para cámara
        servo_pan=ServoConfig(gpio_pin=21, name="Pan", invert=True),    # GPIO21 - CH4 (Pan cámara izq/der)
        servo_tilt=ServoConfig(gpio_pin=20, name="Tilt", invert=True),  # GPIO20 - CH3 (Tilt cámara arriba/abajo)

        # Protección contra picos de corriente
        direction_change_delay=0.075,
        enable_direction_protection=True
    )
}


def get_config() -> dict:
    """Retorna la configuración del sistema."""
    return DEFAULT_CONFIG

