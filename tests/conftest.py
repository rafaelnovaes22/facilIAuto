"""
🧪 Configuração Central de Testes XP - CarFinder

Fixtures compartilhadas seguindo metodologia XP:
- Test Data Builders
- Fast Database Setup
- API Client Configuration
- Mock Data Factories
"""

import asyncio
import sqlite3
import tempfile
from typing import Dict, Generator, List

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app, init_db
from recommendations import SimpleCarRecommender


# ===== FIXTURES DE CONFIGURAÇÃO =====

@pytest.fixture(scope="session")
def event_loop():
    """Event loop para testes async (XP: Fast feedback)"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def temp_db():
    """
    Fixture para banco temporário (XP: Isolated tests)
    Cada teste tem seu próprio banco limpo
    """
    # Criar banco temporário
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_file.name
    temp_file.close()
    
    # Configurar banco temporário
    original_db = 'carfinder.db'
    
    # Patch the database path in main module
    import main
    main.sqlite3.connect = lambda path: sqlite3.connect(temp_db_path)
    
    # Initialize test database
    init_db()
    
    yield temp_db_path
    
    # Cleanup
    import os
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


@pytest.fixture
def client(temp_db):
    """
    Fixture para cliente de teste FastAPI (XP: Simple setup)
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(temp_db):
    """
    Fixture para cliente async (XP: Async testing)
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ===== FIXTURES DE DADOS =====

@pytest.fixture
def sample_questionnaire() -> Dict:
    """
    Fixture com questionário válido (XP: Known good state)
    """
    return {
        "answers": {
            "budget": "30k_50k",
            "usage": "work_app",
            "people": "1_2",
            "priority": "economy",
            "brand": ["chevrolet", "volkswagen"],
            "transmission": "manual",
            "age": "middle",
            "region": "sp"
        },
        "details": "Vou trabalhar como motorista de Uber, preciso de economia máxima",
        "session_id": "test_session_123"
    }


@pytest.fixture
def sample_car() -> Dict:
    """
    Fixture com dados de carro válido (XP: Test data builder)
    """
    return {
        "id": 1,
        "brand": "Chevrolet",
        "model": "Onix",
        "year": 2022,
        "price": 45000,
        "category": "hatch",
        "fuel_type": "flex",
        "transmission": "manual",
        "consumption": 14.2,
        "seats": 5,
        "safety_rating": 4,
        "region": "sp",
        "photo_url": None,
        "available": True
    }


@pytest.fixture
def sample_lead() -> Dict:
    """
    Fixture com lead válido (XP: Simple test data)
    """
    return {
        "car_id": 1,
        "name": "João Silva",
        "phone": "(11) 99999-9999",
        "email": "joao@email.com",
        "message": "Gostaria de mais informações sobre este carro"
    }


@pytest.fixture
def recommendation_engine():
    """
    Fixture para engine de recomendação (XP: Dependency injection)
    """
    return SimpleCarRecommender()


# ===== FIXTURES PARA E2E =====

@pytest.fixture
def browser_context_args(browser_context_args):
    """
    Configuração do browser para E2E (XP: Consistent environment)
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "pt-BR",
        "timezone_id": "America/Sao_Paulo"
    }


@pytest.fixture
def live_server_url():
    """
    URL do servidor para testes E2E (XP: Real environment)
    """
    return "http://localhost:8000"


# ===== FIXTURES DE MOCK DATA =====

@pytest.fixture
def mock_cars_data() -> List[Dict]:
    """
    Fixture com lista de carros para teste (XP: Predictable data)
    """
    return [
        {
            "id": 1,
            "brand": "Chevrolet",
            "model": "Onix",
            "year": 2022,
            "price": 45000,
            "category": "hatch",
            "transmission": "manual",
            "consumption": 14.2,
            "region": "sp"
        },
        {
            "id": 2,
            "brand": "Honda",
            "model": "Civic",
            "year": 2020,
            "price": 85000,
            "category": "sedan",
            "transmission": "automatic",
            "consumption": 11.5,
            "region": "sp"
        },
        {
            "id": 3,
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2021,
            "price": 92000,
            "category": "sedan",
            "transmission": "automatic",
            "consumption": 12.2,
            "region": "sp"
        }
    ]


# ===== UTILITIES PARA TESTES =====

@pytest.fixture
def db_session(temp_db):
    """
    Fixture para sessão de banco (XP: Database testing)
    """
    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def populate_test_cars(db_session, cars_data: List[Dict]):
    """
    Utility para popular banco com carros de teste (XP: Test helper)
    """
    cursor = db_session.cursor()
    
    for car in cars_data:
        cursor.execute('''
            INSERT INTO cars 
            (brand, model, year, price, category, fuel_type, transmission, 
             consumption, seats, safety_rating, region, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            car["brand"], car["model"], car["year"], car["price"],
            car["category"], car.get("fuel_type", "flex"), car["transmission"],
            car["consumption"], car.get("seats", 5), car.get("safety_rating", 4),
            car["region"], car.get("available", True)
        ))
    
    db_session.commit()
    return cursor.lastrowid


# ===== MARKERS PARA ORGANIZAÇÃO XP =====

def pytest_configure(config):
    """
    Configuração de markers XP (XP: Clear test organization)
    """
    config.addinivalue_line("markers", "user_story_1: Questionário funcional")
    config.addinivalue_line("markers", "user_story_2: Recomendações precisas")
    config.addinivalue_line("markers", "user_story_3: Sistema de leads")
    config.addinivalue_line("markers", "user_story_4: Dashboard admin")
    config.addinivalue_line("markers", "tdd_red: Teste falha primeiro (Red)")
    config.addinivalue_line("markers", "tdd_green: Implementação mínima (Green)")
    config.addinivalue_line("markers", "tdd_refactor: Refatoração (Refactor)")


# ===== HOOKS PARA RELATÓRIOS XP =====

@pytest.fixture(autouse=True)
def test_timing(request):
    """
    Auto-fixture para medir tempo de teste (XP: Fast feedback)
    """
    import time
    start_time = time.time()
    
    def fin():
        duration = time.time() - start_time
        if duration > 1.0:  # Slow test warning
            print(f"\n⚠️  SLOW TEST: {request.node.name} took {duration:.2f}s")
    
    request.addfinalizer(fin)