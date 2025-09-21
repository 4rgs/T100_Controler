#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controlador T100 Tank Drive - Solo palanca derecha
Sistema de tank drive simple usando CH2 (forward/back) y CH4 (left/right)
"""

import asyncio
import time
import logging
from typing import Dict, Tuple
from elrs_receiver_ultra_fast import ELRSReceiverUltraFast
from zk5ad_driver_ta6586 import ZK5ADDriverTA6586

class T100TankController:
    """Controlador T100 con tank drive simple."""
    
    def __init__(self):
        """Inicializa el controlador tank."""
        self.elrs_receiver = ELRSReceiverUltraFast()
        self.motor_driver = ZK5ADDriverTA6586()
        
        # Control de bucle
        self.is_running = False
        self.control_frequency_target = 100  # 100Hz
        self.loop_count = 0
        self.last_command_time = 0
        self.failsafe_timeout = 0.5  # 500ms
        
        # Logging
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        print("🚗 T100 Tank Controller inicializado")
    
    def _process_channels_tank(self, channels: Dict[str, float]) -> Tuple[float, float]:
        """
        Procesamiento de canales para tank drive.
        SOLO PALANCA DERECHA - CH2 y CH4
        
        Args:
            channels: Canales ELRS
            
        Returns:
            Tupla (forward_backward, left_right)
        """
        if not channels:
            return 0.0, 0.0
        
        # Debug de canales cada segundo
        if self.loop_count % 100 == 0:
            print(f"\n🕹️ PALANCA DERECHA DETECTADA:")
            ch2 = channels.get('CH2', 0.0) 
            ch4 = channels.get('CH4', 0.0)
            print(f"   CH2 (Forward/Back): {ch2:+.3f}")
            print(f"   CH4 (Left/Right): {ch4:+.3f}")
            print(f"   🚫 Ignorando: CH1, CH3, otros canales")
        
        # MAPEO SIMPLE PALANCA DERECHA:
        # CH2 = Forward/Backward (vertical)
        # CH4 = Left/Right (horizontal)
        
        forward_backward = channels.get('CH2', 0.0)  # Vertical
        left_right = channels.get('CH4', 0.0)        # Horizontal
        
        return forward_backward, left_right
    
    async def tank_control_loop(self):
        """Bucle de control tank drive."""
        loop_time_target = 1.0 / self.control_frequency_target  # 10ms para 100Hz
        
        while self.is_running:
            loop_start = time.perf_counter()
            
            try:
                # Lectura de canales
                channels = self.elrs_receiver.read_channels_ultra_fast()
                
                if channels:
                    # Procesamiento para tank drive
                    forward_backward, left_right = self._process_channels_tank(channels)
                    
                    # Control tank drive
                    pwm_a, pwm_b = self.motor_driver.tank_drive(forward_backward, left_right)
                    
                    # Debug cada 50 loops (0.5 segundos)
                    if self.loop_count % 50 == 0:
                        print(f"Motor A: PWM={pwm_a} | Motor B: PWM={pwm_b}")
                    
                    # Actualizar timestamp
                    self.last_command_time = time.time()
                    
                else:
                    # Failsafe
                    if time.time() - self.last_command_time > self.failsafe_timeout:
                        self.motor_driver.stop_motors()
                
                self.loop_count += 1
                
            except Exception as e:
                self.logger.error(f"Error en control loop: {e}")
                self.motor_driver.stop_motors()
            
            # Sleep adaptativo
            loop_elapsed = time.perf_counter() - loop_start
            sleep_time = max(0, loop_time_target - loop_elapsed)
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    async def status_monitor_tank(self):
        """Monitor de estado tank drive."""
        while self.is_running:
            try:
                await asyncio.sleep(5.0)  # Cada 5 segundos
                
                if self.loop_count > 0:
                    actual_freq = self.loop_count / 5.0  # Frecuencia aproximada
                    
                    print(f"📊 Estado Tank Controller:")
                    print(f"   Frecuencia: ~{actual_freq:.0f}Hz")
                    print(f"   Loops ejecutados: {self.loop_count}")
                    print(f"   Control: Tank Drive (CH2+CH4)")
                    
                    # Reset contador
                    self.loop_count = 0
                
                # Estadísticas ELRS
                if self.elrs_receiver:
                    elrs_stats = self.elrs_receiver.get_performance_stats()
                    print(f"   ELRS: {elrs_stats['packets_received']} pkts, {elrs_stats['errors']} errors")
                
                # Estado de motores
                if self.motor_driver:
                    motor_status = self.motor_driver.get_motor_status()
                    print(f"   Motor A (Izq): {motor_status['motor_a']['direction']} {motor_status['motor_a']['power_percent']:.0f}%")
                    print(f"   Motor B (Der): {motor_status['motor_b']['direction']} {motor_status['motor_b']['power_percent']:.0f}%")
                
            except Exception as e:
                self.logger.error(f"Error en monitor: {e}")
    
    def show_tank_info(self):
        """Mostrar información del tank drive."""
        print("\n🚗 TANK DRIVE - SOLO PALANCA DERECHA:")
        print("   Forward/Back controlado por CH2")
        print("   Left/Right controlado por CH4")
        print("   🚫 IGNORA completamente: CH1, CH3")
        print("\n📋 MAPEO DE CANALES:")
        print("   CH2 → Forward/Backward (palanca derecha ⬆️⬇️)")
        print("   CH4 → Left/Right (palanca derecha ⬅️➡️)")
        print("\n🚗 CONTROLES TANK DRIVE:")
        print("   ✅ Palanca derecha VERTICAL = Adelante/Atrás")
        print("   ✅ Palanca derecha HORIZONTAL = Izquierda/Derecha")
        print("   🚫 Palanca izquierda = IGNORADA")
        print("\n⚙️ VENTAJAS:")
        print("   - Tank drive clásico y confiable")
        print("   - Solo una palanca para controlar")
        print("   - Sin problemas de canales invertidos")
        print("   - Lógica simple y directa")
    
    async def start_tank_controller(self):
        """Inicia el controlador tank."""
        print("\n🚀 Iniciando T100 Tank Controller...")
        
        # Inicializar ELRS
        if not await self.elrs_receiver.initialize():
            print("❌ No se pudo inicializar receptor ELRS")
            return False
        
        # Inicializar driver de motores
        if not self.motor_driver.initialize():
            print("❌ No se pudo inicializar driver de motores")
            return False
        
        # Mostrar información
        self.show_tank_info()
        
        # Iniciar bucles
        self.is_running = True
        self.last_command_time = time.time()
        
        try:
            # Ejecutar bucles concurrentemente
            await asyncio.gather(
                self.tank_control_loop(),
                self.status_monitor_tank()
            )
        except KeyboardInterrupt:
            print("\n🛑 Controlador interrumpido por usuario")
        except Exception as e:
            self.logger.error(f"Error en controlador: {e}")
        finally:
            await self.cleanup()
        
        return True
    
    async def cleanup(self):
        """Limpia recursos."""
        print("\n🧹 Limpiando recursos...")
        self.is_running = False
        
        if self.motor_driver:
            self.motor_driver.cleanup()
        
        if self.elrs_receiver:
            await self.elrs_receiver.cleanup()
        
        print("✅ Limpieza completada")

# Función principal
async def main():
    """Función principal del controlador tank."""
    controller = T100TankController()
    await controller.start_tank_controller()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Tank Controller terminado")
