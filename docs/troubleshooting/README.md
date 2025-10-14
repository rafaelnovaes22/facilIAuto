# 🔧 Troubleshooting - FacilIAuto

Soluções para problemas comuns e scripts de correção.

---

## 📋 **Arquivos de Correção**

### **Erros de Backend**
- `CORRECAO-ERRO-500.md` - Correção de erro 500 no backend
- `restart-backend.bat` - Script para reiniciar o backend (Windows)
- `RESTART-NOW.bat` - Reinício rápido (Windows)

---

## 🚨 **Problemas Comuns**

### **1. Erro 500 no Backend**
**Solução:** Ver `CORRECAO-ERRO-500.md`

```bash
# Windows
docs\troubleshooting\restart-backend.bat

# Linux/Mac
cd platform/backend
pkill -f "uvicorn"
python api/main.py
```

### **2. Frontend não conecta com Backend**
**Verificar:**
- Backend está rodando na porta 8000
- Frontend configurado para `http://localhost:8000`

```bash
# Verificar se backend está rodando
curl http://localhost:8000/health
```

### **3. Testes falhando (pytest)**
**Problema:** Incompatibilidade pydantic/langsmith

**Solução temporária:**
```bash
# Usar script Python direto
cd platform/backend
python run_fase3_tests.py
```

### **4. Node modules faltando**
```bash
cd platform/frontend
npm install
```

### **5. Python packages faltando**
```bash
cd platform/backend
pip install -r requirements.txt
```

---

## 🔄 **Scripts de Reinício**

### **Windows:**
```batch
docs\troubleshooting\restart-backend.bat
docs\troubleshooting\RESTART-NOW.bat
```

### **Linux/Mac:**
```bash
# Parar tudo
./stop-faciliauto.sh

# Iniciar tudo
./start-faciliauto.sh
```

---

## 📞 **Suporte**

Se o problema persistir:
1. Verificar logs em `platform/backend/`
2. Verificar console do navegador (Frontend)
3. Criar issue no GitHub

---

**Última atualização:** 09/10/2025

