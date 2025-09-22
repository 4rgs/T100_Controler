#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T100 ZK-5AD Tank Controller - Versión simplificada y moderna
Controlador principal para T100 con ZK-5AD (TA6586) y control tank drive

NOTA: El receptor ELRS devuelve valores raw sin normalización (172-1811)
Este controlador convierte esos valores al rango -1.0 a 1.0 que espera el driver de motores.
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
    
    def _raw_to_float(self, raw_value: int) -> float:
        """
        Convierte valor raw del ELRS a rango -1.0 a 1.0 usando rango completo.
        
        Args:
            raw_value: Valor raw del ELRS (172-1811)
            
        Returns:
            Valor flotante en rango -1.0 a 1.0
            - 172 (mínimo) -> -1.0 (máximo PWM reversa)
            - 992 (centro) -> 0.0 (parado)
            - 1811 (máximo) -> +1.0 (máximo PWM adelante)
        """
        # Definir rangos del ELRS
        min_value = 172
        max_value = 1811
        center = 992
        
        # Mapear todo el rango (172-1811) a (-1.0 a +1.0)
        # Normalizar primero a 0.0-1.0, luego a -1.0/+1.0
        normalized = (raw_value - min_value) / (max_value - min_value)  # 0.0 - 1.0
        mapped = (normalized * 2.0) - 1.0  # -1.0 - +1.0
        
        # Limitar rango por seguridad
        return max(-1.0, min(1.0, mapped))
    
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
                channels = self.elrs_receiver.read_channels_ultra_fast()
                
                if channels:
                    # Extraer controles de tank drive (valores raw del ELRS)
                    raw_forward_backward = channels.get('CH2', 992)  # Palanca derecha vertical
                    raw_left_right = channels.get('CH4', 992)       # Palanca derecha horizontal
                    
                    # Convertir valores raw ELRS a rango -1.0 a 1.0 para el driver
                    # ELRS típico: centro=992, min=172, max=1811
                    forward_backward = self._raw_to_float(raw_forward_backward)
                    left_right = self._raw_to_float(raw_left_right)
                    
                    # Aplicar control tank drive
                    pwm_a, pwm_b = self.motor_driver.tank_drive(
                        forward_backward, 
                        left_right, 
                        debug=False  # Debug desactivado para funcionamiento normal
                    )
                    
                    # Actualizar tiempo del último comando
                    self.last_command_time = time.time()
                    
                    # Log cada 100 loops (1 segundo a 100Hz)
                    if self.loop_count % 100 == 0:
                        self.logger.info(
                            f"RAW CH2:{raw_forward_backward:4d} CH4:{raw_left_right:4d} | "
                            f"CONV FB:{forward_backward:+.3f} LR:{left_right:+.3f} | "
                            f"PWM A:{pwm_a:3d} B:{pwm_b:3d}"
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