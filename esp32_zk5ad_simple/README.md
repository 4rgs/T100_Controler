# ESP32-S3 ZK-5AD Simple Driver

Un port simplificado del driver ZK-5AD (TA6586) para ESP32-S3 que recibe comandos por UART/USB para controlar los motores del tank drive.

## 🚀 Características

- **Control TA6586**: Port directo del driver Python ZK-5AD
- **Comandos UART/USB**: Control via comandos de texto simples
- **Tank Drive**: Algoritmo completo de tank drive con steering
- **Protección Anti-Picos**: Delay de 100ms en cambios de dirección
- **Control Individual**: Control independiente de cada motor
- **Debug Integrado**: Salida detallada opcional para cada comando

## 📋 Hardware Requerido

- **ESP32-S3 DevKit C1** - Controlador principal
- **ZK-5AD Motor Driver** - Controlador dual TA6586
- **2x Motores DC** - Motores para tank drive
- **Fuente de Alimentación** - 7.4V-12V para motores

## 🔌 Conexiones

```
ESP32-S3 DevKit C1:
┌─────────────────────────────────────┐
│  ESP32-S3 DevKit C1                 │
│                                     │
│  GPIO 18 ──── Motor A IN1 (PWM)     │  ← Hardware PWM0
│  GPIO 24 ──── Motor A IN2 (Digital) │  ← Separación física
│  GPIO 19 ──── Motor B IN1 (PWM)     │  ← Hardware PWM1  
│  GPIO 25 ──── Motor B IN2 (Digital) │  ← Separación física
│                                     │
│  GPIO 2  ──── Status LED            │  ← LED integrado
│  GND     ──── Tierra Común          │
│  USB     ──── Comunicación Serial   │
└─────────────────────────────────────┘

ZK-5AD (TA6586) Motor Driver:
┌─────────────────────────────────────┐
│  ZK-5AD Motor Driver                │
│                                     │
│  VCC ──── 7.4V-12V Fuente          │
│  GND ──── Tierra Común              │
│                                     │
│  IN1A ──── GPIO 18 (Motor A)        │
│  IN2A ──── GPIO 24 (Motor A)        │
│  OUT1A ─── Motor Izquierdo +        │
│  OUT2A ─── Motor Izquierdo -        │
│                                     │
│  IN1B ──── GPIO 19 (Motor B)        │
│  IN2B ──── GPIO 25 (Motor B)        │
│  OUT1B ─── Motor Derecho +          │
│  OUT2B ─── Motor Derecho -          │
└─────────────────────────────────────┘
```

## 🔧 Instalación

