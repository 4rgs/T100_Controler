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
    """Configuración de pines para un motor."""
    enable: int
    in1: int
    in2: int
    invert: bool = False
    power_factor: float = 1.0  # Factor de calibración de potencia (0.5 - 1.5)
    pwm_inverted: bool = False  # PWM invertido: 0=máximo, 255=parado


@dataclass
class HardwareConfig:
    """Configuración del hardware L298N."""
    motor_a: MotorPins  # Motor izquierdo
    motor_b: MotorPins  # Motor derecho
    pwm_frequency: int = 1000
    max_pwm_percent: float = 33.0  # Límite máximo PWM en porcentaje (0-100)


@dataclass
class ServerConfig:
    """Configuración del servidor WebSocket."""
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False


# Configuración por defecto
DEFAULT_CONFIG = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False, power_factor=1.0, pwm_inverted=False),  # Motor izquierdo - normal
        motor_b=MotorPins(enable=19, in1=21, in2=26, invert=False, power_factor=1.0, pwm_inverted=False),   # Motor derecho - PWM INVERTIDO
        pwm_frequency=1000,
        max_pwm_percent=100.0  # Sin límite PWM - potencia completa
    ),
    "server": ServerConfig(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
}


# Configuraciones de calibración predefinidas
# Usa get_calibrated_config() con el nombre de la configuración

CALIBRATION_CONFIGS = {
    "motor_a_fast": {
        "description": "Motor A más rápido - reducir su potencia",
        "motor_a_factor": 0.85,
        "motor_b_factor": 1.0
    },
    "motor_b_fast": {
        "description": "Motor B más rápido - reducir su potencia", 
        "motor_a_factor": 1.0,
        "motor_b_factor": 0.85
    },
    "motor_a_weak": {
        "description": "Motor A débil - aumentar su potencia",
        "motor_a_factor": 1.5,  # Aumentar potencia motor izquierdo
        "motor_b_factor": 1.0
    },
    "motor_b_weak": {
        "description": "Motor B débil - aumentar su potencia",
        "motor_a_factor": 1.0,
        "motor_b_factor": 1.5
    },
    "drift_left": {
        "description": "Se desvía a la izquierda - reducir Motor B",
        "motor_a_factor": 1.0,
        "motor_b_factor": 0.80
    },
    "drift_right": {
        "description": "Se desvía a la derecha - reducir Motor A",
        "motor_a_factor": 0.80,
        "motor_b_factor": 1.0
    }
}


def get_config() -> dict:
    """Retorna la configuración del sistema."""
    return DEFAULT_CONFIG


def get_calibrated_config(calibration_name: str) -> dict:
    """
    Retorna configuración con calibración aplicada.
    
    Args:
        calibration_name: Nombre de la calibración predefinida
        
    Returns:
        Configuración con factores de potencia ajustados
    """
    if calibration_name not in CALIBRATION_CONFIGS:
        raise ValueError(f"Calibración '{calibration_name}' no encontrada. Disponibles: {list(CALIBRATION_CONFIGS.keys())}")
    
    calib = CALIBRATION_CONFIGS[calibration_name]
    config = DEFAULT_CONFIG.copy()
    
    # Crear nueva configuración con factores ajustados
    config["hardware"] = HardwareConfig(
        motor_a=MotorPins(
            enable=12, in1=16, in2=20, 
            invert=False, 
            power_factor=calib["motor_a_factor"],
            pwm_inverted=False
        ),
        motor_b=MotorPins(
            enable=19, in1=21, in2=26, 
            invert=False, 
            power_factor=calib["motor_b_factor"],
            pwm_inverted=True
        ),
        pwm_frequency=2000,
        max_pwm_percent=100
    )
    
    print(f"🔧 Usando calibración: {calib['description']}")
    print(f"   Motor A factor: {calib['motor_a_factor']}")
    print(f"   Motor B factor: {calib['motor_b_factor']}")
    
    return config


def set_custom_calibration(motor_a_factor: float, motor_b_factor: float) -> dict:
    """
    Crea configuración con factores personalizados.
    
    Args:
        motor_a_factor: Factor de potencia Motor A (0.5-1.5)
        motor_b_factor: Factor de potencia Motor B (0.5-1.5)
        
    Returns:
        Configuración con factores personalizados
    """
    # Validar rangos
    motor_a_factor = max(0.5, min(1.5, motor_a_factor))
    motor_b_factor = max(0.5, min(1.5, motor_b_factor))
    
    config = DEFAULT_CONFIG.copy()
    
    config["hardware"] = HardwareConfig(
        motor_a=MotorPins(
            enable=12, in1=16, in2=20, 
            invert=False, 
            power_factor=motor_a_factor,
            pwm_inverted=False
        ),
        motor_b=MotorPins(
            enable=19, in1=21, in2=26, 
            invert=False, 
            power_factor=motor_b_factor,
            pwm_inverted=True
        ),
        pwm_frequency=2000,
        max_pwm_percent=100
    )
    
    print("🎯 Calibración personalizada aplicada:")
    print(f"   Motor A factor: {motor_a_factor}")
    print(f"   Motor B factor: {motor_b_factor}")
    
    return config
