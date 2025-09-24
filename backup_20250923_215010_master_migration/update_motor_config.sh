#!/bin/bash

# Script de actualización rápida para corregir configuración PWM ZK-5AD
# Usar en Raspberry Pi después de los cambios de configuración PWM

echo "🔧 Actualizando configuración PWM ZK-5AD..."
echo "📋 NUEVA CONFIGURACIÓN PWM:"
echo "   Motor A: GPIO 12 (PWM0) + GPIO 16 (Digital)"
echo "   Motor B: GPIO 13 (PWM1) + GPIO 26 (Digital)"
echo "   ✅ Evita interferencia PWM entre motores"
echo ""

# Parar servicio actual
echo "🛑 Parando servicio t100-zk5ad..."
sudo systemctl stop t100-zk5ad 2>/dev/null || true

# Parar motores por emergencia
echo "🚨 Aplicando parada de emergencia..."
python3 emergency_stop.py

# Reinicializar GPIO con nueva configuración
echo "🔧 Reinicializando GPIO con nueva configuración..."
python3 zk5ad_gpio_init.py

echo "✅ Sistema parado - Configuración PWM actualizada"
echo ""
echo "🚀 PARA REINICIAR:"
echo "  sudo systemctl start t100-zk5ad"
echo ""
echo "🔍 HERRAMIENTAS DE DIAGNÓSTICO:"
echo "  python3 diagnose_pwm_channels.py      → Test canales PWM"
echo "  python3 diagnose_motor_individual.py  → Test motores individuales"
echo "  python3 test_tank_movement.py         → Test movimientos tanque"
echo ""
echo "📊 VER LOGS EN TIEMPO REAL:"
echo "  sudo journalctl -u t100-zk5ad -f"
echo ""
echo "⚠️  NOTA: Si persisten problemas PWM, ejecutar diagnose_pwm_channels.py"