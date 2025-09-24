#!/bin/bash

# Script de despliegue rápido para corregir el problema de async/await
# Solo actualiza los archivos que fueron corregidos

echo "🚀 DESPLIEGUE RÁPIDO - CORRECCIÓN ASYNC/AWAIT"
echo "=============================================="

# Configuración
T100_HOST="4rgs@192.168.1.140"
T100_DIR="t100"

# Archivos a actualizar
FILES_TO_UPDATE=(
    "config.py"
    "test_servos_quick.py" 
    "mg90s_servo_driver.py"
    "fix_gpio_crossover.py"
)

echo "📁 Archivos a actualizar:"
for file in "${FILES_TO_UPDATE[@]}"; do
    echo "   - $file"
done

echo ""
echo "🔄 Copiando archivos al T100..."

# Copiar cada archivo
for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$file" ]; then
        echo "   Copiando $file..."
        scp "$file" "$T100_HOST:$T100_DIR/"
        if [ $? -eq 0 ]; then
            echo "   ✅ $file copiado"
        else
            echo "   ❌ Error copiando $file"
        fi
    else
        echo "   ⚠️  $file no encontrado localmente"
    fi
done

echo ""
echo "🔧 Ejecutando test rápido en T100..."
echo "=============================================="

# Ejecutar test remoto
ssh "$T100_HOST" "cd $T100_DIR && python3 test_servos_quick.py"

echo ""
echo "✅ Despliegue rápido completado"
echo ""
echo "🎮 Para probar manualmente:"
echo "   ssh $T100_HOST"
echo "   cd $T100_DIR"
echo "   python3 test_servos_quick.py"
echo "   python3 t100_controller.py"