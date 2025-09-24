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

# Lista de archivos a transferir - Proyecto T100 ZK-5AD + MG90S Servos
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
    
    # MG90S Servos Driver (NUEVO)
    "mg90s_servo_driver.py"
    
    # ZK-5AD GPIO Initialization
    "zk5ad_gpio_init.py"
    "zk5ad-gpio-init.service"
    
    # Herramientas de emergencia y diagnóstico
    "emergency_stop.py"
    "update_motor_config.sh"
    "diagnose_motor_individual.py"
    "diagnose_pwm_channels.py"  
    "test_tank_movement.py"
    "test_raw_conversion.py"
    "test_current_spike_protection.py"
    "test_full_system.py"
    "test_servos_only.py"
    "test_servos_quick.py"
    
    # Documentación
    "CABLEADO_ZK5AD.md"
)

# Transferir archivos
echo "📤 Transfiriendo archivos..."
for file in "${FILES[@]}"; do
    echo "  📄 $file"
    scp -o StrictHostKeyChecking=no "$file" $RPI_USER@$RPI_IP:$PROJECT_DIR/
done

# Hacer ejecutables los scripts
echo "🔧 Configurando permisos..."
ssh -o StrictHostKeyChecking=no $RPI_USER@$RPI_IP "
    chmod +x $PROJECT_DIR/install.sh
    chmod +x $PROJECT_DIR/update_motor_config.sh
    chmod +x $PROJECT_DIR/diagnose_motor_individual.py
    chmod +x $PROJECT_DIR/diagnose_pwm_channels.py
    chmod +x $PROJECT_DIR/test_tank_movement.py
    chmod +x $PROJECT_DIR/test_current_spike_protection.py
    chmod +x $PROJECT_DIR/test_raw_conversion.py
    chmod +x $PROJECT_DIR/test_full_system.py
    chmod +x $PROJECT_DIR/test_servos_only.py
    chmod +x $PROJECT_DIR/test_servos_quick.py
"

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
🚀 T100 ZK-5AD + MG90S CONTROLLER - Sistema completo Tank + Cámara

📋 Ejecutar en el Raspberry Pi:
1. ssh 4rgs@192.168.1.140
2. cd /home/4rgs/t100
3. python3 t100_controller.py

🎯 CONTROLADOR PRINCIPAL:
   python3 t100_controller.py
   ✅ ZK-5AD (TA6586) Tank Drive
   ✅ MG90S Servos Cámara Pan/Tilt
   ✅ Doble joystick: Tank + Cámara
   ✅ Failsafe automático
   ✅ Logging y monitoreo

🎮 CONTROLES ELRS:
   TANK DRIVE:
     CH1: Rotación tank (izquierda/derecha)
     CH2: Aceleración tank (adelante/atrás)
   
   CÁMARA:
     CH3: Tilt cámara (arriba/abajo)
     CH4: Pan cámara (izquierda/derecha)

🚨 HERRAMIENTAS DE DIAGNÓSTICO:
   python3 emergency_stop.py                 # Parada inmediata todo
   python3 test_full_system.py               # Test completo sistema
   python3 test_servos_quick.py              # Test rápido solo servos
   python3 test_servos_only.py               # Test completo solo servos
   python3 diagnose_motor_individual.py      # Test motores individuales
   python3 diagnose_pwm_channels.py          # Test canales PWM
   python3 test_tank_movement.py             # Test movimientos tanque
   python3 test_current_spike_protection.py  # Test protección picos corriente
   python3 test_raw_conversion.py            # Test conversión valores
   ./update_motor_config.sh                  # Actualizar configuración
   
📚 DOCUMENTACIÓN:
   cat CABLEADO_ZK5AD.md                # Guía de cableado completa

🎛️  HARDWARE INTEGRADO:
   ✅ ZK-5AD (TA6586) - Motores tank drive
   ✅ MG90S Servos - Control cámara pan/tilt
   ✅ Control dual independiente
   ✅ Configuración GPIO automática al boot
   ✅ Código limpio y modular
   - Driver servo MG90S completamente nuevo
   - Sistema dual joystick funcional
   - Máxima simplicidad y rendimiento"
