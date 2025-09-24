#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T100 Tank Drive Controller - Proceso dedicado para control de tanque
Solo maneja motores - Sin servos para evitar interferencias
"""

import asyncio
import time
import logging
import signal
import sys
from typing import Dict, Tuple
from elrs_receiver_ultra_fast import ELRSReceiverUltraFast
from zk5ad_driver_ta6586 import ZK5ADDriverTA6586

class T100TankController:
    """Controlador dedicado para tank drive solamente."""
    
    def __init__(self):
        """Inicializa el controlador de tanque."""
        self.elrs_receiver = ELRSReceiverUltraFast()
        self.motor_driver = ZK5ADDriverTA6586()
        
        # Control de bucle
        self.is_running = False
        self.control_frequency_target = 100  # 100Hz para motores
        self.loop_count = 0
        self.last_command_time = 0
        self.failsafe_timeout = 0.5  # 500ms
        
        # Estadísticas
        self.stats_loop_count = 0
        self.stats_start_time = time.time()
        
        # Configuración de logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - TANK - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        print("🚗 T100 Tank Drive Controller inicializado")
        print("   Solo maneja: CH1 (rotación) + CH2 (aceleración)")
        print("   Motores: ZK-5AD (TA6586)")
    
    def _raw_to_float(self, raw_value: int) -> float:
        """Convierte valor raw del ELRS a rango -1.0 a 1.0."""
        min_value = 172
        max_value = 1811
        
        # Mapear todo el rango (172-1811) a (-1.0 a +1.0)
        normalized = (raw_value - min_value) / (max_value - min_value)
        mapped = (normalized * 2.0) - 1.0
        
        # Limitar rango por seguridad
        return max(-1.0, min(1.0, mapped))
    
    async def initialize(self) -> bool:
        """Inicializa todos los componentes."""
        try:
            print("🔧 Inicializando componentes de tanque...")
            
            # Inicializar receptor ELRS
            if not await self.elrs_receiver.initialize():
                print("❌ Error inicializando receptor ELRS")
                return False
            
            # Inicializar driver de motores
            if not self.motor_driver.initialize():
                print("❌ Error inicializando driver ZK-5AD")
                return False
            
            print("✅ Componentes de tanque inicializados")
            return True
            
        except Exception as e:
            print(f"❌ Error en inicialización: {e}")
            return False
    
    async def tank_control_loop(self):
        """Bucle de control dedicado solo para tank drive."""
        loop_time = 1.0 / self.control_frequency_target
        
        print(f"🚀 Iniciando bucle tank drive a {self.control_frequency_target}Hz")
        
        while self.is_running:
            start_time = time.time()
            
            try:
                # Leer canales ELRS
                channels = self.elrs_receiver.read_channels_ultra_fast()
                
                if channels:
                    # Solo extraer controles de tank drive
                    raw_forward_backward = channels.get('CH2', 992)  # CH2: Aceleración
                    raw_left_right = channels.get('CH1', 992)        # CH1: Rotación
                    
                    # Convertir valores raw ELRS a rango -1.0 a 1.0
                    forward_backward = self._raw_to_float(raw_forward_backward)
                    left_right = self._raw_to_float(raw_left_right)
                    
                    # Aplicar control tank drive
                    pwm_a, pwm_b = self.motor_driver.tank_drive(
                        forward_backward, 
                        left_right, 
                        debug=False
                    )
                    
                    # Actualizar tiempo del último comando
                    self.last_command_time = time.time()
                    
                    # Log cada 100 loops (1 segundo a 100Hz)  
                    if self.loop_count % 100 == 0:
                        self.logger.info(
                            f"TANK CH1:{raw_left_right:4d} CH2:{raw_forward_backward:4d} "
                            f"LR:{left_right:+.2f} FB:{forward_backward:+.2f} PWM A:{pwm_a:3d} B:{pwm_b:3d}"
                        )
                
                else:
                    # Verificar failsafe
                    time_since_last_command = time.time() - self.last_command_time
                    if time_since_last_command > self.failsafe_timeout:
                        self.motor_driver.stop_motors()
                        if self.loop_count % 100 == 0:
                            self.logger.warning("⚠️  FAILSAFE: Sin señal ELRS - Motores parados")
                
                self.loop_count += 1
                self.stats_loop_count += 1
                
                # Control de frecuencia
                elapsed = time.time() - start_time
                sleep_time = max(0, loop_time - elapsed)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error en bucle tank: {e}")
                self.motor_driver.stop_motors()
                await asyncio.sleep(0.1)
    
    async def statistics_monitor(self):
        """Monitor de estadísticas del sistema."""
        while self.is_running:
            await asyncio.sleep(5.0)  # Cada 5 segundos
            
            if self.stats_loop_count > 0:
                elapsed = time.time() - self.stats_start_time
                avg_freq = self.stats_loop_count / elapsed
                recent_freq = self.stats_loop_count / 5.0
                
                print(f"📊 TANK: {recent_freq:.1f}Hz actual | {avg_freq:.1f}Hz promedio | Loops: {self.stats_loop_count}")
                
                # Reset para próxima medición
                self.stats_loop_count = 0
                self.stats_start_time = time.time()
    
    def setup_signal_handlers(self):
        """Configura manejadores de señales para parada limpia.""" 
        def signal_handler(signum, frame):
            print(f"\n🛑 Señal {signum} recibida - Parando tank controller...")
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Ejecuta el controlador de tanque."""
        try:
            if not await self.initialize():
                return False
            
            self.is_running = True
            self.setup_signal_handlers()
            
            # Crear tareas concurrentes
            tasks = [
                asyncio.create_task(self.tank_control_loop()),
                asyncio.create_task(self.statistics_monitor())
            ]
            
            print("🎮 TANK CONTROLLER ACTIVO")
            print("   CH1 (Stick Der Horizontal) → Rotación")
            print("   CH2 (Stick Der Vertical) → Aceleración")
            print("🛑 Parar: Ctrl+C")
            
            # Ejecutar hasta interrupción
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupción del usuario")
        except Exception as e:
            print(f"❌ Error crítico en tank: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Limpia recursos y para motores."""
        print("🧹 Limpiando tank controller...")
        self.is_running = False
        
        # Parar motores inmediatamente
        self.motor_driver.stop_motors()
        
        # Limpiar componentes
        self.motor_driver.cleanup()
        await self.elrs_receiver.cleanup()
        
        print("✅ Tank controller limpiado")

async def main():
    """Función principal."""
    print("🚗 T100 Tank Drive Controller")
    print("=" * 40)
    print("Proceso dedicado para control de tanque")
    print("NO maneja servos - Solo motores")
    print("=" * 40)
    
    controller = T100TankController()
    await controller.run()

if __name__ == "__main__":
    asyncio.run(main())