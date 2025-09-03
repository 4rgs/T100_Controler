#!/bin/bash

# T100 Controller Gateway - Script unificado
# Maneja instalación, optimización, auto-actualización y ejecución
# Configurado para usuario 4rgs

set -e

# Configuración de variables de entorno
export T100_USER="${T100_USER:-4rgs}"
export T100_HOME="${T100_HOME:-/home/$T100_USER}"
export T100_INSTALL_DIR="${T100_INSTALL_DIR:-/opt/web-motor/T100-Controler}"
export T100_REPO="${T100_REPO:-https://github.com/4rgs/T100_Controler.git}"
export T100_BRANCH="${T100_BRANCH:-develop}"
export T100_SERVICE_NAME="${T100_SERVICE_NAME:-t100-controller-optimized}"
export T100_PORT="${T100_PORT:-5000}"
export T100_HOST="${T100_HOST:-0.0.0.0}"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funciones de logging
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_debug() { echo -e "${BLUE}[DEBUG]${NC} $1"; }

# Verificar si es root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "No ejecutar como root. Usar: sudo cuando sea necesario"
        exit 1
    fi
}

# Verificar si es Raspberry Pi
is_raspberry_pi() {
    grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null || return 1
}

# Instalar dependencias del sistema
install_system_dependencies() {
    log_info "Instalando dependencias del sistema..."
    
    sudo apt-get update -qq
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        pigpio \
        bc \
        curl \
        systemd
    
    # Habilitar pigpio
    sudo systemctl enable pigpiod
    sudo systemctl start pigpiod || true
    
    log_info "Dependencias del sistema instaladas"
}

# Optimizar sistema para rendimiento
optimize_system() {
    log_info "Optimizando sistema para máximo rendimiento..."
    
    # Configurar parámetros del kernel
    if [ ! -f /etc/sysctl.d/99-t100-controller.conf ]; then
        sudo tee /etc/sysctl.d/99-t100-controller.conf > /dev/null << EOF
# T100 Controller - Optimizaciones de rendimiento
vm.swappiness=1
vm.dirty_ratio=15
vm.dirty_background_ratio=5
vm.vfs_cache_pressure=50
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.core.netdev_max_backlog=5000
kernel.pid_max=4096
EOF
        log_info "Configuración del kernel aplicada"
    fi
    
    # Configurar límites de procesos
    if [ ! -f /etc/security/limits.d/t100-controller.conf ]; then
        sudo tee /etc/security/limits.d/t100-controller.conf > /dev/null << EOF
# T100 Controller - Límites de recursos
$T100_USER    soft    nproc       1024
$T100_USER    hard    nproc       2048
$T100_USER    soft    nofile      1024
$T100_USER    hard    nofile      2048
$T100_USER    soft    memlock     64
$T100_USER    hard    memlock     128
EOF
        log_info "Límites de procesos configurados"
    fi
    
    # Optimizaciones específicas de Raspberry Pi
    if is_raspberry_pi; then
        log_info "Aplicando optimizaciones de Raspberry Pi..."
        
        # Reducir memoria GPU
        if ! grep -q "gpu_mem=16" /boot/config.txt 2>/dev/null; then
            echo "gpu_mem=16" | sudo tee -a /boot/config.txt > /dev/null
            log_info "Memoria GPU reducida a 16MB"
        fi
        
        # Deshabilitar servicios innecesarios
        for service in bluetooth wifi-country triggerhappy; do
            sudo systemctl disable $service 2>/dev/null || true
        done
    fi
    
    log_info "Optimización del sistema completada"
}

# Clonar o actualizar repositorio
setup_repository() {
    log_info "Configurando repositorio en $T100_INSTALL_DIR..."
    
    if [ -d "$T100_INSTALL_DIR" ]; then
        log_info "Actualizando repositorio existente..."
        cd "$T100_INSTALL_DIR"
        
        # Verificar si hay cambios locales
        if ! git diff --quiet 2>/dev/null; then
            log_warning "Hay cambios locales. Guardando en stash..."
            git stash push -m "Auto-stash before update $(date)"
        fi
        
        # Actualizar
        git fetch origin
        git checkout $T100_BRANCH
        git pull origin $T100_BRANCH
        
        # Aplicar stash si existe
        if git stash list | grep -q "Auto-stash"; then
            log_info "Aplicando cambios guardados..."
            git stash pop || log_warning "No se pudieron aplicar los cambios guardados"
        fi
    else
        log_info "Clonando repositorio..."
        sudo mkdir -p $(dirname "$T100_INSTALL_DIR")
        sudo git clone -b $T100_BRANCH "$T100_REPO" "$T100_INSTALL_DIR"
        sudo chown -R $T100_USER:$T100_USER "$T100_INSTALL_DIR"
        cd "$T100_INSTALL_DIR"
    fi
    
    log_info "Repositorio configurado correctamente"
}

