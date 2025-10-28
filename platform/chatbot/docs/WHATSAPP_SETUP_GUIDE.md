# WhatsApp Business API - Guia de Configuração

Este guia detalha o processo completo de configuração da WhatsApp Business API (Cloud API) para o chatbot FacilIAuto.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Criar Conta no Meta Business Suite](#criar-conta-no-meta-business-suite)
3. [Configurar WhatsApp Business API](#configurar-whatsapp-business-api)
4. [Obter Tokens de Acesso](#obter-tokens-de-acesso)
5. [Configurar Webhooks](#configurar-webhooks)
6. [Testar Envio e Recebimento](#testar-envio-e-recebimento)
7. [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

Antes de começar, você precisará de:

- [ ] Conta Facebook pessoal (será usada como administrador)
- [ ] Número de telefone para WhatsApp Business (não pode estar registrado no WhatsApp)
- [ ] Domínio verificado (para produção)
- [ ] Servidor com HTTPS para receber webhooks
- [ ] Cartão de crédito (para verificação, não será cobrado no tier gratuito)

**Limites do Tier Gratuito:**
- 1.000 conversas gratuitas por mês
- Após isso: $0.005 - $0.009 por conversa (varia por país)
- Rate limit: 80 mensagens/segundo

---

## Criar Conta no Meta Business Suite

### Passo 1: Acessar Meta Business Suite

1. Acesse: https://business.facebook.com/
2. Clique em **"Criar conta"**
3. Preencha as informações:
   - Nome da empresa: **FacilIAuto**
   - Seu nome completo
   - Email corporativo

### Passo 2: Verificar Email

1. Verifique seu email
2. Clique no link de confirmação
3. Complete o perfil da empresa

### Passo 3: Adicionar WhatsApp Business

1. No menu lateral, clique em **"Configurações da conta"**
2. Vá para **"Aplicativos e ativos"**
3. Clique em **"Adicionar ativos"** → **"WhatsApp Business"**
4. Siga o assistente de configuração

---

## Configurar WhatsApp Business API

### Passo 1: Criar App no Meta for Developers

1. Acesse: https://developers.facebook.com/
2. Clique em **"Meus Apps"** → **"Criar App"**
3. Selecione tipo: **"Empresa"**
4. Preencha:
   - Nome do app: **FacilIAuto Chatbot**
   - Email de contato
   - Conta comercial: Selecione a conta criada anteriormente

### Passo 2: Adicionar Produto WhatsApp

1. No dashboard do app, procure **"WhatsApp"**
2. Clique em **"Configurar"**
3. Selecione a conta comercial do WhatsApp
4. Aceite os termos de serviço

### Passo 3: Configurar Número de Telefone

**Opção A: Usar Número de Teste (Desenvolvimento)**

1. No painel WhatsApp, vá para **"Introdução"**
2. Use o número de teste fornecido pelo Meta
3. Adicione números de telefone para teste (máximo 5)
4. Envie código de verificação via WhatsApp

**Opção B: Adicionar Número Próprio (Produção)**

1. Vá para **"Números de telefone"**
2. Clique em **"Adicionar número de telefone"**
3. Insira o número (formato: +55 11 99999-9999)
4. Escolha método de verificação:
   - SMS
   - Chamada de voz
5. Insira o código de 6 dígitos
6. Aceite os termos

**⚠️ IMPORTANTE:**
- O número NÃO pode estar registrado no WhatsApp pessoal
- Após adicionar, você tem 14 dias para verificar
- Números não verificados são removidos automaticamente

---

## Obter Tokens de Acesso

### Passo 1: Token Temporário (Desenvolvimento)

1. No painel WhatsApp, vá para **"Introdução"**
2. Copie o **"Token de acesso temporário"**
3. Validade: 24 horas
4. Use apenas para testes iniciais

```bash
# Exemplo de token temporário
WHATSAPP_TEMP_TOKEN="EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Passo 2: Token Permanente (Produção)

1. Vá para **"Configurações"** → **"Básico"**
2. Copie o **"ID do app"** e **"Chave secreta do app"**
3. Vá para **"Usuários do sistema"**
4. Clique em **"Adicionar"**
5. Nome: **FacilIAuto Chatbot System User**
6. Função: **Administrador**
7. Após criar, clique em **"Gerar novo token"**
8. Selecione permissões:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
9. Copie e salve o token (não será mostrado novamente!)

```bash
# Exemplo de token permanente
WHATSAPP_ACCESS_TOKEN="EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
WHATSAPP_PHONE_NUMBER_ID="123456789012345"
WHATSAPP_BUSINESS_ACCOUNT_ID="987654321098765"
```

### Passo 3: Salvar Credenciais

Crie arquivo `.env` na raiz do projeto:

```bash
# WhatsApp Business API Configuration
WHATSAPP_ACCESS_TOKEN=your_permanent_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token_here
WHATSAPP_APP_SECRET=your_app_secret_here

# Webhook Configuration
WEBHOOK_URL=https://your-domain.com/webhook/whatsapp
WEBHOOK_VERIFY_TOKEN=faciliauto_webhook_2024_secure_token
```

---

## Configurar Webhooks

### Passo 1: Preparar Endpoint Local (Desenvolvimento)

Para desenvolvimento local, use **ngrok** para expor seu servidor:

```bash
# Instalar ngrok
# Windows: choco install ngrok
# Mac: brew install ngrok
# Linux: snap install ngrok

# Iniciar túnel
ngrok http 8000

# Copie a URL HTTPS gerada (ex: https://abc123.ngrok.io)
```

### Passo 2: Configurar Webhook no Meta

1. No painel WhatsApp, vá para **"Configuração"**
2. Clique em **"Webhooks"** → **"Configurar"**
3. Preencha:
   - **URL de retorno de chamada**: `https://your-domain.com/webhook/whatsapp`
   - **Token de verificação**: Use o mesmo do `.env` (ex: `faciliauto_webhook_2024_secure_token`)
4. Clique em **"Verificar e salvar"**

**O Meta fará uma requisição GET para verificar:**
```
GET https://your-domain.com/webhook/whatsapp?
  hub.mode=subscribe&
  hub.challenge=1234567890&
  hub.verify_token=faciliauto_webhook_2024_secure_token
```

Seu endpoint deve retornar o `hub.challenge` se o token estiver correto.

### Passo 3: Assinar Eventos

Após verificação, marque os eventos que deseja receber:

- [x] **messages** - Mensagens recebidas
- [x] **message_status** - Status de entrega
- [ ] **messaging_postbacks** - Respostas de botões (opcional)
- [ ] **messaging_optins** - Opt-ins (opcional)

Clique em **"Salvar"**.

### Passo 4: Validar Assinatura de Webhook

O Meta envia um header `X-Hub-Signature-256` com cada webhook. Valide para garantir autenticidade:

```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, app_secret: str) -> bool:
    """
    Verificar assinatura do webhook do Meta
    
    Args:
        payload: Corpo da requisição (bytes)
        signature: Header X-Hub-Signature-256
        app_secret: Chave secreta do app
    
    Returns:
        True se assinatura válida
    """
    expected_signature = hmac.new(
        app_secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Remover prefixo "sha256="
    received_signature = signature.replace('sha256=', '')
    
    return hmac.compare_digest(expected_signature, received_signature)
```

---

## Testar Envio e Recebimento

### Teste 1: Enviar Mensagem de Texto

Use o script de teste fornecido:

```bash
cd platform/chatbot
python scripts/test_whatsapp_send.py
```

Ou manualmente via cURL:

```bash
curl -X POST \
  "https://graph.facebook.com/v18.0/${WHATSAPP_PHONE_NUMBER_ID}/messages" \
  -H "Authorization: Bearer ${WHATSAPP_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "5511999999999",
    "type": "text",
    "text": {
      "body": "Olá! Esta é uma mensagem de teste do FacilIAuto 🚗"
    }
  }'
```

**Resposta esperada:**
```json
{
  "messaging_product": "whatsapp",
  "contacts": [{
    "input": "5511999999999",
    "wa_id": "5511999999999"
  }],
  "messages": [{
    "id": "wamid.HBgNNTUxMTk5OTk5OTk5ORUCABIYFjNFQjBDMDg1RjREMDhGMEE4RjdGAA=="
  }]
}
```

### Teste 2: Receber Mensagem

1. Envie uma mensagem do WhatsApp para o número configurado
2. Verifique os logs do webhook:

```bash
# Iniciar servidor de desenvolvimento
cd platform/chatbot
uvicorn main:app --reload --port 8000

# Em outro terminal, monitorar logs
tail -f logs/webhook.log
```

**Payload esperado do webhook:**
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "5511999999999",
          "phone_number_id": "PHONE_NUMBER_ID"
        },
        "contacts": [{
          "profile": {
            "name": "João Silva"
          },
          "wa_id": "5511888888888"
        }],
        "messages": [{
          "from": "5511888888888",
          "id": "wamid.HBgNNTUxMTg4ODg4ODg4OBUCABIYFjNFQjBDMDg1RjREMDhGMEE4RjdGAA==",
          "timestamp": "1234567890",
          "text": {
            "body": "Olá, quero comprar um carro"
          },
          "type": "text"
        }]
      },
      "field": "messages"
    }]
  }]
}
```

### Teste 3: Enviar Mensagem com Template

Templates devem ser aprovados pelo Meta antes do uso:

```bash
curl -X POST \
  "https://graph.facebook.com/v18.0/${WHATSAPP_PHONE_NUMBER_ID}/messages" \
  -H "Authorization: Bearer ${WHATSAPP_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "5511999999999",
    "type": "template",
    "template": {
      "name": "hello_world",
      "language": {
        "code": "pt_BR"
      }
    }
  }'
