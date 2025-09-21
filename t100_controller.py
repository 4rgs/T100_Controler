#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T100 ZK-5AD Tank Controller - Versión simplificada y moderna
Controlador principal para T100 con ZK-5AD (TA6586) y control tank drive
"""

import asyncio
import time
import logging
from typing import Dict, Tuple
from elrs_receiver_ultra_fast import ELRSReceiverUltraFast
from zk5ad_driver_ta6586 import ZK5ADDriverTA6586

class T100Controller:
    """Controlador principal T100 con ZK-5AD tank drive."""
    
    def __init__(self):
        """Inicializa el controlador T100."""
        self.elrs_receiver = ELRSReceiverUltraFast()
        self.motor_driver = ZK5ADDriverTA6586()
        
        # Control de bucle
        self.is_running = False
        self.control_frequency_target = 100  # 100Hz
        self.loop_count = 0
        self.last_command_time = 0
        self.failsafe_timeout = 0.5  # 500ms
        
        # Configuración de logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        print("🎮 T100 ZK-5AD Controller inicializado")
    
    async def initialize(self) -> bool:
        """Inicializa todos los componentes."""
        try:
            print("🔧 Inicializando componentes...")
            
            # Inicializar receptor ELRS
            if not await self.elrs_receiver.initialize():
                print("❌ Error inicializando receptor ELRS")
                return False
            
            # Inicializar driver de motores
            if not self.motor_driver.initialize():
                print("❌ Error inicializando driver ZK-5AD")
                return False
            
            print("✅ Todos los componentes inicializados")
            return True
            
        except Exception as e:
            print(f"❌ Error en inicialización: {e}")
            return False
    
    async def control_loop(self):
        """Bucle principal de control."""
        loop_time = 1.0 / self.control_frequency_target
        
        print(f"🚀 Iniciando bucle de control a {self.control_frequency_target}Hz")
        
        while self.is_running:
            start_time = time.time()
            
            try:
                # Leer canales ELRS
                channels = await self.elrs_receiver.read_channels()
                
                if channels:
                    # Extraer controles de tank drive
                    forward_backward = channels.get('CH2', 0.0)  # Palanca derecha vertical
                    left_right = channels.get('CH4', 0.0)       # Palanca derecha horizontal
                    
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
                            f"FB: {forward_backward:6.3f} | LR: {left_right:6.3f} | "
                            f"A: {pwm_a:3d} | B: {pwm_b:3d}"
                        )
                
                else:
                    # Verificar failsafe
                    time_since_last_command = time.time() - self.last_command_time
                    if time_since_last_command > self.failsafe_timeout:
                        self.motor_driver.stop_motors()
                        if self.loop_count % 100 == 0:
                            self.logger.warning("⚠️  FAILSAFE: Sin señal ELRS - Motores parados")
                
                self.loop_count += 1
                
                # Control de frecuencia
                elapsed = time.time() - start_time
                sleep_time = max(0, loop_time - elapsed)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Error en bucle de control: {e}")
                self.motor_driver.stop_motors()
                await asyncio.sleep(0.1)
    
    async def run(self):
        """Ejecuta el controlador principal."""
        try:
            if not await self.initialize():
                return False
            
            self.is_running = True
            
            # Crear tareas concurrentes
            tasks = [
                asyncio.create_task(self.control_loop()),
                asyncio.create_task(self._monitor_system())
            ]
            
            # Ejecutar hasta interrupción
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupción del usuario")
        except Exception as e:
            print(f"❌ Error crítico: {e}")
        finally:
            await self.cleanup()
    
    async def _monitor_system(self):
        """Monitor del sistema para estadísticas."""
        while self.is_running:
            await asyncio.sleep(5.0)  # Cada 5 segundos
            
            if self.loop_count > 0:
                freq = self.loop_count / 5.0
                print(f"📊 Frecuencia real: {freq:.1f}Hz | Loops: {self.loop_count}")
                self.loop_count = 0
    
    async def cleanup(self):
        """Limpia recursos y para motores."""
        print("🧹 Limpiando recursos...")
        self.is_running = False
        
        # Parar motores
        self.motor_driver.stop_motors()
        
        # Limpiar componentes
        self.motor_driver.cleanup()
        await self.elrs_receiver.cleanup()
        
        print("✅ Limpieza completada")

async def main():
    """Función principal."""
    print("🚀 T100 ZK-5AD Tank Controller")
    print("=" * 50)
    print("🎮 Control: Palanca derecha (CH2=FB, CH4=LR)")
    print("🛑 Parar: Ctrl+C")
    print("=" * 50)
    
    controller = T100Controller()
    await controller.run()

if __name__ == "__main__":
    asyncio.run(main())