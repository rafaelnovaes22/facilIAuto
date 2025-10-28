#!/usr/bin/env python3
"""
Testar o classificador com casos específicos
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.car_classifier import classifier

# Casos de teste
test_cases = [
    # (nome, modelo, ano, categoria_esperada)
    # Ford Focus - casos especiais por ano
    ("Ford Focus", "Ford Focus", 2009, "Sedan"),
    ("Ford Focus", "Ford Focus", 2010, "Sedan"),
    ("Ford Focus", "Ford Focus", 2013, "Sedan"),
    ("Ford Focus", "Ford Focus", 2014, "Hatch"),  # Nova geração
    ("Ford Focus", "Ford Focus", 2015, "Hatch"),
    ("Ford Focus Sedan", "Ford Focus Sedan", 2015, "Sedan"),
    
    # Motos - devem ser detectadas
    ("Honda CB 500", "Honda CB 500", 2020, "Moto"),
    ("Yamaha MT-07", "Yamaha MT-07", 2021, "Moto"),
    ("Yamaha Xtz 250", "Yamaha Xtz 250", 2024, "Moto"),
    
    # Carros - não devem ser confundidos com motos
    ("Chevrolet Onix Mt", "Chevrolet Onix Mt", 2019, "Hatch"),  # MT = Manual
    ("Chevrolet Onix", "Chevrolet Onix", 2020, "Hatch"),
    ("Chevrolet Tracker", "Chevrolet Tracker", 2021, "SUV"),
    ("Toyota Corolla", "Toyota Corolla", 2020, "Sedan"),
]

print("=" * 80)
print("🧪 TESTE DO CLASSIFICADOR")
print("=" * 80)

passed = 0
failed = 0

for nome, modelo, ano, esperada in test_cases:
    resultado = classifier.classify(nome, modelo, ano)
    status = "✅" if resultado == esperada else "❌"
    
    if resultado == esperada:
        passed += 1
    else:
        failed += 1
    
    print(f"\n{status} {nome} ({ano})")
    print(f"   Esperado: {esperada}")
    print(f"   Obtido:   {resultado}")

print("\n" + "=" * 80)
print(f"Testes: {passed} ✅ | {failed} ❌")
print("=" * 80)
