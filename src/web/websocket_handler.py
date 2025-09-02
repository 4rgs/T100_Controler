#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manejador de WebSocket para comunicación en tiempo real.
"""

import json
from typing import Any

from flask_sock import Sock

from ..control.joystick_controller import JoystickController


def create_websocket_handler(sock: Sock, joystick_controller: JoystickController) -> None:
    """Configura el manejador de WebSocket."""
    
    @sock.route('/ws')
    def ws_route(ws):
        """Maneja la conexión WebSocket para control en tiempo real."""
        while True:
            try:
                msg = ws.receive()
                if msg is None:
                    break
                
                # Acepta texto o binario
                if isinstance(msg, (bytes, bytearray)):
                    try:
                        msg = msg.decode('utf-8')
                    except UnicodeDecodeError:
                        continue
                
                # Parse JSON
                try:
                    data = json.loads(msg)
                except json.JSONDecodeError:
                    continue
                
                # Extraer y validar coordenadas
                x = max(-1.0, min(1.0, float(data.get("x", 0.0))))
                y = max(-1.0, min(1.0, float(data.get("y", 0.0))))
                
                # Aplicar al controlador
                joystick_controller.update(x, y)
                
                # Responder con estado actualizado
                response = {
                    "A": joystick_controller.motors.get_motor_a().get_state().to_dict(),
                    "B": joystick_controller.motors.get_motor_b().get_state().to_dict(),
                    "joy": joystick_controller.joystick_state.to_dict(),
                    "mix": joystick_controller.mix_state.to_dict()
                }
                
                ws.send(json.dumps(response))
                
            except Exception:
                # En caso de error, terminar la conexión
                break
