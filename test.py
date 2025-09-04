#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test del sistema T100 Controller
"""

import asyncio
import json
import time
from config import get_config

def test_config():
    """Test de configuración."""
    print("🔧 Testando configuración...")
    config = get_config()
    
    assert "hardware" in config
    assert "server" in config
    
    hw = config["hardware"]
    assert hasattr(hw, "motor_a")
    assert hasattr(hw, "motor_b")
    assert hasattr(hw, "pwm_frequency")
    
    server = config["server"]
    assert hasattr(server, "host")
    assert hasattr(server, "port")
    
    print("✅ Configuración OK")

def test_driver_import():
    """Test de importación del driver (sin hardware)."""
    print("🔌 Testando importación del driver...")
    
    try:
        # Esto fallará si no hay pigpio, pero está bien para test
        from l298n_driver import L298NDriver
        print("✅ Driver importado correctamente")
    except ImportError as e:
        print(f"⚠️  pigpio no disponible (normal en desarrollo): {e}")
    except Exception as e:
        print(f"❌ Error importando driver: {e}")

def test_server_import():
    """Test de importación del servidor."""
    print("🌐 Testando importación del servidor...")
    
    try:
        from server import T100Server
        print("✅ Servidor importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando servidor: {e}")

async def test_websocket_server():
    """Test básico del servidor WebSocket (sin hardware)."""
    print("🚀 Testando servidor WebSocket...")
    
    try:
        from server import T100Server
        
        # Crear servidor pero no inicializar hardware
        server = T100Server()
        print("✅ Servidor creado correctamente")
        
        # No podemos testear completamente sin websockets conectado,
        # pero al menos verificamos que se puede instanciar
        
    except Exception as e:
        print(f"❌ Error en servidor: {e}")

def test_json_messages():
    """Test de serialización de mensajes JSON."""
    print("📨 Testando mensajes JSON...")
    
    # Test de comandos típicos
    commands = [
        {"type": "tank_drive", "forward": 0.5, "turn": 0.2},
        {"type": "motor_control", "left": 0.3, "right": 0.7},
        {"type": "stop"},
        {"type": "ping"},
        {"type": "status"}
    ]
    
    for cmd in commands:
        try:
            json_str = json.dumps(cmd)
            parsed = json.loads(json_str)
            assert parsed == cmd
        except Exception as e:
            print(f"❌ Error en comando {cmd}: {e}")
            return
    
    print("✅ Mensajes JSON OK")

def main():
    """Ejecutar todos los tests."""
    print("🧪 Iniciando tests del T100 Controller\n")
    
    test_config()
    test_driver_import()
    test_server_import()
    test_json_messages()
    
    # Test async
    print("\n🔄 Testando componentes async...")
    try:
        asyncio.run(test_websocket_server())
    except Exception as e:
        print(f"❌ Error en test async: {e}")
    
    print("\n🎉 Tests completados!")
    print("\n📋 Próximos pasos:")
    print("1. Transferir archivos al Raspberry Pi")
    print("2. Ejecutar ./install.sh en el RPi")
    print("3. Abrir client.html en el navegador")
    print("4. Configurar IP del RPi y conectar")

if __name__ == "__main__":
    main()
