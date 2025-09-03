#!/bin/bash

# Script de actualización automática para T100 Controller
# Actualiza el código desde GitHub y reinicia el servicio

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración
INSTALL_DIR="/opt/web-motor"
PROJECT_DIR="$INSTALL_DIR/T100_Controler"
SERVICE_NAME="web-motor.service"
BRANCH="develop"

echo -e "${BLUE}🔄 Iniciando actualización de T100 Controller...${NC}"
echo "===========================================" 

# Función para mostrar errores
error_exit() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
    exit 1
}

# Verificar que estamos ejecutando como root o con sudo
if [[ $EUID -ne 0 ]]; then
   error_exit "Este script debe ejecutarse como root (usar sudo)"
fi

# Verificar que el directorio del proyecto existe
if [ ! -d "$PROJECT_DIR" ]; then
    error_exit "Directorio del proyecto no encontrado: $PROJECT_DIR"
fi

echo -e "${YELLOW}📁 Cambiando al directorio del proyecto...${NC}"
cd "$PROJECT_DIR" || error_exit "No se puede acceder a $PROJECT_DIR"

# Verificar que es un repositorio git
if [ ! -d ".git" ]; then
    error_exit "No es un repositorio git válido: $PROJECT_DIR"
fi

echo -e "${YELLOW}📡 Obteniendo últimos cambios de GitHub...${NC}"
git fetch origin || error_exit "Error al hacer fetch del repositorio"

# Verificar si hay cambios disponibles
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/$BRANCH)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "${GREEN}✅ El código ya está actualizado${NC}"
else
    echo -e "${YELLOW}📥 Hay actualizaciones disponibles, aplicando...${NC}"
    
    # Hacer stash de cambios locales si existen
    if ! git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}💾 Guardando cambios locales...${NC}"
        git stash push -m "Auto-stash before update $(date)"
    fi
    
    # Hacer pull de develop
    git pull origin $BRANCH || error_exit "Error al hacer pull de la rama $BRANCH"
    
    echo -e "${GREEN}✅ Código actualizado exitosamente${NC}"
fi

# Mostrar información del commit actual
echo -e "${BLUE}📋 Información de la versión actual:${NC}"
echo "Commit: $(git rev-parse --short HEAD)"
echo "Fecha: $(git show -s --format=%ci HEAD)"
echo "Mensaje: $(git show -s --format=%s HEAD)"
echo

# Volver al directorio base
echo -e "${YELLOW}📁 Volviendo a $INSTALL_DIR...${NC}"
cd "$INSTALL_DIR" || error_exit "No se puede acceder a $INSTALL_DIR"

# Recargar systemd daemon
echo -e "${YELLOW}🔄 Recargando systemd daemon...${NC}"
systemctl daemon-reload || error_exit "Error al recargar systemd daemon"

# Verificar el estado del servicio antes del reinicio
echo -e "${YELLOW}🔍 Verificando estado del servicio...${NC}"
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${BLUE}ℹ️  Servicio $SERVICE_NAME está ejecutándose, reiniciando...${NC}"
    systemctl restart $SERVICE_NAME || error_exit "Error al reiniciar el servicio $SERVICE_NAME"
else
    echo -e "${BLUE}ℹ️  Servicio $SERVICE_NAME no está ejecutándose, iniciando...${NC}"
    systemctl start $SERVICE_NAME || error_exit "Error al iniciar el servicio $SERVICE_NAME"
fi

# Esperar un momento para que el servicio se inicie
sleep 3

# Verificar que el servicio se inició correctamente
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✅ Servicio $SERVICE_NAME iniciado correctamente${NC}"
    
    # Mostrar estado del servicio
    echo -e "${BLUE}📊 Estado del servicio:${NC}"
    systemctl status $SERVICE_NAME --no-pager -l
    
    echo
    echo -e "${GREEN}🎉 ¡Actualización completada exitosamente!${NC}"
    echo -e "${GREEN}🌐 El T100 Controller está ejecutándose con la última versión${NC}"
else
    error_exit "El servicio $SERVICE_NAME no pudo iniciarse correctamente"
fi

echo
echo -e "${BLUE}📝 Para ver los logs del servicio:${NC}"
echo "   journalctl -u $SERVICE_NAME -f"
echo
echo -e "${BLUE}📝 Para detener el servicio:${NC}"
echo "   sudo systemctl stop $SERVICE_NAME"
echo
echo -e "${BLUE}📝 Para ver el estado del servicio:${NC}"
echo "   sudo systemctl status $SERVICE_NAME"
echo

exit 0
