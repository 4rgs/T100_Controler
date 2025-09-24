#!/bin/bash

# Script de despliegue optimizado para T100 Camera Controller
# Aplica optimizaciones específicas para evitar interferencias

echo "🔧 Desplegando T100 Camera Controller OPTIMIZADO..."

RPI_IP="192.168.1.140"
RPI_USER="4rgs"
PROJECT_DIR="/home/4rgs/t100"

# Verificar conexión
echo "📡 Verificando conexión con Raspberry Pi..."
if ! ping -c 1 $RPI_IP > /dev/null 2>&1; then
    echo "❌ No se puede conectar a $RPI_IP"
    exit 1
fi

# Copiar archivos optimizados
echo "📁 Copiando archivos optimizados..."
scp -o StrictHostKeyChecking=no t100_camera_only.py $RPI_USER@$RPI_IP:$PROJECT_DIR/
scp -o StrictHostKeyChecking=no t100-camera-optimized.service $RPI_USER@$RPI_IP:$PROJECT_DIR/
scp -o StrictHostKeyChecking=no optimize_camera_process.py $RPI_USER@$RPI_IP:$PROJECT_DIR/

# Hacer ejecutables
echo "⚙️  Configurando permisos..."
ssh $RPI_USER@$RPI_IP "chmod +x $PROJECT_DIR/t100_camera_only.py"
ssh $RPI_USER@$RPI_IP "chmod +x $PROJECT_DIR/optimize_camera_process.py"

# Configurar servicio optimizado
echo "🔧 Configurando servicio optimizado..."
ssh $RPI_USER@$RPI_IP "
    # Parar servicio anterior si existe
    sudo systemctl stop t100-camera 2>/dev/null || true
    sudo systemctl disable t100-camera 2>/dev/null || true
    
    # Instalar servicio optimizado
    sudo cp $PROJECT_DIR/t100-camera-optimized.service /etc/systemd/system/t100-camera.service
    sudo systemctl daemon-reload
    sudo systemctl enable t100-camera.service
    
    echo '✅ Servicio optimizado instalado'
"

# Instalar dependencias para optimización (si no existen)
echo "📦 Verificando dependencias para optimización..."
ssh $RPI_USER@$RPI_IP "
    if ! python3 -c 'import psutil' 2>/dev/null; then
        echo '📦 Instalando psutil para optimización...'
        pip3 install --user psutil
    fi
    
    # Verificar ionice disponible
    if command -v ionice >/dev/null 2>&1; then
        echo '✅ ionice disponible para optimización I/O'
    else
        echo '⚠️  ionice no disponible - algunas optimizaciones limitadas'
    fi
"

# Aplicar configuraciones del kernel para reducir interferencias
echo "🛡️  Aplicando configuraciones anti-interferencia..."
ssh $RPI_USER@$RPI_IP "
    # Crear archivo de configuración temporal
    echo '# Configuraciones anti-interferencia T100 Camera' | sudo tee /etc/sysctl.d/99-t100-camera.conf
    echo 'vm.swappiness = 10' | sudo tee -a /etc/sysctl.d/99-t100-camera.conf
    echo 'kernel.sched_rt_runtime_us = 950000' | sudo tee -a /etc/sysctl.d/99-t100-camera.conf
    
    # Aplicar configuraciones
    sudo sysctl -p /etc/sysctl.d/99-t100-camera.conf
    
    echo '✅ Configuraciones del kernel aplicadas'
"

echo
echo "✅ DESPLIEGUE OPTIMIZADO COMPLETADO!"
echo
echo "🎯 CAMERA CONTROLLER OPTIMIZADO:"
echo "   ✅ Frecuencia reducida: 20Hz (menos CPU)"
echo "   ✅ Logging mínimo (menos I/O)"
echo "   ✅ Movimiento suavizado con umbral"
echo "   ✅ Prioridad de proceso más baja"
echo "   ✅ Límites de recursos aplicados"
echo "   ✅ Configuraciones kernel anti-interferencia"
echo
echo "🚀 COMANDOS PARA RASPBERRY PI:"
echo
echo "📋 INICIAR SERVICIO OPTIMIZADO:"
echo "   sudo systemctl start t100-camera"
echo "   sudo systemctl status t100-camera"
echo
echo "📊 MONITOREAR RENDIMIENTO:"
echo "   python3 optimize_camera_process.py --monitor 60"
echo
echo "🔧 OPTIMIZAR PROCESO EN TIEMPO REAL:"
echo "   sudo python3 optimize_camera_process.py"
echo
echo "📈 VER LOGS OPTIMIZADOS:"
echo "   journalctl -u t100-camera -f --since '5 minutes ago'"
echo
echo "⚡ TEST MANUAL:"
echo "   python3 t100_camera_only.py"
echo
echo "🎮 FUNCIONALIDADES OPTIMIZADAS:"
echo "   - Solo actualiza servos cuando hay movimiento significativo"
echo "   - Umbral de movimiento: 5 unidades raw"
echo "   - Logging cada 2 segundos (reducido)"
echo "   - Failsafe más tolerante: 1.5s"
echo "   - CPU nice +5 (prioridad más baja)"
echo "   - I/O scheduling de baja prioridad"
echo
echo "🛡️  CONFIGURADO PARA NO INTERFERIR CON:"
echo "   - T100 Tank Drive Controller"
echo "   - Otros procesos críticos del sistema"
echo "   - Operaciones I/O del sistema"
echo
echo "⚠️  NOTAS IMPORTANTES:"
echo "   1. El servicio usa menos CPU pero mantiene la responsividad"
echo "   2. Los logs están minimizados para reducir I/O"
echo "   3. Si necesitas más logs, cambia logging.WARNING a logging.INFO"
echo "   4. Para máxima separación, ejecuta tank y cámara en procesos separados"