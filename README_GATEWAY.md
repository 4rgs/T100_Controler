# T100 Controller - Gateway Unificado

## 🚀 Instalación y Uso Simplificado

Este proyecto ahora usa un **único script gateway** que maneja toda la funcionalidad:
- ✅ Instalación completa
- ✅ Optimización del sistema  
- ✅ Auto-actualización
- ✅ Gestión del servicio
- ✅ Monitoreo de recursos

### 📋 Instalación en una línea

```bash
# Clonar e instalar automáticamente
curl -sSL https://raw.githubusercontent.com/4rgs/T100_Controler/develop/t100_gateway.sh | bash -s install
```

### 🔧 Uso del Gateway

```bash
# Comandos principales
./t100_gateway.sh install     # Instalación completa
./t100_gateway.sh run         # Ejecutar en modo directo
./t100_gateway.sh status      # Ver estado del sistema
./t100_gateway.sh update      # Actualizar desde GitHub
./t100_gateway.sh monitor     # Monitorear recursos
./t100_gateway.sh restart     # Reiniciar servicio
./t100_gateway.sh logs        # Ver logs en tiempo real
```

### 🌐 Variables de Entorno

El gateway respeta estas variables de entorno:

```bash
export T100_USER="4rgs"                                    # Usuario del sistema
export T100_INSTALL_DIR="/opt/web-control/T100-Controler" # Directorio de instalación
export T100_BRANCH="develop"                              # Rama de GitHub
export T100_PORT="5000"                                   # Puerto web
export T100_HOST="0.0.0.0"                               # Host de escucha
```

### 📱 Acceso Web

Una vez instalado, accede a la interfaz web:
```
http://[IP_RASPBERRY]:5000
```

### 🔄 Auto-actualización

El sistema incluye auto-actualización automática:
- ✅ Verifica updates cada vez que se inicia
- ✅ Descarga cambios desde GitHub
- ✅ Reinicia el servicio automáticamente
- ✅ Preserva configuraciones locales

### 📊 Monitor de Recursos Integrado

- ✅ CPU, RAM y temperatura en tiempo real
- ✅ Alertas automáticas por uso excesivo
- ✅ Optimización automática del sistema
- ✅ Límites de memoria y CPU configurados

### 🎛️ Servicios del Sistema

El gateway crea automáticamente:
- **Servicio systemd**: `t100-controller-optimized`
- **Límites de recursos**: CPU 80%, RAM 128MB
- **Auto-inicio**: Se inicia con el sistema
- **Auto-restart**: Se reinicia si falla

### 🛠️ Troubleshooting

```bash
# Ver estado completo
./t100_gateway.sh status

# Ver logs en tiempo real
./t100_gateway.sh logs

# Monitorear recursos
./t100_gateway.sh monitor

# Reiniciar si hay problemas
./t100_gateway.sh restart
```

### 📁 Archivos Obsoletos

Con el nuevo gateway, estos archivos ya NO son necesarios:
- ❌ `install_complete.sh`
- ❌ `setup_rpi.sh` 
- ❌ `start_optimized.sh`
- ❌ `optimize_system.sh`
- ❌ `auto_install.sh`
- ❌ `update_*.sh`
- ❌ Múltiples scripts de instalación

### 🎯 Un Solo Comando para Todo

```bash
# Instalación completa en Raspberry Pi
curl -sSL https://raw.githubusercontent.com/4rgs/T100_Controler/develop/t100_gateway.sh | bash -s install

# O manualmente
git clone https://github.com/4rgs/T100_Controler.git
cd T100_Controler
./t100_gateway.sh install
```

¡Eso es todo! 🎉
