"""
🧪 Configuração E2E - Smoke Test Minimalista
Configuração leve apenas para validação crítica
"""
import asyncio
import logging
import subprocess
import sys
import time
from typing import Generator

import pytest
import requests
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def live_server() -> str:
    """
    URL do servidor para testes E2E
    Assume que o servidor está rodando em localhost:8000
    """
    return "http://localhost:8000"


@pytest.fixture(scope="session", autouse=True)
def ensure_server_running(live_server: str) -> Generator[None, None, None]:
    """
    Garante que o servidor está rodando antes dos testes
    """
    print(f"\n🚀 [E2E] Verificando servidor em {live_server}")
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(f"{live_server}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ [E2E] Servidor está rodando e saudável")
                break
        except Exception as e:
            retry_count += 1
            if retry_count == 1:
                print(f"⏳ [E2E] Servidor não disponível, tentando iniciar...")
                # Tentar iniciar o servidor em background
                try:
                    subprocess.Popen([
                        sys.executable, "main.py"
                    ], cwd=".", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"🚀 [E2E] Servidor iniciado em background")
                except Exception as start_error:
                    print(f"⚠️ [E2E] Erro ao iniciar servidor: {start_error}")
            
            print(f"⏳ [E2E] Tentativa {retry_count}/{max_retries} - Aguardando servidor...")
            time.sleep(2)
    
    if retry_count >= max_retries:
        pytest.fail(f"❌ [E2E] Servidor não está disponível em {live_server} após {max_retries} tentativas")
    
    yield
    
    print(f"🏁 [E2E] Testes E2E finalizados")


@pytest.fixture
def enhanced_page(page: Page) -> Page:
    """
    Página com configurações otimizadas para estabilidade
    """
    # Configurações para estabilidade
    page.set_default_timeout(30000)  # 30s timeout padrão
    page.set_default_navigation_timeout(30000)  # 30s para navegação
    
    # Log de console para debug
    page.on("console", lambda msg: print(f"🖥️ [CONSOLE] {msg.type}: {msg.text}"))
    
    # Log de erros de página
    page.on("pageerror", lambda error: print(f"❌ [PAGE ERROR] {error}"))
    
    # Log de requests falhados
    page.on("requestfailed", lambda request: print(f"🌐 [REQUEST FAILED] {request.url}"))
    
    return page


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