### Requisitos
- [PlatformIO](https://platformio.org/) instalado
- ESP32-S3 DevKit C1
- Cable USB-C para programación

### Pasos

1. **Abrir en PlatformIO**:
   - Abrir PlatformIO IDE
   - File → Open Project
   - Seleccionar la carpeta `esp32_zk5ad_simple`

2. **Compilar y Subir**:
   ```bash
   # Usando PlatformIO CLI
   pio run --target upload --target monitor
   
   # O usar botones de PlatformIO IDE:
   # - Click "Build" (✓)
   # - Click "Upload" (→)
   # - Click "Monitor" (🔌)
   ```

3. **Verificar Instalación**:
   - Abrir Serial Monitor (115200 baud)
   - Deberías ver mensajes de inicio y configuración del sistema
   - LED de estado parpadeará lentamente

## 🎮 Comandos Disponibles

### Tank Drive
```
tank <forward_backward> <left_right>
td <forward_backward> <left_right>
```
- `forward_backward`: -1.0 (atrás) a 1.0 (adelante)
- `left_right`: -1.0 (izquierda) a 1.0 (derecha)

**Ejemplos:**
```
tank 0.5 0.0        # Adelante 50%
tank 0.0 0.3        # Girar derecha en el lugar
tank -0.2 -0.1      # Atrás + ligero giro izquierda
td 0.7 0.2 debug    # Adelante + derecha con debug
```

### Control Individual de Motores
```
motor <a|b> <speed>
m <a|b> <speed>
```
- `a|b`: Motor A (izquierdo) o B (derecho)
- `speed`: -1.0 a 1.0

**Ejemplos:**
```
motor a 0.7         # Motor A adelante 70%
motor b -0.3        # Motor B atrás 30%
m a 0.0             # Motor A parar
```

### Control General
```
stop                # Parar todos los motores
s                   # Forma corta

status              # Mostrar estado de motores
st                  # Forma corta

test                # Ejecutar secuencia de prueba
t                   # Forma corta

help                # Mostrar ayuda
h                   # Forma corta
?                   # Forma corta
```

### Debug
Agregar `debug` o `d` a cualquier comando para salida detallada:
```
tank 0.5 0.0 debug
motor a 0.3 d
```

## 📊 Ejemplos de Uso

### Desde Terminal Serial (115200 baud):
```
🚀 ESP32-S3 ZK-5AD Simple Driver Starting...
===============================================

🔧 Initializing ZK-5AD Driver...
✅ Motor driver initialized successfully

🎯 System Ready - Send commands via Serial
Type 'help' for available commands

> tank 0.5 0.0
OK: Tank drive FB=0.50 LR=0.00

> status
STATUS:
Motor A: forward @ 45.0% (PWM: 115)
Motor B: forward @ 45.0% (PWM: 115)
Uptime: 23s
Free Heap: 394532 bytes
OK

> stop
OK: Motors stopped

> motor a 0.3 debug
▶️  TA6586 Motor A: FORWARD - IN1=69, IN2=0
OK: Motor a speed=0.30
```

## 🔍 Integración con Python

Puedes controlar el ESP32 desde Python:

```python
import serial
import time

# Conectar al ESP32
esp32 = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Esperar inicialización

# Enviar comandos
def send_command(cmd):
    esp32.write((cmd + '\n').encode())
    response = esp32.readline().decode().strip()
    print(f"Comando: {cmd} -> Respuesta: {response}")

# Ejemplos de uso
send_command("tank 0.5 0.0")      # Adelante
send_command("tank 0.0 0.3")      # Girar derecha
send_command("stop")              # Parar
send_command("status")            # Estado

esp32.close()
```

## ⚙️ Configuración

### Modificar Pines (config.h):
```cpp
#define MOTOR_A_IN1_PIN     18  // Hardware PWM0
#define MOTOR_A_IN2_PIN     24  // Digital, esquina opuesta
#define MOTOR_B_IN1_PIN     19  // Hardware PWM1
#define MOTOR_B_IN2_PIN     25  // Digital, esquina opuesta
```

### Ajustar Parámetros:
```cpp
#define PWM_FREQUENCY       2000    // Frecuencia PWM
#define MAX_PWM_PERCENT     90.0f   // Potencia máxima
#define DIRECTION_CHANGE_DELAY_MS   100     // Protección picos
#define DEADBAND_THRESHOLD  0.05f   // Zona muerta
```

## 🛠️ Solución de Problemas

### Motores No Responden
- Verificar alimentación del driver (7.4V-12V)
- Comprobar conexiones GPIO
- Verificar cableado TA6586 (IN1/IN2)

### Comandos No Reconocidos
- Verificar baudrate (115200)
- Usar comandos en minúsculas
- Terminar comandos con Enter

### Comportamiento Errático
- Verificar conexiones sueltas
- Monitorear salida serial para errores
- Comprobar estabilidad de alimentación

## 📈 Rendimiento

- **Frecuencia de Control**: Procesamiento inmediato de comandos
- **Latencia**: <10ms desde comando hasta ejecución
- **Memoria**: ~50KB RAM, ~200KB Flash
- **Protección**: Delay automático de 100ms en cambios de dirección

## 🔄 Diferencias con Versión Python

**Ventajas del ESP32:**
- **Tiempo Real**: Sin overhead del OS
- **Menor Latencia**: Control directo de hardware
- **Simplicidad**: Un solo dispositivo
- **Confiabilidad**: Microcontrolador dedicado

**Compatibilidad:**
- Mismo mapeo de GPIO que versión Python
- Algoritmo de tank drive idéntico
- Misma protección anti-picos de corriente
- Compatible con hardware existente

## 📝 Protocolo de Comandos

Todos los comandos siguen el formato:
```
<comando> [parámetros] [debug]
```

Respuestas:
- `OK: <mensaje>` - Comando ejecutado correctamente
- `ERROR: <mensaje>` - Error en el comando
- `STATUS:` - Información de estado (comando status)

El ESP32 está listo para recibir comandos inmediatamente después del inicio y responde a cada comando con confirmación.
