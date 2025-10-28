# 🚀 EXECUTE AGORA - Deploy Imediato

## ⚡ 3 Comandos Para Colocar em Produção

### 1️⃣ Configurar Credenciais (2 minutos)

```powershell
# Copiar arquivo de configuração
Copy-Item .env.production .env

# Abrir para editar
notepad .env
```

**Preencha APENAS estas variáveis** (o resto pode deixar como está):

```env
# WhatsApp (obter do Meta Business Manager)
WHATSAPP_ACCESS_TOKEN=cole_seu_token_aqui
WHATSAPP_PHONE_NUMBER_ID=cole_seu_phone_id_aqui
WHATSAPP_VERIFY_TOKEN=crie_um_token_qualquer_123
WHATSAPP_WEBHOOK_SECRET=crie_um_secret_qualquer_456

# OpenAI
OPENAI_API_KEY=cole_sua_openai_key_aqui

# Database (MUDE A SENHA!)
POSTGRES_PASSWORD=SuaSenhaSegura123!
```

Salve e feche o arquivo.

### 2️⃣ Deploy (3 minutos)

```powershell
# Executar deploy
.\deploy.ps1
```

Aguarde aparecer:
```
✅ Deployment completed!
```

### 3️⃣ Configurar Webhook no WhatsApp (1 minuto)

1. Abra: https://business.facebook.com/
2. Vá em: **WhatsApp > Configuration > Webhook**
3. Clique em **Edit**
4. Preencha:
   - **Callback URL**: `http://seu-ip:8000/webhook/whatsapp`
   - **Verify Token**: (o mesmo que você colocou no `.env`)
5. Marque: **messages**
6. Clique: **Verify and Save**

## ✅ Pronto! Teste Agora

Envie uma mensagem para o número do WhatsApp Business:

```
Olá!
```

Você deve receber uma resposta! 🎉

## 📊 Monitorar

### Ver o que está acontecendo

```powershell
# Logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f
```

### Acessar Dashboard

Abra no navegador: http://localhost:5555

Você verá:
- ✅ Workers ativos
- ✅ Tasks processadas
- ✅ Taxa de sucesso

## 🔧 Comandos Úteis

### Parar tudo

```powershell
docker-compose -f docker-compose.prod.yml down
```

### Reiniciar

```powershell
docker-compose -f docker-compose.prod.yml restart
```

### Ver status

```powershell
docker-compose -f docker-compose.prod.yml ps
```

## ❓ Problemas?

### Webhook não funciona

```powershell
# Verificar se API está rodando
curl http://localhost:8000/health

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f chatbot-api
```

**Solução comum**: 
- Verificar se o IP está correto no webhook
- Verificar se o verify token está correto
- Verificar se marcou "messages" no webhook

### Celery não processa

```powershell
# Ver logs do worker
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# Reiniciar worker
docker-compose -f docker-compose.prod.yml restart celery-worker
```

### Docker não inicia

```powershell
# Verificar se Docker Desktop está rodando
docker ps

# Se não estiver, abra Docker Desktop
```

## 🌐 Deploy em Servidor Real (Opcional)

Se quiser colocar em um servidor com domínio:

1. **Contratar servidor** (AWS, DigitalOcean, etc)
2. **Configurar domínio** (seu-dominio.com)
3. **Instalar SSL** (Let's Encrypt)
4. **Atualizar webhook** para `https://seu-dominio.com/webhook/whatsapp`

Ver guia completo em: `DEPLOYMENT-GUIDE.md`

## 📚 Documentação Completa

- **Quick Start**: `QUICK-START-PRODUCTION.md`
- **Deploy Completo**: `DEPLOYMENT-GUIDE.md`
- **Detalhes Técnicos**: `TASK-9-PRODUCTION-READY.md`
- **Idempotência**: `IDEMPOTENCY_AND_DEBOUNCE.md`

## 🎯 Checklist Rápido

- [ ] `.env` configurado com credenciais
- [ ] `.\deploy.ps1` executado com sucesso
- [ ] Webhook configurado no Meta
- [ ] Mensagem de teste enviada
- [ ] Resposta recebida
- [ ] Flower acessível (http://localhost:5555)
- [ ] Logs sem erros

## 🎉 Sucesso!

Se você:
- ✅ Enviou mensagem
- ✅ Recebeu resposta
- ✅ Viu task no Flower

**Parabéns! Seu chatbot está em produção!** 🚀

---

## 📞 Próximos Passos

1. **Testar diferentes tipos de mensagem**
   - Texto
   - Perguntas sobre carros
   - Solicitação de handoff

2. **Monitorar performance**
   - Acessar Flower
   - Ver tempo de resposta
   - Verificar taxa de sucesso

3. **Ajustar configurações**
   - Aumentar workers se necessário
   - Ajustar rate limits
   - Otimizar prompts

4. **Deploy em servidor** (quando estiver pronto)
   - Seguir `DEPLOYMENT-GUIDE.md`
   - Configurar SSL
   - Configurar domínio

---

**Dúvidas? Consulte a documentação ou veja os logs!**

```powershell
# Ver tudo que está acontecendo
docker-compose -f docker-compose.prod.yml logs -f
```

**Boa sorte! 🍀**
