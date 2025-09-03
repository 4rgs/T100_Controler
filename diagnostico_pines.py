#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de diagnóstico para verificar el uso correcto de pines L298N.
Este script te ayuda a identificar problemas de cableado y configuración.
"""

import time
import sys
import os

# Agregar el directorio src al path para imports relativos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import get_config
from src.hardware.l298n_driver import L298NController


def test_motor_individual(motor, motor_name: str):
    """Prueba un motor individual en todas las direcciones."""
    print(f"\n🔧 Probando {motor_name}...")
    print("=" * 40)
    
    # Test 1: Adelante
    print(f"1️⃣ {motor_name} - ADELANTE (IN1=HIGH, IN2=LOW)")
    motor.set_direction(forward=True)
    motor.set_speed(50.0)  # 50% de velocidad
    time.sleep(2)
    motor.set_speed(0.0)
    time.sleep(1)
    
    # Test 2: Atrás
    print(f"2️⃣ {motor_name} - ATRÁS (IN1=LOW, IN2=HIGH)")
    motor.set_direction(forward=False)
    motor.set_speed(50.0)
    time.sleep(2)
    motor.set_speed(0.0)
    time.sleep(1)
    
    # Test 3: Coast
    print(f"3️⃣ {motor_name} - COAST (IN1=LOW, IN2=LOW)")
    motor.coast()
    time.sleep(1)
    
    print(f"✅ {motor_name} completado")


def test_direcciones_combinadas(controller):
    """Prueba las direcciones combinadas del robot."""
    print("\n🚗 Probando movimientos combinados...")
    print("=" * 40)
    
    tests = [
        ("ADELANTE", True, True, "Ambos motores adelante"),
        ("ATRÁS", False, False, "Ambos motores atrás"),
        ("GIRO DERECHA (en el lugar)", True, False, "Motor A adelante, Motor B atrás"),
        ("GIRO IZQUIERDA (en el lugar)", False, True, "Motor A atrás, Motor B adelante"),
    ]
    
    for i, (nombre, dir_a, dir_b, descripcion) in enumerate(tests, 1):
        print(f"{i}️⃣ {nombre}")
        print(f"   {descripcion}")
        
        # Configurar motores
        controller.get_motor_a().set_direction(dir_a)
        controller.get_motor_b().set_direction(dir_b)
        
        # Aplicar velocidad gradualmente
        for speed in [30, 60, 30]:
            controller.get_motor_a().set_speed(speed)
            controller.get_motor_b().set_speed(speed)
            time.sleep(1)
        
        # Parar
        controller.stop_all()
        time.sleep(2)
        
        # Preguntar al usuario
        respuesta = input("   ¿El movimiento fue correcto? (s/n): ").strip().lower()
        if respuesta != 's':
            print(f"   ❌ Problema detectado en {nombre}")
        else:
            print(f"   ✅ {nombre} funcionando correctamente")


def diagnostico_pines():
    """Diagnóstico completo de pines y configuración."""
    print("🔍 DIAGNÓSTICO DE PINES L298N")
    print("=" * 50)
    
    config = get_config()
    motor_a_pins = config['hardware'].motor_a
    motor_b_pins = config['hardware'].motor_b
    
    print("📋 Configuración actual:")
    print(f"Motor A (izq): ENA={motor_a_pins.enable}, IN1={motor_a_pins.in1}, IN2={motor_a_pins.in2}, invert={motor_a_pins.invert}")
    print(f"Motor B (der): ENB={motor_b_pins.enable}, IN3={motor_b_pins.in1}, IN4={motor_b_pins.in2}, invert={motor_b_pins.invert}")
    print(f"PWM Frequency: {config['hardware'].pwm_frequency} Hz")
    
    print("\n🎯 Recordatorio L298N:")
    print("- Adelante: IN1=HIGH, IN2=LOW")
    print("- Atrás:    IN1=LOW,  IN2=HIGH")  
    print("- Coast:    IN1=LOW,  IN2=LOW")
    print("- Brake:    IN1=HIGH, IN2=HIGH")
    
    input("\n⏸️ Presiona ENTER para continuar...")
    
    try:
        # Inicializar controlador
        controller = L298NController(motor_a_pins, motor_b_pins, config['hardware'].pwm_frequency)
        
        print("\n✅ Conectado a pigpio correctamente")
        
        # Test individual de motores
        test_motor_individual(controller.get_motor_a(), "MOTOR A (IZQUIERDO)")
        test_motor_individual(controller.get_motor_b(), "MOTOR B (DERECHO)")
        
        # Test de direcciones combinadas
        test_direcciones_combinadas(controller)
        
        print("\n🎉 Diagnóstico completado")
        print("\n📝 RECOMENDACIONES:")
        print("- Si un motor gira al revés, cambia su 'invert' a True en settings.py")
        print("- Si los cables están bien pero gira mal, intercambia IN1 e IN2")
        print("- Verifica que ENA/ENB estén conectados a pines PWM")
        print("- Asegúrate de que pigpiod esté ejecutándose")
        
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {e}")
        print("\n🔧 Posibles causas:")
        print("- pigpiod no está ejecutándose: sudo systemctl start pigpiod")
        print("- Pines mal configurados en settings.py")
        print("- Problema de permisos: ejecuta como root o usuario del grupo gpio")
        print("- Problemas de hardware: verifica conexiones")
    
    finally:
        print("\n👋 Finalizando diagnóstico...")


if __name__ == "__main__":
    print("⚠️  ATENCIÓN: Este script moverá los motores físicamente")
    print("🛑 Asegúrate de que el robot esté en un espacio seguro")
    print("🔌 Verifica todas las conexiones antes de continuar")
    
    respuesta = input("\n¿Continuar con el diagnóstico? (s/n): ").strip().lower()
    if respuesta == 's':
        diagnostico_pines()
    else:
        print("👋 Diagnóstico cancelado")
