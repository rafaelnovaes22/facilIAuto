# 🐳 **FacilIAuto - Guia Docker**

## 🚀 **Quick Start**

### **1. Configurar Ambiente**
```bash
# Copiar arquivo de configuração
cp env.example .env

# Editar variáveis se necessário
# notepad .env  # Windows
# nano .env     # Linux/Mac
```

### **2. Executar Stack Completo**
```bash
# Subir aplicação + PostgreSQL
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f faciliauto-app

# Verificar saúde dos serviços
docker-compose ps
```

### **3. Acessar Aplicação**
```bash
# Aplicação principal
http://localhost:8000

# Health check detalhado
http://localhost:8000/health/detailed

# Métricas
http://localhost:8000/metrics

# PostgreSQL
localhost:5432
User: faciliauto_user
Password: faciliauto_password_2024
Database: faciliauto
```

---

## 🔧 **Comandos Úteis**

### **Gerenciamento de Containers**
```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: perde dados)
docker-compose down -v

# Rebuild da aplicação
docker-compose build --no-cache faciliauto-app
docker-compose up -d faciliauto-app

# Ver logs específicos
docker-compose logs faciliauto-app
docker-compose logs faciliauto-db
```

### **Banco de Dados**
```bash
# Conectar ao PostgreSQL
docker-compose exec faciliauto-db psql -U faciliauto_user -d faciliauto

# Backup do banco
docker-compose exec faciliauto-db pg_dump -U faciliauto_user faciliauto > backup.sql

# Restore do banco
docker-compose exec -T faciliauto-db psql -U faciliauto_user faciliauto < backup.sql
```

### **Debug e Desenvolvimento**
```bash
# Executar shell dentro do container da app
docker-compose exec faciliauto-app bash

# Executar pytest dentro do container
docker-compose exec faciliauto-app python -m pytest

# Ver variáveis de ambiente
docker-compose exec faciliauto-app env | grep FACILIAUTO
```

---

## 🎯 **Profiles de Deploy**

### **Desenvolvimento (Padrão)**
```bash
# Apenas app + PostgreSQL
docker-compose up -d
```

### **Com Cache Redis**
```bash
# Inclui Redis para cache
docker-compose --profile cache up -d
```

### **Com Monitoramento**
```bash
# Inclui Prometheus + Grafana
docker-compose --profile monitoring up -d

# Acessar Grafana
http://localhost:3000
User: admin
Password: faciliauto_grafana_2024
```

### **Stack Completo**
```bash
# Todos os serviços
docker-compose --profile cache --profile monitoring up -d
```

---

## 📊 **Monitoramento**

### **Health Checks**
```bash
# Verificar saúde da aplicação
curl http://localhost:8000/health

# Health check detalhado
curl http://localhost:8000/health/detailed | jq

# Métricas de performance
curl http://localhost:8000/metrics | jq
```

### **Logs Estruturados**
```bash
# Ver logs JSON estruturados
docker-compose logs faciliauto-app | jq

# Filtrar por correlation_id
docker-compose logs faciliauto-app | jq 'select(.correlation_id == "your-id")'

# Ver apenas errors
docker-compose logs faciliauto-app | jq 'select(.level == "ERROR")'
```

---

## 🚨 **Troubleshooting**

### **Problema: Container não inicia**
```bash
# Ver logs detalhados
docker-compose logs faciliauto-app

# Verificar configuração
docker-compose config

# Rebuild limpo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **Problema: Banco não conecta**
```bash
# Verificar se PostgreSQL está healthy
docker-compose ps faciliauto-db

# Ver logs do banco
docker-compose logs faciliauto-db

# Testar conexão manual
docker-compose exec faciliauto-db pg_isready -U faciliauto_user
```

### **Problema: Performance lenta**
```bash
# Ver recursos dos containers
docker stats

# Verificar métricas
curl http://localhost:8000/metrics

# Ver health check detalhado
curl http://localhost:8000/health/detailed
```

---

## 🔒 **Segurança**

### **Variáveis Sensíveis**
- ✅ Senhas em variáveis de ambiente
- ✅ Usuário não-root nos containers
- ✅ Health checks configurados
- ✅ Networks isoladas

### **Recomendações Produção**
```bash
# Usar secrets para senhas
docker secret create db_password password.txt
```

---

## 📈 **Performance**

### **Otimizações Implementadas**
- ✅ Multi-stage build (imagem menor)
- ✅ Layers de cache otimizadas
- ✅ Health checks para load balancers
- ✅ Volumes persistentes
- ✅ Network bridge otimizada

### **Recursos Recomendados**
```yaml
# Em produção, adicionar limits
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

## 🎯 **Próximos Passos**

1. **Configurar monitoramento externo** (New Relic, Datadog)
2. **Implementar backup automático** do PostgreSQL
3. **Configurar CI/CD** com GitHub Actions
4. **Deploy em produção** (AWS ECS, Kubernetes)
5. **Implementar cache Redis** para performance
