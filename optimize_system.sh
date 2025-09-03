#!/bin/bash

# Script de optimización del sistema para Raspberry Pi
# Configura el sistema para máximo rendimiento con mínimos recursos

set -e

echo "🚀 Optimizando sistema para aplicación de control de motores..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si es Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    log_warning "No se detectó Raspberry Pi, algunas optimizaciones pueden no aplicar"
fi

# 1. Optimizar configuración del kernel
log_info "Configurando parámetros del kernel..."

# Crear archivo de configuración del kernel si no existe
if [ ! -f /etc/sysctl.d/99-motor-control.conf ]; then
    sudo tee /etc/sysctl.d/99-motor-control.conf > /dev/null << EOF
# Optimizaciones para aplicación de control de motores

# Memoria
vm.swappiness=1
vm.dirty_ratio=15
vm.dirty_background_ratio=5
vm.vfs_cache_pressure=50

# Red (para WebSockets)
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.core.netdev_max_backlog=5000

# Procesos
kernel.pid_max=4096
EOF
    log_info "Configuración del kernel creada"
else
    log_info "Configuración del kernel ya existe"
fi

# 2. Configurar límites de procesos
log_info "Configurando límites de procesos..."

if [ ! -f /etc/security/limits.d/motor-control.conf ]; then
    sudo tee /etc/security/limits.d/motor-control.conf > /dev/null << EOF
# Límites para aplicación de control de motores
*       soft    nproc       1024
*       hard    nproc       2048
*       soft    nofile      1024
*       hard    nofile      2048
*       soft    memlock     64
*       hard    memlock     128
EOF
    log_info "Límites de procesos configurados"
else
    log_info "Límites de procesos ya configurados"
fi

# 3. Optimizar configuración de GPU (Raspberry Pi)
if command -v raspi-config >/dev/null 2>&1; then
    log_info "Optimizando configuración de GPU..."
    
    # Reducir memoria de GPU al mínimo
    if ! grep -q "gpu_mem=16" /boot/config.txt 2>/dev/null; then
        echo "gpu_mem=16" | sudo tee -a /boot/config.txt > /dev/null
        log_info "Memoria GPU reducida a 16MB"
    fi
    
    # Deshabilitar servicios innecesarios
    sudo systemctl disable bluetooth 2>/dev/null || true
    sudo systemctl disable wifi-country 2>/dev/null || true
    sudo systemctl disable triggerhappy 2>/dev/null || true
fi

# 4. Crear script de monitoreo de recursos
log_info "Creando script de monitoreo..."

cat > /tmp/monitor_resources.sh << 'EOF'
#!/bin/bash

# Monitor de recursos simplificado
while true; do
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEM=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
    TEMP=""
    
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        TEMP_RAW=$(cat /sys/class/thermal/thermal_zone0/temp)
        TEMP=$(echo "scale=1; $TEMP_RAW/1000" | bc)
    fi
    
    echo "$(date '+%H:%M:%S') - CPU: ${CPU}% | RAM: ${MEM}% | Temp: ${TEMP}°C"
    
    # Alerta si los recursos están altos
    if (( $(echo "$CPU > 80" | bc -l) )) || (( $(echo "$MEM > 85" | bc -l) )); then
        echo "⚠️  ALERTA: Recursos altos!"
    fi
    
    sleep 2
done
EOF

chmod +x /tmp/monitor_resources.sh
sudo mv /tmp/monitor_resources.sh /usr/local/bin/monitor_resources.sh
log_info "Script de monitoreo instalado en /usr/local/bin/monitor_resources.sh"

# 5. Crear servicio systemd optimizado
log_info "Creando servicio systemd optimizado..."

sudo tee /etc/systemd/system/motor-control-optimized.service > /dev/null << EOF
[Unit]
Description=Motor Control Optimized Service
After=network.target pigpiod.service
Wants=network.target
Requires=pigpiod.service

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/opt/web-control/T100-Controler
Environment=PYTHONPATH=/opt/web-control/T100-Controler
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/python3 motor_control_optimized.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

# Optimizaciones de recursos
Nice=10
CPUQuota=80%
MemoryLimit=128M
TasksMax=50

# Configuración de seguridad
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/web-control/T100-Controler

[Install]
WantedBy=multi-user.target
EOF

# Crear servicio para pigpiod si no existe
if [ ! -f /etc/systemd/system/pigpiod.service ]; then
    sudo tee /etc/systemd/system/pigpiod.service > /dev/null << EOF
[Unit]
Description=Pigpio daemon
After=network.target

[Service]
Type=forking
User=root
ExecStart=/usr/bin/pigpiod
ExecStop=/bin/systemctl kill pigpiod
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    log_info "Servicio pigpiod creado"
fi

sudo systemctl daemon-reload
log_info "Servicios systemd optimizados creados"

# 6. Instalar dependencias mínimas
log_info "Verificando dependencias..."

# Crear requirements optimizado
cat > requirements_optimized.txt << EOF
# Dependencias mínimas optimizadas
Flask==3.0.3
flask-sock==0.7.0
pigpio==1.79
EOF

if command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements_optimized.txt --no-cache-dir --disable-pip-version-check
    log_info "Dependencias instaladas"
else
    log_warning "pip3 no encontrado, instalar manualmente las dependencias"
fi

# 7. Crear script de inicio rápido
log_info "Creando script de inicio rápido..."

cat > start_optimized.sh << 'EOF'
#!/bin/bash

# Script de inicio optimizado
cd "$(dirname "$0")"

echo "🚀 Iniciando aplicación de control de motores optimizada..."

# Verificar pigpio
if ! pgrep pigpiod > /dev/null; then
    echo "Iniciando pigpiod..."
    sudo pigpiod
    sleep 1
fi

# Configurar CPU governor para rendimiento
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1 || true

# Limpiar memoria
echo 1 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 || true

# Iniciar aplicación
python3 motor_control_optimized.py
EOF

chmod +x start_optimized.sh
log_info "Script de inicio creado: ./start_optimized.sh"

# 8. Resumen
echo ""
log_info "✅ Optimización completada!"
echo ""
echo "📋 Resumen de optimizaciones aplicadas:"
echo "   • Configuración del kernel optimizada"
echo "   • Límites de procesos configurados"
echo "   • Memoria GPU reducida (Raspberry Pi)"
echo "   • Servicios systemd con límites de recursos"
echo "   • Script de monitoreo instalado"
echo "   • Dependencias mínimas instaladas"
echo "   • Monitor de recursos integrado en web"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Iniciar aplicación: ./start_optimized.sh"
echo "   • Monitor recursos: monitor_resources.sh"
echo "   • Ver logs: journalctl -u motor-control-optimized -f"
echo "   • Habilitar servicio: sudo systemctl enable motor-control-optimized"
echo "   • Habilitar pigpiod: sudo systemctl enable pigpiod"
echo "   • Iniciar servicios: sudo systemctl start pigpiod motor-control-optimized"
echo ""
echo "🌐 Acceso web:"
echo "   • URL: http://$(hostname -I | awk '{print $1}'):5000"
echo "   • Monitor integrado en la interfaz web"
echo ""
echo "⚠️  Reinicia el sistema para aplicar todas las optimizaciones del kernel"
