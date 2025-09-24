#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Receptor ELRS Ultra-Rápido - Optimizado para máxima responsividad
Diseñado para latencia mínima y máximo rendimiento en RPi Zero 2W
"""

import asyncio
import serial
import time
import logging
import struct
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
import threading
from collections import deque


@dataclass
class ELRSConfigUltraFast:
    """Configuración ultra-optimizada para ELRS."""
    serial_port: str = "/dev/ttyAMA0"
    baud_rate: int = 420000
    timeout: float = 0.001  # 1ms timeout ultra-rápido
    buffer_size: int = 4096  # Buffer más grande
    read_chunk_size: int = 256  # Leer en chunks más grandes


class ELRSReceiverUltraFast:
    """Receptor ELRS ultra-optimizado para máxima responsividad."""
    
    def __init__(self, config: ELRSConfigUltraFast = None):
        """
        Inicializa el receptor ELRS ultra-rápido.
        
        Args:
            config: Configuración ELRS optimizada
        """
        self.config = config or ELRSConfigUltraFast()
        self.serial_connection = None
        self.is_connected = False
        
        # Buffer circular ultra-rápido
        self.buffer = bytearray()
        self.max_buffer_size = self.config.buffer_size
        
        # Cache de canales para acceso ultra-rápido
        self.channels_cache = {}
        self.last_valid_channels = {}
        self.last_update_time = 0
        
        # Estadísticas optimizadas
        self.packets_received = 0
        self.crsf_packets = 0
        self.sbus_packets = 0
        self.errors = 0
        self.parse_time_avg = 0.0
        
        # Threading para lectura asíncrona
        self.read_thread = None
        self.read_thread_running = False
        self.data_queue = deque(maxlen=100)  # Queue circular
        
        # Pre-compilar patrones de búsqueda
        self.crsf_header = 0xC8
        self.sbus_header = 0x0F
        self.sbus_footer = 0x00
        
        # Logger optimizado
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.WARNING)  # Solo errores críticos
    
    async def initialize(self) -> bool:
        """Inicializa la conexión serial ultra-rápida."""
        ports_to_try = [
            self.config.serial_port,
            "/dev/ttyAMA0",
            "/dev/serial0", 
            "/dev/ttyUSB0"
        ]
        
        baud_rates = [420000, 115200]  # Solo los más comunes
        
        for port in ports_to_try:
            if not self._port_exists(port):
                continue
                
            for baud in baud_rates:
                if await self._try_connect_fast(port, baud):
                    self.config.serial_port = port
                    self.config.baud_rate = baud
                    self._start_read_thread()
                    self.logger.info(f"✅ ELRS Ultra-Fast: {port} @ {baud}")
                    return True
        
        self.logger.error("❌ No se pudo conectar a receptor ELRS")
        return False
    
    def _port_exists(self, port: str) -> bool:
        """Verificación rápida de puerto."""
        import os
        return os.path.exists(port)
    
    async def _try_connect_fast(self, port: str, baud_rate: int) -> bool:
        """Conexión ultra-rápida con validación mínima."""
        try:
            test_serial = serial.Serial(
                port=port,
                baudrate=baud_rate,
                timeout=self.config.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                rtscts=False,
                dsrdtr=False,
                xonxoff=False
            )
            
            # Test rápido - solo 0.5 segundos
            test_serial.reset_input_buffer()
            data_received = 0
            
            for _ in range(25):  # 0.5 segundos a 50Hz
                if test_serial.in_waiting > 0:
                    data = test_serial.read(min(test_serial.in_waiting, 64))
                    data_received += len(data)
                    
                    # Verificación rápida de headers válidos
                    if any(b in [0xC8, 0x0F] for b in data):
                        self.serial_connection = test_serial
                        self.is_connected = True
                        return True
                
                await asyncio.sleep(0.02)
            
            test_serial.close()
            return data_received > 10  # Mínimo de datos
            
        except Exception:
            return False
    
    def _start_read_thread(self):
        """Inicia thread de lectura dedicado para máximo rendimiento."""
        self.read_thread_running = True
        self.read_thread = threading.Thread(target=self._read_thread_worker, daemon=True)
        self.read_thread.start()
    
    def _read_thread_worker(self):
        """Worker thread para lectura continua sin bloqueos."""
        while self.read_thread_running and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    # Leer chunk grande de una vez
                    chunk_size = min(self.serial_connection.in_waiting, self.config.read_chunk_size)
                    data = self.serial_connection.read(chunk_size)
                    
                    if data:
                        # Agregar a queue thread-safe
                        self.data_queue.append(data)
                        
                        # Limitar tamaño del buffer principal
                        if len(self.buffer) > self.max_buffer_size:
                            self.buffer = self.buffer[-self.max_buffer_size//2:]
                
                # Sleep mínimo para no saturar CPU
                time.sleep(0.001)  # 1ms
                
            except Exception as e:
                self.logger.error(f"Error en read thread: {e}")
                time.sleep(0.01)
    
    def read_channels_ultra_fast(self) -> Optional[Dict[str, float]]:
        """
        Lectura ultra-rápida de canales con procesamiento optimizado.
        
        Returns:
            Diccionario con canales o None si no hay datos válidos
        """
        if not self.is_connected:
            return None
        
        start_time = time.perf_counter()
        
        try:
            # Procesar datos del queue
            while self.data_queue:
                data_chunk = self.data_queue.popleft()
                self.buffer.extend(data_chunk)
            
            # Procesar buffer si hay suficientes datos
            if len(self.buffer) < 25:  # Mínimo para un paquete SBUS
                return self.last_valid_channels
            
            # Buscar y procesar paquetes de forma optimizada
            channels = self._process_buffer_optimized()
            
            if channels:
                self.last_valid_channels = channels
                self.last_update_time = time.time()
                
                # Actualizar estadísticas de rendimiento
                parse_time = time.perf_counter() - start_time
                self.parse_time_avg = (self.parse_time_avg * 0.9 + parse_time * 0.1)
                
                return channels
            
            # Retornar último válido si es reciente (< 100ms)
            if time.time() - self.last_update_time < 0.1:
                return self.last_valid_channels
                
            return None
            
        except Exception as e:
            self.errors += 1
            return self.last_valid_channels
    
    def _process_buffer_optimized(self) -> Optional[Dict[str, float]]:
        """Procesamiento de buffer ultra-optimizado."""
        if len(self.buffer) < 25:
            return None
        
        # Buscar SBUS primero (más común y rápido de procesar)
        sbus_idx = self._find_sbus_fast()
        if sbus_idx >= 0:
            packet = self._extract_sbus_fast(sbus_idx)
            if packet:
                channels = self._parse_sbus_ultra_fast(packet)
                if channels:
                    self._cleanup_buffer(sbus_idx + 25)
                    return channels
        
        # Buscar CRSF como respaldo
        crsf_idx = self._find_crsf_fast()
        if crsf_idx >= 0:
            packet = self._extract_crsf_fast(crsf_idx)
            if packet:
                channels = self._parse_crsf_ultra_fast(packet)
                if channels:
                    self._cleanup_buffer(crsf_idx + len(packet))
                    return channels
        
        # Limpiar buffer si está muy lleno
        if len(self.buffer) > self.max_buffer_size * 0.8:
            self.buffer = self.buffer[-100:]
        
        return None
    
    def _find_sbus_fast(self) -> int:
        """Búsqueda ultra-rápida de paquete SBUS."""
        for i in range(len(self.buffer) - 24):
            if (self.buffer[i] == 0x0F and 
                i + 24 < len(self.buffer) and
                self.buffer[i + 24] == 0x00):
                return i
        return -1
    
    def _find_crsf_fast(self) -> int:
        """Búsqueda ultra-rápida de paquete CRSF."""
        for i in range(len(self.buffer) - 5):
            if self.buffer[i] == 0xC8:
                return i
        return -1
    
    def _extract_sbus_fast(self, start_idx: int) -> Optional[bytes]:
        """Extracción ultra-rápida de paquete SBUS."""
        if start_idx + 25 <= len(self.buffer):
            return bytes(self.buffer[start_idx:start_idx + 25])
        return None
    
    def _extract_crsf_fast(self, start_idx: int) -> Optional[bytes]:
        """Extracción ultra-rápida de paquete CRSF."""
        if start_idx + 2 < len(self.buffer):
            length = self.buffer[start_idx + 1]
            if length > 2 and start_idx + length + 2 <= len(self.buffer):
                return bytes(self.buffer[start_idx:start_idx + length + 2])
        return None
    
    def _parse_sbus_ultra_fast(self, packet: bytes) -> Optional[Dict[str, float]]:
        """Parser SBUS ultra-optimizado."""
        if len(packet) != 25 or packet[0] != 0x0F or packet[24] != 0x00:
            return None
        
        try:
            channels = {}
            channel_data = packet[1:23]
            
            # Procesar solo los primeros 8 canales para máxima velocidad
            for ch in range(8):
                bit_offset = ch * 11
                byte_offset = bit_offset // 8
                bit_in_byte = bit_offset % 8
                
                if byte_offset + 1 < len(channel_data):
                    if byte_offset + 2 < len(channel_data):
                        raw_value = (
                            (channel_data[byte_offset] >> bit_in_byte) |
                            (channel_data[byte_offset + 1] << (8 - bit_in_byte)) |
                            (channel_data[byte_offset + 2] << (16 - bit_in_byte))
                        ) & 0x7FF
                    else:
                        raw_value = (
                            (channel_data[byte_offset] >> bit_in_byte) |
                            (channel_data[byte_offset + 1] << (8 - bit_in_byte))
                        ) & 0x7FF
                    
                    # Pasar valor raw sin normalización ni inversión
                    channels[f'CH{ch + 1}'] = raw_value
            
            self.sbus_packets += 1
            self.packets_received += 1
            return channels
            
        except Exception:
            self.errors += 1
            return None
    
    def _parse_crsf_ultra_fast(self, packet: bytes) -> Optional[Dict[str, float]]:
        """Parser CRSF ultra-optimizado."""
        if len(packet) < 26 or packet[0] != 0xC8 or packet[2] != 0x16:
            return None
        
        try:
            channels = {}
            channel_data = packet[3:25]
            
            # Procesar solo primeros 8 canales
            for i in range(8):
                start_bit = i * 11
                byte_idx = start_bit // 8
                bit_offset = start_bit % 8
                
                if byte_idx + 1 < len(channel_data):
                    raw_value = (
                        (channel_data[byte_idx] >> bit_offset) |
                        (channel_data[byte_idx + 1] << (8 - bit_offset))
                    ) & 0x7FF
                    
                    # Pasar valor raw sin normalización ni inversión
                    channels[f'CH{i + 1}'] = raw_value
            
            self.crsf_packets += 1
            self.packets_received += 1
            return channels
            
        except Exception:
            self.errors += 1
            return None
    
    def _cleanup_buffer(self, processed_bytes: int):
        """Limpieza ultra-rápida del buffer."""
        if processed_bytes > 0:
            self.buffer = self.buffer[processed_bytes:]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de rendimiento."""
        return {
            'connected': self.is_connected,
            'port': self.config.serial_port,
            'baud_rate': self.config.baud_rate,
            'packets_received': self.packets_received,
            'crsf_packets': self.crsf_packets,
            'sbus_packets': self.sbus_packets,
            'errors': self.errors,
            'parse_time_avg_ms': self.parse_time_avg * 1000,
            'buffer_size': len(self.buffer),
            'queue_size': len(self.data_queue),
            'last_update': self.last_update_time
        }
    
    async def cleanup(self):
        """Limpieza ultra-rápida de recursos."""
        self.is_connected = False
        self.read_thread_running = False
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=0.1)
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()


