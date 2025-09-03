#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación Flask optimizada con monitor de recursos integrado.
"""

import json
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, jsonify, request
from flask_sock import Sock

from ..config.settings import HardwareConfig, DEFAULT_CONFIG
from ..hardware.l298n_driver_optimized import L298NControllerOptimized
from ..control.joystick_controller_optimized import JoystickControllerOptimized


class SimpleResourceMonitor:
    """Monitor de recursos ligero sin dependencias externas."""
    
    def __init__(self):
        self.last_cpu_times = None
        self._get_initial_cpu_times()
    
    def _get_initial_cpu_times(self):
        """Obtiene los tiempos iniciales de CPU."""
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                times = [int(x) for x in line.split()[1:]]
                self.last_cpu_times = times
        except:
            self.last_cpu_times = None
    
    def get_cpu_percent(self) -> float:
        """Obtiene el porcentaje de uso de CPU."""
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                times = [int(x) for x in line.split()[1:]]
                
                if self.last_cpu_times:
                    idle_time = times[3] - self.last_cpu_times[3]
                    total_time = sum(times) - sum(self.last_cpu_times)
                    cpu_percent = 100.0 * (1.0 - idle_time / total_time) if total_time > 0 else 0.0
                else:
                    cpu_percent = 0.0
                
                self.last_cpu_times = times
                return min(100.0, max(0.0, cpu_percent))
        except:
            return 0.0
    
    def get_memory_info(self) -> Dict[str, float]:
        """Obtiene información de memoria."""
        try:
            mem_info = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        mem_info['total'] = int(line.split()[1]) * 1024
                    elif line.startswith('MemAvailable:'):
                        mem_info['available'] = int(line.split()[1]) * 1024
                    elif line.startswith('MemFree:'):
                        mem_info['free'] = int(line.split()[1]) * 1024
            
            if 'total' in mem_info and 'available' in mem_info:
                used = mem_info['total'] - mem_info['available']
                percent = (used / mem_info['total']) * 100.0
                return {
                    'percent': percent,
                    'used_mb': used / (1024 * 1024),
                    'total_mb': mem_info['total'] / (1024 * 1024)
                }
        except:
            pass
        
        return {'percent': 0.0, 'used_mb': 0.0, 'total_mb': 0.0}
    
    def get_temperature(self) -> Optional[float]:
        """Obtiene la temperatura del sistema."""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000.0
                return temp
        except:
            return None


class OptimizedFlaskAppWithMonitor:
    """Aplicación Flask optimizada con monitor integrado."""
    
    def __init__(self):
        self.app = Flask(__name__, template_folder='../templates', static_folder='../static')
        self.sock = Sock(self.app)
        
        # Configurar logging mínimo
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        # Configurar hardware
        self.hardware_config = DEFAULT_CONFIG
        self.motor_controller = None
        self.joystick_controller = None
        
        # Monitor de recursos
        self.resource_monitor = SimpleResourceMonitor()
        
        # Cache para evitar procesamientos innecesarios
        self._last_joystick_time = 0
        self._min_joystick_interval = 0.02  # 50 Hz máximo
        self._last_stats_time = 0
        self._min_stats_interval = 2.0  # Actualizar stats cada 2 segundos
        self._cached_stats = {}
        
        self._setup_hardware()
        self._setup_routes()
    
    def _setup_hardware(self):
        """Configura el hardware optimizado."""
        try:
            self.motor_controller = L298NControllerOptimized(
                self.hardware_config.motor_a_pins,
                self.hardware_config.motor_b_pins,
                pwm_freq=1000
            )
            
            self.joystick_controller = JoystickControllerOptimized(
                self.motor_controller.get_motor_a(),
                self.motor_controller.get_motor_b(),
                self.hardware_config.joystick_config
            )
            
        except Exception as e:
            print(f"Error configurando hardware: {e}")
            self.motor_controller = None
            self.joystick_controller = None
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema con cache."""
        current_time = time.time()
        
        # Usar cache si es reciente
        if (current_time - self._last_stats_time) < self._min_stats_interval and self._cached_stats:
            return self._cached_stats
        
        # Obtener nuevas estadísticas
        cpu_percent = self.resource_monitor.get_cpu_percent()
        memory_info = self.resource_monitor.get_memory_info()
        temperature = self.resource_monitor.get_temperature()
        
        stats = {
            'cpu_percent': round(cpu_percent, 1),
            'memory_percent': round(memory_info['percent'], 1),
            'memory_used_mb': round(memory_info['used_mb'], 1),
            'memory_total_mb': round(memory_info['total_mb'], 1),
            'temperature': round(temperature, 1) if temperature else None,
            'timestamp': int(current_time),
            'status': 'warning' if (cpu_percent > 80 or memory_info['percent'] > 85) else 'ok'
        }
        
        # Actualizar cache
        self._cached_stats = stats
        self._last_stats_time = current_time
        
        return stats
    
    def _setup_routes(self):
        """Configura las rutas optimizadas."""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def api_status():
            """Estado básico del sistema."""
            return jsonify({
                'status': 'online',
                'hardware': self.motor_controller is not None,
                'timestamp': int(time.time())
            })
        
        @self.app.route('/api/system_stats')
        def api_system_stats():
            """Estadísticas del sistema para el monitor."""
            return jsonify(self._get_system_stats())
        
        @self.app.route('/api/stop', methods=['POST'])
        def api_stop():
            """Detiene todos los motores."""
            if self.joystick_controller:
                self.joystick_controller.stop()
            return jsonify({'status': 'stopped'})
        
        @self.app.route('/api/emergency_stop', methods=['POST'])
        def api_emergency_stop():
            """Parada de emergencia."""
            if self.joystick_controller:
                self.joystick_controller.emergency_stop()
            return jsonify({'status': 'emergency_stopped'})
        
        @self.sock.route('/ws/joystick')
        def websocket_joystick(ws):
            """WebSocket optimizado para joystick."""
            try:
                while True:
                    try:
                        data = ws.receive(timeout=0.1)
                        if data:
                            self._process_joystick_data(data)
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"WebSocket error: {e}")
            finally:
                if self.joystick_controller:
                    self.joystick_controller.stop()
    
    def _process_joystick_data(self, data: str) -> None:
        """Procesa datos del joystick con throttling."""
        current_time = time.time()
        
        if current_time - self._last_joystick_time < self._min_joystick_interval:
            return
        
        try:
            joystick_data = json.loads(data)
            x = float(joystick_data.get('x', 0))
            y = float(joystick_data.get('y', 0))
            
            if self.joystick_controller:
                self.joystick_controller.process_joystick_input(x, y)
                self._last_joystick_time = current_time
                
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    
    def get_app(self) -> Flask:
        """Obtiene la instancia de Flask."""
        return self.app


def create_optimized_app() -> Flask:
    """Crea la aplicación Flask optimizada con monitor."""
    optimized_app = OptimizedFlaskAppWithMonitor()
    return optimized_app.get_app()


if __name__ == '__main__':
    app = create_optimized_app()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
