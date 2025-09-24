# T100 Master (ESP32 Coordinator)

La Raspberry Pi Zero 2W actúa como orquestador: lee el receptor ELRS y envía comandos por Serial a dos ESP32-S3 dedicados:

- ESP32 Motores (ZK-5AD/TA6586): comando `tank <forward> <turn>` con valores normalizados -1..1
- ESP32 Cámara (MG90S): comando `cam <pan_raw> <tilt_raw>` con valores RAW 172..1811 (SBUS/CRSF)

## Estructura

- `master/config_master.py`: Configuración de puertos seriales, baudrates y mapeo de canales
- `master/serial_link.py`: Helper robusto de comunicación serie
- `master/master_controller.py`: Bucle maestro que lee ELRS y envía comandos a los ESP32
- `t100_master.py`: Entry point que ejecuta el master controller
- `master/t100-master.service`: Plantilla de servicio systemd

## Requisitos

- RPi Zero 2W con Python 3
- `pyserial` instalado (ver `requirements.txt`)
- Receptor ELRS conectado al puerto serie (`/dev/ttyAMA0` o `/dev/serial0`)
- Dos ESP32-S3 con los firmwares:
  - Motores: proyecto `esp32_zk5ad_simple` (baud 115200)
  - Cámara: proyecto `esp32_servo_cam` (baud 115200)

## Puertos Seriales

Editar `master/config_master.py` para ajustar `candidate_ports` de cada ESP32. Se intentan en orden y también soporta glob bajo `/dev/serial/by-id/`.

## Ejecutar manualmente

```bash
python3 t100_master.py
```

Verás logs de conexión y estado. Conecta y enciende los ESP32 antes de iniciar el master.

## Instalar como servicio (systemd)

1. Copiar el servicio:

```bash
sudo cp master/t100-master.service /etc/systemd/system/t100-master.service
```

2. Editar rutas si es necesario dentro del archivo (WorkingDirectory y ExecStart).

3. Recargar y habilitar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable t100-master
sudo systemctl start t100-master
sudo systemctl status t100-master -n 100
```

## Notas de Mapeo de Canales

- Tank (palanca derecha): `CH2` = Adelante/Atrás (Y), `CH4` = Izq/Derecha (X)
- Cámara (palanca izquierda): `CH3` = Tilt, `CH4` = Pan

Si tu emisora usa otro mapeo, ajusta `ChannelMapping` en `config_master.py`.

## Troubleshooting

- Si no hay respuesta de un ESP32, revisa el cable USB, permisos de `/dev/tty*` y que el firmware esté cargado y activo.
- El master reintenta conexión automáticamente cuando envía comandos.
- Si no hay datos ELRS > 1s, se ejecuta failsafe: `stop` en motores y `center` en cámara.
