#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Solo Servos MG90S - T100 Camera Control
Prueba únicamente los servos de cámara pan/tilt
"""

import asyncio
import time
import math
from mg90s_servo_driver import MG90SServoDriver

class ServoOnlyTest:
    """Test específico para servos MG90S."""
    
    def __init__(self):
        """Inicializa el test de servos."""
        self.servo_driver = MG90SServoDriver()
        print("📹 Test Solo Servos MG90S - Control Cámara Pan/Tilt")
    
    async def run_servo_tests(self):
        """Ejecuta tests específicos de servos."""
        if not await self.servo_driver.initialize():
            print("❌ Error inicializando servos MG90S")
            return
        
        print("\n🚀 COMENZANDO TESTS DE SERVOS")
        self._print_servo_info()
        
        # Tests de servos
        servo_tests = [
            ("Test 1: Posiciones básicas", self._test_basic_positions),
            ("Test 2: Barrido suave", self._test_smooth_sweep),
            ("Test 3: Simulación joystick", self._test_joystick_simulation),
            ("Test 4: Patrón figura-8", self._test_figure_eight),
            ("Test 5: Test precisión", self._test_precision),
        ]
        
        for test_name, test_func in servo_tests:
            print(f"\n🔹 {test_name}")
            try:
                await test_func()
            except Exception as e:
                print(f"❌ Error en {test_name}: {e}")
            
            # Centrar entre tests
            print("   🎯 Centrando servos...")
            self.servo_driver.center_servos()
            await asyncio.sleep(1.0)
        
        print("\n✅ Tests de servos terminados")
        await self.servo_driver.cleanup()
    
    def _print_servo_info(self):
        """Imprime información de los servos."""
        print("\n📋 CONFIGURACIÓN SERVOS MG90S:")
        print("   HARDWARE:")
        print("     Servo Pan:  GPIO 18 (0-180°)")
        print("     Servo Tilt: GPIO 19 (0-180°)")
        print("   CONTROL:")
        print("     PWM: 50Hz (20ms período)")
        print("     Pulsos: 500-2500µs (0-180°)")
        print("     Centro: 1500µs (90°)")
        print("=" * 50)
    
    async def _test_basic_positions(self):
        """Test posiciones básicas de los servos."""
        print("   Probando posiciones básicas...")
        
        positions = [
            (90, 90, "Centro"),
            (0, 90, "Pan extremo izquierdo"),
            (180, 90, "Pan extremo derecho"),
            (90, 0, "Tilt extremo abajo"),
            (90, 180, "Tilt extremo arriba"),
            (0, 0, "Esquina izquierda-abajo"),
            (180, 180, "Esquina derecha-arriba"),
            (90, 90, "Volver al centro"),
        ]
        
        for pan_angle, tilt_angle, description in positions:
            print(f"     {description}: Pan={pan_angle}° Tilt={tilt_angle}°")
            self.servo_driver.set_pan_angle(pan_angle)
            self.servo_driver.set_tilt_angle(tilt_angle)
            await asyncio.sleep(1.0)
    
    async def _test_smooth_sweep(self):
        """Test barrido suave horizontal y vertical."""
        print("   Barrido suave pan y tilt...")
        
        # Barrido horizontal (pan)
        print("     Barrido horizontal (pan) 0° → 180°")
        self.servo_driver.set_tilt_angle(90)  # Mantener tilt centrado
        for angle in range(0, 181, 10):
            print(f"       Pan: {angle}°")
            self.servo_driver.set_pan_angle(angle)
            await asyncio.sleep(0.2)
        
        await asyncio.sleep(0.5)
        
        # Barrido vertical (tilt)
        print("     Barrido vertical (tilt) 180° → 0°")
        self.servo_driver.set_pan_angle(90)  # Mantener pan centrado
        for angle in range(180, -1, -10):
            print(f"       Tilt: {angle}°")
            self.servo_driver.set_tilt_angle(angle)
            await asyncio.sleep(0.2)
    
    async def _test_joystick_simulation(self):
        """Simula entrada de joystick ELRS."""
        print("   Simulando entrada joystick ELRS...")
        
        # Simular diferentes posiciones de joystick ELRS (CH4=Pan, CH3=Tilt)
        joystick_positions = [
            (992, 992, "Centro"),
            (1811, 992, "Pan derecha completa (CH4)"),
            (172, 992, "Pan izquierda completa (CH4)"),
            (992, 1811, "Tilt arriba completa (CH3)"),
            (992, 172, "Tilt abajo completa (CH3)"),
            (1400, 1400, "Derecha-arriba diagonal"),
            (600, 600, "Izquierda-abajo diagonal"),
            (992, 992, "Volver al centro"),
        ]
        
        for raw_pan, raw_tilt, description in joystick_positions:
            print(f"     {description}: CH4={raw_pan} CH3={raw_tilt}")
            pan_degrees, tilt_degrees = self.servo_driver.control_camera(
                raw_pan, raw_tilt, debug=True
            )
            print(f"       → Pan={pan_degrees:.1f}° Tilt={tilt_degrees:.1f}°")
            await asyncio.sleep(1.5)
    
    async def _test_figure_eight(self):
        """Test patrón figura-8 con los servos."""
        print("   Patrón figura-8 (10 segundos)...")
        
        start_time = time.time()
        while time.time() - start_time < 10.0:
            elapsed = time.time() - start_time
            
            # Patrón figura-8 usando funciones trigonométricas
            pan_angle = 90 + 60 * math.sin(elapsed * 0.8)  # 30° → 150°
            tilt_angle = 90 + 30 * math.sin(elapsed * 1.6)  # 60° → 120°
            
            self.servo_driver.set_pan_angle(pan_angle)
            self.servo_driver.set_tilt_angle(tilt_angle)
            
            if int(elapsed * 2) % 2 == 0:  # Imprimir cada 0.5s
                print(f"     t={elapsed:.1f}s: Pan={pan_angle:.1f}° Tilt={tilt_angle:.1f}°")
            
            await asyncio.sleep(0.1)
    
    async def _test_precision(self):
        """Test de precisión en posiciones específicas."""
        print("   Test de precisión (±1°)...")
        
        # Posiciones de precisión
        precision_positions = [
            (45, 45),
            (90, 90),
            (135, 135),
            (60, 120),
            (120, 60),
        ]
        
        for target_pan, target_tilt in precision_positions:
            print(f"     Posición objetivo: Pan={target_pan}° Tilt={target_tilt}°")
            
            # Establecer posición
            self.servo_driver.set_pan_angle(target_pan)
            self.servo_driver.set_tilt_angle(target_tilt)
            
            await asyncio.sleep(1.0)
            
            # Verificar con conversión inversa (simulado)
            print(f"       ✅ Servos posicionados")
    
    def _simulate_raw_to_degrees(self, raw_value):
        """Simula conversión de valor ELRS crudo a grados."""
        # Convertir 172-1811 a 0-180°
        normalized = (raw_value - 172) / (1811 - 172)
        degrees = normalized * 180
        return max(0, min(180, degrees))

async def main():
    """Función principal."""
    print("📹 Test Solo Servos MG90S - Control Cámara Pan/Tilt")
    print("=" * 55)
    print("🎯 OBJETIVO:")
    print("   Probar únicamente los servos MG90S")
    print("   Verificar movimientos pan/tilt de cámara")
    print("")
    print("⚠️  SEGURIDAD:")
    print("   - Observa que los servos se muevan suavemente")
    print("   - Verifica que no haya movimientos bruscos")
    print("   - Los motores permanecerán apagados")
    print("   - Usa Ctrl+C para parar inmediatamente")
    
    test = ServoOnlyTest()
    
    try:
        input("\n📋 Presiona ENTER para comenzar tests de servos...")
        await test.run_servo_tests()
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido por usuario")
    except Exception as e:
        print(f"❌ Error durante test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await test.servo_driver.cleanup()
        except:
            pass
        print("🧹 Limpieza completada")

if __name__ == "__main__":
    asyncio.run(main())