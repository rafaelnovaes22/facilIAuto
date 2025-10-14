#!/bin/bash

# ========================================
# FacilIAuto - Stop Script (Linux/Mac)
# ========================================

echo ""
echo "========================================"
echo "   FACILIAUTO - Parando Serviços"
echo "========================================"
echo ""

# Parar Backend
if [ -f "platform/backend/backend.pid" ]; then
    BACKEND_PID=$(cat platform/backend/backend.pid)
    echo "[INFO] Parando Backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
    rm platform/backend/backend.pid
    echo "[OK] Backend parado"
else
    echo "[INFO] Backend não está rodando (PID file não encontrado)"
fi

# Parar Frontend
if [ -f "platform/frontend/frontend.pid" ]; then
    FRONTEND_PID=$(cat platform/frontend/frontend.pid)
    echo "[INFO] Parando Frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null
    rm platform/frontend/frontend.pid
    echo "[OK] Frontend parado"
else
    echo "[INFO] Frontend não está rodando (PID file não encontrado)"
fi

# Limpar processos Node.js e Python na porta (fallback)
echo ""
echo "[INFO] Limpando processos nas portas 3000 e 8000..."

# Porta 3000 (Frontend)
FRONTEND_PORT_PID=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    kill -9 $FRONTEND_PORT_PID 2>/dev/null
    echo "[OK] Processo na porta 3000 finalizado"
fi

# Porta 8000 (Backend)
BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_PORT_PID" ]; then
    kill -9 $BACKEND_PORT_PID 2>/dev/null
    echo "[OK] Processo na porta 8000 finalizado"
fi

echo ""
echo "========================================"
echo "   FACILIAUTO PARADO COM SUCESSO!"
echo "========================================"
echo ""

