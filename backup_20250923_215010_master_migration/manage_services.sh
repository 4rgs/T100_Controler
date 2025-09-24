#!/bin/bash

# Script de gestión para T100 con procesos separados
# Maneja instalación, inicio, parada y estado de servicios

set -e

# Configuración
SERVICE_TANK="t100-tank.service"
SERVICE_CAMERA="t100-camera.service" 
SERVICE_DIR="/etc/systemd/system"
SCRIPT_DIR="/home/4rgs/t100"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Este script NO debe ejecutarse como root"
        print_error "Ejecuta: ./manage_services.sh <comando>"
        exit 1
    fi
}

install_services() {
    print_status "Instalando servicios T100..."
    
    # Verificar que los archivos existen
    if [[ ! -f "$SERVICE_TANK" ]]; then
        print_error "No se encuentra $SERVICE_TANK"
        exit 1
    fi
    
    if [[ ! -f "$SERVICE_CAMERA" ]]; then
        print_error "No se encuentra $SERVICE_CAMERA"
        exit 1
    fi
    
    # Copiar archivos de servicio
    print_status "Copiando archivos de servicio..."
    sudo cp "$SERVICE_TANK" "$SERVICE_DIR/"
    sudo cp "$SERVICE_CAMERA" "$SERVICE_DIR/"
    
    # Recargar systemd
    print_status "Recargando systemd..."
    sudo systemctl daemon-reload
    
    # Habilitar servicios
    print_status "Habilitando servicios..."
    sudo systemctl enable "$SERVICE_TANK"
    sudo systemctl enable "$SERVICE_CAMERA"
    
    print_success "Servicios instalados y habilitados"
}

start_services() {
    print_status "Iniciando servicios T100..."
    
    print_status "Iniciando servicio tank..."
    sudo systemctl start "$SERVICE_TANK"
    
    print_status "Iniciando servicio cámara..."
    sudo systemctl start "$SERVICE_CAMERA"
    
    sleep 2
    
    # Verificar estado
    if systemctl is-active --quiet "$SERVICE_TANK"; then
        print_success "Servicio tank iniciado"
    else
        print_error "Error iniciando servicio tank"
    fi
    
    if systemctl is-active --quiet "$SERVICE_CAMERA"; then
        print_success "Servicio cámara iniciado"
    else
        print_error "Error iniciando servicio cámara"
    fi
}

stop_services() {
    print_status "Parando servicios T100..."
    
    print_status "Parando servicio tank..."
    sudo systemctl stop "$SERVICE_TANK" || true
    
    print_status "Parando servicio cámara..."
    sudo systemctl stop "$SERVICE_CAMERA" || true
    
    print_success "Servicios parados"
}

restart_services() {
    print_status "Reiniciando servicios T100..."
    stop_services
    sleep 1
    start_services
}

status_services() {
    print_status "Estado de servicios T100:"
    echo ""
    
    echo "🚗 TANK SERVICE:"
    sudo systemctl --no-pager status "$SERVICE_TANK" || true
    echo ""
    
    echo "📹 CAMERA SERVICE:"
    sudo systemctl --no-pager status "$SERVICE_CAMERA" || true
    echo ""
}

logs_services() {
    local service="${1:-both}"
    
    case $service in
        "tank")
            print_status "Logs del servicio tank (últimas 50 líneas):"
            sudo journalctl -u "$SERVICE_TANK" -n 50 --no-pager
            ;;
        "camera")
            print_status "Logs del servicio cámara (últimas 50 líneas):"
            sudo journalctl -u "$SERVICE_CAMERA" -n 50 --no-pager
            ;;
        "both"|*)
            print_status "Logs de ambos servicios (últimas 25 líneas cada uno):"
            echo ""
            echo "🚗 TANK LOGS:"
            sudo journalctl -u "$SERVICE_TANK" -n 25 --no-pager
            echo ""
            echo "📹 CAMERA LOGS:"
            sudo journalctl -u "$SERVICE_CAMERA" -n 25 --no-pager
            ;;
    esac
}

follow_logs() {
    local service="${1:-both}"
    
    case $service in
        "tank")
            print_status "Siguiendo logs del servicio tank (Ctrl+C para salir):"
            sudo journalctl -u "$SERVICE_TANK" -f
            ;;
        "camera")
            print_status "Siguiendo logs del servicio cámara (Ctrl+C para salir):"
            sudo journalctl -u "$SERVICE_CAMERA" -f
            ;;
        "both"|*)
            print_status "Siguiendo logs de ambos servicios (Ctrl+C para salir):"
            sudo journalctl -u "$SERVICE_TANK" -u "$SERVICE_CAMERA" -f
            ;;
    esac
}

uninstall_services() {
    print_warning "Desinstalando servicios T100..."
    
    # Parar servicios
    stop_services
    
    # Deshabilitar servicios
    print_status "Deshabilitando servicios..."
    sudo systemctl disable "$SERVICE_TANK" || true
    sudo systemctl disable "$SERVICE_CAMERA" || true
    
    # Remover archivos de servicio
    print_status "Removiendo archivos de servicio..."
    sudo rm -f "$SERVICE_DIR/$SERVICE_TANK"
    sudo rm -f "$SERVICE_DIR/$SERVICE_CAMERA"
    
    # Recargar systemd
    print_status "Recargando systemd..."
    sudo systemctl daemon-reload
    
    print_success "Servicios desinstalados"
}

show_help() {
    echo "🎛️  T100 Service Manager"
    echo "======================"
    echo ""
    echo "Uso: $0 <comando> [opción]"
    echo ""
    echo "Comandos disponibles:"
    echo "  install    - Instalar servicios"
    echo "  start      - Iniciar servicios"
    echo "  stop       - Parar servicios"
    echo "  restart    - Reiniciar servicios"
    echo "  status     - Ver estado de servicios"
    echo "  logs       - Ver logs de servicios"
    echo "  follow     - Seguir logs en tiempo real"
    echo "  uninstall  - Desinstalar servicios"
    echo "  help       - Mostrar esta ayuda"
    echo ""
    echo "Para logs y follow, puedes especificar:"
    echo "  $0 logs tank     - Solo logs del tank"
    echo "  $0 logs camera   - Solo logs de la cámara"
    echo "  $0 follow tank   - Seguir solo logs del tank"
    echo ""
    echo "Ejemplos:"
    echo "  $0 install && $0 start"
    echo "  $0 status"
    echo "  $0 logs"
    echo "  $0 follow"
}

# Función principal
main() {
    check_root
    
    case "${1:-help}" in
        "install")
            install_services
            ;;
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            status_services
            ;;
        "logs")
            logs_services "$2"
            ;;
        "follow")
            follow_logs "$2"
            ;;
        "uninstall")
            uninstall_services
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

main "$@"