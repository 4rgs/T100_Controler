# T100 Controller - Versión Simplificada

Control remoto para vehículo T100 mediante WebSocket API.

## Hardware
- **Raspberry Pi Zero 2W**
- **Driver L298N** para motores DC
- **Motores DC** (2x)

## Arquitectura
- **Servidor**: Python con WebSocket (pigpio + websockets)
- **Cliente**: HTML5 + JavaScript (joystick virtual)
- **Comunicación**: WebSocket en tiempo real

## 📦 Deploy al Raspberry Pi

```bash
./deploy.sh                    # IP por defecto: 192.168.1.140
./deploy.sh 192.168.1.150      # IP personalizada
```

💡 **Tip**: Para evitar repetir contraseña, configura claves SSH:
```bash
ssh-keygen -t rsa
ssh-copy-id 4rgs@192.168.1.140
```

## Instalación en Raspberry Pi

1. **Clonar el repositorio**:
```bash
git clone <repo_url>
cd t100
```

2. **Ejecutar instalación automática**:
```bash
./install.sh
```

3. **Iniciar servicio**:
```bash
sudo systemctl enable t100
sudo systemctl start t100
```

## Configuración de Hardware

Editar `config.py` según tu conexión L298N:

```python
DEFAULT_CONFIG = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False),  # Motor izquierdo
        motor_b=MotorPins(enable=26, in1=21, in2=19, invert=False),  # Motor derecho
        pwm_frequency=1000
    ),
    "server": ServerConfig(
        host="0.0.0.0",
        port=8080,
        debug=False
    )
}
```

### Conexiones L298N → RPi Zero 2W
- **Motor A (Izquierdo)**:
  - ENA → GPIO 12 (PWM)
  - IN1 → GPIO 16
  - IN2 → GPIO 20
  
- **Motor B (Derecho)**:
  - ENB → GPIO 26 (PWM)
  - IN3 → GPIO 21
  - IN4 → GPIO 19

## Uso

### 1. Cliente Web
Abrir `client.html` en el navegador:
- Configurar IP del Raspberry Pi
- Conectar al servidor
- Usar joystick virtual para controlar

### 2. API WebSocket

**Conectar**: `ws://IP_RPI:8080`

**Comandos disponibles**:

```json
// Control tank drive (recomendado)
{
  "type": "tank_drive",
  "forward": 0.5,  // -1.0 a 1.0 (atrás/adelante)
  "turn": 0.3      // -1.0 a 1.0 (izq/der)
}

// Control directo de motores
{
  "type": "motor_control",
  "left": 0.5,     // Motor izquierdo (-1.0 a 1.0)
  "right": 0.7     // Motor derecho (-1.0 a 1.0)
}

// Parar motores
{
  "type": "stop"
}

// Ping (test latencia)
{
  "type": "ping"
}

// Estado del sistema
{
  "type": "status"
}
```

## Archivos del Proyecto

```
t100/
├── config.py          # Configuración de hardware y servidor
├── l298n_driver.py     # Driver para L298N con pigpio
├── server.py           # Servidor WebSocket API
├── client.html         # Cliente web con joystick
├── calibrate_motors.py # Script de calibración de motores
├── requirements.txt    # Dependencias Python
├── install.sh          # Script de instalación automática
└── README.md          # Este archivo
```

## Calibración de Motores

Los motores DC pueden tener velocidades ligeramente diferentes. Para calibrarlos:

### 1. Calibración Automática (Recomendado)

```bash
# En el Raspberry Pi
python3 calibrate_motors.py
```

El script te guiará paso a paso para:
- Probar cada motor individualmente
- Probar movimiento adelante
- Detectar desviaciones
- Sugerir valores de calibración

### 2. Calibración Manual

Editar `config.py` y ajustar los `power_factor`:

```python
DEFAULT_CONFIG = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False, power_factor=1.0),   # Motor izq
        motor_b=MotorPins(enable=26, in1=21, in2=19, invert=False, power_factor=0.85),  # Motor der
        pwm_frequency=1000
    ),
    ...
}
```

### 3. Configuraciones Predefinidas

```python
from config import get_calibrated_config

# Usar configuración predefinida
config = get_calibrated_config("drift_left")  # Si se desvía a la izquierda
config = get_calibrated_config("motor_a_fast") # Si Motor A es más rápido
```

**Configuraciones disponibles**:
- `motor_a_fast`: Motor A más rápido
- `motor_b_fast`: Motor B más rápido  
- `drift_left`: Se desvía a la izquierda
- `drift_right`: Se desvía a la derecha

### 4. Valores Típicos

- **1.0** = Sin calibración (normal)
- **0.9** = Reducir 10% la potencia
- **0.8** = Reducir 20% la potencia
- **0.7** = Reducir 30% la potencia

## Comandos Útiles

```bash
# Ver logs del servidor
sudo journalctl -u t100 -f

# Reiniciar servicio
sudo systemctl restart t100

# Detener servicio
sudo systemctl stop t100

# Ejecutar manualmente (debug)
cd t100
source venv/bin/activate
python3 server.py

# Test del driver (solo motores)
python3 l298n_driver.py
```

## Solución de Problemas

### 1. Error "pigpio no conectado"
```bash
sudo systemctl start pigpiod
sudo systemctl enable pigpiod
```

### 2. Permisos GPIO
```bash
sudo usermod -a -G gpio 4rgs
```

### 3. Motores no responden
- Verificar conexiones L298N
- Comprobar alimentación motores (VCC L298N)
- Revisar `config.py` para pines correctos

### 4. WebSocket no conecta
- Verificar IP del Raspberry Pi
- Comprobar puerto 8080 abierto
- Ver logs: `sudo journalctl -u t100 -f`

## Desarrollo

Para desarrollo local (sin hardware):
```bash
python3 -m venv venv
source venv/bin/activate
pip install websockets
python3 server.py  # Funcionará sin pigpio para desarrollo
```

## Características

- ✅ **Ultra simple**: Solo 4 archivos principales
- ✅ **Tiempo real**: WebSocket de baja latencia
- ✅ **Joystick virtual**: Control intuitivo desde navegador
- ✅ **Tank drive**: Control natural tipo tanque
- ✅ **Autoinstalación**: Script automático para RPi
- ✅ **Servicio systemd**: Inicio automático
- ✅ **Mobile friendly**: Funciona en móviles
