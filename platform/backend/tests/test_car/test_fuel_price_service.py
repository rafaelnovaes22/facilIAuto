
import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open
from datetime import datetime, timedelta
from services.car.fuel_price_service import FuelPriceService

class TestFuelPriceService:
    
    @pytest.fixture
    def mock_cache_dir(self, tmp_path):
        return tmp_path / "cache"

    @pytest.fixture
    def service(self, mock_cache_dir):
        return FuelPriceService(cache_dir=str(mock_cache_dir))
        
    def test_get_price_from_env(self, service):
        """Preço da váriavel de ambiente tem prioridade 1"""
        with patch.dict(os.environ, {"FUEL_PRICE": "5.50"}):
            price = service.get_current_price()
            assert price == 5.50
            
    def test_get_price_from_cache(self, service):
        """Preço do cache tem prioridade 2"""
        # Preparar cache
        cache_data = {
            "price": 5.80,
            "timestamp": datetime.now().isoformat(),
            "source": "api"
        }
        
        # Garantir diretório
        os.makedirs(service.cache_dir, exist_ok=True)
        
        with open(service.cache_file, "w") as f:
            json.dump(cache_data, f)
            
        with patch.dict(os.environ, {}, clear=True):
             # Mock API to ensure it doesn't hit it
             with patch.object(service, '_fetch_from_api', return_value=None):
                 price = service.get_current_price()
                 assert price == 5.80

    def test_cache_expiration(self, service):
        """Cache expirado deve ser ignorado"""
        # Data de 8 dias atrás
        old_date = datetime.now() - timedelta(days=8)
        cache_data = {
            "price": 4.00,
            "timestamp": old_date.isoformat(),
            "source": "api"
        }
        
        os.makedirs(service.cache_dir, exist_ok=True)
        with open(service.cache_file, "w") as f:
            json.dump(cache_data, f)
            
        with patch.dict(os.environ, {}, clear=True):
             # Mock API falhando -> deve cair no default
             with patch.object(service, '_fetch_from_api', return_value=None):
                 price = service.get_current_price()
                 assert price == service.DEFAULT_PRICE
                 
    def test_fallback_to_default(self, service):
        """Se tudo falhar, usa default"""
        # Sem env, sem cache, sem API
        with patch.dict(os.environ, {}, clear=True):
             with patch.object(service, '_get_cached_price', return_value=None):
                 with patch.object(service, '_fetch_from_api', return_value=None):
                     price = service.get_current_price()
                     assert price == service.DEFAULT_PRICE

    def test_update_default_price(self, service):
        """Atualizar preço padrão deve atualizar cache"""
        service.update_default_price(7.00)
        
        # Verificar se salvou no cache
        with open(service.cache_file, "r") as f:
            data = json.load(f)
            assert data["price"] == 7.00
            
    def test_get_price_info(self, service):
        """Deve retornar metadados corretos"""
        info = service.get_price_info()
        assert "price" in info
        assert "source" in info
        assert "last_updated" in info
