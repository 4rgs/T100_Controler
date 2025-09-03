#!/bin/bash
# Instalación completa del T100 Controller en Raspberry Pi

set -e  # Salir si hay error

echo "🚀 Instalando T100 Motor Controller..."

# Variables
SERVICE_NAME="t100-controller"
INSTALL_DIR="/opt/t100-controller"
USER="4rgs"
REPO_URL="https://github.com/4rgs/T100_Controler.git"
BRANCH="develop"

# Función para logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Iniciando instalación..."

# 1. Parar servicio si existe
if systemctl is-active --quiet $SERVICE_NAME; then
    log "Parando servicio existente..."
    sudo systemctl stop $SERVICE_NAME
fi

# 2. Crear directorio y cambiar permisos
log "Preparando directorio de instalación..."
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$USER $INSTALL_DIR
cd $INSTALL_DIR

# 3. Clonar o actualizar repositorio
if [ -d ".git" ]; then
    log "Actualizando código existente..."
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    log "Clonando repositorio..."
    git clone -b $BRANCH $REPO_URL .
fi

# 4. Crear virtual environment
log "Configurando virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Actualizar pip e instalar dependencias
log "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Verificar que pigpiod esté habilitado
log "Configurando pigpiod..."
if ! systemctl is-enabled --quiet pigpiod; then
    sudo systemctl enable pigpiod
fi

if ! systemctl is-active --quiet pigpiod; then
    sudo systemctl start pigpiod
fi

# 7. Instalar servicio systemd
log "Instalando servicio systemd..."
sudo cp $SERVICE_NAME.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# 8. Iniciar servicio
log "Iniciando servicio..."
sudo systemctl start $SERVICE_NAME

# 9. Verificar estado
log "Verificando instalación..."
sleep 3

if systemctl is-active --quiet $SERVICE_NAME; then
    log "✅ Servicio iniciado correctamente"
    log "🌐 Servidor disponible en: http://$(hostname -I | awk '{print $1}'):8080"
    log "📊 Estado del servicio: sudo systemctl status $SERVICE_NAME"
    log "📝 Logs: sudo journalctl -u $SERVICE_NAME -f"
else
    log "❌ Error: El servicio no se inició correctamente"
    log "📝 Revisar logs: sudo journalctl -u $SERVICE_NAME -n 20"
    exit 1
fi

log "🎉 Instalación completada!"
