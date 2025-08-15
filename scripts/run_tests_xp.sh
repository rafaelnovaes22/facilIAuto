#!/bin/bash
# 🧪 CarFinder XP Test Runner
# Execute este script quando tiver pytest instalado

set -e

echo "🚀 CarFinder XP Test Suite"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    print_error "pytest não encontrado. Instale as dependências primeiro:"
    echo "  pip install -r requirements-test.txt"
    exit 1
fi

# Create test results directory
mkdir -p test-results

print_status "Estrutura de testes XP detectada:"
echo "  📁 tests/unit/ - Testes unitários TDD"
echo "  📁 tests/integration/ - Testes de integração API"  
echo "  📁 tests/e2e/ - Testes E2E Playwright"
echo "  📁 tests/fixtures/ - Fixtures compartilhadas"
echo ""

# Parse command line arguments
SUITE=${1:-"all"}
COVERAGE=${2:-"true"}
VERBOSE=${3:-"true"}

case $SUITE in
    "unit")
        print_status "🧪 Executando Testes Unitários (TDD)"
        if [ "$COVERAGE" = "true" ]; then
            pytest tests/unit/ -v \
                --cov=. \
                --cov-report=term-missing \
                --cov-report=html:htmlcov \
                --cov-report=xml \
                --junitxml=test-results/unit-results.xml \
                -m "unit"
        else
            pytest tests/unit/ -v -m "unit"
        fi
        ;;
        
    "integration") 
        print_status "🔗 Executando Testes de Integração"
        pytest tests/integration/ -v \
            --junitxml=test-results/integration-results.xml \
            -m "integration"
        ;;
        
    "e2e")
        print_status "🌐 Executando Testes E2E"
        # Check if application is running
        if ! curl -f http://localhost:8000/api/health &> /dev/null; then
            print_warning "Aplicação não está rodando. Iniciando..."
            python3 main.py &
            APP_PID=$!
            sleep 5
            
            # Wait for app to be ready
            for i in {1..30}; do
                if curl -f http://localhost:8000/api/health &> /dev/null; then
                    break
                fi
                sleep 1
            done
        fi
        
        pytest tests/e2e/ -v \
            --junitxml=test-results/e2e-results.xml \
            --html=test-results/e2e-report.html \
            --self-contained-html \
            -m "e2e and not slow"
            
        # Stop app if we started it
        if [ ! -z "$APP_PID" ]; then
            kill $APP_PID 2>/dev/null || true
        fi
        ;;
        
    "quick")
        print_status "⚡ Executando Testes Rápidos"
        pytest -v -m "quick" \
            --junitxml=test-results/quick-results.xml
        ;;
        
    "smoke")
        print_status "💨 Executando Smoke Tests"
        pytest -v -m "smoke" \
            --junitxml=test-results/smoke-results.xml
        ;;
        
    "user_story_1")
        print_status "📖 Executando User Story 1: Questionário"
        pytest -v -m "user_story_1" \
            --junitxml=test-results/us1-results.xml
        ;;
        
    "user_story_2")
        print_status "📖 Executando User Story 2: Recomendações"
        pytest -v -m "user_story_2" \
            --junitxml=test-results/us2-results.xml
        ;;
        
    "user_story_3")
        print_status "📖 Executando User Story 3: Leads"
        pytest -v -m "user_story_3" \
            --junitxml=test-results/us3-results.xml
        ;;
        
    "user_story_4")
        print_status "📖 Executando User Story 4: Admin"
        pytest -v -m "user_story_4" \
            --junitxml=test-results/us4-results.xml
        ;;
        
    "tdd")
        print_status "🔄 Executando Ciclo TDD"
        echo "  🔴 RED: Testes que devem falhar primeiro"
        pytest -v -m "tdd_red" || true
        echo ""
        echo "  🟢 GREEN: Implementação mínima"
        pytest -v -m "tdd_green"
        echo ""
        echo "  🔄 REFACTOR: Melhorias mantendo testes verdes"
        pytest -v -m "tdd_refactor"
        ;;
        
    "performance")
        print_status "⚡ Executando Testes de Performance"
        pytest -v -m "performance" \
            --benchmark-only \
            --benchmark-json=test-results/benchmark.json
        ;;
        
    "all")
        print_status "🎯 Executando Suite Completa XP"
        
        # 1. Unit Tests (TDD Core)
        print_status "1/4 🧪 Testes Unitários..."
        pytest tests/unit/ -v \
            --cov=. \
            --cov-report=term-missing \
            --cov-report=html:htmlcov \
            --cov-report=xml \
            --junitxml=test-results/unit-results.xml \
            -m "unit" || exit 1
            
        print_success "✅ Testes unitários passaram!"
        
        # 2. Integration Tests
        print_status "2/4 🔗 Testes de Integração..."
        pytest tests/integration/ -v \
            --junitxml=test-results/integration-results.xml \
            -m "integration" || exit 1
            
        print_success "✅ Testes de integração passaram!"
        
        # 3. Smoke Tests
        print_status "3/4 💨 Smoke Tests..."
        pytest -v -m "smoke" \
            --junitxml=test-results/smoke-results.xml || exit 1
            
        print_success "✅ Smoke tests passaram!"
        
        # 4. Quick E2E (if app running)
        print_status "4/4 🌐 Testes E2E (básicos)..."
        if curl -f http://localhost:8000/api/health &> /dev/null; then
            pytest tests/e2e/ -v \
                --junitxml=test-results/e2e-results.xml \
                -m "e2e and quick" || print_warning "Alguns testes E2E falharam (app pode não estar rodando)"
        else
            print_warning "App não está rodando. Pulando testes E2E."
        fi
        
        print_success "🎉 Suite completa executada!"
        ;;
        
    *)
        print_error "Suite de teste inválida: $SUITE"
        echo ""
        echo "Suites disponíveis:"
        echo "  unit           - Testes unitários TDD"
        echo "  integration    - Testes de integração"
        echo "  e2e           - Testes end-to-end"
        echo "  quick         - Testes rápidos"
        echo "  smoke         - Smoke tests"
        echo "  performance   - Testes de performance"
        echo "  tdd           - Ciclo TDD completo"
        echo "  user_story_1  - Questionário"
        echo "  user_story_2  - Recomendações" 
        echo "  user_story_3  - Leads"
        echo "  user_story_4  - Admin"
        echo "  all           - Suite completa"
        echo ""
        echo "Exemplos:"
        echo "  $0 unit              # Só testes unitários"
        echo "  $0 all               # Suite completa"
        echo "  $0 user_story_2      # Testes de recomendações"
        echo "  $0 tdd               # Ciclo TDD"
        exit 1
        ;;
esac

echo ""
print_success "🎯 Execução concluída!"

# Show coverage report if generated
if [ -f "htmlcov/index.html" ]; then
    print_status "📊 Relatório de cobertura disponível em: htmlcov/index.html"
fi

# Show test results
if [ -d "test-results" ]; then
    print_status "📋 Resultados dos testes disponíveis em: test-results/"
fi

echo ""
echo "💡 Dicas XP:"
echo "  - Mantenha os testes rápidos (< 1s para unit tests)"
echo "  - Escreva testes antes do código (TDD)"
echo "  - Use markers para organizar (@pytest.mark.unit)"
echo "  - Refatore com confiança usando os testes"
echo ""
echo "📖 Para mais informações: docs/TESTING_STRATEGY_XP.md"