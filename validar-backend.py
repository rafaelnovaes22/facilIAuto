#!/usr/bin/env python3
"""
Script de Validação do Backend - FacilIAuto
Valida estrutura, dependências e funcionalidades básicas
"""
import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_check(text, status):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {text}")
    return status

def check_python_version():
    """Verificar versão do Python"""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 11
    print_check(
        f"Python {version.major}.{version.minor}.{version.micro}",
        is_valid
    )
    return is_valid

def check_dependencies():
    """Verificar dependências instaladas"""
    print_header("VERIFICANDO DEPENDÊNCIAS")
    
    dependencies = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'pytest': 'Pytest'
    }
    
    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            version = __import__(module).__version__
            print_check(f"{name} {version}", True)
        except ImportError:
            print_check(f"{name} (não instalado)", False)
            all_ok = False
    
    return all_ok

def check_structure():
    """Verificar estrutura de pastas"""
    print_header("VERIFICANDO ESTRUTURA")
    
    backend_dir = Path("platform/backend")
    required_dirs = [
        "api",
        "models",
        "services",
        "tests",
        "data"
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = backend_dir / dir_name
        exists = dir_path.exists()
        print_check(f"Pasta {dir_name}/", exists)
        all_ok = all_ok and exists
    
    return all_ok

def check_files():
    """Verificar arquivos principais"""
    print_header("VERIFICANDO ARQUIVOS PRINCIPAIS")
    
    backend_dir = Path("platform/backend")
    required_files = [
        "api/main.py",
        "models/car.py",
        "models/dealership.py",
        "models/user_profile.py",
        "services/unified_recommendation_engine.py",
        "requirements.txt",
        "pytest.ini"
    ]
    
    all_ok = True
    for file_name in required_files:
        file_path = backend_dir / file_name
        exists = file_path.exists()
        print_check(f"Arquivo {file_name}", exists)
        all_ok = all_ok and exists
    
    return all_ok

def check_data():
    """Verificar arquivos de dados"""
    print_header("VERIFICANDO DADOS")
    
    backend_dir = Path("platform/backend")
    data_dir = backend_dir / "data"
    
    if not data_dir.exists():
        print_check("Pasta data/", False)
        return False
    
    data_files = list(data_dir.glob("*.json"))
    print_check(f"Arquivos JSON encontrados: {len(data_files)}", len(data_files) > 0)
    
    for file in data_files:
        print(f"  📄 {file.name}")
    
    return len(data_files) > 0

def check_tests():
    """Verificar arquivos de teste"""
    print_header("VERIFICANDO TESTES")
    
    backend_dir = Path("platform/backend")
    tests_dir = backend_dir / "tests"
    
    if not tests_dir.exists():
        print_check("Pasta tests/", False)
        return False
    
    test_files = list(tests_dir.glob("test_*.py"))
    print_check(f"Arquivos de teste encontrados: {len(test_files)}", len(test_files) > 0)
    
    for file in test_files:
        print(f"  🧪 {file.name}")
    
    return len(test_files) > 0

def test_imports():
    """Testar imports básicos"""
    print_header("TESTANDO IMPORTS")
    
    # Adicionar backend ao path
    backend_dir = Path("platform/backend").resolve()
    sys.path.insert(0, str(backend_dir))
    
    imports_to_test = [
        ("models.car", "Car"),
        ("models.dealership", "Dealership"),
        ("models.user_profile", "UserProfile"),
        ("services.unified_recommendation_engine", "UnifiedRecommendationEngine")
    ]
    
    all_ok = True
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print_check(f"Import {module_name}.{class_name}", True)
        except Exception as e:
            print_check(f"Import {module_name}.{class_name}", False)
            print(f"  Erro: {str(e)}")
            all_ok = False
    
    return all_ok

def test_engine_initialization():
    """Testar inicialização do engine"""
    print_header("TESTANDO ENGINE")
    
    try:
        backend_dir = Path("platform/backend").resolve()
        sys.path.insert(0, str(backend_dir))
        
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        
        data_dir = backend_dir / "data"
        engine = UnifiedRecommendationEngine(data_dir=str(data_dir))
        
        print_check("Engine inicializado", True)
        print_check(f"Concessionárias carregadas: {len(engine.dealerships)}", len(engine.dealerships) > 0)
        print_check(f"Carros carregados: {len(engine.all_cars)}", len(engine.all_cars) > 0)
        
        # Estatísticas
        stats = engine.get_stats()
        print(f"\n  📊 Estatísticas:")
        print(f"     Total de concessionárias: {stats['total_dealerships']}")
        print(f"     Concessionárias ativas: {stats['active_dealerships']}")
        print(f"     Total de carros: {stats['total_cars']}")
        print(f"     Carros disponíveis: {stats['available_cars']}")
        
        return True
        
    except Exception as e:
        print_check("Engine inicializado", False)
        print(f"  Erro: {str(e)}")
        return False

def generate_report(results):
    """Gerar relatório final"""
    print_header("RELATÓRIO FINAL")
    
    total = len(results)
    passed = sum(results.values())
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n  Total de verificações: {total}")
    print(f"  Verificações OK: {passed}")
    print(f"  Verificações com problema: {total - passed}")
    print(f"  Taxa de sucesso: {percentage:.1f}%")
    
    if percentage == 100:
        print("\n  🎉 BACKEND 100% VALIDADO!")
        print("  ✅ Tudo está funcionando corretamente")
    elif percentage >= 80:
        print("\n  ⚠️  BACKEND PARCIALMENTE VALIDADO")
        print("  ✅ Estrutura principal OK, alguns ajustes necessários")
    else:
        print("\n  ❌ BACKEND COM PROBLEMAS")
        print("  ⚠️  Várias verificações falharam, revisar configuração")
    
    print("\n  Próximos passos:")
    if not results.get('dependencies', False):
        print("  1. Instalar dependências: pip install -r platform/backend/requirements.txt")
    if not results.get('structure', False):
        print("  2. Verificar estrutura de pastas")
    if not results.get('data', False):
        print("  3. Verificar arquivos de dados em platform/backend/data/")
    if results.get('dependencies', False) and results.get('structure', False):
        print("  1. Rodar testes: cd platform/backend && pytest tests/ -v")
        print("  2. Iniciar API: cd platform/backend && python api/main.py")
        print("  3. Acessar: http://localhost:8000/docs")

def main():
    """Função principal"""
    print("\n" + "🚗 "*20)
    print("  VALIDAÇÃO DO BACKEND - FacilIAuto")
    print("🚗 "*20)
    
    results = {}
    
    # Executar verificações
    print_header("VERIFICANDO PYTHON")
    results['python'] = check_python_version()
    
    results['dependencies'] = check_dependencies()
    results['structure'] = check_structure()
    results['files'] = check_files()
    results['data'] = check_data()
    results['tests'] = check_tests()
    
    # Testes mais avançados (só se básico OK)
    if results['dependencies'] and results['structure']:
        results['imports'] = test_imports()
        results['engine'] = test_engine_initialization()
    
    # Relatório final
    generate_report(results)
    
    # Exit code
    all_ok = all(results.values())
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
