#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de conversión de valores raw ELRS
Verifica que la conversión de valores raw a flotantes funcione correctamente
"""

def raw_to_float(raw_value: int) -> float:
    """
    Convierte valor raw del ELRS a rango -1.0 a 1.0 usando rango completo.
    
    Args:
        raw_value: Valor raw del ELRS (172-1811)
        
    Returns:
        Valor flotante en rango -1.0 a 1.0
        - 172 (mínimo) -> -1.0 (máximo PWM reversa)
        - 992 (centro) -> 0.0 (parado)
        - 1811 (máximo) -> +1.0 (máximo PWM adelante)
    """
    # Definir rangos del ELRS
    min_value = 172
    max_value = 1811
    
    # Mapear todo el rango (172-1811) a (-1.0 a +1.0)
    # Normalizar primero a 0.0-1.0, luego a -1.0/+1.0
    normalized = (raw_value - min_value) / (max_value - min_value)  # 0.0 - 1.0
    mapped = (normalized * 2.0) - 1.0  # -1.0 - +1.0
    
    # Limitar rango por seguridad
    return max(-1.0, min(1.0, mapped))

def test_conversion():
    """Test de la conversión de valores raw."""
    print("🧪 Test de conversión valores raw ELRS")
    print("=" * 50)
    
    # Valores de test con el nuevo mapeo completo
    test_values = [
        (172, "Mínimo", -1.0),        # Máximo PWM reversa
        (582, "25%", -0.5),           # PWM medio reversa
        (992, "Centro", 0.0),         # Parado
        (1401, "75%", 0.5),           # PWM medio adelante
        (1811, "Máximo", 1.0),        # Máximo PWM adelante
        (332, "10%", -0.8),           # PWM alto reversa
        (1651, "90%", 0.8),           # PWM alto adelante
    ]
    
    print("Raw Value | Descripción | Convertido | Esperado | Diferencia")
    print("-" * 60)
    
    for raw, desc, expected in test_values:
        converted = raw_to_float(raw)
        difference = abs(converted - expected)
        status = "✅" if difference < 0.05 else "⚠️"
        
        print(f"{raw:8d} | {desc:11s} | {converted:+8.3f} | {expected:+8.3f} | {difference:8.3f} {status}")
    
    print("\n✅ Test completado")
    print("📝 Los valores convertidos deberían estar en rango [-1.0, 1.0]")

if __name__ == "__main__":
    test_conversion()