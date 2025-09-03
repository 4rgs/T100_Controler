#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T100 Controller - Punto de entrada principal unificado
Utiliza la versión de producción optimizada con control de debug dinámico.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path de Python
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    """Punto de entrada principal del T100 Controller."""
    try:
        # Importar la aplicación de producción
        from src.web.flask_app import OptimizedFlaskAppProduction
        
        # Crear la aplicación
        app_instance = OptimizedFlaskAppProduction()
        
        # Configurar host y puerto desde variables de entorno
        host = os.getenv('T100_HOST', '0.0.0.0')
        port = int(os.getenv('T100_PORT', 5000))
        debug_mode = os.getenv('T100_DEBUG', 'false').lower() == 'true'
        
        print(f"🚀 T100 Controller iniciando en {host}:{port}")
        if debug_mode:
            print("� Modo DEBUG activado")
        else:
            print("🏭 Modo PRODUCCIÓN activado")
        
        # Ejecutar la aplicación
        app_instance.app.run(
            host=host,
            port=port,
            debug=False,  # Siempre False para evitar auto-reload en producción
            threaded=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 T100 Controller detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
