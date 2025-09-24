#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T100 Camera Controller - Proceso dedicado para control de cámara
Solo maneja servos - Sin motores para evitar interferencias
"""

import asyncio
import time
import logging
import signal
import sys
from typing import Dict, Tuple
from elrs_receiver_ultra_fast import ELRSReceiverUltraFast
from mg90s_servo_driver import MG90SServoDriver

class T100CameraController:
    """Controlador dedicado para cámara solamente."""
    
    def __init__(self):
        """Inicializa el controlador de cámara."""
        self.elrs_receiver = ELRSReceiverUltraFast()
        self.servo_driver = MG90SServoDriver()
        
        # Control de bucle optimizado para no interferir
        self.is_running = False
        self.control_frequency_target = 20  # 20Hz - Frecuencia más baja para reducir carga CPU
        self.loop_count = 0
        self.last_command_time = 0
        self.failsafe_timeout = 1.5  # 1500ms (más tolerante para reducir reactividad)
        
        # Estadísticas optimizadas
        self.stats_loop_count = 0
        self.stats_start_time = time.time()
        self.skip_stats_logs = 0  # Contador para reducir logs
        
        # Configuración optimizada de logging
        logging.basicConfig(
            level=logging.WARNING,  # Solo warnings y errores para reducir I/O
            format='%(asctime)s - CAM - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Optimizaciones de proceso
        self.smooth_movement = True  # Suavizado de movimientos
        self.last_pan_cmd = 992
        self.last_tilt_cmd = 992
        self.movement_threshold = 5  # Umbral mínimo de movimiento para actualizar
        
        # Detección automática de interferencias
        self.interference_detector = {
            'loop_delays': [],
            'max_delay_threshold': 0.1,  # 100ms es demasiado para 20Hz
            'consecutive_delays': 0,
            'interference_detected': False
        }
        
        print("📹 T100 Camera Controller OPTIMIZADO inicializado")
        print("   Solo maneja: CH3 (tilt) + CH4 (pan)")
        print("   Servos: MG90S @ 20Hz (optimizado)")
        print("   Logging reducido para menor interferencia")
        print("   Detección automática de interferencias: ✅")
    
    async def initialize(self) -> bool:
        """Inicializa todos los componentes."""
        try:
            print("🔧 Inicializando componentes de cámara...")
            
            # Inicializar receptor ELRS
            if not await self.elrs_receiver.initialize():
                print("❌ Error inicializando receptor ELRS")
                return False
            
            # Inicializar driver de servos
            if not self.servo_driver.initialize():
                print("❌ Error inicializando servos MG90S")
                return False
            
            print("✅ Componentes de cámara inicializados")
            return True
            
        except Exception as e:
            print(f"❌ Error en inicialización: {e}")
            return False
    
    async def camera_control_loop(self):
        """Bucle de control optimizado dedicado solo para cámara."""
        loop_time = 1.0 / self.control_frequency_target
        
        print(f"🚀 Iniciando bucle cámara OPTIMIZADO a {self.control_frequency_target}Hz")
        
        while self.is_running:
            start_time = time.time()
            
            try:
                # Leer canales ELRS
                channels = self.elrs_receiver.read_channels_ultra_fast()
                
                if channels:
                    # Solo extraer controles de cámara
                    raw_pan = channels.get('CH4', 992)   # CH4: Pan (izquierda/derecha)
                    raw_tilt = channels.get('CH3', 992)  # CH3: Tilt (arriba/abajo)
                    
                    # OPTIMIZACIÓN: Solo actualizar si hay cambio significativo
                    pan_changed = abs(raw_pan - self.last_pan_cmd) > self.movement_threshold
                    tilt_changed = abs(raw_tilt - self.last_tilt_cmd) > self.movement_threshold
                    
                    if pan_changed or tilt_changed or (time.time() - self.last_command_time > 0.5):
                        # Aplicar control de servos de cámara solo cuando es necesario
                        pan_degrees, tilt_degrees = self.servo_driver.control_camera(
                            raw_pan,
                            raw_tilt,
                            debug=False
                        )
                        
                        # Actualizar tiempo del último comando
                        self.last_command_time = time.time()
                        self.last_pan_cmd = raw_pan
                        self.last_tilt_cmd = raw_tilt
                        
                        # Log reducido cada 40 loops (2 segundos a 20Hz) y solo si hay cambios
                        if self.loop_count % 40 == 0 and (pan_changed or tilt_changed):
                            print(f"CAM: Pan:{pan_degrees:5.1f}° Tilt:{tilt_degrees:5.1f}°")
                    
                    # Actualizar tiempo para failsafe
                    self.last_command_time = time.time()
                
                else:
                    # Verificar failsafe para cámara
                    time_since_last_command = time.time() - self.last_command_time
                    if time_since_last_command > self.failsafe_timeout:
                        self.servo_driver.center_servos()
                        # Log de failsafe muy reducido para no saturar
                        if self.skip_stats_logs % 100 == 0:  # Solo cada 100 loops sin señal
                            print("⚠️  CAM FAILSAFE: Servos centrados")
                        self.skip_stats_logs += 1
                
                self.loop_count += 1
                self.stats_loop_count += 1
                
                # OPTIMIZACIÓN: Control de frecuencia con sleep adaptativo
                elapsed = time.time() - start_time
                sleep_time = max(0.005, loop_time - elapsed)  # Mínimo 5ms para no saturar CPU
                
                # Detección automática de interferencias
                self._detect_interference(elapsed)
                
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error en bucle cámara: {e}")
                self.servo_driver.center_servos()
                await asyncio.sleep(0.1)
    
    def _detect_interference(self, loop_elapsed_time):
        """Detecta automáticamente interferencias en el bucle."""
        detector = self.interference_detector
        
        # Guardar tiempo de loop
        detector['loop_delays'].append(loop_elapsed_time)
        
        # Mantener solo los últimos 50 samples
        if len(detector['loop_delays']) > 50:
            detector['loop_delays'].pop(0)
        
        # Detectar delay excesivo
        if loop_elapsed_time > detector['max_delay_threshold']:
            detector['consecutive_delays'] += 1
            
            # Si hay 3 delays consecutivos, es interferencia
            if detector['consecutive_delays'] >= 3 and not detector['interference_detected']:
                detector['interference_detected'] = True
                print(f"⚠️  INTERFERENCIA DETECTADA: Loop delay {loop_elapsed_time*1000:.1f}ms")
                print("   Posible causa: Otro proceso usando GPIO/PWM")
                print("   Recomendación: Verificar procesos simultáneos")
        else:
            detector['consecutive_delays'] = 0
            
            # Reset detección si vuelve a la normalidad
            if detector['interference_detected'] and detector['consecutive_delays'] == 0:
                if len(detector['loop_delays']) >= 10:
                    recent_avg = sum(detector['loop_delays'][-10:]) / 10
                    if recent_avg < detector['max_delay_threshold'] * 0.5:
                        detector['interference_detected'] = False
                        print("✅ Interferencia resuelta - Funcionamiento normal")
    
    async def statistics_monitor(self):
        """Monitor optimizado de estadísticas del sistema."""
        while self.is_running:
            await asyncio.sleep(10.0)  # Cada 10 segundos (menos frecuente)
            
            if self.stats_loop_count > 0:
                elapsed = time.time() - self.stats_start_time
                avg_freq = self.stats_loop_count / elapsed
                recent_freq = self.stats_loop_count / 10.0
                
                # Solo mostrar stats si la frecuencia es estable (sin errores)
                if recent_freq > (self.control_frequency_target * 0.8):
                    print(f"📊 CAM: {recent_freq:.1f}Hz | Optimizado ✅")
                else:
                    print(f"📊 CAM: {recent_freq:.1f}Hz | ⚠️ Baja frecuencia")
                
                # Reset para próxima medición
                self.stats_loop_count = 0
                self.stats_start_time = time.time()
    
    def setup_signal_handlers(self):
        """Configura manejadores de señales para parada limpia."""
        def signal_handler(signum, frame):
            print(f"\n🛑 Señal {signum} recibida - Parando camera controller...")
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Ejecuta el controlador de cámara."""
        try:
            if not await self.initialize():
                return False
            
            self.is_running = True
            self.setup_signal_handlers()
            
            # Crear tareas concurrentes
            tasks = [
                asyncio.create_task(self.camera_control_loop()),
                asyncio.create_task(self.statistics_monitor())
            ]
            
            print("🎮 CAMERA CONTROLLER ACTIVO")
            print("   CH3 (Stick Izq Vertical) → Tilt")
            print("   CH4 (Stick Izq Horizontal) → Pan")
            print("🛑 Parar: Ctrl+C")
            
            # Ejecutar hasta interrupción
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupción del usuario")
        except Exception as e:
            print(f"❌ Error crítico en cámara: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Limpia recursos y centra servos."""
        print("🧹 Limpiando camera controller...")
        self.is_running = False
        
        # Centrar servos
        self.servo_driver.center_servos()
        
        # Limpiar componentes
        self.servo_driver.cleanup()
        await self.elrs_receiver.cleanup()
        
        print("✅ Camera controller limpiado")

async def main():
    """Función principal."""
    print("📹 T100 Camera Controller")
    print("=" * 40)
    print("Proceso dedicado para control de cámara")
    print("NO maneja motores - Solo servos")
    print("=" * 40)
    
    controller = T100CameraController()
    await controller.run()

if __name__ == "__main__":
    asyncio.run(main())