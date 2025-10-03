# 🚀 Como Rodar o FacilIAuto - Guia Completo

## 📋 PRÉ-REQUISITOS

```bash
# Verificar se está tudo instalado
node --version    # Precisa 18+
npm --version     # Precisa 8+
python --version  # Precisa 3.8+
```

---

## 🎭 OPÇÃO 1: SETUP XP COMPLETO (RECOMENDADO)

### 📁 Setup Inicial com Metodologia XP

```bash
# 1. Navegar para o projeto
cd CarRecommendationSite

# 2. Executar setup XP automático
# Linux/Mac:
chmod +x setup-xp.sh
./setup-xp.sh

# Windows:
setup-xp.bat

# 3. Iniciar desenvolvimento XP
./start-dev.sh  # Criado pelo setup
```

**✅ O que o setup XP faz:**
- ✅ Configura Git hooks automáticos
- ✅ Instala todas as dependências
- ✅ Configura ambiente TDD
- ✅ Prepara testes E2E
- ✅ Cria scripts de desenvolvimento
- ✅ Configura VS Code para pair programming

---

## 🧪 OPÇÃO 2: DESENVOLVIMENTO COM TDD

### 🔧 Backend (TDD Implementado)

```bash
# 1. Backend com TDD ativo
cd CarRecommendationSite/backend

# 2. Instalar dependências
npm install

# 3. Rodar em modo TDD (watch)
npm run test:watch  # TDD contínuo ✅

# 4. Rodar backend (outro terminal)
npm run dev  # Servidor em http://localhost:5000
```

### 🌐 Frontend (React + Vite)

```bash
# 1. Frontend (novo terminal)
cd CarRecommendationSite/frontend

# 2. Instalar dependências
npm install

# 3. Rodar frontend
npm run dev  # http://localhost:3000

# 4. Testes unitários (outro terminal)
npm run test:watch  # Testes contínuos
```

### 🧪 Testes E2E

```bash
# No diretório frontend
npm run e2e:open    # Interface interativa
# ou
npm run e2e         # Execução headless
```

---

## ⚡ OPÇÃO 3: EXECUÇÃO RÁPIDA

### 🚀 Para Demonstração

```bash
# 1. Backend rápido
cd CarRecommendationSite/backend
npm install && npm run dev

# 2. Frontend rápido (novo terminal)
cd CarRecommendationSite/frontend  
npm install && npm run dev

# ✅ Projeto rodando:
# Backend:  http://localhost:5000
# Frontend: http://localhost:3000
```

---

## 🎯 OPÇÃO 4: SISTEMA COMPLETO (PRODUÇÃO-LIKE)

### 🔧 Backend Completo

```bash
cd CarRecommendationSite/backend

# Desenvolvimento
npm run dev

# Produção
npm run build
npm start

# Testes
npm test                 # TDD suite
npm run test:coverage    # Com coverage
npm run lint            # Code quality
```

### 🌐 Frontend Completo

```bash
cd CarRecommendationSite/frontend

# Desenvolvimento
npm run dev

# Produção
npm run build
npm run preview

# Testes
npm run test:unit       # Unitários
npm run test:component  # Componentes
npm run e2e            # End-to-end
npm run test:coverage  # Coverage
```

---

## 🎭 OPÇÃO 5: METODOLOGIA XP ATIVA

### 👥 Para Pair Programming

```bash
# 1. Setup para pairs
cd CarRecommendationSite
code .  # VS Code com Live Share

# 2. TDD session
cd backend
npm run test:watch

# 3. Pair rotation (15-20 min)
# Driver: escreve código
# Navigator: pensa na arquitetura
```

### 🔄 Ciclo TDD Completo

```bash
# 🔴 RED: Escrever teste que falha
cd backend
npm run test:watch

# 🟢 GREEN: Implementar código mínimo
# (editar arquivos)

# 🔵 REFACTOR: Melhorar código
npm run lint:fix
```

---

## 📊 OPÇÃO 6: VALIDAÇÃO COMPLETA

### 🧪 Executar Todos os Testes

```bash
# Script automático de validação
cd CarRecommendationSite

# Linux/Mac:
chmod +x run-full-tests.sh
./run-full-tests.sh

# Windows:
run-full-tests.bat
```

**📋 O que testa:**
- ✅ TDD Backend (9 testes)
- ✅ Testes Unitários Frontend
- ✅ Testes E2E (398 linhas)
- ✅ Metodologia XP (100/100)
- ✅ Integração completa
- ✅ Relatório detalhado

---

## 🌐 ACESSO AOS SERVIÇOS

### 📱 URLs Locais

```
🔧 Backend API:     http://localhost:5000
📚 API Docs:        http://localhost:5000/docs
🌐 Frontend:        http://localhost:3000
🧪 Test Coverage:   coverage/index.html
```

### 🔍 Monitoramento

```bash
# Logs backend
cd backend && npm run dev  # Logs em tempo real

# Logs frontend
cd frontend && npm run dev  # Hot reload ativo

# Cypress E2E
npm run e2e:open  # Interface visual
```

---

## 🚨 SOLUÇÃO DE PROBLEMAS

### ❌ Problemas Comuns

**🔧 Backend não inicia:**
```bash
cd backend
rm -rf node_modules
npm install
npm run dev
```

**🌐 Frontend não carrega:**
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

**🧪 Testes falham:**
```bash
# Backend
cd backend && npm test

# Frontend
cd frontend && npm run test:unit

# E2E
cd frontend && npm run e2e
```

### ✅ Verificação de Saúde

```bash
# Verificar se tudo está funcionando
cd CarRecommendationSite

# Backend health
curl http://localhost:5000/health

# Frontend health
curl http://localhost:3000

# Testes health
npm test  # Em ambos os diretórios
```

---

## 🎯 PRÓXIMOS PASSOS

### 🚀 Após rodar localmente:

1. **✅ Testar funcionalidade:**
   - Abrir http://localhost:3000
   - Fazer questionário completo
   - Ver recomendações com fotos

2. **✅ Validar TDD:**
   - Verificar 9 testes passando
   - Confirmar coverage 80%+

3. **✅ E2E funcionando:**
   - Cypress abrindo corretamente
   - Testes user-journey passando

4. **✅ Produção:**
   - Deploy backend (Railway/Heroku)
   - Deploy frontend (Vercel/Netlify)
   - Configurar domínio

---

## 🎭 COMANDOS RÁPIDOS

### ⚡ Para Desenvolvimento

```bash
# Tudo em um terminal
cd CarRecommendationSite/backend && npm run dev &
cd CarRecommendationSite/frontend && npm run dev &
```

### 🧪 Para Testes

```bash
# TDD ativo
cd backend && npm run test:watch &
cd frontend && npm run test:watch &
```

### 🔧 Para Debug

```bash
# Backend com debug
cd backend && npm run dev --verbose

# Frontend com debug  
cd frontend && npm run dev --debug
```

---

## 🎉 SUCESSO!

**✅ Se tudo funcionou:**
- Backend: http://localhost:5000 ✅
- Frontend: http://localhost:3000 ✅  
- Testes TDD: 9/9 passando ✅
- E2E: Cypress funcionando ✅
- XP: Metodologia ativa ✅

**🚀 Projeto FacilIAuto rodando com metodologia XP completa!**
