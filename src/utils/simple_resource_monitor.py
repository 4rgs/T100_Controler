#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitor de recursos simplificado sin dependencias externas.
"""

import os
import time
import threading
from typing import Dict, Any, Optional


class SimpleResourceMonitor:
    """Monitor de recursos simplificado que no requiere psutil."""
    
    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self.monitoring = False
        self.stats = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_mb': 0.0,
            'temperature': None
        }
        self._thread = None
        self._last_cpu_stats = None
    
    def start_monitoring(self):
        """Inicia el monitoreo."""
        if not self.monitoring:
            self.monitoring = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
    
    def stop_monitoring(self):
        """Detiene el monitoreo."""
        self.monitoring = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _monitor_loop(self):
        """Loop principal de monitoreo."""
        while self.monitoring:
            try:
                # CPU usando /proc/stat
                self._update_cpu_stats()
                
                # Memoria usando /proc/meminfo
                self._update_memory_stats()
                
                # Temperatura (Raspberry Pi)
                self._update_temperature()
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(self.interval)
    
    def _update_cpu_stats(self):
        """Actualiza estadísticas de CPU usando /proc/stat."""
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline().strip()
            
            # Parsear la primera línea (cpu total)
            fields = line.split()
            if len(fields) >= 8:
                # user, nice, system, idle, iowait, irq, softirq, steal
                idle = int(fields[4])
                total = sum(int(f) for f in fields[1:8])
                
                if self._last_cpu_stats:
                    last_idle, last_total = self._last_cpu_stats
                    idle_delta = idle - last_idle
                    total_delta = total - last_total
                    
                    if total_delta > 0:
                        cpu_percent = 100.0 * (1.0 - idle_delta / total_delta)
                        self.stats['cpu_percent'] = max(0.0, min(100.0, cpu_percent))
                
                self._last_cpu_stats = (idle, total)
                
        except (IOError, ValueError, IndexError):
            pass
    
    def _update_memory_stats(self):
        """Actualiza estadísticas de memoria usando /proc/meminfo."""
        try:
            meminfo = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        # Extraer solo el número (en kB)
                        value_kb = int(value.split()[0])
                        meminfo[key] = value_kb
            
            # Calcular uso de memoria
            total_kb = meminfo.get('MemTotal', 0)
            free_kb = meminfo.get('MemFree', 0)
            buffers_kb = meminfo.get('Buffers', 0)
            cached_kb = meminfo.get('Cached', 0)
            
            if total_kb > 0:
                used_kb = total_kb - free_kb - buffers_kb - cached_kb
                memory_percent = (used_kb / total_kb) * 100.0
                memory_mb = used_kb / 1024.0
                
                self.stats['memory_percent'] = max(0.0, min(100.0, memory_percent))
                self.stats['memory_mb'] = memory_mb
                
        except (IOError, ValueError, KeyError):
            pass
    
    def _update_temperature(self):
        """Actualiza temperatura del sistema."""
        try:
            # Raspberry Pi
            if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp_millicelsius = int(f.read().strip())
                    self.stats['temperature'] = temp_millicelsius / 1000.0
            else:
                self.stats['temperature'] = None
                
        except (IOError, ValueError):
            self.stats['temperature'] = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene las estadísticas actuales."""
        return self.stats.copy()
    
    def is_overloaded(self) -> bool:
        """Verifica si el sistema está sobrecargado."""
        return (self.stats['cpu_percent'] > 80.0 or 
                self.stats['memory_percent'] > 85.0 or
                (self.stats['temperature'] and self.stats['temperature'] > 70.0))
    
    def print_stats(self):
        """Imprime estadísticas en consola."""
        stats = self.get_stats()
        temp_str = f"{stats['temperature']:.1f}°C" if stats['temperature'] else "N/A"
        print(f"CPU: {stats['cpu_percent']:.1f}% | "
              f"RAM: {stats['memory_percent']:.1f}% ({stats['memory_mb']:.1f}MB) | "
              f"Temp: {temp_str}")


# Crear alias para compatibilidad
ResourceMonitor = SimpleResourceMonitor

# Instancia global del monitor
resource_monitor = SimpleResourceMonitor()


def start_resource_monitoring():
    """Inicia el monitoreo de recursos."""
    resource_monitor.start_monitoring()


def stop_resource_monitoring():
    """Detiene el monitoreo de recursos."""
    resource_monitor.stop_monitoring()


def get_resource_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de recursos."""
    return resource_monitor.get_stats()


def is_system_overloaded() -> bool:
    """Verifica si el sistema está sobrecargado."""
    return resource_monitor.is_overloaded()


if __name__ == '__main__':
    # Test del monitor
    monitor = SimpleResourceMonitor(1.0)
    monitor.start_monitoring()
    
    try:
        for i in range(10):
            time.sleep(2)
            monitor.print_stats()
            if monitor.is_overloaded():
                print("⚠️  Sistema sobrecargado!")
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop_monitoring()
