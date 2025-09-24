#!/bin/bash

# Script para copiar todos los archivos necesarios al T100

T100_HOST="4rgs@192.168.1.140"
T100_DIR="t100"

echo "📁 Copiando todos los archivos necesarios al T100..."

# Archivos principales de la nueva arquitectura
CORE_FILES=(
    "elrs_receiver_ultra_fast.py"
    "zk5ad_driver_ta6586.py"
    "mg90s_servo_driver.py"
    "config.py"
    "t100_tank_only.py"
    "t100_camera_only.py"
    "t100_master.py"
    "test_separated_processes.py"
    "manage_services.sh"
    "t100-tank.service"
    "t100-camera.service"
)

# Archivos de prueba y utilidad
UTIL_FILES=(
    "test_servos_quick.py"
    "fix_gpio_crossover.py"
    "diagnose_gpio_mapping.py"
)

ALL_FILES=("${CORE_FILES[@]}" "${UTIL_FILES[@]}")

echo "Copiando ${#ALL_FILES[@]} archivos..."

# Copiar todos los archivos
scp "${ALL_FILES[@]}" "$T100_HOST:$T100_DIR/"

if [ $? -eq 0 ]; then
    echo "✅ Todos los archivos copiados correctamente"
    
    # Configurar permisos
    echo "🔧 Configurando permisos..."
    ssh "$T100_HOST" "cd $T100_DIR && chmod +x *.py *.sh"
    
    echo ""
    echo "🎯 ARCHIVOS LISTOS EN EL T100"
    echo "Para probar:"
    echo "1. ssh $T100_HOST"
    echo "2. cd $T100_DIR"
    echo "3. python3 t100_camera_only.py  # Probar cámara"
    echo "4. python3 t100_tank_only.py    # Probar tank"
    echo "5. python3 t100_master.py       # Probar maestro"
    echo ""
    echo "Para servicios:"
    echo "./manage_services.sh start"
    echo "./manage_services.sh status"
    
else
    echo "❌ Error copiando archivos"
    exit 1
fi