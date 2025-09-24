#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuración ANTI-INTERFERENCIA para T100 Controller
Separación física y temporal de canales PWM para eliminar interferencias
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
    """Configuración ANTI-INTERFERENCIA del hardware."""
    # Motores para tank drive (campos requeridos primero)
    motor_a: MotorPins  # Motor izquierdo
    motor_b: MotorPins  # Motor derecho
    servo_pan: ServoConfig   # Servo horizontal (CH4)
    servo_tilt: ServoConfig  # Servo vertical (CH3)
    
    # Campos con valores por defecto - CONFIGURACIÓN ANTI-INTERFERENCIA
    pwm_frequency: int = 2000  # Reducida para menor interferencia
    max_pwm_percent: float = 90  # Limitado para reducir ruido eléctrico
    direction_change_delay: float = 0.100  # Aumentado para estabilidad
    enable_direction_protection: bool = True
    
    # NUEVOS PARÁMETROS ANTI-INTERFERENCIA
    servo_update_interval: float = 0.050  # 50ms entre updates de servos (20Hz)
    motor_update_interval: float = 0.020  # 20ms entre updates de motores (50Hz)
    enable_temporal_separation: bool = True  # Separación temporal de actualizaciones


# CONFIGURACIÓN ANTI-INTERFERENCIA - MÁXIMA SEPARACIÓN FÍSICA
#
# ESTRATEGIA: Separar físicamente los canales PWM lo máximo posible
# 
# MAPEO GPIO OPTIMIZADO (SEPARACIÓN FÍSICA):
#
#     [SERVO TILT - GPIO 4]    <- Esquina opuesta, lejos de motores
#         │
#     [SERVO PAN - GPIO 17]    <- Pin de power rail, aislado
#         │
#     ORUGA IZQ        ORUGA DER
#         ▲               ▲
#    [MOTOR A]  ◄─H─►  [MOTOR B]
#         │               │  
#    (GPIO 18,24)    (GPIO 19,25)  <- HW-PWM + Digital separados
#
# VENTAJAS DE ESTA CONFIGURACIÓN:
# 1. GPIO 18/19: Hardware PWM dedicado (PWM0/PWM1)
# 2. GPIO 24/25: Pines digitales en esquina opuesta
# 3. GPIO 4/17: Servos en rail de alimentación, físicamente separados
# 4. Máxima distancia física entre todos los canales
# 5. Frecuencias PWM reducidas para menor EMI
#
# CONTROLES ELRS (sin cambios):  
# - CH1: Rotación tank (izquierda/derecha)
# - CH2: Aceleración tank (adelante/atrás)
# - CH3: Tilt cámara (arriba/abajo)
# - CH4: Pan cámara (izquierda/derecha)
#
DEFAULT_CONFIG_ANTI_INTERFERENCE = {
    "hardware": HardwareConfig(
        # Motores - Hardware PWM dedicado + digitales separados
        motor_a=MotorPins(in1=18, in2=24, invert=False, power_factor=0.9),  # PWM0 + GPIO24 (esquina opuesta)
        motor_b=MotorPins(in1=19, in2=25, invert=True, power_factor=0.9),   # PWM1 + GPIO25 (esquina opuesta)
        
        # Servos - En power rail, máxima separación
        servo_pan=ServoConfig(gpio_pin=17, name="Pan", invert=True),    # GPIO17 - Power rail
        servo_tilt=ServoConfig(gpio_pin=4, name="Tilt", invert=True),   # GPIO4 - Power rail, esquina opuesta
        
        # Configuración anti-interferencia
        pwm_frequency=2000,           # Reducida para menor EMI
        max_pwm_percent=90.0,         # Limitada para menos ruido
        direction_change_delay=0.100, # Aumentado para estabilidad
        enable_direction_protection=True,
        
        # Separación temporal
        servo_update_interval=0.050,     # Servos a 20Hz
        motor_update_interval=0.020,     # Motores a 50Hz  
        enable_temporal_separation=True  # Activar separación temporal
    )
}


def get_anti_interference_config() -> dict:
    """Retorna la configuración anti-interferencia."""
    return DEFAULT_CONFIG_ANTI_INTERFERENCE


if __name__ == "__main__":
    print("🛡️  CONFIGURACIÓN ANTI-INTERFERENCIA T100")
    print("=" * 50)
    
    config = get_anti_interference_config()
    hw = config['hardware']
    
    print("\n🚗 MOTORES (Hardware PWM + Digitales separados):")
    print(f"   Motor A: GPIO {hw.motor_a.in1} (PWM0) + GPIO {hw.motor_a.in2} (Digital)")
    print(f"   Motor B: GPIO {hw.motor_b.in1} (PWM1) + GPIO {hw.motor_b.in2} (Digital)")
    print(f"   PWM Frecuencia: {hw.pwm_frequency} Hz (reducida)")
    print(f"   Potencia máxima: {hw.max_pwm_percent}% (limitada)")
    
    print("\n📹 SERVOS (Power rail, máxima separación):")
    print(f"   Pan:  GPIO {hw.servo_pan.gpio_pin} (Power rail)")
    print(f"   Tilt: GPIO {hw.servo_tilt.gpio_pin} (Power rail, esquina opuesta)")
    
    print("\n⏱️  SEPARACIÓN TEMPORAL:")
    print(f"   Servos: {hw.servo_update_interval*1000:.0f}ms entre updates")
    print(f"   Motores: {hw.motor_update_interval*1000:.0f}ms entre updates")
    print(f"   Separación activada: {hw.enable_temporal_separation}")
    
    print("\n🎯 VENTAJAS:")
    print("   ✅ Máxima separación física entre canales")
    print("   ✅ Hardware PWM dedicado para motores")
    print("   ✅ Servos en power rail aislado")
    print("   ✅ Frecuencias PWM reducidas (menos EMI)")
    print("   ✅ Separación temporal de actualizaciones")
    print("   ✅ Potencia limitada (menos ruido eléctrico)")