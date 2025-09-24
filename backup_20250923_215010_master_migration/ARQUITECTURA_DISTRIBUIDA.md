# T100 - Arquitectura Distribuida con ESP32 y ATmega32U4

## 🎯 Filosofía: Separación Total por Dispositivos

### Problemas Actuales Resueltos:
- ❌ Interferencia entre PWM de motores y servos
- ❌ Sobrecarga de la Raspberry Pi con múltiples procesos
- ❌ GPIO sharing y conflictos de recursos
- ❌ Latencia por cambios de contexto

### ✅ Solución: Un Dispositivo = Una Función

---

## 🏗️ Distribución de Responsabilidades

### 1. **Raspberry Pi - MAESTRO CENTRAL**
```
🧠 RESPONSABILIDADES:
├── Recepción ELRS (receptor conectado aquí)
├── Procesamiento de comandos de control
├── Distribución de órdenes via comunicación serie
├── Supervisión y monitoreo del sistema
├── Interfaz web/SSH para configuración
└── Logging y diagnósticos
```

### 2. **ESP32 #1 - CONTROLADOR DE MOTORES**
```
🚗 TANK DRIVE CONTROLLER
├── Control exclusivo de motores ZK-5AD
├── PWM dedicado para IN1/IN2 de cada motor
├── Protección contra picos de corriente
├── Failsafe independiente (500ms)
├── Comunicación serie con RPi (115200 baud)
└── GPIO disponibles: 32 pines, PWM dedicado
```

### 3. **ESP32 #2 - CONTROLADOR DE CÁMARA**
```
📹 CAMERA GIMBAL CONTROLLER  
├── Control exclusivo de servos MG90S
├── PWM suave para Pan/Tilt
├── Interpolación de movimientos
├── Failsafe independiente (1000ms)
├── Comunicación serie con RPi (115200 baud)
└── Posible expansión: encoders, IMU para estabilización
```

### 4. **ATmega32U4 - SENSORES Y AUXILIARES**
```
📊 SENSOR HUB & AUXILIARES
├── Lectura de sensores (corriente, voltaje, temperatura)
├── Control de LEDs de estado
├── Buzzer para alertas
├── Expansión I2C para sensores adicionales
├── Comunicación serie con RPi (57600 baud)
└── Backup de comandos críticos (emergency stop)
```

---

## 📡 Protocolo de Comunicación

### Raspberry Pi → ESP32 Motores
```
Formato: "M<L_speed><L_dir><R_speed><R_dir>\n"
Ejemplo: "M100F050R\n"  // Motor izq 100% adelante, der 50% atrás
```

### Raspberry Pi → ESP32 Cámara  
```
Formato: "C<pan_angle><tilt_angle>\n"
Ejemplo: "C090045\n"     // Pan 90°, Tilt 45°
```

### Raspberry Pi → ATmega32U4
```
Formato: "S<sensor_request>\n" o "A<action><params>\n"
Ejemplo: "SALL\n"        // Leer todos los sensores
Ejemplo: "ALED1\n"       // Encender LED 1
```

---

## 🔧 Ventajas de Esta Arquitectura

### ✅ **Aislamiento Completo**
- Cada dispositivo maneja solo su hardware específico
- Zero conflictos de GPIO o recursos compartidos
- Fallos en un subsistema no afectan otros

### ✅ **Especialización**
- ESP32: Ideales para PWM de alta frecuencia y control de motores
- ATmega32U4: Perfecto para sensores y tareas de tiempo real
- RPi: Enfocado en lógica de alto nivel y comunicaciones

### ✅ **Escalabilidad**
- Fácil agregar más ESP32 para funciones adicionales
- Comunicación serie simple y robusta
- Cada dispositivo puede tener su propio firmware optimizado

### ✅ **Debugging Simplificado**
- Cada subsistema se puede probar independientemente
- Logs separados por función
- Reemplazo individual de componentes

---

## 📋 Plan de Implementación

### Fase 1: Diseño de Protocolos
```bash
1. Definir comandos de comunicación serie
2. Crear bibliotecas de comunicación para cada dispositivo
3. Establecer heartbeat y timeouts
```

### Fase 2: Firmware ESP32 Motores
```bash
1. Control PWM optimizado para ZK-5AD
2. Protección de corriente integrada
3. Failsafe independiente
4. Parser de comandos serie
```

### Fase 3: Firmware ESP32 Cámara
```bash
1. Control suave de servos MG90S
2. Interpolación de posiciones
3. Límites de movimiento
4. Comunicación bidireccional
```

### Fase 4: Firmware ATmega32U4
```bash
1. Hub de sensores
2. Sistema de alertas
3. Backup de emergency stop
4. I2C expansion bus
```

### Fase 5: Maestro RPi
```bash
1. Refactorizar código actual
2. Implementar distribución de comandos
3. Monitor de salud de subsistemas
4. Interface web actualizada
```

---

## 🛠️ Herramientas Necesarias

### Para ESP32:
- Arduino IDE o PlatformIO
- ESP32DevKit boards
- Librerías: ESP32Servo, HardwareSerial

### Para ATmega32U4:
- Arduino IDE 
- Arduino Leonardo/Pro Micro
- Librerías estándar de Arduino

### Para RPi:
- Python 3.8+
- pySerial para comunicación
- Tu código actual como base

---

## 🧪 Testing Distribuido

Cada subsistema se puede probar independientemente:

```bash
# Test solo motores (ESP32 #1)
python3 test_distributed_motors.py

# Test solo cámara (ESP32 #2)  
python3 test_distributed_camera.py

# Test sensores (ATmega32U4)
python3 test_distributed_sensors.py

# Test sistema completo
python3 test_distributed_full.py
```

¿Te parece bien esta aproximación? ¿Qué subsistema te gustaría que desarrollemos primero?