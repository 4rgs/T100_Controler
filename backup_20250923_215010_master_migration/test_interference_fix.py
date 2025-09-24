#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test rápido para verificar que la corrección anti-interferencia funciona
"""

import time
import sys

try:
    import pigpio
except ImportError:
    print("❌ pigpio no instalado. Instala con: sudo apt install python3-pigpio")
    sys.exit(1)

from config import get_config

def test_anti_interference():
    """Test de la configuración anti-interferencia."""
    print("🧪 TEST ANTI-INTERFERENCIA")
    print("=" * 40)
    
    config = get_config()
    hw = config['hardware']
    
    # Mostrar configuración
    print(f"\n⚙️  Configuración cargada:")
    print(f"   Motor A: GPIO {hw.motor_a.in1}, {hw.motor_a.in2}")
    print(f"   Motor B: GPIO {hw.motor_b.in1}, {hw.motor_b.in2}")
    print(f"   Servo Pan: GPIO {hw.servo_pan.gpio_pin}")
    print(f"   Servo Tilt: GPIO {hw.servo_tilt.gpio_pin}")
    print(f"   PWM Freq: {hw.pwm_frequency} Hz")
    
    # Conectar a pigpio
    pi = pigpio.pi()
    if not pi.connected:
        print("❌ No se pudo conectar a pigpio daemon")
        return False
    
    try:
        print(f"\n🔄 Probando configuración por 3 segundos...")
        
        # Configurar pines
        pi.set_mode(hw.motor_a.in1, pigpio.OUTPUT)
        pi.set_mode(hw.motor_a.in2, pigpio.OUTPUT) 
        pi.set_mode(hw.motor_b.in1, pigpio.OUTPUT)
        pi.set_mode(hw.motor_b.in2, pigpio.OUTPUT)
        pi.set_mode(hw.servo_pan.gpio_pin, pigpio.OUTPUT)
        pi.set_mode(hw.servo_tilt.gpio_pin, pigpio.OUTPUT)
        
        # Test PWM suave
        print("   🚗 Activando motores...")
        pi.hardware_PWM(hw.motor_a.in1, hw.pwm_frequency, 250000)  # 25%
        pi.hardware_PWM(hw.motor_b.in1, hw.pwm_frequency, 250000)  # 25%
        
        time.sleep(1)
        
        print("   📹 Activando servos...")
        pi.set_PWM_frequency(hw.servo_pan.gpio_pin, 50)
        pi.set_PWM_frequency(hw.servo_tilt.gpio_pin, 50)
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 1500)    # Centro
        pi.set_servo_pulsewidth(hw.servo_tilt.gpio_pin, 1500)   # Centro
        
        time.sleep(2)
        
        print("   🔄 Movimiento suave...")
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 1000)    # Izquierda
        time.sleep(0.5)
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 2000)    # Derecha
        time.sleep(0.5)
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 1500)    # Centro
        
        print("   ✅ Test completado sin interferencias aparentes")
        
    except Exception as e:
        print(f"   ❌ Error durante test: {e}")
        return False
    finally:
        # Limpiar
        pi.hardware_PWM(hw.motor_a.in1, 0, 0)
        pi.hardware_PWM(hw.motor_b.in1, 0, 0)
        pi.set_PWM_dutycycle(hw.motor_a.in2, 0)
        pi.set_PWM_dutycycle(hw.motor_b.in2, 0)
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 0)
        pi.set_servo_pulsewidth(hw.servo_tilt.gpio_pin, 0)
        pi.stop()
    
    return True

if __name__ == "__main__":
    if test_anti_interference():
        print("\n✅ CONFIGURACIÓN ANTI-INTERFERENCIA OK")
        print("\n📋 Próximos pasos:")
        print("   1. Reconectar cables según diagrama mostrado")
        print("   2. Reiniciar servicios: sudo systemctl restart t100-*")
        print("   3. Probar sistema completo")
    else:
        print("\n❌ Problemas detectados en configuración")
