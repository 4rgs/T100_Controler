#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Versión de producción con debug mínimo para flask_app_optimized.py
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, render_template, jsonify, request
from flask_sock import Sock

from ..config.settings import HardwareConfig, DEFAULT_CONFIG
from ..hardware.l298n_driver import L298NControllerOptimized
from ..control.joystick_controller import JoystickControllerOptimized
from ..utils.resource_monitor import SimpleResourceMonitor


class OptimizedFlaskAppProduction:
    """Aplicación Flask optimizada para producción (debug mínimo)."""
    
    def __init__(self, debug_mode: bool = False):
        self.app = Flask(__name__, template_folder='../../templates', static_folder='../../static')
        self.sock = Sock(self.app)
        self.debug_mode = debug_mode
        
        # Configurar logging mínimo
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        
        # Configurar hardware
        self.hardware_config = DEFAULT_CONFIG
        self.motor_controller = None
        self.joystick_controller = None
        
        # Monitor de recursos optimizado
        self.resource_monitor = SimpleResourceMonitor(interval=3.0)  # Cada 3 segundos
        self.resource_monitor.start_monitoring()
        
        # Cache para evitar procesamientos innecesarios
        self._last_joystick_time = 0
        self._min_joystick_interval = 0.02  # 50 Hz máximo
        
        # Estadísticas de conexión
        self._connection_count = 0
        self._last_data_time = 0
        
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
                self.motor_controller,
                joystick_config,
                debug=self.debug_mode
            )
            
            if self.debug_mode:
                print("✅ Hardware configurado correctamente")
            
        except Exception as e:
            print(f"❌ Error configurando hardware: {e}")
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
                'connections': self._connection_count,
                'last_data': self._last_data_time,
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
            self._connection_count += 1
            connection_id = self._connection_count
            
            if self.debug_mode:
                print(f"🔌 WebSocket #{connection_id} conectado")
            
            connection_active = True
            error_count = 0
            max_errors = 5
            
            try:
                while connection_active and error_count < max_errors:
                    try:
                        data = ws.receive(timeout=0.5)
                        if data:
                            self._last_data_time = int(time.time())
                            self._process_joystick_data(data, connection_id)
                            error_count = 0  # Reset contador de errores en éxito
                            
                    except TimeoutError:
                        # Timeout normal, continuar
                        continue
                    except ConnectionError:
                        # Conexión cerrada normalmente
                        if self.debug_mode:
                            print(f"🔌 WebSocket #{connection_id} desconectado normalmente")
                        connection_active = False
                        break
                    except Exception as e:
                        error_count += 1
                        error_msg = str(e)
                        if "Connection closed" in error_msg:
                            if self.debug_mode:
                                print(f"🔌 WebSocket #{connection_id} cerrado por cliente")
                            connection_active = False
                            break
                        else:
                            if self.debug_mode or error_count == 1:
                                print(f"❌ Error #{error_count} en WebSocket #{connection_id}: {e}")
                            if error_count >= max_errors:
                                print(f"💥 Demasiados errores en WebSocket #{connection_id}, cerrando")
                                connection_active = False
                        
            except Exception as e:
                print(f"💥 Error crítico en WebSocket #{connection_id}: {e}")
            finally:
                if self.debug_mode:
                    print(f"🔌 Limpiando WebSocket #{connection_id}")
                # Detener motores al desconectar
                if self.joystick_controller:
                    self.joystick_controller.stop()
    
    def _process_joystick_data(self, data: str, connection_id: int = 0) -> None:
        """Procesa datos del joystick con throttling."""
        current_time = time.time()
        
        # Throttling: limitar frecuencia de actualización
        if current_time - self._last_joystick_time < self._min_joystick_interval:
            return
        
        try:
            joystick_data = json.loads(data)
            x = float(joystick_data.get('x', 0))
            y = float(joystick_data.get('y', 0))
            
            if self.debug_mode and (x != 0 or y != 0):  # Solo log cuando hay movimiento
                print(f"🎮 #{connection_id}: x={x:.2f}, y={y:.2f}")
            
            # Procesar solo si hay controlador
            if self.joystick_controller:
                self.joystick_controller.process_joystick_input(x, y)
                self._last_joystick_time = current_time
            elif self.debug_mode:
                print("❌ No hay controlador de joystick disponible")
                
        except json.JSONDecodeError as e:
            if self.debug_mode:
                print(f"❌ Error JSON en #{connection_id}: {e}")
        except (ValueError, TypeError) as e:
            if self.debug_mode:
                print(f"❌ Error de datos en #{connection_id}: {e}")
        except Exception as e:
            print(f"❌ Error procesando joystick en #{connection_id}: {e}")
    
    def get_app(self) -> Flask:
        """Obtiene la instancia de Flask."""
        return self.app


def create_optimized_app(debug: bool = False) -> Flask:
    """Crea la aplicación Flask optimizada."""
    optimized_app = OptimizedFlaskAppProduction(debug_mode=debug)
    return optimized_app.get_app()


if __name__ == '__main__':
    import os
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app = create_optimized_app(debug=debug_mode)
    app.run(host='0.0.0.0', port=5000, debug=debug_mode, threaded=True)
