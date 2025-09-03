#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnóstico específico para el problema de coast inverso.
Este script prueba individualmente cada función de cada motor.
"""

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import pigpio
except ImportError:
    print("❌ pigpio no está instalado. Ejecuta: pip install pigpio")
    sys.exit(1)

from src.config.settings import get_config


def test_raw_pins(config):
    """Prueba directa de pines sin usar el driver."""
    print("🔧 PRUEBA DIRECTA DE PINES (sin driver)")
    print("=" * 50)
    
    pi = pigpio.pi()
    if not pi.connected:
        print("❌ No se puede conectar a pigpio")
        return
    
    motor_a = config['hardware'].motor_a
    motor_b = config['hardware'].motor_b
    
    # Configurar todos los pines como salida
    for pin in [motor_a.enable, motor_a.in1, motor_a.in2, 
                motor_b.enable, motor_b.in1, motor_b.in2]:
        pi.set_mode(pin, pigpio.OUTPUT)
        pi.write(pin, 0)
    
    # Configurar PWM
    pi.set_PWM_frequency(motor_a.enable, 1000)
    pi.set_PWM_frequency(motor_b.enable, 1000)
    
    print(f"Motor A: ENA={motor_a.enable}, IN1={motor_a.in1}, IN2={motor_a.in2}")
    print(f"Motor B: ENB={motor_b.enable}, IN3={motor_b.in1}, IN4={motor_b.in2}")
    
    # Test coast directo - AMBOS MOTORES
    print("\n1️⃣ COAST DIRECTO - Ambos motores")
    print("   Motor A: IN1=0, IN2=0, ENA=0")
    print("   Motor B: IN3=0, IN4=0, ENB=0")
    
    # Motor A coast
    pi.write(motor_a.in1, 0)
    pi.write(motor_a.in2, 0)
    pi.set_PWM_dutycycle(motor_a.enable, 0)
    
    # Motor B coast
    pi.write(motor_b.in1, 0)
    pi.write(motor_b.in2, 0)
    pi.set_PWM_dutycycle(motor_b.enable, 0)
    
    time.sleep(3)
    
    respuesta = input("¿Ambos motores están detenidos? (s/n): ").strip().lower()
    if respuesta != 's':
        print("❌ PROBLEMA: Uno o ambos motores no se detuvieron")
    else:
        print("✅ Coast directo funciona correctamente")
    
    # Test individual motor A
    print("\n2️⃣ MOTOR A - Test individual")
    
    # Coast motor A
    print("   Coast Motor A")
    pi.write(motor_a.in1, 0)
    pi.write(motor_a.in2, 0)
    pi.set_PWM_dutycycle(motor_a.enable, 0)
    time.sleep(2)
    
    # Forward motor A
    print("   Forward Motor A (IN1=1, IN2=0, PWM=128)")
    pi.write(motor_a.in1, 1)
    pi.write(motor_a.in2, 0)
    pi.set_PWM_dutycycle(motor_a.enable, 128)
    time.sleep(2)
    
    # Coast motor A
    print("   Coast Motor A")
    pi.write(motor_a.in1, 0)
    pi.write(motor_a.in2, 0)
    pi.set_PWM_dutycycle(motor_a.enable, 0)
    time.sleep(2)
    
    respuesta_a = input("¿Motor A funcionó correctamente? (s/n): ").strip().lower()
    
    # Test individual motor B
    print("\n3️⃣ MOTOR B - Test individual")
    
    # Coast motor B
    print("   Coast Motor B")
    pi.write(motor_b.in1, 0)
    pi.write(motor_b.in2, 0)
    pi.set_PWM_dutycycle(motor_b.enable, 0)
    time.sleep(2)
    
    # Forward motor B
    print("   Forward Motor B (IN3=1, IN4=0, PWM=128)")
    pi.write(motor_b.in1, 1)
    pi.write(motor_b.in2, 0)
    pi.set_PWM_dutycycle(motor_b.enable, 128)
    time.sleep(2)
    
    # Coast motor B
    print("   Coast Motor B")
    pi.write(motor_b.in1, 0)
    pi.write(motor_b.in2, 0)
    pi.set_PWM_dutycycle(motor_b.enable, 0)
    time.sleep(2)
    
    respuesta_b = input("¿Motor B funcionó correctamente? (s/n): ").strip().lower()
    
    # Limpieza final
    for pin in [motor_a.enable, motor_a.in1, motor_a.in2, 
                motor_b.enable, motor_b.in1, motor_b.in2]:
        pi.write(pin, 0)
    pi.stop()
    
    # Diagnóstico
    print("\n📊 DIAGNÓSTICO:")
    if respuesta_a != 's':
        print("❌ MOTOR A tiene problemas")
        print(f"   Verifica conexiones en pines {motor_a.enable}, {motor_a.in1}, {motor_a.in2}")
    else:
        print("✅ MOTOR A funciona correctamente")
    
    if respuesta_b != 's':
        print("❌ MOTOR B tiene problemas")
        print(f"   Verifica conexiones en pines {motor_b.enable}, {motor_b.in1}, {motor_b.in2}")
        print("   POSIBLES CAUSAS:")
        print("   - Pines mal configurados en settings.py")
        print("   - Cableado incorrecto")
        print("   - Driver L298N defectuoso")
    else:
        print("✅ MOTOR B funciona correctamente")


def test_problematic_sequence():
    """Reproduce la secuencia exacta que causa el problema."""
    print("\n🐛 REPRODUCIENDO SECUENCIA PROBLEMÁTICA")
    print("=" * 50)
    
    config = get_config()
    
    try:
        from src.hardware.l298n_driver import L298NController
        
        controller = L298NController(
            config['hardware'].motor_a,
            config['hardware'].motor_b,
            config['hardware'].pwm_frequency
        )
        
        print("1️⃣ Estado inicial - ambos motores coast")
        controller.stop_all()
        time.sleep(2)
        
        print("2️⃣ Motor A coast individual")
        controller.get_motor_a().coast()
        time.sleep(2)
        respuesta_a = input("¿Motor A se detuvo? (s/n): ").strip().lower()
        
        print("3️⃣ Motor B coast individual")
        controller.get_motor_b().coast()
        time.sleep(2)
        respuesta_b = input("¿Motor B se detuvo? (s/n): ").strip().lower()
        
        if respuesta_a != 's':
            print("❌ Motor A no hace coast correctamente")
        if respuesta_b != 's':
            print("❌ Motor B no hace coast correctamente - PROBLEMA IDENTIFICADO")
            print("   El motor derecho acelera en lugar de detenerse")
        
        # Limpieza
        controller.stop_all()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO ESPECÍFICO - PROBLEMA COAST INVERSO")
    print("=" * 60)
    print("Este script investigará por qué el motor derecho acelera al hacer coast")
    print()
    
    config = get_config()
    
    respuesta = input("¿Ejecutar diagnóstico de pines directos? (s/n): ").strip().lower()
    if respuesta == 's':
        test_raw_pins(config)
    
    respuesta = input("\n¿Ejecutar test de secuencia problemática? (s/n): ").strip().lower()
    if respuesta == 's':
        test_problematic_sequence()
    
    print("\n💡 RECOMENDACIONES:")
    print("1. Si Motor B acelera en coast, posibles causas:")
    print("   - Pines IN3/IN4 intercambiados")
    print("   - Pin ENB no conectado o mal configurado")
    print("   - Problema en L298N (canal B defectuoso)")
    print("2. Soluciones a probar:")
    print("   - Intercambiar pines IN3 e IN4 en settings.py")
    print("   - Verificar conexión del pin ENB")
    print("   - Probar con otro canal del L298N")
