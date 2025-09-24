#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de Protección contra Picos de Corriente - ZK-5AD
Prueba específica para verificar que la protección funciona correctamente
"""

import asyncio
import time
from zk5ad_driver_ta6586 import ZK5ADDriverTA6586

class CurrentSpikeProtectionTest:
    """Test específico para protección contra picos de corriente."""
    
    def __init__(self):
        """Inicializa el test."""
        self.driver = ZK5ADDriverTA6586()
        print("🛡️  Test de Protección contra Picos de Corriente iniciado")
    
    async def run_protection_tests(self):
        """Ejecuta tests de protección contra picos de corriente."""
        if not self.driver.initialize():
            print("❌ Error inicializando driver ZK-5AD")
            return
        
        print("\n🚀 COMENZANDO TESTS DE PROTECCIÓN")
        self._print_protection_info()
        
        # Tests de cambio de dirección
        direction_tests = [
            ("Test 1: Adelante -> Atrás", 0.5, -0.5),
            ("Test 2: Atrás -> Adelante", -0.5, 0.5),
            ("Test 3: Adelante -> Stop -> Atrás", 0.5, 0.0, -0.5),
            ("Test 4: Cambios rápidos", [0.3, -0.3, 0.3, -0.3]),
            ("Test 5: Giro completo", [(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5)]),
        ]
        
        for test_name, *speeds in direction_tests:
            print(f"\n🔹 {test_name}")
            
            if test_name == "Test 3: Adelante -> Stop -> Atrás":
                # Test con parada intermedia
                await self._test_with_stop(speeds[0], speeds[1], speeds[2])
            elif test_name == "Test 4: Cambios rápidos":
                # Test cambios rápidos
                await self._test_rapid_changes(speeds[0])
            elif test_name == "Test 5: Giro completo":
                # Test de giro con tank drive
                await self._test_tank_turns(speeds[0])
            else:
                # Test simple de cambio de dirección
                await self._test_direction_change(speeds[0], speeds[1])
            
            # Pausa entre tests
            print("   🛑 Parado - Esperando...")
            self.driver.stop_motors()
            await asyncio.sleep(2.0)
        
        print("\n✅ Tests de protección completados")
        self.driver.stop_motors()
    
    def _print_protection_info(self):
        """Imprime información sobre la protección."""
        delay_ms = self.driver.direction_change_delay * 1000
        enabled = "✅ ACTIVADA" if self.driver.enable_direction_protection else "❌ DESACTIVADA"
        
        print("\n📋 CONFIGURACIÓN DE PROTECCIÓN:")
        print(f"   Estado: {enabled}")
        print(f"   Delay de seguridad: {delay_ms:.0f}ms")
        print(f"   Detecta cambios: forward ↔ backward")
        print("=" * 50)
    
    async def _test_direction_change(self, speed1: float, speed2: float):
        """Test básico de cambio de dirección."""
        dir1 = "ADELANTE" if speed1 > 0 else "ATRÁS"
        dir2 = "ADELANTE" if speed2 > 0 else "ATRÁS"
        
        print(f"   Paso 1: {dir1} (velocidad {speed1:+.1f})")
        start_time = time.time()
        pwm_a, pwm_b = self.driver.tank_drive(speed1, 0.0, debug=True)
        
        await asyncio.sleep(1.5)
        
        print(f"   Paso 2: Cambio a {dir2} (velocidad {speed2:+.1f})")
        change_start = time.time()
        pwm_a, pwm_b = self.driver.tank_drive(speed2, 0.0, debug=True)
        change_time = (time.time() - change_start) * 1000
        
        print(f"   ⏱️  Tiempo de cambio: {change_time:.0f}ms")
        await asyncio.sleep(1.5)
    
    async def _test_with_stop(self, speed1: float, stop_speed: float, speed2: float):
        """Test con parada intermedia."""
        print(f"   Paso 1: Velocidad {speed1:+.1f}")
        self.driver.tank_drive(speed1, 0.0, debug=True)
        await asyncio.sleep(1.0)
        
        print(f"   Paso 2: STOP")
        self.driver.tank_drive(stop_speed, 0.0, debug=True)
        await asyncio.sleep(0.5)
        
        print(f"   Paso 3: Velocidad {speed2:+.1f} (sin protección, ya parado)")
        self.driver.tank_drive(speed2, 0.0, debug=True)
        await asyncio.sleep(1.0)
    
    async def _test_rapid_changes(self, speed_list: list):
        """Test de cambios rápidos de dirección."""
        print("   Ejecutando cambios rápidos cada 0.5s:")
        
        for i, speed in enumerate(speed_list):
            direction = "ADELANTE" if speed > 0 else "ATRÁS"
            print(f"   Cambio {i+1}: {direction} ({speed:+.1f})")
            
            start_time = time.time()
            self.driver.tank_drive(speed, 0.0, debug=True)
            elapsed = (time.time() - start_time) * 1000
            
            print(f"   ⏱️  Tiempo aplicado: {elapsed:.0f}ms")
            await asyncio.sleep(0.5)
    
    async def _test_tank_turns(self, turn_list: list):
        """Test de giros completos con tank drive."""
        print("   Ejecutando giros de tanque:")
        
        directions = ["ADELANTE-DER", "ADELANTE-IZQ", "ATRÁS-IZQ", "ATRÁS-DER"]
        
        for i, (fb, lr) in enumerate(turn_list):
            print(f"   Giro {i+1}: {directions[i]} (FB:{fb:+.1f}, LR:{lr:+.1f})")
            
            start_time = time.time()
            pwm_a, pwm_b = self.driver.tank_drive(fb, lr, debug=True)
            elapsed = (time.time() - start_time) * 1000
            
            print(f"   ⏱️  PWM A:{pwm_a:3d} B:{pwm_b:3d} | Tiempo: {elapsed:.0f}ms")
            await asyncio.sleep(1.0)
    
    def cleanup(self):
        """Limpia recursos."""
        self.driver.cleanup()

async def main():
    """Función principal."""
    print("🛡️  Test de Protección contra Picos de Corriente ZK-5AD")
    print("=" * 60)
    print("🎯 OBJETIVO:")
    print("   Verificar que los cambios de dirección incluyan pausa de seguridad")
    print("   Proteger contra picos de corriente al invertir motores")
    print("")
    print("⚠️  SEGURIDAD:")
    print("   - Los cambios forward↔backward incluyen pausa automática")
    print("   - Observar los tiempos de cambio en los logs")
    print("   - Usa Ctrl+C para parar inmediatamente")
    
    test = CurrentSpikeProtectionTest()
    
    try:
        input("\n📋 Presiona ENTER para comenzar los tests...")
        await test.run_protection_tests()
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido por usuario")
    except Exception as e:
        print(f"❌ Error durante test: {e}")
    finally:
        test.cleanup()
        print("🧹 Limpieza completada")

if __name__ == "__main__":
    asyncio.run(main())