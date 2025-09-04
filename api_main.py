#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T100 API Controller - Solo API sin frontend web
Versión optimizada específicamente para Raspberry Pi Zero 2W
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask
from flask_cors import CORS

# Agregar el directorio src al path de Python
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def setup_logging(debug_mode=False):
    """Configurar logging optimizado para RPI"""
    log_level = logging.DEBUG if debug_mode else logging.WARNING
    
    # Configuración minimalista de logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ] if debug_mode else [logging.NullHandler()]
    )
    
    # Silenciar logs innecesarios en producción
    if not debug_mode:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        logging.getLogger('urllib3').setLevel(logging.ERROR)

def create_api_app():
    """Crear aplicación Flask minimalista solo para API"""
    from src.hardware.l298n_driver_ultra import UltraOptimizedL298NDriver
    from src.control.joystick_controller_ultra import UltraOptimizedJoystickController
    from src.config.settings import MotorConfig, JoystickConfig
    
    # Crear Flask app minimalista
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    
    # CORS habilitado para desarrollo
    CORS(app, origins="*")
    
    # Inicializar hardware
    motor_config = MotorConfig()
    joystick_config = JoystickConfig()
    motor_driver = UltraOptimizedL298NDriver(motor_config)
    controller = UltraOptimizedJoystickController(motor_driver, joystick_config)
    
    @app.route('/api/status', methods=['GET'])
    def get_status():
        """Estado del sistema"""
        return {
            'status': 'online',
            'controller': 'T100_API',
            'version': '2.0.0-api',
            'mode': 'production' if not app.debug else 'debug'
        }
    
    @app.route('/api/motors/status', methods=['GET'])
    def get_motor_status():
        """Estado de los motores"""
        return motor_driver.get_status()
    
    @app.route('/api/control', methods=['POST'])
    def control_motors():
        """Control directo de motores via joystick data"""
        from flask import request
        
        try:
            data = request.get_json(force=True)
            x = float(data.get('x', 0))
            y = float(data.get('y', 0))
            
            # Procesar input del joystick
            controller.process_joystick_input(x, y)
            
            return {
                'success': True,
                'x': x,
                'y': y,
                'timestamp': data.get('timestamp', 0)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}, 400
    
    @app.route('/api/emergency/stop', methods=['POST'])
    def emergency_stop():
        """Parada de emergencia"""
        try:
            motor_driver.emergency_stop()
            return {'success': True, 'message': 'Emergency stop executed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Obtener configuración actual"""
        return {
            'motor_config': {
                'max_speed': motor_config.max_speed,
                'acceleration_factor': motor_config.acceleration_factor
            },
            'joystick_config': {
                'deadzone': joystick_config.deadzone,
                'sensitivity': joystick_config.sensitivity,
                'turn_factor': joystick_config.turn_factor
            }
        }
    
    # Cleanup al cerrar
    @app.teardown_appcontext
    def cleanup(exception):
        if exception:
            motor_driver.emergency_stop()
    
    return app, motor_driver

def main():
    """Punto de entrada principal de la API T100"""
    try:
        # Configurar entorno
        debug_mode = os.getenv('T100_DEBUG', 'false').lower() == 'true'
        host = os.getenv('T100_HOST', '0.0.0.0')
        port = int(os.getenv('T100_PORT', 5000))
        
        # Configurar logging
        setup_logging(debug_mode)
        
        # Crear aplicación
        app, motor_driver = create_api_app()
        
        print(f"🔌 T100 API Controller iniciando en {host}:{port}")
        print(f"📡 Modo: {'DEBUG' if debug_mode else 'PRODUCCIÓN'}")
        print("🎮 API Endpoints disponibles:")
        print("   GET  /api/status")
        print("   GET  /api/motors/status")
        print("   POST /api/control")
        print("   POST /api/emergency/stop")
        print("   GET  /api/config")
        
        try:
            # Ejecutar servidor Flask
            app.run(
                host=host,
                port=port,
                debug=False,  # Siempre False en producción
                threaded=True,
                use_reloader=False
            )
        finally:
            # Cleanup al finalizar
            motor_driver.cleanup()
            print("🔌 Hardware limpiado correctamente")
        
    except KeyboardInterrupt:
        print("\n👋 T100 API Controller detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error crítico en API: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
