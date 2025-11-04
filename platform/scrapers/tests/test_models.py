"""
Tests for scraper data models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from scraper.models import Vehicle, Config, Checkpoint, ValidationResult, ScrapingResult


class TestVehicle:
    """Tests for Vehicle model"""
    
    def test_valid_vehicle(self):
        """Test creating a valid vehicle"""
        vehicle = Vehicle(
            id="test_1",
            nome="Toyota Corolla GLi",
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            preco=95000.0,
            quilometragem=45000,
            combustivel="Flex",
            cambio="Automático CVT",
            cor="Prata",
            portas=4,
            categoria="Sedan",
            imagens=["https://example.com/img1.jpg"],
            descricao="Carro em ótimo estado",
            url_original="https://robustcar.com.br/veiculo/1",
            content_hash="a" * 32
        )
        
        assert vehicle.nome == "Toyota Corolla GLi"
        assert vehicle.ano == 2022
        assert vehicle.preco == 95000.0
    
    def test_vehicle_price_validation(self):
        """Test price validation - must be positive"""
        with pytest.raises(ValidationError) as exc_info:
            Vehicle(
                id="test_1",
                nome="Test Car",
                marca="Test",
                modelo="Model",
                ano=2022,
                preco=-1000.0,  # Invalid: negative price
                quilometragem=10000,
                combustivel="Flex",
                cambio="Manual",
                categoria="Sedan",
                url_original="https://example.com",
                content_hash="a" * 32
            )
        
        assert "Preço deve ser positivo" in str(exc_info.value)
    
    def test_vehicle_km_validation_new_car(self):
        """Test mileage validation for new cars"""
        with pytest.raises(ValidationError) as exc_info:
            Vehicle(
                id="test_1",
                nome="Test Car",
                marca="Test",
                modelo="Model",
                ano=2024,
                preco=100000.0,
                quilometragem=60000,  # Invalid: too high for new car
                combustivel="Flex",
                cambio="Manual",
                categoria="Sedan",
                url_original="https://example.com",
                content_hash="a" * 32
            )
        
        assert "Quilometragem muito alta para carro novo" in str(exc_info.value)
    
    def test_vehicle_year_range(self):
        """Test year must be between 2010 and 2026"""
        with pytest.raises(ValidationError):
            Vehicle(
                id="test_1",
                nome="Test Car",
                marca="Test",
                modelo="Model",
                ano=2009,  # Invalid: too old
                preco=50000.0,
                quilometragem=100000,
                combustivel="Flex",
                cambio="Manual",
                categoria="Sedan",
                url_original="https://example.com",
                content_hash="a" * 32
            )
    
    def test_vehicle_cambio_validation(self):
        """Test cambio must be in allowed list"""
        with pytest.raises(ValidationError):
            Vehicle(
                id="test_1",
                nome="Test Car",
                marca="Test",
                modelo="Model",
                ano=2022,
                preco=50000.0,
                quilometragem=10000,
                combustivel="Flex",
                cambio="Invalid Cambio",  # Invalid
                categoria="Sedan",
                url_original="https://example.com",
                content_hash="a" * 32
            )
    
    def test_vehicle_image_url_validation(self):
        """Test image URLs must be valid HTTP(S)"""
        with pytest.raises(ValidationError) as exc_info:
            Vehicle(
                id="test_1",
                nome="Test Car",
                marca="Test",
                modelo="Model",
                ano=2022,
                preco=50000.0,
                quilometragem=10000,
                combustivel="Flex",
                cambio="Manual",
                categoria="Sedan",
                imagens=["invalid-url"],  # Invalid URL
                url_original="https://example.com",
                content_hash="a" * 32
            )
        
        assert "URL de imagem inválida" in str(exc_info.value)
    
    def test_vehicle_to_dict(self):
        """Test converting vehicle to dictionary"""
        vehicle = Vehicle(
            id="test_1",
            nome="Test Car",
            marca="Test",
            modelo="Model",
            ano=2022,
            preco=50000.0,
            quilometragem=10000,
            combustivel="Flex",
            cambio="Manual",
            categoria="Sedan",
            url_original="https://example.com",
            content_hash="a" * 32
        )
        
        data = vehicle.to_dict()
        assert isinstance(data, dict)
        assert data['nome'] == "Test Car"
        assert data['ano'] == 2022
        assert isinstance(data['data_scraping'], str)  # Should be ISO format
    
    def test_vehicle_from_dict(self):
        """Test creating vehicle from dictionary"""
        data = {
            'id': 'test_1',
            'nome': 'Test Car',
            'marca': 'Test',
            'modelo': 'Model',
            'ano': 2022,
            'preco': 50000.0,
            'quilometragem': 10000,
            'combustivel': 'Flex',
            'cambio': 'Manual',
            'categoria': 'Sedan',
            'url_original': 'https://example.com',
            'data_scraping': '2025-10-30T14:30:00',
            'content_hash': 'a' * 32
        }
        
        vehicle = Vehicle.from_dict(data)
        assert vehicle.nome == "Test Car"
        assert isinstance(vehicle.data_scraping, datetime)
    
    def test_calculate_content_hash(self):
        """Test content hash calculation"""
        data = {
            'nome': 'Test Car',
            'marca': 'Test',
            'preco': 50000.0,
            'ano': 2022
        }
        
        hash1 = Vehicle.calculate_content_hash(data)
        assert len(hash1) == 32
        
        # Same data should produce same hash
        hash2 = Vehicle.calculate_content_hash(data)
        assert hash1 == hash2
        
        # Different data should produce different hash
        data['preco'] = 60000.0
        hash3 = Vehicle.calculate_content_hash(data)
        assert hash1 != hash3


class TestConfig:
    """Tests for Config model"""
    
    def test_default_config(self):
        """Test creating config with default values"""
        config = Config()
        
        assert config.scraper_name == "robustcar-scraper"
        assert config.http_timeout == 30
        assert config.rate_limit_requests_per_minute == 60
        assert config.workers_max_concurrent == 3
        assert config.cache_enabled is True
    
    def test_custom_config(self):
        """Test creating config with custom values"""
        config = Config(
            http_timeout=60,
            rate_limit_requests_per_minute=30,
            workers_max_concurrent=5
        )
        
        assert config.http_timeout == 60
        assert config.rate_limit_requests_per_minute == 30
        assert config.workers_max_concurrent == 5
    
    def test_config_validation_timeout(self):
        """Test timeout validation"""
        with pytest.raises(ValidationError):
            Config(http_timeout=200)  # Too high
    
    def test_config_validation_throttle(self):
        """Test throttle validation"""
        with pytest.raises(ValidationError) as exc_info:
            Config(rate_limit_business_hours_throttle=1.5)  # Too high
        
        assert "Throttle deve estar entre 0.1 e 1.0" in str(exc_info.value)
    
    def test_config_quality_thresholds(self):
        """Test quality threshold validation"""
        with pytest.raises(ValidationError) as exc_info:
            Config(quality_min_completeness=0.3)  # Too low
        
        assert "Completude mínima deve ser pelo menos 0.5" in str(exc_info.value)


class TestCheckpoint:
    """Tests for Checkpoint model"""
    
    def test_checkpoint_creation(self):
        """Test creating a checkpoint"""
        checkpoint = Checkpoint(
            id="checkpoint_1",
            processed_count=50,
            success_count=48,
            error_count=2,
            last_vehicle_id="vehicle_50"
        )
        
        assert checkpoint.id == "checkpoint_1"
        assert checkpoint.processed_count == 50
        assert checkpoint.success_count == 48
    
    def test_checkpoint_to_dict(self):
        """Test converting checkpoint to dictionary"""
        checkpoint = Checkpoint(
            id="checkpoint_1",
            processed_count=50,
            success_count=48,
            error_count=2
        )
        
        data = checkpoint.to_dict()
        assert isinstance(data, dict)
        assert data['id'] == "checkpoint_1"
        assert isinstance(data['timestamp'], str)
    
    def test_checkpoint_from_dict(self):
        """Test creating checkpoint from dictionary"""
        data = {
            'id': 'checkpoint_1',
            'timestamp': '2025-10-30T14:30:00',
            'processed_count': 50,
            'success_count': 48,
            'error_count': 2,
            'last_vehicle_id': 'vehicle_50',
            'metadata': {}
        }
        
        checkpoint = Checkpoint.from_dict(data)
        assert checkpoint.id == "checkpoint_1"
        assert isinstance(checkpoint.timestamp, datetime)


class TestValidationResult:
    """Tests for ValidationResult model"""
    
    def test_validation_result_valid(self):
        """Test creating a valid validation result"""
        result = ValidationResult(
            is_valid=True,
            completeness=0.95,
            errors=[],
            warnings=[]
        )
        
        assert result.is_valid is True
        assert result.completeness == 0.95
        assert len(result.errors) == 0
    
    def test_validation_result_invalid(self):
        """Test creating an invalid validation result"""
        result = ValidationResult(
            is_valid=False,
            completeness=0.75,
            errors=["Missing required field: preco"],
            warnings=["Low quality image"],
            missing_fields=["preco"]
        )
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1


class TestScrapingResult:
    """Tests for ScrapingResult model"""
    
    def test_scraping_result_creation(self):
        """Test creating a scraping result"""
        start = datetime.now()
        result = ScrapingResult(
            id="run_1",
            start_time=start,
            mode="full",
            total_processed=100,
            total_success=95,
            total_errors=5
        )
        
        assert result.id == "run_1"
        assert result.mode == "full"
        assert result.total_processed == 100
    
    def test_scraping_result_success_rate(self):
        """Test success rate calculation"""
        result = ScrapingResult(
            id="run_1",
            start_time=datetime.now(),
            mode="full",
            total_processed=100,
            total_success=95,
            total_errors=5
        )
        
        assert result.success_rate == 0.95
    
    def test_scraping_result_error_rate(self):
        """Test error rate calculation"""
        result = ScrapingResult(
            id="run_1",
            start_time=datetime.now(),
            mode="full",
            total_processed=100,
            total_success=95,
            total_errors=5
        )
        
        assert result.error_rate == 0.05
    
    def test_scraping_result_duration(self):
        """Test duration calculation"""
        start = datetime(2025, 10, 30, 14, 0, 0)
        end = datetime(2025, 10, 30, 14, 5, 30)
        
        result = ScrapingResult(
            id="run_1",
            start_time=start,
            end_time=end,
            mode="full"
        )
        
        assert result.duration_seconds == 330.0  # 5 minutes 30 seconds
    
    def test_scraping_result_to_dict(self):
        """Test converting scraping result to dictionary"""
        vehicle = Vehicle(
            id="test_1",
            nome="Test Car",
            marca="Test",
            modelo="Model",
            ano=2022,
            preco=50000.0,
            quilometragem=10000,
            combustivel="Flex",
            cambio="Manual",
            categoria="Sedan",
            url_original="https://example.com",
            content_hash="a" * 32
        )
        
        result = ScrapingResult(
            id="run_1",
            start_time=datetime.now(),
            mode="full",
            vehicles=[vehicle]
        )
        
        data = result.to_dict()
        assert isinstance(data, dict)
        assert len(data['vehicles']) == 1
        assert isinstance(data['vehicles'][0], dict)
