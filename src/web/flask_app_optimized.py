#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación Flask optimizada para mínimo uso de recursos.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, jsonify, request
from flask_sock import Sock

from ..config.settings import HardwareConfig, DEFAULT_CONFIG
from ..hardware.l298n_driver_optimized import L298NControllerOptimized
from ..control.joystick_controller_optimized import JoystickControllerOptimized
from ..utils.simple_resource_monitor import SimpleResourceMonitor


class OptimizedFlaskApp:
    """Aplicación Flask optimizada."""
    
    def __init__(self):
        self.app = Flask(__name__, template_folder='../../templates', static_folder='../../static')
        self.sock = Sock(self.app)
        
        # Configurar logging mínimo
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        # Configurar hardware
        self.hardware_config = DEFAULT_CONFIG
        self.motor_controller = None
        self.joystick_controller = None
        
        # Monitor de recursos optimizado
        self.resource_monitor = SimpleResourceMonitor(interval=2.0)  # Cada 2 segundos
        self.resource_monitor.start_monitoring()
        
        # Cache para evitar procesamientos innecesarios
        self._last_joystick_time = 0
        self._min_joystick_interval = 0.02  # 50 Hz máximo
        
        self._setup_hardware()
        self._setup_routes()
    
    def _setup_hardware(self):
        """Configura el hardware optimizado."""
        try:
            hardware_config = self.hardware_config["hardware"]
            joystick_config = self.hardware_config["joystick"]
            
            self.motor_controller = L298NControllerOptimized(
                hardware_config.motor_a,
                hardware_config.motor_b,
                pwm_freq=hardware_config.pwm_frequency
            )
            
            self.joystick_controller = JoystickControllerOptimized(
                self.motor_controller.get_motor_a(),
                self.motor_controller.get_motor_b(),
                joystick_config
            )
            
        except Exception as e:
            print(f"Error configurando hardware: {e}")
            self.motor_controller = None
            self.joystick_controller = None
    
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
        
        @self.app.route('/api/resources')
        def api_resources():
            """Obtiene estadísticas de recursos del sistema."""
            stats = self.resource_monitor.get_stats()
            return jsonify({
                'cpu_percent': round(stats['cpu_percent'], 1),
                'memory_percent': round(stats['memory_percent'], 1),
                'memory_mb': round(stats['memory_mb'], 1),
                'temperature': round(stats['temperature'], 1) if stats['temperature'] else None,
                'overloaded': self.resource_monitor.is_overloaded(),
                'timestamp': int(time.time())
            })
        
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
            print("🔌 Nueva conexión WebSocket establecida")
            try:
                while True:
                    # Recibir datos con timeout más largo
                    try:
                        data = ws.receive(timeout=1.0)  # 1 segundo timeout
                        if data:
                            print(f"📥 Datos recibidos: {data[:50]}...")  # Debug: primeros 50 chars
                            self._process_joystick_data(data)
                    except TimeoutError:
                        # Timeout normal, continuar
                        continue
                    except Exception as e:
                        print(f"❌ Error recibiendo datos WebSocket: {e}")
                        continue
                        
            except Exception as e:
                print(f"💥 WebSocket error: {e}")
            finally:
                print("🔌 Conexión WebSocket cerrada")
                # Detener motores al desconectar
                if self.joystick_controller:
                    self.joystick_controller.stop()
    
    def _process_joystick_data(self, data: str) -> None:
        """Procesa datos del joystick con throttling."""
        current_time = time.time()
        
        # Throttling: limitar frecuencia de actualización
        if current_time - self._last_joystick_time < self._min_joystick_interval:
            return
        
        try:
            joystick_data = json.loads(data)
            x = float(joystick_data.get('x', 0))
            y = float(joystick_data.get('y', 0))
            
            print(f"🎮 Joystick: x={x:.2f}, y={y:.2f}")  # Debug
            
            # Procesar solo si hay controlador
            if self.joystick_controller:
                self.joystick_controller.process_joystick_input(x, y)
                self._last_joystick_time = current_time
                print(f"✅ Comando enviado a motores")  # Debug
            else:
                print(f"❌ No hay controlador de joystick disponible")  # Debug
                
        except json.JSONDecodeError as e:
            print(f"❌ Error JSON: {e}")
        except (ValueError, TypeError) as e:
            print(f"❌ Error de datos: {e}")
        except Exception as e:
            print(f"❌ Error procesando joystick: {e}")
    
    def get_app(self) -> Flask:
        """Obtiene la instancia de Flask."""
        return self.app


def create_optimized_app() -> Flask:
    """Crea la aplicación Flask optimizada."""
    optimized_app = OptimizedFlaskApp()
    return optimized_app.get_app()


if __name__ == '__main__':
    app = create_optimized_app()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
