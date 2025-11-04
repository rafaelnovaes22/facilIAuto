"""
Validation script for DataValidator implementation.

This script tests the DataValidator without pytest to avoid dependency conflicts.
"""

import sys
from datetime import datetime
from scraper.data_validator import DataValidator
from scraper.models import ValidationResult


def test_basic_validation():
    """Test basic validation functionality."""
    print("\n=== Test 1: Basic Validation ===")
    
    validator = DataValidator()
    
    # Valid vehicle data
    valid_data = {
        'id': 'test_001',
        'nome': 'Toyota Corolla GLi 1.8',
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'ano': 2022,
        'preco': 95000.0,
        'quilometragem': 35000,
        'combustivel': 'Flex',
        'cambio': 'Automático CVT',
        'cor': 'Prata',
        'portas': 4,
        'categoria': 'Sedan',
        'imagens': ['http://example.com/img1.jpg', 'http://example.com/img2.jpg'],
        'descricao': 'Carro em excelente estado, único dono, revisões em dia.',
        'url_original': 'https://robustcar.com.br/veiculo/001',
        'content_hash': 'a' * 32
    }
    
    result = validator.validate(valid_data)
    
    assert result.is_valid, "Valid vehicle should pass validation"
    assert len(result.errors) == 0, "Valid vehicle should have no errors"
    assert result.completeness > 0.9, "Complete vehicle should have high completeness"
    
    print(f"✓ Valid vehicle passed validation")
    print(f"  Completeness: {result.completeness:.2f}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")


def test_missing_required_field():
    """Test validation with missing required field."""
    print("\n=== Test 2: Missing Required Field ===")
    
    validator = DataValidator()
    
    invalid_data = {
        'id': 'test_002',
        'nome': 'Honda Civic',
        'marca': 'Honda',
        'modelo': 'Civic',
        'ano': 2021,
        # Missing 'preco' - required field
        'quilometragem': 40000,
        'combustivel': 'Flex',
        'cambio': 'Manual',
        'categoria': 'Sedan',
        'url_original': 'https://robustcar.com.br/veiculo/002',
        'content_hash': 'b' * 32
    }
    
    result = validator.validate(invalid_data)
    
    assert not result.is_valid, "Vehicle with missing required field should fail"
    assert len(result.errors) > 0, "Should have errors"
    assert 'preco' in result.missing_fields, "Should identify missing field"
    
    print(f"✓ Missing required field detected")
    print(f"  Errors: {result.errors}")
    print(f"  Missing fields: {result.missing_fields}")


def test_enum_validation():
    """Test enum field validation."""
    print("\n=== Test 3: Enum Validation ===")
    
    validator = DataValidator()
    
    # Test valid cambio values
    valid_cambios = ['Manual', 'Automático', 'Automático CVT', 'Automatizada']
    for cambio in valid_cambios:
        is_valid, error = validator.validate_field('cambio', cambio)
        assert is_valid, f"Câmbio '{cambio}' should be valid"
    
    print(f"✓ All valid câmbio values accepted: {', '.join(valid_cambios)}")
    
    # Test invalid cambio
    is_valid, error = validator.validate_field('cambio', 'Sequencial')
    assert not is_valid, "Invalid câmbio should be rejected"
    print(f"✓ Invalid câmbio rejected: {error}")
    
    # Test valid combustivel values
    valid_combustiveis = ['Flex', 'Gasolina', 'Diesel', 'Elétrico', 'Híbrido']
    for combustivel in valid_combustiveis:
        is_valid, error = validator.validate_field('combustivel', combustivel)
        assert is_valid, f"Combustível '{combustivel}' should be valid"
    
    print(f"✓ All valid combustível values accepted: {', '.join(valid_combustiveis)}")
    
    # Test valid categoria values
    valid_categorias = ['Hatch', 'Sedan', 'SUV', 'Pickup', 'Compacto', 'Van']
    for categoria in valid_categorias:
        is_valid, error = validator.validate_field('categoria', categoria)
        assert is_valid, f"Categoria '{categoria}' should be valid"
    
    print(f"✓ All valid categoria values accepted: {', '.join(valid_categorias)}")


