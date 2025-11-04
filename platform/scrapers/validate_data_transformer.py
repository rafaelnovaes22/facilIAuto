"""
Validation script for DataTransformer class.

This script tests the DataTransformer implementation without pytest.
Requirements: 1.4, 5.1
"""

import sys
from datetime import datetime
from scraper.data_transformer import DataTransformer


def test_normalize_price():
    """Test price normalization"""
    print("Testing normalize_price...")
    transformer = DataTransformer()
    
    tests = [
        ('R$ 95.990,00', 95990.0),
        ('R$ 125.500,00', 125500.0),
        ('85.000,00', 85000.0),
        ('95990', 95990.0),
        ('', None),
        ('abc', None),
    ]
    
    for input_val, expected in tests:
        result = transformer.normalize_price(input_val)
        status = "✓" if result == expected else "✗"
        print(f"  {status} normalize_price('{input_val}') = {result} (expected {expected})")
        if result != expected:
            return False
    
    return True


def test_normalize_km():
    """Test km normalization"""
    print("\nTesting normalize_km...")
    transformer = DataTransformer()
    
    tests = [
        ('50.000 km', 50000),
        ('50000', 50000),
        ('50.000 quilômetros', 50000),
        ('KM: 50.000', 50000),
        ('', None),
        ('abc', None),
    ]
    
    for input_val, expected in tests:
        result = transformer.normalize_km(input_val)
        status = "✓" if result == expected else "✗"
        print(f"  {status} normalize_km('{input_val}') = {result} (expected {expected})")
        if result != expected:
            return False
    
    return True


def test_normalize_cambio():
    """Test cambio normalization"""
    print("\nTesting normalize_cambio...")
    transformer = DataTransformer()
    
    tests = [
        ('Manual', 'Manual'),
        ('manual', 'Manual'),
        ('Automático', 'Automático'),
        ('automatico', 'Automático'),
        ('CVT', 'Automático CVT'),
        ('Automatizada', 'Automatizada'),
        ('AMT', 'Automatizada'),
        ('', None),
        ('unknown', None),
    ]
    
    for input_val, expected in tests:
        result = transformer.normalize_cambio(input_val)
        status = "✓" if result == expected else "✗"
        print(f"  {status} normalize_cambio('{input_val}') = {result} (expected {expected})")
        if result != expected:
            return False
    
    return True


def test_calculate_hash():
    """Test hash calculation"""
    print("\nTesting calculate_hash...")
    transformer = DataTransformer()
    
    # Test consistency
    data1 = {
        'nome': 'Toyota Corolla',
        'preco': 95990.0,
        'ano': 2022,
        'quilometragem': 45000
    }
    
    data2 = {
        'nome': 'Toyota Corolla',
        'preco': 95990.0,
        'ano': 2022,
        'quilometragem': 45000
    }
    
    hash1 = transformer.calculate_hash(data1)
    hash2 = transformer.calculate_hash(data2)
    
    print(f"  Hash 1: {hash1}")
    print(f"  Hash 2: {hash2}")
    
    if hash1 != hash2:
        print("  ✗ Hashes should be equal for same data")
        return False
    
    if len(hash1) != 32:
        print(f"  ✗ Hash length should be 32, got {len(hash1)}")
        return False
    
    print("  ✓ Hash consistency test passed")
    
    # Test that metadata is excluded
    data3 = {
        'id': 'test_001',
        'nome': 'Toyota Corolla',
        'preco': 95990.0,
        'data_scraping': datetime.now()
    }
    
    data4 = {
        'id': 'test_002',  # Different ID
        'nome': 'Toyota Corolla',
        'preco': 95990.0,
        'data_scraping': datetime.now()  # Different timestamp
    }
    
    hash3 = transformer.calculate_hash(data3)
    hash4 = transformer.calculate_hash(data4)
    
    if hash3 != hash4:
        print("  ✗ Hashes should be equal when only metadata differs")
        return False
    
    print("  ✓ Metadata exclusion test passed")
    
    # Test change detection
    data5 = {
        'nome': 'Toyota Corolla',
        'preco': 95990.0,
        'quilometragem': 45000
    }
    
    data6 = {
        'nome': 'Toyota Corolla',
        'preco': 89990.0,  # Different price
        'quilometragem': 45000
    }
    
    hash5 = transformer.calculate_hash(data5)
    hash6 = transformer.calculate_hash(data6)
    
    if hash5 == hash6:
        print("  ✗ Hashes should be different when content changes")
        return False
    
    print("  ✓ Change detection test passed")
    
    return True


