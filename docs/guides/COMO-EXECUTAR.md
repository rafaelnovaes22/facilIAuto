# 🚀 Como Executar o FacilIAuto

## ⚡ **Método Mais Rápido (Recomendado)**

### **Windows**
```bash
# Na raiz do projeto, execute:
start-faciliauto.bat
```

### **Linux/Mac**
```bash
# Na raiz do projeto, execute:
chmod +x start-faciliauto.sh
./start-faciliauto.sh
```

**O que acontece:**
1. ✅ Instala dependências (Python + npm) se necessário
2. ✅ Inicia backend em http://localhost:8000
3. ✅ Inicia frontend em http://localhost:3000
4. ✅ Abre navegador automaticamente

---

## 🔧 **Opções de Execução**

### **1. Script Completo (Com Setup)**
- **Windows**: `start-faciliauto.bat`
- **Linux/Mac**: `./start-faciliauto.sh`
- **Faz**: Instala dependências + Inicia serviços

### **2. Script Simples (Sem Setup)**
- **Windows**: `start-faciliauto-simple.bat`
- **Faz**: Apenas inicia serviços (assume dependências já instaladas)

### **3. Parar Serviços (Linux/Mac)**
```bash
./stop-faciliauto.sh
```

---

## 📋 **Pré-requisitos**

### **Instalar Primeiro**
- ✅ **Python 3.8+** - [Download](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Download](https://nodejs.org/)
- ✅ **Git** - [Download](https://git-scm.com/)

### **Verificar Instalação**
```bash
python --version    # ou python3 --version
node --version
npm --version
git --version
```

---

## 🎯 **Acessar Aplicação**

Após executar o script:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Frontend** | http://localhost:3000 | Interface do usuário |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Health Check** | http://localhost:8000/health | Status da API |

---

## 🔍 **Solução de Problemas**

### **Erro: Python não encontrado**
```bash
# Instalar Python
# Windows: https://www.python.org/downloads/
# Linux: sudo apt-get install python3
# Mac: brew install python3
```

### **Erro: Node.js não encontrado**
```bash
# Instalar Node.js
# Windows/Mac: https://nodejs.org/
# Linux: sudo apt-get install nodejs npm
```

### **Erro: Porta 8000 em uso**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### **Erro: Porta 3000 em uso**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

---

## 🛠️ **Execução Manual (Sem Scripts)**

### **Backend**
```bash
cd platform/backend
pip install -r requirements.txt
python api/main.py
```

### **Frontend**
```bash
cd platform/frontend
npm install
npm run dev
```

---

## ✅ **Checklist de Verificação**

Antes de usar, verifique:

- [ ] Python 3.8+ instalado
- [ ] Node.js 18+ instalado
- [ ] Na raiz do projeto (onde está `README.md`)
- [ ] Portas 3000 e 8000 livres

---

## 🎉 **Pronto!**

Execute o script e o FacilIAuto estará rodando em **http://localhost:3000** 🚀

Para mais detalhes, veja o [README.md](README.md) principal.

