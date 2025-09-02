#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de calibración interactiva para encontrar la configuración correcta.
"""

import time
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.hardware.l298n_driver import L298NController
from calibration_configs import CONFIGURATIONS


def test_configuration(config_name, config):
    """Prueba una configuración específica."""
    print(f"\n🔧 Probando configuración: {config_name}")
    print(f"   Motor A: Invert={config['hardware'].motor_a.invert}")
    print(f"   Motor B: Invert={config['hardware'].motor_b.invert}")
    
    try:
        controller = L298NController(
            config['hardware'].motor_a,
            config['hardware'].motor_b,
            config['hardware'].pwm_frequency
        )
        
        motor_a = controller.get_motor_a()
        motor_b = controller.get_motor_b()
        
        print("\n   ⬆️ Prueba: Ambos motores adelante (debería avanzar)")
        motor_a.set_direction(forward=True)
        motor_a.set_speed(40.0)
        motor_b.set_direction(forward=True)
        motor_b.set_speed(40.0)
        time.sleep(1.5)
        controller.stop_all()
        time.sleep(0.5)
        
        print("   ➡️ Prueba: Giro derecha (Motor A adelante, Motor B atrás)")
        motor_a.set_direction(forward=True)
        motor_a.set_speed(40.0)
        motor_b.set_direction(forward=False)
        motor_b.set_speed(40.0)
        time.sleep(1.5)
        controller.stop_all()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error con esta configuración: {e}")
        return False


def main():
    """Función principal de calibración."""
    print("🎯 CALIBRACIÓN INTERACTIVA DE MOTORES")
    print("=" * 40)
    print("Este script probará diferentes configuraciones para encontrar la correcta.")
    print("\nObserva el comportamiento del robot y anota cuál funciona mejor:")
    print("✅ Adelante = robot avanza hacia adelante")
    print("✅ Giro derecha = robot gira hacia la derecha")
    
    print("\nConfiguraciones disponibles:")
    for key, (name, _) in CONFIGURATIONS.items():
        print(f"  {key}. {name}")
    
    print("\n⚠️  ADVERTENCIA: El robot se moverá durante las pruebas")
    input("\nPresiona ENTER para continuar o Ctrl+C para cancelar...")
    
    working_configs = []
    
    for key, (config_name, config) in CONFIGURATIONS.items():
        try:
            print(f"\n{'='*50}")
            if test_configuration(config_name, config):
                response = input("\n¿Esta configuración funcionó correctamente? (s/n): ").lower().strip()
                if response in ['s', 'si', 'sí', 'y', 'yes']:
                    working_configs.append((key, config_name, config))
                    print(f"✅ Configuración {key} marcada como funcionando")
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n👋 Calibración cancelada por el usuario")
            break
        except Exception as e:
            print(f"❌ Error general: {e}")
            continue
    
    # Mostrar resultados
    print(f"\n{'='*50}")
    print("📊 RESULTADOS DE CALIBRACIÓN:")
    
    if working_configs:
        print("\n✅ Configuraciones que funcionaron:")
        for key, name, config in working_configs:
            print(f"   {key}. {name}")
            print(f"      Motor A: invert={config['hardware'].motor_a.invert}")
            print(f"      Motor B: invert={config['hardware'].motor_b.invert}")
        
        print("\n📝 Para usar la configuración elegida, modifica src/config/settings.py:")
        best_config = working_configs[0][2]  # Primera que funcionó
        print(f"   motor_a=MotorPins(enable=12, in1=16, in2=20, invert={best_config['hardware'].motor_a.invert})")
        print(f"   motor_b=MotorPins(enable=26, in1=19, in2=21, invert={best_config['hardware'].motor_b.invert})")
        
    else:
        print("\n❌ Ninguna configuración funcionó correctamente.")
        print("   Verifica las conexiones físicas del hardware.")


if __name__ == "__main__":
    main()
