#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Driver ZK-5AD (TA6586) Tank Drive - Específico para este módulo
Creado específicamente para el controlador dual ZK-5AD con chip TA6586
"""

import pigpio
import time
from typing import Tuple, Dict, Any
from dataclasses import dataclass
from config import get_config

@dataclass
class TA6586MotorStatus:
    """Estado de un motor en el controlador TA6586."""
    direction: str = "stop"
    power_percent: float = 0.0
    pwm_value: int = 0

class ZK5ADDriverTA6586:
    """Driver específico para ZK-5AD (TA6586) tank drive."""
    
    def __init__(self):
        """Inicializa el driver ZK-5AD."""
        self.pi = None
        self.is_initialized = False
        
        # Configuración de hardware
        config = get_config()
        hw_config = config['hardware']
        self.motor_a_config = hw_config.motor_a  # Motor izquierdo
        self.motor_b_config = hw_config.motor_b  # Motor derecho
        
        # Estado de motores
        self.motor_a_status = TA6586MotorStatus()
        self.motor_b_status = TA6586MotorStatus()
        
        # Configuración específica TA6586
        self.deadband = 0.05  # Zona muerta
        self.max_pwm = 255    # PWM máximo
        self.pwm_frequency = hw_config.pwm_frequency
        
        print("🚗 Driver ZK-5AD (TA6586) inicializado")
        print(f"   Motor A (Izq): GPIO {self.motor_a_config.in1}, {self.motor_a_config.in2}")
        print(f"   Motor B (Der): GPIO {self.motor_b_config.in1}, {self.motor_b_config.in2}")
        print(f"   PWM Frequency: {self.pwm_frequency} Hz")
    
    def initialize(self) -> bool:
        """Inicializa la conexión pigpio y configura los pines."""
        try:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                print("❌ No se pudo conectar a pigpio daemon")
                return False
            
            # Configurar pines como salida
            for motor_config in [self.motor_a_config, self.motor_b_config]:
                self.pi.set_mode(motor_config.in1, pigpio.OUTPUT)
                self.pi.set_mode(motor_config.in2, pigpio.OUTPUT)
                
                # Configurar frecuencia PWM si el pin lo soporta
                try:
                    self.pi.set_PWM_frequency(motor_config.in1, self.pwm_frequency)
                    self.pi.set_PWM_frequency(motor_config.in2, self.pwm_frequency)
                except Exception as e:
                    print(f"⚠️  Advertencia PWM frequency para GPIO {motor_config.in1}, {motor_config.in2}: {e}")
                
                # Inicializar en estado parado TA6586 (H+H = BRAKE)
                self.pi.set_PWM_dutycycle(motor_config.in1, 255)
                self.pi.set_PWM_dutycycle(motor_config.in2, 255)
            
            self.is_initialized = True
            print("✅ Driver ZK-5AD (TA6586) inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando driver ZK-5AD: {e}")
            return False
    
    def tank_drive(self, forward_backward: float, left_right: float, debug: bool = False) -> Tuple[int, int]:
        """
        Control de tank drive para ZK-5AD.
        
        Args:
            forward_backward: CH2 - Adelante/Atrás (-1.0 a 1.0)
            left_right: CH4 - Izquierda/Derecha (-1.0 a 1.0)
            debug: Mostrar información de debug
            
        Returns:
            Tupla (pwm_a, pwm_b) con valores PWM aplicados
        """
        if not self.pi or not self.pi.connected:
            return 0, 0
        
        # Aplicar zona muerta
        if abs(forward_backward) < self.deadband:
            forward_backward = 0.0
        if abs(left_right) < self.deadband:
            left_right = 0.0
        
        # LÓGICA TANK DRIVE:
        # forward_backward controla velocidad base
        # left_right modifica cada motor para girar
        
        # Calcular velocidades base
        left_speed = forward_backward   # Motor A (izquierdo)
        right_speed = forward_backward  # Motor B (derecho)
        
        # Aplicar giro
        if left_right > 0:  # Girar a la derecha
            left_speed += left_right    # Motor izq más rápido
            right_speed -= left_right   # Motor der más lento
        elif left_right < 0:  # Girar a la izquierda
            left_speed += left_right    # Motor izq más lento (left_right es negativo)
            right_speed -= left_right   # Motor der más rápido
        
        # Limitar velocidades a rango válido
        left_speed = max(-1.0, min(1.0, left_speed))
        right_speed = max(-1.0, min(1.0, right_speed))
        
        # Aplicar a motores
        pwm_a = self._set_ta6586_motor(left_speed, self.motor_a_config, 'A', debug)
        pwm_b = self._set_ta6586_motor(right_speed, self.motor_b_config, 'B', debug)
        
        if debug:
            print(f"🔧 TA6586 Control: Motor A PWM={pwm_a} | Motor B PWM={pwm_b}")
        
        return pwm_a, pwm_b
    
    def _set_ta6586_motor(self, speed: float, motor_config, motor_name: str, debug: bool = False) -> int:
        """
        Controla un motor individual en el TA6586.
        
        TA6586 Logic:
        - Para avanzar: IN1=PWM, IN2=0
        - Para retroceder: IN1=0, IN2=PWM  
        - Para parar: IN1=0, IN2=0
        
        Args:
            speed: Velocidad (-1.0 a 1.0)
            motor_config: Configuración del motor
            motor_name: 'A' o 'B'
            
        Returns:
            Valor PWM aplicado
        """
        # Parar si velocidad es cero - TA6586: H+H = BRAKE (frenado activo)
        if abs(speed) < self.deadband:
            self.pi.set_PWM_dutycycle(motor_config.in1, 255)  # HIGH
            self.pi.set_PWM_dutycycle(motor_config.in2, 255)  # HIGH
            
            # Actualizar estado
            if motor_name == 'A':
                self.motor_a_status = TA6586MotorStatus("brake", 0.0, 255)
            else:
                self.motor_b_status = TA6586MotorStatus("brake", 0.0, 255)
            
            if debug:
                print(f"🛑 TA6586 Motor {motor_name}: BRAKE (H+H)")
            
            return 255
        
        # Calcular PWM con factor de potencia
        pwm_final = int(abs(speed) * self.max_pwm * motor_config.power_factor)
        pwm_final = max(0, min(self.max_pwm, pwm_final))
        
        # TA6586 Logic: PWM en un pin, 0 en el otro para dirección
        if speed > 0:
            direction = "forward"
            if motor_config.invert:
                # Invertido: IN2=PWM, IN1=0
                self.pi.set_PWM_dutycycle(motor_config.in1, 0)
                self.pi.set_PWM_dutycycle(motor_config.in2, pwm_final)
                if debug:
                    print(f"▶️  TA6586 Motor {motor_name}: FORWARD (inverted) - IN1=0, IN2={pwm_final}")
            else:
                # Normal: IN1=PWM, IN2=0  
                self.pi.set_PWM_dutycycle(motor_config.in1, pwm_final)
                self.pi.set_PWM_dutycycle(motor_config.in2, 0)
                if debug:
                    print(f"▶️  TA6586 Motor {motor_name}: FORWARD - IN1={pwm_final}, IN2=0")
        else:
            direction = "backward"
            if motor_config.invert:
                # Invertido: IN1=PWM, IN2=0
                self.pi.set_PWM_dutycycle(motor_config.in1, pwm_final)
                self.pi.set_PWM_dutycycle(motor_config.in2, 0)
                if debug:
                    print(f"◀️  TA6586 Motor {motor_name}: BACKWARD (inverted) - IN1={pwm_final}, IN2=0")
            else:
                # Normal: IN2=PWM, IN1=0
                self.pi.set_PWM_dutycycle(motor_config.in1, 0)
                self.pi.set_PWM_dutycycle(motor_config.in2, pwm_final)
                if debug:
                    print(f"◀️  TA6586 Motor {motor_name}: BACKWARD - IN1=0, IN2={pwm_final}")
        
        # Actualizar estado
        power_percent = abs(speed) * 100
        if motor_name == 'A':
            self.motor_a_status = TA6586MotorStatus(direction, power_percent, pwm_final)
        else:
            self.motor_b_status = TA6586MotorStatus(direction, power_percent, pwm_final)
        
        return pwm_final
    
    def stop_motors(self):
        """Para ambos motores inmediatamente."""
        if not self.pi or not self.pi.connected:
            return
        
        for motor_config in [self.motor_a_config, self.motor_b_config]:
            # TA6586: H+H = BRAKE (parada activa)
            self.pi.set_PWM_dutycycle(motor_config.in1, 255)
            self.pi.set_PWM_dutycycle(motor_config.in2, 255)
        
        self.motor_a_status = TA6586MotorStatus("brake", 0.0, 255)
        self.motor_b_status = TA6586MotorStatus("brake", 0.0, 255)
        
        print("🛑 Motores TA6586 parados")
    
    def get_motor_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene el estado actual de los motores."""
        return {
            'motor_a': {
                'direction': self.motor_a_status.direction,
                'power_percent': self.motor_a_status.power_percent,
                'pwm_value': self.motor_a_status.pwm_value
            },
            'motor_b': {
                'direction': self.motor_b_status.direction,
                'power_percent': self.motor_b_status.power_percent,
                'pwm_value': self.motor_b_status.pwm_value
            }
        }
    
    def test_ta6586_drive(self):
        """Test específico para el TA6586."""
        if not self.is_initialized:
            print("❌ Driver ZK-5AD no inicializado")
            return
        
        print("\n🧪 Test ZK-5AD (TA6586) Tank Drive")
        
        test_cases = [
            (0.0, 0.0, "Parado"),
            (0.3, 0.0, "Adelante lento"),
            (0.7, 0.0, "Adelante rápido"),
            (-0.3, 0.0, "Atrás lento"),
            (-0.7, 0.0, "Atrás rápido"),
            (0.0, 0.5, "Giro derecha en el lugar"),
            (0.0, -0.5, "Giro izquierda en el lugar"),
            (0.5, 0.3, "Adelante + giro derecha"),
            (0.5, -0.3, "Adelante + giro izquierda"),
            (-0.5, 0.3, "Atrás + giro derecha"),
            (-0.5, -0.3, "Atrás + giro izquierda"),
        ]
        
        for forward_back, left_right, description in test_cases:
            print(f"\n📋 {description}")
            self.tank_drive(forward_back, left_right, debug=True)
            time.sleep(2.0)
        
        # Parar al final
        self.stop_motors()
        print("\n✅ Test TA6586 completado")
    
    def cleanup(self):
        """Limpia recursos."""
        if self.pi and self.pi.connected:
            self.stop_motors()
            self.pi.stop()
        print("🧹 Driver ZK-5AD (TA6586) limpiado")

# Test del driver
if __name__ == "__main__":
    driver = ZK5ADDriverTA6586()
    
    if driver.initialize():
        try:
            driver.test_ta6586_drive()
        except KeyboardInterrupt:
            print("\n🛑 Test interrumpido")
        finally:
            driver.cleanup()
    else:
        print("❌ No se pudo inicializar el driver ZK-5AD")