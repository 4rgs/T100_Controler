#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Archivo principal optimizado para máximo rendimiento.
"""

import os
import sys
import gc
import signal
import resource
from typing import Optional

# Configurar límites de recursos antes de importar otros módulos
def configure_system_limits():
    """Configura límites del sistema para optimizar recursos."""
    try:
        # Limitar memoria virtual
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        if soft == -1 or soft > 256 * 1024 * 1024:  # 256MB
            resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, hard))
        
        # Optimizar garbage collection
        gc.set_threshold(100, 10, 10)  # Más agresivo
        
        # Configurar variables de entorno para Python
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'  # No crear .pyc
        os.environ['PYTHONUNBUFFERED'] = '1'  # Sin buffer
        
    except Exception as e:
        print(f"Warning: No se pudieron configurar límites: {e}")

# Configurar antes de importar
configure_system_limits()

# Verificar si usar modo debug
debug_mode = os.environ.get('T100_DEBUG', 'false').lower() == 'true'

if debug_mode:
    print("🐛 Modo debug activado")
    from src.web.flask_app_optimized import create_optimized_app
else:
    print("🚀 Modo producción activado")
    from src.web.flask_app_production import create_optimized_app


class MotorControlApp:
    """Aplicación principal optimizada."""
    
    def __init__(self):
        self.app = None
        self._running = True
        
        # Configurar manejadores de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Maneja señales del sistema."""
        print(f"\nRecibida señal {signum}, cerrando aplicación...")
        self._running = False
        if self.app:
            # Forzar limpieza
            gc.collect()
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Ejecuta la aplicación optimizada."""
        try:
            print("Iniciando aplicación de control de motores optimizada...")
            
            # Crear aplicación con modo debug
            self.app = create_optimized_app(debug=debug_mode)
            
            # Configuración optimizada de Flask
            self.app.config.update({
                'TESTING': False,
                'DEBUG': debug_mode,
                'SEND_FILE_MAX_AGE_DEFAULT': 31536000,  # Cache estático 1 año
                'MAX_CONTENT_LENGTH': 1024,  # 1KB máximo para requests
            })
            
            print(f"Servidor iniciado en http://{host}:{port}")
            print("Presiona Ctrl+C para detener")
            
            # Ejecutar servidor
            self.app.run(
                host=host,
                port=port,
                debug=debug,
                threaded=True,
                use_reloader=False,  # Sin recarga automática
                processes=1  # Un solo proceso
            )
            
        except KeyboardInterrupt:
            print("\nDeteniendo servidor...")
        except Exception as e:
            print(f"Error ejecutando aplicación: {e}")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Limpia recursos al cerrar."""
        print("Limpiando recursos...")
        gc.collect()
        print("Aplicación cerrada")


def main():
    """Función principal."""
    app = MotorControlApp()
    
    # Usar debug_mode global o argumentos de línea de comandos
    final_debug_mode = debug_mode or '--debug' in sys.argv
    
    try:
        app.run(debug=final_debug_mode)
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
