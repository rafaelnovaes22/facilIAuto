# 🚂 Deploy no Railway - FacilIAuto

**Tempo Estimado**: 20-30 minutos  
**Custo**: Free tier (500h/mês) ou $5/mês por serviço

---

## 📋 Pré-requisitos

- ✅ Conta no Railway: https://railway.app
- ✅ Login com GitHub
- ✅ Código no GitHub (já feito ✅)

---

## 🎯 Passo a Passo

### **1. Criar Projeto no Railway** (2 min)

1. Acesse https://railway.app
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha o repositório: `rafaelnovaes22/facilIAuto`
5. Railway detectará automaticamente o projeto

---

### **2. Deploy do Backend** (5 min)

#### **2.1. Configurar Serviço Backend**

1. No Railway, clique em **"+ New"** → **"GitHub Repo"**
2. Selecione `facilIAuto`
3. Configure:
   - **Name**: `faciliauto-backend`
   - **Root Directory**: `platform/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api/main.py`

#### **2.2. Variáveis de Ambiente**

No painel do backend, vá em **"Variables"** e adicione:

```bash
# Porta (Railway fornece automaticamente)
PORT=8000

# Python
PYTHONUNBUFFERED=1
```

#### **2.3. Gerar Domínio Público**

1. Vá em **"Settings"** → **"Networking"**
2. Clique em **"Generate Domain"**
3. Copie a URL (ex: `faciliauto-backend.up.railway.app`)

---

### **3. Deploy do Frontend** (5 min)

#### **3.1. Configurar Serviço Frontend**

1. No Railway, clique em **"+ New"** → **"GitHub Repo"**
2. Selecione `facilIAuto` novamente
3. Configure:
   - **Name**: `faciliauto-frontend`
   - **Root Directory**: `platform/frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview`

#### **3.2. Variáveis de Ambiente**

No painel do frontend, vá em **"Variables"** e adicione:

```bash
# URL do Backend (use a URL gerada no passo 2.3)
VITE_API_URL=https://faciliauto-backend.up.railway.app

# Número do WhatsApp (formato: DDI + DDD + Número)
VITE_WHATSAPP_NUMBER=5511949105033

# Porta
PORT=3000
```

**⚠️ IMPORTANTE**: 
- `VITE_API_URL` é **obrigatória** e deve apontar para a URL do backend
- `VITE_WHATSAPP_NUMBER` é **obrigatória** no formato DDI + DDD + Número (ex: 5511949105033)
- A aplicação **não iniciará** se essas variáveis estiverem ausentes ou inválidas
- Railway aplica as variáveis automaticamente no próximo deploy

#### **3.3. Gerar Domínio Público**

1. Vá em **"Settings"** → **"Networking"**
2. Clique em **"Generate Domain"**
3. Copie a URL (ex: `faciliauto-frontend.up.railway.app`)

---

### **4. Atualizar CORS no Backend** (2 min)

Após obter a URL do frontend, atualize o CORS:

```python
# platform/backend/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://faciliauto-frontend.up.railway.app",  # Produção
        "http://localhost:3000"  # Desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Faça commit e push:
```bash
git add platform/backend/api/main.py
git commit -m "fix: atualizar CORS para Railway"
git push
```

Railway fará redeploy automático! 🚀

---

### **5. Atualizar API URL no Frontend** (2 min)

Crie arquivo `.env.production`:

```bash
# platform/frontend/.env.production
VITE_API_URL=https://faciliauto-backend.up.railway.app
```

Faça commit e push:
```bash
git add platform/frontend/.env.production
git commit -m "fix: configurar API URL para produção"
git push
```

---

## ✅ Verificação

### **Backend**
Acesse: `https://faciliauto-backend.up.railway.app/health`

Deve retornar:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### **API Docs**
Acesse: `https://faciliauto-backend.up.railway.app/docs`

### **Frontend**
Acesse: `https://faciliauto-frontend.up.railway.app`

---

## 🧪 Testar Funcionalidade

1. Acesse o frontend
2. Preencha o questionário
3. Selecione perfil **"Comercial"**
4. Verifique que:
   - ✅ Fiat Fiorino, Strada aparecem (ideais)
   - ✅ Hyundai HR aparece com avisos (limitado)
   - ❌ Fiat Toro, Jeep Compass não aparecem (rejeitados)

---

## 📊 Monitoramento

### **Logs**
- Backend: Railway Dashboard → `faciliauto-backend` → **"Deployments"** → **"View Logs"**
- Frontend: Railway Dashboard → `faciliauto-frontend` → **"Deployments"** → **"View Logs"**

### **Métricas**
- CPU, RAM, Network no Railway Dashboard

---

## 💰 Custos

### **Free Tier**
- ✅ 500 horas/mês por serviço
- ✅ 2 serviços = 1.000 horas/mês total
- ✅ Suficiente para testes e MVP

### **Hobby Plan** ($5/mês por serviço)
- Uso ilimitado
- Melhor performance
- Domínio customizado

---

## 🔧 Troubleshooting

### **Erro: Build Failed**

