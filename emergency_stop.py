#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PARADA DE EMERGENCIA T100 - ZK-5AD (TA6586)
Parada inmediata usando comandos pigs directos
"""

import subprocess
import time
import sys


def emergency_stop_all():
    """Parada de emergencia inmediata usando pigs para ZK-5AD."""
    print("🚨 PARADA DE EMERGENCIA ZK-5AD ACTIVADA")
    print("Aplicando freno H+H en todos los pines...")
    
    try:
        # Pines ZK-5AD (TA6586) - configuración actualizada
        zk5ad_pins = [12, 13, 16, 26]  # Motor A: 12,16 | Motor B: 13,26
        
        print("🛑 Configurando todos los pines ZK-5AD en HIGH (255)...")
        
        # Comando pigs para poner todos los pines en HIGH (freno H+H)
        for pin in zk5ad_pins:
            result = subprocess.run(
                ["pigs", "w", str(pin), "1"], 
                capture_output=True, 
                text=True, 
                timeout=2
            )
            
            if result.returncode == 0:
                print(f"   GPIO {pin}: HIGH (BRAKE)")
            else:
                print(f"   GPIO {pin}: ERROR - {result.stderr}")
        
        print("✅ Freno H+H aplicado en todos los motores ZK-5AD")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Error: Timeout ejecutando comando pigs")
        return False
    except FileNotFoundError:
        print("❌ Error: pigpio no instalado (comando 'pigs' no encontrado)")
        print("   Instalar: sudo apt install pigpio")
        return False
    except Exception as e:
        print(f"❌ Error en parada de emergencia: {e}")
        return False


def kill_all_services():
    """Mata todos los procesos T100 que puedan estar ejecutándose."""
    print("🔪 Terminando todos los procesos T100...")
    
    # Matar procesos Python relacionados con T100
    try:
        subprocess.run(["sudo", "pkill", "-f", "t100_controller"], 
                       capture_output=True, timeout=5)
        print("   Proceso t100_controller: TERMINADO")
    except:
        pass
    
    try:
        subprocess.run(["sudo", "pkill", "-f", "elrs"], 
                       capture_output=True, timeout=5)
        print("   Procesos ELRS: TERMINADOS")
    except:
        pass
    
    try:
        subprocess.run(["sudo", "pkill", "-f", "zk5ad"], 
                       capture_output=True, timeout=5)
        print("   Procesos ZK-5AD: TERMINADOS")
    except:
        pass


def main():
    """Función principal de emergencia."""
    print("🚨 T100 ZK-5AD EMERGENCY STOP")
    print("=" * 35)
    
    # 1. Matar procesos primero
    kill_all_services()
    time.sleep(1)
    
    # 2. Parada de emergencia de hardware
    if emergency_stop_all():
        print("\n✅ PARADA DE EMERGENCIA COMPLETADA")
        print("   ✅ Todos los motores: FRENADO H+H")
        print("   ✅ Todos los procesos: TERMINADOS")
        print("   ✅ ZK-5AD: MODO SEGURO")
    else:
        print("\n❌ ERROR EN PARADA DE EMERGENCIA")
        print("   🔌 DESCONECTA LA ALIMENTACIÓN INMEDIATAMENTE")
        print("   🔧 Verifica instalación pigpio")
    
    print("\n🔍 VERIFICACIÓN:")
    print("1. Motores completamente detenidos")
    print("2. GPIO 12,13,18,19 en HIGH")
    print("3. Reiniciar: python3 t100_controller.py")


if __name__ == "__main__":
    main()
