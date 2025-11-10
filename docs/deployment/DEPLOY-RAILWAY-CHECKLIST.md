# ✅ Checklist: Deploy Railway - FacilIAuto

**Tempo Total**: 20-30 minutos

---

## 📋 Antes de Começar

- [ ] Conta no Railway criada (https://railway.app)
- [ ] Login com GitHub feito
- [ ] Código no GitHub atualizado ✅ (já feito!)

---

## 🚂 Deploy Backend (10 min)

### Passo 1: Criar Serviço
- [ ] Acessar https://railway.app
- [ ] Clicar em "New Project"
- [ ] Selecionar "Deploy from GitHub repo"
- [ ] Escolher repositório `rafaelnovaes22/facilIAuto`

### Passo 2: Configurar Backend
- [ ] Nome: `faciliauto-backend`
- [ ] Root Directory: `platform/backend`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python api/main.py`

### Passo 3: Variáveis de Ambiente
- [ ] Adicionar `PORT=8000`
- [ ] Adicionar `PYTHONUNBUFFERED=1`

### Passo 4: Gerar Domínio
- [ ] Settings → Networking → Generate Domain
- [ ] Copiar URL (ex: `faciliauto-backend.up.railway.app`)
- [ ] Testar: `https://[URL]/health`

---

## 🎨 Deploy Frontend (10 min)

### Passo 1: Criar Serviço
- [ ] Clicar em "+ New" → "GitHub Repo"
- [ ] Selecionar `facilIAuto` novamente

### Passo 2: Configurar Frontend
- [ ] Nome: `faciliauto-frontend`
- [ ] Root Directory: `platform/frontend`
- [ ] Build Command: `npm install && npm run build`
- [ ] Start Command: `npm run preview`

### Passo 3: Variáveis de Ambiente
- [ ] Adicionar `VITE_API_URL=https://[backend-url]`
- [ ] Adicionar `PORT=3000`

### Passo 4: Gerar Domínio
- [ ] Settings → Networking → Generate Domain
- [ ] Copiar URL (ex: `faciliauto-frontend.up.railway.app`)

---

## 🔧 Ajustes Finais (5 min)

### Atualizar CORS
- [ ] Editar `platform/backend/api/main.py`
- [ ] Adicionar URL do frontend em `allow_origins`
- [ ] Commit e push

### Criar .env.production
- [ ] Criar `platform/frontend/.env.production`
- [ ] Adicionar `VITE_API_URL=https://[backend-url]`
- [ ] Commit e push

---

## ✅ Verificação (5 min)

### Backend
- [ ] Acessar `https://[backend-url]/health`
- [ ] Deve retornar `{"status": "healthy"}`
- [ ] Acessar `https://[backend-url]/docs`
- [ ] Swagger UI deve carregar

### Frontend
- [ ] Acessar `https://[frontend-url]`
- [ ] Página inicial deve carregar
- [ ] Preencher questionário
- [ ] Selecionar perfil "Comercial"

### Validação Funcional
- [ ] ✅ Fiat Fiorino aparece (ideal)
- [ ] ✅ Fiat Strada aparece (ideal)
- [ ] ✅ Hyundai HR aparece com avisos (limitado)
- [ ] ❌ Fiat Toro NÃO aparece (rejeitado)
- [ ] ❌ Jeep Compass NÃO aparece (rejeitado)

---

## 🎉 Pronto!

- [ ] Backend no ar: `https://[backend-url]`
- [ ] Frontend no ar: `https://[frontend-url]`
- [ ] Funcionalidade validada
- [ ] Compartilhar URLs com equipe

---

## 📝 Anotações

**Backend URL**: ___________________________________

**Frontend URL**: ___________________________________

**Data Deploy**: ___________________________________

**Problemas Encontrados**: 
___________________________________
___________________________________

---

**Guia Completo**: `docs/deployment/RAILWAY-DEPLOY.md`
