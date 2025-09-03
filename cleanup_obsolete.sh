#!/bin/bash

# Script para limpiar archivos obsoletos y usar solo el gateway

echo "🧹 Limpiando archivos obsoletos del T100 Controller..."

# Lista de archivos obsoletos que se pueden eliminar
OBSOLETE_FILES=(
    "setup_rpi.sh"
    "install_rpi.sh"
    "install_complete.sh"
    "start_optimized.sh"
    "optimize_system.sh"
    "auto_install.sh"
    "update_t100.sh"
    "update_simple.sh"
    "update_t100_lite.sh"
    "start_with_update.sh"
    "migrate_to_autoupdate.sh"
    "verify_environment.sh"
    "update_system.sh"
)

# Archivos de servicio obsoletos
OBSOLETE_SERVICES=(
    "t100-controller.service"
    "t100-controller-autoupdate.service"
)

# Contar archivos encontrados
found_files=0
removed_files=0

echo "Buscando archivos obsoletos..."

for file in "${OBSOLETE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ❌ Encontrado: $file"
        found_files=$((found_files + 1))
    fi
done

# Verificar servicios obsoletos
for service in "${OBSOLETE_SERVICES[@]}"; do
    if [ -f "/etc/systemd/system/$service" ]; then
        echo "  ❌ Servicio obsoleto: $service"
        found_files=$((found_files + 1))
    fi
done

if [ $found_files -eq 0 ]; then
    echo "✅ No se encontraron archivos obsoletos"
    exit 0
fi

echo ""
echo "Se encontraron $found_files archivos obsoletos."
read -p "¿Deseas eliminarlos? (y/N): " -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Eliminando archivos obsoletos..."
    
    # Eliminar archivos
    for file in "${OBSOLETE_FILES[@]}"; do
        if [ -f "$file" ]; then
            rm "$file"
            echo "  🗑️  Eliminado: $file"
            removed_files=$((removed_files + 1))
        fi
    done
    
    # Eliminar servicios obsoletos
    for service in "${OBSOLETE_SERVICES[@]}"; do
        if [ -f "/etc/systemd/system/$service" ]; then
            # Detener y deshabilitar servicio
            sudo systemctl stop "$service" 2>/dev/null || true
            sudo systemctl disable "$service" 2>/dev/null || true
            sudo rm "/etc/systemd/system/$service"
            echo "  🗑️  Eliminado servicio: $service"
            removed_files=$((removed_files + 1))
        fi
    done
    
    # Recargar systemd si se eliminaron servicios
    if [ $removed_files -gt 0 ]; then
        sudo systemctl daemon-reload
    fi
    
    echo ""
    echo "✅ Limpieza completada: $removed_files archivos eliminados"
    echo ""
    echo "🚀 Ahora usa solamente:"
    echo "   ./t100_gateway.sh [comando]"
    echo ""
    echo "📋 Comandos disponibles:"
    echo "   install  - Instalación completa"
    echo "   run      - Ejecutar directamente"
    echo "   status   - Ver estado"
    echo "   update   - Actualizar desde GitHub"
    echo "   monitor  - Monitorear recursos"
    echo "   restart  - Reiniciar servicio"
    echo "   logs     - Ver logs"
    
else
    echo "❌ Limpieza cancelada"
fi
