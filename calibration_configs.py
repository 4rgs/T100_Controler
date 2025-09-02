#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuraciones alternativas para calibración de motores.
"""

from src.config.settings import HardwareConfig, MotorPins, JoystickConfig, ServerConfig

# Configuración 1: Sin inversión (configuración estándar)
CONFIG_NO_INVERT = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False),
        motor_b=MotorPins(enable=26, in1=19, in2=21, invert=False),
        pwm_frequency=1000
    ),
    "joystick": JoystickConfig(deadzone=0.03, non_linear_factor=1.0),
    "server": ServerConfig(host="0.0.0.0", port=8080, debug=False)
}

# Configuración 2: Solo Motor A invertido
CONFIG_A_INVERTED = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=True),
        motor_b=MotorPins(enable=26, in1=19, in2=21, invert=False),
        pwm_frequency=1000
    ),
    "joystick": JoystickConfig(deadzone=0.03, non_linear_factor=1.0),
    "server": ServerConfig(host="0.0.0.0", port=8080, debug=False)
}

# Configuración 3: Solo Motor B invertido
CONFIG_B_INVERTED = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False),
        motor_b=MotorPins(enable=26, in1=19, in2=21, invert=True),
        pwm_frequency=1000
    ),
    "joystick": JoystickConfig(deadzone=0.03, non_linear_factor=1.0),
    "server": ServerConfig(host="0.0.0.0", port=8080, debug=False)
}

# Configuración 4: Ambos motores invertidos
CONFIG_BOTH_INVERTED = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=True),
        motor_b=MotorPins(enable=26, in1=19, in2=21, invert=True),
        pwm_frequency=1000
    ),
    "joystick": JoystickConfig(deadzone=0.03, non_linear_factor=1.0),
    "server": ServerConfig(host="0.0.0.0", port=8080, debug=False)
}

# Configuración 5: Motores intercambiados (A->B, B->A)
CONFIG_SWAPPED = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=26, in1=19, in2=21, invert=False),  # Era Motor B
        motor_b=MotorPins(enable=12, in1=16, in2=20, invert=False),  # Era Motor A
        pwm_frequency=1000
    ),
    "joystick": JoystickConfig(deadzone=0.03, non_linear_factor=1.0),
    "server": ServerConfig(host="0.0.0.0", port=8080, debug=False)
}

CONFIGURATIONS = {
    "1": ("Sin inversión", CONFIG_NO_INVERT),
    "2": ("Solo Motor A invertido", CONFIG_A_INVERTED),
    "3": ("Solo Motor B invertido", CONFIG_B_INVERTED),
    "4": ("Ambos motores invertidos", CONFIG_BOTH_INVERTED),
    "5": ("Motores intercambiados", CONFIG_SWAPPED),
}