# Configurar entorno Python
setup_python_environment() {
    log_info "Configurando entorno Python..."
    
    cd "$T100_INSTALL_DIR"
    
    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_info "Entorno virtual creado"
    fi
    
    # Activar entorno
    source venv/bin/activate
    
    # Actualizar pip
    pip install --upgrade pip --quiet
    
    # Instalar dependencias optimizadas
    if [ -f "requirements_optimized.txt" ]; then
        pip install -r requirements_optimized.txt --no-cache-dir --quiet
    elif [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --no-cache-dir --quiet
    fi
    
    log_info "Entorno Python configurado"
}

# Crear servicio systemd
create_systemd_service() {
    log_info "Creando servicio systemd optimizado..."
    
    sudo tee /etc/systemd/system/$T100_SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=T100 Controller Optimized Service
After=network.target pigpiod.service
Wants=network.target
Requires=pigpiod.service

[Service]
Type=simple
User=$T100_USER
Group=$T100_USER
WorkingDirectory=$T100_INSTALL_DIR
Environment=PYTHONPATH=$T100_INSTALL_DIR
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=PYTHONUNBUFFERED=1
Environment=T100_HOST=$T100_HOST
Environment=T100_PORT=$T100_PORT
Environment=T100_DEBUG=false
ExecStartPre=/bin/bash -c 'cd $T100_INSTALL_DIR && source venv/bin/activate'
ExecStart=/bin/bash -c 'cd $T100_INSTALL_DIR && source venv/bin/activate && python motor_control_optimized.py'
ExecReload=/bin/bash $T100_INSTALL_DIR/t100_gateway.sh update
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
ReadWritePaths=$T100_INSTALL_DIR
ReadWritePaths=/dev/gpiomem

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    log_info "Servicio systemd creado: $T100_SERVICE_NAME"
}

# Auto-actualización
auto_update() {
    log_info "Ejecutando auto-actualización..."
    
    cd "$T100_INSTALL_DIR"
    
    # Verificar conexión a internet
    if ! curl -s --connect-timeout 5 https://github.com >/dev/null; then
        log_warning "Sin conexión a internet. Saltando actualización"
        return 0
    fi
    
    # Obtener hash actual
    local current_hash=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    
    # Fetch cambios remotos
    git fetch origin $T100_BRANCH 2>/dev/null || {
        log_warning "No se pudo obtener actualizaciones"
        return 0
    }
    
    # Verificar si hay actualizaciones
    local remote_hash=$(git rev-parse origin/$T100_BRANCH)
    
    if [ "$current_hash" != "$remote_hash" ]; then
        log_info "Nueva versión disponible. Actualizando..."
        
        # Guardar cambios locales si existen
        if ! git diff --quiet; then
            git stash push -m "Auto-update stash $(date)"
        fi
        
        # Actualizar
        git checkout $T100_BRANCH
        git pull origin $T100_BRANCH
        
        # Actualizar dependencias Python
        source venv/bin/activate
        if [ -f "requirements_optimized.txt" ]; then
            pip install -r requirements_optimized.txt --no-cache-dir --quiet
        fi
        
        log_info "Actualización completada. Reiniciando servicio..."
        sudo systemctl restart $T100_SERVICE_NAME
        
        return 1  # Indica que hubo actualización
    else
        log_debug "Sistema actualizado"
        return 0
    fi
}

# Monitorear recursos
monitor_resources() {
    while true; do
        local cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d',' -f1)
        local mem=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
        local temp="N/A"
        
        if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
            local temp_raw=$(cat /sys/class/thermal/thermal_zone0/temp)
            temp=$(echo "scale=1; $temp_raw/1000" | bc 2>/dev/null || echo "N/A")
        fi
        
        echo "$(date '+%H:%M:%S') - CPU: ${cpu}% | RAM: ${mem}% | Temp: ${temp}°C"
        
        # Alerta si los recursos están altos
        if (( $(echo "$cpu > 80" | bc -l 2>/dev/null || echo 0) )) || \
           (( $(echo "$mem > 85" | bc -l 2>/dev/null || echo 0) )); then
            echo "⚠️  ALERTA: Recursos altos!"
        fi
        
        sleep 3
    done
}

