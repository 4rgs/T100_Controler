#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnóstico PWM Raspberry Pi - ZK-5AD
Detecta problemas de interferencia PWM y configuración GPIO
"""

import pigpio
import time
import sys

class PWMDiagnostic:
    """Diagnóstico específico para problemas PWM."""
    
    def __init__(self):
        """Inicializa el diagnóstico PWM."""
        self.pi = None
        # Configuración actual
        self.motor_a_pins = [12, 16]  # PWM0 + Digital
        self.motor_b_pins = [13, 26]  # PWM1 + Digital
        self.all_pins = self.motor_a_pins + self.motor_b_pins
        
        print("🔍 Diagnóstico PWM para ZK-5AD iniciado")
        print(f"Motor A: GPIO {self.motor_a_pins[0]} (PWM0) + GPIO {self.motor_a_pins[1]} (Digital)")
        print(f"Motor B: GPIO {self.motor_b_pins[0]} (PWM1) + GPIO {self.motor_b_pins[1]} (Digital)")
    
    def initialize(self) -> bool:
        """Inicializa pigpio."""
        try:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                print("❌ No se pudo conectar a pigpio daemon")
                return False
            
            print("✅ Conectado a pigpio daemon")
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando pigpio: {e}")
            return False
    
    def test_gpio_configuration(self):
        """Test de configuración básica GPIO."""
        print("\n🔧 TEST 1: Configuración GPIO")
        print("-" * 40)
        
        for pin in self.all_pins:
            try:
                # Configurar como OUTPUT
                self.pi.set_mode(pin, pigpio.OUTPUT)
                mode = self.pi.get_mode(pin)
                
                # Verificar si es PWM hardware
                is_hardware_pwm = pin in [12, 13, 18, 19]
                pwm_channel = "PWM0" if pin in [12, 18] else "PWM1" if pin in [13, 19] else "Digital"
                
                print(f"GPIO {pin:2d}: Modo={mode} | Tipo={pwm_channel} | {'✅' if mode == 1 else '❌'}")
                
            except Exception as e:
                print(f"GPIO {pin:2d}: ❌ Error - {e}")
    
    def test_pwm_channels(self):
        """Test de canales PWM por separado."""
        print("\n⚡ TEST 2: Canales PWM por separado")
        print("-" * 40)
        
        # Test PWM0 (GPIO 12)
        print("🔹 Probando PWM0 (GPIO 12)...")
        try:
            self.pi.hardware_PWM(12, 1000, 500000)  # 1kHz, 50% duty cycle
            time.sleep(2)
            self.pi.hardware_PWM(12, 0, 0)  # Parar
            print("  ✅ PWM0 funcionando")
        except Exception as e:
            print(f"  ❌ PWM0 error: {e}")
        
        # Test PWM1 (GPIO 13)
        print("🔹 Probando PWM1 (GPIO 13)...")
        try:
            self.pi.hardware_PWM(13, 1000, 500000)  # 1kHz, 50% duty cycle
            time.sleep(2)
            self.pi.hardware_PWM(13, 0, 0)  # Parar
            print("  ✅ PWM1 funcionando")
        except Exception as e:
            print(f"  ❌ PWM1 error: {e}")
    
    def test_simultaneous_pwm(self):
        """Test de PWM simultáneo en ambos canales."""
        print("\n🔄 TEST 3: PWM simultáneo")
        print("-" * 40)
        
        try:
            print("🔹 Ejecutando PWM0 y PWM1 simultáneamente...")
            
            # Iniciar ambos PWM
            self.pi.hardware_PWM(12, 1000, 250000)  # 25% duty cycle
            self.pi.hardware_PWM(13, 1000, 750000)  # 75% duty cycle
            
            print("  PWM0 (GPIO 12): 25% duty cycle")
            print("  PWM1 (GPIO 13): 75% duty cycle")
            print("  Ejecutando por 3 segundos...")
            
            time.sleep(3)
            
            # Parar ambos
            self.pi.hardware_PWM(12, 0, 0)
            self.pi.hardware_PWM(13, 0, 0)
            
            print("  ✅ Test simultáneo completado")
            
        except Exception as e:
            print(f"  ❌ Error en PWM simultáneo: {e}")
    
    def test_motor_simulation(self):
        """Test simulando control de motores ZK-5AD."""
        print("\n🚗 TEST 4: Simulación control motores")
        print("-" * 40)
        
        motor_tests = [
            ("Motor A adelante", 12, 16, True, False),   # PWM en 12, LOW en 16
            ("Motor A atrás", 12, 16, False, True),      # LOW en 12, PWM en 16
            ("Motor B adelante", 13, 26, True, False),   # PWM en 13, LOW en 26
            ("Motor B atrás", 13, 26, False, True),      # LOW en 13, PWM en 26
        ]
        
        for test_name, pin1, pin2, pin1_pwm, pin2_pwm in motor_tests:
            print(f"🔹 {test_name}:")
            
            try:
                if pin1_pwm:
                    self.pi.hardware_PWM(pin1, 1000, 500000)  # 50% PWM
                    self.pi.write(pin2, 0)  # LOW
                    print(f"  GPIO {pin1}: PWM 50% | GPIO {pin2}: LOW")
                else:
                    self.pi.write(pin1, 0)  # LOW
                    self.pi.set_PWM_dutycycle(pin2, 128)  # 50% PWM software
                    print(f"  GPIO {pin1}: LOW | GPIO {pin2}: PWM 50%")
                
                time.sleep(1.5)
                
                # Parar
                self.pi.hardware_PWM(pin1, 0, 0)
                self.pi.set_PWM_dutycycle(pin2, 0)
                print(f"  ✅ {test_name} completado")
                
            except Exception as e:
                print(f"  ❌ Error en {test_name}: {e}")
    
    def cleanup(self):
        """Limpia todos los GPIO."""
        if self.pi and self.pi.connected:
            print("\n🧹 Limpiando GPIO...")
            
            for pin in self.all_pins:
                try:
                    self.pi.hardware_PWM(pin, 0, 0)
                    self.pi.set_PWM_dutycycle(pin, 0)  
                    self.pi.write(pin, 0)
                except:
                    pass
            
            self.pi.stop()
            print("✅ GPIO limpiado")

def main():
    """Función principal."""
    print("🔍 Diagnóstico PWM para ZK-5AD - Raspberry Pi")
    print("=" * 50)
    print("🎯 OBJETIVO: Detectar problemas de interferencia PWM")
    print("🔧 CONFIGURACIÓN NUEVA:")
    print("   Motor A: GPIO 12 (PWM0) + GPIO 16 (Digital)")
    print("   Motor B: GPIO 13 (PWM1) + GPIO 26 (Digital)")
    print("=" * 50)
    
    diagnostic = PWMDiagnostic()
    
    if not diagnostic.initialize():
        return
    
    try:
        diagnostic.test_gpio_configuration()
        diagnostic.test_pwm_channels()
        diagnostic.test_simultaneous_pwm()
        diagnostic.test_motor_simulation()
        
        print("\n✅ DIAGNÓSTICO COMPLETADO")
        print("📋 Si todos los tests pasaron, la configuración PWM es correcta")
        
    except KeyboardInterrupt:
        print("\n🛑 Diagnóstico interrumpido")
    except Exception as e:
        print(f"\n❌ Error durante diagnóstico: {e}")
    finally:
        diagnostic.cleanup()

if __name__ == "__main__":
    main()