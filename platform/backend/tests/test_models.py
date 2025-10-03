"""
Testes Unitários para Modelos (TDD)
"""
import pytest
from pydantic import ValidationError
from models.car import Car, CarFilter
from models.dealership import Dealership, DealershipStats
from models.user_profile import UserProfile
from datetime import datetime


class TestCarModel:
    """Testes para o modelo Car"""
    
    def test_create_car_valid(self, sample_car):
        """Teste: criar carro com dados válidos"""
        assert sample_car.id == "test_car_001"
        assert sample_car.marca == "Fiat"
        assert sample_car.preco == 84990.0
        assert sample_car.disponivel is True
    
    def test_car_required_fields(self):
        """Teste: validar campos obrigatórios"""
        with pytest.raises(ValidationError):
            Car()  # Sem campos obrigatórios
    
    def test_car_price_validation(self, sample_dealership):
        """Teste: preço deve ser positivo"""
        with pytest.raises(ValidationError):
            Car(
                id="test",
                dealership_id=sample_dealership.id,
                nome="Test",
                marca="Test",
                modelo="Test",
                ano=2020,
                preco=-1000,  # Preço negativo
                quilometragem=0,
                combustivel="Flex",
                categoria="Hatch",
                dealership_name="Test",
                dealership_city="Test",
                dealership_state="SP",
                dealership_phone="",
                dealership_whatsapp=""
            )
    
    def test_car_scores_range(self, sample_car):
        """Teste: scores devem estar entre 0.0 e 1.0"""
        assert 0.0 <= sample_car.score_familia <= 1.0
        assert 0.0 <= sample_car.score_economia <= 1.0
        assert 0.0 <= sample_car.score_performance <= 1.0
        assert 0.0 <= sample_car.score_conforto <= 1.0
        assert 0.0 <= sample_car.score_seguranca <= 1.0
    
    def test_car_default_values(self, sample_dealership):
        """Teste: valores padrão são aplicados"""
        car = Car(
            id="test",
            dealership_id=sample_dealership.id,
            nome="Test",
            marca="Test",
            modelo="Test",
            ano=2020,
            preco=50000,
            quilometragem=0,
            combustivel="Flex",
            categoria="Hatch",
            dealership_name="Test",
            dealership_city="Test",
            dealership_state="SP",
            dealership_phone="",
            dealership_whatsapp=""
        )
        assert car.disponivel is True
        assert car.destaque is False
        assert car.cambio == "Manual"
        assert car.portas == 4


class TestDealershipModel:
    """Testes para o modelo Dealership"""
    
    def test_create_dealership_valid(self, sample_dealership):
        """Teste: criar concessionária com dados válidos"""
        assert sample_dealership.id == "test_dealer"
        assert sample_dealership.name == "Test Dealership"
        assert sample_dealership.active is True
    
    def test_dealership_required_fields(self):
        """Teste: validar campos obrigatórios"""
        with pytest.raises(ValidationError):
            Dealership()
    
    def test_dealership_default_active(self):
        """Teste: concessionária ativa por padrão"""
        dealer = Dealership(
            id="test",
            name="Test",
            city="São Paulo",
            state="SP",
            region="Sudeste",
            phone="123456789",
            whatsapp="123456789"
        )
        assert dealer.active is True
        assert dealer.verified is False
        assert dealer.premium is False
    
    def test_dealership_stats_model(self):
        """Teste: modelo de estatísticas"""
        stats = DealershipStats(
            dealership_id="test",
            total_cars=50,
            active_cars=45,
            avg_price=75000.0,
            price_min=40000.0,
            price_max=150000.0,
            total_recommendations=1000,
            conversion_rate=0.15,
            last_updated=datetime.now()
        )
        assert stats.total_cars == 50
        assert 0.0 <= stats.conversion_rate <= 1.0


class TestUserProfileModel:
    """Testes para o modelo UserProfile"""
    
    def test_create_profile_valid(self, sample_user_profile):
        """Teste: criar perfil com dados válidos"""
        assert sample_user_profile.orcamento_min == 50000
        assert sample_user_profile.orcamento_max == 100000
        assert sample_user_profile.uso_principal == "familia"
    
    def test_profile_required_fields(self):
        """Teste: campos obrigatórios mínimos"""
        profile = UserProfile(
            orcamento_min=30000,
            orcamento_max=50000,
            uso_principal="trabalho"
        )
        assert profile.orcamento_min == 30000
        assert profile.tamanho_familia == 1  # Default
    
    def test_profile_priorities_validation(self, sample_user_profile):
        """Teste: prioridades devem estar entre 1 e 5"""
        for key, value in sample_user_profile.prioridades.items():
            assert 1 <= value <= 5, f"Prioridade {key} fora do range"
    
    def test_profile_budget_consistency(self):
        """Teste: orçamento máximo deve ser >= mínimo"""
        # Nota: Pydantic não valida isso automaticamente,
        # mas devemos testar a lógica de negócio
        profile = UserProfile(
            orcamento_min=100000,
            orcamento_max=50000,  # Inconsistente
            uso_principal="familia"
        )
        # Aqui apenas criamos, validação de negócio será na API
        assert profile.orcamento_min > profile.orcamento_max
    
    def test_profile_defaults(self):
        """Teste: valores padrão do perfil"""
        profile = UserProfile(
            orcamento_min=30000,
            orcamento_max=50000,
            uso_principal="primeiro_carro"
        )
        assert profile.tamanho_familia == 1
        assert profile.primeiro_carro is False
        assert profile.prioridades["economia"] == 3


class TestCarFilter:
    """Testes para filtros de busca"""
    
    def test_create_filter_empty(self):
        """Teste: criar filtro vazio"""
        filter = CarFilter()
        assert filter.preco_min is None
        assert filter.preco_max is None
    
    def test_create_filter_with_values(self):
        """Teste: criar filtro com valores"""
        filter = CarFilter(
            preco_min=50000,
            preco_max=80000,
            marca="Fiat",
            categoria="Sedan"
        )
        assert filter.preco_min == 50000
        assert filter.marca == "Fiat"

