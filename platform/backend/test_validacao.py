"""
Script de validação dos testes - Plataforma FacilIAuto
Executa testes manuais para verificar funcionalidade
"""

import sys
from pathlib import Path

# Adicionar backend ao path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_imports():
    """Testar se todos os módulos podem ser importados"""
    print("[TEST] Testando imports...")
    try:
        from models.car import Car
        from models.dealership import Dealership
        from models.user_profile import UserProfile
        from models.feedback import FeedbackAction, UserFeedback
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        from services.feedback_engine import FeedbackEngine
        from services.car_metrics import CarMetricsCalculator
        from utils.geo_distance import haversine_distance, get_city_coordinates
        print("[OK] Todos os imports funcionaram!")
        return True
    except Exception as e:
        print(f"[ERRO] Erro nos imports: {e}")
        return False

def test_models():
    """Testar criação de modelos"""
    print("\n[TEST] Testando modelos...")
    try:
        from models.user_profile import UserProfile
        
        # Criar perfil básico
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            cidade="São Paulo",
            estado="SP"
        )
        print(f"[OK] UserProfile criado: {profile.uso_principal}")
        
        # Testar novos campos da Fase 1
        profile_fase1 = UserProfile(
            orcamento_min=60000,
            orcamento_max=90000,
            uso_principal="familia",
            cidade="São Paulo",
            estado="SP",
            ano_minimo=2020,
            km_maxima=50000,
            raio_maximo_km=30,
            must_haves=["airbag", "ar_condicionado"]
        )
        print(f"[OK] UserProfile Fase 1: ano_minimo={profile_fase1.ano_minimo}, km_maxima={profile_fase1.km_maxima}")
        
        return True
    except Exception as e:
        print(f"[ERRO] Erro nos modelos: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_geo_distance():
    """Testar cálculo de distância geográfica"""
    print("\n[TEST] Testando distâncias geográficas...")
    try:
        from utils.geo_distance import haversine_distance, get_city_coordinates
        
        # São Paulo -> Rio de Janeiro
        sp_coords = get_city_coordinates("São Paulo", "SP")
        rj_coords = get_city_coordinates("Rio de Janeiro", "RJ")
        
        if sp_coords and rj_coords:
            distance = haversine_distance(
                sp_coords[0], sp_coords[1],
                rj_coords[0], rj_coords[1]
            )
            print(f"[OK] Distância SP->RJ: {distance:.1f} km (esperado ~357 km)")
            return 350 <= distance <= 365
        else:
            print("[AVISO] Coordenadas não encontradas")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro nas distâncias: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_car_metrics():
    """Testar cálculo de métricas de carros"""
    print("\n[TEST] Testando métricas de carros (Fase 3)...")
    try:
        from services.car_metrics import CarMetricsCalculator
        
        calculator = CarMetricsCalculator()
        
        # Teste: carro Toyota 2020 com 30.000 km
        confiabilidade = calculator.calculate_reliability_index("Toyota", "Sedan")
        revenda = calculator.calculate_resale_index("Toyota", 2020, 30000)
        depreciacao = calculator.calculate_depreciation_rate("Sedan", 2020)
        manutencao = calculator.calculate_annual_maintenance_cost("Toyota", "Sedan", 2020, 30000)
        
        print(f"[OK] Toyota Sedan 2020:")
        print(f"   - Confiabilidade: {confiabilidade:.2f}")
        print(f"   - Revenda: {revenda:.2f}")
        print(f"   - Depreciação: {depreciacao:.2%}")
        print(f"   - Manutenção anual: R$ {manutencao:.2f}")
        
        return True
    except Exception as e:
        print(f"[ERRO] Erro nas métricas: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recommendation_engine():
    """Testar engine de recomendação"""
    print("\n[TEST] Testando engine de recomendação...")
    try:
        from services.unified_recommendation_engine import UnifiedRecommendationEngine
        from models.user_profile import UserProfile
        
        engine = UnifiedRecommendationEngine()
        
        # Verificar se carros foram carregados
        total_cars = len(engine.all_cars)
        print(f"[OK] Carros carregados: {total_cars}")
        
        if total_cars == 0:
            print("[AVISO] Nenhum carro encontrado nos dados!")
            return False
        
        # Criar perfil de teste
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            cidade="São Paulo",
            estado="SP"
        )
        
        # Gerar recomendações
        recommendations = engine.recommend(profile, limit=5)
        print(f"[OK] Recomendações geradas: {len(recommendations)}")
        
        if len(recommendations) > 0:
            first = recommendations[0]
            print(f"   Melhor match: {first.car.nome} - Score: {first.score:.2%}")
            print(f"   Justificativa: {first.justification[:100]}...")
        
        return True
    except Exception as e:
        print(f"[ERRO] Erro no engine: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_feedback_engine():
    """Testar sistema de feedback (Fase 2)"""
    print("\n[TEST] Testando sistema de feedback...")
    try:
        from services.feedback_engine import FeedbackEngine
        from models.feedback import FeedbackAction, UserFeedback
        from models.user_profile import UserProfile
        
        engine = FeedbackEngine()
        
        # Criar perfil
        profile = UserProfile(
            orcamento_min=60000,
            orcamento_max=90000,
            uso_principal="familia"
        )
        
        # Simular feedback positivo
        feedback = UserFeedback(
            user_id="test_user",
            car_id="car_123",
            action=FeedbackAction.LIKE,
            car_features={
                "categoria": "SUV",
                "marca": "Toyota",
                "preco": 75000
            }
        )
        
        # Adicionar feedback
        history = engine.add_feedback(feedback, profile)
        print(f"[OK] Feedback registrado: {history.feedback_count} interações")
        
        # Ajustar pesos
        adjusted_weights = engine.adjust_weights(history, profile)
        print(f"[OK] Pesos ajustados: {len(adjusted_weights)} prioridades")
        
        return True
    except Exception as e:
        print(f"[ERRO] Erro no feedback: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar todos os testes de validação"""
    print("=" * 60)
    print("VALIDACAO DA PLATAFORMA FACILIAUTO")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Modelos": test_models(),
        "Distâncias Geográficas (Fase 1)": test_geo_distance(),
        "Métricas de Carros (Fase 3)": test_car_metrics(),
        "Engine de Recomendação": test_recommendation_engine(),
        "Sistema de Feedback (Fase 2)": test_feedback_engine(),
    }
    
    print("\n" + "=" * 60)
    print(" RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "[OK] PASSOU" if result else "[ERRO] FALHOU"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"TOTAL: {passed}/{total} testes passaram ({passed/total*100:.0f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n TODOS OS TESTES PASSARAM! PLATAFORMA FUNCIONANDO CORRETAMENTE!")
        return 0
    else:
        print(f"\n[AVISO] {total - passed} teste(s) falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

