#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask App ULTRA-OPTIMIZADA para latencia mínima.
Elimina logs innecesarios y optimiza el procesamiento WebSocket.
"""

import json
import os
from pathlib import Path
from flask import Flask, render_template
from flask_sock import Sock

from ..config.settings import get_ultra_low_latency_config
from ..hardware.l298n_driver_ultra import UltraFastL298NController
from ..control.joystick_controller_ultra import UltraFastJoystickController


class UltraLowLatencyFlaskApp:
    """Aplicación Flask ultra-optimizada para latencia mínima."""
    
    def __init__(self):
        # Rutas absolutas
        current_file = Path(__file__).resolve()
        src_dir = current_file.parent.parent
        templates_dir = src_dir / "templates"
        static_dir = src_dir.parent / "static"
        
        self.app = Flask(__name__, 
                        template_folder=str(templates_dir), 
                        static_folder=str(static_dir))
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
        
        if debug_mode:
            print("⚡ ULTRA LOW LATENCY MODE ACTIVATED")
            print(f"🎮 Deadzone: {config['joystick'].deadzone}")
            print(f"⚙️ PWM Freq: {config['hardware'].pwm_frequency}Hz")
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Configurar rutas ultra-optimizadas."""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_motors():
            self.joystick_controller.stop()
            return {'status': 'stopped'}
        
        @self.app.route('/api/emergency', methods=['POST'])
        def emergency_stop():
            self.joystick_controller.emergency_stop()
            return {'status': 'emergency_stopped'}
        
        # WebSocket ultra-optimizado
        @self.sock.route('/ws/joystick')
        def handle_joystick_ultra(ws):
            """WebSocket ultra-optimizado sin logs ni verificaciones innecesarias."""
            connection_count = 0
            
            while True:
                try:
                    # Recibir datos sin timeout para máxima velocidad
                    data = ws.receive()
                    if not data:
                        break
                    
                    # Parse JSON ultra-rápido
                    try:
                        if isinstance(data, (bytes, bytearray)):
                            data = data.decode('utf-8')
                        msg = json.loads(data)
                    except:
                        continue
                    
                    # Extraer coordenadas y aplicar inmediatamente
                    x = max(-1.0, min(1.0, float(msg.get("x", 0.0))))
                    y = max(-1.0, min(1.0, float(msg.get("y", 0.0))))
                    
                    # Aplicar al controlador ultra-rápido
                    self.joystick_controller.update(x, y)
                    
                    # Respuesta mínima cada 10 mensajes para reducir overhead
                    connection_count += 1
                    if connection_count % 10 == 0:
                        try:
                            response = {
                                "A": self.joystick_controller.motors.get_motor_a().get_state().to_dict(),
                                "B": self.joystick_controller.motors.get_motor_b().get_state().to_dict(),
                                "joy": self.joystick_controller.joystick_state.to_dict(),
                                "mix": self.joystick_controller.mix_state.to_dict()
                            }
                            ws.send(json.dumps(response))
                        except:
                            pass  # Ignore send errors for maximum speed
                    
                except:
                    break  # Exit on any error for maximum reliability


# Alias para compatibilidad
OptimizedFlaskAppProduction = UltraLowLatencyFlaskApp
