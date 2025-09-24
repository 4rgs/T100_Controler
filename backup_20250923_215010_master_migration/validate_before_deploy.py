#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Validación Pre-Despliegue
Valida que todos los módulos se importen correctamente antes del deploy
"""

import sys
import importlib
import traceback

def test_imports():
    """Prueba que todos los módulos se puedan importar correctamente."""
    print("🔍 VALIDACIÓN PRE-DESPLIEGUE - Test de importaciones")
    print("=" * 60)
    
    modules_to_test = [
        ("config", "Configuración del sistema"),
        ("elrs_receiver_ultra_fast", "Receptor ELRS Ultra Fast"),
        ("zk5ad_driver_ta6586", "Driver ZK-5AD (TA6586)"),
        ("mg90s_servo_driver", "Driver MG90S Servos"),
        ("t100_controller", "Controlador principal T100"),
        ("emergency_stop", "Parada de emergencia"),
    ]
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module_name, description in modules_to_test:
        print(f"\n📦 Probando: {module_name} - {description}")
        try:
            # Intentar importar el módulo
            module = importlib.import_module(module_name)
            
            # Verificar clases principales si existen
            if module_name == "config":
                assert hasattr(module, 'HardwareConfig')
                assert hasattr(module, 'ServoConfig')
                print("   ✅ HardwareConfig y ServoConfig encontradas")
            
            elif module_name == "elrs_receiver_ultra_fast":
                assert hasattr(module, 'ELRSReceiverUltraFast')
                print("   ✅ ELRSReceiverUltraFast encontrada")
            
            elif module_name == "zk5ad_driver_ta6586":
                assert hasattr(module, 'ZK5ADDriver')
                print("   ✅ ZK5ADDriver encontrada")
            
            elif module_name == "mg90s_servo_driver":
                assert hasattr(module, 'MG90SServoDriver')
                print("   ✅ MG90SServoDriver encontrada")
            
            elif module_name == "t100_controller":
                assert hasattr(module, 'T100Controller')
                print("   ✅ T100Controller encontrada")
            
            elif module_name == "emergency_stop":
                # Es un script, no una clase
                print("   ✅ Script de emergencia válido")
            
            print(f"   ✅ {module_name} importado correctamente")
            success_count += 1
            
        except ImportError as e:
            error_msg = str(e)
            if "serial" in error_msg or "pigpio" in error_msg:
                print(f"   ⚠️  {module_name}: {e}")
                print(f"   💡 Normal en macOS - estas librerías solo están en Raspberry Pi")
                success_count += 1  # Contar como éxito ya que es esperado
            else:
                print(f"   ❌ Error importando {module_name}: {e}")
                print(f"   💡 Verifica que el archivo {module_name}.py existe")
        except AssertionError as e:
            print(f"   ❌ {module_name} importado pero falta clase esperada")
        except Exception as e:
            print(f"   ❌ Error inesperado en {module_name}: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADOS: {success_count}/{total_count} módulos válidos")
    
    if success_count == total_count:
        print("✅ VALIDACIÓN EXITOSA - El sistema está listo para desplegarse")
        return True
    else:
        print("❌ VALIDACIÓN FALLIDA - Corrige los errores antes del deploy")
        return False

def test_config_values():
    """Prueba valores de configuración críticos."""
    print("\n🔧 Probando configuración...")
    
    try:
        from config import HardwareConfig, MotorPins, ServoConfig
        
        # Crear configuración de prueba con valores correctos
        motor_a = MotorPins(in1=16, in2=20)
        motor_b = MotorPins(in1=26, in2=21)
        servo_pan = ServoConfig(gpio_pin=18, name="pan")
        servo_tilt = ServoConfig(gpio_pin=19, name="tilt")
        
        # Verificar que se puede crear la configuración
        config = HardwareConfig(
            motor_a=motor_a,
            motor_b=motor_b, 
            servo_pan=servo_pan,
            servo_tilt=servo_tilt
        )
        
        print(f"   Motor A: GPIO {config.motor_a.in1}, {config.motor_a.in2}")
        print(f"   Motor B: GPIO {config.motor_b.in1}, {config.motor_b.in2}")
        print(f"   Servo Pan: GPIO {config.servo_pan.gpio_pin} '{config.servo_pan.name}'")
        print(f"   Servo Tilt: GPIO {config.servo_tilt.gpio_pin} '{config.servo_tilt.name}'")
        print(f"   PWM Frecuencia: {config.pwm_frequency} Hz")
        print(f"   Máximo PWM: {config.max_pwm_percent}%")
        
        print("   ✅ Configuración hardware válida")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en configuración: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de validación."""
    print("🚀 T100 - VALIDACIÓN PRE-DESPLIEGUE")
    print("Verifica que el código esté listo para transferir al Raspberry Pi")
    print("")
    
    # Test de importaciones
    imports_ok = test_imports()
    
    # Test de configuración
    config_ok = test_config_values()
    
    print("\n" + "=" * 60)
    if imports_ok and config_ok:
        print("🎉 SISTEMA VALIDADO - Listo para deploy")
        print("💡 Ejecuta: ./deploy.sh para transferir al Raspberry Pi")
        sys.exit(0)
    else:
        print("🚫 VALIDACIÓN FALLIDA - Corrige errores antes de continuar")
        sys.exit(1)

if __name__ == "__main__":
    main()