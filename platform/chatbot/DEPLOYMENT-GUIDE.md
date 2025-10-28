# Guia de Deploy em Produção - WhatsApp Chatbot

## 📋 Pré-requisitos

### 1. Servidor
- Ubuntu 20.04+ ou similar
- Mínimo 2GB RAM, 2 CPU cores
- Docker e Docker Compose instalados
- Domínio configurado com SSL (HTTPS obrigatório para webhook)

### 2. Contas e Credenciais
- ✅ Meta Business Account
- ✅ WhatsApp Business API configurada
- ✅ OpenAI API Key
- ✅ Acesso ao backend da FacilIAuto

## 🚀 Passo a Passo

### Passo 1: Preparar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalação
docker --version
docker-compose --version
```

### Passo 2: Clonar e Configurar Projeto

```bash
# Clonar repositório
git clone <seu-repositorio>
cd platform/chatbot

# Copiar arquivo de ambiente
cp .env.production .env

# Editar variáveis de ambiente
nano .env
```

### Passo 3: Configurar Variáveis de Ambiente

Edite o arquivo `.env` com suas credenciais:

```bash
# Database
POSTGRES_PASSWORD=SuaSenhaSegura123!

# WhatsApp (obter do Meta Business Manager)
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=seu_token_customizado_123
WHATSAPP_WEBHOOK_SECRET=seu_secret_webhook_456

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Backend
BACKEND_API_URL=https://api.faciliauto.com
BACKEND_API_KEY=sua_api_key_backend

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
```

### Passo 4: Configurar SSL/HTTPS

WhatsApp exige HTTPS. Use Nginx + Let's Encrypt:

```bash
# Instalar Nginx
sudo apt install nginx -y

# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

Configurar Nginx (`/etc/nginx/sites-available/chatbot`):

```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    # Webhook endpoint
    location /webhook/whatsapp {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for webhook
        proxy_connect_timeout 5s;
        proxy_send_timeout 5s;
        proxy_read_timeout 5s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000;
        access_log off;
    }

    # Flower monitoring (opcional, proteger com auth)
    location /flower/ {
        proxy_pass http://localhost:5555/;
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

Ativar configuração:

```bash
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Passo 5: Inicializar Banco de Dados

```bash
# Criar diretórios necessários
mkdir -p logs data

# Iniciar apenas PostgreSQL primeiro
docker-compose -f docker-compose.prod.yml up -d postgres

# Aguardar PostgreSQL iniciar
sleep 10

# Executar migrações
docker-compose -f docker-compose.prod.yml run --rm chatbot-api alembic upgrade head
```

### Passo 6: Iniciar Todos os Serviços

```bash
# Iniciar todos os containers
docker-compose -f docker-compose.prod.yml up -d

# Verificar status
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

Você deve ver:

```
✅ faciliauto-redis          - healthy
✅ faciliauto-postgres       - healthy
✅ faciliauto-chatbot-api    - healthy
✅ faciliauto-celery-worker  - running
✅ faciliauto-celery-beat    - running
✅ faciliauto-flower         - running
```

### Passo 7: Configurar Webhook no WhatsApp

1. Acesse Meta Business Manager
2. Vá em WhatsApp > Configuration
3. Configure webhook:
   - **URL**: `https://seu-dominio.com/webhook/whatsapp`
   - **Verify Token**: (mesmo valor do `.env`)
   - **Webhook Fields**: Marque `messages`

4. Clique em "Verify and Save"

5. Teste enviando mensagem para o número do WhatsApp Business

### Passo 8: Verificar Funcionamento

```bash
# Verificar health check
curl https://seu-dominio.com/health

# Ver logs do webhook
docker-compose -f docker-compose.prod.yml logs -f chatbot-api

# Ver logs do Celery worker
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# Acessar Flower (monitoring)
# https://seu-dominio.com/flower/
```

## 📊 Monitoramento

### Flower - Celery Monitoring

Acesse: `https://seu-dominio.com/flower/`

Você verá:
- Tasks em execução
- Taxa de sucesso/falha
- Tempo médio de processamento
- Workers ativos

### Logs

```bash
# Logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker-compose -f docker-compose.prod.yml logs -f chatbot-api
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# Logs salvos em arquivo
tail -f logs/chatbot.log
```

### Redis Monitoring

```bash
# Conectar ao Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli

# Ver estatísticas
INFO stats

# Ver chaves de idempotência
KEYS "idempotency:*"

# Ver chaves de debounce
KEYS "debounce:*"

# Ver uso de memória
INFO memory
```

### PostgreSQL Monitoring

```bash
# Conectar ao PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres psql -U faciliauto -d faciliauto_chatbot

# Ver sessões ativas
SELECT COUNT(*) FROM sessions WHERE status = 'active';

# Ver mensagens processadas hoje
SELECT COUNT(*) FROM messages WHERE created_at >= CURRENT_DATE;

# Ver taxa de handoff
SELECT 
    COUNT(*) FILTER (WHERE handoff_requested = true) * 100.0 / COUNT(*) as handoff_rate
FROM sessions
WHERE created_at >= CURRENT_DATE;
```

## 🔧 Manutenção

### Atualizar Aplicação

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose -f docker-compose.prod.yml build

