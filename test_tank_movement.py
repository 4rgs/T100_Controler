#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de Movim        print("📋 CONFIGURACIÓN FÍSICA:")
        print("   Motor A (GPIO 12,16) → Oruga IZQUIERDA")  
        print("   Motor B (GPIO 13,26) → Oruga DERECHA")
        print("   PWM optimizado: PWM0/PWM1 sin interferencia")
        print("   Motores en configuración H (orientación opuesta)")
        print("=" * 50) Tank Drive - ZK-5AD
Prueba específica para verificar movimientos del tanque con orugas
"""

import asyncio
import time
from zk5ad_driver_ta6586 import ZK5ADDriverTA6586

class TankMovementTest:
    """Test específico para movimientos de tanque."""
    
    def __init__(self):
        """Inicializa el test."""
        self.driver = ZK5ADDriverTA6586()
        print("🚗 Test de Movimiento Tank Drive iniciado")
    
    async def run_tank_tests(self):
        """Ejecuta tests de movimiento del tanque."""
        if not self.driver.initialize():
            print("❌ Error inicializando driver ZK-5AD")
            return
        
        print("\n🚀 COMENZANDO TESTS DE MOVIMIENTO TANQUE")
        self._print_legend()
        
        # Tests básicos de movimiento
        movements = [
            (0.5, 0.0, "ADELANTE RECTO", "Ambas orugas hacia adelante"),
            (-0.5, 0.0, "ATRÁS RECTO", "Ambas orugas hacia atrás"),
            (0.0, 0.5, "GIRO DERECHA (en lugar)", "Oruga izq adelante, derecha atrás"),
            (0.0, -0.5, "GIRO IZQUIERDA (en lugar)", "Oruga derecha adelante, izq atrás"),
            (0.4, 0.3, "ADELANTE + DERECHA", "Oruga izq más rápida que derecha"),
            (0.4, -0.3, "ADELANTE + IZQUIERDA", "Oruga derecha más rápida que izq"),
            (-0.4, 0.3, "ATRÁS + DERECHA", "Oruga izq atrás más rápida"),
            (-0.4, -0.3, "ATRÁS + IZQUIERDA", "Oruga derecha atrás más rápida"),
        ]
        
        for fb, lr, name, description in movements:
            print(f"\n🔹 {name}")
            print(f"   Esperado: {description}")
            
            pwm_a, pwm_b = self.driver.tank_drive(fb, lr, debug=True)
            print(f"   Control: FB={fb:+.1f} LR={lr:+.1f}")
            print(f"   PWM: Motor A (izq)={pwm_a:3d}, Motor B (der)={pwm_b:3d}")
            
            # Determinar dirección esperada de cada motor
            self._analyze_motor_directions(fb, lr, pwm_a, pwm_b)
            
            print(f"   ⏱️  Ejecutando por 3 segundos...")
            await asyncio.sleep(3.0)
            
            # Parar entre movimientos
            self.driver.stop_motors()
            print(f"   🛑 Parado")
            await asyncio.sleep(1.0)
        
        print("\n✅ Tests de movimiento completados")
        self.driver.stop_motors()
    
    def _print_legend(self):
        """Imprime la leyenda de la configuración."""
        print("\n📋 CONFIGURACIÓN FÍSICA:")
        print("   Motor A (GPIO 12,13) → Oruga IZQUIERDA")
        print("   Motor B (GPIO 18,19) → Oruga DERECHA")
        print("   Motores en configuración H (orientación opuesta)")
        print("=" * 50)
    
    def _analyze_motor_directions(self, fb: float, lr: float, pwm_a: int, pwm_b: int):
        """Analiza las direcciones esperadas de los motores."""
        # Calcular velocidades esperadas para tank drive
        left_speed = fb + lr   # Motor A (izquierdo)
        right_speed = fb - lr  # Motor B (derecho)
        
        # Limitar a rango válido
        left_speed = max(-1.0, min(1.0, left_speed))
        right_speed = max(-1.0, min(1.0, right_speed))
        
        print(f"   Análisis:")
        print(f"     Velocidad oruga izq (A): {left_speed:+.2f} → PWM: {pwm_a}")
        print(f"     Velocidad oruga der (B): {right_speed:+.2f} → PWM: {pwm_b}")
        
        # Determinar direcciones
        dir_a = "ADELANTE" if left_speed > 0 else "ATRÁS" if left_speed < 0 else "PARADO"
        dir_b = "ADELANTE" if right_speed > 0 else "ATRÁS" if right_speed < 0 else "PARADO"
        
        print(f"     → Oruga izq debe ir: {dir_a}")
        print(f"     → Oruga der debe ir: {dir_b}")
    
    def cleanup(self):
        """Limpia recursos."""
        self.driver.cleanup()

async def main():
    """Función principal."""
    print("🚗 Test de Movimiento Tank Drive ZK-5AD")
    print("=" * 50)
    print("🎯 OBJETIVO:")
    print("   Verificar que los movimientos del tanque sean correctos")
    print("   Observar cada oruga durante las pruebas")
    print("")
    print("⚠️  SEGURIDAD:")
    print("   - Mantén el tanque elevado o en superficie segura")
    print("   - Usa Ctrl+C para parar inmediatamente")
    print("   - Cada movimiento dura 3 segundos")
    
    test = TankMovementTest()
    
    try:
        input("\n📋 Presiona ENTER para comenzar los tests...")
        await test.run_tank_tests()
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido por usuario")
    except Exception as e:
        print(f"❌ Error durante test: {e}")
    finally:
        test.cleanup()
        print("🧹 Limpieza completada")

if __name__ == "__main__":
    asyncio.run(main())