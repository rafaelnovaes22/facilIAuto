"""
Tests for field extractors module.

Requirements: 1.1, 1.4, 9.1, 9.2
"""

import pytest
from scraper.extractors import FieldExtractor


class TestFieldExtractor:
    """Test FieldExtractor class"""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance"""
        return FieldExtractor(selector_config_path="config/selectors.yaml")
    
    def test_extract_price_brazilian_format(self, extractor):
        """Test extracting price in Brazilian format"""
        assert extractor.extract_price("R$ 95.990,00") == 95990.0
        assert extractor.extract_price("R$ 125.000,00") == 125000.0
        assert extractor.extract_price("Preço: R$ 89.900") == 89900.0
    
    def test_extract_price_simple_format(self, extractor):
        """Test extracting price in simple format"""
        assert extractor.extract_price("95990") == 95990.0
        assert extractor.extract_price("125000") == 125000.0
    
    def test_extract_price_invalid(self, extractor):
        """Test extracting invalid price"""
        assert extractor.extract_price("") is None
        assert extractor.extract_price("abc") is None
        assert extractor.extract_price("R$ 5.000") is None  # Too low
        assert extractor.extract_price("R$ 600.000") is None  # Too high
    
    def test_extract_km_various_formats(self, extractor):
        """Test extracting mileage in various formats"""
        assert extractor.extract_km("50.000 km") == 50000
        assert extractor.extract_km("50000") == 50000
        assert extractor.extract_km("KM: 45.000") == 45000
        assert extractor.extract_km("45.000 quilômetros") == 45000
    
    def test_extract_km_invalid(self, extractor):
        """Test extracting invalid mileage"""
        assert extractor.extract_km("") is None
        assert extractor.extract_km("abc") is None
        assert extractor.extract_km("600.000 km") is None  # Too high
    
    def test_extract_year_single(self, extractor):
        """Test extracting single year"""
        assert extractor.extract_year("2022") == 2022
        assert extractor.extract_year("Ano: 2023") == 2023
    
    def test_extract_year_double_format(self, extractor):
        """Test extracting year in YYYY/YYYY format"""
        assert extractor.extract_year("2022/2023") == 2023  # Model year
        assert extractor.extract_year("2021/2022") == 2022
    
    def test_extract_year_invalid(self, extractor):
        """Test extracting invalid year"""
        assert extractor.extract_year("") is None
        assert extractor.extract_year("abc") is None
        assert extractor.extract_year("2009") is None  # Too old
        assert extractor.extract_year("2027") is None  # Too new
    
    def test_extract_doors(self, extractor):
        """Test extracting number of doors"""
        assert extractor.extract_doors("4 portas") == 4
        assert extractor.extract_doors("Portas: 2") == 2
        assert extractor.extract_doors("5") == 5
    
    def test_extract_doors_invalid(self, extractor):
        """Test extracting invalid door count"""
        assert extractor.extract_doors("") is None
        assert extractor.extract_doors("abc") is None
        assert extractor.extract_doors("10 portas") is None  # Out of range
    
    def test_normalize_cambio(self, extractor):
        """Test normalizing transmission type"""
        assert extractor.normalize_cambio("manual") == "Manual"
        assert extractor.normalize_cambio("Automático") == "Automático"
        assert extractor.normalize_cambio("automático cvt") == "Automático CVT"
        assert extractor.normalize_cambio("CVT") == "Automático CVT"
        assert extractor.normalize_cambio("automatizada") == "Automatizada"
        assert extractor.normalize_cambio("AMT") == "Automatizada"
    
    def test_normalize_cambio_invalid(self, extractor):
        """Test normalizing invalid transmission"""
        assert extractor.normalize_cambio("") is None
        assert extractor.normalize_cambio("unknown") is None
    
    def test_normalize_combustivel(self, extractor):
        """Test normalizing fuel type"""
        assert extractor.normalize_combustivel("flex") == "Flex"
        assert extractor.normalize_combustivel("Flexível") == "Flex"
        assert extractor.normalize_combustivel("gasolina") == "Gasolina"
        assert extractor.normalize_combustivel("diesel") == "Diesel"
        assert extractor.normalize_combustivel("elétrico") == "Elétrico"
        assert extractor.normalize_combustivel("híbrido") == "Híbrido"
    
    def test_normalize_combustivel_invalid(self, extractor):
        """Test normalizing invalid fuel type"""
        assert extractor.normalize_combustivel("") is None
        assert extractor.normalize_combustivel("unknown") is None
    
    def test_normalize_categoria(self, extractor):
        """Test normalizing vehicle category"""
        assert extractor.normalize_categoria("hatch") == "Hatch"
        assert extractor.normalize_categoria("Hatchback") == "Hatch"
        assert extractor.normalize_categoria("sedan") == "Sedan"
        assert extractor.normalize_categoria("Sedã") == "Sedan"
        assert extractor.normalize_categoria("SUV") == "SUV"
        assert extractor.normalize_categoria("pickup") == "Pickup"
        assert extractor.normalize_categoria("Picape") == "Pickup"
        assert extractor.normalize_categoria("van") == "Van"
    
    def test_normalize_categoria_invalid(self, extractor):
        """Test normalizing invalid category"""
        assert extractor.normalize_categoria("") is None
        assert extractor.normalize_categoria("unknown") is None
    
    def test_validate_images(self, extractor):
        """Test validating image URLs"""
        urls = [
            "http://example.com/img1.jpg",
            "https://example.com/img2.png",
            "invalid-url",
            "",
            "http://example.com/img1.jpg",  # Duplicate
        ]
        
        valid = extractor.validate_images(urls)
        
        assert len(valid) == 2  # Only 2 unique valid URLs
        assert "http://example.com/img1.jpg" in valid
        assert "https://example.com/img2.png" in valid
    
    def test_validate_images_empty(self, extractor):
        """Test validating empty image list"""
        assert extractor.validate_images([]) == []
        assert extractor.validate_images(None) == []
    
    def test_extract_and_normalize_complete(self, extractor):
        """Test extracting and normalizing complete data"""
        raw_data = {
            'nome': 'Toyota Corolla GLi',
            'preco': 'R$ 95.990,00',
            'ano': '2022/2023',
            'quilometragem': '45.000 km',
            'cambio': 'automático cvt',
            'combustivel': 'flex',
            'categoria': 'sedan',
            'portas': '4 portas',
            'imagens': ['http://example.com/img1.jpg', 'http://example.com/img2.jpg'],
            'url_original': 'http://example.com/car/1'
        }
        
        normalized = extractor.extract_and_normalize(raw_data)
        
        assert normalized['nome'] == 'Toyota Corolla GLi'
        assert normalized['preco'] == 95990.0
        assert normalized['ano'] == 2023
        assert normalized['quilometragem'] == 45000
        assert normalized['cambio'] == 'Automático CVT'
        assert normalized['combustivel'] == 'Flex'
        assert normalized['categoria'] == 'Sedan'
        assert normalized['portas'] == 4
        assert len(normalized['imagens']) == 2
        assert normalized['url_original'] == 'http://example.com/car/1'
    
    def test_extract_and_normalize_partial(self, extractor):
        """Test extracting with missing fields"""
        raw_data = {
            'nome': 'Toyota Corolla',
            'preco': 'R$ 95.990,00',
            'ano': '2022',
        }
        
        normalized = extractor.extract_and_normalize(raw_data)
        
        assert 'nome' in normalized
        assert 'preco' in normalized
        assert 'ano' in normalized
        assert 'quilometragem' not in normalized
        assert 'cambio' not in normalized
