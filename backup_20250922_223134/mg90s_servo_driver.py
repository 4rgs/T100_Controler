#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Driver para Servos MG90S - Control de cámara Pan/Tilt
Diseñado para controlar servos MG90S con joystick izquierdo
"""

import pigpio
import time
from typing import Tuple, Dict, Any
from dataclasses import dataclass
from config import get_config

@dataclass
class ServoStatus:
    """Estado de un servo MG90S."""
    position_degrees: float = 90.0  # Posición actual en grados (0-180)
    pulse_width: int = 1500        # Ancho de pulso actual en microsegundos
    name: str = "servo"            # Nombre del servo

class MG90SServoDriver:
    """Driver específico para servos MG90S."""
    
    def __init__(self):
        """Inicializa el driver de servos MG90S."""
        self.pi = None
        self.is_initialized = False
        
        # Configuración de hardware
        config = get_config()
        hw_config = config['hardware']
        self.servo_pan_config = hw_config.servo_pan    # Servo horizontal
        self.servo_tilt_config = hw_config.servo_tilt  # Servo vertical
        
        # Estado de servos
        self.servo_pan_status = ServoStatus(name="Pan")
        self.servo_tilt_status = ServoStatus(name="Tilt")
        
        # Configuración específica MG90S
        self.servo_frequency = 50  # 50Hz para servos estándar
        
        print("📹 Driver Servos MG90S inicializado")
        print(f"   Servo Pan: GPIO {self.servo_pan_config.gpio_pin} (CH4 - Pan cámara izq/der)")
        print(f"   Servo Tilt: GPIO {self.servo_tilt_config.gpio_pin} (CH3 - Tilt cámara arriba/abajo)")
    
    def initialize(self) -> bool:
        """Inicializa la conexión pigpio y configura servos."""
        try:
            # Conectar a pigpio daemon
            self.pi = pigpio.pi()
            if not self.pi.connected:
                print("❌ No se pudo conectar a pigpio daemon para servos")
                return False
            
            # Configurar pines como OUTPUT
            self.pi.set_mode(self.servo_pan_config.gpio_pin, pigpio.OUTPUT)
            self.pi.set_mode(self.servo_tilt_config.gpio_pin, pigpio.OUTPUT)
            
            # Configurar frecuencia PWM para servos (50Hz)
            try:
                self.pi.set_PWM_frequency(self.servo_pan_config.gpio_pin, self.servo_frequency)
                self.pi.set_PWM_frequency(self.servo_tilt_config.gpio_pin, self.servo_frequency)
            except Exception as e:
                print(f"⚠️  Advertencia configurando frecuencia servos: {e}")
            
            # Posicionar servos en centro al inicio
            self._set_servo_center(self.servo_pan_config, "Pan")
            self._set_servo_center(self.servo_tilt_config, "Tilt")
            
            self.is_initialized = True
            print("✅ Driver Servos MG90S inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando servos MG90S: {e}")
            return False
    
    def _set_servo_center(self, servo_config, servo_name: str):
        """Posiciona un servo en el centro (90°)."""
        try:
            self.pi.set_servo_pulsewidth(servo_config.gpio_pin, servo_config.center_pulse)
            print(f"   {servo_name}: Centro ({servo_config.center_pulse}µs)")
        except Exception as e:
            print(f"   ❌ Error centrando servo {servo_name}: {e}")
    
    def control_camera(self, pan_input: int, tilt_input: int, debug: bool = False) -> Tuple[float, float]:
        """
        Controla los servos de la cámara con inputs del joystick izquierdo.
        
        Args:
            pan_input: Valor raw CH1 (joystick izquierdo horizontal) - típicamente 172-1811
            tilt_input: Valor raw CH3 (joystick izquierdo vertical) - típicamente 172-1811
            debug: Mostrar información de debug
            
        Returns:
            Tupla (pan_degrees, tilt_degrees) con posiciones actuales
        """
        if not self.pi or not self.pi.connected:
            return 90.0, 90.0
        
        # Convertir inputs raw a ángulos de servo (0-180°)
        pan_degrees = self._raw_to_servo_angle(pan_input, self.servo_pan_config)
        tilt_degrees = self._raw_to_servo_angle(tilt_input, self.servo_tilt_config)
        
        # Aplicar control a servos
        pan_pulse = self._set_servo_angle(self.servo_pan_config, pan_degrees, "Pan", debug)
        tilt_pulse = self._set_servo_angle(self.servo_tilt_config, tilt_degrees, "Tilt", debug)
        
        # Actualizar estado
        self.servo_pan_status = ServoStatus(pan_degrees, pan_pulse, "Pan")
        self.servo_tilt_status = ServoStatus(tilt_degrees, tilt_pulse, "Tilt")
        
        if debug:
            print(f"📹 Cámara: Pan={pan_degrees:.1f}° ({pan_pulse}µs) | Tilt={tilt_degrees:.1f}° ({tilt_pulse}µs)")
        
        return pan_degrees, tilt_degrees
    
    def _raw_to_servo_angle(self, raw_value: int, servo_config) -> float:
        """
        Convierte valor raw del ELRS a ángulo de servo (0-180°).
        
        Args:
            raw_value: Valor raw del ELRS (172-1811)
            servo_config: Configuración del servo
            
        Returns:
            Ángulo en grados (0-180°)
        """
        # Valores típicos ELRS
        min_raw = 172
        max_raw = 1811
        
        # Normalizar a 0.0-1.0
        normalized = (raw_value - min_raw) / (max_raw - min_raw)
        normalized = max(0.0, min(1.0, normalized))  # Limitar rango
        
        # Convertir a ángulo de servo (0-180°)
        angle = normalized * 180.0
        
        # Aplicar inversión si está configurada
        if servo_config.invert:
            angle = 180.0 - angle
        
        return angle
    
    def _set_servo_angle(self, servo_config, angle_degrees: float, servo_name: str, debug: bool = False) -> int:
        """
        Posiciona un servo en el ángulo especificado.
        
        Args:
            servo_config: Configuración del servo
            angle_degrees: Ángulo deseado (0-180°)
            servo_name: Nombre del servo para debug
            debug: Mostrar información de debug
            
        Returns:
            Ancho de pulso aplicado en microsegundos
        """
        # Limitar ángulo a rango válido
        angle_degrees = max(0.0, min(180.0, angle_degrees))
        
        # Convertir ángulo a ancho de pulso
        # 0° = min_pulse, 90° = center_pulse, 180° = max_pulse
        pulse_range = servo_config.max_pulse - servo_config.min_pulse
        pulse_width = servo_config.min_pulse + (angle_degrees / 180.0) * pulse_range
        pulse_width = int(pulse_width)
        
        # Aplicar pulso al servo
        try:
            self.pi.set_servo_pulsewidth(servo_config.gpio_pin, pulse_width)
            
            if debug:
                print(f"   {servo_name}: {angle_degrees:.1f}° -> {pulse_width}µs")
            
            return pulse_width
            
        except Exception as e:
            print(f"❌ Error controlando servo {servo_name}: {e}")
            return servo_config.center_pulse
    
    def center_servos(self):
        """Centra ambos servos (posición 90°)."""
        if not self.pi or not self.pi.connected:
            return
        
        print("📹 Centrando servos de cámara...")
        self._set_servo_center(self.servo_pan_config, "Pan")
        self._set_servo_center(self.servo_tilt_config, "Tilt")
        
        # Actualizar estado
        self.servo_pan_status = ServoStatus(90.0, self.servo_pan_config.center_pulse, "Pan")
        self.servo_tilt_status = ServoStatus(90.0, self.servo_tilt_config.center_pulse, "Tilt")
    
    def get_servo_status(self) -> Dict[str, ServoStatus]:
        """Retorna el estado actual de los servos."""
        return {
            'pan': self.servo_pan_status,
            'tilt': self.servo_tilt_status
        }
    
    def cleanup(self):
        """Limpia recursos y centra servos."""
        print("🧹 Limpiando servos MG90S...")
        
        if self.pi and self.pi.connected:
            # Centrar servos antes de limpiar
            self.center_servos()
            time.sleep(0.5)  # Dar tiempo a los servos
            
            # Desactivar PWM
            try:
                self.pi.set_servo_pulsewidth(self.servo_pan_config.gpio_pin, 0)
                self.pi.set_servo_pulsewidth(self.servo_tilt_config.gpio_pin, 0)
            except:
                pass
            
            self.pi.stop()
        
        self.is_initialized = False
        print("✅ Servos MG90S limpiados")


# Test de servos
def test_servos():
    """Test básico de servos MG90S."""
    print("📹 Test Servos MG90S")
    
    driver = MG90SServoDriver()
    
    if not driver.initialize():
        print("❌ No se pudo inicializar driver de servos")
        return
    
    try:
        print("\n🔄 Test de movimientos...")
        
        # Test posiciones extremas
        positions = [
            (172, 172, "Esquina inferior izquierda"),
            (1811, 172, "Esquina inferior derecha"), 
            (1811, 1811, "Esquina superior derecha"),
            (172, 1811, "Esquina superior izquierda"),
            (992, 992, "Centro"),
        ]
        
        for pan_raw, tilt_raw, desc in positions:
            print(f"\n📍 {desc}:")
            pan_deg, tilt_deg = driver.control_camera(pan_raw, tilt_raw, debug=True)
            time.sleep(1.5)
        
        print("\n✅ Test de servos completado")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido")
    finally:
        driver.cleanup()


if __name__ == "__main__":
    test_servos()