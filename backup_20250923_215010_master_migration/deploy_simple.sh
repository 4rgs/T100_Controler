#!/bin/bash

# Despliegue simplificado paso a paso
# Versión con mejor debugging

T100_HOST="4rgs@192.168.1.140"
T100_DIR="t100"

echo "🚀 DESPLIEGUE SIMPLIFICADO T100"
echo "==============================="

# Paso 1: Verificar archivos locales
echo "📋 Paso 1: Verificando archivos locales..."
FILES_TO_COPY=(
    "t100_tank_only.py"
    "t100_camera_only.py" 
    "t100_master.py"
    "manage_services.sh"
    "t100-tank.service"
    "t100-camera.service"
    "test_separated_processes.py"
    "config.py"
    "mg90s_servo_driver.py"
)

for file in "${FILES_TO_COPY[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (faltante)"
        exit 1
    fi
done

# Paso 2: Test de conectividad
echo ""
echo "📡 Paso 2: Probando conectividad..."
if ssh -o ConnectTimeout=5 "$T100_HOST" "echo 'Conectividad OK'" 2>/dev/null; then
    echo "  ✅ SSH conectividad OK"
else
    echo "  ❌ No se puede conectar"
    echo "  Verifica que el T100 esté encendido y conectado"
    exit 1
fi

# Paso 3: Crear directorio y backup
echo ""
echo "💾 Paso 3: Preparando directorio remoto..."
ssh "$T100_HOST" "
    mkdir -p $T100_DIR
    cd $T100_DIR
    if ls *.py >/dev/null 2>&1; then
        echo 'Creando backup...'
        tar -czf backup_\$(date +%Y%m%d_%H%M%S).tar.gz *.py *.service 2>/dev/null || true
    fi
"

# Paso 4: Copiar archivos uno por uno
echo ""
echo "📁 Paso 4: Copiando archivos..."
for file in "${FILES_TO_COPY[@]}"; do
    echo "  Copiando $file..."
    if scp "$file" "$T100_HOST:$T100_DIR/" >/dev/null 2>&1; then
        echo "    ✅ OK"
    else
        echo "    ❌ FALLÓ"
        echo "    Intentando con verbose..."
        scp -v "$file" "$T100_HOST:$T100_DIR/"
        if [[ $? -ne 0 ]]; then
            echo "    Error copiando $file"
            exit 1
        fi
    fi
done

# Paso 5: Configurar permisos
echo ""
echo "🔧 Paso 5: Configurando permisos..."
ssh "$T100_HOST" "cd $T100_DIR && chmod +x *.py *.sh"
echo "  ✅ Permisos configurados"

# Paso 6: Verificar archivos remotos
echo ""
echo "📋 Paso 6: Verificando archivos remotos..."
ssh "$T100_HOST" "cd $T100_DIR && ls -la *.py *.service *.sh"

echo ""
echo "✅ DESPLIEGUE BÁSICO COMPLETADO"
echo ""
echo "🎯 PRÓXIMOS PASOS MANUALES:"
echo "1. Conectar al T100:"
echo "   ssh $T100_HOST"
echo ""
echo "2. Ir al directorio:"
echo "   cd $T100_DIR"
echo ""
echo "3. Probar los scripts:"
echo "   python3 t100_tank_only.py    # (Ctrl+C para parar)"
echo "   python3 t100_camera_only.py  # (Ctrl+C para parar)"
echo "   python3 t100_master.py       # (Ctrl+C para parar)"
echo ""
echo "4. Si funcionan, instalar servicios:"
echo "   ./manage_services.sh install"
echo "   ./manage_services.sh start"
echo ""
echo "5. Ver estado:"
echo "   ./manage_services.sh status"
echo "   ./manage_services.sh logs"