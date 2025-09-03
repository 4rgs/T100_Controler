#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verificación detallada de señales de pines L298N.
Este script muestra exactamente qué señales se envían a cada pin.
"""

import time
import sys
import os

# Solo para Raspberry Pi con pigpio
try:
    import pigpio
except ImportError:
    print("❌ Este script requiere pigpio (solo funciona en Raspberry Pi)")
    sys.exit(1)

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import get_config


class PinMonitor:
    """Monitor de estado de pines para diagnóstico."""
    
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("No se puede conectar a pigpio")
        
        self.config = get_config()
        self.motor_a = self.config['hardware'].motor_a
        self.motor_b = self.config['hardware'].motor_b
        
        # Configurar pines como salida
        self._setup_pins()
    
    def _setup_pins(self):
        """Configura todos los pines como salida."""
        pins = [
            self.motor_a.enable, self.motor_a.in1, self.motor_a.in2,
            self.motor_b.enable, self.motor_b.in1, self.motor_b.in2
        ]
        
        for pin in pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 0)
        
        # Configurar PWM en pines enable
        self.pi.set_PWM_frequency(self.motor_a.enable, 1000)
        self.pi.set_PWM_frequency(self.motor_b.enable, 1000)
    
    def mostrar_estado_pines(self):
        """Muestra el estado actual de todos los pines."""
        print("\n📊 ESTADO ACTUAL DE PINES:")
        print("-" * 50)
        
        # Motor A
        ena_state = self.pi.get_PWM_dutycycle(self.motor_a.enable)
        in1_state = self.pi.read(self.motor_a.in1)
        in2_state = self.pi.read(self.motor_a.in2)
        
        print(f"Motor A (Izquierdo):")
        print(f"  ENA (GPIO{self.motor_a.enable}): PWM={ena_state}/255 ({ena_state/2.55:.1f}%)")
        print(f"  IN1 (GPIO{self.motor_a.in1}): {in1_state} ({'HIGH' if in1_state else 'LOW'})")
        print(f"  IN2 (GPIO{self.motor_a.in2}): {in2_state} ({'HIGH' if in2_state else 'LOW'})")
        
        # Determinar dirección Motor A
        if in1_state and in2_state:
            dir_a = "BRAKE"
        elif in1_state and not in2_state:
            dir_a = "FORWARD" if not self.motor_a.invert else "BACKWARD"
        elif not in1_state and in2_state:
            dir_a = "BACKWARD" if not self.motor_a.invert else "FORWARD"
        else:
            dir_a = "COAST"
        print(f"  Dirección: {dir_a}")
        
        # Motor B
        enb_state = self.pi.get_PWM_dutycycle(self.motor_b.enable)
        in3_state = self.pi.read(self.motor_b.in1)  # IN3
        in4_state = self.pi.read(self.motor_b.in2)  # IN4
        
        print(f"\nMotor B (Derecho):")
        print(f"  ENB (GPIO{self.motor_b.enable}): PWM={enb_state}/255 ({enb_state/2.55:.1f}%)")
        print(f"  IN3 (GPIO{self.motor_b.in1}): {in3_state} ({'HIGH' if in3_state else 'LOW'})")
        print(f"  IN4 (GPIO{self.motor_b.in2}): {in4_state} ({'HIGH' if in4_state else 'LOW'})")
        
        # Determinar dirección Motor B
        if in3_state and in4_state:
            dir_b = "BRAKE"
        elif in3_state and not in4_state:
            dir_b = "FORWARD" if not self.motor_b.invert else "BACKWARD"
        elif not in3_state and in4_state:
            dir_b = "BACKWARD" if not self.motor_b.invert else "FORWARD"
        else:
            dir_b = "COAST"
        print(f"  Dirección: {dir_b}")
        print("-" * 50)
    
    def test_motor_sequence(self, motor_name: str, enable_pin: int, in1_pin: int, in2_pin: int, invert: bool):
        """Prueba secuencia completa de un motor."""
        print(f"\n🔧 Probando {motor_name}...")
        
        # 1. Coast (todo apagado)
        print("1️⃣ COAST - Todo apagado")
        self.pi.set_PWM_dutycycle(enable_pin, 0)
        self.pi.write(in1_pin, 0)
        self.pi.write(in2_pin, 0)
        self.mostrar_estado_pines()
        time.sleep(2)
        
        # 2. Forward
        print("2️⃣ FORWARD - IN1=HIGH, IN2=LOW")
        if not invert:
            self.pi.write(in1_pin, 1)
            self.pi.write(in2_pin, 0)
        else:
            self.pi.write(in1_pin, 0)
            self.pi.write(in2_pin, 1)
        self.pi.set_PWM_dutycycle(enable_pin, 128)  # 50%
        self.mostrar_estado_pines()
        time.sleep(3)
        
        # 3. Stop antes de cambio
        print("3️⃣ STOP antes de cambio de dirección")
        self.pi.set_PWM_dutycycle(enable_pin, 0)
        self.mostrar_estado_pines()
        time.sleep(1)
        
        # 4. Backward
        print("4️⃣ BACKWARD - IN1=LOW, IN2=HIGH")
        if not invert:
            self.pi.write(in1_pin, 0)
            self.pi.write(in2_pin, 1)
        else:
            self.pi.write(in1_pin, 1)
            self.pi.write(in2_pin, 0)
        self.pi.set_PWM_dutycycle(enable_pin, 128)  # 50%
        self.mostrar_estado_pines()
        time.sleep(3)
        
        # 5. Final stop
        print("5️⃣ STOP final")
        self.pi.set_PWM_dutycycle(enable_pin, 0)
        self.pi.write(in1_pin, 0)
        self.pi.write(in2_pin, 0)
        self.mostrar_estado_pines()
        time.sleep(1)
    
    def run_verification(self):
        """Ejecuta verificación completa."""
        print("🔍 VERIFICACIÓN DETALLADA DE PINES L298N")
        print("=" * 60)
        
        print("📋 Configuración:")
        print(f"Motor A: ENA={self.motor_a.enable}, IN1={self.motor_a.in1}, IN2={self.motor_a.in2}, invert={self.motor_a.invert}")
        print(f"Motor B: ENB={self.motor_b.enable}, IN3={self.motor_b.in1}, IN4={self.motor_b.in2}, invert={self.motor_b.invert}")
        
        # Estado inicial
        self.mostrar_estado_pines()
        
        input("\n⏸️ Presiona ENTER para probar Motor A...")
        self.test_motor_sequence(
            "MOTOR A (IZQUIERDO)", 
            self.motor_a.enable, 
            self.motor_a.in1, 
            self.motor_a.in2, 
            self.motor_a.invert
        )
        
        input("\n⏸️ Presiona ENTER para probar Motor B...")
        self.test_motor_sequence(
            "MOTOR B (DERECHO)", 
            self.motor_b.enable, 
            self.motor_b.in1, 
            self.motor_b.in2, 
            self.motor_b.invert
        )
        
        print("\n✅ Verificación completada")
        print("\n📝 ANÁLISIS:")
        print("- Si el motor gira al revés cuando debería ir adelante:")
        print("  → Cambia 'invert=True' en settings.py para ese motor")
        print("- Si no gira en absoluto:")
        print("  → Verifica conexiones ENA/ENB y alimentación")
        print("- Si gira pero en dirección incorrecta siempre:")
        print("  → Intercambia físicamente los cables IN1/IN2 o IN3/IN4")
    
    def cleanup(self):
        """Limpieza final."""
        if hasattr(self, 'pi'):
            # Apagar todo
            pins = [
                self.motor_a.enable, self.motor_a.in1, self.motor_a.in2,
                self.motor_b.enable, self.motor_b.in1, self.motor_b.in2
            ]
            
            for pin in pins:
                self.pi.write(pin, 0)
                self.pi.set_PWM_dutycycle(pin, 0)
            
            self.pi.stop()


def main():
    """Función principal."""
    print("⚠️  ATENCIÓN: Este script controlará los motores directamente")
    print("🛑 Asegúrate de que el robot esté seguro antes de continuar")
    
    respuesta = input("\n¿Continuar con la verificación de pines? (s/n): ").strip().lower()
    if respuesta != 's':
        print("👋 Verificación cancelada")
        return
    
    monitor = None
    try:
        monitor = PinMonitor()
        monitor.run_verification()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Soluciones:")
        print("- Ejecuta: sudo systemctl start pigpiod")
        print("- Verifica que los pines estén disponibles")
        print("- Ejecuta como root o usuario del grupo gpio")
    finally:
        if monitor:
            monitor.cleanup()
        print("\n👋 Finalizando verificación...")


if __name__ == "__main__":
    main()
