#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitor de recursos del sistema para optimización.
"""

import psutil
import time
import threading
from typing import Dict, Any


class ResourceMonitor:
    """Monitor de recursos del sistema."""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.monitoring = False
        self.stats = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_mb': 0.0,
            'temperature': None
        }
        self._thread = None
    
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
                # CPU
                self.stats['cpu_percent'] = psutil.cpu_percent()
                
                # Memoria
                memory = psutil.virtual_memory()
                self.stats['memory_percent'] = memory.percent
                self.stats['memory_mb'] = memory.used / (1024 * 1024)
                
                # Temperatura (Raspberry Pi)
                try:
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        temp = int(f.read().strip()) / 1000.0
                        self.stats['temperature'] = temp
                except:
                    self.stats['temperature'] = None
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(self.interval)
    
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
        print(f"CPU: {stats['cpu_percent']:.1f}% | "
              f"RAM: {stats['memory_percent']:.1f}% ({stats['memory_mb']:.1f}MB) | "
              f"Temp: {stats['temperature']:.1f}°C" if stats['temperature'] else "Temp: N/A")


# Instancia global del monitor
resource_monitor = ResourceMonitor()


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
    monitor = ResourceMonitor(0.5)
    monitor.start_monitoring()
    
    try:
        for i in range(10):
            time.sleep(1)
            monitor.print_stats()
            if monitor.is_overloaded():
                print("⚠️  Sistema sobrecargado!")
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop_monitoring()
