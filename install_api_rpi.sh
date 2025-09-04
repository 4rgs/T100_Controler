#!/bin/bash

# T100 Controller - Instalación API para Raspberry Pi Zero 2W
# Configuración optimizada solo para API sin frontend web

set -e

echo "🔌 T100 Controller - Instalación API para RPI Zero 2W"
echo "=================================================="

# Configurar para modo API por defecto
export T100_MODE="api"

# Verificar que estamos en Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Este script está optimizado para Raspberry Pi"
    read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar usuario
if [[ $EUID -eq 0 ]]; then
    echo "❌ No ejecutar como root. Usar usuario normal."
    exit 1
fi

echo "📦 Instalando dependencias del sistema..."
sudo apt-get update -qq
sudo apt-get install -y python3-pip python3-venv git pigpio systemd

echo "🔧 Configurando pigpio..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

echo "📁 Clonando repositorio..."
T100_DIR="/opt/web-motor/T100-Controler"
if [ -d "$T100_DIR" ]; then
    echo "📂 Directorio existente, actualizando..."
    cd "$T100_DIR"
    git pull
else
    sudo mkdir -p $(dirname "$T100_DIR")
    sudo git clone https://github.com/4rgs/T100_Controler.git "$T100_DIR"
    sudo chown -R $USER:$USER "$T100_DIR"
    cd "$T100_DIR"
fi

echo "🐍 Configurando entorno Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "⚙️  Configurando servicio para modo API..."
# Asegurar que el script gateway use modo API
sed -i 's/export T100_MODE=.*/export T100_MODE="api"/' t100_gateway.sh

# Hacer ejecutable
chmod +x t100_gateway.sh

# Crear servicio
./t100_gateway.sh api-mode

echo "🚀 Habilitando e iniciando servicio..."
sudo systemctl enable t100-controller
sudo systemctl start t100-controller

echo "✅ Instalación completada!"
echo ""
echo "📊 Estado del servicio:"
sudo systemctl status t100-controller --no-pager -l

echo ""
echo "🌐 Información de acceso:"
IP=$(hostname -I | awk '{print $1}')
echo "  📡 API URL: http://$IP:5000"
echo "  🔍 Endpoints disponibles:"
echo "    GET  /api/status"
echo "    GET  /api/motors/status" 
echo "    POST /api/control"
echo "    POST /api/emergency/stop"
echo "    GET  /api/config"

echo ""
echo "🛠️  Comandos útiles:"
echo "  Estado:     sudo systemctl status t100-controller"
echo "  Logs:       journalctl -u t100-controller -f"
echo "  Reiniciar:  sudo systemctl restart t100-controller"
echo "  Detener:    sudo systemctl stop t100-controller"

echo ""
echo "🎮 Cliente de desarrollo:"
echo "  Abrir dev_client.html en tu navegador"
echo "  Configurar URL: http://$IP:5000"

echo ""
echo "🔧 Para cambiar a modo web completo:"
echo "  ./t100_gateway.sh web-mode"