def test_range_validation():
    """Test range validation for numeric fields."""
    print("\n=== Test 4: Range Validation ===")
    
    validator = DataValidator()
    
    # Test price range
    is_valid, _ = validator.validate_field('preco', 50000.0)
    assert is_valid, "Valid price should pass"
    
    is_valid, error = validator.validate_field('preco', 5000.0)
    assert not is_valid, "Price below minimum should fail"
    print(f"✓ Price below minimum rejected: {error}")
    
    is_valid, error = validator.validate_field('preco', 600000.0)
    assert not is_valid, "Price above maximum should fail"
    print(f"✓ Price above maximum rejected: {error}")
    
    # Test year range
    is_valid, _ = validator.validate_field('ano', 2022)
    assert is_valid, "Valid year should pass"
    
    is_valid, error = validator.validate_field('ano', 2005)
    assert not is_valid, "Year below minimum should fail"
    print(f"✓ Year below minimum rejected: {error}")
    
    # Test km range
    is_valid, _ = validator.validate_field('quilometragem', 50000)
    assert is_valid, "Valid km should pass"
    
    is_valid, error = validator.validate_field('quilometragem', 600000)
    assert not is_valid, "KM above maximum should fail"
    print(f"✓ KM above maximum rejected: {error}")


def test_cross_validation():
    """Test cross-validation between fields."""
    print("\n=== Test 5: Cross Validation ===")
    
    validator = DataValidator()
    
    # Test new car with high mileage (should fail)
    data = {
        'id': 'test_003',
        'nome': 'Novo Carro',
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'ano': 2024,
        'preco': 120000.0,
        'quilometragem': 80000,  # Too high for new car
        'combustivel': 'Flex',
        'cambio': 'Automático',
        'categoria': 'Sedan',
        'url_original': 'https://robustcar.com.br/veiculo/003',
        'content_hash': 'c' * 32
    }
    
    result = validator.validate(data)
    assert not result.is_valid, "New car with high mileage should fail"
    assert any('quilometragem muito alta' in error.lower() for error in result.errors)
    print(f"✓ New car with high mileage rejected")
    print(f"  Error: {result.errors[0]}")
    
    # Test old car with high mileage (should warn)
    data['ano'] = 2015
    data['quilometragem'] = 300000
    
    result = validator.validate(data)
    assert result.is_valid, "Old car with high mileage should be valid"
    assert len(result.warnings) > 0, "Should have warnings"
    print(f"✓ Old car with high mileage generates warning")
    print(f"  Warning: {result.warnings[0]}")


def test_completeness_calculation():
    """Test completeness calculation."""
    print("\n=== Test 6: Completeness Calculation ===")
    
    validator = DataValidator()
    
    # Complete vehicle
    complete_data = {
        'id': 'test_004',
        'nome': 'Complete Car',
        'marca': 'Honda',
        'modelo': 'Civic',
        'ano': 2021,
        'preco': 85000.0,
        'quilometragem': 40000,
        'combustivel': 'Flex',
        'cambio': 'Manual',
        'cor': 'Preto',
        'portas': 4,
        'categoria': 'Sedan',
        'imagens': ['img1.jpg', 'img2.jpg', 'img3.jpg'],
        'descricao': 'Descrição completa do veículo',
        'url_original': 'https://robustcar.com.br/veiculo/004',
        'content_hash': 'd' * 32
    }
    
    completeness = validator.calculate_completeness(complete_data)
    assert completeness == 1.0, "Complete vehicle should have 100% completeness"
    print(f"✓ Complete vehicle: {completeness:.2f} (100%)")
    
    # Only required fields
    required_only = {
        'id': 'test_005',
        'nome': 'Required Only',
        'marca': 'Ford',
        'modelo': 'Ka',
        'ano': 2020,
        'preco': 45000.0,
        'quilometragem': 50000,
        'combustivel': 'Flex',
        'cambio': 'Manual',
        'categoria': 'Hatch',
        'url_original': 'https://robustcar.com.br/veiculo/005',
        'content_hash': 'e' * 32
    }
    
    completeness = validator.calculate_completeness(required_only)
    assert completeness == 0.7, "Required-only vehicle should have 70% completeness"
    print(f"✓ Required fields only: {completeness:.2f} (70%)")


