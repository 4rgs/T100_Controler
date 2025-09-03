#!/bin/bash

# Script de verificación rápida para T100 Controller

echo "🔍 Verificando T100 Controller..."

# Verificar servicio
echo "📊 Estado del servicio:"
sudo systemctl status t100-controller-optimized --no-pager -l

echo ""
echo "📋 Últimos logs:"
journalctl -u t100-controller-optimized -n 10 --no-pager

echo ""
echo "🌐 Verificando puerto 5000:"
if netstat -tlnp | grep -q ":5000 "; then
    echo "✅ Puerto 5000 está activo"
    IP=$(hostname -I | awk '{print $1}')
    echo "🔗 Acceso web: http://$IP:5000"
else
    echo "❌ Puerto 5000 no está activo"
fi

echo ""
echo "🔧 Memoria y CPU:"
free -h | head -2
top -bn1 | grep "Cpu(s)" | head -1

if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    echo "🌡️  Temperatura: $(cat /sys/class/thermal/thermal_zone0/temp | awk '{printf("%.1f°C\n", $1/1000)}')"
fi

echo ""
echo "📁 Verificando archivos:"
cd /opt/web-motor/T100-Controler || cd /opt/web-control/T100-Controler 2>/dev/null || {
    echo "❌ Directorio de instalación no encontrado"
    exit 1
}

echo "✅ Directorio: $(pwd)"

if [ -f "motor_control_optimized.py" ]; then
    echo "✅ motor_control_optimized.py existe"
else
    echo "❌ motor_control_optimized.py no encontrado"
fi

if [ -d "venv" ]; then
    echo "✅ Entorno virtual existe"
    if [ -f "venv/bin/python" ]; then
        echo "✅ Python virtual activo"
    fi
else
    echo "❌ Entorno virtual no encontrado"
fi

echo ""
echo "🚀 Comandos útiles:"
echo "   Ver logs: journalctl -u t100-controller-optimized -f"
echo "   Reiniciar: sudo systemctl restart t100-controller-optimized"
echo "   Estado: sudo systemctl status t100-controller-optimized"
echo "   Detener: sudo systemctl stop t100-controller-optimized"
