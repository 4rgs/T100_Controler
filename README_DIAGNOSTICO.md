# 🔧 Diagnóstico de Pines L298N

Este documento te guía para resolver problemas de dirección en los motores.

## 🎯 Síntomas Comunes

### ❌ Problema: "No funciona hacia atrás o giro a la derecha"

**Posibles Causas:**
1. **Configuración de inversión incorrecta** (`invert=True/False`)
2. **Cableado físico intercambiado** (IN1/IN2 o IN3/IN4)
3. **Secuencia incorrecta** en cambios de dirección
4. **Problemas de PWM** en pines ENA/ENB

## 🔍 Scripts de Diagnóstico

### 1. Diagnóstico Completo
```bash
python3 diagnostico_pines.py
```
**Qué hace:**
- Prueba cada motor individualmente
- Verifica movimientos combinados
- Te guía paso a paso

### 2. Verificación Detallada de Pines
```bash
python3 verificar_pines.py
```
**Qué hace:**
- Muestra estado exacto de cada pin
- Monitorea señales PWM y digitales
- Verifica secuencias de cambio

## 📋 Tabla de Referencia L298N

| Movimiento | Motor A (Izq) | Motor B (Der) | IN1 | IN2 | IN3 | IN4 |
|------------|---------------|---------------|-----|-----|-----|-----|
| **Adelante** | Forward | Forward | 1 | 0 | 1 | 0 |
| **Atrás** | Backward | Backward | 0 | 1 | 0 | 1 |
| **Giro Derecha** | Forward | Backward | 1 | 0 | 0 | 1 |
| **Giro Izquierda** | Backward | Forward | 0 | 1 | 1 | 0 |
| **Stop** | Coast | Coast | 0 | 0 | 0 | 0 |

## ⚙️ Configuración en `src/config/settings.py`

```python
DEFAULT_CONFIG = {
    "hardware": HardwareConfig(
        motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False),  # ← Cambiar si gira al revés
        motor_b=MotorPins(enable=26, in1=19, in2=21, invert=False),  # ← Cambiar si gira al revés
        pwm_frequency=4000  # ← Frecuencia PWM (1000-20000 Hz)
    ),
    # ...
}
```

## 🔧 Soluciones por Síntoma

### ✅ Motor gira al revés cuando debería ir adelante
**Solución 1 (Recomendada):**
```python
# En settings.py, cambiar invert=True para ese motor
motor_a=MotorPins(enable=12, in1=16, in2=20, invert=True)
```

**Solución 2 (Alternativa):**
- Intercambia físicamente los cables IN1/IN2 (o IN3/IN4)

### ✅ No gira en absoluto
**Verificar:**
1. **Alimentación:** L298N tiene VCC y alimentación de motores
2. **Pines PWM:** ENA/ENB deben estar en pines PWM válidos
3. **pigpiod:** Debe estar ejecutándose
   ```bash
   sudo systemctl status pigpiod
   sudo systemctl start pigpiod
   ```

### ✅ Gira pero se detiene al cambiar dirección
**Problema:** Secuencia incorrecta en cambios de dirección

**Solución:** El código ya implementa la secuencia correcta:
```python
# 1. Parar motor
motor.set_speed(0.0)
# 2. Cambiar dirección  
motor.set_direction(is_forward)
# 3. Aplicar nueva velocidad
motor.set_speed(speed_percent)
```

### ✅ Movimientos diagonales no funcionan
**Verificar:** Lógica de mezcla diferencial
```python
# Para giro a la derecha (x > 0):
left = y - x   # Motor izquierdo
right = y + x  # Motor derecho
```

## 🧪 Proceso de Diagnóstico Paso a Paso

### Paso 1: Verificación Básica
```bash
# Verificar que pigpiod esté funcionando
sudo systemctl status pigpiod

# Si no está activo:
sudo systemctl enable --now pigpiod
```

### Paso 2: Prueba Individual
```bash
# Ejecutar diagnóstico
python3 diagnostico_pines.py
```

**Observar:**
- ¿Gira cada motor cuando se supone?
- ¿La dirección es correcta?
- ¿Se detiene correctamente?

### Paso 3: Ajustar Configuración
Si un motor gira al revés:
```python
# En src/config/settings.py
motor_a=MotorPins(enable=12, in1=16, in2=20, invert=True)  # ← Cambiar aquí
```

### Paso 4: Verificar Cableado
```
Raspberry Pi → L298N
GPIO12 → ENA
GPIO16 → IN1  
GPIO20 → IN2
GPIO26 → ENB
GPIO19 → IN3
GPIO21 → IN4
```

### Paso 5: Prueba de Movimientos
```bash
# Ejecutar aplicación principal
python3 main.py

# Ir a http://IP_RPI:8080
# Probar todos los movimientos en el joystick virtual
```

## 📊 Debug Logs

Con los logs mejorados, verás:
```
[JOY] x=1.00 y=0.00 -> L=-1.00 R=1.00
[MOTOR_A] Dir: back, Speed: 100%
[MOTOR_B] Dir: fwd, Speed: 100%
---
```

**Interpretar:**
- `x=1.00 y=0.00`: Joystick a la derecha
- `L=-1.00 R=1.00`: Motor izq atrás, derecho adelante
- `Dir: back/fwd`: Dirección física del motor
- `Speed: 100%`: Velocidad PWM

## 🚨 Problemas Comunes y Soluciones

| Problema | Síntoma | Solución |
|----------|---------|----------|
| **Motor invertido** | Gira al revés | `invert=True` en settings.py |
| **No gira** | Sin movimiento | Verificar VCC, ENA/ENB, cables |
| **Se traba** | Para al cambiar dirección | Ya corregido en el código |
| **Giro incorrecto** | Derecha va a izquierda | Verificar mezcla diferencial |
| **PWM no funciona** | Velocidad fija | Usar pines PWM válidos (GPIO12, 26) |

## 🎯 Configuraciones de Prueba

### Configuración Estándar (por defecto)
```python
motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False)
motor_b=MotorPins(enable=26, in1=19, in2=21, invert=False)
```

### Si Motor A va al revés
```python
motor_a=MotorPins(enable=12, in1=16, in2=20, invert=True)
motor_b=MotorPins(enable=26, in1=19, in2=21, invert=False)
```

### Si Motor B va al revés
```python
motor_a=MotorPins(enable=12, in1=16, in2=20, invert=False)
motor_b=MotorPins(enable=26, in1=19, in2=21, invert=True)
```

### Si ambos van al revés
```python
motor_a=MotorPins(enable=12, in1=16, in2=20, invert=True)
motor_b=MotorPins(enable=26, in1=19, in2=21, invert=True)
```

## 🏁 Resultado Esperado

Después del diagnóstico y configuración:
- ✅ **Adelante**: Ambos motores hacia adelante
- ✅ **Atrás**: Ambos motores hacia atrás  
- ✅ **Derecha**: Motor izq adelante, motor der atrás
- ✅ **Izquierda**: Motor izq atrás, motor der adelante
- ✅ **Transiciones suaves** entre movimientos
