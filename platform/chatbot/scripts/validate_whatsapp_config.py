#!/usr/bin/env python3
"""
Script para validar configuração da WhatsApp Business API

Este script verifica se todas as credenciais estão configuradas corretamente
e testa a conectividade com a API.

Usage:
    python scripts/validate_whatsapp_config.py
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configurações
ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
BUSINESS_ACCOUNT_ID = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')
APP_SECRET = os.getenv('WHATSAPP_APP_SECRET')
VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v18.0')
API_BASE_URL = os.getenv('WHATSAPP_API_BASE_URL', 'https://graph.facebook.com')


def print_header(title: str):
    """Imprimir cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_check(label: str, value: any, is_valid: bool):
    """Imprimir resultado de verificação"""
    status = "✅" if is_valid else "❌"
    if value and len(str(value)) > 50:
        display_value = str(value)[:20] + "..." + str(value)[-10:]
    else:
        display_value = value if value else "NÃO CONFIGURADO"
    
    print(f"{status} {label}: {display_value}")


def validate_env_vars() -> bool:
    """Validar variáveis de ambiente"""
    print_header("1. Validando Variáveis de Ambiente")
    
    all_valid = True
    
    # Obrigatórias
    print_check("WHATSAPP_ACCESS_TOKEN", ACCESS_TOKEN, bool(ACCESS_TOKEN))
    if not ACCESS_TOKEN:
        all_valid = False
    
    print_check("WHATSAPP_PHONE_NUMBER_ID", PHONE_NUMBER_ID, bool(PHONE_NUMBER_ID))
    if not PHONE_NUMBER_ID:
        all_valid = False
    
    print_check("WEBHOOK_VERIFY_TOKEN", VERIFY_TOKEN, bool(VERIFY_TOKEN))
    if not VERIFY_TOKEN:
        all_valid = False
    
    # Opcionais mas recomendadas
    print_check("WHATSAPP_BUSINESS_ACCOUNT_ID", BUSINESS_ACCOUNT_ID, bool(BUSINESS_ACCOUNT_ID))
    print_check("WHATSAPP_APP_SECRET", APP_SECRET, bool(APP_SECRET))
    
    return all_valid


def validate_token() -> bool:
    """Validar token de acesso"""
    print_header("2. Validando Token de Acesso")
    
    if not ACCESS_TOKEN:
        print("❌ Token não configurado")
        return False
    
    # Tentar fazer uma requisição simples
    url = f"{API_BASE_URL}/{API_VERSION}/me"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    try:
        print("🔄 Testando token...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token válido!")
            print(f"   App ID: {data.get('id')}")
            print(f"   App Name: {data.get('name', 'N/A')}")
            return True
        else:
            print(f"❌ Token inválido!")
            print(f"   Status: {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao validar token: {e}")
        return False


def validate_phone_number() -> bool:
    """Validar Phone Number ID"""
    print_header("3. Validando Phone Number ID")
    
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("❌ Credenciais não configuradas")
        return False
    
    url = f"{API_BASE_URL}/{API_VERSION}/{PHONE_NUMBER_ID}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    try:
        print("🔄 Testando Phone Number ID...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Phone Number ID válido!")
            print(f"   Número: {data.get('display_phone_number')}")
            print(f"   Status: {data.get('verified_name', 'N/A')}")
            print(f"   Quality: {data.get('quality_rating', 'N/A')}")
            return True
        else:
            print(f"❌ Phone Number ID inválido!")
            print(f"   Status: {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao validar Phone Number ID: {e}")
        return False


def validate_business_account() -> bool:
    """Validar Business Account ID"""
    print_header("4. Validando Business Account ID")
    
    if not BUSINESS_ACCOUNT_ID:
        print("⚠️  Business Account ID não configurado (opcional)")
        return True
    
    if not ACCESS_TOKEN:
        print("❌ Token não configurado")
        return False
    
    url = f"{API_BASE_URL}/{API_VERSION}/{BUSINESS_ACCOUNT_ID}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    try:
        print("🔄 Testando Business Account ID...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Business Account ID válido!")
            print(f"   Nome: {data.get('name', 'N/A')}")
            print(f"   ID: {data.get('id')}")
            return True
        else:
            print(f"⚠️  Business Account ID pode estar incorreto")
            print(f"   Status: {response.status_code}")
            return True  # Não é crítico
    except Exception as e:
        print(f"⚠️  Erro ao validar Business Account ID: {e}")
        return True  # Não é crítico


def test_send_message() -> bool:
    """Testar envio de mensagem (simulado)"""
    print_header("5. Testando Capacidade de Envio")
    
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("❌ Credenciais não configuradas")
        return False
    
    # Não vamos enviar mensagem real, apenas validar o endpoint
    url = f"{API_BASE_URL}/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
    
    print(f"✅ Endpoint de envio configurado:")
    print(f"   URL: {url}")
    print(f"   Método: POST")
    print(f"   Auth: Bearer Token")
    
    print("\n💡 Para testar envio real, use:")
    print("   python scripts/test_whatsapp_send.py --to 5511999999999 --message 'Teste'")
    
    return True


def check_rate_limits() -> bool:
    """Verificar informações sobre rate limits"""
    print_header("6. Informações sobre Rate Limits")
    
    print("📊 Limites da WhatsApp Business API:")
    print("   • Tier Gratuito: 1.000 conversas/mês")
    print("   • Rate Limit: 80 mensagens/segundo")
    print("   • Rate Limit: 1.000 mensagens/minuto")
    print("\n💡 Para testar rate limits, use:")
    print("   python scripts/test_rate_limits.py --to 5511999999999 --count 10")
    
    return True


def print_summary(results: dict):
    """Imprimir resumo final"""
    print_header("RESUMO DA VALIDAÇÃO")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\n📊 Resultados:")
    print(f"   Total de verificações: {total}")
    print(f"   ✅ Passou: {passed}")
    print(f"   ❌ Falhou: {failed}")
    
    print(f"\n📋 Detalhes:")
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    if failed == 0:
        print("\n🎉 Todas as verificações passaram!")
        print("✅ Sua configuração está pronta para uso.")
        print("\n📚 Próximos passos:")
        print("   1. Testar envio: python scripts/test_whatsapp_send.py")
        print("   2. Configurar webhook: python scripts/test_whatsapp_webhook.py")
        print("   3. Ver guia completo: docs/WHATSAPP_SETUP_GUIDE.md")
    else:
        print("\n⚠️  Algumas verificações falharam.")
        print("📚 Consulte o guia de configuração:")
        print("   docs/WHATSAPP_SETUP_GUIDE.md")
    
    print("="*60 + "\n")
    
    return failed == 0


def main():
    print("\n" + "="*60)
    print("  🔍 VALIDAÇÃO DE CONFIGURAÇÃO - WhatsApp Business API")
    print("="*60)
    print("\nEste script irá validar sua configuração do WhatsApp.")
    print("Certifique-se de ter configurado o arquivo .env corretamente.\n")
    
    # Executar validações
    results = {
        "Variáveis de Ambiente": validate_env_vars(),
        "Token de Acesso": validate_token(),
        "Phone Number ID": validate_phone_number(),
        "Business Account ID": validate_business_account(),
        "Capacidade de Envio": test_send_message(),
        "Rate Limits": check_rate_limits(),
    }
    
    # Imprimir resumo
    success = print_summary(results)
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
