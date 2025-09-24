#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Optimizador específico para el proceso T100 Camera Controller
Aplica configuraciones de sistema para minimizar interferencias
"""

import os
import sys
import subprocess
import psutil
import time

class CameraProcessOptimizer:
    """Optimizador para el proceso de cámara T100."""
    
    def __init__(self):
        """Inicializa el optimizador."""
        self.process_name = "t100_camera_only.py"
        self.target_nice = 5  # Prioridad más baja
        self.target_ionice_class = 2  # Best effort I/O
        self.target_ionice_priority = 4  # Baja prioridad I/O
        
    def find_camera_process(self):
        """Encuentra el proceso de cámara en ejecución."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any(self.process_name in arg for arg in proc.info['cmdline']):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def optimize_process_priority(self, process):
        """Optimiza la prioridad del proceso."""
        try:
            pid = process.pid
            
            # Ajustar prioridad CPU (nice)
            current_nice = process.nice()
            if current_nice != self.target_nice:
                process.nice(self.target_nice)
                print(f"✅ CPU nice ajustado: {current_nice} → {self.target_nice}")
            
            # Ajustar prioridad I/O (ionice)
            try:
                # Usar ionice directamente
                subprocess.run(['ionice', '-c', str(self.target_ionice_class), 
                              '-n', str(self.target_ionice_priority), '-p', str(pid)], 
                              check=True, capture_output=True)
                print(f"✅ I/O priority ajustada: Clase {self.target_ionice_class}, Prioridad {self.target_ionice_priority}")
            except subprocess.CalledProcessError:
                print("⚠️  No se pudo ajustar prioridad I/O (ionice no disponible)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error optimizando proceso: {e}")
            return False
    
    def set_cpu_affinity(self, process):
        """Establece afinidad de CPU para evitar conflictos."""
        try:
            # En Pi Zero 2W, usar solo los últimos cores para cámara
            available_cpus = list(range(psutil.cpu_count()))
            if len(available_cpus) > 2:
                # Reservar último CPU para cámara (menos carga)
                camera_cpus = [available_cpus[-1]]
                process.cpu_affinity(camera_cpus)
                print(f"✅ CPU affinity configurada: {camera_cpus}")
            else:
                print("ℹ️  CPU affinity no configurada (Pi Zero limitado)")
            
            return True
            
        except Exception as e:
            print(f"⚠️  No se pudo configurar CPU affinity: {e}")
            return False
    
    def optimize_system_settings(self):
        """Optimiza configuraciones del sistema."""
        optimizations = []
        
        try:
            # Reducir swappiness para evitar I/O de swap
            with open('/proc/sys/vm/swappiness', 'w') as f:
                f.write('10')
            optimizations.append("Swappiness reducido a 10")
        except:
            pass
        
        try:
            # Optimizar scheduler I/O
            io_schedulers = ['/sys/block/mmcblk0/queue/scheduler']  # SD card típica
            for scheduler_path in io_schedulers:
                if os.path.exists(scheduler_path):
                    with open(scheduler_path, 'w') as f:
                        f.write('deadline')
                    optimizations.append("I/O scheduler configurado a deadline")
                    break
        except:
            pass
        
        if optimizations:
            print("✅ Optimizaciones del sistema aplicadas:")
            for opt in optimizations:
                print(f"   - {opt}")
        
        return len(optimizations) > 0
    
    def monitor_performance(self, duration=30):
        """Monitorea el rendimiento del proceso."""
        process = self.find_camera_process()
        if not process:
            print("❌ Proceso de cámara no encontrado para monitoreo")
            return
        
        print(f"📊 Monitoreando rendimiento durante {duration}s...")
        
        start_time = time.time()
        samples = []
        
        while time.time() - start_time < duration:
            try:
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                samples.append({
                    'cpu': cpu_percent,
                    'memory': memory_mb,
                    'timestamp': time.time()
                })
                
                time.sleep(1)
                
            except psutil.NoSuchProcess:
                print("⚠️  Proceso terminado durante monitoreo")
                break
        
        if samples:
            avg_cpu = sum(s['cpu'] for s in samples) / len(samples)
            avg_memory = sum(s['memory'] for s in samples) / len(samples)
            max_cpu = max(s['cpu'] for s in samples)
            max_memory = max(s['memory'] for s in samples)
            
            print(f"\n📈 RESULTADOS DE RENDIMIENTO:")
            print(f"   CPU promedio: {avg_cpu:.1f}%")
            print(f"   CPU máximo: {max_cpu:.1f}%")
            print(f"   RAM promedio: {avg_memory:.1f} MB")
            print(f"   RAM máximo: {max_memory:.1f} MB")
            
            # Evaluar rendimiento
            if avg_cpu < 15 and max_cpu < 30:
                print("   ✅ Rendimiento CPU: EXCELENTE")
            elif avg_cpu < 25:
                print("   ✅ Rendimiento CPU: BUENO")
            else:
                print("   ⚠️  Rendimiento CPU: ALTO - Revisar optimizaciones")
            
            if avg_memory < 50:
                print("   ✅ Uso RAM: BAJO")
            elif avg_memory < 100:
                print("   ✅ Uso RAM: NORMAL")
            else:
                print("   ⚠️  Uso RAM: ALTO")
    
    def run_optimization(self):
        """Ejecuta la optimización completa."""
        print("🔧 T100 Camera Process Optimizer")
        print("=" * 40)
        
        process = self.find_camera_process()
        if not process:
            print("❌ El proceso de cámara no está ejecutándose")
            print("   Inicia el proceso primero: python3 t100_camera_only.py")
            return False
        
        print(f"✅ Proceso de cámara encontrado (PID: {process.pid})")
        
        # Aplicar optimizaciones
        success = True
        success &= self.optimize_process_priority(process)
        success &= self.set_cpu_affinity(process)
        
        # Optimizaciones del sistema (requiere sudo)
        if os.geteuid() == 0:
            self.optimize_system_settings()
        else:
            print("ℹ️  Ejecutar como sudo para optimizaciones adicionales del sistema")
        
        if success:
            print("\n✅ OPTIMIZACIÓN COMPLETADA")
            print("📊 El proceso de cámara está optimizado para no interferir")
            return True
        else:
            print("\n⚠️  OPTIMIZACIÓN PARCIAL")
            return False

def main():
    """Función principal."""
    optimizer = CameraProcessOptimizer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Solo monitorear
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        optimizer.monitor_performance(duration)
    else:
        # Optimizar
        if optimizer.run_optimization():
            print("\n🎯 RECOMENDACIONES:")
            print("1. El proceso de cámara ahora tiene prioridad más baja")
            print("2. No debería interferir con el tank drive")
            print("3. Monitorea con: python3 optimize_camera_process.py --monitor 60")
            print("4. Si aún hay problemas, considera reducir la frecuencia a 15Hz")

if __name__ == "__main__":
    main()