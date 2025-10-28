#!/usr/bin/env python3
"""
Validação rápida do classificador
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.car_classifier import classifier

def validate():
    """Validar casos críticos"""
    
    print("=" * 80)
    print("✅ VALIDAÇÃO DO CLASSIFICADOR")
    print("=" * 80)
    
    tests = [
        # (nome, modelo, ano, esperado, descrição)
        ("Ford Focus", "Ford Focus", 2009, "Sedan", "Focus 2009 = Sedan"),
        ("Ford Focus", "Ford Focus", 2014, "Hatch", "Focus 2014+ = Hatch"),
        ("Honda CB 500", "Honda CB 500", 2020, "Moto", "Honda CB = Moto"),
        ("Yamaha MT-07", "Yamaha MT-07", 2021, "Moto", "Yamaha MT = Moto"),
        ("Yamaha Xtz 250", "Yamaha Xtz 250", 2024, "Moto", "Yamaha XTZ = Moto"),
        ("Chevrolet Onix Mt", "Chevrolet Onix Mt", 2019, "Hatch", "Onix MT ≠ Moto"),
        ("Chevrolet Tracker", "Chevrolet Tracker", 2021, "SUV", "Tracker = SUV"),
        ("Toyota Corolla", "Toyota Corolla", 2020, "Sedan", "Corolla = Sedan"),
    ]
    
    passed = 0
    failed = 0
    
    for nome, modelo, ano, esperado, desc in tests:
        resultado = classifier.classify(nome, modelo, ano)
        ok = resultado == esperado
        
        if ok:
            passed += 1
            print(f"✅ {desc}")
        else:
            failed += 1
            print(f"❌ {desc}")
            print(f"   Esperado: {esperado}, Obtido: {resultado}")
    
    print("\n" + "=" * 80)
    if failed == 0:
        print(f"🎉 TODOS OS {passed} TESTES PASSARAM!")
        print("=" * 80)
        return True
    else:
        print(f"⚠️  {failed} TESTES FALHARAM de {passed + failed}")
        print("=" * 80)
        return False

if __name__ == '__main__':
    success = validate()
    sys.exit(0 if success else 1)
