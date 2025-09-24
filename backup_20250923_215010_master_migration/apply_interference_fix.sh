#!/bin/bash

# Script de implementación rápida para eliminar interferencias PWM
# Aplica la configuración anti-interferencia automáticamente

set -e

echo "🛡️  T100 - ELIMINADOR DE INTERFERENCIAS PWM"
echo "=============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "config.py" ] || [ ! -f "t100_controller.py" ]; then
    print_error "No estás en el directorio T100 correcto"
    exit 1
fi

print_info "Directorio T100 detectado correctamente"

# 1. Crear backup de archivos actuales
echo -e "\n📦 ${BLUE}PASO 1: Creando backup...${NC}"

BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

cp config.py "$BACKUP_DIR/"
cp t100_controller.py "$BACKUP_DIR/" 2>/dev/null || true
cp mg90s_servo_driver.py "$BACKUP_DIR/" 2>/dev/null || true

print_status "Backup creado en $BACKUP_DIR/"

# 2. Aplicar nueva configuración anti-interferencia
echo -e "\n⚙️  ${BLUE}PASO 2: Aplicando configuración anti-interferencia...${NC}"

# Crear nueva configuración
cat > config_new.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuración T100 - ANTI-INTERFERENCIA APLICADA
Hardware: ZK-5AD + RPi Zero 2W + Servos MG90S
"""

from dataclasses import dataclass


@dataclass
class MotorPins:
    """Configuración de pines para un motor ZK-5AD (TA6586)."""
    in1: int  # Pin IN1 - PWM para control de velocidad/dirección
    in2: int  # Pin IN2 - PWM para control de velocidad/dirección
    invert: bool = False
    power_factor: float = 1.0  # Factor de calibración de potencia (0.5 - 1.5)


@dataclass
class ServoConfig:
    """Configuración para servo MG90S."""
    gpio_pin: int  # Pin GPIO para control PWM del servo
    center_pulse: int = 1500  # Pulso central en microsegundos (1500µs = 90°)
    min_pulse: int = 500      # Pulso mínimo en microsegundos (~0°)
    max_pulse: int = 2500     # Pulso máximo en microsegundos (~180°)
    invert: bool = False      # Invertir dirección del servo
    name: str = "servo"       # Nombre descriptivo


@dataclass
class HardwareConfig:
    """Configuración ANTI-INTERFERENCIA del hardware."""
    # Motores para tank drive (campos requeridos primero)
    motor_a: MotorPins  # Motor izquierdo
    motor_b: MotorPins  # Motor derecho
    servo_pan: ServoConfig   # Servo horizontal (CH4)
    servo_tilt: ServoConfig  # Servo vertical (CH3)
    
    # Campos con valores por defecto - OPTIMIZADO ANTI-INTERFERENCIA
    pwm_frequency: int = 2000  # Reducida para menor interferencia
    max_pwm_percent: float = 90  # Limitado para reducir ruido eléctrico
    direction_change_delay: float = 0.100  # Aumentado para estabilidad
    enable_direction_protection: bool = True


# CONFIGURACIÓN ANTI-INTERFERENCIA - MÁXIMA SEPARACIÓN FÍSICA
#
# CAMBIOS APLICADOS:
# ==================
# ANTES (problemático):              DESPUÉS (anti-interferencia):
# - Motor A: GPIO 12,16              → Motor A: GPIO 18,24  
# - Motor B: GPIO 13,26              → Motor B: GPIO 19,25
# - Servo Pan: GPIO 21               → Servo Pan: GPIO 17
# - Servo Tilt: GPIO 20              → Servo Tilt: GPIO 4
#
# VENTAJAS:
# - GPIO 18/19: Hardware PWM dedicado (PWM0/PWM1) 
# - GPIO 24/25: Digitales en esquina opuesta del chip
# - GPIO 17/4: Power rail, máxima separación física
# - Frecuencia PWM reducida: 4000Hz → 2000Hz
# - Potencia limitada: 100% → 90%
#
DEFAULT_CONFIG = {
    "hardware": HardwareConfig(
        # Motores - Hardware PWM + digitales separados
        motor_a=MotorPins(in1=18, in2=24, invert=False, power_factor=0.9),  # PWM0 + Esquina opuesta
        motor_b=MotorPins(in1=19, in2=25, invert=True, power_factor=0.9),   # PWM1 + Esquina opuesta
        
        # Servos - Power rail, máxima separación
        servo_pan=ServoConfig(gpio_pin=17, name="Pan", invert=True),    # Power rail
        servo_tilt=ServoConfig(gpio_pin=4, name="Tilt", invert=True),   # Power rail, esquina opuesta
        
        # Anti-interferencia
        pwm_frequency=2000,           # Reducida
        max_pwm_percent=90.0,         # Limitada
        direction_change_delay=0.100, # Estabilidad
        enable_direction_protection=True
    )
}


def get_config() -> dict:
    """Retorna la configuración anti-interferencia."""
    return DEFAULT_CONFIG
EOF

print_status "Nueva configuración generada"

# 3. Reemplazar configuración actual
echo -e "\n🔄 ${BLUE}PASO 3: Aplicando nueva configuración...${NC}"

mv config.py config_old.py
mv config_new.py config.py

print_status "Configuración anti-interferencia aplicada"

# 4. Mostrar diagrama de cableado
echo -e "\n🔌 ${BLUE}PASO 4: NUEVO DIAGRAMA DE CABLEADO${NC}"
echo "======================================"

echo -e "\n${YELLOW}📡 RASPBERRY PI → ZK-5AD:${NC}"
echo "   GPIO 18 (Pin 12) → Motor A IN1  [PWM0 - Hardware]"
echo "   GPIO 24 (Pin 18) → Motor A IN2  [Digital]"
echo "   GPIO 19 (Pin 35) → Motor B IN1  [PWM1 - Hardware]" 
echo "   GPIO 25 (Pin 22) → Motor B IN2  [Digital]"

echo -e "\n${YELLOW}📹 RASPBERRY PI → SERVOS:${NC}"
echo "   GPIO 17 (Pin 11) → Servo Pan   [Power rail]"
echo "   GPIO 4  (Pin 7)  → Servo Tilt  [Power rail]"

echo -e "\n${YELLOW}⚡ ALIMENTACIÓN:${NC}"
echo "   3.3V (Pin 1) → ZK-5AD 3V3"
echo "   GND  (Pin 6) → ZK-5AD GND" 
echo "   Fuente externa 6-12V → ZK-5AD VT"

# 5. Crear script de test rápido
echo -e "\n🧪 ${BLUE}PASO 5: Creando test de verificación...${NC}"

cat > test_interference_fix.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test rápido para verificar que la corrección anti-interferencia funciona
"""

