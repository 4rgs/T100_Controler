#!/usr/bin/env python3
"""
Script de validación para giros invertidos
"""

# Simular la lógica de mezcla diferencial
def test_differential_mix(x, y, invert_turn=False, turn_factor=1.0):
    """Simula la lógica de mezcla diferencial"""
    
    # Aplicar factor de giro
    x *= turn_factor
    
    # Invertir dirección de giro si está configurado
    if invert_turn:
        x = -x
    
    # Calcular velocidades de ruedas
    left = y - x
    right = y + x
    
    # Normalizar si alguna velocidad excede 1.0
    max_value = max(abs(left), abs(right))
    if max_value > 1.0:
        left /= max_value
        right /= max_value
    
    return left, right

def test_movements():
    """Prueba diferentes movimientos para validar la lógica"""
    
    print("🧪 VALIDACIÓN DE LÓGICA DE GIROS")
    print("="*50)
    print()
    
    test_cases = [
        (0.0, 1.0, "Adelante"),
        (0.0, -1.0, "Atrás"),
        (1.0, 0.0, "Giro Derecha (en el lugar)"),
        (-1.0, 0.0, "Giro Izquierda (en el lugar)"),
        (0.5, 0.5, "Adelante + Giro Derecha"),
        (-0.5, 0.5, "Adelante + Giro Izquierda"),
        (0.5, -0.5, "Atrás + Giro Derecha"),
        (-0.5, -0.5, "Atrás + Giro Izquierda"),
    ]
    
    print("CONFIGURACIÓN ORIGINAL (invert_turn=False):")
    print("-" * 45)
    for x, y, desc in test_cases:
        left, right = test_differential_mix(x, y, invert_turn=False)
        direction = ""
        if left > right:
            direction = "→ Gira DERECHA"
        elif right > left:
            direction = "→ Gira IZQUIERDA"
        elif left == right and left > 0:
            direction = "→ Adelante"
        elif left == right and left < 0:
            direction = "→ Atrás"
        else:
            direction = "→ Parado"
            
        print(f"{desc:25s} -> L:{left:6.2f} R:{right:6.2f} {direction}")
    
    print("\n" + "="*50)
    print("CONFIGURACIÓN CORREGIDA (invert_turn=True):")
    print("-" * 45)
    for x, y, desc in test_cases:
        left, right = test_differential_mix(x, y, invert_turn=True)
        direction = ""
        if left > right:
            direction = "→ Gira DERECHA"
        elif right > left:
            direction = "→ Gira IZQUIERDA"
        elif left == right and left > 0:
            direction = "→ Adelante"
        elif left == right and left < 0:
            direction = "→ Atrás"
        else:
            direction = "→ Parado"
            
        print(f"{desc:25s} -> L:{left:6.2f} R:{right:6.2f} {direction}")
    
    print("\n" + "="*50)
    print("🎯 ANÁLISIS:")
    print()
    print("Si el problema era que giros estaban invertidos:")
    print("• Joystick derecha debería girar a la DERECHA")
    print("• Joystick izquierda debería girar a la IZQUIERDA")
    print()
    print("Con invert_turn=True:")
    print("• Giro Derecha: Motor izq > Motor der (correcto)")
    print("• Giro Izquierda: Motor der > Motor izq (correcto)")
    print()
    print("✅ La configuración invert_turn_direction=True")
    print("   debería corregir el problema de giros invertidos.")

if __name__ == "__main__":
    test_movements()
