#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test completo del T100 API Controller
Verifica todos los endpoints y funcionalidades
"""

import requests
import time
import json
import sys
from urllib.parse import urljoin

class T100APITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 5
        
    def print_status(self, message, status="INFO"):
        symbols = {"INFO": "ℹ️", "OK": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{symbols.get(status, 'ℹ️')} {message}")
        
    def test_endpoint(self, endpoint, method="GET", data=None):
        """Test individual endpoint"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            else:
                self.print_status(f"Método no soportado: {method}", "ERROR")
                return False
                
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    self.print_status(f"{method} {endpoint} - OK", "OK")
                    print(f"   Respuesta: {json.dumps(json_data, indent=2)}")
                    return True
                except json.JSONDecodeError:
                    self.print_status(f"{method} {endpoint} - Respuesta no JSON", "WARNING")
                    return False
            else:
                self.print_status(f"{method} {endpoint} - HTTP {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_status(f"No se puede conectar a {url}", "ERROR")
            return False
        except requests.exceptions.Timeout:
            self.print_status(f"Timeout en {endpoint}", "ERROR")
            return False
        except Exception as e:
            self.print_status(f"Error en {endpoint}: {e}", "ERROR")
            return False
    
    def test_control_sequence(self):
        """Test secuencia de control"""
        self.print_status("Probando secuencia de control...", "INFO")
        
        movements = [
            {"x": 0.0, "y": 0.0, "desc": "Centro"},
            {"x": 0.0, "y": 0.5, "desc": "Adelante"},
            {"x": 0.0, "y": -0.5, "desc": "Atrás"},
            {"x": 0.5, "y": 0.0, "desc": "Derecha"},
            {"x": -0.5, "y": 0.0, "desc": "Izquierda"},
            {"x": 0.0, "y": 0.0, "desc": "Centro (stop)"}
        ]
        
        success_count = 0
        
        for movement in movements:
            data = {
                "x": movement["x"],
                "y": movement["y"],
                "timestamp": int(time.time() * 1000)
            }
            
            print(f"   🎮 {movement['desc']}: x={movement['x']}, y={movement['y']}")
            
            if self.test_endpoint("/api/control", "POST", data):
                success_count += 1
            
            time.sleep(0.5)  # Pausa entre movimientos
        
        return success_count == len(movements)
    
    def test_latency(self, count=10):
        """Test de latencia"""
        self.print_status(f"Midiendo latencia ({count} requests)...", "INFO")
        
        latencies = []
        
        for i in range(count):
            start_time = time.time()
            
            try:
                response = self.session.get(urljoin(self.base_url, "/api/status"))
                if response.status_code == 200:
                    latency = (time.time() - start_time) * 1000
                    latencies.append(latency)
                    print(f"   Request {i+1}: {latency:.2f}ms")
                else:
                    print(f"   Request {i+1}: ERROR {response.status_code}")
            except Exception as e:
                print(f"   Request {i+1}: ERROR {e}")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            self.print_status(f"Latencia promedio: {avg_latency:.2f}ms", "OK")
            self.print_status(f"Latencia mínima: {min_latency:.2f}ms", "INFO")
            self.print_status(f"Latencia máxima: {max_latency:.2f}ms", "INFO")
            
            return avg_latency < 100  # Considerar OK si < 100ms
        
        return False
    
    def run_full_test(self):
        """Ejecutar test completo"""
        print("🧪 T100 API Controller - Test Completo")
        print("=" * 50)
        
        # Test básico de conexión
        self.print_status(f"Probando conexión a {self.base_url}", "INFO")
        
        # Test de endpoints básicos
        endpoints = [
            ("/api/status", "GET"),
            ("/api/config", "GET"),
            ("/api/motors/status", "GET")
        ]
        
        basic_tests_passed = 0
        for endpoint, method in endpoints:
            if self.test_endpoint(endpoint, method):
                basic_tests_passed += 1
        
        print()
        
        # Test de control
        control_test_passed = self.test_control_sequence()
        print()
        
        # Test de parada de emergencia
        emergency_test_passed = self.test_endpoint("/api/emergency/stop", "POST")
        print()
        
        # Test de latencia
        latency_test_passed = self.test_latency()
        print()
        
        # Resumen
        print("📊 Resumen del Test")
        print("-" * 30)
        print(f"Tests básicos: {basic_tests_passed}/{len(endpoints)}")
        print(f"Test de control: {'✅' if control_test_passed else '❌'}")
        print(f"Test de emergencia: {'✅' if emergency_test_passed else '❌'}")
        print(f"Test de latencia: {'✅' if latency_test_passed else '❌'}")
        
        total_score = basic_tests_passed + sum([
            control_test_passed,
            emergency_test_passed, 
            latency_test_passed
        ])
        
        total_tests = len(endpoints) + 3
        
        print(f"\n🎯 Puntuación total: {total_score}/{total_tests}")
        
        if total_score == total_tests:
            self.print_status("¡Todos los tests pasaron! 🎉", "OK")
            return True
        elif total_score >= total_tests * 0.7:
            self.print_status("La mayoría de tests pasaron ⚠️", "WARNING")
            return False
        else:
            self.print_status("Múltiples tests fallaron ❌", "ERROR")
            return False

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print(f"🔍 Probando T100 API en: {base_url}")
    print()
    
    tester = T100APITester(base_url)
    success = tester.run_full_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
