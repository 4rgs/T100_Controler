#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Driver L298N optimizado para mínimo uso de recursos.
"""

import atexit
import signal
import time
from typing import Optional

import pigpio

from ..config.settings import MotorPins
from .motor_interface import MotorInterface, MotorState, MotorDirection


class L298NMotorOptimized(MotorInterface):
    """Motor individual optimizado para bajo consumo de recursos."""
    
    __slots__ = ['pi', 'pins', 'state', '_last_direction', '_last_speed']
    
    def __init__(self, pi_instance: pigpio.pi, pins: MotorPins, pwm_freq: int = 1000):
        self.pi = pi_instance
        self.pins = pins
        self.state = MotorState()
        self._last_direction = None
        self._last_speed = 0.0
        
        # Configurar pines una sola vez
        for pin in (pins.enable, pins.in1, pins.in2):
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 0)
        
        # Configurar PWM una sola vez
        self.pi.set_PWM_frequency(pins.enable, pwm_freq)
        self.pi.set_PWM_dutycycle(pins.enable, 0)
    
    def _drive_pins_fast(self, pin1_high: bool, pin2_high: bool) -> None:
        """Controla los pines de dirección sin logging para máximo rendimiento."""
        self.pi.write(self.pins.in1, 1 if pin1_high else 0)
        self.pi.write(self.pins.in2, 1 if pin2_high else 0)
    
    def set_direction(self, forward: bool, brake: bool = False) -> None:
        """Establece la dirección solo si cambió."""
        direction = "brake" if brake else ("fwd" if forward else "back")
        
        # Optimización: solo cambiar si la dirección es diferente
        if self._last_direction == direction:
            return
            
        # Parar PWM antes del cambio
        self.pi.set_PWM_dutycycle(self.pins.enable, 0)
        
        if brake:
            self._drive_pins_fast(True, True)
            self.state.direction = MotorDirection.BRAKE
        else:
            actual_forward = forward ^ self.pins.invert
            if actual_forward:
                self._drive_pins_fast(True, False)
                self.state.direction = MotorDirection.FORWARD
            else:
                self._drive_pins_fast(False, True)
                self.state.direction = MotorDirection.BACKWARD
        
        self._last_direction = direction
    
    def set_speed(self, speed_percent: float) -> None:
        """Establece la velocidad solo si cambió significativamente."""
        speed_percent = max(0.0, min(100.0, speed_percent))
        
        # Optimización: solo cambiar si la diferencia es significativa (>1%)
        if abs(speed_percent - self._last_speed) < 1.0:
            return
            
        duty_cycle = int(speed_percent * 2.55)
        self.pi.set_PWM_dutycycle(self.pins.enable, duty_cycle)
        self.state.speed_percent = speed_percent
        self._last_speed = speed_percent
    
    def coast(self) -> None:
        """Modo coast optimizado."""
        if self._last_direction == "coast" and self._last_speed == 0.0:
            return  # Ya está en coast
            
        self._drive_pins_fast(False, False)
        self.pi.set_PWM_dutycycle(self.pins.enable, 0)
        self.state.direction = MotorDirection.COAST
        self.state.speed_percent = 0.0
        self._last_direction = "coast"
        self._last_speed = 0.0
    
    def get_state(self) -> MotorState:
        """Obtiene el estado actual del motor."""
        return self.state


class L298NControllerOptimized:
    """Controlador optimizado para dos motores L298N."""
    
    __slots__ = ['pi', 'motor_a', 'motor_b']
    
    def __init__(self, motor_a_pins: MotorPins, motor_b_pins: MotorPins, pwm_freq: int = 1000):
        # Conectar a pigpio
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("No se puede conectar a pigpio")
        
        # Crear motores optimizados
        self.motor_a = L298NMotorOptimized(self.pi, motor_a_pins, pwm_freq)
        self.motor_b = L298NMotorOptimized(self.pi, motor_b_pins, pwm_freq)
        
        # Registrar limpieza
        atexit.register(self._cleanup)
        signal.signal(signal.SIGINT, self._cleanup_signal)
        signal.signal(signal.SIGTERM, self._cleanup_signal)
    
    def get_motor_a(self) -> MotorInterface:
        return self.motor_a
    
    def get_motor_b(self) -> MotorInterface:
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
