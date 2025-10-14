# 🚀 Deployment Guide - FacilIAuto Backend

**Autor:** Operations Manager  
**Data:** Outubro 2024  
**Versão:** 1.0

---

## 🎯 **Objetivo**

Guia completo para deploy do backend FacilIAuto em ambiente de produção.

---

## 📋 **Pré-requisitos**

### **Infraestrutura**
- ✅ Docker 20.10+
- ✅ Docker Compose 2.0+
- ✅ 2GB RAM mínimo
- ✅ 10GB disco disponível
- ✅ Portas 80, 443, 8000 disponíveis

### **Opcionais**
- Kubernetes 1.24+ (para produção escalável)
- Load Balancer (AWS ALB, GCP LB, etc)
- Domínio configurado
- Certificado SSL

---

## 🚀 **Deploy com Docker Compose**

### **1. Preparação**

```bash
# Clone do repositório
git clone https://github.com/rafaelnovaes22/facilIAuto.git
cd facilIAuto/platform/backend

# Verificar arquivos
ls -la
# Deve ter: Dockerfile, docker-compose.yml, requirements.txt
```

### **2. Configuração**

```bash
# Criar arquivo .env
cat > .env << EOF
ENVIRONMENT=production
LOG_LEVEL=info
WORKERS=4
DATABASE_URL=postgresql://user:pass@localhost:5432/faciliauto
REDIS_URL=redis://redis:6379/0
SECRET_KEY=$(openssl rand -hex 32)
EOF

# Ajustar permissões
chmod 600 .env
```

### **3. Build**

```bash
# Build da imagem
docker-compose build

# Verificar imagem
docker images | grep faciliauto
```

### **4. Deploy**

```bash
# Subir serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Logs
docker-compose logs -f api
```

### **5. Verificação**

```bash
# Health check
curl http://localhost:8000/health

# Stats
curl http://localhost:8000/stats

# Test recommendation
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "orcamento_min": 50000,
    "orcamento_max": 80000,
    "uso_principal": "familia",
    "prioridades": {
      "economia": 4,
      "espaco": 5,
      "performance": 2,
      "conforto": 4,
      "seguranca": 5
    }
  }'
```

---

## 🔧 **Configurações de Produção**

### **1. SSL/TLS**

```bash
# Gerar certificado self-signed (desenvolvimento)
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Para produção, use Let's Encrypt
# certbot certonly --standalone -d api.faciliauto.com
```

### **2. Firewall**

```bash
# UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### **3. Logs**

```bash
# Configurar rotação de logs
cat > /etc/logrotate.d/faciliauto << EOF
/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 faciliauto faciliauto
}
EOF
```

---

## 📊 **Monitoring**

### **1. Prometheus + Grafana**

```bash
# Acessar Prometheus
http://localhost:9090

# Acessar Grafana
http://localhost:3001
# User: admin
# Pass: faciliauto2024
```

### **2. Métricas Importantes**

```
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Response time (p95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# CPU usage
rate(process_cpu_seconds_total[5m])

# Memory usage
process_resident_memory_bytes
```

### **3. Alertas**

```yaml
# alerts/api-alerts.yml
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        annotations:
          summary: "High response time detected"
      
      - alert: APIDown
        expr: up{job="faciliauto-api"} == 0
        for: 1m
        annotations:
          summary: "API is down"
```

---

## 🔄 **Scaling**

### **1. Horizontal Scaling**

```bash
# Escalar API para 4 réplicas
docker-compose up -d --scale api=4

# Verificar
docker-compose ps
```

### **2. Vertical Scaling**

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### **3. Auto-scaling (Kubernetes)**

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: faciliauto-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: faciliauto-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 💾 **Backup e Recovery**

### **1. Backup de Dados**

```bash
# Script de backup
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/faciliauto"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Criar diretório
mkdir -p $BACKUP_DIR

# Backup de dados
tar -czf $BACKUP_DIR/data_$TIMESTAMP.tar.gz ./data/

# Backup de configurações
tar -czf $BACKUP_DIR/config_$TIMESTAMP.tar.gz \
  docker-compose.yml \
  nginx.conf \
  monitoring/

# Limpar backups antigos (manter últimos 7 dias)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x backup.sh

# Agendar (cron)
crontab -e
# 0 2 * * * /app/backup.sh
```

### **2. Recovery**

```bash
# Restaurar dados
cd /app
tar -xzf /backups/faciliauto/data_20241001_020000.tar.gz

# Reiniciar serviços
docker-compose restart
```

---

## 🔒 **Segurança**

### **1. Checklist de Segurança**

- [ ] Usuário não-root no container
- [ ] Volumes read-only quando possível
- [ ] Secrets não comitados no Git
- [ ] SSL/TLS configurado
- [ ] Rate limiting ativo
- [ ] Firewall configurado
- [ ] Logs de auditoria
- [ ] Scan de vulnerabilidades

### **2. Environment Variables**

```bash
# NUNCA commitar .env
echo ".env" >> .gitignore

# Usar secrets manager em produção
# AWS Secrets Manager, HashiCorp Vault, etc.
```

---

## 📈 **Performance Tuning**

### **1. Uvicorn Workers**

```python
# Cálculo recomendado: (2 * CPU cores) + 1
# Para 4 cores: 9 workers

CMD ["python", "-m", "uvicorn", "api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "9"]
```

### **2. Cache (Redis)**

```python
# Implementar cache para endpoints lentos
@app.get("/cars")
@cache(expire=300)  # 5 minutos
async def get_cars():
    ...
```

### **3. Database Connection Pool**

```python
# Configurar pool de conexões
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
```

---

## ✅ **Checklist de Deploy**

### **Pre-Deploy**
- [ ] Testes passando (100%)
- [ ] Code review aprovado
- [ ] Secrets configurados
- [ ] SSL certificado válido
- [ ] Backup recente disponível
- [ ] Rollback plan definido

### **Deploy**
- [ ] Build da imagem
- [ ] Deploy em staging
- [ ] Smoke tests em staging
- [ ] Deploy em produção
- [ ] Verificação de health
- [ ] Monitoring ativo

### **Post-Deploy**
- [ ] Métricas normais
- [ ] Logs sem erros críticos
- [ ] Performance aceitável
- [ ] Alertas configurados
- [ ] Documentação atualizada
- [ ] Stakeholders notificados

---

## 🆘 **Troubleshooting**

### **Container não inicia**
```bash
# Ver logs
docker-compose logs api

# Ver últimos erros
docker-compose logs --tail=50 api

# Entrar no container
docker-compose exec api /bin/bash
```

### **High memory usage**
```bash
# Ver uso de recursos
docker stats

# Reduzir workers
# Ajustar em docker-compose.yml
```

### **Slow response**
```bash
# Verificar logs
docker-compose logs api | grep "ERROR\|WARNING"

# Profile da aplicação
# Usar py-spy ou cProfile
```

---

## 📞 **Suporte**

### **Escalação**
1. **Ops Team**: ops@faciliauto.com
2. **Tech Lead**: tech@faciliauto.com  
3. **On-call**: +55 11 9xxxx-xxxx

### **Documentação**
- API Docs: https://api.faciliauto.com/docs
- Internal Wiki: https://wiki.faciliauto.com
- Runbooks: https://runbooks.faciliauto.com

---

**Status:** ✅ Production Ready  
**SLA Target:** 99.5% uptime  
**RTO:** < 1 hour  
**RPO:** < 24 hours