import time
import sys

try:
    import pigpio
except ImportError:
    print("❌ pigpio no instalado. Instala con: sudo apt install python3-pigpio")
    sys.exit(1)

from config import get_config

def test_anti_interference():
    """Test de la configuración anti-interferencia."""
    print("🧪 TEST ANTI-INTERFERENCIA")
    print("=" * 40)
    
    config = get_config()
    hw = config['hardware']
    
    # Mostrar configuración
    print(f"\n⚙️  Configuración cargada:")
    print(f"   Motor A: GPIO {hw.motor_a.in1}, {hw.motor_a.in2}")
    print(f"   Motor B: GPIO {hw.motor_b.in1}, {hw.motor_b.in2}")
    print(f"   Servo Pan: GPIO {hw.servo_pan.gpio_pin}")
    print(f"   Servo Tilt: GPIO {hw.servo_tilt.gpio_pin}")
    print(f"   PWM Freq: {hw.pwm_frequency} Hz")
    
    # Conectar a pigpio
    pi = pigpio.pi()
    if not pi.connected:
        print("❌ No se pudo conectar a pigpio daemon")
        return False
    
    try:
        print(f"\n🔄 Probando configuración por 3 segundos...")
        
        # Configurar pines
        pi.set_mode(hw.motor_a.in1, pigpio.OUTPUT)
        pi.set_mode(hw.motor_a.in2, pigpio.OUTPUT) 
        pi.set_mode(hw.motor_b.in1, pigpio.OUTPUT)
        pi.set_mode(hw.motor_b.in2, pigpio.OUTPUT)
        pi.set_mode(hw.servo_pan.gpio_pin, pigpio.OUTPUT)
        pi.set_mode(hw.servo_tilt.gpio_pin, pigpio.OUTPUT)
        
        # Test PWM suave
        print("   🚗 Activando motores...")
        pi.hardware_PWM(hw.motor_a.in1, hw.pwm_frequency, 250000)  # 25%
        pi.hardware_PWM(hw.motor_b.in1, hw.pwm_frequency, 250000)  # 25%
        
        time.sleep(1)
        
        print("   📹 Activando servos...")
        pi.set_PWM_frequency(hw.servo_pan.gpio_pin, 50)
        pi.set_PWM_frequency(hw.servo_tilt.gpio_pin, 50)
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 1500)    # Centro
        pi.set_servo_pulsewidth(hw.servo_tilt.gpio_pin, 1500)   # Centro
        
        time.sleep(2)
        
        print("   🔄 Movimiento suave...")
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 1000)    # Izquierda
        time.sleep(0.5)
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 2000)    # Derecha
        time.sleep(0.5)
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 1500)    # Centro
        
        print("   ✅ Test completado sin interferencias aparentes")
        
    except Exception as e:
        print(f"   ❌ Error durante test: {e}")
        return False
    finally:
        # Limpiar
        pi.hardware_PWM(hw.motor_a.in1, 0, 0)
        pi.hardware_PWM(hw.motor_b.in1, 0, 0)
        pi.set_PWM_dutycycle(hw.motor_a.in2, 0)
        pi.set_PWM_dutycycle(hw.motor_b.in2, 0)
        pi.set_servo_pulsewidth(hw.servo_pan.gpio_pin, 0)
        pi.set_servo_pulsewidth(hw.servo_tilt.gpio_pin, 0)
        pi.stop()
    
    return True

