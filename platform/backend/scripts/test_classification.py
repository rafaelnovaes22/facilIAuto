"""
Script simples para testar classificação de veículos
"""

import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.car_classifier import CarClassifier


def test_classification():
    """Testar classificação de veículos"""
    
    classifier = CarClassifier()
    
    print("\n" + "="*80)
    print("TESTES DE CLASSIFICAÇÃO DE VEÍCULOS")
    print("="*80)
    
    # Casos de teste
    test_cases = [
        # (nome, modelo, ano, marca, esperado, descrição)
        ("Yamaha Xtz 250", "Xtz 250", 2024, "YAMAHA", "Moto", "Yamaha XTZ 250"),
        ("Yamaha Neo Automatic", "Neo Automatic", 2024, "YAMAHA", "Moto", "Yamaha Neo (scooter)"),
        ("Chevrolet Onix Mt", "Chevrolet Onix Mt", 2024, "Chevrolet", "Hatch", "Chevrolet Onix"),
        ("Toyota Prius Hybrid", "Toyota Prius Hybrid", 2024, "Toyota", "Hatch", "Toyota Prius"),
        ("Mitsubishi Asx Cvt", "Mitsubishi Asx Cvt", 2024, "Mitsubishi", "SUV", "Mitsubishi ASX"),
        ("Honda Civic 2.0 EX", "Civic", 2024, "Honda", "Sedan", "Honda Civic"),
        ("Honda Fit 1.5", "Fit", 2024, "Honda", "Hatch", "Honda Fit"),
        ("Chevrolet Tracker T", "Chevrolet Tracker T", 2025, "Chevrolet", "SUV", "Chevrolet Tracker"),
        ("Toyota Corolla Gli", "Toyota Corolla Gli", 2022, "Toyota", "Sedan", "Toyota Corolla"),
        ("Fiat Strada Volcano", "Fiat Strada Volcano", 2025, "Fiat", "Pickup", "Fiat Strada"),
        ("Volkswagen Gol 1.0", "Gol", 2020, "Volkswagen", "Hatch", "VW Gol"),
        ("Renault Kwid Zen", "Renault Kwid Zen", 2025, "Renault", "Compacto", "Renault Kwid"),
        ("Honda CB 500", "CB 500", 2024, "Honda", "Moto", "Honda CB (moto)"),
        ("Kawasaki Ninja 400", "Ninja 400", 2024, "Kawasaki", "Moto", "Kawasaki Ninja"),
    ]
    
    passed = 0
    failed = 0
    
    for nome, modelo, ano, marca, esperado, descricao in test_cases:
        resultado = classifier.classify(nome=nome, modelo=modelo, ano=ano, marca=marca)
        
        if resultado == esperado:
            print(f"✅ {descricao}: {resultado}")
            passed += 1
        else:
            print(f"❌ {descricao}: esperado '{esperado}', obteve '{resultado}'")
            failed += 1
    
    print("\n" + "="*80)
    print(f"RESULTADO: {passed} passaram, {failed} falharam")
    print("="*80)
    
    return failed == 0


if __name__ == '__main__':
    success = test_classification()
    sys.exit(0 if success else 1)
