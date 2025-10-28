# WhatsApp Business API - Quick Start

Guia rápido para começar a usar a WhatsApp Business API em 15 minutos.

## ⚡ Setup Rápido (Desenvolvimento)

### 1. Criar Conta e App (5 minutos)

```bash
# 1. Acesse e crie conta
https://developers.facebook.com/

# 2. Crie um app
- Tipo: "Empresa"
- Nome: "FacilIAuto Chatbot"

# 3. Adicione produto WhatsApp
- Dashboard → Adicionar Produto → WhatsApp
```

### 2. Configurar Ambiente (2 minutos)

```bash
# Copiar template de configuração
cd platform/chatbot
cp .env.example .env

# Editar .env com suas credenciais
# (obtenha no painel do Meta)
```

### 3. Obter Credenciais (3 minutos)

No painel do Meta:

```bash
# 1. Token temporário (válido 24h)
WhatsApp → Introdução → Copiar "Token de acesso temporário"

# 2. Phone Number ID
WhatsApp → Introdução → Copiar "ID do número de telefone"

# 3. Adicionar número de teste
WhatsApp → Introdução → "Para" → Adicionar seu número
```

Cole no `.env`:

```bash
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxx...
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WEBHOOK_VERIFY_TOKEN=faciliauto_webhook_2024_secure_token
```

### 4. Testar Envio (2 minutos)

```bash
# Instalar dependências
pip install requests python-dotenv

# Enviar mensagem de teste
python scripts/test_whatsapp_send.py \
  --to 5511999999999 \
  --message "Olá! Teste do FacilIAuto 🚗"

# Você deve receber a mensagem no WhatsApp!
```

### 5. Configurar Webhook (3 minutos)

```bash
# Terminal 1: Iniciar servidor webhook
python scripts/test_whatsapp_webhook.py

# Terminal 2: Expor com ngrok
ngrok http 8000

# Copie a URL HTTPS (ex: https://abc123.ngrok.io)
```

No painel do Meta:

```bash
# WhatsApp → Configuração → Webhooks
URL: https://abc123.ngrok.io/webhook/whatsapp
Token: faciliauto_webhook_2024_secure_token

# Marcar eventos:
☑️ messages
☑️ message_status
```

### 6. Testar Recebimento (1 minuto)

```bash
# Envie uma mensagem do WhatsApp para o número de teste
# Você verá o payload no terminal do webhook!
```

---

## ✅ Checklist de Validação

- [ ] Mensagem enviada com sucesso via API
- [ ] Mensagem recebida no WhatsApp
- [ ] Webhook verificado no Meta
- [ ] Webhook recebe mensagens
- [ ] Payload do webhook é válido
- [ ] Assinatura do webhook é verificada

---

## 🚀 Próximos Passos

### Para Desenvolvimento:

1. Implementar handlers de mensagem (Task 8)
2. Integrar com NLP Service (Task 5)
3. Implementar Session Manager (Task 4)

### Para Produção:

1. Obter token permanente (válido indefinidamente)
2. Adicionar número próprio (não de teste)
3. Configurar domínio com HTTPS
4. Implementar rate limiting
5. Configurar monitoring

---

## 📚 Recursos Úteis

**Documentação:**
- [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Webhook Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks)
- [Message Templates](https://developers.facebook.com/docs/whatsapp/message-templates)

**Ferramentas:**
- [API Explorer](https://developers.facebook.com/tools/explorer/)
- [Webhook Tester](https://webhook.site/)
- [ngrok](https://ngrok.com/)

**Suporte:**
- [Meta Business Help Center](https://www.facebook.com/business/help)
- [Developer Community](https://developers.facebook.com/community/)

---

## 🐛 Problemas Comuns

### "Invalid OAuth access token"
→ Token expirado. Gere novo token no painel.

### "Webhook verification failed"
→ Verifique se o WEBHOOK_VERIFY_TOKEN está correto.

### "Phone number not registered"
→ Adicione seu número na lista de teste.

### Webhook não recebe mensagens
→ Verifique se o ngrok está rodando e a URL está correta.

---

**Tempo total:** ~15 minutos ⏱️

**Dificuldade:** Fácil 🟢

**Custo:** Gratuito (1000 conversas/mês) 💰
