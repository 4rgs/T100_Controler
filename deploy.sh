#!/bin/bash

# Script para desplegar T100 Controller al Raspberry Pi
# Uso: ./deploy.sh [IP_RASPBERRY_PI]

# Configuración por defecto
RPI_IP=${1:-"192.168.1.140"}
RPI_USER="4rgs"
PROJECT_DIR="/home/4rgs/t100"

echo "🚁 Desplegando T100 Controller a Raspberry Pi..."
echo "📡 IP objetivo: $RPI_IP"
echo "👤 Usuario: $RPI_USER"
echo "📁 Directorio: $PROJECT_DIR"
echo

# Verificar conectividad
echo "🔍 Verificando conectividad..."
if ! ping -c 1 $RPI_IP > /dev/null 2>&1; then
    echo "❌ No se puede conectar a $RPI_IP"
    echo "💡 Verifica la IP y que el Raspberry Pi esté encendido"
    exit 1
fi

echo "✅ Raspberry Pi accesible"
echo "💡 Tip: Para evitar repetir contraseña, configura claves SSH:"
echo "   ssh-keygen -t rsa && ssh-copy-id $RPI_USER@$RPI_IP"
echo

# Crear directorio remoto
echo "📁 Creando directorio remoto..."
ssh -o StrictHostKeyChecking=no $RPI_USER@$RPI_IP "mkdir -p $PROJECT_DIR"

# Archivos a transferir (solo esenciales para API)
FILES=(
    "config.py"
    "l298n_driver.py"
    "server.py"
    "client.html"
    "calibrate_motors.py"
    "requirements.txt"
    "install.sh"
    "README.md"
)

# Transferir archivos
echo "📤 Transfiriendo archivos..."
for file in "${FILES[@]}"; do
    echo "  📄 $file"
    scp -o StrictHostKeyChecking=no "$file" $RPI_USER@$RPI_IP:$PROJECT_DIR/
done

# Hacer ejecutable el script de instalación
echo "🔧 Configurando permisos..."
ssh -o StrictHostKeyChecking=no $RPI_USER@$RPI_IP "chmod +x $PROJECT_DIR/install.sh"

echo
echo "✅ Despliegue completado!"
echo
echo "🚀 Próximos pasos en el Raspberry Pi:"
echo "1. ssh $RPI_USER@$RPI_IP"
echo "2. cd $PROJECT_DIR"
echo "3. ./install.sh"
echo "4. python3 calibrate_motors.py  # Calibrar motores si es necesario"
echo "5. sudo systemctl start t100"
echo
echo "🌐 Una vez instalado, abrir client.html en el navegador:"
echo "   - Configurar IP: $RPI_IP"
echo "   - Puerto: 8080"
echo "   - Conectar y controlar!"
echo
echo "🔧 Para calibración de motores:"
echo "   python3 calibrate_motors.py  # Calibrar motores"
echo
echo "📊 Para monitorear:"
echo "   ssh $RPI_USER@$RPI_IP"
echo "   sudo journalctl -u t100 -f"
