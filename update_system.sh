#!/bin/bash

# Script de actualización automática para el dispositivo
# Se ejecuta al hacer push al repositorio

set -e

# Configuración
REPO_DIR="/opt/web-control/T100-Controler"
SERVICE_NAME="motor-control-optimized"
BACKUP_DIR="/opt/web-control/backups"
LOG_FILE="/var/log/t100-update.log"

# Función de logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "🚀 Iniciando actualización automática del sistema T100..."

# Crear directorio de backup si no existe
sudo mkdir -p "$BACKUP_DIR"

# Función para hacer backup
backup_current() {
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    log "📦 Creando backup: $backup_name"
    
    sudo cp -r "$REPO_DIR" "$BACKUP_DIR/$backup_name"
    
    # Mantener solo los últimos 5 backups
    cd "$BACKUP_DIR"
    sudo ls -t | tail -n +6 | sudo xargs -r rm -rf
}

# Función para verificar el sistema
verify_system() {
    log "🔍 Verificando sistema antes de actualización..."
    
    # Verificar servicio
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "✅ Servicio $SERVICE_NAME está activo"
        return 0
    else
        log "❌ Servicio $SERVICE_NAME no está activo"
        return 1
    fi
}

# Función para detener servicios
stop_services() {
    log "⏹️  Deteniendo servicios..."
    sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    sleep 2
}

# Función para iniciar servicios
start_services() {
    log "▶️  Iniciando servicios..."
    sudo systemctl start pigpiod 2>/dev/null || true
    sleep 2
    sudo systemctl start "$SERVICE_NAME"
    sleep 3
}

# Función para verificar la actualización
verify_update() {
    log "🧪 Verificando actualización..."
    
    # Verificar que el servicio esté funcionando
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "✅ Servicio iniciado correctamente"
        
        # Verificar puerto 5000
        if netstat -ln | grep -q ":5000"; then
            log "✅ Puerto 5000 está abierto"
            return 0
        else
            log "❌ Puerto 5000 no está disponible"
            return 1
        fi
    else
        log "❌ Servicio no se pudo iniciar"
        return 1
    fi
}

# Función para rollback
rollback() {
    log "🔄 Iniciando rollback..."
    
    # Obtener el backup más reciente
    local latest_backup=$(ls -t "$BACKUP_DIR" | head -n 1)
    
    if [ -n "$latest_backup" ]; then
        log "📦 Restaurando desde backup: $latest_backup"
        
        # Detener servicios
        stop_services
        
        # Restaurar backup
        sudo rm -rf "$REPO_DIR"
        sudo cp -r "$BACKUP_DIR/$latest_backup" "$REPO_DIR"
        
        # Reiniciar servicios
        start_services
        
        if verify_update; then
            log "✅ Rollback completado exitosamente"
            return 0
        else
            log "❌ Rollback falló"
            return 1
        fi
    else
        log "❌ No hay backups disponibles para rollback"
        return 1
    fi
}

# Función principal de actualización
main_update() {
    cd "$REPO_DIR"
    
    # Verificar estado actual
    if ! verify_system; then
        log "❌ Sistema no está en estado válido para actualización"
        exit 1
    fi
    
    # Hacer backup
    backup_current
    
    # Obtener cambios
    log "📥 Obteniendo últimos cambios del repositorio..."
    sudo git fetch origin develop
    
    # Verificar si hay cambios
    if git diff --quiet HEAD origin/develop; then
        log "ℹ️  No hay cambios nuevos, saliendo..."
        exit 0
    fi
    
    # Detener servicios
    stop_services
    
    # Actualizar código
    log "🔄 Actualizando código..."
    sudo git reset --hard origin/develop
    
    # Verificar dependencias
    if [ -f "requirements_optimized.txt" ]; then
        log "📦 Actualizando dependencias..."
        pip3 install -r requirements_optimized.txt --user --no-cache-dir --quiet
    fi
    
    # Ajustar permisos
    sudo chown -R 4rgs:4rgs "$REPO_DIR"
    sudo chmod +x "$REPO_DIR"/*.sh 2>/dev/null || true
    
    # Reiniciar servicios
    start_services
    
    # Verificar actualización
    if verify_update; then
        log "✅ Actualización completada exitosamente"
        
        # Enviar notificación al log del sistema
        logger "T100 Control: Actualización exitosa a commit $(git rev-parse --short HEAD)"
        
        # Mostrar información del sistema
        log "📊 Estado del sistema después de actualización:"
        log "   Commit: $(git rev-parse --short HEAD)"
        log "   RAM: $(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')%"
        
        if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
            local temp=$(cat /sys/class/thermal/thermal_zone0/temp)
            local temp_c=$(echo "scale=1; $temp/1000" | bc 2>/dev/null || echo "N/A")
            log "   Temperatura: ${temp_c}°C"
        fi
        
        return 0
    else
        log "❌ Verificación de actualización falló, iniciando rollback..."
        rollback
        return 1
    fi
}

# Verificar si estamos en el directorio correcto
if [ ! -d "$REPO_DIR" ]; then
    log "❌ Directorio del repositorio no encontrado: $REPO_DIR"
    exit 1
fi

# Verificar si somos root o tenemos permisos sudo
if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
    log "❌ Se requieren permisos de sudo para ejecutar la actualización"
    exit 1
fi

# Ejecutar actualización principal
if main_update; then
    log "🎉 Actualización completada exitosamente"
    exit 0
else
    log "💥 Actualización falló"
    exit 1
fi
