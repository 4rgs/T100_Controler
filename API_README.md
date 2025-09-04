# T100 Controller - API Mode

## 🚀 Optimización Completa del Sistema

Esta versión ha sido completamente optimizada para separar la API del frontend, ofreciendo máximo rendimiento en Raspberry Pi Zero 2W y flexibilidad de desarrollo.

### 📋 Arquitectura Optimizada

```
┌─────────────────────────────────────────┐
│         Raspberry Pi Zero 2W           │
│  ┌─────────────────────────────────┐    │
│  │        T100 API Server          │    │
│  │     (Solo endpoints API)        │    │
│  │                                 │    │
│  │  • Control de motores           │    │
│  │  • Estado del sistema           │    │
│  │  • Configuración                │    │
│  │  • Parada de emergencia         │    │
│  └─────────────────────────────────┘    │
│              Puerto 5000                │
└─────────────────────────────────────────┘
                    │
                    │ HTTP/JSON
                    │
┌─────────────────────────────────────────┐
│       Espacio de Desarrollo             │
│  ┌─────────────────────────────────┐    │
│  │      Cliente Web (HTML/JS)      │    │
│  │                                 │    │
│  │  • Joystick virtual             │    │
│  │  • Monitoreo en tiempo real     │    │
│  │  • Logs de actividad            │    │
│  │  • Control de emergencia        │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## 🔧 Instalación en Raspberry Pi Zero 2W

### Instalación Rápida (Solo API)
```bash
# Descargar e instalar
curl -sSL https://raw.githubusercontent.com/4rgs/T100_Controler/develop/install_api_rpi.sh | bash

# O manualmente:
git clone https://github.com/4rgs/T100_Controler.git
cd T100_Controler
chmod +x install_api_rpi.sh
./install_api_rpi.sh
```

### Instalación Manual
```bash
# Clonar repositorio
git clone https://github.com/4rgs/T100_Controler.git
cd T100_Controler

# Configurar modo API
./t100_gateway.sh install
./t100_gateway.sh api-mode
```

## 🌐 API Endpoints

### Estado del Sistema
```http
GET /api/status
```
Respuesta:
```json
{
  "status": "online",
  "controller": "T100_API", 
  "version": "2.0.0-api",
  "mode": "production"
}
```

### Control de Motores
```http
POST /api/control
Content-Type: application/json

{
  "x": 0.5,
  "y": 0.8,
  "timestamp": 1234567890
}
```

### Estado de Motores
```http
GET /api/motors/status
```

### Parada de Emergencia
```http
POST /api/emergency/stop
```

### Configuración
```http
GET /api/config
```

## 🎮 Cliente de Desarrollo

### Uso del Cliente Web
1. Abrir `dev_client.html` en tu navegador
2. Configurar URL: `http://IP_RASPBERRY:5000`
3. Hacer clic en "Conectar"
4. Usar el joystick virtual para controlar

### Características del Cliente
- **Joystick Virtual**: Control preciso con mouse/touch
- **Monitoreo en Tiempo Real**: Estado de motores y sistema
- **Logs de Actividad**: Seguimiento de comandos y errores
- **Latencia**: Medición de tiempo de respuesta
- **Parada de Emergencia**: Botón de seguridad

## ⚙️ Gestión del Servicio

### Comandos Básicos
```bash
# Cambiar a modo API únicamente
./t100_gateway.sh api-mode

# Cambiar a modo web completo
./t100_gateway.sh web-mode

# Estado del servicio
./t100_gateway.sh status

# Ver logs en tiempo real
./t100_gateway.sh logs

# Reiniciar servicio
./t100_gateway.sh restart

# Habilitar debug
./t100_gateway.sh debug-on
```

### Systemd
```bash
# Estado
sudo systemctl status t100-controller

# Reiniciar
sudo systemctl restart t100-controller

# Logs
journalctl -u t100-controller -f
```

## 🔧 Optimizaciones Específicas

### Raspberry Pi Zero 2W
- **CPU**: Limitado al 60% para evitar throttling
- **RAM**: Máximo 96MB para el proceso
- **Procesos**: Máximo 30 tareas concurrentes
- **GPU**: Reducida a 16MB
- **Servicios**: Bluetooth y WiFi innecesarios deshabilitados

### Performance
- **Sin Frontend**: Solo API, máximo rendimiento
- **Logging Mínimo**: Solo errores críticos
- **Threading Optimizado**: Manejo eficiente de concurrencia
- **JSON Compacto**: Sin formateo pretty para menor latencia

## 📊 Monitoreo

### Recursos del Sistema
```bash
# Monitor en tiempo real
./t100_gateway.sh monitor

# Ver uso actual
htop
free -h
vcgencmd measure_temp
```

### Logs de la Aplicación
```bash
# Logs del servicio
journalctl -u t100-controller -f

# Debug detallado
./t100_gateway.sh debug-on
./t100_gateway.sh logs
```

## 🚨 Solución de Problemas

### Servicio No Inicia
```bash
# Verificar estado
sudo systemctl status t100-controller

# Verificar dependencias
sudo systemctl status pigpiod

# Recrear servicio
./t100_gateway.sh reinstall
```

### Sin Conexión desde Cliente
1. Verificar IP de la Raspberry Pi: `hostname -I`
2. Verificar puerto abierto: `netstat -tlnp | grep :5000`
3. Verificar firewall: `sudo ufw status`
4. Probar con curl: `curl http://IP:5000/api/status`

### Problemas de Hardware
```bash
# Verificar GPIO
ls -la /dev/gpio*

# Verificar pigpio
sudo systemctl status pigpiod

# Test de pines
./verificar_pines.py
```

## 🔄 Actualización

### Actualización Automática
```bash
./t100_gateway.sh update
```

### Actualización Manual
```bash
cd /opt/web-motor/T100-Controler
git pull origin develop
./t100_gateway.sh restart
```

## 📝 Configuración Avanzada

### Variables de Entorno
```bash
# En /etc/systemd/system/t100-controller.service
Environment=T100_HOST=0.0.0.0
Environment=T100_PORT=5000
Environment=T100_DEBUG=false
Environment=T100_MODE=api
```

### Configuración de Motor
Editar `src/config/settings.py` para ajustar:
- `max_speed`: Velocidad máxima
- `acceleration_factor`: Factor de aceleración
- `turn_factor`: Sensibilidad de giro

## 🤝 Desarrollo

### Agregar Nuevos Endpoints
1. Editar `api_main.py`
2. Agregar ruta en la función `create_api_app()`
3. Reiniciar servicio

### Cliente Personalizado
- Usar `dev_client.html` como base
- API compatible con cualquier lenguaje/framework
- Documentación de endpoints disponible en `/api/status`

## 📞 Soporte

Para reportar problemas o sugerir mejoras:
- GitHub Issues: https://github.com/4rgs/T100_Controler/issues
- Logs detallados: `./t100_gateway.sh debug-on && ./t100_gateway.sh logs`