# Función principal de instalación
install() {
    log_info "🚀 Iniciando instalación completa de T100 Controller..."
    
    check_root
    install_system_dependencies
    optimize_system
    setup_repository
    setup_python_environment
    create_systemd_service
    
    # Habilitar y iniciar servicio
    sudo systemctl enable $T100_SERVICE_NAME
    sudo systemctl start $T100_SERVICE_NAME
    
    log_info "✅ Instalación completada!"
    log_info "📋 Comandos útiles:"
    log_info "   Estado: sudo systemctl status $T100_SERVICE_NAME"
    log_info "   Logs: journalctl -u $T100_SERVICE_NAME -f"
    log_info "   Reiniciar: sudo systemctl restart $T100_SERVICE_NAME"
    log_info "   Acceso web: http://$(hostname -I | awk '{print $1}'):$T100_PORT"
}

# Función para ejecutar sin servicio
run() {
    log_info "🚀 Iniciando T100 Controller en modo directo..."
    
    cd "$T100_INSTALL_DIR"
    
    # Verificar pigpio
    if ! pgrep pigpiod > /dev/null; then
        log_info "Iniciando pigpiod..."
        sudo pigpiod
        sleep 2
    fi
    
    # Configurar CPU para rendimiento
    if [ -d /sys/devices/system/cpu/cpu0/cpufreq ]; then
        echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1 || true
    fi
    
    # Limpiar cache
    sync && echo 1 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 || true
    
    # Activar entorno y ejecutar
    source venv/bin/activate
    exec python motor_control_optimized.py
}

# Función de actualización
update() {
    log_info "🔄 Actualizando T100 Controller..."
    
    if auto_update; then
        log_info "✅ Sistema actualizado y reiniciado"
    else
        log_info "✅ Sistema ya está actualizado"
    fi
}

# Función de estado
status() {
    log_info "📊 Estado del T100 Controller:"
    
    # Estado del servicio
    if systemctl is-active --quiet $T100_SERVICE_NAME; then
        echo -e "${GREEN}🟢 Servicio: ACTIVO${NC}"
    else
        echo -e "${RED}🔴 Servicio: INACTIVO${NC}"
    fi
    
    # Estado de pigpio
    if pgrep pigpiod > /dev/null; then
        echo -e "${GREEN}🟢 pigpiod: ACTIVO${NC}"
    else
        echo -e "${RED}🔴 pigpiod: INACTIVO${NC}"
    fi
    
    # Recursos del sistema
    if command -v free >/dev/null && command -v bc >/dev/null; then
        local mem=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
        echo "💾 Uso de memoria: ${mem}%"
    fi
    
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        local temp_raw=$(cat /sys/class/thermal/thermal_zone0/temp)
        local temp=$(echo "scale=1; $temp_raw/1000" | bc 2>/dev/null || echo "N/A")
        echo "🌡️  Temperatura: ${temp}°C"
    fi
    
    # URL de acceso
    local ip=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
    echo "🌐 Acceso web: http://${ip}:${T100_PORT}"
}

# Función de verificación completa
verify_system() {
    log_info "🔍 Verificación completa del sistema T100 Controller..."
    
    echo ""
    echo "📊 Estado del servicio:"
    sudo systemctl status $T100_SERVICE_NAME --no-pager -l || true
    
    echo ""
    echo "📋 Últimos 10 logs:"
    journalctl -u $T100_SERVICE_NAME -n 10 --no-pager || true
    
    echo ""
    echo "🌐 Verificando puerto $T100_PORT:"
    if netstat -tlnp 2>/dev/null | grep -q ":$T100_PORT "; then
        log_info "Puerto $T100_PORT está activo"
        local ip=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
        echo "🔗 Acceso web: http://$ip:$T100_PORT"
    else
        log_warning "Puerto $T100_PORT no está activo"
    fi
    
    echo ""
    echo "🔧 Recursos del sistema:"
    if command -v free >/dev/null; then
        free -h | head -2
    fi
    
    if command -v top >/dev/null; then
        top -bn1 | grep "Cpu(s)" | head -1 || true
    fi
    
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        local temp_raw=$(cat /sys/class/thermal/thermal_zone0/temp)
        local temp=$(echo "scale=1; $temp_raw/1000" | bc 2>/dev/null || echo "N/A")
        echo "🌡️  Temperatura: ${temp}°C"
    fi
    
    echo ""
    echo "📁 Verificando archivos de instalación:"
    
    if [ -d "$T100_INSTALL_DIR" ]; then
        echo "✅ Directorio de instalación: $T100_INSTALL_DIR"
        cd "$T100_INSTALL_DIR"
        
        if [ -f "motor_control_optimized.py" ]; then
            echo "✅ motor_control_optimized.py existe"
        else
            echo "❌ motor_control_optimized.py no encontrado"
        fi
        
        if [ -f "t100_gateway.sh" ]; then
            echo "✅ t100_gateway.sh existe"
        else
            echo "❌ t100_gateway.sh no encontrado"
        fi
        
        if [ -d "venv" ]; then
            echo "✅ Entorno virtual existe"
            if [ -f "venv/bin/python" ]; then
                echo "✅ Python virtual disponible"
            fi
        else
            echo "❌ Entorno virtual no encontrado"
        fi
        
        if [ -d "src" ]; then
            echo "✅ Directorio src/ existe"
        else
            echo "❌ Directorio src/ no encontrado"
        fi
        
    else
        echo "❌ Directorio de instalación no encontrado: $T100_INSTALL_DIR"
    fi
    
    echo ""
    echo "🚀 Comandos útiles:"
    echo "   Ver logs en tiempo real: ./t100_gateway.sh logs"
    echo "   Reiniciar servicio: ./t100_gateway.sh restart"
    echo "   Ver estado: ./t100_gateway.sh status"
    echo "   Monitorear recursos: ./t100_gateway.sh monitor"
    echo "   Actualizar desde GitHub: ./t100_gateway.sh update"
}

