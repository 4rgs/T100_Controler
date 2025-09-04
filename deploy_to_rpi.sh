#!/bin/bash

# T100 Controller - Deploy a Raspberry Pi
# Script para desplegar la versión API desde el desarrollo

set -e

# Configuración
RPI_HOST="${1:-}"
RPI_USER="${2:-4rgs}"
LOCAL_DIR="$(pwd)"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verificar parámetros
if [ -z "$RPI_HOST" ]; then
    log_error "Se requiere la IP o hostname de la Raspberry Pi"
    echo "Uso: $0 <IP_RASPBERRY> [usuario]"
    echo "Ejemplo: $0 192.168.1.100 4rgs"
    exit 1
fi

log_info "🚀 Desplegando T100 Controller a $RPI_HOST"
log_info "👤 Usuario: $RPI_USER"

# Verificar conexión SSH
log_info "🔍 Verificando conexión SSH..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes $RPI_USER@$RPI_HOST exit 2>/dev/null; then
    log_error "No se puede conectar por SSH a $RPI_USER@$RPI_HOST"
    log_info "Asegúrate de:"
    log_info "  1. SSH habilitado en la Raspberry Pi"
    log_info "  2. Clave SSH configurada (ssh-copy-id $RPI_USER@$RPI_HOST)"
    log_info "  3. IP correcta"
    exit 1
fi

log_info "✅ Conexión SSH establecida"

# Verificar archivos necesarios
REQUIRED_FILES=(
    "api_main.py"
    "install_api_rpi.sh"
    "t100_gateway.sh"
    "dev_client.html"
    "test_api.py"
    "requirements.txt"
    "src/"
)

log_info "📋 Verificando archivos necesarios..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -e "$LOCAL_DIR/$file" ]; then
        log_error "Archivo faltante: $file"
        exit 1
    fi
done

log_info "✅ Todos los archivos encontrados"

# Crear directorio temporal para el deploy
TEMP_DIR="/tmp/t100_deploy_$(date +%s)"
mkdir -p "$TEMP_DIR"

log_info "📦 Preparando archivos para deploy..."

# Copiar archivos necesarios
cp -r "$LOCAL_DIR/src" "$TEMP_DIR/"
cp "$LOCAL_DIR/api_main.py" "$TEMP_DIR/"
cp "$LOCAL_DIR/install_api_rpi.sh" "$TEMP_DIR/"
cp "$LOCAL_DIR/t100_gateway.sh" "$TEMP_DIR/"
cp "$LOCAL_DIR/requirements.txt" "$TEMP_DIR/"
cp "$LOCAL_DIR/dev_client.html" "$TEMP_DIR/"
cp "$LOCAL_DIR/test_api.py" "$TEMP_DIR/"

# Crear archivo de deploy info
cat > "$TEMP_DIR/deploy_info.txt" << EOF
T100 Controller API Deploy
=========================
Fecha: $(date)
Desde: $(hostname)
Usuario: $(whoami)
Commit: $(git rev-parse HEAD 2>/dev/null || echo "N/A")
Branch: $(git branch --show-current 2>/dev/null || echo "N/A")
EOF

log_info "📡 Transfiriendo archivos a la Raspberry Pi..."

# Transferir archivos
ssh $RPI_USER@$RPI_HOST "mkdir -p /tmp/t100_deploy"
scp -r "$TEMP_DIR"/* $RPI_USER@$RPI_HOST:/tmp/t100_deploy/

log_info "🔧 Ejecutando instalación en la Raspberry Pi..."

# Ejecutar instalación remota
ssh $RPI_USER@$RPI_HOST << 'EOF'
set -e

echo "🔄 Iniciando instalación en Raspberry Pi..."

# Ir al directorio de deploy
cd /tmp/t100_deploy

# Parar servicio si existe
sudo systemctl stop t100-controller 2>/dev/null || true

# Directorio de instalación
INSTALL_DIR="/opt/web-motor/T100-Controler"

# Backup de configuración existente si existe
if [ -d "$INSTALL_DIR" ]; then
    echo "💾 Creando backup de configuración..."
    if [ -f "$INSTALL_DIR/config.local.py" ]; then
        cp "$INSTALL_DIR/config.local.py" /tmp/config.local.py.backup
        echo "✅ Backup de configuración guardado"
    fi
fi

# Crear directorio de instalación
sudo mkdir -p "$INSTALL_DIR"

# Copiar archivos nuevos
echo "📁 Copiando archivos..."
sudo cp -r * "$INSTALL_DIR/"
sudo chown -R $USER:$USER "$INSTALL_DIR"

# Ir al directorio de instalación
cd "$INSTALL_DIR"

# Restaurar configuración si existe
if [ -f "/tmp/config.local.py.backup" ]; then
    cp /tmp/config.local.py.backup config.local.py
    echo "✅ Configuración restaurada"
fi

# Hacer scripts ejecutables
chmod +x install_api_rpi.sh
chmod +x t100_gateway.sh
chmod +x test_api.py

# Configurar entorno Python si no existe
if [ ! -d "venv" ]; then
    echo "🐍 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno e instalar dependencias
echo "📦 Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configurar para modo API
echo "⚙️ Configurando modo API..."
export T100_MODE="api"
sed -i 's/export T100_MODE=.*/export T100_MODE="api"/' t100_gateway.sh

# Crear/actualizar servicio systemd
./t100_gateway.sh api-mode

# Habilitar e iniciar servicio
echo "🚀 Iniciando servicio..."
sudo systemctl enable t100-controller
sudo systemctl start t100-controller

# Esperar a que inicie
sleep 3

# Verificar estado
echo "📊 Verificando estado del servicio..."
sudo systemctl status t100-controller --no-pager -l

echo "✅ Instalación completada!"

# Limpiar archivos temporales
rm -rf /tmp/t100_deploy

EOF

# Limpiar archivos temporales locales
rm -rf "$TEMP_DIR"

log_info "🧪 Ejecutando test de la API..."

# Esperar un poco más para que inicie completamente
sleep 5

# Test de la API
if python3 test_api.py "http://$RPI_HOST:5000"; then
    log_info "✅ Test de API exitoso!"
else
    log_warning "⚠️ Test de API falló, pero el servicio puede estar iniciando"
fi

log_info "🎉 Deploy completado exitosamente!"
echo ""
echo "📊 Información del deploy:"
echo "  🌐 API URL: http://$RPI_HOST:5000"
echo "  🎮 Cliente: Abrir dev_client.html y usar la URL anterior"
echo ""
echo "🛠️ Comandos útiles en la RPI:"
echo "  ssh $RPI_USER@$RPI_HOST"
echo "  sudo systemctl status t100-controller"
echo "  journalctl -u t100-controller -f"
echo ""
echo "🔧 Gestión remota:"
echo "  ssh $RPI_USER@$RPI_HOST 'cd /opt/web-motor/T100-Controler && ./t100_gateway.sh status'"
echo "  ssh $RPI_USER@$RPI_HOST 'cd /opt/web-motor/T100-Controler && ./t100_gateway.sh restart'"
