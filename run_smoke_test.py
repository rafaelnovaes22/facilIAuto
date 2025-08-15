#!/usr/bin/env python3
"""
🧪 Executor do Smoke Test E2E - FacilIAuto
Script simplificado para executar o teste crítico
"""
import subprocess
import sys
import time
import requests
from typing import Optional


def check_server_health(url: str = "http://localhost:8000", max_retries: int = 5) -> bool:
    """
    Verifica se o servidor está rodando e saudável
    
    Args:
        url: URL base do servidor
        max_retries: Número máximo de tentativas
        
    Returns:
        True se servidor está saudável
    """
    print(f"🏥 Verificando saúde do servidor em {url}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Servidor está saudável!")
                return True
        except Exception as e:
            print(f"⏳ Tentativa {attempt + 1}/{max_retries} - Servidor não disponível: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    print(f"❌ Servidor não está disponível após {max_retries} tentativas")
    return False


def run_smoke_test(browser: str = "chromium") -> bool:
    """
    Executa o smoke test E2E
    
    Args:
        browser: Browser para usar (chromium, firefox, webkit)
        
    Returns:
        True se teste passou
    """
    print(f"🧪 Executando smoke test com {browser}")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/e2e/test_smoke.py",
        f"--browser={browser}",
        "-v",
        "--tb=short",
        "--no-header"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Mostrar output
        if result.stdout:
            print("📋 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("🔍 STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ SMOKE TEST PASSOU!")
            return True
        else:
            print(f"❌ SMOKE TEST FALHOU (código: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ SMOKE TEST TIMEOUT após 5 minutos")
        return False
    except Exception as e:
        print(f"💥 ERRO ao executar smoke test: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 FACILIAUTO - SMOKE TEST E2E")
    print("=" * 60)
    
    # 1. Verificar servidor
    if not check_server_health():
        print("❌ Servidor não está disponível. Inicie com: python main.py")
        sys.exit(1)
    
    # 2. Executar teste
    browser = sys.argv[1] if len(sys.argv) > 1 else "chromium"
    
    if run_smoke_test(browser):
        print("\n🎉 SUCESSO: Smoke test passou - Sistema funcionando!")
        sys.exit(0)
    else:
        print("\n💥 FALHA: Smoke test falhou - Verifique o sistema!")
        sys.exit(1)


if __name__ == "__main__":
    main()
