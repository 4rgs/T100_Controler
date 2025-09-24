#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
T100 Master (ESP32 Coordinator)
- Nueva arquitectura: la RPi Zero 2W lee ELRS y coordina 2 ESP32 por Serial
- Motor ESP32: recibe comandos `tank <forward> <turn>` (-1..1)
- Cámara ESP32: recibe comandos `cam <pan_raw> <tilt_raw>` (172..1811)

Este archivo es ahora un simple entrypoint que delega en `master/master_controller.py`.
"""

import asyncio
from master.master_controller import main as master_main


if __name__ == "__main__":
    asyncio.run(master_main())