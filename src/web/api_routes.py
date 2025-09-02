#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rutas de la API REST para el control de motores.
"""

from flask import Blueprint, jsonify, request

from ..control.joystick_controller import JoystickController


def create_api_routes(joystick_controller: JoystickController) -> Blueprint:
    """Crea las rutas de la API REST."""
    
    api = Blueprint('api', __name__, url_prefix='/api')
    
    @api.route('/health', methods=['GET'])
    def health():
        """Endpoint de salud que retorna el estado actual del sistema."""
        state = joystick_controller.get_state()
        
        # Agregar información adicional de duty cycle
        state["A"]["duty"] = int(state["A"]["speed"] * 2.55)
        state["B"]["duty"] = int(state["B"]["speed"] * 2.55)
        
        return jsonify(state)
    
    @api.route('/stop', methods=['POST'])
    def stop():
        """Detiene todos los motores."""
        joystick_controller.stop()
        return jsonify({"ok": True})
    
    @api.route('/joy', methods=['POST'])
    def joystick_http():
        """Endpoint HTTP para test rápido del backend."""
        try:
            data = request.get_json(force=True) or {}
            x = max(-1.0, min(1.0, float(data.get("x", 0.0))))
            y = max(-1.0, min(1.0, float(data.get("y", 0.0))))
        except (ValueError, TypeError):
            return jsonify({"ok": False, "error": "bad payload"}), 400
        
        joystick_controller.update(x, y)
        
        return jsonify({
            "ok": True,
            "state": joystick_controller.get_state()
        })
    
    return api
