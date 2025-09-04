#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de calibración de motores para T100 Controller
Ayuda a encontrar los factores de potencia correctos para que ambos motores funcionen a la misma velocidad.
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


class MotorCalibrator:
    """Herramienta de calibración de motores."""
    
    def __init__(self):
        """Inicializa el calibrador."""
        self.driver = None
        self.config = get_config()
        
    def start_calibration(self):
        """Inicia el proceso de calibración."""
        print("🔧 Calibrador de Motores T100")
        print("=" * 40)
        print("Este script te ayudará a calibrar los motores para que funcionen")
        print("a la misma velocidad ajustando los factores de potencia.")
        print("\n⚠️  IMPORTANTE:")
        print("- Asegúrate de que el vehículo pueda moverse libremente")
        print("- Ten a mano el botón de parada de emergencia")
        print("- Observa cuidadosamente el comportamiento de cada motor")
        
        input("\n📋 Presiona Enter para continuar...")
        
        try:
            self.driver = L298NDriver()
            print("✅ Driver inicializado correctamente")
            
            self.test_individual_motors()
            self.test_forward_movement()
            self.suggest_calibration()
            
        except KeyboardInterrupt:
            print("\n🛑 Calibración interrumpida por usuario")
        except Exception as e:
            print(f"❌ Error durante calibración: {e}")
        finally:
            if self.driver:
                self.driver.cleanup()
    
    def test_individual_motors(self):
        """Test individual de cada motor."""
        print("\n🔍 FASE 1: Test Individual de Motores")
        print("-" * 40)
        
        speeds = [0.3, 0.5, 0.7, 1.0]
        
        for speed in speeds:
            print(f"\n⚡ Probando velocidad {speed:.1f}:")
            
            # Motor A (izquierdo)
            print(f"  🔄 Motor A (izquierdo) a {speed:.1f}")
            self.driver.set_motor_speed('A', speed)
            time.sleep(3)
            self.driver.stop_all()
            time.sleep(1)
            
            # Motor B (derecho)
            print(f"  🔄 Motor B (derecho) a {speed:.1f}")
            self.driver.set_motor_speed('B', speed)
            time.sleep(3)
            self.driver.stop_all()
            time.sleep(1)
            
            response = input("  ❓ ¿Motor A más rápido (a), Motor B más rápido (b), o Iguales (i)? [a/b/i]: ").lower().strip()
            
            if response == 'a':
                print("  📝 Motor A es más rápido que Motor B")
            elif response == 'b':
                print("  📝 Motor B es más rápido que Motor A")
            else:
                print("  📝 Motores funcionan a velocidad similar")
    
    def test_forward_movement(self):
        """Test de movimiento hacia adelante."""
        print("\n🚗 FASE 2: Test de Movimiento Adelante")
        print("-" * 40)
        
        speeds = [0.3, 0.5, 0.7, 1.0]
        
        for speed in speeds:
            print(f"\n⚡ Probando movimiento adelante a {speed:.1f}")
            print("  Observa si el vehículo va recto o se desvía")
            
            self.driver.tank_drive(speed, 0)
            time.sleep(4)
            self.driver.stop_all()
            time.sleep(2)
            
            direction = input(f"  ❓ ¿Hacia dónde se desvía? [izq/der/recto]: ").lower().strip()
            
            if direction.startswith('izq'):
                print("  📝 Se desvía a la izquierda (motor derecho más rápido)")
            elif direction.startswith('der'):
                print("  📝 Se desvía a la derecha (motor izquierdo más rápido)")
            else:
                print("  📝 Va recto (motores balanceados)")
    
    def suggest_calibration(self):
        """Sugiere valores de calibración."""
        print("\n🎯 SUGERENCIAS DE CALIBRACIÓN")
        print("=" * 40)
        
        print("\n📋 Basándose en tus observaciones:")
        
        print("\n🔧 Casos comunes de calibración:")
        print("1. Si Motor A es más rápido → Reducir power_factor de Motor A")
        print("2. Si Motor B es más rápido → Reducir power_factor de Motor B")
        print("3. Si se desvía a la izquierda → Reducir power_factor Motor B")
        print("4. Si se desvía a la derecha → Reducir power_factor Motor A")
        
        print("\n📝 Para calibrar, edita config.py:")
        print("```python")
        print("DEFAULT_CONFIG = {")
        print('    "hardware": HardwareConfig(')
        print('        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False, power_factor=1.0),')
        print('        motor_b=MotorPins(enable=26, in1=21, in2=19, invert=False, power_factor=0.85),')
        print('        pwm_frequency=1000')
        print('    ),')
        print('    ...')
        print('```')
        
        print("\n💡 Valores típicos de power_factor:")
        print("- 1.0  = Potencia normal (sin calibración)")
        print("- 0.9  = Reducir 10% la potencia")
        print("- 0.8  = Reducir 20% la potencia")
        print("- 0.7  = Reducir 30% la potencia")
        
        print("\n🔄 Proceso iterativo:")
        print("1. Ajusta power_factor en config.py")
        print("2. Reinicia el servidor")
        print("3. Prueba el movimiento")
        print("4. Repite hasta lograr movimiento recto")
        
        print("\n⚡ Ejemplo práctico:")
        print("Si el vehículo se desvía a la izquierda:")
        print("→ Motor B (derecho) es más rápido")
        print("→ Cambiar power_factor de Motor B de 1.0 a 0.85")
        print("→ Probar y ajustar hasta que vaya recto")
    
    def interactive_calibration(self):
        """Calibración interactiva (opcional)."""
        print("\n🎮 CALIBRACIÓN INTERACTIVA")
        print("-" * 40)
        
        current_factor_a = 1.0
        current_factor_b = 1.0
        
        while True:
            print(f"\n⚙️ Factores actuales: A={current_factor_a:.2f}, B={current_factor_b:.2f}")
            print("Comandos:")
            print("  'a+' / 'a-' : Aumentar/Reducir Motor A")
            print("  'b+' / 'b-' : Aumentar/Reducir Motor B")
            print("  'test'       : Probar movimiento adelante")
            print("  'quit'       : Salir")
            
            cmd = input("Comando: ").lower().strip()
            
            if cmd == 'a+':
                current_factor_a = min(1.5, current_factor_a + 0.05)
            elif cmd == 'a-':
                current_factor_a = max(0.5, current_factor_a - 0.05)
            elif cmd == 'b+':
                current_factor_b = min(1.5, current_factor_b + 0.05)
            elif cmd == 'b-':
                current_factor_b = max(0.5, current_factor_b - 0.05)
            elif cmd == 'test':
                print("Probando movimiento...")
                # Aplicar factores temporalmente
                self.driver.hw_config.motor_a.power_factor = current_factor_a
                self.driver.hw_config.motor_b.power_factor = current_factor_b
                self.driver.tank_drive(0.7, 0)
                time.sleep(3)
                self.driver.stop_all()
            elif cmd == 'quit':
                break
            
            print(f"Factores: A={current_factor_a:.2f}, B={current_factor_b:.2f}")


def main():
    """Función principal."""
    calibrator = MotorCalibrator()
    calibrator.start_calibration()
    
    # Preguntar si quiere calibración interactiva
    response = input("\n❓ ¿Quieres hacer calibración interactiva? [y/n]: ").lower().strip()
    if response.startswith('y'):
        calibrator.interactive_calibration()


if __name__ == "__main__":
    main()