def test_transform():
    """Test complete transformation"""
    print("\nTesting transform...")
    transformer = DataTransformer()
    
    raw_data = {
        'id': 'test_001',
        'nome': 'Toyota Corolla GLi',
        'marca': 'Toyota',
        'modelo': 'Corolla',
        'preco': 'R$ 95.990,00',
        'quilometragem': '45.000 km',
        'ano': '2022/2023',
        'combustivel': 'Flex',
        'cambio': 'Automático CVT',
        'categoria': 'Sedan',
        'cor': 'Prata',
        'portas': '4',
        'imagens': [
            'https://example.com/car1.jpg',
            'https://example.com/car2.jpg'
        ],
        'descricao': 'Carro em excelente estado',
        'url_original': 'https://robustcar.com.br/veiculo/001'
    }
    
    result = transformer.transform(raw_data)
    
    checks = [
        ('id', 'test_001'),
        ('nome', 'Toyota Corolla GLi'),
        ('marca', 'Toyota'),
        ('modelo', 'Corolla'),
        ('preco', 95990.0),
        ('quilometragem', 45000),
        ('ano', 2023),  # Model year from 2022/2023
        ('combustivel', 'Flex'),
        ('cambio', 'Automático CVT'),
        ('categoria', 'Sedan'),
        ('cor', 'Prata'),
        ('portas', 4),
    ]
    
    all_passed = True
    for field, expected in checks:
        if field in result:
            actual = result[field]
            status = "✓" if actual == expected else "✗"
            print(f"  {status} {field}: {actual} (expected {expected})")
            if actual != expected:
                all_passed = False
        else:
            print(f"  ✗ {field}: missing (expected {expected})")
            all_passed = False
    
    # Check metadata
    if 'data_scraping' not in result:
        print("  ✗ data_scraping: missing")
        all_passed = False
    else:
        print(f"  ✓ data_scraping: {result['data_scraping']}")
    
    if 'content_hash' not in result:
        print("  ✗ content_hash: missing")
        all_passed = False
    elif len(result['content_hash']) != 32:
        print(f"  ✗ content_hash: invalid length {len(result['content_hash'])}")
        all_passed = False
    else:
        print(f"  ✓ content_hash: {result['content_hash']}")
    
    if len(result.get('imagens', [])) != 2:
        print(f"  ✗ imagens: expected 2, got {len(result.get('imagens', []))}")
        all_passed = False
    else:
        print(f"  ✓ imagens: {len(result['imagens'])} images")
    
    return all_passed


def test_validate_and_transform():
    """Test validation and transformation"""
    print("\nTesting validate_and_transform...")
    transformer = DataTransformer()
    
    # Valid data
    valid_data = {
        'id': 'test_001',
        'nome': 'Toyota Corolla',
        'preco': '95990',
        'ano': '2022',
        'quilometragem': '45000'
    }
    
    result = transformer.validate_and_transform(valid_data)
    if result is None:
        print("  ✗ Valid data should not return None")
        return False
    print("  ✓ Valid data accepted")
    
    # Missing required field
    invalid_data = {
        'id': 'test_001',
        'nome': 'Toyota Corolla',
        # Missing preco
        'ano': '2022',
        'quilometragem': '45000'
    }
    
    result = transformer.validate_and_transform(invalid_data)
    if result is not None:
        print("  ✗ Missing required field should return None")
        return False
    print("  ✓ Missing required field rejected")
    
    # Price out of range
    invalid_price = {
        'id': 'test_001',
        'nome': 'Toyota Corolla',
        'preco': '5000',  # Too low
        'ano': '2022',
        'quilometragem': '45000'
    }
    
    result = transformer.validate_and_transform(invalid_price)
    if result is not None:
        print("  ✗ Price out of range should return None")
        return False
    print("  ✓ Price out of range rejected")
    
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("DataTransformer Validation")
    print("=" * 60)
    
    tests = [
        test_normalize_price,
        test_normalize_km,
        test_normalize_cambio,
        test_calculate_hash,
        test_transform,
        test_validate_and_transform,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n  ✗ Exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
