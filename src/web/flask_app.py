#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación Flask principal del servidor web.
"""

from flask import Flask, render_template
from flask_sock import Sock

from ..config.settings import ServerConfig
from ..control.joystick_controller import JoystickController
from .api_routes import create_api_routes
from .websocket_handler import create_websocket_handler


def create_app(joystick_controller: JoystickController, config: ServerConfig) -> Flask:
    """Crea y configura la aplicación Flask."""
    
    app = Flask(__name__, 
                template_folder='../../../templates',
                static_folder='../../../static')
    
    # Configurar WebSocket
    sock = Sock(app)
    
    # Configurar rutas
    @app.route('/')
    def index():
        """Página principal del joystick."""
        return render_template('index.html')
    
    # Registrar rutas de API
    api_blueprint = create_api_routes(joystick_controller)
    app.register_blueprint(api_blueprint)
    
    # Configurar WebSocket
    create_websocket_handler(sock, joystick_controller)
    
    return app


def run_server(joystick_controller: JoystickController, config: ServerConfig) -> None:
    """Ejecuta el servidor web."""
    app = create_app(joystick_controller, config)
    
    print(f"🌐 Servidor iniciando en http://{config.host}:{config.port}")
    
    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug,
        threaded=True
    )
