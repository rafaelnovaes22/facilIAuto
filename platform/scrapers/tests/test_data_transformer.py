"""
Tests for DataTransformer class.

Requirements: 1.4, 5.1
"""

import pytest
from datetime import datetime
from scraper.data_transformer import DataTransformer


class TestDataTransformer:
    """Test suite for DataTransformer"""
    
    @pytest.fixture
    def transformer(self):
        """Create DataTransformer instance"""
        return DataTransformer()
    
    @pytest.fixture
    def sample_raw_data(self):
        """Sample raw vehicle data"""
        return {
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
    
    def test_normalize_price_brazilian_format(self, transformer):
        """Test price normalization with Brazilian format"""
        assert transformer.normalize_price('R$ 95.990,00') == 95990.0
        assert transformer.normalize_price('R$ 125.500,00') == 125500.0
        assert transformer.normalize_price('85.000,00') == 85000.0
    
    def test_normalize_price_simple_format(self, transformer):
        """Test price normalization with simple format"""
        assert transformer.normalize_price('95990') == 95990.0
        assert transformer.normalize_price('125500') == 125500.0
    
    def test_normalize_price_invalid(self, transformer):
        """Test price normalization with invalid values"""
        assert transformer.normalize_price('') is None
        assert transformer.normalize_price('abc') is None
        assert transformer.normalize_price('5000') is None  # Too low
        assert transformer.normalize_price('600000') is None  # Too high
    
    def test_normalize_km_various_formats(self, transformer):
        """Test km normalization with various formats"""
        assert transformer.normalize_km('50.000 km') == 50000
        assert transformer.normalize_km('50000') == 50000
        assert transformer.normalize_km('50.000 quilômetros') == 50000
        assert transformer.normalize_km('KM: 50.000') == 50000
    
    def test_normalize_km_invalid(self, transformer):
        """Test km normalization with invalid values"""
        assert transformer.normalize_km('') is None
        assert transformer.normalize_km('abc') is None
        assert transformer.normalize_km('600000') is None  # Too high
    
    def test_normalize_cambio_standard_values(self, transformer):
        """Test cambio normalization"""
        assert transformer.normalize_cambio('Manual') == 'Manual'
        assert transformer.normalize_cambio('Automático') == 'Automático'
        assert transformer.normalize_cambio('Automático CVT') == 'Automático CVT'
        assert transformer.normalize_cambio('Automatizada') == 'Automatizada'
    
    def test_normalize_cambio_variations(self, transformer):
        """Test cambio normalization with variations"""
        assert transformer.normalize_cambio('manual') == 'Manual'
        assert transformer.normalize_cambio('automatico') == 'Automático'
        assert transformer.normalize_cambio('CVT') == 'Automático CVT'
        assert transformer.normalize_cambio('AMT') == 'Automatizada'
    
    def test_normalize_cambio_invalid(self, transformer):
        """Test cambio normalization with invalid values"""
        assert transformer.normalize_cambio('') is None
        assert transformer.normalize_cambio('unknown') is None
    
    def test_calculate_hash_consistency(self, transformer):
        """Test that hash calculation is consistent"""
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
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
    
    def test_calculate_hash_excludes_metadata(self, transformer):
        """Test that hash excludes metadata fields"""
        data1 = {
            'id': 'test_001',
            'nome': 'Toyota Corolla',
            'preco': 95990.0,
            'data_scraping': datetime.now()
        }
        
        data2 = {
            'id': 'test_002',  # Different ID
            'nome': 'Toyota Corolla',
            'preco': 95990.0,
            'data_scraping': datetime.now()  # Different timestamp
        }
        
        hash1 = transformer.calculate_hash(data1)
        hash2 = transformer.calculate_hash(data2)
        
        # Hashes should be the same because metadata is excluded
        assert hash1 == hash2
    
    def test_calculate_hash_detects_changes(self, transformer):
        """Test that hash detects content changes"""
        data1 = {
            'nome': 'Toyota Corolla',
            'preco': 95990.0,
            'quilometragem': 45000
        }
        
        data2 = {
            'nome': 'Toyota Corolla',
            'preco': 89990.0,  # Different price
            'quilometragem': 45000
        }
        
        hash1 = transformer.calculate_hash(data1)
        hash2 = transformer.calculate_hash(data2)
        
        # Hashes should be different
        assert hash1 != hash2
    
    def test_transform_complete_data(self, transformer, sample_raw_data):
        """Test transformation of complete raw data"""
        result = transformer.transform(sample_raw_data)
        
        # Check that all fields are transformed
        assert result['id'] == 'test_001'
        assert result['nome'] == 'Toyota Corolla GLi'
        assert result['marca'] == 'Toyota'
        assert result['modelo'] == 'Corolla'
        assert result['preco'] == 95990.0
        assert result['quilometragem'] == 45000
        assert result['ano'] == 2023  # Model year from 2022/2023
        assert result['combustivel'] == 'Flex'
        assert result['cambio'] == 'Automático CVT'
        assert result['categoria'] == 'Sedan'
        assert result['cor'] == 'Prata'
        assert result['portas'] == 4
        assert len(result['imagens']) == 2
        assert result['descricao'] == 'Carro em excelente estado'
        assert result['url_original'] == 'https://robustcar.com.br/veiculo/001'
        
        # Check metadata
        assert 'data_scraping' in result
        assert 'content_hash' in result
        assert len(result['content_hash']) == 32
    
    def test_transform_adds_timestamp(self, transformer):
        """Test that transform adds timestamp if not present"""
        raw_data = {
            'id': 'test_001',
            'nome': 'Toyota Corolla',
            'preco': '95990',
            'ano': '2022',
            'quilometragem': '45000'
        }
        
        result = transformer.transform(raw_data)
        
        assert 'data_scraping' in result
        assert isinstance(result['data_scraping'], datetime)
    
    def test_validate_and_transform_valid_data(self, transformer, sample_raw_data):
        """Test validate_and_transform with valid data"""
        result = transformer.validate_and_transform(sample_raw_data)
        
        assert result is not None
        assert result['preco'] == 95990.0
        assert result['ano'] == 2023
        assert result['quilometragem'] == 45000
    
    def test_validate_and_transform_missing_required_field(self, transformer):
        """Test validate_and_transform with missing required field"""
        raw_data = {
            'id': 'test_001',
            'nome': 'Toyota Corolla',
            # Missing preco
            'ano': '2022',
            'quilometragem': '45000'
        }
        
        result = transformer.validate_and_transform(raw_data)
        
        assert result is None
    
    def test_validate_and_transform_price_out_of_range(self, transformer):
        """Test validate_and_transform with price out of range"""
        raw_data = {
            'id': 'test_001',
            'nome': 'Toyota Corolla',
            'preco': '5000',  # Too low
            'ano': '2022',
            'quilometragem': '45000'
        }
        
        result = transformer.validate_and_transform(raw_data)
        
        assert result is None
    
    def test_validate_and_transform_year_out_of_range(self, transformer):
        """Test validate_and_transform with year out of range"""
        raw_data = {
            'id': 'test_001',
            'nome': 'Toyota Corolla',
            'preco': '95990',
            'ano': '2005',  # Too old
            'quilometragem': '45000'
        }
        
        result = transformer.validate_and_transform(raw_data)
        
        assert result is None
    
    def test_validate_and_transform_km_out_of_range(self, transformer):
        """Test validate_and_transform with km out of range"""
        raw_data = {
            'id': 'test_001',
            'nome': 'Toyota Corolla',
            'preco': '95990',
            'ano': '2022',
            'quilometragem': '600000'  # Too high
        }
        
        result = transformer.validate_and_transform(raw_data)
        
        assert result is None
    
    def test_normalize_year_model_year_format(self, transformer):
        """Test year normalization with YYYY/YYYY format"""
        assert transformer.normalize_year('2022/2023') == 2023
        assert transformer.normalize_year('2021/2022') == 2022
    
    def test_normalize_year_simple_format(self, transformer):
        """Test year normalization with simple format"""
        assert transformer.normalize_year('2022') == 2022
        assert transformer.normalize_year('Ano: 2022') == 2022
    
    def test_normalize_combustivel_standard_values(self, transformer):
        """Test combustivel normalization"""
        assert transformer.normalize_combustivel('Flex') == 'Flex'
        assert transformer.normalize_combustivel('Gasolina') == 'Gasolina'
        assert transformer.normalize_combustivel('Diesel') == 'Diesel'
        assert transformer.normalize_combustivel('Elétrico') == 'Elétrico'
        assert transformer.normalize_combustivel('Híbrido') == 'Híbrido'
    
    def test_normalize_combustivel_variations(self, transformer):
        """Test combustivel normalization with variations"""
        assert transformer.normalize_combustivel('flex') == 'Flex'
        assert transformer.normalize_combustivel('eletrico') == 'Elétrico'
        assert transformer.normalize_combustivel('hibrido') == 'Híbrido'
    
    def test_normalize_categoria_standard_values(self, transformer):
        """Test categoria normalization"""
        assert transformer.normalize_categoria('Hatch') == 'Hatch'
        assert transformer.normalize_categoria('Sedan') == 'Sedan'
        assert transformer.normalize_categoria('SUV') == 'SUV'
        assert transformer.normalize_categoria('Pickup') == 'Pickup'
        assert transformer.normalize_categoria('Compacto') == 'Compacto'
        assert transformer.normalize_categoria('Van') == 'Van'
    
    def test_normalize_categoria_variations(self, transformer):
        """Test categoria normalization with variations"""
        assert transformer.normalize_categoria('hatch') == 'Hatch'
        assert transformer.normalize_categoria('suv') == 'SUV'
        assert transformer.normalize_categoria('picape') == 'Pickup'
    
    def test_transform_partial_data(self, transformer):
        """Test transformation with partial data"""
        raw_data = {
            'id': 'test_001',
            'nome': 'Toyota Corolla',
            'preco': '95990',
            'ano': '2022'
            # Missing some optional fields
        }
        
        result = transformer.transform(raw_data)
        
        assert result is not None
        assert result['nome'] == 'Toyota Corolla'
        assert result['preco'] == 95990.0
        assert result['ano'] == 2022
        assert 'content_hash' in result
