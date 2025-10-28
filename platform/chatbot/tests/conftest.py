"""Pytest configuration and shared fixtures."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI application."""
    from src.main import app
    return TestClient(app)


@pytest.fixture
async def mock_redis():
    """Mock Redis client for testing."""
    # TODO: Implement mock Redis client
    pass


@pytest.fixture
async def mock_postgres():
    """Mock PostgreSQL connection for testing."""
    # TODO: Implement mock PostgreSQL connection
    pass


@pytest.fixture
async def mock_whatsapp_api():
    """Mock WhatsApp API for testing."""
    # TODO: Implement mock WhatsApp API
    pass


@pytest.fixture
def sample_whatsapp_message():
    """Sample WhatsApp message payload for testing."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "5511999999999",
                                "phone_number_id": "123456789",
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Test User"},
                                    "wa_id": "5511888888888",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5511888888888",
                                    "id": "wamid.test123",
                                    "timestamp": "1234567890",
                                    "text": {"body": "Olá, quero comprar um carro"},
                                    "type": "text",
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing."""
    return {
        "orcamento_min": 40000,
        "orcamento_max": 60000,
        "uso_principal": "trabalho",
        "city": "São Paulo",
        "state": "SP",
        "prioridades": {
            "economia": 8,
            "conforto": 7,
            "seguranca": 9,
        },
        "marcas_preferidas": ["Toyota", "Honda"],
        "tipos_preferidos": ["sedan", "hatch"],
    }
