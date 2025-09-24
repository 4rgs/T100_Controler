#!/bin/bash

echo "🧹 Limpiando archivos obsoletos del proyecto T100..."

# Archivos ESENCIALES para ZK-5AD controller (NO eliminar)
KEEP_FILES=(
    "config.py"
    "elrs_receiver_ultra_fast.py" 
    "elrs_channel_mapper.py"
    "zk5ad_driver_ta6586.py"
    "zk5ad_gpio_init.py"
    "t100_controller.py"
    "emergency_stop.py"
    "requirements.txt"
    "install.sh"
    "deploy.sh"
    "cleanup_obsolete.sh"
    "CABLEADO_ZK5AD.md"
    ".gitignore"
)

# Archivos OBSOLETOS a eliminar (L298N legacy y otros)
OBSOLETE_FILES=(
    # Drivers L298N obsoletos
    "l298n_driver.py"
    "l298n_driver_cartesian_map.py"
    "l298n_driver_curve_corrected.py"
    "l298n_driver_diagram_based.py"
    "l298n_driver_fixed_pwm.py"
    "l298n_driver_ultra_fast.py"
    "l298n_driver_independent_control.py"
    "l298n_driver_tank_simple.py"
    
    # Controladores obsoletos
    "t100_cartesian_controller.py"
    "t100_curve_corrected.py"
    "t100_diagram_based.py"
    "t100_fixed_complete.py"
    "t100_maximum_performance.py"
    "t100_ultra_responsive.py"
    "t100_independent_controller.py"
    "t100_tank_controller.py"
    
    # Herramientas obsoletas
    "calibrate_motors.py"
    "diagnose_motor_emergency.py"
    "test_elrs_reader.py"
    "test_pwm_behavior.py"
    "test_channel_mapping.py"
    
    # Receptores ELRS obsoletos
    "elrs_receiver.py"
    "elrs_receiver_fixed.py"
    "elrs_config.py"
    "elrs_server.py"
    
    # Scripts de instalación obsoletos
    "install_elrs.sh"
    "install_elrs_simple.sh"
    "install_fixed_service.sh"
    "migrate_to_elrs.py"
    "migrate_to_fixed_service.sh"
    "setup_fixed_controller.sh"
    "setup_ultra_responsive.sh"
    
    # Herramientas de diagnóstico obsoletas
    "diagnose_elrs.py"
    "diagnose_motor_sensitivity.py"
    "fix_motor_a_sensitivity.py"
    "fix_serial_port.py"
    "monitor_elrs.py"
    "monitor_serial_raw.py"
    "performance_selector.py"
    
    # Tests obsoletos
    "test_elrs_fixed.py"
    "test_elrs_quick.py"
    "test_monitor_port.py"
    "update_to_fixed_receiver.py"
    
    # Scripts de servicio obsoletos
    "control_service.sh"
    "t100-fixed.service"
    
    # Calibraciones obsoletas
    "calibrate_elrs.py"
    
    # Servidor web obsoleto
    "server.py"
    "set_elrs_port.py"
    
    # READMEs obsoletos
    "README.md"
    "README_ELRS.md"
    "README_INDEPENDENT.md"
)

# Función para verificar si un archivo debe mantenerse
should_keep() {
    local file="$1"
    for keep_file in "${KEEP_FILES[@]}"; do
        if [[ "$file" == "$keep_file" ]]; then
            return 0
        fi
    done
    return 1
}

# Eliminar archivos obsoletos
echo "📄 Eliminando archivos obsoletos..."
for file in "${OBSOLETE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  🗑️  Eliminando: $file"
        rm "$file"
    fi
done

# Eliminar directorio web-client si existe
if [[ -d "web-client" ]]; then
    echo "  🗑️  Eliminando directorio: web-client/"
    rm -rf "web-client"
fi

echo ""
echo "✅ Limpieza completada!"
echo ""
echo "📁 Archivos MANTENIDOS (ZK-5AD refactorizado):"
for file in "${KEEP_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    fi
done

echo ""
echo "🎯 PROYECTO ZK-5AD REFACTORIZADO:"
echo "  ✅ Solo driver ZK-5AD (TA6586)"
echo "  ✅ Controlador único: t100_controller.py"
echo "  ✅ Tank drive: CH2 → Forward/Back, CH4 → Left/Right"
echo "  ✅ GPIO automático al boot"
echo "  ✅ Código limpio y moderno"
echo "  🗑️  Eliminado todo legacy L298N"
