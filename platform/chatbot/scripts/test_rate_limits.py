#!/usr/bin/env python3
"""
Script para testar rate limits da WhatsApp Business API

Este script envia múltiplas mensagens para validar os limites de taxa:
- Tier gratuito: 80 mensagens/segundo, 1000 mensagens/minuto

Usage:
    python scripts/test_rate_limits.py --to 5511999999999 --count 10
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configurações
ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v18.0')
API_BASE_URL = os.getenv('WHATSAPP_API_BASE_URL', 'https://graph.facebook.com')


def send_message(to: str, message: str, index: int) -> dict:
    """
    Enviar uma mensagem
    
    Args:
        to: Número do destinatário
        message: Texto da mensagem
        index: Índice da mensagem
    
    Returns:
        Dict com resultado
    """
    url = f"{API_BASE_URL}/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": f"{message} (#{index})"
        }
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        elapsed = time.time() - start_time
        
        return {
            "index": index,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "elapsed": elapsed,
            "response": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "index": index,
            "status_code": 0,
            "success": False,
            "elapsed": elapsed,
            "error": str(e)
        }


def test_sequential(to: str, message: str, count: int, delay: float = 0):
    """
    Testar envio sequencial de mensagens
    
    Args:
        to: Número do destinatário
        message: Texto base da mensagem
        count: Quantidade de mensagens
        delay: Delay entre mensagens (segundos)
    """
    print(f"\n📤 Teste Sequencial: {count} mensagens")
    print(f"⏱️  Delay entre mensagens: {delay}s")
    print("="*60)
    
    results = []
    start_time = time.time()
    
    for i in range(1, count + 1):
        result = send_message(to, message, i)
        results.append(result)
        
        status = "✅" if result["success"] else "❌"
        print(f"{status} Mensagem {i}/{count} - "
              f"Status: {result['status_code']} - "
              f"Tempo: {result['elapsed']:.2f}s")
        
        if delay > 0 and i < count:
            time.sleep(delay)
    
    total_time = time.time() - start_time
    
    print_summary(results, total_time)


def test_parallel(to: str, message: str, count: int, workers: int = 10):
    """
    Testar envio paralelo de mensagens
    
    Args:
        to: Número do destinatário
        message: Texto base da mensagem
        count: Quantidade de mensagens
        workers: Número de threads paralelas
    """
    print(f"\n📤 Teste Paralelo: {count} mensagens com {workers} workers")
    print("="*60)
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(send_message, to, message, i): i 
            for i in range(1, count + 1)
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            status = "✅" if result["success"] else "❌"
            print(f"{status} Mensagem {result['index']}/{count} - "
                  f"Status: {result['status_code']} - "
                  f"Tempo: {result['elapsed']:.2f}s")
    
    total_time = time.time() - start_time
    
    print_summary(results, total_time)


def print_summary(results: list, total_time: float):
    """Imprimir resumo dos resultados"""
    print("\n" + "="*60)
    print("📊 RESUMO")
    print("="*60)
    
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    failed = total - successful
    
    avg_time = sum(r["elapsed"] for r in results) / total if total > 0 else 0
    min_time = min(r["elapsed"] for r in results) if results else 0
    max_time = max(r["elapsed"] for r in results) if results else 0
    
    rate = total / total_time if total_time > 0 else 0
    
    print(f"Total de mensagens: {total}")
    print(f"✅ Sucesso: {successful} ({successful/total*100:.1f}%)")
    print(f"❌ Falhas: {failed} ({failed/total*100:.1f}%)")
    print(f"\n⏱️  Tempo total: {total_time:.2f}s")
    print(f"📈 Taxa: {rate:.2f} mensagens/segundo")
    print(f"\n⏱️  Tempo por mensagem:")
    print(f"   Média: {avg_time:.2f}s")
    print(f"   Mínimo: {min_time:.2f}s")
    print(f"   Máximo: {max_time:.2f}s")
    
    # Verificar rate limit
    if rate > 80:
        print(f"\n⚠️  ATENÇÃO: Taxa de {rate:.2f} msg/s excede o limite de 80 msg/s")
    else:
        print(f"\n✅ Taxa dentro do limite (80 msg/s)")
    
    # Mostrar erros
    errors = [r for r in results if not r["success"]]
    if errors:
        print(f"\n❌ Erros encontrados:")
        for error in errors[:5]:  # Mostrar apenas os primeiros 5
            print(f"   Mensagem {error['index']}: {error.get('error', error.get('response'))}")
        if len(errors) > 5:
            print(f"   ... e mais {len(errors) - 5} erros")
    
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Testar rate limits da WhatsApp Business API"
    )
    parser.add_argument(
        "--to",
        required=True,
        help="Número de telefone do destinatário (ex: 5511999999999)"
    )
    parser.add_argument(
        "--message",
        default="Teste de rate limit",
        help="Mensagem base a enviar"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Quantidade de mensagens a enviar (padrão: 10)"
    )
    parser.add_argument(
        "--mode",
        choices=["sequential", "parallel"],
        default="sequential",
        help="Modo de envio (padrão: sequential)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0,
        help="Delay entre mensagens em modo sequencial (segundos)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Número de workers em modo paralelo (padrão: 10)"
    )
    
    args = parser.parse_args()
    
    # Validar configurações
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("❌ Configurações não encontradas no .env")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🧪 TESTE DE RATE LIMITS - WhatsApp Business API")
    print("="*60)
    print(f"📱 Para: {args.to}")
    print(f"📝 Mensagem: {args.message}")
    print(f"🔢 Quantidade: {args.count}")
    print(f"🔄 Modo: {args.mode}")
    
    if args.mode == "sequential":
        print(f"⏱️  Delay: {args.delay}s")
    else:
        print(f"👷 Workers: {args.workers}")
    
    print("\n⚠️  AVISO: Este teste enviará mensagens reais!")
    print("⚠️  Certifique-se de usar um número de teste.")
    
    response = input("\nDeseja continuar? (s/n): ")
    if response.lower() != 's':
        print("❌ Teste cancelado")
        sys.exit(0)
    
    # Executar teste
    if args.mode == "sequential":
        test_sequential(args.to, args.message, args.count, args.delay)
    else:
        test_parallel(args.to, args.message, args.count, args.workers)


if __name__ == "__main__":
    main()
