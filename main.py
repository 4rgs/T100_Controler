#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aplicación principal del sistema de control de motores.

Esta aplicación modularizada sigue los principios SOLID:
- S: Cada clase tiene una responsabilidad única
- O: Abierto para extensión, cerrado para modificación  
- L: Las implementaciones son intercambiables
- I: Interfaces específicas y bien definidas
- D: Dependencia de abstracciones, no de implementaciones concretas
"""

import sys
import os

# Agregar el directorio src al path para imports relativos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import get_config
from src.hardware.l298n_driver import L298NController
from src.control.joystick_controller import JoystickController
from src.web.flask_app import run_server


def main():
    """Función principal que ensambla e inicia el sistema."""
    try:
        # Cargar configuración
        config = get_config()
        
        print("🚀 Iniciando sistema de control de motores modularizado...")
        print(f"📋 Configuración: Motor A en pines {config['hardware'].motor_a.enable}/"
              f"{config['hardware'].motor_a.in1}/{config['hardware'].motor_a.in2}")
        print(f"📋 Configuración: Motor B en pines {config['hardware'].motor_b.enable}/"
              f"{config['hardware'].motor_b.in1}/{config['hardware'].motor_b.in2}")
        
        # Inicializar hardware
        motor_controller = L298NController(
            config['hardware'].motor_a,
            config['hardware'].motor_b,
            config['hardware'].pwm_frequency
        )
        print("✅ Hardware L298N inicializado")
        
        # Inicializar controlador de joystick
        joystick_controller = JoystickController(
            motor_controller,
            config['joystick']
        )
        print("✅ Controlador de joystick inicializado")
        
        # Iniciar servidor web
        print("🌐 Iniciando servidor web...")
        run_server(joystick_controller, config['server'])
        
    except KeyboardInterrupt:
        print("\n👋 Cerrando aplicación...")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
