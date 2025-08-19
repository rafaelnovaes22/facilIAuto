#!/bin/bash

# Script para fazer push do projeto FeiraBrás para o GitHub

echo "🚀 Enviando projeto FeiraBrás para GitHub..."
echo "================================================"

# Verifica se está no diretório correto
if [ ! -f "package.json" ]; then
    echo "❌ Erro: Execute este script dentro do diretório feira-bras-app"
    exit 1
fi

# Remove remote antigo se existir
echo "📝 Configurando repositório remoto..."
git remote remove origin 2>/dev/null

# Adiciona o novo remote
git remote add origin https://github.com/rafaelnovaes22/modexar.git

# Mostra status
echo ""
echo "📊 Status do Git:"
git status --short

# Mostra commits que serão enviados
echo ""
echo "📋 Commits a serem enviados:"
git log --oneline -5

# Faz o push
echo ""
echo "📤 Enviando para GitHub..."
echo "Você precisará inserir suas credenciais do GitHub"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Projeto enviado com sucesso!"
    echo "🔗 Acesse: https://github.com/rafaelnovaes22/modexar"
else
    echo ""
    echo "⚠️  Houve um problema no envio."
    echo ""
    echo "Tente uma das seguintes opções:"
    echo ""
    echo "1. Use um Personal Access Token:"
    echo "   git push https://SEU_USUARIO:SEU_TOKEN@github.com/rafaelnovaes22/modexar.git main"
    echo ""
    echo "2. Configure SSH:"
    echo "   git remote set-url origin git@github.com:rafaelnovaes22/modexar.git"
    echo "   git push -u origin main"
    echo ""
    echo "3. Force push (sobrescreve o remoto):"
    echo "   git push -f origin main"
fi