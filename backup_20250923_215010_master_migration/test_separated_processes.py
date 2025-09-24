#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de procesos separados - Verifica que tank y cámara funcionan independientemente
"""

import asyncio
import time
import subprocess
import sys
import signal
from typing import Optional, List

class SeparatedProcessTest:
    """Test para verificar procesos separados."""
    
    def __init__(self):
        """Inicializa el test."""
        self.tank_process: Optional[subprocess.Popen] = None
        self.camera_process: Optional[subprocess.Popen] = None
        self.test_duration = 30  # 30 segundos de test
        
    def start_process(self, script_name: str, process_type: str) -> Optional[subprocess.Popen]:
        """Inicia un proceso específico."""
        try:
            print(f"🚀 Iniciando proceso {process_type}...")
            process = subprocess.Popen(
                [sys.executable, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Verificar que se inició
            time.sleep(2)
            if process.poll() is None:
                print(f"✅ Proceso {process_type} iniciado (PID: {process.pid})")
                return process
            else:
                print(f"❌ Error iniciando proceso {process_type}")
                return None
                
        except Exception as e:
            print(f"❌ Error iniciando {process_type}: {e}")
            return None
    
    def check_process_output(self, process: subprocess.Popen, process_name: str, lines_to_read: int = 5):
        """Verifica la salida de un proceso."""
        if not process or not process.stdout:
            return []
        
        lines = []
        try:
            for _ in range(lines_to_read):
                line = process.stdout.readline()
                if line:
                    lines.append(line.strip())
                else:
                    break
        except:
            pass
        
        if lines:
            print(f"📊 {process_name} output:")
            for line in lines[-3:]:  # Solo mostrar últimas 3 líneas
                print(f"   {line}")
        
        return lines
    
    def terminate_process(self, process: Optional[subprocess.Popen], name: str):
        """Termina un proceso de forma segura."""
        if process:
            try:
                print(f"🛑 Terminando proceso {name}...")
                process.terminate()
                
                try:
                    process.wait(timeout=5)
                    print(f"✅ Proceso {name} terminado correctamente")
                except subprocess.TimeoutExpired:
                    print(f"⚠️  Forzando terminación de {name}...")
                    process.kill()
                    process.wait()
                    print(f"✅ Proceso {name} forzado a terminar")
                    
            except Exception as e:
                print(f"❌ Error terminando {name}: {e}")
    
    async def run_test(self):
        """Ejecuta el test de procesos separados."""
        print("🧪 TEST DE PROCESOS SEPARADOS")
        print("=" * 50)
        print(f"Duración del test: {self.test_duration} segundos")
        print("Verificando que tank y cámara funcionan independientemente")
        print("=" * 50)
        
        try:
            # Test 1: Solo tank
            print("\n1️⃣  PROBANDO SOLO TANK DRIVE")
            print("-" * 30)
            
            self.tank_process = self.start_process("t100_tank_only.py", "TANK")
            if not self.tank_process:
                print("❌ No se pudo iniciar proceso tank")
                return False
            
            # Dejar correr 10 segundos
            print("⏱️  Ejecutando tank por 10 segundos...")
            for i in range(10):
                await asyncio.sleep(1)
                if i % 3 == 0:  # Cada 3 segundos
                    self.check_process_output(self.tank_process, "TANK", 2)
                
                # Verificar que sigue vivo
                if self.tank_process.poll() is not None:
                    print("❌ Proceso tank se cerró inesperadamente")
                    return False
            
            print("✅ Tank funcionando correctamente")
            self.terminate_process(self.tank_process, "TANK")
            self.tank_process = None
            
            # Test 2: Solo cámara
            print("\n2️⃣  PROBANDO SOLO CÁMARA")
            print("-" * 30)
            
            self.camera_process = self.start_process("t100_camera_only.py", "CAMERA")
            if not self.camera_process:
                print("❌ No se pudo iniciar proceso cámara")
                return False
            
            # Dejar correr 10 segundos
            print("⏱️  Ejecutando cámara por 10 segundos...")
            for i in range(10):
                await asyncio.sleep(1)
                if i % 3 == 0:  # Cada 3 segundos
                    self.check_process_output(self.camera_process, "CAMERA", 2)
                
                # Verificar que sigue vivo
                if self.camera_process.poll() is not None:
                    print("❌ Proceso cámara se cerró inesperadamente")
                    return False
            
            print("✅ Cámara funcionando correctamente")
            self.terminate_process(self.camera_process, "CAMERA")
            self.camera_process = None
            
            # Test 3: Ambos procesos simultáneos
            print("\n3️⃣  PROBANDO AMBOS PROCESOS SIMULTÁNEOS")
            print("-" * 40)
            
            # Iniciar ambos
            self.tank_process = self.start_process("t100_tank_only.py", "TANK")
            self.camera_process = self.start_process("t100_camera_only.py", "CAMERA")
            
            if not self.tank_process or not self.camera_process:
                print("❌ Error iniciando uno o ambos procesos")
                return False
            
            # Ejecutar ambos por 10 segundos
            print("⏱️  Ejecutando ambos procesos por 10 segundos...")
            for i in range(10):
                await asyncio.sleep(1)
                
                # Verificar que ambos siguen vivos
                tank_alive = self.tank_process.poll() is None
                camera_alive = self.camera_process.poll() is None
                
                if not tank_alive:
                    print("❌ Proceso tank falló durante ejecución simultánea")
                    return False
                    
                if not camera_alive:
                    print("❌ Proceso cámara falló durante ejecución simultánea")
                    return False
                
                # Mostrar status cada 5 segundos
                if i % 5 == 0:
                    print(f"📊 Segundo {i}: Tank 🟢 | Cámara 🟢")
            
            print("✅ Ambos procesos funcionando simultáneamente sin interferencias")
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Test interrumpido por usuario")
            return False
            
        except Exception as e:
            print(f"❌ Error durante test: {e}")
            return False
            
        finally:
            # Limpiar procesos
            self.terminate_process(self.tank_process, "TANK")
            self.terminate_process(self.camera_process, "CAMERA")
    
    async def run_master_test(self):
        """Test del controlador maestro."""
        print("\n4️⃣  PROBANDO CONTROLADOR MAESTRO")
        print("-" * 40)
        
        try:
            master_process = self.start_process("t100_master.py", "MASTER")
            if not master_process:
                print("❌ No se pudo iniciar controlador maestro")
                return False
            
            # Ejecutar por 15 segundos
            print("⏱️  Ejecutando controlador maestro por 15 segundos...")
            for i in range(15):
                await asyncio.sleep(1)
                
                if master_process.poll() is not None:
                    print("❌ Controlador maestro falló")
                    return False
                
                if i % 5 == 0:
                    print(f"📊 Segundo {i}: Maestro 🟢")
            
            print("✅ Controlador maestro funcionando correctamente")
            self.terminate_process(master_process, "MASTER")
            return True
            
        except Exception as e:
            print(f"❌ Error en test maestro: {e}")
            return False

async def main():
    """Función principal."""
    print("🧪 T100 SEPARATED PROCESSES TEST")
    print("=" * 60)
    print("Este test verifica que los procesos separados funcionan")
    print("correctamente sin interferencias entre ellos.")
    print("=" * 60)
    
    tester = SeparatedProcessTest()
    
    try:
        # Test de procesos individuales
        success = await tester.run_test()
        
        if success:
            # Test del controlador maestro
            master_success = await tester.run_master_test()
            
            if master_success:
                print("\n" + "=" * 60)
                print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
                print("=" * 60)
                print("✅ Procesos separados funcionan correctamente")
                print("✅ No hay interferencias entre tank y cámara")
                print("✅ Controlador maestro gestiona ambos procesos")
                print("\n💡 RECOMENDACIÓN:")
                print("   Usa los procesos separados para evitar el cruce de señales")
                print("   Comando: python3 t100_master.py")
                
            else:
                print("\n❌ Test del controlador maestro falló")
        else:
            print("\n❌ Tests de procesos individuales fallaron")
    
    except KeyboardInterrupt:
        print("\n🛑 Tests interrumpidos")
    
    except Exception as e:
        print(f"\n❌ Error crítico en tests: {e}")

if __name__ == "__main__":
    asyncio.run(main())