# Función de ayuda
show_help() {
    echo "T100 Controller Gateway - Script unificado"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  install     Instalación completa del sistema"
    echo "  run         Ejecutar en modo directo (sin servicio)"
    echo "  update      Actualizar desde repositorio"
    echo "  status      Mostrar estado del sistema"
    echo "  verify      Verificación completa del sistema"
    echo "  monitor     Monitorear recursos en tiempo real"
    echo "  restart     Reiniciar servicio"
    echo "  stop        Detener servicio"
    echo "  start       Iniciar servicio"
    echo "  logs        Mostrar logs del servicio"
    echo "  debug-on    Habilitar modo debug"
    echo "  debug-off   Deshabilitar modo debug"
    echo ""
    echo "Variables de entorno:"
    echo "  T100_USER=$T100_USER"
    echo "  T100_INSTALL_DIR=$T100_INSTALL_DIR"
    echo "  T100_BRANCH=$T100_BRANCH"
    echo "  T100_PORT=$T100_PORT"
}

# Función para habilitar modo debug
enable_debug_mode() {
    log_info "🐛 Habilitando modo debug..."
    
    # Actualizar servicio systemd
    sudo sed -i 's/Environment=T100_DEBUG=false/Environment=T100_DEBUG=true/' /etc/systemd/system/$T100_SERVICE_NAME.service
    sudo systemctl daemon-reload
    sudo systemctl restart $T100_SERVICE_NAME
    
    log_info "✅ Modo debug habilitado. Ver logs con: ./t100_gateway.sh logs"
    log_warning "⚠️  El modo debug genera muchos logs. Deshabilitar en producción."
}

# Función para deshabilitar modo debug
disable_debug_mode() {
    log_info "🚀 Deshabilitando modo debug..."
    
    # Actualizar servicio systemd
    sudo sed -i 's/Environment=T100_DEBUG=true/Environment=T100_DEBUG=false/' /etc/systemd/system/$T100_SERVICE_NAME.service
    sudo systemctl daemon-reload
    sudo systemctl restart $T100_SERVICE_NAME
    
    log_info "✅ Modo debug deshabilitado. Logs mínimos activados."
}

# Función principal
main() {
    case "${1:-}" in
        install)
            install
            ;;
        run)
            run
            ;;
        update)
            update
            ;;
        status)
            status
            ;;
        monitor)
            monitor_resources
            ;;
        verify)
            verify_system
            ;;
        restart)
            sudo systemctl restart $T100_SERVICE_NAME
            log_info "Servicio reiniciado"
            ;;
        stop)
            sudo systemctl stop $T100_SERVICE_NAME
            log_info "Servicio detenido"
            ;;
        start)
            sudo systemctl start $T100_SERVICE_NAME
            log_info "Servicio iniciado"
            ;;
        logs)
            journalctl -u $T100_SERVICE_NAME -f
            ;;
        debug-on)
            enable_debug_mode
            ;;
        debug-off)
            disable_debug_mode
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            log_error "Se requiere un comando. Usar: $0 help"
            exit 1
            ;;
        *)
            log_error "Comando desconocido: $1"
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
