#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementación concreta del driver L298N usando pigpio.
"""

import atexit
import signal
from typing import Optional

import pigpio

from ..config.settings import MotorPins
from .motor_interface import MotorInterface, MotorState, MotorDirection


class L298NMotor(MotorInterface):
    """Motor individual controlado por L298N."""
    
    def __init__(self, pi_instance: pigpio.pi, pins: MotorPins, pwm_freq: int = 1000):
        self.pi = pi_instance
        self.pins = pins
        self.state = MotorState()
        
        # Configurar pines
        for pin in (pins.enable, pins.in1, pins.in2):
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 0)
        
        # Configurar PWM
        self.pi.set_PWM_frequency(pins.enable, pwm_freq)
        self.pi.set_PWM_dutycycle(pins.enable, 0)
    
    def _drive_pins(self, pin1_high: bool, pin2_high: bool) -> None:
        """Controla los pines de dirección del motor."""
        self.pi.write(self.pins.in1, 1 if pin1_high else 0)
        self.pi.write(self.pins.in2, 1 if pin2_high else 0)
    
    def set_direction(self, forward: bool, brake: bool = False) -> None:
        """Establece la dirección del motor."""
        if brake:
            self._drive_pins(True, True)
            self.state.direction = MotorDirection.BRAKE
            return
        
        # Aplicar inversión si está configurada
        actual_forward = forward ^ self.pins.invert
        
        if actual_forward:
            self._drive_pins(True, False)
            self.state.direction = MotorDirection.FORWARD
        else:
            self._drive_pins(False, True)
            self.state.direction = MotorDirection.BACKWARD
    
    def set_speed(self, speed_percent: float) -> None:
        """Establece la velocidad del motor (0-100%)."""
        speed_percent = max(0.0, min(100.0, speed_percent))
        duty_cycle = int(speed_percent * 2.55)  # Convertir a 0-255
        
        self.pi.set_PWM_dutycycle(self.pins.enable, duty_cycle)
        self.state.speed_percent = speed_percent
    
    def coast(self) -> None:
        """Pone el motor en modo coast (libre)."""
        self._drive_pins(False, False)
        self.pi.set_PWM_dutycycle(self.pins.enable, 0)
        self.state.direction = MotorDirection.COAST
        self.state.speed_percent = 0.0
    
    def get_state(self) -> MotorState:
        """Obtiene el estado actual del motor."""
        return self.state


class L298NController:
    """Controlador para dos motores L298N."""
    
    def __init__(self, motor_a_pins: MotorPins, motor_b_pins: MotorPins, pwm_freq: int = 1000):
        # Conectar a pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("❌ No puedo conectar a pigpio. Ejecuta: sudo systemctl enable --now pigpiod")
        
        # Crear motores
        self.motor_a = L298NMotor(self.pi, motor_a_pins, pwm_freq)
        self.motor_b = L298NMotor(self.pi, motor_b_pins, pwm_freq)
        
        # Registrar limpieza
        atexit.register(self._cleanup)
        signal.signal(signal.SIGINT, self._cleanup_signal)
        signal.signal(signal.SIGTERM, self._cleanup_signal)
    
    def get_motor_a(self) -> MotorInterface:
        """Obtiene el motor A (izquierdo)."""
        return self.motor_a
    
    def get_motor_b(self) -> MotorInterface:
        """Obtiene el motor B (derecho)."""
        return self.motor_b
    
    def stop_all(self) -> None:
        """Detiene todos los motores."""
        self.motor_a.coast()
        self.motor_b.coast()
    
    def _cleanup(self) -> None:
        """Limpieza de recursos."""
        try:
            self.stop_all()
        finally:
            if hasattr(self, 'pi'):
                self.pi.stop()
    
    def _cleanup_signal(self, signum, frame) -> None:
        """Manejo de señales para limpieza."""
        self._cleanup()
