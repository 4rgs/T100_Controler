#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnóstico de Motores ZK-5AD - Test individual
Prueba cada motor por separado para verificar direcciones correctas
"""

import asyncio
import time
from zk5ad_driver_ta6586 import ZK5ADDriverTA6586

class MotorDiagnostic:
    """Diagnóstico individual de motores ZK-5AD."""
    
    def __init__(self):
        """Inicializa el diagnóstico."""
        self.driver = ZK5ADDriverTA6586()
        print("🔧 Diagnóstico de Motores ZK-5AD iniciado")
    
    async def test_individual_motors(self):
        """Test individual de cada motor."""
        if not self.driver.initialize():
            print("❌ Error inicializando driver ZK-5AD")
            return
        
        print("\n🚀 COMENZANDO TESTS INDIVIDUALES")
        print("Observa cada motor y verifica que gire en la dirección correcta")
        print("=" * 60)
        
        # Test Motor A (Izquierdo)
        print("\n🔹 MOTOR A (IZQUIERDO)")
        await self._test_motor_sequence("A")
        
        # Pausa entre tests
        print("\n⏸️  Pausa 2 segundos...")
        await asyncio.sleep(2.0)
        
        # Test Motor B (Derecho)
        print("\n🔹 MOTOR B (DERECHO)")
        await self._test_motor_sequence("B")
        
        # Test Tank Drive
        print("\n🔹 TEST TANK DRIVE")
        await self._test_tank_drive()
        
        # Parar todo
        self.driver.stop_motors()
        print("\n✅ Tests completados - Motores parados")
    
    async def _test_motor_sequence(self, motor_name: str):
        """Test de secuencia para un motor específico."""
        speeds = [0.3, 0.5, 0.8, 0.0, -0.3, -0.5, -0.8, 0.0]
        directions = ["30%", "50%", "80%", "STOP", "-30%", "-50%", "-80%", "STOP"]
        
        for speed, desc in zip(speeds, directions):
            if motor_name == "A":
                pwm_a, _ = self.driver.tank_drive(speed, 0.0, debug=True)
                print(f"   Motor A: {desc} -> PWM: {pwm_a}")
            else:
                _, pwm_b = self.driver.tank_drive(0.0, 0.0, debug=False)  # Parar A
                # Simular solo motor B moviendo forward_backward
                _, pwm_b = self.driver.tank_drive(speed, 0.0, debug=True)
                print(f"   Motor B: {desc} -> PWM: {pwm_b}")
            
            await asyncio.sleep(1.5)  # 1.5 segundos por test
    
    async def _test_tank_drive(self):
        """Test de tank drive completo."""
        print("   Testing tank drive combinations...")
        
        tests = [
            (0.5, 0.0, "Adelante recto"),
            (-0.5, 0.0, "Atrás recto"),
            (0.0, 0.5, "Girar derecha en el lugar"),
            (0.0, -0.5, "Girar izquierda en el lugar"),
            (0.5, 0.3, "Adelante + giro derecha"),
            (0.5, -0.3, "Adelante + giro izquierda"),
            (0.0, 0.0, "STOP")
        ]
        
        for fb, lr, desc in tests:
            pwm_a, pwm_b = self.driver.tank_drive(fb, lr, debug=True)
            print(f"   {desc}: FB={fb:+.1f} LR={lr:+.1f} -> A:{pwm_a:3d} B:{pwm_b:3d}")
            await asyncio.sleep(2.0)
    
    def cleanup(self):
        """Limpia recursos."""
        self.driver.cleanup()

async def main():
    """Función principal."""
    print("🚗 Diagnóstico Individual de Motores ZK-5AD - Configuración Tanque")
    print("=" * 60)
    print("📋 CONFIGURACIÓN FÍSICA:")
    print("   Motor A (GPIO 12,16) → Oruga IZQUIERDA")
    print("   Motor B (GPIO 13,26) → Oruga DERECHA")
    print("   PWM optimizado: PWM0/PWM1 sin interferencia")
    print("   Motores en configuración H (orientación opuesta)")
    print("=" * 50)
    print("")
    print("✅ COMPORTAMIENTO ESPERADO:")
    print("   - ADELANTE: Motor A gira normal, Motor B gira invertido")
    print("   - ATRÁS: Motor A gira inverso, Motor B gira normal")
    print("   - DERECHA: Motor A más rápido que Motor B")
    print("   - IZQUIERDA: Motor B más rápido que Motor A")
    print("")
    print("🚨 Usa Ctrl+C para parar en emergencia")
    print("=" * 60)
    
    diagnostic = MotorDiagnostic()
    
    try:
        await diagnostic.test_individual_motors()
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido por usuario")
    except Exception as e:
        print(f"❌ Error durante test: {e}")
    finally:
        diagnostic.cleanup()

if __name__ == "__main__":
    asyncio.run(main())