#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Driver L298N ULTRA-OPTIMIZADO para latencia mínima.
Elimina verificaciones innecesarias y optimiza el acceso directo a GPIO.
"""

import pigpio
from typing import Optional

from ..hardware.motor_interface import MotorInterface, DualMotorInterface, MotorDirection, MotorState
from ..config.settings import MotorPins


class UltraFastMotor(MotorInterface):
    """Motor ultra-optimizado sin verificaciones innecesarias."""
    
    __slots__ = ['pi', 'enable_pin', 'in1_pin', 'in2_pin', 'invert', '_direction', '_speed']
    
    def __init__(self, pi: pigpio.pi, pins: MotorPins, pwm_freq: int = 20000):
        self.pi = pi
        self.enable_pin = pins.enable
        self.in1_pin = pins.in1
        self.in2_pin = pins.in2
        self.invert = pins.invert
        self._direction = MotorDirection.FORWARD
        self._speed = 0.0
        
        # Configurar pines directamente sin verificaciones
        pi.set_mode(self.enable_pin, pigpio.OUTPUT)
        pi.set_mode(self.in1_pin, pigpio.OUTPUT)
        pi.set_mode(self.in2_pin, pigpio.OUTPUT)
        
        # Configurar PWM ultra-alto
        pi.set_PWM_frequency(self.enable_pin, pwm_freq)
        pi.set_PWM_range(self.enable_pin, 100)
        
        # Estado inicial
        pi.write(self.in1_pin, 0)
        pi.write(self.in2_pin, 0)
        pi.set_PWM_dutycycle(self.enable_pin, 0)
    
    def set_direction(self, forward: bool, brake: bool = False) -> None:
        """Configurar dirección ultra-rápida."""
        if brake:
            # Freno inmediato
            self.pi.write(self.in1_pin, 1)
            self.pi.write(self.in2_pin, 1)
            self._direction = MotorDirection.BRAKE
            return
        
        # Aplicar inversión si es necesario
        actual_forward = forward if not self.invert else not forward
        
        if actual_forward:
            self.pi.write(self.in1_pin, 1)
            self.pi.write(self.in2_pin, 0)
            self._direction = MotorDirection.FORWARD
        else:
            self.pi.write(self.in1_pin, 0)
            self.pi.write(self.in2_pin, 1)
            self._direction = MotorDirection.REVERSE
    
    def set_speed(self, speed_percent: float) -> None:
        """Configurar velocidad ultra-rápida."""
        # Clamp directo sin verificaciones extra
        if speed_percent > 100.0:
            speed_percent = 100.0
        elif speed_percent < 0.0:
            speed_percent = 0.0
        
        self._speed = speed_percent
        self.pi.set_PWM_dutycycle(self.enable_pin, int(speed_percent))
    
    def coast(self) -> None:
        """Parada libre ultra-rápida."""
        self.pi.write(self.in1_pin, 0)
        self.pi.write(self.in2_pin, 0)
        self.pi.set_PWM_dutycycle(self.enable_pin, 0)
        self._direction = MotorDirection.COAST
        self._speed = 0.0
    
    def brake(self) -> None:
        """Freno ultra-rápido."""
        self.pi.write(self.in1_pin, 1)
        self.pi.write(self.in2_pin, 1)
        self.pi.set_PWM_dutycycle(self.enable_pin, 100)
        self._direction = MotorDirection.BRAKE
        self._speed = 0.0
    
    def get_state(self) -> MotorState:
        """Estado actual."""
        return MotorState(
            direction=self._direction,
            speed_percent=self._speed,
            timestamp=0.0  # Sin timestamp para mayor velocidad
        )


class UltraFastL298NController(DualMotorInterface):
    """Controlador L298N ultra-optimizado."""
    
    __slots__ = ['pi', 'motor_a', 'motor_b', '_initialized']
    
    def __init__(self, config_motor_a: MotorPins, config_motor_b: MotorPins, 
                 pwm_freq: int = 20000, debug: bool = False):
        # Conexión directa a pigpio sin verificaciones
        self.pi = pigpio.pi()
        
        if debug:
            print(f"⚡ ULTRA L298N: PWM={pwm_freq}Hz")
        
        # Crear motores ultra-optimizados
        self.motor_a = UltraFastMotor(self.pi, config_motor_a, pwm_freq)
        self.motor_b = UltraFastMotor(self.pi, config_motor_b, pwm_freq)
        self._initialized = True
    
    def get_motor_a(self) -> MotorInterface:
        return self.motor_a
    
    def get_motor_b(self) -> MotorInterface:
        return self.motor_b
    
    def stop_all(self) -> None:
        """Parar todos los motores inmediatamente."""
        self.motor_a.coast()
        self.motor_b.coast()
    
    def brake_all(self) -> None:
        """Frenar todos los motores inmediatamente."""
        self.motor_a.brake()
        self.motor_b.brake()
    
    def __del__(self):
        """Cleanup ultrarrápido."""
        if hasattr(self, '_initialized') and self._initialized:
            self.stop_all()
            if hasattr(self, 'pi'):
                self.pi.stop()


# Alias para compatibilidad
L298NControllerOptimized = UltraFastL298NController
