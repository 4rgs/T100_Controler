#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de conectividad WebSocket para debugging
"""

import json
import time
import threading
from src.web.flask_app_optimized import create_optimized_app

def test_websocket_connectivity():
    """Test básico de conectividad WebSocket"""
    print("🧪 Test de conectividad WebSocket iniciado...")
    
    app = create_optimized_app()
    
    # Iniciar servidor en thread separado
    def run_server():
        app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Esperar a que el servidor inicie
    time.sleep(2)
    
    print("✅ Servidor iniciado en http://127.0.0.1:5001")
    print("🌐 Ruta WebSocket: ws://127.0.0.1:5001/ws/joystick")
    print("📱 Para probar manualmente, abre: http://127.0.0.1:5001")
    print("")
    print("📋 Debugging activo - verifica los logs para:")
    print("   • 🔌 Nueva conexión WebSocket establecida")
    print("   • 📥 Datos recibidos: {...}")
    print("   • 🎮 Joystick: x=..., y=...")
    print("   • ✅ Comando enviado a motores")
    print("")
    print("Presiona Ctrl+C para detener...")
    
    try:
        # Mantener el test corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Test detenido")

if __name__ == '__main__':
    test_websocket_connectivity()
