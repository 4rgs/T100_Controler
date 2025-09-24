#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Rápido Servos MG90S - Validación básica
Prueba simple y rápida de los servos de cámara
"""

import asyncio
import time
from mg90s_servo_driver import MG90SServoDriver

async def quick_servo_test():
    """Test rápido de servos MG90S."""
    print("⚡ TEST RÁPIDO SERVOS MG90S")
    print("=" * 35)
    
    # Inicializar driver
    servo_driver = MG90SServoDriver()
    
    try:
        print("🔧 Inicializando servos...")
        if not servo_driver.initialize():
            print("❌ Error inicializando servos")
            return
        
        print("✅ Servos inicializados")
        print("📋 GPIO 21 = Pan (CH4), GPIO 20 = Tilt (CH3)")
        print()
        
        # Test 1: Centrar servos
        print("1️⃣  Centrando servos (90°, 90°)...")
        servo_driver.center_servos()
        await asyncio.sleep(2)
        
        # Test 2: Pan izquierda-derecha
        print("2️⃣  Pan: Izquierda (0°) → Derecha (180°)")
        servo_driver.set_pan_angle(0)
        await asyncio.sleep(1.5)
        servo_driver.set_pan_angle(180)
        await asyncio.sleep(1.5)
        servo_driver.set_pan_angle(90)  # Centro
        await asyncio.sleep(1)
        
        # Test 3: Tilt arriba-abajo
        print("3️⃣  Tilt: Abajo (0°) → Arriba (180°)")
        servo_driver.set_tilt_angle(0)
        await asyncio.sleep(1.5)
        servo_driver.set_tilt_angle(180)
        await asyncio.sleep(1.5)
        servo_driver.set_tilt_angle(90)  # Centro
        await asyncio.sleep(1)
        
        # Test 4: Simulación joystick
        print("4️⃣  Simulando joystick ELRS...")
        
        # Joystick positions: (CH4_raw, CH3_raw, description) - Nueva asignación
        positions = [
            (992, 992, "Centro"),
            (1600, 992, "Pan derecha (CH4)"),
            (400, 992, "Pan izquierda (CH4)"),
            (992, 1600, "Tilt arriba (CH3)"),
            (992, 400, "Tilt abajo (CH3)"),
            (992, 992, "Centro final"),
        ]
        
        for ch4, ch3, desc in positions:
            print(f"     {desc}: CH4={ch4} CH3={ch3}")
            pan_deg, tilt_deg = servo_driver.control_camera(ch4, ch3, debug=False)
            print(f"       → Pan={pan_deg:.0f}° Tilt={tilt_deg:.0f}°")
            await asyncio.sleep(1.5)
        
        print("\n✅ Test rápido completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("🧹 Limpiando...")
        servo_driver.cleanup()
        print("🎯 Servos centrados y desactivados")

def main():
    """Función principal."""
    print("Presiona Ctrl+C para cancelar en cualquier momento")
    print()
    
    try:
        asyncio.run(quick_servo_test())
    except KeyboardInterrupt:
        print("\n🛑 Test cancelado por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()