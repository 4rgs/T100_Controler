#!/bin/bash

# Script de inicio rápido optimizado
cd "$(dirname "$0")"

echo "🚀 Iniciando aplicación de control de motores optimizada..."

# Función para logging
log_info() {
    echo "$(date '+%H:%M:%S') [INFO] $1"
}

log_error() {
    echo "$(date '+%H:%M:%S') [ERROR] $1"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "motor_control_optimized.py" ]; then
    log_error "No se encuentra motor_control_optimized.py en el directorio actual"
    exit 1
fi

# Verificar pigpio
if ! pgrep pigpiod > /dev/null; then
    log_info "Iniciando pigpiod..."
    sudo pigpiod
    sleep 2
    
    if ! pgrep pigpiod > /dev/null; then
        log_error "No se pudo iniciar pigpiod"
        exit 1
    fi
fi

# Configurar CPU governor para rendimiento (si está disponible)
if [ -d /sys/devices/system/cpu/cpu0/cpufreq ]; then
    log_info "Configurando CPU para máximo rendimiento..."
    echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1 || true
fi

# Limpiar cache del sistema
log_info "Liberando memoria cache..."
sync
echo 1 | sudo tee /proc/sys/vm/drop_caches > /dev/null 2>&1 || true

# Configurar prioridad del proceso
log_info "Configurando prioridad del proceso..."
ulimit -v 262144  # Limitar memoria virtual a 256MB
ulimit -u 64      # Limitar procesos

# Verificar Python y dependencias
if ! python3 -c "import flask, flask_sock, pigpio" 2>/dev/null; then
    log_error "Faltan dependencias. Ejecuta: pip3 install -r requirements_optimized.txt"
    exit 1
fi

# Mostrar estado del sistema antes de iniciar
if command -v free >/dev/null 2>&1; then
    MEM_FREE=$(free -m | awk 'NR==2{printf "%.1f", $7*100/$2}')
    log_info "Memoria libre: ${MEM_FREE}%"
fi

if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
    TEMP_C=$(echo "scale=1; $TEMP/1000" | bc 2>/dev/null || echo "N/A")
    log_info "Temperatura: ${TEMP_C}°C"
fi

# Iniciar aplicación optimizada
log_info "Iniciando aplicación..."
exec nice -n 10 python3 motor_control_optimized.py
