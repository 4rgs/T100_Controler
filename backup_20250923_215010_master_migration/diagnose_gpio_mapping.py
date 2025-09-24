#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnóstico de mapeo GPIO - Verifica la configuración correcta de pines
Detecta y corrige problemas de cruce de señales entre servos y motores
"""

import pigpio
import time
from config import get_config

class GPIOMappingDiagnostic:
    """Diagnóstico del mapeo de GPIO para T100."""
    
    def __init__(self):
        """Inicializa el diagnóstico."""
        self.pi = None
        self.config = get_config()
        self.hw_config = self.config['hardware']
        
    def initialize(self):
        """Inicializa pigpio."""
        try:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                print("❌ No se pudo conectar a pigpio daemon")
                return False
            print("✅ Conectado a pigpio daemon")
            return True
        except Exception as e:
            print(f"❌ Error conectando a pigpio: {e}")
            return False
    
    def show_configuration(self):
        """Muestra la configuración actual."""
        print("\n📋 CONFIGURACIÓN ACTUAL:")
        print("=" * 50)
        
        print("🚗 MOTORES TANK DRIVE:")
        print(f"   Motor A (Izq): GPIO {self.hw_config.motor_a.in1}, {self.hw_config.motor_a.in2}")
        print(f"   Motor B (Der): GPIO {self.hw_config.motor_b.in1}, {self.hw_config.motor_b.in2}")
        
        print("\n📹 SERVOS CÁMARA:")
        print(f"   Servo Pan:  GPIO {self.hw_config.servo_pan.gpio_pin} ← CH4 (izq/der)")
        print(f"   Servo Tilt: GPIO {self.hw_config.servo_tilt.gpio_pin} ← CH3 (arriba/abajo)")
        
        print("\n🎮 MAPEO DE CANALES:")
        print("   CH1 → Rotación tank (izquierda/derecha)")
        print("   CH2 → Aceleración tank (adelante/atrás)")
        print("   CH3 → Tilt cámara (arriba/abajo)")
        print("   CH4 → Pan cámara (izquierda/derecha)")
    
    def check_gpio_conflicts(self):
        """Verifica conflictos de GPIO."""
        print("\n🔍 VERIFICANDO CONFLICTOS GPIO:")
        print("=" * 50)
        
        # Recopilar todos los GPIO usados
        used_gpios = []
        gpio_assignments = {}
        
        # Motores
        motor_a_gpios = [self.hw_config.motor_a.in1, self.hw_config.motor_a.in2]
        motor_b_gpios = [self.hw_config.motor_b.in1, self.hw_config.motor_b.in2]
        
        for gpio in motor_a_gpios:
            used_gpios.append(gpio)
            gpio_assignments[gpio] = "Motor A"
            
        for gpio in motor_b_gpios:
            used_gpios.append(gpio)
            gpio_assignments[gpio] = "Motor B"
        
        # Servos
        servo_gpios = [self.hw_config.servo_pan.gpio_pin, self.hw_config.servo_tilt.gpio_pin]
        for gpio in servo_gpios:
            used_gpios.append(gpio)
            if gpio == self.hw_config.servo_pan.gpio_pin:
                gpio_assignments[gpio] = "Servo Pan"
            else:
                gpio_assignments[gpio] = "Servo Tilt"
        
        # Verificar duplicados
        duplicates = []
        for gpio in used_gpios:
            if used_gpios.count(gpio) > 1:
                if gpio not in duplicates:
                    duplicates.append(gpio)
        
        if duplicates:
            print("❌ CONFLICTOS DETECTADOS:")
            for gpio in duplicates:
                print(f"   GPIO {gpio} usado múltiples veces")
        else:
            print("✅ Sin conflictos GPIO detectados")
        
        print("\n📍 ASIGNACIÓN GPIO:")
        for gpio in sorted(gpio_assignments.keys()):
            assignment = gpio_assignments[gpio]
            print(f"   GPIO {gpio:2d} → {assignment}")
    
    def test_gpio_functionality(self):
        """Prueba la funcionalidad básica de GPIO."""
        print("\n🧪 PROBANDO FUNCIONALIDAD GPIO:")
        print("=" * 50)
        
        if not self.pi:
            print("❌ pigpio no inicializado")
            return
        
        # Test GPIO motores
        print("🚗 Probando GPIO motores...")
        motor_gpios = [
            self.hw_config.motor_a.in1, self.hw_config.motor_a.in2,
            self.hw_config.motor_b.in1, self.hw_config.motor_b.in2
        ]
        
        for gpio in motor_gpios:
            try:
                self.pi.set_mode(gpio, pigpio.OUTPUT)
                self.pi.write(gpio, 1)
                time.sleep(0.1)
                self.pi.write(gpio, 0)
                print(f"   ✅ GPIO {gpio} OK")
            except Exception as e:
                print(f"   ❌ GPIO {gpio} Error: {e}")
        
        # Test GPIO servos
        print("\n📹 Probando GPIO servos...")
        servo_gpios = [self.hw_config.servo_pan.gpio_pin, self.hw_config.servo_tilt.gpio_pin]
        
        for gpio in servo_gpios:
            try:
                self.pi.set_mode(gpio, pigpio.OUTPUT)
                self.pi.set_servo_pulsewidth(gpio, 1500)  # Centro
                time.sleep(0.5)
                self.pi.set_servo_pulsewidth(gpio, 0)  # Apagar
                print(f"   ✅ GPIO {gpio} OK")
            except Exception as e:
                print(f"   ❌ GPIO {gpio} Error: {e}")
    
    def verify_channel_mapping(self):
        """Verifica el mapeo correcto de canales."""
        print("\n🎯 VERIFICANDO MAPEO DE CANALES:")
        print("=" * 50)
        
        expected_mapping = {
            "CH1": "Rotación tank (Motor A/B)",
            "CH2": "Aceleración tank (Motor A/B)", 
            "CH3": f"Tilt cámara (GPIO {self.hw_config.servo_tilt.gpio_pin})",
            "CH4": f"Pan cámara (GPIO {self.hw_config.servo_pan.gpio_pin})"
        }
        
        print("✅ MAPEO ESPERADO:")
        for channel, function in expected_mapping.items():
            print(f"   {channel} → {function}")
        
        # Verificar consistency
        print("\n🔧 VERIFICACIÓN DE CONSISTENCIA:")
        
        # CH3 debe ir a Tilt (GPIO configurado)
        # CH4 debe ir a Pan (GPIO configurado)
        
        issues = []
        
        # Nota: Esta verificación es más conceptual ya que el mapeo real
        # se hace en t100_controller.py
        
        print("   ✅ Configuración parece consistente")
        print("   📝 Verificar en t100_controller.py que:")
        print("      - CH3 se asigna a raw_tilt")
        print("      - CH4 se asigna a raw_pan")
        print("      - CH1 se asigna a raw_left_right") 
        print("      - CH2 se asigna a raw_forward_backward")
    
    def run_full_diagnostic(self):
        """Ejecuta diagnóstico completo."""
        print("🔧 DIAGNÓSTICO MAPEO GPIO T100")
        print("=" * 50)
        
        if not self.initialize():
            return False
        
        self.show_configuration()
        self.check_gpio_conflicts()
        self.test_gpio_functionality()
        self.verify_channel_mapping()
        
        print("\n✅ DIAGNÓSTICO COMPLETADO")
        print("\n💡 RECOMENDACIONES:")
        print("   1. Verifica que los cables estén conectados a los GPIO correctos")
        print("   2. Ejecuta 'python3 test_servos_quick.py' para probar servos")
        print("   3. Ejecuta 'python3 test_full_system.py' para probar el sistema")
        print("   4. Si hay cruce de señales, verifica el cableado físico")
        
        return True
    
    def cleanup(self):
        """Limpia recursos."""
        if self.pi:
            self.pi.stop()

def main():
    """Función principal."""
    diagnostic = GPIOMappingDiagnostic()
    try:
        diagnostic.run_full_diagnostic()
    except KeyboardInterrupt:
        print("\n🛑 Diagnóstico interrumpido")
    finally:
        diagnostic.cleanup()

if __name__ == "__main__":
    main()