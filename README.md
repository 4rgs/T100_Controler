# T100 Controller Project

El proyecto T100 controla un sistema de orugas (tank drive) con cámara, diseñado para operar con Raspberry Pi y/o offloading en ESP32. La arquitectura actual migra hacia un modelo Master/Worker, donde la Raspberry Pi actúa como Master y los microcontroladores (ESP32-S3) como Workers especializados.

## Arquitectura General

- Master (Raspberry Pi Zero 2W)
  - Orquesta la lógica de alto nivel y el enlace serie con dispositivos.
  - Servicios de sistema para ejecución persistente.
  - Entrada RC mediante ELRS/CRSF.
- Workers (ESP32)
  - Firmware dedicado para control de motores (ZK-5AD/TA6586) y servos (MG90S) de cámara.
  - Comunicación por USB Serial con el Master.

La transición a esta arquitectura ayuda a:
- Reducir la carga de CPU en la Raspberry Pi y mejorar la latencia.
- Aislar interferencias y picos de corriente mediante control local en el microcontrolador.
- Aumentar la frecuencia de control efectiva y la robustez del sistema.

## Tecnologías y Herramientas

- Raspberry Pi (Python 3.11+)
  - pigpio (control PWM/GPIO en versiones legacy)
  - asyncio / websockets (versiones previas)
- ESP32-S3 (PlatformIO + Arduino framework)
  - Control PWM para motores TA6586 (ZK-5AD)
  - Librería ESP32Servo para MG90S (Pan/Tilt)
  - Protocolo de comandos por Serial USB
- ELRS / CRSF para control remoto
- Systemd para servicios en el Master

## Estructura del Repositorio

- `master/` — Arquitectura Master para Raspberry Pi
  - Configuración, controlador principal, enlace serie y servicio systemd.
  - Ver detalles y guía de uso aquí: [master/README.md](master/README.md)
- `esp32_servo_cam/` — Firmware ESP32 para control de servos de cámara (Pan/Tilt)
  - Comandos seriales `cam <pan> <tilt>`, `center`, `stop`, etc.
  - Ver guía completa aquí: [esp32_servo_cam/README.md](esp32_servo_cam/README.md)
- `esp32_zk5ad_simple/` — Firmware ESP32 para control de motores ZK-5AD (TA6586)
  - Implementa la lógica de tank drive y protección de picos de corriente.
  - Ver guía completa aquí: [esp32_zk5ad_simple/README.md](esp32_zk5ad_simple/README.md)
- `backup_YYYYMMDD_*` — Copias de seguridad de la arquitectura y scripts legacy.

## Puesta en Marcha Rápida

1. Instala dependencias en Raspberry Pi:
   ```bash
   pip install -r requirements.txt
   ```
2. Configura el Master:
   - Ajusta parámetros en `master/config_master.py` (puertos, canales, límites).
   - Opcional: instala el servicio `master/t100-master.service`.
3. Flashea el/los firmwares ESP32 con PlatformIO:
   - `esp32_servo_cam/`
   - `esp32_zk5ad_simple/`
4. Conecta los ESP32 por USB y verifica el enlace serie.

## Estado Actual y Notas

- Migración a arquitectura Master/Worker en progreso; contenidos legacy preservados en `backup_...`.
- Verifica inversión de PWM y mapeos según el hardware (ver documentación en `backup_...` y `master/`).
- Se recomienda mantener `__pycache__/` y `*.pyc` fuera del control de versiones en futuras limpiezas.

## Licencia

Este proyecto se distribuye bajo la licencia MIT (salvo indicación contraria en submódulos o librerías).
