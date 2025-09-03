#!/usr/bin/env python3

# Test de importaciones para verificar que funcionen correctamente

try:
    print("Probando importación de simple_resource_monitor...")
    from src.utils.simple_resource_monitor import SimpleResourceMonitor
    print("✅ SimpleResourceMonitor importado correctamente")
    
    # Crear instancia para verificar
    monitor = SimpleResourceMonitor()
    print("✅ Instancia creada correctamente")
    
    # Obtener stats iniciales
    stats = monitor.get_stats()
    print(f"✅ Stats obtenidos: {stats}")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")

try:
    print("\nProbando importación de flask_app_optimized...")
    from src.web.flask_app_optimized import create_optimized_app
    print("✅ flask_app_optimized importado correctamente")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")

print("\nTest completado.")
