#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de inicialización temprana para ZK-5AD
Se ejecuta al arranque para asegurar que los GPIO estén en estado seguro
"""

import pigpio
import time
import sys

# Pines GPIO del ZK-5AD (según config.py) - CONFIGURACIÓN ACTUALIZADA
ZK5AD_GPIO_PINS = [12, 13, 16, 26]  # Motor A: 12,16 | Motor B: 13,26

def initialize_zk5ad_gpio():
    """Inicializa los GPIO del ZK-5AD en estado seguro."""
    try:
        print("🔧 Inicializando GPIO para ZK-5AD...")
        
        # Conectar a pigpio daemon
        pi = pigpio.pi()
        if not pi.connected:
            print("❌ No se pudo conectar a pigpio daemon")
            return False
        
        # Configurar cada pin en estado seguro
        for gpio_pin in ZK5AD_GPIO_PINS:
            # Configurar como OUTPUT
            pi.set_mode(gpio_pin, pigpio.OUTPUT)
            
            # Establecer PWM en 255 (motores frenados H+H según truth table)
            pi.set_PWM_dutycycle(gpio_pin, 255)
            
            print(f"   GPIO {gpio_pin}: Configurado como OUTPUT, PWM=255 (BRAKE)")
        
        print("✅ GPIO ZK-5AD inicializados en estado seguro")
        
        # Mantener la configuración por un momento
        time.sleep(1)
        
        # Cerrar conexión
        pi.stop()
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando GPIO ZK-5AD: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Script de inicialización ZK-5AD")
    success = initialize_zk5ad_gpio()
    sys.exit(0 if success else 1)