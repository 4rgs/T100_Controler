#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración del Master T100 para controlar ESP32 de Motores y Cámara vía Serial.
- Define puertos y baudrates de los dispositivos ESP32
- Define mapeo de canales ELRS para Tank y Cámara
"""
from dataclasses import dataclass
from typing import List


@dataclass
class SerialDeviceConfig:
    name: str
    # Lista de puertos preferidos a probar en orden
    candidate_ports: List[str]
    baud_rate: int
    # Comando de health-check
    status_cmd: str = "status"


@dataclass
class ChannelMapping:
    # Tank drive (palanca derecha normalmente):
    # CH2 = Adelante/Atrás (vertical) | CH1 = Izq/Der (horizontal)
    tank_forward_ch: str = "CH2"
    tank_turn_ch: str = "CH1"
    # Cámara (palanca izquierda):
    cam_pan_ch: str = "CH4"
    cam_tilt_ch: str = "CH3"


@dataclass
class MasterConfig:
    # Dispositivos ESP32
    esp32_motor: SerialDeviceConfig
    esp32_cam: SerialDeviceConfig
    # Mapeo de canales ELRS
    channels: ChannelMapping
    # Frecuencias de envío a cada dispositivo
    tank_rate_hz: int = 100
    cam_rate_hz: int = 20
    # Timeouts y reintentos
    write_timeout_s: float = 0.05
    read_timeout_s: float = 0.1
    command_retries: int = 2


def get_default_master_config() -> MasterConfig:
    return MasterConfig(
        esp32_motor=SerialDeviceConfig(
            name="esp32_motor",
            candidate_ports=[
                "/dev/ttyUSB0",
                "/dev/ttyACM0",
                "/dev/serial/by-id/usb-ESP32*_MOTOR*",
                "/dev/ttyUSB1",
                "/dev/ttyACM1",
            ],
            baud_rate=115200,
            status_cmd="status",
        ),
        esp32_cam=SerialDeviceConfig(
            name="esp32_cam",
            candidate_ports=[
                "/dev/ttyUSB1",
                "/dev/ttyACM1",
                "/dev/serial/by-id/usb-ESP32*_CAM*",
                "/dev/ttyUSB0",
                "/dev/ttyACM0",
            ],
            baud_rate=115200,
            status_cmd="status",
        ),
        channels=ChannelMapping(
            tank_forward_ch="CH2",
            tank_turn_ch="CH1",
            cam_pan_ch="CH4",
            cam_tilt_ch="CH3",
        ),
        tank_rate_hz=100,
        cam_rate_hz=20,
        write_timeout_s=0.05,
        read_timeout_s=0.1,
        command_retries=2,
    )
