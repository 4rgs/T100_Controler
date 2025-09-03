#!/bin/bash
# Script para configurar el entorno en Raspberry Pi

echo "🔧 Configurando entorno para T100 Controller..."

# Crear directorio de trabajo
sudo mkdir -p /opt/t100-controller
sudo chown 4rgs:4rgs /opt/t100-controller
cd /opt/t100-controller

# Crear virtual environment
echo "📦 Creando virtual environment..."
python3 -m venv venv

# Activar virtual environment
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install Flask==3.0.3
pip install pigpio==1.79
pip install flask-sock==0.7.0
pip install simple-websocket==1.0.0

echo "✅ Entorno configurado correctamente"
echo "📍 Ubicación: /opt/t100-controller"
echo "🐍 Virtual env: /opt/t100-controller/venv"
