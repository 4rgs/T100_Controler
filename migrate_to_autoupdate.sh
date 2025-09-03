#!/bin/bash

# Script para migrar al servicio con auto-actualización

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Migrando a servicio con auto-actualización...${NC}"

# Verificar permisos de root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ Este script debe ejecutarse como root (usar sudo)${NC}"
   exit 1
fi

# Variables
OLD_SERVICE="web-motor.service"
NEW_SERVICE="t100-controller-autoupdate.service"
PROJECT_DIR="/opt/web-control/T100_Controler"

# Detener servicio anterior si existe
if systemctl is-active --quiet $OLD_SERVICE 2>/dev/null; then
    echo -e "${YELLOW}⏹️ Deteniendo servicio anterior...${NC}"
    systemctl stop $OLD_SERVICE
fi

if systemctl is-enabled --quiet $OLD_SERVICE 2>/dev/null; then
    echo -e "${YELLOW}❌ Deshabilitando servicio anterior...${NC}"
    systemctl disable $OLD_SERVICE
fi

# Copiar nuevo archivo de servicio
echo -e "${YELLOW}📄 Instalando nuevo servicio...${NC}"
cp "$PROJECT_DIR/$NEW_SERVICE" "/etc/systemd/system/"

# Recargar systemd
echo -e "${YELLOW}🔄 Recargando systemd daemon...${NC}"
systemctl daemon-reload

# Habilitar nuevo servicio
echo -e "${YELLOW}✅ Habilitando nuevo servicio...${NC}"
systemctl enable $NEW_SERVICE

# Iniciar nuevo servicio
echo -e "${YELLOW}▶️ Iniciando servicio con auto-actualización...${NC}"
systemctl start $NEW_SERVICE

# Esperar un momento
sleep 5

# Verificar estado
if systemctl is-active --quiet $NEW_SERVICE; then
    echo -e "${GREEN}✅ ¡Migración completada exitosamente!${NC}"
    echo -e "${GREEN}🔄 El servicio ahora se auto-actualiza en cada inicio${NC}"
    echo
    echo -e "${BLUE}📊 Estado del nuevo servicio:${NC}"
    systemctl status $NEW_SERVICE --no-pager -l
else
    echo -e "${RED}❌ Error: El nuevo servicio no pudo iniciarse${NC}"
    echo -e "${YELLOW}📋 Verificando logs...${NC}"
    journalctl -u $NEW_SERVICE --no-pager -l
    exit 1
fi

echo
echo -e "${BLUE}📝 Comandos para el nuevo servicio:${NC}"
echo "   Ver logs:      journalctl -u $NEW_SERVICE -f"
echo "   Reiniciar:     sudo systemctl restart $NEW_SERVICE"
echo "   Detener:       sudo systemctl stop $NEW_SERVICE"
echo "   Estado:        sudo systemctl status $NEW_SERVICE"
echo
echo -e "${GREEN}🎉 ¡El T100 Controller ahora se actualiza automáticamente!${NC}"
echo -e "${YELLOW}⚠️ Cada vez que reinicies el servicio, verificará e instalará actualizaciones desde GitHub${NC}"
