#!/usr/bin/env python3
"""
Script de teste para envio de mensagens via WhatsApp Business API

Usage:
    python scripts/test_whatsapp_send.py --to 5511999999999 --message "Olá!"
"""

import os
import sys
import argparse
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configurações
ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
API_VERSION = os.getenv('WHATSAPP_API_VERSION', 'v18.0')
API_BASE_URL = os.getenv('WHATSAPP_API_BASE_URL', 'https://graph.facebook.com')


def send_text_message(to: str, message: str) -> dict:
    """
    Enviar mensagem de texto via WhatsApp
    
    Args:
        to: Número de telefone do destinatário (formato: 5511999999999)
        message: Texto da mensagem
    
    Returns:
        Resposta da API
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
            "body": message
        }
    }
    
    print(f"📤 Enviando mensagem para {to}...")
    print(f"📝 Mensagem: {message}")
    print(f"🔗 URL: {url}")
    
    response = requests.post(url, headers=headers, json=payload)
    
    return response


def send_template_message(to: str, template_name: str = "hello_world") -> dict:
    """
    Enviar mensagem usando template aprovado
    
    Args:
        to: Número de telefone do destinatário
        template_name: Nome do template aprovado
    
    Returns:
        Resposta da API
    """
    url = f"{API_BASE_URL}/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "pt_BR"
            }
        }
    }
    
    print(f"📤 Enviando template '{template_name}' para {to}...")
    
    response = requests.post(url, headers=headers, json=payload)
    
    return response


def send_image_message(to: str, image_url: str, caption: str = "") -> dict:
    """
    Enviar mensagem com imagem
    
    Args:
        to: Número de telefone do destinatário
        image_url: URL pública da imagem
        caption: Legenda da imagem (opcional)
    
    Returns:
        Resposta da API
    """
    url = f"{API_BASE_URL}/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {
            "link": image_url
        }
    }
    
    if caption:
        payload["image"]["caption"] = caption
    
    print(f"📤 Enviando imagem para {to}...")
    print(f"🖼️  URL: {image_url}")
    if caption:
        print(f"📝 Legenda: {caption}")
    
    response = requests.post(url, headers=headers, json=payload)
    
    return response


def print_response(response: requests.Response):
    """Imprimir resposta formatada"""
    print("\n" + "="*60)
    print(f"Status Code: {response.status_code}")
    print("="*60)
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("\n✅ Mensagem enviada com sucesso!")
            if "messages" in data:
                message_id = data["messages"][0]["id"]
                print(f"📬 Message ID: {message_id}")
        else:
            print("\n❌ Erro ao enviar mensagem!")
            if "error" in data:
                error = data["error"]
                print(f"🔴 Erro: {error.get('message', 'Unknown error')}")
                print(f"🔴 Código: {error.get('code', 'N/A')}")
                print(f"🔴 Tipo: {error.get('type', 'N/A')}")
    except json.JSONDecodeError:
        print(response.text)
    
    print("="*60 + "\n")


def validate_config():
    """Validar configurações necessárias"""
    if not ACCESS_TOKEN:
        print("❌ WHATSAPP_ACCESS_TOKEN não configurado no .env")
        return False
    
    if not PHONE_NUMBER_ID:
        print("❌ WHATSAPP_PHONE_NUMBER_ID não configurado no .env")
        return False
    
    print("✅ Configurações validadas")
    print(f"📱 Phone Number ID: {PHONE_NUMBER_ID}")
    print(f"🔑 Access Token: {ACCESS_TOKEN[:20]}...")
    print()
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Testar envio de mensagens via WhatsApp Business API"
    )
    parser.add_argument(
        "--to",
        required=True,
        help="Número de telefone do destinatário (ex: 5511999999999)"
    )
    parser.add_argument(
        "--message",
        help="Mensagem de texto a enviar"
    )
    parser.add_argument(
        "--template",
        help="Nome do template a enviar"
    )
    parser.add_argument(
        "--image",
        help="URL da imagem a enviar"
    )
    parser.add_argument(
        "--caption",
        help="Legenda da imagem"
    )
    
    args = parser.parse_args()
    
    # Validar configurações
    if not validate_config():
        sys.exit(1)
    
    # Enviar mensagem apropriada
    if args.message:
        response = send_text_message(args.to, args.message)
        print_response(response)
    
    elif args.template:
        response = send_template_message(args.to, args.template)
        print_response(response)
    
    elif args.image:
        response = send_image_message(args.to, args.image, args.caption or "")
        print_response(response)
    
    else:
        print("❌ Especifique --message, --template ou --image")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