# Restart services (zero downtime)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build chatbot-api
docker-compose -f docker-compose.prod.yml up -d --no-deps --build celery-worker

# Run migrations if needed
docker-compose -f docker-compose.prod.yml run --rm chatbot-api alembic upgrade head
```

### Backup

```bash
# Backup PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U faciliauto faciliauto_chatbot > backup_$(date +%Y%m%d).sql

# Backup Redis (snapshot)
docker-compose -f docker-compose.prod.yml exec redis redis-cli BGSAVE

# Backup DuckDB
cp data/analytics.duckdb backup/analytics_$(date +%Y%m%d).duckdb
```

### Restore

```bash
# Restore PostgreSQL
cat backup_20240115.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U faciliauto faciliauto_chatbot

# Restore DuckDB
cp backup/analytics_20240115.duckdb data/analytics.duckdb
```

### Escalar Workers

```bash
# Aumentar número de workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3

# Verificar workers no Flower
# https://seu-dominio.com/flower/
```

## 🚨 Troubleshooting

### Webhook não recebe mensagens

```bash
# 1. Verificar se API está rodando
curl https://seu-dominio.com/health

# 2. Verificar logs
docker-compose -f docker-compose.prod.yml logs -f chatbot-api

# 3. Testar webhook manualmente
curl -X POST https://seu-dominio.com/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=test" \
  -d '{"object":"whatsapp_business_account","entry":[]}'

# 4. Verificar configuração no Meta
# - URL correta?
# - Verify token correto?
# - Webhook fields marcados?
```

### Celery worker não processa tasks

```bash
# 1. Verificar se worker está rodando
docker-compose -f docker-compose.prod.yml ps celery-worker

# 2. Verificar logs do worker
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# 3. Verificar conexão com Redis
docker-compose -f docker-compose.prod.yml exec celery-worker python -c "from config.celery_config import celery_app; print(celery_app.broker_connection().connect())"

# 4. Reiniciar worker
docker-compose -f docker-compose.prod.yml restart celery-worker
```

### Redis com memória cheia

```bash
# 1. Ver uso de memória
docker-compose -f docker-compose.prod.yml exec redis redis-cli INFO memory

# 2. Limpar chaves expiradas
docker-compose -f docker-compose.prod.yml exec redis redis-cli --scan --pattern "idempotency:*" | xargs redis-cli DEL

# 3. Aumentar maxmemory no docker-compose.prod.yml
# command: redis-server --maxmemory 1gb

# 4. Reiniciar Redis
docker-compose -f docker-compose.prod.yml restart redis
```

### PostgreSQL lento

```bash
# 1. Ver queries lentas
docker-compose -f docker-compose.prod.yml exec postgres psql -U faciliauto -d faciliauto_chatbot -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# 2. Criar índices se necessário
# Ver migrations em alembic/versions/

# 3. Vacuum database
docker-compose -f docker-compose.prod.yml exec postgres psql -U faciliauto -d faciliauto_chatbot -c "VACUUM ANALYZE;"
```

## 📈 Performance

### Configurações Recomendadas

**Para baixo volume (< 100 msgs/dia)**:
- 1 Celery worker
- 512MB Redis
- 2GB PostgreSQL

**Para médio volume (100-1000 msgs/dia)**:
- 2-3 Celery workers
- 1GB Redis
- 4GB PostgreSQL

**Para alto volume (> 1000 msgs/dia)**:
- 5+ Celery workers
- 2GB+ Redis
- 8GB+ PostgreSQL
- Considerar Redis Cluster
- Considerar PostgreSQL replication

### Otimizações

```yaml
# docker-compose.prod.yml

# Aumentar workers da API
command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 8

# Aumentar concurrency do Celery
command: celery -A config.celery_config worker --concurrency=8

# Usar autoscaling
command: celery -A config.celery_config worker --autoscale=10,3
```

## 🔒 Segurança

### Checklist de Segurança

- ✅ HTTPS configurado (Let's Encrypt)
- ✅ Webhook signature verification ativada
- ✅ Senhas fortes no `.env`
- ✅ Firewall configurado (apenas portas 80, 443, 22)
- ✅ Flower protegido com autenticação
- ✅ PostgreSQL não exposto publicamente
- ✅ Redis não exposto publicamente
- ✅ Logs não contêm dados sensíveis
- ✅ Backups automáticos configurados

### Firewall

```bash
# Configurar UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📞 Suporte

Em caso de problemas:

1. Verificar logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Verificar health checks: `curl https://seu-dominio.com/health`
3. Verificar Flower: `https://seu-dominio.com/flower/`
4. Consultar documentação: `docs/`

## ✅ Checklist Final

Antes de considerar o deploy completo:

- [ ] Todos os containers rodando (green/healthy)
- [ ] Webhook configurado e verificado no Meta
- [ ] SSL/HTTPS funcionando
- [ ] Teste de mensagem enviada e respondida
- [ ] Flower acessível e mostrando workers
- [ ] Logs sem erros críticos
- [ ] Backup configurado
- [ ] Monitoring configurado
- [ ] Documentação atualizada
- [ ] Equipe treinada

🎉 **Parabéns! Seu chatbot está em produção!**