# Test ultra-rápido
async def test_ultra_fast_receiver():
    """Test del receptor ultra-rápido."""
    print("🚀 Test Receptor ELRS Ultra-Fast")
    
    receiver = ELRSReceiverUltraFast()
    
    if await receiver.initialize():
        print("✅ Receptor ultra-rápido inicializado")
        
        try:
            start_time = time.time()
            samples = 0
            
            for i in range(500):  # 5 segundos a 100Hz
                channels = receiver.read_channels_ultra_fast()
                
                if channels and i % 20 == 0:  # Mostrar cada 200ms
                    ch1 = channels.get('CH1', 0)
                    ch2 = channels.get('CH2', 0)
                    ch3 = channels.get('CH3', 0)
                    ch4 = channels.get('CH4', 0)
                    
                    elapsed = time.time() - start_time
                    rate = samples / elapsed if elapsed > 0 else 0
                    
                    print(f"[{rate:.0f}Hz] CH1:{ch1:4d} CH2:{ch2:4d} CH3:{ch3:4d} CH4:{ch4:4d}")
                    samples += 1
                
                await asyncio.sleep(0.01)  # 100Hz
                
        except KeyboardInterrupt:
            print("\n🛑 Test interrumpido")
        
        # Estadísticas finales
        stats = receiver.get_performance_stats()
        print(f"\n📊 Estadísticas Ultra-Fast:")
        print(f"  Paquetes: {stats['packets_received']}")
        print(f"  SBUS: {stats['sbus_packets']}")
        print(f"  CRSF: {stats['crsf_packets']}")
        print(f"  Errores: {stats['errors']}")
        print(f"  Tiempo parse promedio: {stats['parse_time_avg_ms']:.2f}ms")
        print(f"  Buffer size: {stats['buffer_size']} bytes")
        
        await receiver.cleanup()
    else:
        print("❌ No se pudo inicializar receptor ultra-rápido")


if __name__ == "__main__":
    asyncio.run(test_ultra_fast_receiver())
