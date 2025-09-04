#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
L298N Driver Ultra-Optimizado para Raspberry Pi Zero 2W
Diseñado para eficiencia en dispositivos de bajos recursos
"""

import pigpio
import time
from typing import Optional
from config import get_config


class L298NDriverOptimized:
    """Driver L298N ultra-optimizado para RPi Zero 2W."""
    
    def __init__(self):
        """Inicialización mínima y eficiente."""
        self.config = get_config()
        self.hw_config = self.config["hardware"]
        
        # Conexión pigpio única
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio daemon no disponible")
        
        # Cache de configuración para evitar recálculos
        self._setup_hardware()
        self._cache_pwm_values()
        
        print("✅ L298N Driver optimizado iniciado")
        if self.hw_config.max_pwm_percent >= 100.0:
            print("   PWM: Sin límite - Potencia completa (0-255)")
        else:
            print(f"   PWM límite: {self.hw_config.max_pwm_percent}% = {self.max_pwm_value}/255")
        
    def _setup_hardware(self):
        """Configuración hardware una sola vez."""
        motor_a = self.hw_config.motor_a
        motor_b = self.hw_config.motor_b
        
        # Configurar todos los pines como OUTPUT
        pins = [motor_a.enable, motor_a.in1, motor_a.in2, 
                motor_b.enable, motor_b.in1, motor_b.in2]
        
        for pin in pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 0)  # Estado inicial LOW
        
        # Configurar PWM en pines ENABLE una sola vez
        freq = self.hw_config.pwm_frequency
        self.pi.set_PWM_frequency(motor_a.enable, freq)
        self.pi.set_PWM_frequency(motor_b.enable, freq)
        self.pi.set_PWM_range(motor_a.enable, 255)
        self.pi.set_PWM_range(motor_b.enable, 255)
        
        # Inicializar PWM en 0
        self.pi.set_PWM_dutycycle(motor_a.enable, 0)
        self.pi.set_PWM_dutycycle(motor_b.enable, 0)
        
    def _cache_pwm_values(self):
        """Pre-calcular valores PWM para optimización."""
        max_percent = self.hw_config.max_pwm_percent / 100.0
        self.max_pwm_value = int(255 * max_percent)
        
        # Cache de factores de potencia
        self.motor_a_factor = self.hw_config.motor_a.power_factor
        self.motor_b_factor = self.hw_config.motor_b.power_factor
        
    def _set_motor_raw(self, motor_pins, speed: float, power_factor: float):
        """
        Control directo de motor optimizado.
        
        Args:
            motor_pins: Configuración de pines del motor
            speed: Velocidad (-1.0 a 1.0)
            power_factor: Factor de calibración
        """
        # Aplicar inversión si está configurada
        if motor_pins.invert:
            speed = -speed
            
        # Limitar entrada
        speed = max(-1.0, min(1.0, speed))
        
        # Calcular PWM (siempre positivo)
        abs_speed = abs(speed)
        calibrated_speed = abs_speed * power_factor
        # NO limitar calibrated_speed para permitir power_factor > 1.0
        
        # Aplicar límite PWM máximo y convertir a entero
        pwm_value = int(calibrated_speed * self.max_pwm_value)
        pwm_value = max(0, min(self.max_pwm_value, pwm_value))  # Limitar al PWM máximo permitido
        
        # Aplicar inversión PWM si está configurada
        if motor_pins.pwm_inverted:
            pwm_value = self.max_pwm_value - pwm_value  # Invertir: 0→255, 255→0
        
        # Control de dirección optimizado (solo cambiar cuando sea necesario)
        if speed > 0.01:  # Adelante
            self.pi.write(motor_pins.in1, 1)
            self.pi.write(motor_pins.in2, 0)
        elif speed < -0.01:  # Atrás
            self.pi.write(motor_pins.in1, 0)
            self.pi.write(motor_pins.in2, 1)
        else:  # Parar (freno)
            self.pi.write(motor_pins.in1, 0)
            self.pi.write(motor_pins.in2, 0)
            pwm_value = 0
        
        # Aplicar PWM
        self.pi.set_PWM_dutycycle(motor_pins.enable, pwm_value)
        
        # Debug: mostrar valores de PWM aplicados
        if abs(speed) > 0.01:
            direction = "ADELANTE" if speed > 0 else "ATRÁS"
            motor_name = "A(izq)" if motor_pins.enable == 12 else "B(der)"
            pwm_info = f"PWM {pwm_value}/{self.max_pwm_value}"
            if motor_pins.pwm_inverted:
                original_pwm = self.max_pwm_value - pwm_value
                pwm_info += f" (invertido desde {original_pwm})"
            print(f"🔧 Motor {motor_name}: speed={speed:.2f} × factor={power_factor} = {pwm_info} [{direction}]")
        
        return pwm_value
        
    def set_motor_a(self, speed: float):
        """Control Motor A (izquierdo)."""
        return self._set_motor_raw(self.hw_config.motor_a, speed, self.motor_a_factor)
        
    def set_motor_b(self, speed: float):
        """Control Motor B (derecho).""" 
        return self._set_motor_raw(self.hw_config.motor_b, speed, self.motor_b_factor)
        
    def set_motors(self, left_speed: float, right_speed: float):
        """Control ambos motores simultáneamente."""
        # Normalizar entradas una sola vez
        left_speed = max(-1.0, min(1.0, left_speed))
        right_speed = max(-1.0, min(1.0, right_speed))
        
        # Aplicar a motores
        pwm_a = self.set_motor_a(left_speed)
        pwm_b = self.set_motor_b(right_speed)
        
        return pwm_a, pwm_b
        
    def tank_drive(self, forward: float, turn: float, debug: bool = False):
        """
        Control tank drive optimizado y corregido.
        
        Args:
            forward: Adelante/atrás (-1.0 a 1.0)
            turn: Giro (-1.0=izq, +1.0=der)
            debug: Mostrar información de debug
        """
        # Normalizar entradas
        forward = max(-1.0, min(1.0, forward))
        turn = max(-1.0, min(1.0, turn))
        
        # Algoritmo tank drive corregido (giros invertidos)
        left_speed = forward + turn   # Giro derecha (+turn) = motor izq más rápido
        right_speed = forward - turn  # Giro derecha (+turn) = motor der más lento
        
        # Normalización proporcional si excede límites
        max_magnitude = max(abs(left_speed), abs(right_speed))
        if max_magnitude > 1.0:
            scale = 1.0 / max_magnitude
            left_speed *= scale
            right_speed *= scale
            
        # Clamp final
        left_speed = max(-1.0, min(1.0, left_speed))
        right_speed = max(-1.0, min(1.0, right_speed))
        
        if debug:
            print(f"Tank: fwd={forward:.2f}, turn={turn:.2f} → L={left_speed:.2f}, R={right_speed:.2f}")
        
        return self.set_motors(left_speed, right_speed)
        
    def stop(self):
        """Parada rápida."""
        self.pi.write(self.hw_config.motor_a.in1, 0)
        self.pi.write(self.hw_config.motor_a.in2, 0)
        self.pi.write(self.hw_config.motor_b.in1, 0)
        self.pi.write(self.hw_config.motor_b.in2, 0)
        self.pi.set_PWM_dutycycle(self.hw_config.motor_a.enable, 0)
        self.pi.set_PWM_dutycycle(self.hw_config.motor_b.enable, 0)
        
    def coast(self):
        """Modo coast (rueda libre)."""
        self.stop()  # En L298N, stop y coast son equivalentes
        
    def cleanup(self):
        """Limpieza de recursos."""
        self.stop()
        if self.pi.connected:
            self.pi.stop()


# Función de test para verificar funcionamiento
def test_driver():
    """Test rápido del driver optimizado."""
    print("🧪 Test L298N Driver Optimizado")
    
    try:
        driver = L298NDriverOptimized()
        
        print("\n1. Test motores individuales:")
        print("Motor A adelante 50%")
        driver.set_motor_a(0.5)
        time.sleep(1)
        
        print("Motor A atrás 50%")
        driver.set_motor_a(-0.5)
        time.sleep(1)
        
        print("Motor B adelante 50%")
        driver.set_motor_b(0.5)
        time.sleep(1)
        
        print("Motor B atrás 50%")
        driver.set_motor_b(-0.5)
        time.sleep(1)
        
        print("\n2. Test tank drive:")
        print("Adelante")
        driver.tank_drive(0.5, 0, debug=True)
        time.sleep(1)
        
        print("Giro derecha")
        driver.tank_drive(0.5, 0.5, debug=True)
        time.sleep(1)
        
        print("Giro izquierda")
        driver.tank_drive(0.5, -0.5, debug=True)
        time.sleep(1)
        
        print("Giro en sitio derecha")
        driver.tank_drive(0, 0.7, debug=True)
        time.sleep(1)
        
        print("Parar")
        driver.stop()
        
    except KeyboardInterrupt:
        print("\nTest interrumpido")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'driver' in locals():
            driver.cleanup()


if __name__ == "__main__":
    test_driver()
