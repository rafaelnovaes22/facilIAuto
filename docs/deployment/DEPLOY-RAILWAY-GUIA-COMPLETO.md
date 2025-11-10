# 🚀 Guia Completo: Deploy FacilIAuto no Railway

**Tempo Total**: 20-30 minutos  
**Custo**: Gratuito (Railway Free Tier)  
**Última Atualização**: Novembro 2024

---

## 📋 Pré-requisitos

- ✅ Conta no GitHub (já tem!)
- ✅ Código atualizado no GitHub (já feito!)
- ✅ Conta no Railway (criar em https://railway.app)

---

## 🎯 Visão Geral

Vamos fazer deploy de 2 serviços:
1. **Backend** (FastAPI + Python) → `faciliauto-backend`
2. **Frontend** (React + Vite) → `faciliauto-frontend`

---

## 🚂 PARTE 1: Deploy do Backend (10 min)

### Passo 1: Criar Projeto no Railway

1. Acesse https://railway.app
2. Clique em **"Login"** → **"Login with GitHub"**
3. Autorize o Railway a acessar seus repositórios
4. Clique em **"New Project"**
5. Selecione **"Deploy from GitHub repo"**
6. Escolha o repositório: **`rafaelnovaes22/facilIAuto`**

### Passo 2: Configurar Backend

1. Railway vai detectar automaticamente o projeto
2. Clique em **"Add variables"** ou vá em **Settings → Variables**
3. Adicione as seguintes variáveis:

```bash
PORT=8000
PYTHONUNBUFFERED=1
ENVIRONMENT=production
LOG_LEVEL=info
```

4. Em **Settings → General**:
   - **Service Name**: `faciliauto-backend`
   - **Root Directory**: `platform/backend`

5. Em **Settings → Deploy**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Passo 3: Gerar Domínio Público

1. Vá em **Settings → Networking**
2. Clique em **"Generate Domain"**
3. Railway vai gerar uma URL tipo: `faciliauto-backend-production.up.railway.app`
4. **COPIE ESTA URL** - você vai precisar dela!

### Passo 4: Verificar Deploy

1. Aguarde o deploy terminar (1-2 minutos)
2. Acesse: `https://[sua-url-backend]/health`
3. Deve retornar:
```json
{
  "status": "healthy",
  "dealerships": 3,
  "cars": 150
}
```

4. Teste a documentação: `https://[sua-url-backend]/docs`

✅ **Backend no ar!**

---

## 🎨 PARTE 2: Deploy do Frontend (10 min)

### Passo 1: Adicionar Novo Serviço

1. No mesmo projeto Railway, clique em **"+ New"**
2. Selecione **"GitHub Repo"**
3. Escolha novamente: **`rafaelnovaes22/facilIAuto`**

### Passo 2: Configurar Frontend

1. Em **Settings → General**:
   - **Service Name**: `faciliauto-frontend`
   - **Root Directory**: `platform/frontend`

2. Em **Settings → Variables**, adicione:

```bash
PORT=3000
VITE_API_URL=https://[SUA-URL-BACKEND-AQUI]
NODE_ENV=production
```

⚠️ **IMPORTANTE**: Substitua `[SUA-URL-BACKEND-AQUI]` pela URL que você copiou no Passo 3 do Backend!

3. Em **Settings → Deploy**:
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`

### Passo 3: Gerar Domínio Público

1. Vá em **Settings → Networking**
2. Clique em **"Generate Domain"**
3. Railway vai gerar uma URL tipo: `faciliauto-frontend-production.up.railway.app`
4. **COPIE ESTA URL**

### Passo 4: Atualizar CORS no Backend

1. Volte para o serviço **Backend**
2. Vá em **Settings → Variables**
3. Adicione uma nova variável:

```bash
FRONTEND_URL=https://[SUA-URL-FRONTEND-AQUI]
```

4. Clique em **"Redeploy"** para aplicar as mudanças

### Passo 5: Verificar Deploy

1. Aguarde o deploy terminar (2-3 minutos)
2. Acesse: `https://[sua-url-frontend]`
3. A página inicial deve carregar!

✅ **Frontend no ar!**

---

## ✅ PARTE 3: Validação Completa (5 min)

### Teste 1: Health Check

```bash
# Backend
curl https://[sua-url-backend]/health

# Deve retornar: {"status": "healthy", ...}
```

### Teste 2: API Docs

1. Acesse: `https://[sua-url-backend]/docs`
2. Swagger UI deve carregar
3. Teste o endpoint `/recommend` com:

```json
{
  "orcamento_min": 50000,
  "orcamento_max": 80000,
  "uso_principal": "familia",
  "state": "SP"
}
```

### Teste 3: Fluxo Completo no Frontend

1. Acesse: `https://[sua-url-frontend]`
2. Clique em **"Começar"**
3. Preencha o questionário:
   - Orçamento: R$ 50.000 - R$ 80.000
   - Uso: Família
   - Prioridades: Segurança (5), Espaço (5), Economia (4)
4. Clique em **"Ver Recomendações"**
5. Deve mostrar lista de carros recomendados!

### Teste 4: TCO e Indicadores Financeiros

1. Na lista de recomendações, verifique:
   - ✅ Badge "Dentro do orçamento" ou "Acima do orçamento"
   - ✅ Indicador de saúde financeira (verde/amarelo/vermelho)
   - ✅ Badge "Alta quilometragem" (se aplicável)
   - ✅ Detalhes do TCO ao expandir o card

---

## 🔧 PARTE 4: Configurações Opcionais

### Domínio Customizado (Opcional)

Se você tem um domínio próprio:

1. No Railway, vá em **Settings → Networking**
2. Clique em **"Custom Domain"**
3. Adicione seu domínio: `api.faciliauto.com.br`
4. Configure o DNS conforme instruções do Railway

### Monitoramento (Opcional)

Railway oferece métricas básicas:
- CPU Usage
- Memory Usage
- Network Traffic
- Logs em tempo real

Acesse em: **Metrics** ou **Deployments → View Logs**

### Variáveis de Ambiente Adicionais (Opcional)

Para features avançadas, adicione:

```bash
# Backend
REDIS_URL=redis://...  # Se usar cache
DATABASE_URL=postgresql://...  # Se usar banco de dados
SENTRY_DSN=https://...  # Para error tracking

# Frontend
VITE_ANALYTICS_ID=G-...  # Google Analytics
VITE_SENTRY_DSN=https://...  # Error tracking
```

---

## 🆘 Troubleshooting

### Backend não inicia

**Problema**: Deploy falha com erro de dependências

**Solução**:
1. Verifique `requirements.txt` está correto
2. Adicione `PYTHONUNBUFFERED=1` nas variáveis
3. Veja os logs: **Deployments → View Logs**

### Frontend não conecta ao Backend

**Problema**: Erro de CORS ou "Network Error"

**Solução**:
1. Verifique `VITE_API_URL` está correto (com https://)
2. Verifique `FRONTEND_URL` no backend está correto
3. Redeploy do backend após adicionar `FRONTEND_URL`

### Página em branco no Frontend

**Problema**: Frontend carrega mas não mostra nada

**Solução**:
1. Abra o Console do navegador (F12)
2. Veja se há erros de API
3. Verifique se `VITE_API_URL` está correto
4. Teste o backend diretamente: `https://[backend]/health`

### Deploy muito lento

**Problema**: Build demora mais de 5 minutos

**Solução**:
1. Railway Free Tier tem recursos limitados
2. Considere upgrade para Hobby Plan ($5/mês)
3. Ou use cache de build (Railway faz automaticamente)

---

## 📊 Custos e Limites

### Railway Free Tier
- ✅ $5 de crédito grátis por mês
- ✅ 500 horas de execução
- ✅ 100GB de tráfego
- ✅ Suficiente para MVP e testes

### Railway Hobby Plan ($5/mês)
- ✅ $5 de crédito + $5 pagos = $10 total
- ✅ Execução ilimitada
- ✅ 100GB de tráfego
- ✅ Recomendado para produção

---

## 🎉 Pronto!

Seu FacilIAuto está no ar! 🚀

**URLs para compartilhar:**
- Backend: `https://[sua-url-backend]`
- Frontend: `https://[sua-url-frontend]`
- API Docs: `https://[sua-url-backend]/docs`

**Próximos passos:**
1. Compartilhe as URLs com a equipe
2. Configure domínio customizado (opcional)
3. Configure monitoramento (Sentry, etc)
4. Faça testes com usuários reais
5. Colete feedback e itere!

---

## 📞 Suporte

**Problemas?**
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/rafaelnovaes22/facilIAuto/issues

**Dúvidas sobre o código?**
- Veja: `docs/guides/COMO-EXECUTAR.md`
- Veja: `platform/backend/README.md`
- Veja: `platform/frontend/README.md`

---

**Status**: ✅ Production Ready  
**Última Atualização**: Novembro 2024  
**Versão**: 1.0.0
