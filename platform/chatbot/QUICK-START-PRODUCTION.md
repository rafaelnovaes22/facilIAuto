# 🚀 Quick Start - Produção em 5 Minutos

## Pré-requisitos

- ✅ Docker Desktop instalado
- ✅ WhatsApp Business API configurada
- ✅ OpenAI API Key

## Passo 1: Configurar Variáveis de Ambiente

```powershell
# Copiar arquivo de exemplo
Copy-Item .env.production .env

# Editar com suas credenciais
notepad .env
```

**Variáveis obrigatórias**:
```env
# WhatsApp (obter do Meta Business Manager)
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=meu_token_123
WHATSAPP_WEBHOOK_SECRET=meu_secret_456

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Database (mudar senha!)
POSTGRES_PASSWORD=SuaSenhaSegura123!
```

## Passo 2: Deploy

```powershell
# Executar script de deploy
.\deploy.ps1
```

Aguarde 2-3 minutos. Você verá:

```
✓ Docker is installed
✓ Docker Compose is installed
✓ PostgreSQL is ready
✓ Migrations completed
✓ Redis is ready
✓ API is healthy
✓ Celery worker is running

✅ Deployment completed!
```

## Passo 3: Configurar Webhook

1. Acesse [Meta Business Manager](https://business.facebook.com/)
2. Vá em **WhatsApp > Configuration**
3. Configure webhook:
   - **URL**: `http://localhost:8000/webhook/whatsapp` (para teste local)
   - **Verify Token**: (mesmo valor do `.env`)
   - **Webhook Fields**: Marque `messages`
4. Clique em **Verify and Save**

## Passo 4: Testar

Envie uma mensagem para o número do WhatsApp Business:

```
Olá!
```

Você deve receber uma resposta do chatbot! 🎉

## Monitorar

### Ver Logs em Tempo Real

```powershell
docker-compose -f docker-compose.prod.yml logs -f
```

### Acessar Flower (Monitoring)

Abra no navegador: http://localhost:5555

Você verá:
- Tasks processadas
- Workers ativos
- Taxa de sucesso

### Verificar Health

```powershell
curl http://localhost:8000/health
```

## Comandos Úteis

### Parar Serviços

```powershell
docker-compose -f docker-compose.prod.yml down
```

### Reiniciar Serviços

```powershell
docker-compose -f docker-compose.prod.yml restart
```

### Ver Status

```powershell
docker-compose -f docker-compose.prod.yml ps
```

### Ver Logs de um Serviço Específico

```powershell
# API
docker-compose -f docker-compose.prod.yml logs -f chatbot-api

# Celery Worker
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# Redis
docker-compose -f docker-compose.prod.yml logs -f redis
```

### Escalar Workers

```powershell
# Aumentar para 3 workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3
```

## Troubleshooting

### Webhook não funciona

```powershell
# 1. Verificar se API está rodando
curl http://localhost:8000/health

# 2. Ver logs
docker-compose -f docker-compose.prod.yml logs -f chatbot-api

# 3. Verificar configuração no Meta
# - URL correta?
# - Verify token correto?
```

### Celery não processa mensagens

```powershell
# 1. Verificar worker
docker-compose -f docker-compose.prod.yml ps celery-worker

# 2. Ver logs do worker
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# 3. Reiniciar worker
docker-compose -f docker-compose.prod.yml restart celery-worker
```

### Redis com erro

```powershell
# Reiniciar Redis
docker-compose -f docker-compose.prod.yml restart redis

# Verificar logs
docker-compose -f docker-compose.prod.yml logs redis
```

## Deploy em Servidor (Produção Real)

Para deploy em servidor com domínio:

1. **Configure SSL/HTTPS** (obrigatório para WhatsApp)
   - Use Nginx + Let's Encrypt
   - Ver `DEPLOYMENT-GUIDE.md` para detalhes

2. **Atualize webhook URL**
   - De: `http://localhost:8000/webhook/whatsapp`
   - Para: `https://seu-dominio.com/webhook/whatsapp`

3. **Configure firewall**
   - Abrir portas 80 e 443
   - Fechar porta 8000 (usar Nginx como proxy)

4. **Configure backups**
   - PostgreSQL: backup diário
   - Redis: snapshot periódico

Ver documentação completa em `DEPLOYMENT-GUIDE.md`

## Arquitetura

```
WhatsApp → Webhook → FastAPI → Celery → Redis
                                  ↓
                              Workers
                                  ↓
                         Process Message
                                  ↓
                         Send Response
```

## Próximos Passos

1. ✅ Chatbot funcionando localmente
2. ⬜ Deploy em servidor com SSL
3. ⬜ Configurar monitoring (Sentry, Prometheus)
4. ⬜ Configurar backups automáticos
5. ⬜ Treinar modelo com dados reais
6. ⬜ Implementar analytics dashboard

## Suporte

- 📖 Documentação completa: `DEPLOYMENT-GUIDE.md`
- 🔧 Troubleshooting: `DEPLOYMENT-GUIDE.md#troubleshooting`
- 📊 Monitoring: http://localhost:5555 (Flower)
- 🏥 Health check: http://localhost:8000/health

---

**Pronto! Seu chatbot está rodando! 🚀**

Envie uma mensagem para o WhatsApp Business e veja a mágica acontecer! ✨