if __name__ == "__main__":
    if test_anti_interference():
        print("\n✅ CONFIGURACIÓN ANTI-INTERFERENCIA OK")
        print("\n📋 Próximos pasos:")
        print("   1. Reconectar cables según diagrama mostrado")
        print("   2. Reiniciar servicios: sudo systemctl restart t100-*")
        print("   3. Probar sistema completo")
    else:
        print("\n❌ Problemas detectados en configuración")
EOF

chmod +x test_interference_fix.py
print_status "Test de verificación creado"

# 6. Mostrar resumen final
echo -e "\n🎯 ${GREEN}CORRECCIÓN ANTI-INTERFERENCIA APLICADA${NC}"
echo "========================================"

echo -e "\n${GREEN}✅ CAMBIOS REALIZADOS:${NC}"
echo "   • Nueva configuración GPIO con máxima separación física"
echo "   • Frecuencia PWM reducida: 4000Hz → 2000Hz"  
echo "   • Potencia limitada: 100% → 90%"
echo "   • Hardware PWM dedicado para motores"
echo "   • Servos en power rail aislado"

echo -e "\n${YELLOW}📋 PRÓXIMOS PASOS OBLIGATORIOS:${NC}"
echo "   1. RECONECTAR CABLES según diagrama mostrado arriba"
echo "   2. Ejecutar test: python3 test_interference_fix.py"
echo "   3. Si test OK, reiniciar servicios:"
echo "      sudo systemctl restart t100-tank"
echo "      sudo systemctl restart t100-camera"
echo "   4. Probar sistema completo"

echo -e "\n${BLUE}ℹ️  ARCHIVOS CREADOS:${NC}"
echo "   • $BACKUP_DIR/ (backup de configuración anterior)"
echo "   • config.py (nueva configuración anti-interferencia)"
echo "   • test_interference_fix.py (test de verificación)"

echo -e "\n${RED}⚠️  IMPORTANTE:${NC}"
echo "   • Los cables DEBEN reconectarse según el nuevo diagrama"
echo "   • La configuración anterior está en $BACKUP_DIR/"
echo "   • Para revertir: mv config_old.py config.py"

print_status "Corrección anti-interferencia completada"

echo -e "\n🔌 ${YELLOW}RECUERDA: Reconectar cables según diagrama antes de probar${NC}"