"""
Pytest configuration and shared fixtures for RobustCar Scraper tests
"""

import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "scraper": {
            "name": "robustcar-scraper",
            "version": "1.0.0",
            "source_url": "https://www.robustcar.com.br"
        },
        "http": {
            "timeout": 30,
            "max_retries": 3,
            "retry_backoff": 2.0
        },
        "rate_limiting": {
            "requests_per_minute": 60,
            "delay_between_requests": 1.0
        },
        "workers": {
            "max_concurrent": 3,
            "queue_size": 100
        },
        "quality": {
            "min_completeness": 0.95,
            "fail_threshold": 0.10
        }
    }


@pytest.fixture
def sample_vehicle_data():
    """Sample vehicle data for testing"""
    return {
        "id": "test_vehicle_1",
        "nome": "Toyota Corolla GLi",
        "marca": "Toyota",
        "modelo": "Corolla",
        "ano": 2022,
        "preco": 95000.0,
        "quilometragem": 45000,
        "combustivel": "Flex",
        "cambio": "Automático CVT",
        "cor": "Prata",
        "portas": 4,
        "categoria": "Sedan",
        "imagens": ["https://example.com/img1.jpg"],
        "descricao": "Veículo em excelente estado",
        "url_original": "https://www.robustcar.com.br/vehicle/1"
    }


@pytest.fixture
def sample_html_listing():
    """Sample HTML for listing page"""
    return """
    <html>
        <body>
            <div class="vehicles">
                <a href="/vehicle/1" class="vehicle-card">Vehicle 1</a>
                <a href="/vehicle/2" class="vehicle-card">Vehicle 2</a>
                <a href="/vehicle/3" class="vehicle-card">Vehicle 3</a>
            </div>
            <a href="/page/2" class="pagination-next">Next</a>
        </body>
    </html>
    """


@pytest.fixture
def sample_html_vehicle():
    """Sample HTML for vehicle detail page"""
    return """
    <html>
        <body>
            <h1 class="car-title">Toyota Corolla GLi</h1>
            <span class="car-price">R$ 95.990,00</span>
            <span class="brand">Toyota</span>
            <span class="model">Corolla</span>
            <span class="year">2022</span>
            <span class="mileage">45.000 km</span>
            <span class="fuel">Flex</span>
            <span class="transmission">Automático CVT</span>
            <span class="color">Prata</span>
            <span class="doors">4</span>
            <span class="category">Sedan</span>
            <div class="gallery">
                <img src="https://example.com/img1.jpg" />
                <img src="https://example.com/img2.jpg" />
            </div>
            <div class="description">Veículo em excelente estado</div>
        </body>
    </html>
    """
