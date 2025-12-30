"""
Script para executar testes da FASE 3 manualmente
"""

import sys
from pathlib import Path

# Adicionar backend ao path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from services.car_metrics import CarMetricsCalculator
from models.car import Car
from models.user_profile import UserProfile
from datetime import datetime

def run_tests():
    """Executar testes da FASE 3 manualmente"""
    calculator = CarMetricsCalculator()
    passed = 0
    failed = 0
    
    print("=" * 70)
    print("EXECUTANDO TESTES DA FASE 3 - METRICAS AVANCADAS")
    print("=" * 70)
    
    # TESTE 1: Confiabilidade - Toyota novo
    print("\n[TESTE 1] Confiabilidade - Toyota novo com baixa km")
    try:
        reliability = calculator.calculate_reliability_index(
            marca="Toyota",
            ano=2024,
            quilometragem=5000
        )
        assert 0.92 <= reliability <= 0.95, f"Esperado 0.92-0.95, obtido {reliability}"
        print(f"  [OK] Confiabilidade: {reliability:.3f}")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 2: Confiabilidade - Fiat velho
    print("\n[TESTE 2] Confiabilidade - Fiat velho com alta km")
    try:
        reliability = calculator.calculate_reliability_index(
            marca="Fiat",
            ano=2015,
            quilometragem=150000
        )
        assert 0.30 <= reliability <= 0.50, f"Esperado 0.30-0.50, obtido {reliability}"
        print(f"  [OK] Confiabilidade: {reliability:.3f}")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 3: Revenda - Toyota novo
    print("\n[TESTE 3] Revenda - Toyota novo")
    try:
        resale = calculator.calculate_resale_index(
            marca="Toyota",
            categoria="SUV",
            ano=2023
        )
        assert 0.88 <= resale <= 1.0, f"Esperado 0.88-1.0, obtido {resale}"
        print(f"  [OK] Revenda: {resale:.3f}")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 4: Revenda - Fiat velho
    print("\n[TESTE 4] Revenda - Fiat velho")
    try:
        resale = calculator.calculate_resale_index(
            marca="Fiat",
            categoria="Hatch",
            ano=2015
        )
        assert 0.50 <= resale <= 0.72, f"Esperado 0.50-0.72, obtido {resale}"
        print(f"  [OK] Revenda: {resale:.3f}")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 5: Depreciação - SUV vs Hatch
    print("\n[TESTE 5] Depreciacao - SUV deprecia menos que Hatch")
    try:
        dep_suv = calculator.calculate_depreciation_rate(
            marca="Toyota",
            categoria="SUV",
            ano=2022
        )
        dep_hatch = calculator.calculate_depreciation_rate(
            marca="Fiat",
            categoria="Hatch",
            ano=2022
        )
        assert dep_suv < dep_hatch, f"SUV ({dep_suv}) deve ser < Hatch ({dep_hatch})"
        print(f"  [OK] SUV: {dep_suv:.1%}, Hatch: {dep_hatch:.1%}")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 6: Manutenção - Toyota vs BMW
    print("\n[TESTE 6] Manutencao - BMW custa mais que Toyota")
    try:
        cost_toyota = calculator.estimate_maintenance_cost(
            marca="Toyota",
            ano=2023,
            quilometragem=10000
        )
        cost_bmw = calculator.estimate_maintenance_cost(
            marca="BMW",
            ano=2023,
            quilometragem=10000
        )
        assert cost_bmw > cost_toyota, f"BMW (R$ {cost_bmw}) deve ser > Toyota (R$ {cost_toyota})"
        print(f"  [OK] Toyota: R$ {cost_toyota:.2f}, BMW: R$ {cost_bmw:.2f}")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 7: Manutenção aumenta com idade
    print("\n[TESTE 7] Manutencao - Aumenta com idade do carro")
    try:
        cost_new = calculator.estimate_maintenance_cost(
            marca="Honda",
            ano=2024,
            quilometragem=5000
        )
        cost_old = calculator.estimate_maintenance_cost(
            marca="Honda",
            ano=2015,
            quilometragem=5000
        )
        assert cost_old > cost_new, f"Velho (R$ {cost_old}) deve ser > Novo (R$ {cost_new})"
        print(f"  [OK] Novo (2024): R$ {cost_new:.2f}, Velho (2015): R$ {cost_old:.2f}")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 8: TCO - Premium vs Econômico
    print("\n[TESTE 8] TCO - Premium tem maior custo total")
    try:
        metrics_economico = calculator.calculate_all_metrics("Fiat", "Hatch", 2023, 10000)
        metrics_premium = calculator.calculate_all_metrics("BMW", "Sedan", 2023, 10000)
        
        tco_economico = calculator.get_car_total_cost_5_years(
            preco=80000,
            taxa_depreciacao=metrics_economico["taxa_depreciacao_anual"],
            custo_manutencao=metrics_economico["custo_manutencao_anual"]
        )
        tco_premium = calculator.get_car_total_cost_5_years(
            preco=80000,
            taxa_depreciacao=metrics_premium["taxa_depreciacao_anual"],
            custo_manutencao=metrics_premium["custo_manutencao_anual"]
        )
        assert tco_premium["custo_total"] > tco_economico["custo_total"], \
            f"Premium (R$ {tco_premium['custo_total']}) deve ser > Economico (R$ {tco_economico['custo_total']})"
        print(f"  [OK] Economico: R$ {tco_economico['custo_total']:.2f}, Premium: R$ {tco_premium['custo_total']:.2f}")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 9: Calcular todas as métricas
    print("\n[TESTE 9] Calcular todas as metricas de uma vez")
    try:
        metrics = calculator.calculate_all_metrics(
            marca="Toyota",
            categoria="SUV",
            ano=2023,
            quilometragem=15000
        )
        
        assert "indice_confiabilidade" in metrics
        assert "indice_revenda" in metrics
        assert "taxa_depreciacao_anual" in metrics
        assert "custo_manutencao_anual" in metrics
        
        assert 0.0 <= metrics["indice_confiabilidade"] <= 1.0
        assert 0.0 <= metrics["indice_revenda"] <= 1.0
        assert 0.0 < metrics["taxa_depreciacao_anual"] < 0.30
        assert metrics["custo_manutencao_anual"] > 0
        
        print(f"  [OK] Confiabilidade: {metrics['indice_confiabilidade']:.3f}")
        print(f"  [OK] Revenda: {metrics['indice_revenda']:.3f}")
        print(f"  [OK] Depreciacao: {metrics['taxa_depreciacao_anual']:.1%}")
        print(f"  [OK] Manutencao: R$ {metrics['custo_manutencao_anual']:.2f}")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 10: Integração com Car model
    print("\n[TESTE 10] Integracao - Car model tem campos de metricas")
    try:
        car = Car(
            id="test_car",
            dealership_id="d1",
            nome="Corolla 2024",
            marca="Toyota",
            modelo="Corolla",
            ano=2024,
            preco=135990,
            quilometragem=0,
            combustivel="Flex",
            categoria="Sedan",
            dealership_name="Test",
            dealership_city="SP",
            dealership_state="SP",
            dealership_phone="111",
            dealership_whatsapp="111",
            indice_confiabilidade=0.93,
            indice_revenda=0.90,
            taxa_depreciacao_anual=0.16,
            custo_manutencao_anual=2200.0
        )
        
        assert hasattr(car, 'indice_confiabilidade')
        assert hasattr(car, 'indice_revenda')
        assert hasattr(car, 'taxa_depreciacao_anual')
        assert hasattr(car, 'custo_manutencao_anual')
        assert car.indice_confiabilidade == 0.93
        
        print(f"  [OK] Car model possui todos os campos de metricas")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 11: UserProfile com novas prioridades
    print("\n[TESTE 11] Integracao - UserProfile com novas prioridades FASE 3")
    try:
        profile = UserProfile(
            orcamento_min=80000,
            orcamento_max=150000,
            uso_principal="trabalho",
            prioridades={
                "economia": 3,
                "espaco": 3,
                "revenda": 5,
                "confiabilidade": 5,
                "custo_manutencao": 4
            }
        )
        
        assert profile.prioridades["revenda"] == 5
        assert profile.prioridades["confiabilidade"] == 5
        assert profile.prioridades["custo_manutencao"] == 4
        
        print(f"  [OK] UserProfile possui novas prioridades FASE 3")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # TESTE 12: Edge case - Carro muito antigo
    print("\n[TESTE 12] Edge Case - Carro muito antigo (>15 anos)")
    try:
        metrics = calculator.calculate_all_metrics(
            marca="Fiat",
            categoria="Hatch",
            ano=2005,
            quilometragem=250000
        )
        
        print(f"  [INFO] Confiabilidade: {metrics['indice_confiabilidade']:.3f}")
        print(f"  [INFO] Revenda: {metrics['indice_revenda']:.3f}")
        print(f"  [INFO] Manutencao: R$ {metrics['custo_manutencao_anual']:.2f}")
        
        assert metrics["indice_confiabilidade"] < 0.45, \
            f"Confiabilidade deve ser baixa, obtido {metrics['indice_confiabilidade']:.3f}"
        assert metrics["indice_revenda"] < 0.65, \
            f"Revenda deve ser baixa, obtido {metrics['indice_revenda']:.3f}"
        assert metrics["custo_manutencao_anual"] > 2500, \
            f"Manutencao deve ser alta, obtido R$ {metrics['custo_manutencao_anual']:.2f}"
        
        print(f"  [OK] Metricas corretas para carro muito antigo")
        passed += 1
    except Exception as e:
        print(f"  [ERRO] {e}")
        failed += 1
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    print(f"Total de testes: {passed + failed}")
    print(f"Testes passaram: {passed} [OK]")
    print(f"Testes falharam: {failed} [ERRO]")
    print(f"Percentual: {passed/(passed+failed)*100:.1f}%")
    print("=" * 70)
    
    if failed == 0:
        print("\n[SUCESSO] TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"\n[FALHA] {failed} teste(s) falharam.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())

