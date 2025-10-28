# WhatsApp Business API - Scripts de Teste

Scripts utilitários para configuração e teste da WhatsApp Business API.

## 📋 Scripts Disponíveis

### 1. validate_whatsapp_config.py

Valida toda a configuração da WhatsApp Business API.

```bash
python scripts/validate_whatsapp_config.py
```

**O que valida:**
- ✅ Variáveis de ambiente configuradas
- ✅ Token de acesso válido
- ✅ Phone Number ID válido
- ✅ Business Account ID (opcional)
- ✅ Endpoint de envio configurado
- ✅ Informações sobre rate limits

**Quando usar:**
- Após configurar o `.env` pela primeira vez
- Para diagnosticar problemas de configuração
- Antes de fazer deploy em produção

---

### 2. test_whatsapp_send.py

Testa envio de mensagens via WhatsApp Business API.

```bash
# Enviar mensagem de texto
python scripts/test_whatsapp_send.py \
  --to 5511999999999 \
  --message "Olá! Teste do FacilIAuto 🚗"

# Enviar template
python scripts/test_whatsapp_send.py \
  --to 5511999999999 \
  --template hello_world

# Enviar imagem
python scripts/test_whatsapp_send.py \
  --to 5511999999999 \
  --image "https://example.com/car.jpg" \
  --caption "Honda Civic 2023"
```

**Parâmetros:**
- `--to`: Número do destinatário (obrigatório)
- `--message`: Texto da mensagem
- `--template`: Nome do template aprovado
- `--image`: URL da imagem
- `--caption`: Legenda da imagem

**Quando usar:**
- Para testar conectividade com a API
- Para validar tokens de acesso
- Para testar diferentes tipos de mensagem

---

### 3. test_whatsapp_webhook.py

Servidor de teste para receber webhooks do WhatsApp.

```bash
# Iniciar servidor
python scripts/test_whatsapp_webhook.py

# Em outro terminal, expor com ngrok
ngrok http 8000
```

**Endpoints:**
- `GET /webhook/whatsapp` - Verificação do webhook
- `POST /webhook/whatsapp` - Receber mensagens
- `GET /health` - Health check

**O que faz:**
- ✅ Valida signature do Meta
- ✅ Processa diferentes tipos de mensagem
- ✅ Exibe payload formatado no console
- ✅ Extrai metadados, contatos e mensagens

**Quando usar:**
- Durante desenvolvimento local
- Para debugar payloads do webhook
- Para testar recebimento de mensagens

---

### 4. test_rate_limits.py

Testa rate limits da WhatsApp Business API.

```bash
# Teste sequencial (10 mensagens com delay)
python scripts/test_rate_limits.py \
  --to 5511999999999 \
  --count 10 \
  --mode sequential \
  --delay 0.5

# Teste paralelo (50 mensagens com 10 workers)
python scripts/test_rate_limits.py \
  --to 5511999999999 \
  --count 50 \
  --mode parallel \
  --workers 10
```

**Parâmetros:**
- `--to`: Número do destinatário (obrigatório)
- `--count`: Quantidade de mensagens (padrão: 10)
- `--mode`: sequential ou parallel (padrão: sequential)
- `--delay`: Delay entre mensagens em segundos (modo sequential)
- `--workers`: Número de threads (modo parallel)

**Métricas coletadas:**
- Taxa de sucesso/falha
- Tempo médio por mensagem
- Taxa de mensagens por segundo
- Identificação de rate limiting

**Quando usar:**
- Para validar limites de taxa
- Para testar performance sob carga
- Antes de escalar em produção

---

## 🚀 Quick Start

### Setup Inicial

```bash
# 1. Instalar dependências
pip install requests python-dotenv fastapi uvicorn

# 2. Configurar .env
cp .env.example .env
# Editar .env com suas credenciais

# 3. Validar configuração
python scripts/validate_whatsapp_config.py

# 4. Testar envio
python scripts/test_whatsapp_send.py \
  --to SEU_NUMERO \
  --message "Teste"

# 5. Testar webhook
python scripts/test_whatsapp_webhook.py
```

---

## 📚 Dependências

```bash
pip install -r requirements.txt
```

**Principais:**
- `requests` - HTTP client
- `python-dotenv` - Gerenciamento de .env
- `fastapi` - Framework web (webhook)
- `uvicorn` - ASGI server (webhook)

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'requests'"

```bash
pip install requests python-dotenv
```

### Erro: "Invalid OAuth access token"

1. Verifique se o token está correto no `.env`
2. Gere novo token no painel do Meta
3. Tokens temporários expiram em 24h

### Erro: "Phone number not registered"

1. Adicione seu número na lista de teste
2. WhatsApp → Introdução → "Para" → Adicionar número

### Webhook não recebe mensagens

1. Verifique se o ngrok está rodando
2. Verifique se a URL está correta no Meta
3. Verifique se os eventos estão marcados

---

## 📖 Documentação Adicional

- [Guia Completo de Setup](../docs/WHATSAPP_SETUP_GUIDE.md)
- [Quick Start Guide](../docs/WHATSAPP_QUICK_START.md)
- [WhatsApp API Docs](https://developers.facebook.com/docs/whatsapp)

---

## 🤝 Contribuindo

Para adicionar novos scripts:

1. Seguir o padrão de nomenclatura: `test_*.py` ou `validate_*.py`
2. Incluir docstring com descrição e usage
3. Adicionar tratamento de erros adequado
4. Documentar neste README

---

**Última atualização:** 2024-10-15
**Versão:** 1.0.0
