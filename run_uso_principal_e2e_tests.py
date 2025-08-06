#!/usr/bin/env python
"""
Script para executar testes E2E de Uso Principal seguindo metodologia XP

Este script executa os testes End-to-End específicos para a funcionalidade
de critérios de uso principal do veículo, implementada seguindo os princípios
da metodologia XP (Extreme Programming).

Categorias de testes:
- Interface melhorada do questionário
- Sistema de scoring avançado  
- Agente especializado do chatbot LangGraph
- Integração ponta-a-ponta
- Testes de regressão
- Testes de performance
"""

import subprocess
import sys
import time
import os
from typing import List, Dict

class XPTestRunner:
    """
    Runner de testes seguindo metodologia XP
    
    Princípios XP aplicados:
    - Feedback rápido
    - Testes pequenos e focados
    - Integração contínua
    - Refatoração orientada por testes
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {}
    
    def run_test_category(self, marker: str, description: str, critical: bool = True) -> bool:
        """Executa uma categoria de testes"""
        print(f"\n🧪 {description}")
        print("-" * 60)
        
        cmd = [
            sys.executable, "-m", "pytest",
            f"-m", marker,
            "-v",
            "--tb=short",
            "--no-header",
            "--no-summary",
            "-q"
        ]
        
        try:
            start = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            duration = time.time() - start
            
            success = result.returncode == 0
            
            self.results[marker] = {
                "success": success,
                "duration": duration,
                "critical": critical,
                "description": description
            }
            
            if success:
                print(f"✅ {description} - PASSOU ({duration:.1f}s)")
            else:
                print(f"❌ {description} - FALHOU ({duration:.1f}s)")
                if result.stdout:
                    print("STDOUT:", result.stdout[-500:])  # Últimas 500 chars
                if result.stderr:
                    print("STDERR:", result.stderr[-500:])
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT após 300s")
            self.results[marker] = {
                "success": False,
                "duration": 300,
                "critical": critical,
                "description": description
            }
            return False
        
        except Exception as e:
            print(f"💥 {description} - ERRO: {e}")
            self.results[marker] = {
                "success": False,
                "duration": 0,
                "critical": critical,
                "description": description
            }
            return False
    
    def run_all_uso_principal_tests(self) -> bool:
        """Executa todos os testes de uso principal"""
        print("🎯 TESTES E2E - CRITÉRIOS DE USO PRINCIPAL DO VEÍCULO")
        print("="*80)
        print("Metodologia: XP (Extreme Programming)")
        print("Abordagem: Test-Driven Development (TDD)")
        print("="*80)
        
        # Testes críticos (devem passar)
        critical_tests = [
            ("uso_principal and unit", "Testes Unitários - UsoMatcher"),
            ("uso_principal and e2e", "Testes E2E - Interface e Fluxo"),
            ("langgraph_uso_principal", "Testes E2E - Agente LangGraph"),
        ]
        
        # Testes complementares (podem falhar sem impedir deploy)
        complementary_tests = [
            ("uso_principal and performance", "Testes de Performance"),
            ("uso_principal and integration", "Testes de Integração"),
        ]
        
        all_passed = True
        critical_passed = True
        
        # Executar testes críticos
        print("\n🔥 TESTES CRÍTICOS (obrigatórios)")
        for marker, description in critical_tests:
            success = self.run_test_category(marker, description, critical=True)
            if not success:
                critical_passed = False
                all_passed = False
        
        # Executar testes complementares
        print("\n📊 TESTES COMPLEMENTARES (informativos)")
        for marker, description in complementary_tests:
            success = self.run_test_category(marker, description, critical=False)
            if not success:
                all_passed = False
        
        return critical_passed, all_passed
    
    def generate_report(self, critical_passed: bool, all_passed: bool):
        """Gera relatório final dos testes"""
        total_time = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("📋 RELATÓRIO FINAL - TESTES E2E USO PRINCIPAL")
        print("="*80)
        
        print(f"⏱️ Tempo total: {total_time:.1f}s")
        print(f"🧪 Categorias testadas: {len(self.results)}")
        
        # Resumo por categoria
        for marker, result in self.results.items():
            status = "✅ PASSOU" if result["success"] else "❌ FALHOU"
            critical = "🔥 CRÍTICO" if result["critical"] else "📊 COMPLEMENTAR"
            print(f"  {status} | {critical} | {result['description']} ({result['duration']:.1f}s)")
        
        # Status geral
        print("\n🏆 STATUS GERAL:")
        
        if critical_passed:
            print("✅ TESTES CRÍTICOS: TODOS PASSARAM")
            print("   ✓ Funcionalidade de uso principal está funcionando")
            print("   ✓ Agente LangGraph operacional")
            print("   ✓ Interface melhorada validada")
        else:
            print("❌ TESTES CRÍTICOS: FALHARAM")
            print("   ⚠️ Funcionalidade de uso principal tem problemas")
            print("   ⚠️ Revisar implementação antes do deploy")
        
        if all_passed:
            print("🎉 TODOS OS TESTES: PASSOU COMPLETO")
            print("   ✓ Sistema pronto para produção")
        else:
            print("⚠️ ALGUNS TESTES: FALHARAM")
            print("   ℹ️ Funcionalidades complementares podem ter problemas")
        
        # Recomendações XP
        print("\n💡 RECOMENDAÇÕES XP:")
        if critical_passed:
            print("   ✓ Continuar com integração contínua")
            print("   ✓ Considerar refatoração baseada em feedback")
            print("   ✓ Executar testes regularmente")
        else:
            print("   🔄 Aplicar ciclo TDD: Red → Green → Refactor")
            print("   🧪 Focar nos testes que falharam primeiro")
            print("   👥 Considerar pair programming para resolver problemas")
        
        return critical_passed

def main():
    """Função principal"""
    # Verificar se estamos no diretório correto
    if not os.path.exists("app/uso_principal_processor.py"):
        print("❌ Execute este script na raiz do projeto FacilIAuto")
        sys.exit(1)
    
    # Configurar ambiente de teste
    os.environ['PYTEST_CURRENT_TEST'] = 'uso_principal_e2e'
    
    # Executar testes
    runner = XPTestRunner()
    critical_passed, all_passed = runner.run_all_uso_principal_tests()
    
    # Gerar relatório
    success = runner.generate_report(critical_passed, all_passed)
    
    # Exit code baseado nos testes críticos
    sys.exit(0 if critical_passed else 1)

if __name__ == "__main__":
    main()