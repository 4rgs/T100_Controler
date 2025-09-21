# Cableado ZK-5AD con Raspberry Pi Zero 2W

## Módulo ZK-5AD (TA6586)

El **ZK-5AD** es un controlador dual de motores basado en el chip **TA6586** que simplifica el control de motores DC eliminando la necesidad de pines Enable separados.

### Características principales:
- **Control de 2 motores DC simultáneamente**
- **Control PWM directo en pines IN1/IN2**
- **No requiere pines Enable separados**
- **Alimentación lógica 3.3V compatible con RPi**

## Pinout del ZK-5AD

| Pin ZK-5AD | Función | Descripción |
|-------------|---------|-------------|
| **GND** | Tierra común | GND del sistema |
| **3V3** | Alimentación lógica | 3.3V para la lógica de control |
| **VT** | Alimentación motores | Tensión de alimentación para motores |
| **D0** | Motor A - IN1 | Control PWM Motor A |
| **D1** | Motor A - IN2 | Control PWM Motor A |
| **D2** | Motor B - IN1 | Control PWM Motor B |
| **D3** | Motor B - IN2 | Control PWM Motor B |

## Cableado con Raspberry Pi Zero 2W

### Conexiones de alimentación:
```
ZK-5AD         →  Raspberry Pi Zero 2W
======================================
GND            →  GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
3V3            →  3.3V (Pin 1 o 17)
VT             →  Fuente externa 6-12V (NO conectar a RPi)
```

### Conexiones de control (configuración por defecto):
```
ZK-5AD         →  Raspberry Pi Zero 2W          →  GPIO
========================================================
D0 (Motor A IN1) →  Pin 32 (GPIO 12)          →  GPIO 12
D1 (Motor A IN2) →  Pin 36 (GPIO 16)          →  GPIO 16
D2 (Motor B IN1) →  Pin 38 (GPIO 20)          →  GPIO 20
D3 (Motor B IN2) →  Pin 40 (GPIO 21)          →  GPIO 21
```

### Conexiones de motores:
```
Motor Izquierdo (A)  →  Terminales Motor A del ZK-5AD
Motor Derecho (B)    →  Terminales Motor B del ZK-5AD
```

## Diagrama de pines Raspberry Pi Zero 2W

```
    3V3  (1) (2)  5V
  GPIO2  (3) (4)  5V
  GPIO3  (5) (6)  GND
  GPIO4  (7) (8)  GPIO14
    GND  (9) (10) GPIO15
 GPIO17 (11) (12) GPIO18
 GPIO27 (13) (14) GND
 GPIO22 (15) (16) GPIO23
    3V3 (17) (18) GPIO24
 GPIO10 (19) (20) GND
  GPIO9 (21) (22) GPIO25
 GPIO11 (23) (24) GPIO8
    GND (25) (26) GPIO7
  GPIO0 (27) (28) GPIO1
  GPIO5 (29) (30) GND
  GPIO6 (31) (32) GPIO12  ← D0 (Motor A IN1)
 GPIO13 (33) (34) GND
 GPIO19 (35) (36) GPIO16  ← D1 (Motor A IN2)
 GPIO26 (37) (38) GPIO20  ← D2 (Motor B IN1)
    GND (39) (40) GPIO21  ← D3 (Motor B IN2)
```

## Diferencias con L298N tradicional

| Aspecto | L298N tradicional | ZK-5AD (TA6586) |
|---------|-------------------|-----------------|
| **Pines por motor** | 3 (IN1, IN2, EN) | 2 (IN1, IN2) |
| **Control velocidad** | PWM en pin Enable | PWM directo en IN1/IN2 |
| **Pines totales** | 6 pines | 4 pines |
| **Lógica control** | Digital IN + PWM EN | PWM directo |

## Lógica de control TA6586

### Para avanzar (Forward):
- **IN1 = PWM (0-255)**
- **IN2 = 0**

### Para retroceder (Backward):
- **IN1 = 0** 
- **IN2 = PWM (0-255)**

### Para parar:
- **IN1 = 0**
- **IN2 = 0**

## Fuente de alimentación

### Alimentación lógica (3V3):
- **Fuente**: RPi 3.3V
- **Consumo**: < 50mA
- **Pin RPi**: Pin 1 o 17

### Alimentación motores (VT):
- **Fuente**: Externa 6-12V DC
- **Capacidad**: Según motores (típico 2-3A)
- **IMPORTANTE**: ⚠️ **NO conectar VT a la RPi**

## Configuración en software

La configuración actualizada en `config.py`:

```python
DEFAULT_CONFIG = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(in1=12, in2=16, invert=False, power_factor=1.0),
        motor_b=MotorPins(in1=20, in2=21, invert=False, power_factor=1.0),
        pwm_frequency=4000,
        max_pwm_percent=100.0
    ),
    # ... resto de configuración
}
```

## Ventajas del ZK-5AD

1. **Menos pines GPIO utilizados** (4 vs 6)
2. **Control más directo** (sin intermediario Enable)
3. **Lógica simplificada** en software
4. **Compatible con 3.3V** nativo
5. **Menor latencia** en control

## Troubleshooting

### Motor no se mueve:
1. Verificar conexiones de alimentación VT
2. Comprobar que GND esté conectado
3. Verificar cables de motores

### Control errático:
1. Verificar conexión 3V3 estable
2. Comprobar pines GPIO correctos
3. Verificar ground común

### Un motor funciona, otro no:
1. Intercambiar conexiones para identificar si es hardware o software
2. Verificar configuración `invert` en config.py
3. Comprobar factor de potencia `power_factor`

---

✅ **El driver ha sido actualizado para ZK-5AD (TA6586)**  
🔧 **Configuración lista para usar**  
📡 **Compatible con control remoto WebSocket**