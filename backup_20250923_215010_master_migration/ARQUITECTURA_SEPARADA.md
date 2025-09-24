# T100 - Nueva Arquitectura de Procesos Separados

## 🎯 Solución al Problema de Cruce de Señales

El problema de cruce entre los inputs de servos y motores se resuelve **separando completamente** el control en **dos procesos independientes**:

### 🚗 Proceso Tank Drive (t100_tank_only.py)
- **Frecuencia**: 100Hz (respuesta rápida)
- **Canales**: CH1 (rotación) + CH2 (aceleración)
- **Hardware**: Solo motores ZK-5AD (GPIO 12, 13, 16, 26)
- **Failsafe**: 500ms

### 📹 Proceso Cámara (t100_camera_only.py)
- **Frecuencia**: 30Hz (movimiento suave)
- **Canales**: CH3 (tilt) + CH4 (pan)
- **Hardware**: Solo servos MG90S (GPIO 20, 21)
- **Failsafe**: 1000ms

## 🎛️ Gestión del Sistema

### Controlador Maestro (t100_master.py)
- Lanza y supervisa ambos procesos
- Reinicia automáticamente si fallan
- Monitor de salud en tiempo real

### Servicios Systemd
```bash
# Instalar servicios
./manage_services.sh install

# Iniciar sistema
./manage_services.sh start

# Ver estado
./manage_services.sh status

# Ver logs en tiempo real
./manage_services.sh follow
```

## 🧪 Testing

### Test de Procesos Separados
```bash
python3 test_separated_processes.py
```

### Tests Individuales
```bash
# Solo tank
python3 t100_tank_only.py

# Solo cámara  
python3 t100_camera_only.py

# Controlador maestro
python3 t100_master.py
```

## 🎮 Mapeo Final de Controles

```
STICK DERECHO (Tank Drive):
├── CH1 (Horizontal) → Rotación tank (izq/der)
└── CH2 (Vertical)   → Aceleración tank (adelante/atrás)

STICK IZQUIERDO (Cámara):
├── CH3 (Vertical)   → Tilt cámara (arriba/abajo)
└── CH4 (Horizontal) → Pan cámara (izq/der)
```

## 🔌 Configuración GPIO Final

```
MOTORES (Proceso Tank):
├── Motor A (Izq): GPIO 12 (PWM) + GPIO 16 (Dir)
└── Motor B (Der): GPIO 13 (PWM) + GPIO 26 (Dir)

SERVOS (Proceso Cámara):
├── Servo Pan:  GPIO 21 ← CH4
└── Servo Tilt: GPIO 20 ← CH3
```

## ✅ Ventajas de la Separación

1. **Eliminación total de interferencias**: Cada proceso maneja solo sus GPIO
2. **Frecuencias optimizadas**: Tank 100Hz, Cámara 30Hz
3. **Mejor robustez**: Si falla uno, el otro sigue funcionando
4. **Debugging sencillo**: Logs separados por función
5. **Escalabilidad**: Fácil agregar más funciones

## 🚀 Despliegue y Uso

### Instalación Rápida
```bash
# Transferir archivos
scp t100_*.py manage_services.sh *.service 4rgs@192.168.1.140:t100/

# En el T100
ssh 4rgs@192.168.1.140
cd t100
./manage_services.sh install
./manage_services.sh start
```

### Uso Diario
```bash
# Ver estado
./manage_services.sh status

# Reiniciar si hay problemas
./manage_services.sh restart

# Ver logs
./manage_services.sh logs

# Parar todo
./manage_services.sh stop
```

## 🔧 Troubleshooting

### Verificar Procesos
```bash
ps aux | grep t100
```

### Logs Detallados
```bash
# Logs del tank
sudo journalctl -u t100-tank.service -f

# Logs de la cámara
sudo journalctl -u t100-camera.service -f
```

### Test Manual
```bash
# Probar solo tank
python3 t100_tank_only.py

# Probar solo cámara
python3 t100_camera_only.py
```

Esta arquitectura resuelve completamente el problema de cruce de señales al aislar cada subsistema en su propio proceso independiente.