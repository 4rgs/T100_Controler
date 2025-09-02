#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilidad de diagnóstico y calibración para motores L298N.
"""

import time
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config.settings import get_config
from src.hardware.l298n_driver import L298NController


def test_motor_individual(motor, motor_name: str):
    """Prueba un motor individual en todas las direcciones."""
    print(f"\n🔧 Probando {motor_name}...")
    
    # Test adelante
    print(f"  ▶️ {motor_name} - Adelante 50% por 2 segundos")
    motor.set_direction(forward=True)
    motor.set_speed(50.0)
    time.sleep(2)
    motor.coast()
    time.sleep(1)
    
    # Test atrás
    print(f"  ◀️ {motor_name} - Atrás 50% por 2 segundos")
    motor.set_direction(forward=False)
    motor.set_speed(50.0)
    time.sleep(2)
    motor.coast()
    time.sleep(1)


def test_differential_movements(controller):
    """Prueba movimientos diferenciales específicos."""
    motor_a = controller.get_motor_a()
    motor_b = controller.get_motor_b()
    
    print("\n🎯 Pruebas de movimiento diferencial:")
    
    # Adelante
    print("  ⬆️ ADELANTE: Ambos motores hacia adelante")
    motor_a.set_direction(forward=True)
    motor_a.set_speed(50.0)
    motor_b.set_direction(forward=True)
    motor_b.set_speed(50.0)
    time.sleep(2)
    controller.stop_all()
    time.sleep(1)
    
    # Atrás
    print("  ⬇️ ATRÁS: Ambos motores hacia atrás")
    motor_a.set_direction(forward=False)
    motor_a.set_speed(50.0)
    motor_b.set_direction(forward=False)
    motor_b.set_speed(50.0)
    time.sleep(2)
    controller.stop_all()
    time.sleep(1)
    
    # Giro derecha
    print("  ➡️ GIRO DERECHA: Motor A adelante, Motor B atrás")
    motor_a.set_direction(forward=True)
    motor_a.set_speed(50.0)
    motor_b.set_direction(forward=False)
    motor_b.set_speed(50.0)
    time.sleep(2)
    controller.stop_all()
    time.sleep(1)
    
    # Giro izquierda
    print("  ⬅️ GIRO IZQUIERDA: Motor A atrás, Motor B adelante")
    motor_a.set_direction(forward=False)
    motor_a.set_speed(50.0)
    motor_b.set_direction(forward=True)
    motor_b.set_speed(50.0)
    time.sleep(2)
    controller.stop_all()
    time.sleep(1)


def main():
    """Función principal de diagnóstico."""
    print("🚗 DIAGNÓSTICO DE MOTORES L298N")
    print("=" * 40)
    
    try:
        # Cargar configuración
        config = get_config()
        print(f"📋 Motor A - ENA:{config['hardware'].motor_a.enable}, IN1:{config['hardware'].motor_a.in1}, IN2:{config['hardware'].motor_a.in2}, Invert:{config['hardware'].motor_a.invert}")
        print(f"📋 Motor B - ENB:{config['hardware'].motor_b.enable}, IN3:{config['hardware'].motor_b.in1}, IN4:{config['hardware'].motor_b.in2}, Invert:{config['hardware'].motor_b.invert}")
        
        # Inicializar hardware
        controller = L298NController(
            config['hardware'].motor_a,
            config['hardware'].motor_b,
            config['hardware'].pwm_frequency
        )
        
        motor_a = controller.get_motor_a()
        motor_b = controller.get_motor_b()
        
        print("\n⚠️  ADVERTENCIA: Asegúrate de que el robot esté en una superficie segura")
        print("⚠️  Los motores se moverán durante la prueba")
        input("\nPresiona ENTER para continuar o Ctrl+C para cancelar...")
        
        # Pruebas individuales
        test_motor_individual(motor_a, "Motor A (Izquierdo)")
        test_motor_individual(motor_b, "Motor B (Derecho)")
        
        # Pruebas diferenciales
        test_differential_movements(controller)
        
        print("\n✅ Diagnóstico completado!")
        print("\n📝 INTERPRETACIÓN DE RESULTADOS:")
        print("   - Si el robot va hacia ATRÁS cuando debería ir ADELANTE: cambiar invert=True/False")
        print("   - Si gira IZQUIERDA cuando debería girar DERECHA: intercambiar motores A/B")
        print("   - Si un motor no se mueve: verificar conexiones de ese motor")
        
    except KeyboardInterrupt:
        print("\n👋 Diagnóstico cancelado por el usuario")
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
    finally:
        try:
            controller.stop_all()
        except:
            pass


if __name__ == "__main__":
    main()
