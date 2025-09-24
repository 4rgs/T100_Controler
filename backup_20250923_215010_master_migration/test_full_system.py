#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Completo Tank + Cámara - T100 ZK-5AD + MG90S
Prueba integrada de todo el sistema: motores y servos
"""  

import asyncio
import time
from t100_controller import T100Controller

class FullSystemTest:
    """Test completo del sistema T100."""
    
    def __init__(self):
        """Inicializa el test del sistema completo."""
        self.controller = T100Controller()
        print("🎮 Test Completo T100 - Tank Drive + Servos Cámara")
    
    async def run_system_tests(self):
        """Ejecuta tests completos del sistema."""
        if not await self.controller.initialize():
            print("❌ Error inicializando sistema T100")
            return
        
        print("\n🚀 COMENZANDO TESTS COMPLETOS")
        self._print_system_info()
        
        # Tests combinados
        combined_tests = [
            ("Test 1: Solo Tank - Adelante", self._test_tank_only),
            ("Test 2: Solo Cámara - Barrido", self._test_camera_only),
            ("Test 3: Tank + Cámara - Combinado", self._test_combined_control),
            ("Test 4: Simulación Patrullaje", self._test_patrol_simulation),
        ]
        
        for test_name, test_func in combined_tests:
            print(f"\n🔹 {test_name}")
            try:
                await test_func()
            except Exception as e:
                print(f"❌ Error en {test_name}: {e}")
            
            # Pausa entre tests
            print("   🛑 Parado - Esperando...")
            await self._stop_all()
            await asyncio.sleep(2.0)
        
        print("\n✅ Tests completos terminados")
        await self.controller.cleanup()
    
    def _print_system_info(self):
        """Imprime información del sistema."""
        print("\n📋 CONFIGURACIÓN SISTEMA T100:")
        print("   MOTORES:")
        print("     Motor A (Izq): GPIO 12, 16")
        print("     Motor B (Der): GPIO 13, 26")
        print("   SERVOS:")
        print("     Servo Pan:  GPIO 21 (CH4 - Pan cámara)")
        print("     Servo Tilt: GPIO 20 (CH3 - Tilt cámara)")
        print("   CONTROLES ELRS:")
        print("     CH1 → Rotación tank (izquierda/derecha)")
        print("     CH2 → Aceleración tank (adelante/atrás)")
        print("     CH3 → Tilt cámara (arriba/abajo)")
        print("     CH4 → Pan cámara (izquierda/derecha)")
        print("=" * 60)
    
    async def _test_tank_only(self):
        """Test solo del tank drive."""
        print("   Solo movimientos de tanque (servos centrados):")
        
        # Simular canales ELRS para solo tank
        test_channels = [
            {'CH1': 992, 'CH2': 1400, 'CH3': 992, 'CH4': 992},  # Adelante (CH2)
            {'CH1': 992, 'CH2': 600, 'CH3': 992, 'CH4': 992},   # Atrás (CH2)
            {'CH1': 1400, 'CH2': 992, 'CH3': 992, 'CH4': 992},  # Derecha (CH1)
            {'CH1': 600, 'CH2': 992, 'CH3': 992, 'CH4': 992},   # Izquierda (CH1)
        ]
        
        directions = ["ADELANTE", "ATRÁS", "DERECHA", "IZQUIERDA"]
        
        for channels, direction in zip(test_channels, directions):
            print(f"     {direction}: CH1={channels['CH1']} CH2={channels['CH2']}")
            await self._simulate_control_loop(channels, 2.0)
    
    async def _test_camera_only(self):
        """Test solo de servos de cámara."""
        print("   Solo movimientos de cámara (tanque parado):")
        
        # Simular canales ELRS para solo cámara
        test_channels = [
            {'CH1': 992, 'CH2': 992, 'CH3': 992, 'CH4': 1400},  # Pan derecha (CH4)
            {'CH1': 992, 'CH2': 992, 'CH3': 992, 'CH4': 600},   # Pan izquierda (CH4)
            {'CH1': 992, 'CH2': 992, 'CH3': 1400, 'CH4': 992},  # Tilt arriba (CH3)
            {'CH1': 992, 'CH2': 992, 'CH3': 600, 'CH4': 992},   # Tilt abajo (CH3)
            {'CH1': 992, 'CH2': 992, 'CH3': 992, 'CH4': 992},   # Centro
        ]
        
        directions = ["PAN DERECHA", "PAN IZQUIERDA", "TILT ARRIBA", "TILT ABAJO", "CENTRO"]
        
        for channels, direction in zip(test_channels, directions):
            print(f"     {direction}: CH3={channels['CH3']} CH4={channels['CH4']}")
            await self._simulate_control_loop(channels, 1.5)
    
    async def _test_combined_control(self):
        """Test de control combinado tank + cámara."""
        print("   Movimientos combinados tanque + cámara:")
        
        # Simular canales ELRS para control combinado
        test_channels = [
            {'CH1': 992, 'CH2': 1200, 'CH3': 1200, 'CH4': 1400},  # Adelante + Tilt arriba + Pan derecha
            {'CH1': 1200, 'CH2': 1200, 'CH3': 800, 'CH4': 600},   # Adelante + derecha + Tilt abajo + Pan izq
            {'CH1': 600, 'CH2': 800, 'CH3': 1400, 'CH4': 1200},   # Atrás + izq + Tilt arriba + Pan der
        ]
        
        descriptions = [
            "Adelante + Tilt arriba + Pan derecha",
            "Adelante-derecha + Tilt abajo + Pan izquierda", 
            "Atrás-izquierda + Tilt arriba + Pan derecha"
        ]
        
        for channels, desc in zip(test_channels, descriptions):
            print(f"     {desc}")
            print(f"       Tank: CH2={channels['CH2']} CH4={channels['CH4']}")
            print(f"       Cam:  CH1={channels['CH1']} CH3={channels['CH3']}")
            await self._simulate_control_loop(channels, 2.5)
    
    async def _test_patrol_simulation(self):
        """Simulación de patrullaje completo."""
        print("   Simulando patrullaje con cámara activa:")
        
        # Secuencia de patrullaje realista
        patrol_sequence = [
            ({'CH1': 992, 'CH2': 1300, 'CH3': 992, 'CH4': 992}, "Avanzar", 2.0),    # Avanzar
            ({'CH1': 1600, 'CH2': 992, 'CH3': 1200, 'CH4': 992}, "Explorar derecha", 1.5),  # Mirar derecha
            ({'CH1': 992, 'CH2': 1200, 'CH3': 992, 'CH4': 1300}, "Girar derecha", 1.5),     # Girar
            ({'CH1': 400, 'CH2': 1200, 'CH3': 800, 'CH4': 992}, "Explorar izquierda", 1.5),  # Mirar izq
            ({'CH1': 992, 'CH2': 992, 'CH3': 992, 'CH4': 992}, "Parar y centrar", 1.0),     # Parar
        ]
        
        for channels, action, duration in patrol_sequence:
            print(f"     {action}: Tank(CH2={channels['CH2']}, CH4={channels['CH4']}) "
                  f"Cam(CH1={channels['CH1']}, CH3={channels['CH3']})")
            await self._simulate_control_loop(channels, duration)
    
    async def _simulate_control_loop(self, channels: dict, duration: float):
        """Simula el bucle de control con canales específicos."""
        # Extraer valores con nueva asignación
        raw_forward_backward = channels.get('CH2', 992)  # CH2: Aceleración
        raw_left_right = channels.get('CH1', 992)        # CH1: Rotación
        raw_pan = channels.get('CH4', 992)               # CH4: Pan cámara
        raw_tilt = channels.get('CH3', 992)              # CH3: Tilt cámara
        
        # Convertir para motores
        forward_backward = self.controller._raw_to_float(raw_forward_backward)
        left_right = self.controller._raw_to_float(raw_left_right)
        
        # Aplicar controles
        pwm_a, pwm_b = self.controller.motor_driver.tank_drive(
            forward_backward, left_right, debug=True
        )
        
        pan_degrees, tilt_degrees = self.controller.servo_driver.control_camera(
            raw_pan, raw_tilt, debug=True
        )
        
        print(f"       → PWM A:{pwm_a:3d} B:{pwm_b:3d} | Pan:{pan_degrees:5.1f}° Tilt:{tilt_degrees:5.1f}°")
        
        # Esperar duración especificada
        await asyncio.sleep(duration)
    
    async def _stop_all(self):
        """Para todo el sistema."""
        self.controller.motor_driver.stop_motors()
        self.controller.servo_driver.center_servos()

async def main():
    """Función principal."""
    print("🎮 Test Completo Sistema T100 - Tank Drive + Servos MG90S")
    print("=" * 65)
    print("🎯 OBJETIVO:")
    print("   Probar integración completa del sistema")
    print("   Tank drive (ZK-5AD) + Servos cámara (MG90S)")
    print("")
    print("⚠️  SEGURIDAD:")
    print("   - Mantén el tanque en superficie segura")
    print("   - Observa movimientos de motores y servos")
    print("   - Usa Ctrl+C para parar inmediatamente")
    
    test = FullSystemTest()
    
    try:
        input("\n📋 Presiona ENTER para comenzar los tests completos...")
        await test.run_system_tests()
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido por usuario")
    except Exception as e:
        print(f"❌ Error durante test: {e}")
    finally:
        try:
            await test.controller.cleanup()
        except:
            pass
        print("🧹 Limpieza completada")

if __name__ == "__main__":
    asyncio.run(main())