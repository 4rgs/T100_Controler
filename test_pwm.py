#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test rápido de PWM para verificar configuración antes de calibrar motores
"""

import time
import sys
from config import get_config

try:
    from l298n_driver import L298NDriver
except ImportError:
    print("❌ No se puede importar L298NDriver (pigpio no disponible)")
    print("💡 Este script debe ejecutarse en el Raspberry Pi")
    sys.exit(1)


def test_pwm_setup():
    """Test básico de configuración PWM."""
    print("🔧 Test de Configuración PWM")
    print("=" * 30)
    
    try:
        # Inicializar driver
        driver = L298NDriver()
        
        # Test PWM en diferentes valores
        test_values = [0, 64, 127, 191, 255]
        
        print("\n🧪 Test Motor A (pin 12):")
        for pwm in test_values:
            try:
                driver.pi.set_PWM_dutycycle(12, pwm)
                print(f"   PWM {pwm:3d} → ✅")
                time.sleep(0.5)
            except Exception as e:
                print(f"   PWM {pwm:3d} → ❌ {e}")
        
        print("\n🧪 Test Motor B (pin 26):")
        for pwm in test_values:
            try:
                driver.pi.set_PWM_dutycycle(26, pwm)
                print(f"   PWM {pwm:3d} → ✅")
                time.sleep(0.5)
            except Exception as e:
                print(f"   PWM {pwm:3d} → ❌ {e}")
        
        # Detener todo
        driver.stop_all()
        
        print("\n✅ Test PWM completado")
        
        # Test de driver
        print("\n🚗 Test rápido de motores:")
        
        print("   Motor A adelante 30%...")
        driver.set_motor_speed('A', 0.3)
        time.sleep(2)
        
        print("   Motor B adelante 30%...")
        driver.stop_all()
        driver.set_motor_speed('B', 0.3)
        time.sleep(2)
        
        print("   Ambos motores 50%...")
        driver.set_motors(0.5, 0.5)
        time.sleep(2)
        
        driver.stop_all()
        print("   ✅ Test de motores completado")
        
        driver.cleanup()
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False
    
    return True


if __name__ == "__main__":
    if test_pwm_setup():
        print("\n🎉 Sistema listo para calibración!")
        print("Ejecuta: python3 calibrate_motors.py")
    else:
        print("\n⚠️  Hay problemas con la configuración PWM")
        print("Revisa las conexiones y permisos")
