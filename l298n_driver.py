#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Driver L298N para control de motores con pigpio
Hardware: L298N + Raspberry Pi Zero 2W
"""

import pigpio
import time
from typing import Tuple
from config import get_config


class L298NDriver:
    """Driver para controlar motores DC mediante L298N con pigpio."""
    
    def __init__(self):
        """Inicializa la conexión pigpio y configura los pines."""
        self.config = get_config()
        self.hw_config = self.config["hardware"]
        
        # Conectar a pigpio daemon
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("No se pudo conectar al daemon pigpio")
        
        # Configurar pines como salida
        self._setup_pins()
        
        # Estado inicial: motores detenidos
        self.stop_all()
        
        print("L298N Driver inicializado correctamente")
    
    def _setup_pins(self):
        """Configura todos los pines como salida."""
        motor_a = self.hw_config.motor_a
        motor_b = self.hw_config.motor_b
        
        # Motor A
        self.pi.set_mode(motor_a.enable, pigpio.OUTPUT)
        self.pi.set_mode(motor_a.in1, pigpio.OUTPUT)
        self.pi.set_mode(motor_a.in2, pigpio.OUTPUT)
        
        # Motor B
        self.pi.set_mode(motor_b.enable, pigpio.OUTPUT)
        self.pi.set_mode(motor_b.in1, pigpio.OUTPUT)
        self.pi.set_mode(motor_b.in2, pigpio.OUTPUT)
        
        # Configurar PWM frequency y rango
        freq = self.hw_config.pwm_frequency
        
        # Motor A PWM setup
        self.pi.set_PWM_frequency(motor_a.enable, freq)
        self.pi.set_PWM_range(motor_a.enable, 255)  # Establecer rango 0-255
        
        # Motor B PWM setup  
        self.pi.set_PWM_frequency(motor_b.enable, freq)
        self.pi.set_PWM_range(motor_b.enable, 255)  # Establecer rango 0-255
        
        # Inicializar PWM en 0
        self.pi.set_PWM_dutycycle(motor_a.enable, 0)
        self.pi.set_PWM_dutycycle(motor_b.enable, 0)
        
        # Verificar configuración PWM
        self._verify_pwm_setup()
    
    def _verify_pwm_setup(self):
        """Verifica que la configuración PWM esté correcta."""
        motor_a = self.hw_config.motor_a
        motor_b = self.hw_config.motor_b
        
        print("🔍 Verificando configuración PWM...")
        
        # Verificar Motor A
        range_a = self.pi.get_PWM_range(motor_a.enable)
        freq_a = self.pi.get_PWM_frequency(motor_a.enable)
        print(f"   Motor A (pin {motor_a.enable}): Rango={range_a}, Freq={freq_a}Hz")
        
        # Verificar Motor B
        range_b = self.pi.get_PWM_range(motor_b.enable)
        freq_b = self.pi.get_PWM_frequency(motor_b.enable)
        print(f"   Motor B (pin {motor_b.enable}): Rango={range_b}, Freq={freq_b}Hz")
        
        # Verificar que los rangos sean correctos
        if range_a != 255 or range_b != 255:
            print(f"⚠️  Advertencia: Rangos PWM incorrectos (esperado 255)")
            return False
        
        print("✅ Configuración PWM verificada correctamente")
        return True
    
    def set_motor_speed(self, motor: str, speed: float):
        """
        Controla un motor específico.
        
        Args:
            motor: 'A' o 'B'
            speed: Velocidad entre -1.0 (atrás máx) y 1.0 (adelante máx)
        """
        if motor.upper() == 'A':
            motor_config = self.hw_config.motor_a
        elif motor.upper() == 'B':
            motor_config = self.hw_config.motor_b
        else:
            raise ValueError("Motor debe ser 'A' o 'B'")
        
        # Aplicar inversión si está configurada
        if motor_config.invert:
            speed = -speed
        
        # Limitar velocidad estrictamente entre -1.0 y 1.0
        speed = max(-1.0, min(1.0, speed))
        
        # Aplicar factor de calibración de potencia
        abs_speed = abs(speed)
        calibrated_speed = abs_speed * motor_config.power_factor
        
        # Asegurar que el valor calibrado no exceda 1.0
        calibrated_speed = min(1.0, calibrated_speed)
        
        # Convertir a PWM (0-255) con normalización segura
        pwm_value = int(calibrated_speed * 255)
        
        # Asegurar que PWM esté en rango válido (0-255)
        pwm_value = max(0, min(255, pwm_value))
        
        if speed > 0.01:  # Umbral mínimo para evitar ruido
            # Adelante
            self.pi.write(motor_config.in1, 1)
            self.pi.write(motor_config.in2, 0)
        elif speed < -0.01:  # Umbral mínimo para evitar ruido
            # Atrás
            self.pi.write(motor_config.in1, 0)
            self.pi.write(motor_config.in2, 1)
        else:
            # Parar (freno) - zona muerta
            self.pi.write(motor_config.in1, 0)
            self.pi.write(motor_config.in2, 0)
            pwm_value = 0  # Asegurar PWM 0 en parada
        
        # Aplicar PWM con verificación adicional
        try:
            # Verificar que el pin esté configurado correctamente
            current_range = self.pi.get_PWM_range(motor_config.enable)
            if current_range != 255:
                print(f"⚠️  Reconfigurando rango PWM pin {motor_config.enable}: {current_range} → 255")
                self.pi.set_PWM_range(motor_config.enable, 255)
            
            # Establecer PWM
            self.pi.set_PWM_dutycycle(motor_config.enable, pwm_value)
            
        except Exception as e:
            print(f"❌ Error estableciendo PWM {pwm_value} en pin {motor_config.enable}: {e}")
            print(f"   Rango actual: {self.pi.get_PWM_range(motor_config.enable)}")
            print(f"   Frecuencia: {self.pi.get_PWM_frequency(motor_config.enable)}")
            
            # Intentar reconfigurar completamente el pin
            try:
                print(f"🔧 Reconfigurando pin {motor_config.enable}...")
                self.pi.set_mode(motor_config.enable, pigpio.OUTPUT)
                self.pi.set_PWM_frequency(motor_config.enable, self.hw_config.pwm_frequency)
                self.pi.set_PWM_range(motor_config.enable, 255)
                self.pi.set_PWM_dutycycle(motor_config.enable, pwm_value)
                print(f"✅ Pin {motor_config.enable} reconfigurado correctamente")
            except Exception as e2:
                print(f"❌ Fallo crítico en pin {motor_config.enable}: {e2}")
                # Como último recurso, usar GPIO normal
                if pwm_value > 0:
                    self.pi.write(motor_config.enable, 1)
                else:
                    self.pi.write(motor_config.enable, 0)
    
    def set_motors(self, left_speed: float, right_speed: float):
        """
        Controla ambos motores simultáneamente.
        
        Args:
            left_speed: Velocidad motor izquierdo (-1.0 a 1.0)
            right_speed: Velocidad motor derecho (-1.0 a 1.0)
        """
        # Normalizar entradas antes de procesar
        left_speed = max(-1.0, min(1.0, left_speed))
        right_speed = max(-1.0, min(1.0, right_speed))
        
        self.set_motor_speed('A', left_speed)
        self.set_motor_speed('B', right_speed)
    
    def tank_drive(self, forward: float, turn: float):
        """
        Control tipo tanque: forward/backward + turn.
        
        Args:
            forward: Movimiento adelante/atrás (-1.0 a 1.0)
            turn: Giro izquierda/derecha (-1.0 a 1.0)
        """
        # Normalizar entradas
        forward = max(-1.0, min(1.0, forward))
        turn = max(-1.0, min(1.0, turn))
        
        # Calcular velocidades de cada motor
        left_speed = forward + turn
        right_speed = forward - turn
        
        # Normalizar si excede los límites (método mejorado)
        max_speed = max(abs(left_speed), abs(right_speed))
        if max_speed > 1.0:
            # Escalar proporcionalmente para mantener la dirección
            scale_factor = 1.0 / max_speed
            left_speed *= scale_factor
            right_speed *= scale_factor
        
        # Asegurar que están en rango después de la normalización
        left_speed = max(-1.0, min(1.0, left_speed))
        right_speed = max(-1.0, min(1.0, right_speed))
        
        self.set_motors(left_speed, right_speed)
    
    def stop_all(self):
        """Detiene todos los motores."""
        self.set_motors(0, 0)
    
    def coast_all(self):
        """Pone todos los motores en modo coast (libre)."""
        motor_a = self.hw_config.motor_a
        motor_b = self.hw_config.motor_b
        
        # Desactivar todas las señales
        for motor in [motor_a, motor_b]:
            self.pi.write(motor.in1, 0)
            self.pi.write(motor.in2, 0)
            self.pi.set_PWM_dutycycle(motor.enable, 0)
    
    def cleanup(self):
        """Limpia recursos y cierra conexión pigpio."""
        self.stop_all()
        time.sleep(0.1)
        self.pi.stop()
        print("L298N Driver cerrado correctamente")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


# Test del driver
if __name__ == "__main__":
    try:
        with L298NDriver() as driver:
            print("Probando motores...")
            
            # Test básico
            print("Adelante 50%")
            driver.tank_drive(0.5, 0)
            time.sleep(2)
            
            print("Giro derecha")
            driver.tank_drive(0, 0.5)
            time.sleep(1)
            
            print("Giro izquierda")
            driver.tank_drive(0, -0.5)
            time.sleep(1)
            
            print("Atrás 50%")
            driver.tank_drive(-0.5, 0)
            time.sleep(2)
            
            print("Parar")
            driver.stop_all()
            
    except KeyboardInterrupt:
        print("\nTest interrumpido por usuario")
    except Exception as e:
        print(f"Error en test: {e}")
