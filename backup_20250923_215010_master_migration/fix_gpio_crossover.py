#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de reparación para el problema de cruce de señales GPIO
Corrige la configuración y verifica que todo esté alineado correctamente
"""

import os
import sys

def check_current_configuration():
    """Verifica la configuración actual."""
    print("🔍 VERIFICANDO CONFIGURACIÓN ACTUAL:")
    print("=" * 50)
    
    # Importar configuración
    try:
        from config import get_config
        config = get_config()
        hw_config = config['hardware']
        
        print("✅ Configuración importada correctamente")
        print(f"\n📹 SERVOS CONFIGURADOS:")
        print(f"   Pan:  GPIO {hw_config.servo_pan.gpio_pin}")
        print(f"   Tilt: GPIO {hw_config.servo_tilt.gpio_pin}")
        
        print(f"\n🚗 MOTORES CONFIGURADOS:")
        print(f"   Motor A: GPIO {hw_config.motor_a.in1}, {hw_config.motor_a.in2}")
        print(f"   Motor B: GPIO {hw_config.motor_b.in1}, {hw_config.motor_b.in2}")
        
        return hw_config
        
    except Exception as e:
        print(f"❌ Error importando configuración: {e}")
        return None

def verify_controller_mapping():
    """Verifica el mapeo en el controlador."""
    print("\n🎮 VERIFICANDO MAPEO EN CONTROLADOR:")
    print("=" * 50)
    
    controller_file = "/Users/alvarogonzalez/t100/t100_controller.py"
    
    if not os.path.exists(controller_file):
        print("❌ No se encuentra t100_controller.py")
        return False
    
    try:
        with open(controller_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar las asignaciones de canales
        mapping_found = {
            'CH1_tank': False,
            'CH2_tank': False, 
            'CH3_tilt': False,
            'CH4_pan': False
        }
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "channels.get('CH1'" in line and "left_right" in line:
                mapping_found['CH1_tank'] = True
                print(f"   ✅ CH1 → Tank rotación (línea {i+1})")
                
            elif "channels.get('CH2'" in line and "forward_backward" in line:
                mapping_found['CH2_tank'] = True
                print(f"   ✅ CH2 → Tank aceleración (línea {i+1})")
                
            elif "channels.get('CH3'" in line and "tilt" in line:
                mapping_found['CH3_tilt'] = True
                print(f"   ✅ CH3 → Tilt cámara (línea {i+1})")
                
            elif "channels.get('CH4'" in line and "pan" in line:
                mapping_found['CH4_pan'] = True
                print(f"   ✅ CH4 → Pan cámara (línea {i+1})")
        
        # Verificar que todos los mapeos están presentes
        missing = [k for k, v in mapping_found.items() if not v]
        if missing:
            print(f"   ❌ Mapeos faltantes: {missing}")
            return False
        else:
            print("   ✅ Todos los mapeos de canales están correctos")
            return True
            
    except Exception as e:
        print(f"❌ Error leyendo controlador: {e}")
        return False

def check_gpio_conflicts(hw_config):
    """Verifica conflictos de GPIO."""
    print("\n⚠️  VERIFICANDO CONFLICTOS GPIO:")
    print("=" * 50)
    
    if not hw_config:
        print("❌ No hay configuración de hardware")
        return False
    
    # Recopilar todos los GPIO
    gpio_usage = {}
    
    # Motores
    gpio_usage[hw_config.motor_a.in1] = "Motor A IN1"
    gpio_usage[hw_config.motor_a.in2] = "Motor A IN2"
    gpio_usage[hw_config.motor_b.in1] = "Motor B IN1"  
    gpio_usage[hw_config.motor_b.in2] = "Motor B IN2"
    
    # Servos
    gpio_usage[hw_config.servo_pan.gpio_pin] = "Servo Pan"
    gpio_usage[hw_config.servo_tilt.gpio_pin] = "Servo Tilt"
    
    # Verificar duplicados
    all_gpios = list(gpio_usage.keys())
    conflicts = []
    
    for gpio in set(all_gpios):
        if all_gpios.count(gpio) > 1:
            conflicts.append(gpio)
    
    if conflicts:
        print("❌ CONFLICTOS DETECTADOS:")
        for gpio in conflicts:
            print(f"   GPIO {gpio} usado múltiples veces")
        return False
    else:
        print("✅ Sin conflictos GPIO detectados")
        
        print("\n📍 ASIGNACIÓN FINAL:")
        for gpio in sorted(gpio_usage.keys()):
            print(f"   GPIO {gpio:2d} → {gpio_usage[gpio]}")
        
        return True

def show_expected_wiring():
    """Muestra el cableado esperado."""
    print("\n🔌 CABLEADO ESPERADO:")
    print("=" * 50)
    
    print("🚗 MOTORES (ZK-5AD):")
    print("   Motor A (Izquierdo):")
    print("     - IN1 → GPIO 12 (PWM)")
    print("     - IN2 → GPIO 16 (Digital)")
    print("   Motor B (Derecho):")
    print("     - IN1 → GPIO 13 (PWM)")
    print("     - IN2 → GPIO 26 (Digital)")
    
    print("\n📹 SERVOS (MG90S):")
    print("   Servo Pan (Horizontal):")
    print("     - Signal → GPIO 21")
    print("     - VCC → 5V")
    print("     - GND → GND")
    print("   Servo Tilt (Vertical):")
    print("     - Signal → GPIO 20")
    print("     - VCC → 5V") 
    print("     - GND → GND")

def show_control_mapping():
    """Muestra el mapeo de controles."""
    print("\n🎮 MAPEO DE CONTROLES ELRS:")
    print("=" * 50)
    
    print("🕹️  STICK DERECHO (Tank Drive):")
    print("   CH1 (Horizontal) → Rotación tank (izq/der)")
    print("   CH2 (Vertical)   → Aceleración tank (adelante/atrás)")
    
    print("\n🕹️  STICK IZQUIERDO (Cámara):")
    print("   CH3 (Vertical)   → Tilt cámara (arriba/abajo)")
    print("   CH4 (Horizontal) → Pan cámara (izq/der)")

def main():
    """Función principal."""
    print("🔧 REPARACIÓN CRUCE DE SEÑALES T100")
    print("=" * 60)
    print("Este script verifica y corrige el problema de cruce de señales")
    print("entre los servos y motores en el T100 Controller.")
    print("=" * 60)
    
    # Verificar configuración actual
    hw_config = check_current_configuration()
    
    # Verificar mapeo del controlador
    controller_ok = verify_controller_mapping()
    
    # Verificar conflictos GPIO
    gpio_ok = check_gpio_conflicts(hw_config)
    
    # Mostrar información de cableado
    show_expected_wiring()
    show_control_mapping()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO:")
    print("=" * 60)
    
    if hw_config and controller_ok and gpio_ok:
        print("✅ CONFIGURACIÓN CORRECTA")
        print("\n💡 SI AÚN HAY CRUCE DE SEÑALES:")
        print("   1. Verifica el cableado físico")
        print("   2. Asegúrate que los cables están en los GPIO correctos")
        print("   3. Reinicia el pigpio daemon: sudo systemctl restart pigpiod")
        print("   4. Prueba con: python3 test_servos_quick.py")
        
    else:
        print("❌ CONFIGURACIÓN TIENE PROBLEMAS")
        print("\n🔧 ACCIONES REQUERIDAS:")
        if not hw_config:
            print("   - Revisar archivo config.py")
        if not controller_ok:
            print("   - Revisar mapeo en t100_controller.py")
        if not gpio_ok:
            print("   - Resolver conflictos de GPIO")
    
    print("\n🚀 PARA PROBAR DESPUÉS DE CORREGIR:")
    print("   python3 diagnose_gpio_mapping.py  # (Si pigpio está disponible)")
    print("   python3 test_servos_quick.py")
    print("   python3 test_full_system.py")
    print("   python3 t100_controller.py")

if __name__ == "__main__":
    main()