#!/bin/bash

# ========================================
# FacilIAuto - Startup Script (Linux/Mac)
# ========================================

echo ""
echo "========================================"
echo "   FACILIAUTO - Iniciando Projeto"
echo "========================================"
echo ""

# Verificar se estamos na raiz do projeto
if [ ! -d "platform" ]; then
    echo "[ERRO] Execute este script na raiz do projeto FacilIAuto"
    exit 1
fi

echo "[1/5] Configurando Backend..."
echo ""

# Ir para o backend
cd platform/backend

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "[INFO] Criando ambiente virtual Python..."
    python3 -m venv venv
fi

echo "[INFO] Ativando ambiente virtual..."
source venv/bin/activate

echo "[INFO] Instalando dependências do backend..."
pip install -r requirements.txt --quiet

echo ""
echo "[2/5] Configurando Frontend..."
echo ""

# Voltar para a raiz e ir para frontend
cd ../..
cd platform/frontend

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "[ERRO] Node.js não encontrado. Instale Node.js 18+ primeiro."
    exit 1
fi

# Instalar dependências do frontend (se necessário)
if [ ! -d "node_modules" ]; then
    echo "[INFO] Instalando dependências do frontend..."
    npm install --quiet
else
    echo "[INFO] Dependências do frontend já instaladas."
fi

echo ""
echo "[3/5] Iniciando Backend API..."
echo ""

# Voltar para backend
cd ../backend

# Iniciar backend em background
source venv/bin/activate
nohup python api/main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

echo "[OK] Backend iniciado em http://localhost:8000 (PID: $BACKEND_PID)"
sleep 3

echo ""
echo "[4/5] Iniciando Frontend..."
echo ""

# Ir para frontend
cd ../frontend

# Iniciar frontend em background
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

echo "[OK] Frontend iniciado em http://localhost:3000 (PID: $FRONTEND_PID)"
sleep 3

echo ""
echo "[5/5] Abrindo navegador..."
echo ""

# Aguardar serviços iniciarem
sleep 5

# Abrir navegador (detectar SO)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
    elif command -v gnome-open &> /dev/null; then
        gnome-open http://localhost:3000
    fi
fi

# Voltar para raiz
cd ../..

echo ""
echo "========================================"
echo "   FACILIAUTO INICIADO COM SUCESSO!"
echo "========================================"
echo ""
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "   Backend PID:  $BACKEND_PID (salvo em platform/backend/backend.pid)"
echo "   Frontend PID: $FRONTEND_PID (salvo em platform/frontend/frontend.pid)"
echo ""
echo "   Para parar os serviços:"
echo "   ./stop-faciliauto.sh"
echo ""
echo "========================================"
echo ""