**Backend**:
```bash
# Verificar requirements.txt
cd platform/backend
pip install -r requirements.txt
```

**Frontend**:
```bash
# Verificar package.json
cd platform/frontend
npm install
npm run build
```

### **Erro: Missing environment variable**

Se o build falhar com erro de variável de ambiente:

```
❌ Missing required environment variable: VITE_API_URL
```

**Solução**:
1. Vá em Railway Dashboard → Frontend Service → **"Variables"**
2. Adicione a variável faltante:
   - `VITE_API_URL`: URL do backend (ex: `https://faciliauto-backend.up.railway.app`)
   - `VITE_WHATSAPP_NUMBER`: Número do WhatsApp (ex: `5511949105033`)
3. Railway fará redeploy automaticamente

### **Erro: Invalid VITE_API_URL format**

Se o build falhar com erro de formato de URL:

```
❌ Invalid VITE_API_URL format: invalid-url
Expected format: http://localhost:8000 or https://api.example.com
```

**Solução**:
1. Verifique que a URL começa com `http://` ou `https://`
2. Verifique que não há espaços ou caracteres inválidos
3. Exemplo correto: `https://faciliauto-backend.up.railway.app`

### **Erro: Cannot connect to backend**

1. Verificar URL do backend em `VITE_API_URL`
2. Verificar CORS no backend
3. Verificar logs do backend no Railway

### **Erro: Port already in use**

Railway gerencia portas automaticamente. Certifique-se de usar:
```python
port = int(os.environ.get("PORT", 8000))
```

### **Erro 405: Method Not Allowed**

Se você ver erro 405 no console do navegador:

1. Verifique que `VITE_API_URL` está configurada corretamente
2. Verifique que o backend está rodando e acessível
3. Verifique os logs do backend para erros de roteamento
4. Certifique-se que não há proxy intermediário modificando as requisições

---

## 🔐 Configuração de Variáveis de Ambiente

### **Desenvolvimento Local**

O projeto usa arquivos `.env` para configuração local:

**Backend** (`platform/backend/.env`):
```bash
# Não requer variáveis de ambiente específicas
# Porta é configurada automaticamente
```

**Frontend** (`platform/frontend/.env.development`):
```bash
# Criado automaticamente - usado em desenvolvimento
VITE_API_URL=http://localhost:8000
VITE_WHATSAPP_NUMBER=5511949105033
```

**Frontend** (`platform/frontend/.env.production`):
```bash
# Usado em builds de produção local
VITE_API_URL=https://faciliauto-backend.up.railway.app
VITE_WHATSAPP_NUMBER=5511949105033
```

### **Railway (Produção)**

Variáveis configuradas no Railway Dashboard:

**Backend**:
- `PORT`: Gerenciado automaticamente pelo Railway
- `PYTHONUNBUFFERED=1`: Para logs em tempo real

**Frontend**:
- `VITE_API_URL`: **Obrigatória** - URL do backend
- `VITE_WHATSAPP_NUMBER`: **Obrigatória** - Número do WhatsApp
- `PORT`: Gerenciado automaticamente pelo Railway

### **Validação Automática**

O frontend valida automaticamente as variáveis de ambiente na inicialização:

✅ **Validações realizadas**:
- Verifica se `VITE_API_URL` está definida
- Valida formato da URL (http:// ou https://)
- Verifica se `VITE_WHATSAPP_NUMBER` está definida
- Valida formato do número (DDI + DDD + Número)

❌ **Se houver erro**:
- Build falha com mensagem clara
- Logs indicam qual variável está faltando ou inválida
- Aplicação não inicia até correção

### **Como Atualizar Variáveis**

**Railway**:
1. Acesse Railway Dashboard
2. Selecione o serviço (backend ou frontend)
3. Vá em **"Variables"**
4. Adicione/edite a variável
5. Railway faz redeploy automaticamente

**Local**:
1. Edite o arquivo `.env.development` ou `.env.production`
2. Reinicie o servidor de desenvolvimento
3. Variáveis são carregadas automaticamente

---

## 🚀 Deploy Automático

Railway faz deploy automático a cada push no GitHub!

```bash
# Fazer mudanças
git add .
git commit -m "feat: nova funcionalidade"
git push

# Railway detecta e faz deploy automaticamente 🎉
```

---

## 📱 Domínio Customizado (Opcional)

1. Compre um domínio (ex: faciliauto.com.br)
2. No Railway: **Settings** → **Domains** → **Custom Domain**
3. Configure DNS:
   ```
   CNAME @ faciliauto-frontend.up.railway.app
   ```

---

## 🎉 Pronto!

Seu FacilIAuto está no ar! 🚀

**URLs**:
- Frontend: `https://faciliauto-frontend.up.railway.app`
- Backend: `https://faciliauto-backend.up.railway.app`
- API Docs: `https://faciliauto-backend.up.railway.app/docs`

---

## 📚 Recursos

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app

---

**Criado em**: 04 de Novembro, 2025  
**Tempo de Deploy**: 20-30 minutos  
**Status**: ✅ Pronto para uso
