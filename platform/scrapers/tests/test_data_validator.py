"""
Tests for DataValidator.

Requirements: 4.1, 4.2, 4.3, 4.4, 1.3, 4.5
"""

import pytest
from datetime import datetime
from scraper.data_validator import DataValidator
from scraper.models import ValidationResult


@pytest.fixture
def validator():
    """Create DataValidator instance."""
    return DataValidator()


@pytest.fixture
def valid_vehicle_data():
    """Create valid vehicle data for testing."""
    return {
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


class TestDataValidatorBasic:
    """Test basic validation functionality."""
    
    def test_validate_valid_vehicle(self, validator, valid_vehicle_data):
        """Test validation of completely valid vehicle."""
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.completeness > 0.9
    
    def test_validate_missing_required_field(self, validator, valid_vehicle_data):
        """Test validation fails when required field is missing."""
        del valid_vehicle_data['preco']
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is False
        assert any('preco' in error.lower() for error in result.errors)
        assert 'preco' in result.missing_fields
    
    def test_validate_empty_required_field(self, validator, valid_vehicle_data):
        """Test validation fails when required field is empty."""
        valid_vehicle_data['marca'] = ''
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is False
        assert any('marca' in error.lower() for error in result.errors)
    
    def test_validate_none_required_field(self, validator, valid_vehicle_data):
        """Test validation fails when required field is None."""
        valid_vehicle_data['modelo'] = None
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is False
        assert any('modelo' in error.lower() for error in result.errors)


class TestFieldValidation:
    """Test individual field validation."""
    
    def test_validate_price_valid(self, validator):
        """Test price validation with valid value."""
        is_valid, error = validator.validate_field('preco', 50000.0)
        assert is_valid is True
        assert error is None
    
    def test_validate_price_too_low(self, validator):
        """Test price validation with value below minimum."""
        is_valid, error = validator.validate_field('preco', 5000.0)
        assert is_valid is False
        assert 'fora da faixa' in error.lower()
    
    def test_validate_price_too_high(self, validator):
        """Test price validation with value above maximum."""
        is_valid, error = validator.validate_field('preco', 600000.0)
        assert is_valid is False
        assert 'fora da faixa' in error.lower()
    
    def test_validate_price_invalid_type(self, validator):
        """Test price validation with invalid type."""
        is_valid, error = validator.validate_field('preco', 'cinquenta mil')
        assert is_valid is False
        assert 'numérico' in error.lower()
    
    def test_validate_year_valid(self, validator):
        """Test year validation with valid value."""
        is_valid, error = validator.validate_field('ano', 2022)
        assert is_valid is True
        assert error is None
    
    def test_validate_year_too_old(self, validator):
        """Test year validation with value below minimum."""
        is_valid, error = validator.validate_field('ano', 2005)
        assert is_valid is False
        assert 'fora da faixa' in error.lower()
    
    def test_validate_year_future(self, validator):
        """Test year validation with future year."""
        is_valid, error = validator.validate_field('ano', 2030)
        assert is_valid is False
        assert 'fora da faixa' in error.lower()
    
    def test_validate_km_valid(self, validator):
        """Test mileage validation with valid value."""
        is_valid, error = validator.validate_field('quilometragem', 50000)
        assert is_valid is True
        assert error is None
    
    def test_validate_km_negative(self, validator):
        """Test mileage validation with negative value."""
        is_valid, error = validator.validate_field('quilometragem', -1000)
        assert is_valid is False
        assert 'fora da faixa' in error.lower()
    
    def test_validate_km_too_high(self, validator):
        """Test mileage validation with value above maximum."""
        is_valid, error = validator.validate_field('quilometragem', 600000)
        assert is_valid is False
        assert 'fora da faixa' in error.lower()


class TestEnumValidation:
    """Test enum field validation."""
    
    def test_validate_cambio_valid(self, validator):
        """Test cambio validation with valid values."""
        valid_cambios = ['Manual', 'Automático', 'Automático CVT', 'Automatizada']
        
        for cambio in valid_cambios:
            is_valid, error = validator.validate_field('cambio', cambio)
            assert is_valid is True, f"Câmbio '{cambio}' should be valid"
            assert error is None
    
    def test_validate_cambio_invalid(self, validator):
        """Test cambio validation with invalid value."""
        is_valid, error = validator.validate_field('cambio', 'Sequencial')
        assert is_valid is False
        assert 'inválido' in error.lower()
    
    def test_validate_combustivel_valid(self, validator):
        """Test combustivel validation with valid values."""
        valid_combustiveis = ['Flex', 'Gasolina', 'Diesel', 'Elétrico', 'Híbrido']
        
        for combustivel in valid_combustiveis:
            is_valid, error = validator.validate_field('combustivel', combustivel)
            assert is_valid is True, f"Combustível '{combustivel}' should be valid"
            assert error is None
    
    def test_validate_combustivel_invalid(self, validator):
        """Test combustivel validation with invalid value."""
        is_valid, error = validator.validate_field('combustivel', 'GNV')
        assert is_valid is False
        assert 'inválido' in error.lower()
    
    def test_validate_categoria_valid(self, validator):
        """Test categoria validation with valid values."""
        valid_categorias = ['Hatch', 'Sedan', 'SUV', 'Pickup', 'Compacto', 'Van']
        
        for categoria in valid_categorias:
            is_valid, error = validator.validate_field('categoria', categoria)
            assert is_valid is True, f"Categoria '{categoria}' should be valid"
            assert error is None
    
    def test_validate_categoria_invalid(self, validator):
        """Test categoria validation with invalid value."""
        is_valid, error = validator.validate_field('categoria', 'Conversível')
        assert is_valid is False
        assert 'inválida' in error.lower()


class TestCrossValidation:
    """Test cross-validation between fields."""
    
    def test_validate_new_car_high_mileage(self, validator, valid_vehicle_data):
        """Test validation fails for new car with high mileage."""
        valid_vehicle_data['ano'] = 2024
        valid_vehicle_data['quilometragem'] = 80000
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is False
        assert any('quilometragem muito alta' in error.lower() for error in result.errors)
    
    def test_validate_new_car_low_mileage(self, validator, valid_vehicle_data):
        """Test validation passes for new car with low mileage."""
        valid_vehicle_data['ano'] = 2024
        valid_vehicle_data['quilometragem'] = 15000
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is True
    
    def test_validate_old_car_high_mileage_warning(self, validator, valid_vehicle_data):
        """Test warning for old car with suspiciously high mileage."""
        valid_vehicle_data['ano'] = 2015
        valid_vehicle_data['quilometragem'] = 300000
        
        result = validator.validate(valid_vehicle_data)
        
        # Should be valid but with warning
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any('quilometragem' in warning.lower() for warning in result.warnings)
    
    def test_validate_price_category_mismatch_low(self, validator, valid_vehicle_data):
        """Test warning for price too low for category."""
        valid_vehicle_data['categoria'] = 'SUV'
        valid_vehicle_data['preco'] = 25000.0  # Too low for SUV
        
        result = validator.validate(valid_vehicle_data)
        
        # Should be valid but with warning
        assert result.is_valid is True
        assert any('preço' in warning.lower() and 'baixo' in warning.lower() 
                  for warning in result.warnings)
    
    def test_validate_price_category_mismatch_high(self, validator, valid_vehicle_data):
        """Test warning for price too high for category."""
        valid_vehicle_data['categoria'] = 'Compacto'
        valid_vehicle_data['preco'] = 150000.0  # Too high for Compacto
        
        result = validator.validate(valid_vehicle_data)
        
        # Should be valid but with warning
        assert result.is_valid is True
        assert any('preço' in warning.lower() and 'alto' in warning.lower() 
                  for warning in result.warnings)


class TestCompletenessCalculation:
    """Test completeness calculation."""
    
    def test_completeness_all_fields(self, validator, valid_vehicle_data):
        """Test completeness with all fields present."""
        completeness = validator.calculate_completeness(valid_vehicle_data)
        
        assert completeness == 1.0
    
    def test_completeness_only_required(self, validator, valid_vehicle_data):
        """Test completeness with only required fields."""
        # Remove optional fields
        del valid_vehicle_data['cor']
        del valid_vehicle_data['portas']
        del valid_vehicle_data['imagens']
        del valid_vehicle_data['descricao']
        
        completeness = validator.calculate_completeness(valid_vehicle_data)
        
        # Should be 0.7 (70% weight for required fields)
        assert completeness == 0.7
    
    def test_completeness_missing_required(self, validator, valid_vehicle_data):
        """Test completeness with missing required field."""
        del valid_vehicle_data['preco']
        
        completeness = validator.calculate_completeness(valid_vehicle_data)
        
        # Should be less than 0.7
        assert completeness < 0.7
    
    def test_completeness_partial_optional(self, validator, valid_vehicle_data):
        """Test completeness with some optional fields."""
        # Remove half of optional fields
        del valid_vehicle_data['portas']
        del valid_vehicle_data['descricao']
        
        completeness = validator.calculate_completeness(valid_vehicle_data)
        
        # Should be between 0.7 and 1.0
        assert 0.7 < completeness < 1.0


class TestAnomalyDetection:
    """Test anomaly detection."""
    
    def test_detect_round_price(self, validator, valid_vehicle_data):
        """Test detection of suspiciously round price."""
        valid_vehicle_data['preco'] = 100000.0
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is True
        assert any('arredondado' in warning.lower() for warning in result.warnings)
    
    def test_detect_no_images(self, validator, valid_vehicle_data):
        """Test detection of missing images."""
        valid_vehicle_data['imagens'] = []
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is True
        assert any('imagem' in warning.lower() for warning in result.warnings)
    
    def test_detect_few_images(self, validator, valid_vehicle_data):
        """Test detection of few images."""
        valid_vehicle_data['imagens'] = ['http://example.com/img1.jpg']
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is True
        assert any('poucas imagens' in warning.lower() for warning in result.warnings)
    
    def test_detect_missing_description(self, validator, valid_vehicle_data):
        """Test detection of missing description."""
        valid_vehicle_data['descricao'] = None
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is True
        assert any('descrição ausente' in warning.lower() for warning in result.warnings)
    
    def test_detect_short_description(self, validator, valid_vehicle_data):
        """Test detection of short description."""
        valid_vehicle_data['descricao'] = 'Carro bom'
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is True
        assert any('descrição muito curta' in warning.lower() for warning in result.warnings)
    
    def test_detect_missing_color(self, validator, valid_vehicle_data):
        """Test detection of missing color."""
        valid_vehicle_data['cor'] = None
        
        result = validator.validate(valid_vehicle_data)
        
        assert result.is_valid is True
        assert any('cor' in warning.lower() for warning in result.warnings)


class TestQualityReport:
    """Test quality report generation."""
    
    def test_generate_report_empty_list(self, validator):
        """Test quality report with empty vehicle list."""
        report = validator.generate_quality_report([])
        
        assert report['total_vehicles'] == 0
        assert report['avg_completeness'] == 0.0
    
    def test_generate_report_single_vehicle(self, validator, valid_vehicle_data):
        """Test quality report with single vehicle."""
        report = validator.generate_quality_report([valid_vehicle_data])
        
        assert report['total_vehicles'] == 1
        assert report['avg_completeness'] > 0.9
        assert report['validation_summary']['valid'] == 1
        assert report['validation_summary']['invalid'] == 0
        assert report['quality_grade'] in ['A+', 'A', 'B', 'C', 'D', 'F']
    
    def test_generate_report_multiple_vehicles(self, validator, valid_vehicle_data):
        """Test quality report with multiple vehicles."""
        vehicles = [valid_vehicle_data.copy() for _ in range(5)]
        
        # Make one vehicle invalid
        vehicles[2]['preco'] = -1000
        
        report = validator.generate_quality_report(vehicles)
        
        assert report['total_vehicles'] == 5
        assert report['validation_summary']['valid'] == 4
        assert report['validation_summary']['invalid'] == 1
        assert report['validation_summary']['valid_percentage'] == 0.8
    
    def test_generate_report_field_completeness(self, validator, valid_vehicle_data):
        """Test field completeness in quality report."""
        vehicles = [valid_vehicle_data.copy() for _ in range(3)]
        
        # Remove optional field from one vehicle
        del vehicles[1]['cor']
        
        report = validator.generate_quality_report(vehicles)
        
        # All required fields should be 100% complete
        assert report['field_completeness']['preco'] == 1.0
        assert report['field_completeness']['marca'] == 1.0
        
        # Color should be 66.7% complete (2 out of 3)
        assert abs(report['field_completeness']['cor'] - 0.667) < 0.01
    
    def test_quality_grade_excellent(self, validator, valid_vehicle_data):
        """Test quality grade calculation for excellent data."""
        vehicles = [valid_vehicle_data.copy() for _ in range(10)]
        
        report = validator.generate_quality_report(vehicles)
        
        assert report['quality_grade'] in ['A+', 'A']
    
    def test_quality_grade_poor(self, validator, valid_vehicle_data):
        """Test quality grade calculation for poor data."""
        vehicles = []
        for i in range(10):
            vehicle = valid_vehicle_data.copy()
            # Remove many fields to reduce completeness
            if i % 2 == 0:
                del vehicle['cor']
                del vehicle['portas']
                del vehicle['imagens']
                del vehicle['descricao']
            # Make some invalid
            if i % 3 == 0:
                vehicle['preco'] = -1000
            vehicles.append(vehicle)
        
        report = validator.generate_quality_report(vehicles)
        
        # Should have lower grade due to invalid vehicles and low completeness
        assert report['quality_grade'] in ['C', 'D', 'F']


class TestValidationResult:
    """Test ValidationResult model."""
    
    def test_validation_result_valid(self, validator, valid_vehicle_data):
        """Test ValidationResult for valid vehicle."""
        result = validator.validate(valid_vehicle_data)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.completeness, float)
        assert isinstance(result.missing_fields, list)
    
    def test_validation_result_to_dict(self, validator, valid_vehicle_data):
        """Test ValidationResult conversion to dictionary."""
        result = validator.validate(valid_vehicle_data)
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert 'is_valid' in result_dict
        assert 'errors' in result_dict
        assert 'warnings' in result_dict
        assert 'completeness' in result_dict
        assert 'missing_fields' in result_dict
