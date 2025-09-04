#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T100 API Minimalista - Solo para control de motores
API pura sin interfaz web, optimizada para máxima performance
"""

import json
import os
import time
from pathlib import Path
from flask import Flask, jsonify, request
from flask_sock import Sock
from flask_cors import CORS

from ..config.settings import get_ultra_low_latency_config
from ..hardware.l298n_driver_ultra import UltraFastL298NController
from ..control.joystick_controller_ultra import UltraFastJoystickController


class T100MinimalAPI:
    """API minimalista para control T100 - Solo endpoints esenciales."""
    
    def __init__(self):
        self.app = Flask(__name__)
        
        # CORS para desarrollo (permitir conexiones desde cualquier origen)
        CORS(self.app, origins="*", allow_headers="*", methods="*")
        
        self.sock = Sock(self.app)
        
        # Configuración ultra-baja latencia
        config = get_ultra_low_latency_config()
        debug_mode = os.getenv('T100_DEBUG', 'false').lower() == 'true'
        
        # Inicializar hardware ultra-optimizado
        self.motor_controller = UltraFastL298NController(
            config["hardware"].motor_a,
            config["hardware"].motor_b,
            config["hardware"].pwm_frequency,
            debug=debug_mode
        )
        
        self.joystick_controller = UltraFastJoystickController(
            self.motor_controller,
            config["joystick"],
            debug=debug_mode
        )
        
        # Stats para monitoreo
        self.stats = {
            'commands_processed': 0,
            'active_connections': 0,
            'start_time': time.time(),
            'last_command_time': 0
        }
        
        if debug_mode:
            print("⚡ T100 MINIMAL API ACTIVATED")
            print(f"🎮 Deadzone: {config['joystick'].deadzone}")
            print(f"⚙️ PWM Freq: {config['hardware'].pwm_frequency}Hz")
            print("🌐 CORS habilitado para desarrollo")
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Configurar rutas API minimalistas."""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Estado básico del sistema."""
            uptime = time.time() - self.stats['start_time']
            return jsonify({
                'status': 'online',
                'uptime_seconds': round(uptime, 1),
                'commands_processed': self.stats['commands_processed'],
                'active_connections': self.stats['active_connections'],
                'last_command_age_ms': round((time.time() - self.stats['last_command_time']) * 1000) if self.stats['last_command_time'] > 0 else None,
                'hardware_ready': self.motor_controller is not None,
                'timestamp': int(time.time() * 1000)
            })
        
        @self.app.route('/api/control/stop', methods=['POST'])
        def stop_motors():
            """Detener todos los motores."""
            self.joystick_controller.stop()
            return jsonify({'status': 'stopped', 'timestamp': int(time.time() * 1000)})
        
        @self.app.route('/api/control/emergency', methods=['POST'])
        def emergency_stop():
            """Parada de emergencia."""
            self.joystick_controller.emergency_stop()
            return jsonify({'status': 'emergency_stopped', 'timestamp': int(time.time() * 1000)})
        
        @self.app.route('/api/control/move', methods=['POST'])
        def move_robot():
            """Control directo por HTTP (para testing)."""
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            try:
                x = float(data.get('x', 0.0))
                y = float(data.get('y', 0.0))
                
                # Clamp values
                x = max(-1.0, min(1.0, x))
                y = max(-1.0, min(1.0, y))
                
                self.joystick_controller.update(x, y)
                self.stats['commands_processed'] += 1
                self.stats['last_command_time'] = time.time()
                
                return jsonify({
                    'status': 'executed',
                    'x': x,
                    'y': y,
                    'timestamp': int(time.time() * 1000)
                })
                
            except (ValueError, TypeError) as e:
                return jsonify({'error': f'Invalid coordinates: {e}'}), 400
        
        @self.app.route('/api/motor/state', methods=['GET'])
        def get_motor_state():
            """Obtener estado actual de los motores."""
            try:
                motor_a_state = self.motor_controller.get_motor_a().get_state()
                motor_b_state = self.motor_controller.get_motor_b().get_state()
                
                return jsonify({
                    'motor_a': motor_a_state.to_dict(),
                    'motor_b': motor_b_state.to_dict(),
                    'joystick': self.joystick_controller.joystick_state.to_dict(),
                    'mix': self.joystick_controller.mix_state.to_dict(),
                    'timestamp': int(time.time() * 1000)
                })
            except Exception as e:
                return jsonify({'error': f'Failed to get motor state: {e}'}), 500
        
        # WebSocket para control en tiempo real
        @self.sock.route('/ws/control')
        def handle_realtime_control(ws):
            """WebSocket ultra-optimizado para control en tiempo real."""
            connection_start = time.time()
            command_count = 0
            self.stats['active_connections'] += 1
            
            try:
                while True:
                    # Recibir comando
                    data = ws.receive()
                    if not data:
                        break
                    
                    try:
                        # Parse JSON ultra-rápido
                        if isinstance(data, (bytes, bytearray)):
                            data = data.decode('utf-8')
                        msg = json.loads(data)
                        
                        # Extraer coordenadas
                        x = max(-1.0, min(1.0, float(msg.get("x", 0.0))))
                        y = max(-1.0, min(1.0, float(msg.get("y", 0.0))))
                        
                        # Aplicar control inmediatamente
                        self.joystick_controller.update(x, y)
                        
                        # Actualizar stats
                        command_count += 1
                        self.stats['commands_processed'] += 1
                        self.stats['last_command_time'] = time.time()
                        
                        # Respuesta mínima cada 10 comandos para reducir overhead
                        if command_count % 10 == 0:
                            response = {
                                "cmd": command_count,
                                "timestamp": int(time.time() * 1000)
                            }
                            ws.send(json.dumps(response))
                    
                    except (json.JSONDecodeError, ValueError, TypeError):
                        continue  # Ignorar comandos malformados
                    except Exception:
                        break  # Salir en cualquier otro error
                        
            except Exception:
                pass  # Ignorar errores de conexión
            finally:
                # Cleanup
                self.stats['active_connections'] -= 1
                self.joystick_controller.stop()
                
                connection_duration = time.time() - connection_start
                if os.getenv('T100_DEBUG', 'false').lower() == 'true':
                    print(f"🔌 WebSocket desconectado. Duración: {connection_duration:.1f}s, Comandos: {command_count}")


def create_minimal_api():
    """Factory para crear la API minimalista."""
    api = T100MinimalAPI()
    return api.app


if __name__ == '__main__':
    # Para testing directo
    api = T100MinimalAPI()
    host = os.getenv('T100_HOST', '0.0.0.0')
    port = int(os.getenv('T100_PORT', 5001))  # Puerto diferente por defecto
    
    print(f"🚀 T100 Minimal API iniciando en {host}:{port}")
    api.app.run(host=host, port=port, debug=False, threaded=True)
