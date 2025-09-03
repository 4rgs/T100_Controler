# Configuración de Controles - T100 Controller

## Diferencias entre Joystick Virtual y Gamepad Físico

### 🖱️ **Joystick Virtual (Mouse/Touch)**
- **Comportamiento estándar**: Arriba = avanzar, Abajo = retroceder
- **Eje Y**: NO invertido (↑ positivo = adelante)
- **Zona muerta**: 0.03 (3%)
- **Uso**: Mouse o pantalla táctil en el navegador

### 🎮 **Gamepad Físico (Control conectado)**
- **Comportamiento tipo drone**: Stick hacia arriba = avanzar (como controles de drones/aviones)
- **Eje Y**: Invertido tipo drone (stick ↑ físico = valor negativo = adelante)
- **Zona muerta**: 0.06 (6%) - más amplia para evitar drift
- **Botón B/○**: Detiene todos los motores
- **Uso**: Cualquier gamepad compatible con HTML5 Gamepad API

## 🔧 Configuración Técnica

### JavaScript (joystick.js)
```javascript
// Joystick virtual (canvas)
stick.y = +(-dy/R).toFixed(3);  // ↑ positivo (normal)

// Gamepad físico  
let y = (gp.axes[1] || 0);      // Mantener valor crudo (tipo drone)
```

### Backend (settings.py)
```python
"joystick": JoystickConfig(
    deadzone=0.03,              # Zona muerta pequeña
    non_linear_factor=1.0       # Respuesta lineal
),
"gamepad": GamepadConfig(
    deadzone=0.06,              # Zona muerta más amplia
    invert_y_axis=True,         # Comportamiento tipo drone
    non_linear_factor=1.0       # Respuesta lineal
)
```

## 🎯 Comportamiento Esperado

### Movimientos del Robot
- **Adelante**: Joystick virtual ↑ / Gamepad stick ↑
- **Atrás**: Joystick virtual ↓ / Gamepad stick ↓  
- **Derecha**: Joystick virtual → / Gamepad stick →
- **Izquierda**: Joystick virtual ← / Gamepad stick ←

### Diferencia Clave
- **Joystick virtual**: Intuitivo para pantalla táctil
- **Gamepad físico**: Como control de drone/avión para mayor precisión

## 🛠️ Personalización

Para cambiar el comportamiento del gamepad, edita `src/config/settings.py`:

```python
"gamepad": GamepadConfig(
    deadzone=0.06,
    invert_y_axis=False,        # Cambiar a False para comportamiento normal
    non_linear_factor=1.0
)
```

> **Nota**: Los cambios requieren reiniciar el servidor para aplicarse.
