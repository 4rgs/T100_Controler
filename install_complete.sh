#!/bin/bash

# Script de instalación completa para T100 Controller en Raspberry Pi
# Este script configura todo desde cero

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
INSTALL_DIR="/opt/web-control"
PROJECT_DIR="$INSTALL_DIR/T100_Controler"
SERVICE_NAME="web-motor.service"
USER_NAME="4rgs"
REPO_URL="https://github.com/4rgs/T100_Controler.git"

echo -e "${BLUE}🚀 Instalación completa de T100 Controller${NC}"
echo "=============================================="

# Verificar root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ Este script debe ejecutarse como root (usar sudo)${NC}"
   exit 1
fi

# Crear directorio de instalación
echo -e "${YELLOW}📁 Creando directorio de instalación...${NC}"
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Clonar o actualizar repositorio
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}📥 Actualizando repositorio existente...${NC}"
    cd $PROJECT_DIR
    git pull origin develop
else
    echo -e "${YELLOW}📥 Clonando repositorio...${NC}"
    git clone $REPO_URL
    cd $PROJECT_DIR
    git checkout develop
fi

# Instalar dependencias del sistema
echo -e "${YELLOW}📦 Instalando dependencias del sistema...${NC}"
apt update
apt install -y python3 python3-pip python3-venv pigpio

# Habilitar y iniciar pigpiod
echo -e "${YELLOW}🔧 Configurando pigpiod...${NC}"
systemctl enable pigpiod
systemctl start pigpiod

# Crear entorno virtual
echo -e "${YELLOW}🐍 Creando entorno virtual de Python...${NC}"
python3 -m venv $INSTALL_DIR/venv

# Activar entorno virtual e instalar dependencias
echo -e "${YELLOW}📚 Instalando dependencias de Python...${NC}"
source $INSTALL_DIR/venv/bin/activate
pip install --upgrade pip
pip install -r $PROJECT_DIR/requirements.txt

# Configurar permisos
echo -e "${YELLOW}🔒 Configurando permisos...${NC}"
chown -R $USER_NAME:$USER_NAME $INSTALL_DIR
usermod -a -G gpio $USER_NAME

# Instalar servicio systemd
echo -e "${YELLOW}⚙️ Instalando servicio systemd...${NC}"
cp $PROJECT_DIR/t100-controller.service /etc/systemd/system/$SERVICE_NAME

# Recargar systemd y habilitar servicio
systemctl daemon-reload
systemctl enable $SERVICE_NAME

# Iniciar servicio
echo -e "${YELLOW}▶️ Iniciando servicio...${NC}"
systemctl start $SERVICE_NAME

# Verificar estado
sleep 3
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✅ ¡Instalación completada exitosamente!${NC}"
    echo -e "${GREEN}🌐 T100 Controller está ejecutándose${NC}"
    echo
    systemctl status $SERVICE_NAME --no-pager -l
else
    echo -e "${RED}❌ Error: El servicio no pudo iniciarse${NC}"
    journalctl -u $SERVICE_NAME --no-pager -l
    exit 1
fi

echo
echo -e "${BLUE}📝 Comandos útiles:${NC}"
echo "   Ver logs:      journalctl -u $SERVICE_NAME -f"
echo "   Reiniciar:     sudo systemctl restart $SERVICE_NAME"
echo "   Detener:       sudo systemctl stop $SERVICE_NAME"
echo "   Estado:        sudo systemctl status $SERVICE_NAME"
echo "   Actualizar:    sudo $PROJECT_DIR/update_t100.sh"
echo
echo -e "${GREEN}🎉 ¡Disfruta tu T100 Controller!${NC}"