```

### Teste 4: Enviar Mensagem com Imagem

```bash
curl -X POST \
  "https://graph.facebook.com/v18.0/${WHATSAPP_PHONE_NUMBER_ID}/messages" \
  -H "Authorization: Bearer ${WHATSAPP_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "5511999999999",
    "type": "image",
    "image": {
      "link": "https://faciliauto.com/cars/honda-civic-2023.jpg",
      "caption": "Honda Civic 2023 - R$ 120.000"
    }
  }'
```

### Teste 5: Validar Rate Limits

```bash
# Testar múltiplas mensagens
python scripts/test_rate_limits.py
```

---

## Troubleshooting

### Erro: "Invalid OAuth access token"

**Causa:** Token expirado ou inválido

**Solução:**
1. Gere novo token permanente
2. Atualize `.env`
3. Reinicie o servidor

### Erro: "Webhook verification failed"

**Causa:** Token de verificação incorreto

**Solução:**
1. Verifique se `WEBHOOK_VERIFY_TOKEN` no `.env` corresponde ao configurado no Meta
2. Certifique-se de que o endpoint GET retorna o `hub.challenge`

### Erro: "Phone number not registered"

**Causa:** Número não verificado ou removido

**Solução:**
1. Verifique o número no painel do Meta
2. Complete o processo de verificação em 14 dias

### Erro: "Rate limit exceeded"

**Causa:** Muitas mensagens em curto período

**Solução:**
1. Implemente backoff exponencial
2. Use fila de mensagens (Celery)
3. Considere upgrade de tier

### Webhook não recebe mensagens

**Checklist:**
- [ ] Webhook está verificado no painel do Meta?
- [ ] Eventos "messages" estão marcados?
- [ ] URL está acessível publicamente (HTTPS)?
- [ ] Firewall permite requisições do Meta?
- [ ] Servidor está rodando?

**IPs do Meta para whitelist:**
```
31.13.64.0/19
31.13.96.0/19
45.64.40.0/22
66.220.144.0/20
69.63.176.0/20
69.171.224.0/19
74.119.76.0/22
103.4.96.0/22
157.240.0.0/17
173.252.64.0/18
179.60.192.0/22
185.60.216.0/22
204.15.20.0/22
```

---

## Próximos Passos

Após configuração bem-sucedida:

1. ✅ Implementar webhook handler (Task 8)
2. ✅ Integrar com NLP Service (Task 5)
3. ✅ Implementar Session Manager (Task 4)
4. ✅ Testar fluxo completo E2E (Task 14)

---

## Referências

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Cloud API Quick Start](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
- [Webhook Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks)
- [Message Templates](https://developers.facebook.com/docs/whatsapp/message-templates)
- [Rate Limits](https://developers.facebook.com/docs/whatsapp/cloud-api/rate-limits)

---

**Última atualização:** 2024-10-15
**Versão:** 1.0.0
**Autor:** FacilIAuto Dev Team
