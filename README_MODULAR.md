# Sistema de Control de Motores Modularizado

Este proyecto implementa un sistema web de control de motores L298N usando Raspberry Pi, siguiendo los principios SOLID y DRY para una arquitectura limpia y mantenible.

## Arquitectura

El sistema está dividido en módulos especializados:

```
src/
├── config/          # Configuración centralizada
├── hardware/        # Abstracción del hardware L298N
├── control/         # Lógica de control y mezcla diferencial
├── web/            # Interfaz web y APIs
└── utils.py        # Utilidades compartidas
```

## Principios SOLID Implementados

### Single Responsibility Principle (SRP)
- `L298NMotor`: Solo controla un motor individual
- `JoystickController`: Solo maneja la lógica de joystick
- `L298NController`: Solo gestiona el hardware L298N
- Cada clase tiene una responsabilidad única y bien definida

### Open/Closed Principle (OCP)
- `MotorInterface`: Abstracción que permite nuevos tipos de motores
- `DualMotorInterface`: Protocolo extensible para controladores
- Sistema abierto para extensión (nuevos motores) pero cerrado para modificación

### Liskov Substitution Principle (LSP)
- Cualquier implementación de `MotorInterface` es intercambiable
- `L298NMotor` puede ser sustituido por otros motores sin afectar el código cliente

### Interface Segregation Principle (ISP)
- `MotorInterface`: Interfaz específica para motores individuales
- `DualMotorInterface`: Protocolo específico para controladores de dos motores
- No hay métodos innecesarios en las interfaces

### Dependency Inversion Principle (DIP)
- `JoystickController` depende de `DualMotorInterface`, no de implementaciones concretas
- Inyección de dependencias en el constructor
- Abstracciones no dependen de detalles

## Estructura de Archivos

### Configuración (`src/config/`)
- `settings.py`: Configuración centralizada con dataclasses

### Hardware (`src/hardware/`)
- `motor_interface.py`: Interfaces y abstracciones
- `l298n_driver.py`: Implementación específica para L298N

### Control (`src/control/`)
- `joystick_controller.py`: Lógica de mezcla diferencial y control

### Web (`src/web/`)
- `flask_app.py`: Aplicación Flask principal
- `api_routes.py`: Rutas de la API REST
- `websocket_handler.py`: Manejo de WebSocket en tiempo real

### Frontend
- `templates/index.html`: Interfaz web
- `static/js/joystick.js`: Lógica del joystick virtual

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Asegurar que pigpio esté ejecutándose:
```bash
sudo systemctl enable --now pigpiod
```

3. Ejecutar la aplicación:
```bash
python main.py
```

## Configuración

La configuración se encuentra en `src/config/settings.py`. Puedes modificar:

- Pines de los motores
- Frecuencia PWM
- Zona muerta del joystick
- Puerto del servidor web

## Uso

1. Abre http://localhost:8080 en tu navegador
2. Usa el joystick virtual con mouse/touch o un gamepad físico
3. Los motores responderán en tiempo real a los comandos

## API REST

- `GET /api/health`: Estado del sistema
- `POST /api/stop`: Detener todos los motores
- `POST /api/joy`: Control directo por HTTP

## WebSocket

- Endpoint: `/ws`
- Envía: `{"x": float, "y": float}` (rango -1.0 a 1.0)
- Recibe: Estado actualizado del sistema

## Extensibilidad

Para agregar un nuevo tipo de motor:

1. Implementa `MotorInterface`
2. Crea tu controlador implementando `DualMotorInterface`
3. Úsalo en `main.py` sin modificar otras partes del código

## Ventajas de esta Arquitectura

- **Mantenibilidad**: Código organizado y fácil de entender
- **Testabilidad**: Cada módulo se puede testear independientemente
- **Extensibilidad**: Fácil agregar nuevos tipos de motores o interfaces
- **Reutilización**: Componentes reutilizables en otros proyectos
- **Separación de responsabilidades**: Cada módulo tiene un propósito claro
