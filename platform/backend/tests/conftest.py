"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
import os

# Adicionar backend ao path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from models.car import Car
from models.dealership import Dealership
from models.user_profile import UserProfile


@pytest.fixture
def sample_dealership():
    """Concessionária de exemplo"""
    return Dealership(
        id="test_dealer",
        name="Test Dealership",
        city="São Paulo",
        state="SP",
        region="Sudeste",
        phone="(11) 1234-5678",
        whatsapp="5511987654321",
        email="test@dealer.com",
        active=True,
        verified=True
    )


@pytest.fixture
def sample_car(sample_dealership):
    """Carro de exemplo"""
    return Car(
        id="test_car_001",
        dealership_id=sample_dealership.id,
        nome="FIAT CRONOS DRIVE 1.3",
        marca="Fiat",
        modelo="Cronos",
        versao="Drive 1.3",
        ano=2022,
        preco=84990.0,
        quilometragem=35000,
        combustivel="Flex",
        cambio="Manual",
        categoria="Sedan",
        score_familia=0.8,
        score_economia=0.9,
        score_performance=0.6,
        score_conforto=0.7,
        score_seguranca=0.8,
        dealership_name=sample_dealership.name,
        dealership_city=sample_dealership.city,
        dealership_state=sample_dealership.state,
        dealership_phone=sample_dealership.phone,
        dealership_whatsapp=sample_dealership.whatsapp,
        disponivel=True
    )


@pytest.fixture
def sample_user_profile():
    """Perfil de usuário de exemplo"""
    return UserProfile(
        orcamento_min=50000,
        orcamento_max=100000,
        city="São Paulo",
        state="SP",
        uso_principal="familia",
        tamanho_familia=4,
        necessita_espaco=True,
        tem_criancas=True,
        prioridades={
            "economia": 4,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        tipos_preferidos=["SUV", "Sedan"]
    )


@pytest.fixture
def multiple_cars(sample_dealership):
    """Lista de múltiplos carros para testes"""
    return [
        Car(
            id=f"test_car_{i:03d}",
            dealership_id=sample_dealership.id,
            nome=f"Test Car {i}",
            marca="Test",
            modelo=f"Model{i}",
            ano=2020 + (i % 5),
            preco=50000 + (i * 5000),
            quilometragem=30000 + (i * 5000),
            combustivel="Flex",
            categoria=["Hatch", "Sedan", "SUV"][i % 3],
            score_familia=0.5 + (i % 5) * 0.1,
            score_economia=0.5 + (i % 5) * 0.1,
            score_performance=0.5 + (i % 5) * 0.1,
            score_conforto=0.5 + (i % 5) * 0.1,
            score_seguranca=0.5 + (i % 5) * 0.1,
            dealership_name=sample_dealership.name,
            dealership_city=sample_dealership.city,
            dealership_state=sample_dealership.state,
            dealership_phone=sample_dealership.phone,
            dealership_whatsapp=sample_dealership.whatsapp,
            disponivel=True
        )
        for i in range(10)
    ]

