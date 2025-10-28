#!/usr/bin/env python3
"""
Script de teste para webhook do WhatsApp Business API

Este script simula o servidor webhook para receber mensagens do WhatsApp.
Use com ngrok para expor localmente durante desenvolvimento.

Usage:
    python scripts/test_whatsapp_webhook.py
"""

import os
import hmac
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
import uvicorn
import json

# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configurações
VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN')
APP_SECRET = os.getenv('WHATSAPP_APP_SECRET')

app = FastAPI(title="WhatsApp Webhook Test Server")


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verificar assinatura do webhook
    
    Args:
        payload: Corpo da requisição (bytes)
        signature: Header X-Hub-Signature-256
    
    Returns:
        True se assinatura válida
    """
    if not APP_SECRET:
        print("⚠️  APP_SECRET não configurado, pulando validação de assinatura")
        return True
    
    expected_signature = hmac.new(
        APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Remover prefixo "sha256="
    received_signature = signature.replace('sha256=', '') if signature else ''
    
    is_valid = hmac.compare_digest(expected_signature, received_signature)
    
    if not is_valid:
        print(f"❌ Assinatura inválida!")
        print(f"   Esperado: {expected_signature}")
        print(f"   Recebido: {received_signature}")
    
    return is_valid


@app.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    """
    Endpoint de verificação do webhook (chamado pelo Meta)
    
    O Meta faz uma requisição GET para verificar o webhook:
    GET /webhook/whatsapp?hub.mode=subscribe&hub.challenge=123&hub.verify_token=token
    
    Devemos retornar o hub.challenge se o token estiver correto.
    """
    print("\n" + "="*60)
    print("📥 Requisição de verificação do webhook recebida")
    print("="*60)
    print(f"Mode: {hub_mode}")
    print(f"Challenge: {hub_challenge}")
    print(f"Verify Token: {hub_verify_token}")
    print("="*60)
    
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("✅ Token verificado com sucesso!")
        print(f"📤 Retornando challenge: {hub_challenge}")
        print("="*60 + "\n")
        return PlainTextResponse(content=hub_challenge)
    else:
        print("❌ Token de verificação inválido!")
        print(f"   Esperado: {VERIFY_TOKEN}")
        print(f"   Recebido: {hub_verify_token}")
        print("="*60 + "\n")
        raise HTTPException(status_code=403, detail="Invalid verify token")


@app.post("/webhook/whatsapp")
async def handle_webhook(request: Request):
    """
    Endpoint para receber mensagens do WhatsApp
    
    O Meta envia um POST com o seguinte formato:
    {
      "object": "whatsapp_business_account",
      "entry": [{
        "id": "BUSINESS_ACCOUNT_ID",
        "changes": [{
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {...},
            "contacts": [{...}],
            "messages": [{...}]
          },
          "field": "messages"
        }]
      }]
    }
    """
    # Obter corpo da requisição
    body = await request.body()
    
    # Verificar assinatura
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse JSON
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Imprimir payload recebido
    print("\n" + "="*60)
    print("📥 Webhook recebido do WhatsApp")
    print("="*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("="*60)
    
    # Processar mensagens
    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    
                    # Extrair metadados
                    metadata = value.get("metadata", {})
                    print(f"\n📱 Número do negócio: {metadata.get('display_phone_number')}")
                    print(f"🆔 Phone Number ID: {metadata.get('phone_number_id')}")
                    
                    # Extrair contatos
                    contacts = value.get("contacts", [])
                    for contact in contacts:
                        print(f"\n👤 Contato:")
                        print(f"   Nome: {contact.get('profile', {}).get('name')}")
                        print(f"   WhatsApp ID: {contact.get('wa_id')}")
                    
                    # Extrair mensagens
                    messages = value.get("messages", [])
                    for message in messages:
                        print(f"\n💬 Mensagem:")
                        print(f"   ID: {message.get('id')}")
                        print(f"   De: {message.get('from')}")
                        print(f"   Tipo: {message.get('type')}")
                        print(f"   Timestamp: {message.get('timestamp')}")
                        
                        # Conteúdo baseado no tipo
                        msg_type = message.get('type')
                        if msg_type == 'text':
                            text = message.get('text', {}).get('body', '')
                            print(f"   Texto: {text}")
                        elif msg_type == 'image':
                            image = message.get('image', {})
                            print(f"   Imagem ID: {image.get('id')}")
                            print(f"   MIME Type: {image.get('mime_type')}")
                            print(f"   Caption: {image.get('caption', 'N/A')}")
                        elif msg_type == 'audio':
                            audio = message.get('audio', {})
                            print(f"   Áudio ID: {audio.get('id')}")
                            print(f"   MIME Type: {audio.get('mime_type')}")
                        elif msg_type == 'document':
                            document = message.get('document', {})
                            print(f"   Documento ID: {document.get('id')}")
                            print(f"   Filename: {document.get('filename')}")
                            print(f"   MIME Type: {document.get('mime_type')}")
                        elif msg_type == 'location':
                            location = message.get('location', {})
                            print(f"   Latitude: {location.get('latitude')}")
                            print(f"   Longitude: {location.get('longitude')}")
                            print(f"   Nome: {location.get('name', 'N/A')}")
                            print(f"   Endereço: {location.get('address', 'N/A')}")
                    
                    # Extrair status de mensagens
                    statuses = value.get("statuses", [])
                    for status in statuses:
                        print(f"\n📊 Status de mensagem:")
                        print(f"   ID: {status.get('id')}")
                        print(f"   Status: {status.get('status')}")
                        print(f"   Timestamp: {status.get('timestamp')}")
                        print(f"   Para: {status.get('recipient_id')}")
    
    print("="*60 + "\n")
    
    # Retornar 200 OK para confirmar recebimento
    return {"status": "ok"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "whatsapp-webhook-test",
        "verify_token_configured": bool(VERIFY_TOKEN),
        "app_secret_configured": bool(APP_SECRET)
    }


def main():
    print("\n" + "="*60)
    print("🚀 Iniciando servidor de teste do webhook WhatsApp")
    print("="*60)
    print(f"✅ Verify Token: {VERIFY_TOKEN}")
    print(f"✅ App Secret: {'Configurado' if APP_SECRET else 'Não configurado'}")
    print("\n📝 Endpoints disponíveis:")
    print("   GET  /webhook/whatsapp - Verificação do webhook")
    print("   POST /webhook/whatsapp - Receber mensagens")
    print("   GET  /health - Health check")
    print("\n🔗 Para expor localmente, use ngrok:")
    print("   ngrok http 8000")
    print("\n📚 Configure o webhook no Meta com:")
    print("   URL: https://your-ngrok-url.ngrok.io/webhook/whatsapp")
    print(f"   Token: {VERIFY_TOKEN}")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
