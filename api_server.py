#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T100 API Server - Punto de entrada para la API minimalista
Solo control de motores, sin interfaz web
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path de Python
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    """Punto de entrada principal de la API T100."""
    try:
        # Importar la API minimalista
        from src.api.t100_api import T100MinimalAPI
        
        # Crear la API
        api_instance = T100MinimalAPI()
        
        # Configurar host y puerto desde variables de entorno
        host = os.getenv('T100_HOST', '0.0.0.0')
        port = int(os.getenv('T100_PORT', 5001))  # Puerto diferente para la API
        debug_mode = os.getenv('T100_DEBUG', 'false').lower() == 'true'
        
        print(f"🚀 T100 Minimal API iniciando en {host}:{port}")
        if debug_mode:
            print("🔧 Modo DEBUG activado")
        else:
            print("⚡ Modo PRODUCCIÓN activado")
        
        print("📚 Endpoints disponibles:")
        print(f"  GET  http://{host}:{port}/api/status")
        print(f"  POST http://{host}:{port}/api/control/stop")
        print(f"  POST http://{host}:{port}/api/control/emergency")
        print(f"  POST http://{host}:{port}/api/control/move")
        print(f"  GET  http://{host}:{port}/api/motor/state")
        print(f"  WS   ws://{host}:{port}/ws/control")
        
        # Ejecutar la API
        api_instance.app.run(
            host=host,
            port=port,
            debug=False,  # Siempre False para máxima performance
            threaded=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 T100 API detenida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error iniciando T100 API: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
