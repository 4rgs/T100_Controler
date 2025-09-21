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

# Lista de archivos a transferir - Proyecto T100 ZK-5AD limpio
FILES=(
    # Configuración
    "config.py"
    "requirements.txt"
    "install.sh"
    
    # Sistema ELRS
    "elrs_receiver_ultra_fast.py"
    
    # ZK-5AD Driver y Controller principal
    "zk5ad_driver_ta6586.py"
    "t100_controller.py"
    
    # ZK-5AD GPIO Initialization
    "zk5ad_gpio_init.py"
    "zk5ad-gpio-init.service"
    
    # Herramientas de emergencia
    "emergency_stop.py"
    
    # Documentación
    "CABLEADO_ZK5AD.md"
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

# Instalar servicio de inicialización ZK-5AD
echo "⚙️  Instalando servicio de inicialización ZK-5AD..."
ssh -o StrictHostKeyChecking=no $RPI_USER@$RPI_IP "
    sudo cp $PROJECT_DIR/zk5ad-gpio-init.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable zk5ad-gpio-init.service
    echo '✅ Servicio ZK-5AD inicialización instalado'
"

echo
echo "✅ Despliegue completado!
🚀 T100 ZK-5AD CONTROLLER - Proyecto refactorizado y limpio

📋 Ejecutar en el Raspberry Pi:
1. ssh 4rgs@192.168.1.140
2. cd /home/4rgs/t100
3. python3 t100_controller.py

🎯 CONTROLADOR PRINCIPAL:
   python3 t100_controller.py
   ✅ ZK-5AD (TA6586) Tank Drive
   ✅ CH2 → Forward/Back, CH4 → Left/Right
   ✅ Control con palanca derecha únicamente
   ✅ Failsafe automático
   ✅ Logging y monitoreo

🎮 CONTROLES:
   Palanca derecha VERTICAL: Adelante/Atrás
   Palanca derecha HORIZONTAL: Izquierda/Derecha
   Palanca izquierda: IGNORADA

🚨 HERRAMIENTAS:
   python3 emergency_stop.py     # Parada inmediata
   
📚 DOCUMENTACIÓN:
   cat CABLEADO_ZK5AD.md         # Guía de cableado completa

🧹 PROYECTO REFACTORIZADO:
   ✅ Solo ZK-5AD (TA6586) - Eliminado L298N obsoleto
   ✅ Controlador único y moderno  
   ✅ Configuración GPIO automática al boot
   ✅ Código limpio y mantenible
   - Solo 15 archivos esenciales
   - Sin versiones antiguas ni código muerto
   - Máxima simplicidad y rendimiento"