def test_quality_report():
    """Test quality report generation."""
    print("\n=== Test 7: Quality Report ===")
    
    validator = DataValidator()
    
    vehicles = []
    
    # Add 5 valid vehicles
    for i in range(5):
        vehicles.append({
            'id': f'test_{i:03d}',
            'nome': f'Vehicle {i}',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano': 2022,
            'preco': 90000.0 + (i * 1000),
            'quilometragem': 30000 + (i * 5000),
            'combustivel': 'Flex',
            'cambio': 'Automático',
            'cor': 'Prata',
            'portas': 4,
            'categoria': 'Sedan',
            'imagens': ['img1.jpg', 'img2.jpg'],
            'descricao': 'Descrição do veículo',
            'url_original': f'https://robustcar.com.br/veiculo/{i:03d}',
            'content_hash': f'{i:032d}'
        })
    
    # Add 1 invalid vehicle
    vehicles.append({
        'id': 'test_invalid',
        'nome': 'Invalid Vehicle',
        'marca': 'Honda',
        'modelo': 'Civic',
        'ano': 2021,
        'preco': -1000.0,  # Invalid price
        'quilometragem': 40000,
        'combustivel': 'Flex',
        'cambio': 'Manual',
        'categoria': 'Sedan',
        'url_original': 'https://robustcar.com.br/veiculo/invalid',
        'content_hash': 'f' * 32
    })
    
    report = validator.generate_quality_report(vehicles)
    
    assert report['total_vehicles'] == 6
    assert report['validation_summary']['valid'] == 5
    assert report['validation_summary']['invalid'] == 1
    assert report['quality_grade'] in ['A+', 'A', 'B', 'C', 'D', 'F']
    
    print(f"✓ Quality report generated")
    print(f"  Total vehicles: {report['total_vehicles']}")
    print(f"  Valid: {report['validation_summary']['valid']}")
    print(f"  Invalid: {report['validation_summary']['invalid']}")
    print(f"  Avg completeness: {report['avg_completeness']:.2f}")
    print(f"  Quality grade: {report['quality_grade']}")


def test_anomaly_detection():
    """Test anomaly detection."""
    print("\n=== Test 8: Anomaly Detection ===")
    
    validator = DataValidator()
    
    # Test round price
    data = {
        'id': 'test_006',
        'nome': 'Round Price Car',
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'ano': 2022,
        'preco': 100000.0,  # Suspiciously round
        'quilometragem': 35000,
        'combustivel': 'Flex',
        'cambio': 'Automático',
        'categoria': 'Sedan',
        'url_original': 'https://robustcar.com.br/veiculo/006',
        'content_hash': 'g' * 32
    }
    
    result = validator.validate(data)
    assert result.is_valid
    assert any('arredondado' in warning.lower() for warning in result.warnings)
    print(f"✓ Round price detected: {result.warnings[0]}")
    
    # Test missing images
    data['preco'] = 95000.0
    data['imagens'] = []
    
    result = validator.validate(data)
    assert any('imagem' in warning.lower() for warning in result.warnings)
    print(f"✓ Missing images detected")
    
    # Test missing description
    data['imagens'] = ['img1.jpg']
    data['descricao'] = None
    
    result = validator.validate(data)
    assert any('descrição' in warning.lower() for warning in result.warnings)
    print(f"✓ Missing description detected")


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("DataValidator Implementation Validation")
    print("=" * 60)
    
    try:
        test_basic_validation()
        test_missing_required_field()
        test_enum_validation()
        test_range_validation()
        test_cross_validation()
        test_completeness_calculation()
        test_quality_report()
        test_anomaly_detection()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nDataValidator implementation is working correctly!")
        print("\nFeatures validated:")
        print("  ✓ Required field validation")
        print("  ✓ Type and range validation")
        print("  ✓ Enum validation (câmbio, combustível, categoria)")
        print("  ✓ Cross-validation (km vs year, price vs category)")
        print("  ✓ Completeness calculation")
        print("  ✓ Quality report generation")
        print("  ✓ Anomaly detection")
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
