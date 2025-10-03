#!/bin/bash
# Script para rodar todos os testes do backend
# FacilIAuto Platform - Linux/Mac

echo "========================================"
echo "FacilIAuto - Backend Tests"
echo "========================================"
echo

cd "$(dirname "$0")"

# Verificar se pytest esta instalado
if ! python -c "import pytest" 2>/dev/null; then
    echo "[ERRO] pytest nao instalado!"
    echo "Execute: pip install -r requirements.txt"
    exit 1
fi

echo "[1/3] Testes Unitarios dos Modelos..."
pytest tests/test_models.py -v

echo
echo "[2/3] Testes do Recommendation Engine..."
pytest tests/test_recommendation_engine.py -v

echo
echo "[3/3] Testes de Integracao da API..."
pytest tests/test_api_integration.py -v

echo
echo "========================================"
echo "Relatorio de Cobertura"
echo "========================================"
pytest --cov=. --cov-report=term-missing --cov-report=html

echo
echo "[OK] Todos os testes concluidos!"
echo "Relatorio HTML: htmlcov/index.html"

