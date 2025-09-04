#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Servidor WebSocket API para control remoto del T100
Hardware: L298N + Raspberry Pi Zero 2W
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Any
from config import get_config
from l298n_driver import L298NDriverOptimized


class T100Server:
    """Servidor WebSocket para control remoto del T100."""
    
    def __init__(self):
        """Inicializa el servidor."""
        self.config = get_config()
        self.server_config = self.config["server"]
        
        # Inicializar driver de motores
        self.motor_driver = None
        
        # Estado del sistema
        self.is_running = False
        self.connected_clients = set()
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def initialize_hardware(self):
        """Inicializa el hardware de manera asíncrona."""
        try:
            self.motor_driver = L298NDriverOptimized()
            self.logger.info("Hardware inicializado correctamente")
            return True
        except Exception as e:
            self.logger.error(f"Error al inicializar hardware: {e}")
            return False
    
    async def handle_client(self, websocket, path):
        """Maneja las conexiones de clientes WebSocket."""
        client_addr = websocket.remote_address
        self.logger.info(f"Cliente conectado desde {client_addr}")
        
        self.connected_clients.add(websocket)
        
        try:
            # Enviar mensaje de bienvenida
            welcome_msg = {
                "type": "welcome",
                "message": "Conectado al T100 Controller",
                "server_info": {
                    "version": "1.0",
                    "hardware": "L298N + RPi Zero 2W"
                }
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # Procesar mensajes del cliente
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_command(websocket, data)
                except json.JSONDecodeError:
                    await self.send_error(websocket, "Formato JSON inválido")
                except Exception as e:
                    await self.send_error(websocket, f"Error procesando comando: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Cliente {client_addr} desconectado")
        except Exception as e:
            self.logger.error(f"Error en conexión con {client_addr}: {e}")
        finally:
            self.connected_clients.discard(websocket)
            # Parar motores cuando se desconecta el cliente
            if self.motor_driver:
                self.motor_driver.stop()
    
    async def process_command(self, websocket, data: Dict[str, Any]):
        """Procesa comandos del cliente."""
        command_type = data.get("type")
        
        if command_type == "motor_control":
            await self.handle_motor_control(websocket, data)
        elif command_type == "tank_drive":
            await self.handle_tank_drive(websocket, data)
        elif command_type == "stop":
            await self.handle_stop(websocket)
        elif command_type == "ping":
            await self.handle_ping(websocket)
        elif command_type == "status":
            await self.handle_status(websocket)
        else:
            await self.send_error(websocket, f"Comando desconocido: {command_type}")
    
    async def handle_motor_control(self, websocket, data: Dict[str, Any]):
        """Maneja control directo de motores."""
        try:
            left_speed = float(data.get("left", 0))
            right_speed = float(data.get("right", 0))
            
            # Normalizar valores de entrada
            left_speed = max(-1.0, min(1.0, left_speed))
            right_speed = max(-1.0, min(1.0, right_speed))
            
            if self.motor_driver:
                self.motor_driver.set_motors(left_speed, right_speed)
                
                response = {
                    "type": "motor_control_ack",
                    "left": left_speed,
                    "right": right_speed
                }
                await websocket.send(json.dumps(response))
            else:
                await self.send_error(websocket, "Hardware no disponible")
                
        except (ValueError, TypeError) as e:
            await self.send_error(websocket, f"Valores de motor inválidos: {e}")
    
    async def handle_tank_drive(self, websocket, data: Dict[str, Any]):
        """Maneja control tipo tanque."""
        try:
            forward = float(data.get("forward", 0))
            turn = float(data.get("turn", 0))
            
            # Normalizar valores de entrada
            forward = max(-1.0, min(1.0, forward))
            turn = max(-1.0, min(1.0, turn))
            
            if self.motor_driver:
                self.motor_driver.tank_drive(forward, turn)
                
                response = {
                    "type": "tank_drive_ack",
                    "forward": forward,
                    "turn": turn
                }
                await websocket.send(json.dumps(response))
            else:
                await self.send_error(websocket, "Hardware no disponible")
                
        except (ValueError, TypeError) as e:
            await self.send_error(websocket, f"Valores de tank drive inválidos: {e}")
    
    async def handle_stop(self, websocket):
        """Maneja comando de parada."""
        if self.motor_driver:
            self.motor_driver.stop()
            
            response = {
                "type": "stop_ack",
                "message": "Motores detenidos"
            }
            await websocket.send(json.dumps(response))
        else:
            await self.send_error(websocket, "Hardware no disponible")
    
    async def handle_ping(self, websocket):
        """Responde a ping del cliente."""
        response = {
            "type": "pong",
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket.send(json.dumps(response))
    
    async def handle_status(self, websocket):
        """Envía estado del sistema."""
        response = {
            "type": "status",
            "hardware_ready": self.motor_driver is not None,
            "connected_clients": len(self.connected_clients),
            "server_running": self.is_running
        }
        await websocket.send(json.dumps(response))
    
    async def send_error(self, websocket, message: str):
        """Envía mensaje de error al cliente."""
        error_msg = {
            "type": "error",
            "message": message
        }
        await websocket.send(json.dumps(error_msg))
    
    async def start_server(self):
        """Inicia el servidor WebSocket."""
        # Inicializar hardware
        hardware_ready = await self.initialize_hardware()
        if not hardware_ready:
            self.logger.warning("Servidor iniciando sin hardware (modo desarrollo)")
        
        host = self.server_config.host
        port = self.server_config.port
        
        self.logger.info(f"Iniciando servidor en {host}:{port}")
        
        # Iniciar servidor WebSocket
        start_server = websockets.serve(
            self.handle_client,
            host,
            port,
            ping_interval=20,
            ping_timeout=10
        )
        
        self.is_running = True
        self.logger.info("Servidor T100 iniciado correctamente")
        
        await start_server
    
    def cleanup(self):
        """Limpia recursos del servidor."""
        if self.motor_driver:
            self.motor_driver.cleanup()
        self.is_running = False
        self.logger.info("Servidor T100 cerrado")


async def main():
    """Función principal del servidor."""
    server = T100Server()
    
    try:
        await server.start_server()
        # Mantener el servidor corriendo
        await asyncio.Future()  # Ejecutar indefinidamente
    except KeyboardInterrupt:
        print("\nServidor interrumpido por usuario")
    except Exception as e:
        print(f"Error en servidor: {e}")
    finally:
        server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
