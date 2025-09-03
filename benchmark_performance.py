#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Benchmark y test de rendimiento para la aplicación optimizada.
"""

import time
import gc
import tracemalloc
import threading
from typing import Dict, List, Tuple

def memory_benchmark():
    """Prueba de uso de memoria."""
    print("🧠 Benchmark de memoria...")
    
    # Iniciar trazado de memoria
    tracemalloc.start()
    
    # Simular carga de módulos
    try:
        from src.config.settings import DEFAULT_CONFIG
        from src.hardware.l298n_driver_optimized import L298NControllerOptimized
        from src.control.joystick_controller_optimized import JoystickControllerOptimized
        
        snapshot1 = tracemalloc.take_snapshot()
        
        # Simular creación de objetos (sin hardware real)
        config = DEFAULT_CONFIG
        
        snapshot2 = tracemalloc.take_snapshot()
        
        # Mostrar diferencias
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        print("📊 Top 5 incrementos de memoria:")
        for index, stat in enumerate(top_stats[:5], 1):
            print(f"{index}. {stat}")
        
        # Memoria total
        current, peak = tracemalloc.get_traced_memory()
        print(f"💾 Memoria actual: {current / 1024 / 1024:.1f} MB")
        print(f"💾 Pico de memoria: {peak / 1024 / 1024:.1f} MB")
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
    finally:
        tracemalloc.stop()

def cpu_benchmark():
    """Prueba de uso de CPU."""
    print("\n⚡ Benchmark de CPU...")
    
    # Test de procesamiento de joystick
    start_time = time.time()
    iterations = 10000
    
    for i in range(iterations):
        # Simular procesamiento de joystick
        x = (i % 200 - 100) / 100.0  # -1.0 a 1.0
        y = ((i * 7) % 200 - 100) / 100.0  # -1.0 a 1.0
        
        # Aplicar deadzone simulada
        if abs(x) < 0.1:
            x = 0.0
        if abs(y) < 0.1:
            y = 0.0
        
        # Mezcla diferencial simulada
        left = y - x
        right = y + x
        
        # Normalización
        max_val = max(abs(left), abs(right))
        if max_val > 1.0:
            left /= max_val
            right /= max_val
    
    end_time = time.time()
    processing_time = end_time - start_time
    ops_per_second = iterations / processing_time
    
    print(f"🔢 Procesadas {iterations} iteraciones en {processing_time:.3f}s")
    print(f"🚀 Velocidad: {ops_per_second:.0f} operaciones/segundo")
    print(f"⏱️  Tiempo por operación: {processing_time*1000/iterations:.3f}ms")

def websocket_simulation():
    """Simula carga de WebSocket."""
    print("\n🌐 Simulación de WebSocket...")
    
    messages_sent = 0
    errors = 0
    start_time = time.time()
    
    def simulate_client():
        nonlocal messages_sent, errors
        for i in range(100):
            try:
                # Simular envío de datos de joystick
                data = f'{{"x": {(i%20-10)/10}, "y": {((i*3)%20-10)/10}}}'
                
                # Simular procesamiento
                time.sleep(0.01)  # 100 Hz
                messages_sent += 1
                
            except Exception:
                errors += 1
    
    # Simular múltiples clientes
    threads = []
    for i in range(3):  # 3 clientes simultáneos
        thread = threading.Thread(target=simulate_client)
        threads.append(thread)
        thread.start()
    
    # Esperar que terminen
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"📨 Mensajes procesados: {messages_sent}")
    print(f"❌ Errores: {errors}")
    print(f"⏱️  Tiempo total: {total_time:.2f}s")
    print(f"🚀 Mensajes/segundo: {messages_sent/total_time:.1f}")

def garbage_collection_test():
    """Test de recolección de basura."""
    print("\n🗑️  Test de garbage collection...")
    
    # Crear muchos objetos
    objects = []
    start_time = time.time()
    
    for i in range(1000):
        objects.append({
            'id': i,
            'data': f"test_data_{i}" * 10,
            'nested': {'value': i * 2}
        })
    
    creation_time = time.time() - start_time
    
    # Forzar recolección
    gc_start = time.time()
    collected = gc.collect()
    gc_time = time.time() - gc_start
    
    # Limpiar objetos
    del objects
    
    final_gc_start = time.time()
    final_collected = gc.collect()
    final_gc_time = time.time() - final_gc_start
    
    print(f"⏱️  Creación de 1000 objetos: {creation_time:.3f}s")
    print(f"🧹 Primera GC: {collected} objetos en {gc_time:.3f}s")
    print(f"🧹 GC final: {final_collected} objetos en {final_gc_time:.3f}s")

def run_all_benchmarks():
    """Ejecuta todos los benchmarks."""
    print("🚀 Iniciando benchmarks de rendimiento...")
    print("=" * 50)
    
    start_total = time.time()
    
    try:
        memory_benchmark()
        cpu_benchmark()
        websocket_simulation()
        garbage_collection_test()
        
    except Exception as e:
        print(f"❌ Error en benchmark: {e}")
        import traceback
        traceback.print_exc()
    
    total_time = time.time() - start_total
    
    print("\n" + "=" * 50)
    print(f"✅ Benchmarks completados en {total_time:.2f}s")
    print("\n💡 Recomendaciones:")
    print("   • Ejecutar 'sudo nice -n -10 python3 motor_control_optimized.py' para mayor prioridad")
    print("   • Monitorear recursos con 'monitor_resources.sh'")
    print("   • Verificar temperatura del sistema regularmente")

if __name__ == '__main__':
    run_all_benchmarks()
