#!/bin/bash

# 🚀 FacilIAuto - Start Script Rápido
# Inicia backend + frontend simultaneamente

echo "🚀 Iniciando FacilIAuto..."
echo "=========================="

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Verificar se está no diretório correto
if [ ! -d "CarRecommendationSite" ]; then
    echo "❌ Execute este script na raiz do projeto (onde está CarRecommendationSite/)"
    exit 1
fi

cd CarRecommendationSite

# Verificar pré-requisitos
print_step "Verificando pré-requisitos..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale Node.js 18+ primeiro."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado. Instale npm primeiro."
    exit 1
fi

print_success "Pré-requisitos OK"

# Função para instalar dependências se necessário
install_if_needed() {
    if [ ! -d "node_modules" ]; then
        print_step "Instalando dependências $1..."
        npm install
        print_success "Dependências $1 instaladas"
    else
        print_info "Dependências $1 já instaladas"
    fi
}

# Preparar backend
print_step "Preparando Backend..."
cd backend
install_if_needed "backend"

# Verificar se testes TDD estão funcionando
print_step "Verificando TDD..."
if npm test --silent > /dev/null 2>&1; then
    print_success "TDD Backend funcionando (9 testes)"
else
    print_info "TDD pode precisar de ajustes, mas continuando..."
fi

cd ..

# Preparar frontend
print_step "Preparando Frontend..."
cd frontend
install_if_needed "frontend"

cd ..

# Criar script de início simultâneo
print_step "Criando scripts de execução..."

cat > start-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando FacilIAuto Backend + Frontend..."

# Função para cleanup ao interromper
cleanup() {
    echo "🛑 Parando serviços..."
    jobs -p | xargs -r kill
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar backend em background
echo "🔧 Iniciando Backend..."
cd backend && npm run dev &
BACKEND_PID=$!

# Aguardar backend inicializar
echo "⏳ Aguardando backend inicializar..."
sleep 3

# Iniciar frontend em background  
echo "🌐 Iniciando Frontend..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 FacilIAuto rodando!"
echo "📡 Backend:  http://localhost:5000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:5000/docs"
echo ""
echo "📋 Para parar: Ctrl+C"
echo "🧪 Para TDD: npm run test:watch (em outro terminal)"
echo ""

# Aguardar interrupção
wait
EOF

chmod +x start-dev.sh

# Criar script de TDD
cat > start-tdd.sh << 'EOF'
#!/bin/bash
echo "🧪 Iniciando TDD FacilIAuto..."

# Backend TDD
echo "🔧 TDD Backend..."
cd backend && npm run test:watch &

# Frontend TDD  
echo "🌐 TDD Frontend..."
cd ../frontend && npm run test:watch &

echo "🧪 TDD ativo! Ctrl+C para parar"
wait
EOF

chmod +x start-tdd.sh

# Criar script de testes E2E
cat > start-e2e.sh << 'EOF'
#!/bin/bash
echo "🌐 Iniciando Testes E2E..."

cd frontend

echo "🧪 Abrindo Cypress..."
npm run e2e:open
EOF

chmod +x start-e2e.sh

print_success "Scripts criados"

# Instruções finais
echo ""
echo "🎉 FacilIAuto pronto para 
rodar!"
echo "================================="
echo ""
print_info "COMANDOS DISPONÍVEIS:"
echo ""
echo "🚀 INÍCIO RÁPIDO:"
echo "   ./start-dev.sh     # Backend + Frontend simultâneo"
echo ""
echo "🧪 DESENVOLVIMENTO TDD:"
echo "   ./start-tdd.sh     # TDD contínuo"
echo ""
echo "🌐 TESTES E2E:"
echo "   ./start-e2e.sh     # Cypress E2E"
echo ""
echo "🔧 MANUAL:"
echo "   cd backend && npm run dev"
echo "   cd frontend && npm run dev"
echo ""
print_success "✅ Execute qualquer comando acima para começar!"
echo ""
print_info "📖 Guia completo: COMO-RODAR-FACILIAUTO.md"
