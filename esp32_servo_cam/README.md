# ESP32-S3 Servo Camera Controller (Pan/Tilt)

Firmware para ESP32-S3 DevKit C1 para controlar 2 servos MG90S (Pan/Tilt) por puerto serial USB.
Replica la lógica de `t100_camera_only.py` y el mapeo de `mg90s_servo_driver.py`:
- Rango ELRS raw 172..1811 → 0..180° (con opción de inversión por eje)
- Pulsos MG90S ~500–2400 µs a 50 Hz
- Comandos por Serial con protocolo simple (similar a `esp32_zk5ad_simple`)

## Hardware
- Board: ESP32-S3 DevKit C1
- Servos MG90S
- Pines (ajustables en `include/ServoDriver.h`):
  - Pan → GPIO4
  - Tilt → GPIO17
- Frecuencia: 50 Hz

## Estructura
```
esp32_servo_cam/
  platformio.ini
  include/
    ServoDriver.h
    CommandParser.h
  src/
    ServoDriver.cpp
    CommandParser.cpp
    main.cpp
```

## Build & Upload (PlatformIO)
1. Conectar la ESP32-S3 por USB.
2. Desde el directorio del proyecto:
   - Compilar: `pio run`
   - Subir: `pio run -t upload`
   - Monitor: `pio device monitor -b 115200`

> Nota: `platformio.ini` habilita USB CDC al boot (`-DARDUINO_USB_CDC_ON_BOOT=1`).

## Comandos por Serial
- `help`
- `status`
- `center` (centra ambos servos a 90°)
- `stop` (alias de `center`)
- `cam <pan> <tilt>`
  - Soporta valores ELRS raw `172..1811`
  - O valores normalizados `-1..1` (se convierten a raw internamente)
  - Agregar `debug` o `d` al final para mostrar pulsos µs

### Ejemplos
- `cam 992 992` → centro en ambos
- `cam 172 172` → esquina inferior izquierda (0°)
- `cam 1811 1811` → esquina superior derecha (180°)
- `cam 0.0 0.0` → valores normalizados (centro)
- `cam -1 1` → pan al mínimo, tilt al máximo
- `center`
- `status`

## Ajustes
Editar `include/ServoDriver.h`:
- Límites de pulso: `SERVO_MIN_US`, `SERVO_CENTER_US`, `SERVO_MAX_US`
- Inversión: `PAN_INVERT`, `TILT_INVERT`
- Pines: `SERVO_PAN_PIN`, `SERVO_TILT_PIN`

## Notas de compatibilidad
- Usa `ESP32Servo` (`madhephaestus/ESP32Servo`).
- Si hay jitter, probar ajustar `SERVO_MIN_US`/`MAX_US` y verificar la fuente de alimentación de los servos.
- Para evitar ruido/interferencias, separar GND y alimentar servos con fuente estable (no del USB del ESP32 si consumen mucho).
