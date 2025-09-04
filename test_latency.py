#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de latencia ultra-rápido para T100 Controller
Mide la responsividad del joystick en tiempo real
"""

import asyncio
import aiohttp
import time
import json
import sys
import statistics

class UltraLatencyTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
        
    async def __aenter__(self):
        # Configurar sesión HTTP optimizada para velocidad
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=100,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=1, connect=0.5)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_control_command(self, x, y):
        """Enviar comando de control y medir latencia"""
        start_time = time.perf_counter()
        
        try:
            data = {
                'x': x,
                'y': y,
                'timestamp': int(time.time() * 1000)
            }
            
            async with self.session.post(f'{self.base_url}/api/control', 
                                       json=data) as response:
                await response.json()
                end_time = time.perf_counter()
                
                latency_ms = (end_time - start_time) * 1000
                return latency_ms, response.status == 200
                
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            return latency_ms, False
    
    async def test_continuous_joystick(self, duration_seconds=10):
        """Test continuo de joystick simulando movimiento real"""
        print(f"🎮 Iniciando test continuo por {duration_seconds} segundos...")
        print("   Simulando movimientos de joystick a 60 FPS")
        
        latencies = []
        success_count = 0
        total_count = 0
        
        start_time = time.time()
        frame_time = 1.0 / 60.0  # 60 FPS
        
        while time.time() - start_time < duration_seconds:
            frame_start = time.time()
            
            # Simular movimiento circular del joystick
            t = time.time() - start_time
            x = 0.5 * time.cos(t * 2)  # Movimiento circular
            y = 0.5 * time.sin(t * 2)
            
            # Enviar comando
            latency, success = await self.send_control_command(x, y)
            
            latencies.append(latency)
            if success:
                success_count += 1
            total_count += 1
            
            # Mostrar progreso cada segundo
            if total_count % 60 == 0:
                avg_latency = statistics.mean(latencies[-60:])
                success_rate = (success_count / total_count) * 100
                print(f"   {total_count//60}s - Latencia promedio: {avg_latency:.1f}ms - Éxito: {success_rate:.1f}%")
            
            # Mantener 60 FPS
            elapsed = time.time() - frame_start
            if elapsed < frame_time:
                await asyncio.sleep(frame_time - elapsed)
        
        return latencies, success_count, total_count
    
    async def test_burst_performance(self, burst_size=100):
        """Test de ráfaga para medir capacidad máxima"""
        print(f"⚡ Test de ráfaga: {burst_size} comandos simultáneos...")
        
        start_time = time.perf_counter()
        
        # Crear tareas concurrentes
        tasks = []
        for i in range(burst_size):
            x = (i % 100) / 100.0 - 0.5  # Variación de -0.5 a 0.5
            y = ((i * 37) % 100) / 100.0 - 0.5  # Patrón pseudo-aleatorio
            task = self.send_control_command(x, y)
            tasks.append(task)
        
        # Ejecutar todas las tareas
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        
        # Analizar resultados
        latencies = []
        success_count = 0
        
        for result in results:
            if isinstance(result, tuple):
                latency, success = result
                latencies.append(latency)
                if success:
                    success_count += 1
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            print(f"   Tiempo total: {total_time:.1f}ms")
            print(f"   Comandos exitosos: {success_count}/{burst_size}")
            print(f"   Latencia promedio: {avg_latency:.1f}ms")
            print(f"   Latencia mínima: {min_latency:.1f}ms")
            print(f"   Latencia máxima: {max_latency:.1f}ms")
            print(f"   Throughput: {(success_count / total_time) * 1000:.1f} cmd/s")
        
        return latencies, success_count
    
    async def run_full_test(self):
        """Ejecutar suite completa de tests de latencia"""
        print("🚀 T100 Ultra-Latency Test Suite")
        print("=" * 50)
        
        # Test de conexión básica
        print("🔍 Verificando conexión...")
        try:
            async with self.session.get(f'{self.base_url}/api/status') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Conectado a {data.get('controller', 'T100')}")
                else:
                    print(f"   ❌ Error de conexión: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"   ❌ No se puede conectar: {e}")
            return False
        
        print()
        
        # Test de latencia individual
        print("📏 Test de latencia individual...")
        latency, success = await self.send_control_command(0.0, 0.0)
        if success:
            print(f"   ✅ Latencia: {latency:.2f}ms")
        else:
            print(f"   ❌ Error en comando individual")
        
        print()
        
        # Test continuo
        continuous_latencies, continuous_success, continuous_total = await self.test_continuous_joystick(5)
        
        print()
        
        # Test de ráfaga
        burst_latencies, burst_success = await self.test_burst_performance(50)
        
        print()
        
        # Resumen final
        print("📊 Resumen Final")
        print("-" * 30)
        
        if continuous_latencies:
            avg_continuous = statistics.mean(continuous_latencies)
            print(f"Latencia promedio continua: {avg_continuous:.1f}ms")
            
            # Clasificar rendimiento
            if avg_continuous < 10:
                print("🟢 EXCELENTE - Ultra-responsivo")
            elif avg_continuous < 20:
                print("🟡 BUENO - Responsivo")
            elif avg_continuous < 50:
                print("🟠 ACEPTABLE - Levemente perceptible")
            else:
                print("🔴 LENTO - Necesita optimización")
        
        success_rate = (continuous_success / continuous_total) * 100 if continuous_total > 0 else 0
        print(f"Tasa de éxito: {success_rate:.1f}%")
        
        return success_rate > 95 and (statistics.mean(continuous_latencies) if continuous_latencies else 100) < 30

async def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print(f"🎯 Probando ultra-latencia en: {base_url}")
    print()
    
    async with UltraLatencyTester(base_url) as tester:
        success = await tester.run_full_test()
        
        if success:
            print("\n🎉 ¡Test de ultra-latencia EXITOSO!")
        else:
            print("\n⚠️ Test completado con observaciones")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
