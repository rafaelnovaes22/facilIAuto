"""
🧪 E2E Tests Configuration - Playwright
Configuração específica para testes end-to-end
"""

import asyncio
import subprocess
import time

import pytest
import requests
from playwright.async_api import async_playwright


# Event loop fixture removido - usando o do conftest.py principal


@pytest.fixture(scope="session")
async def browser():
    """Browser instance para testes E2E"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,  # Mudar para False para debug visual
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser):
    """Browser context para isolamento de testes"""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context):
    """Page instance para testes"""
    page = await context.new_page()
    yield page
    await page.close()


@pytest.fixture(scope="session")
def app_server():
    """Servidor da aplicação para testes E2E"""
    # Verificar se o servidor já está rodando
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor já está rodando")
            yield "http://localhost:8000"
            return
    except Exception:
        pass

    # Iniciar servidor para testes
    print("🚀 Iniciando servidor para testes E2E...")
    process = subprocess.Popen(
        ["python", "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Aguardar servidor inicializar
    for _ in range(30):  # 30 segundos timeout
        try:
            response = requests.get("http://localhost:8000/health", timeout=1)
            if response.status_code == 200:
                print("✅ Servidor iniciado com sucesso")
                break
        except Exception:
            time.sleep(1)
    else:
        process.terminate()
        raise Exception("Falha ao iniciar servidor para testes")

    yield "http://localhost:8000"

    # Cleanup
    process.terminate()
    process.wait()
    print("🛑 Servidor de testes encerrado")


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup automático para cada teste"""
    # Configurações globais para todos os testes - versão não-async
    pass


@pytest.fixture
async def mock_api_responses(page):
    """Mock de respostas da API para testes isolados"""
    # Mock de resposta de busca bem-sucedida
    await page.route(
        "**/buscar",
        lambda route: route.fulfill(
            json={
                "recomendacoes": [
                    {
                        "id": "test-1",
                        "marca": "Toyota",
                        "modelo": "Corolla",
                        "ano": 2022,
                        "preco": 65000,
                        "km": 25000,
                        "combustivel": "Flex",
                        "cor": "Branco",
                        "score_compatibilidade": 95.5,
                        "razoes_recomendacao": ["Marca preferida", "Modelo específico"],
                        "pontos_fortes": ["Econômico", "Confiável"],
                        "consideracoes": ["Considere o consumo"],
                        "fotos": ["https://via.placeholder.com/300x200"],
                        "descricao": "Corolla 2022 em excelente estado",
                    }
                ],
                "resumo_perfil": "Você busca um carro econômico da Toyota para uso urbano",
                "sugestoes_gerais": [
                    "Considere fazer um test drive antes da compra",
                    "Verifique o histórico de manutenção",
                ],
            }
        ),
    )

    # Mock de validação de preferências
    await page.route(
        "**/api/validate-preferences",
        lambda route: route.fulfill(
            json={
                "is_valid": True,
                "confidence_score": 0.95,
                "suggestions": [],
                "normalized_data": {
                    "marca_principal": {"normalizada": "TOYOTA"},
                    "modelo_principal": {"normalizado": "Corolla"},
                },
                "validation_issues": [],
                "processing_quality": "excellent",
            }
        ),
    )

    # Mock de auto-complete
    await page.route(
        "**/api/autocomplete/**",
        lambda route: route.fulfill(
            json={"suggestions": ["Corolla", "Camry", "Civic"]}
        ),
    )
