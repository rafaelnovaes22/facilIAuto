"""
Testes de Classificação e Recomendação por Perfil
Valida que as categorias estão corretas e recomendações são precisas
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.car_classifier import CarClassifier
from services.unified_recommendation_engine import UnifiedRecommendationEngine
from models.user_profile import UserProfile


class TestCarClassification:
    """Testes de classificação de carros"""
    
    def test_tracker_is_suv(self):
        """CHEVROLET TRACKER deve ser SUV, não Hatch"""
        classifier = CarClassifier()
        categoria = classifier.classify("CHEVROLET TRACKER T", "CHEVROLET TRACKER T")
        assert categoria == "SUV", f"TRACKER deveria ser SUV, mas foi classificado como {categoria}"
        print("[OK] TRACKER corretamente classificado como SUV")
    
    def test_frontier_is_pickup(self):
        """NISSAN FRONTIER deve ser Pickup, não Hatch"""
        classifier = CarClassifier()
        categoria = classifier.classify("NISSAN FRONTIER ATTACK", "NISSAN FRONTIER ATTACK")
        assert categoria == "Pickup", f"FRONTIER deveria ser Pickup, mas foi classificado como {categoria}"
        print("[OK] FRONTIER corretamente classificado como Pickup")
    
    def test_corolla_is_sedan(self):
        """TOYOTA COROLLA deve ser Sedan, não Hatch"""
        classifier = CarClassifier()
        categoria = classifier.classify("TOYOTA COROLLA GLI", "TOYOTA COROLLA GLI")
        assert categoria == "Sedan", f"COROLLA deveria ser Sedan, mas foi classificado como {categoria}"
        print("[OK] COROLLA corretamente classificado como Sedan")
    
    def test_kwid_is_compacto(self):
        """RENAULT KWID deve ser Compacto, não Hatch"""
        classifier = CarClassifier()
        categoria = classifier.classify("RENAULT KWID ZEN", "RENAULT KWID ZEN")
        assert categoria == "Compacto", f"KWID deveria ser Compacto, mas foi classificado como {categoria}"
        print("[OK] KWID corretamente classificado como Compacto")
    
    def test_spin_is_van(self):
        """CHEVROLET SPIN deve ser Van, não Hatch"""
        classifier = CarClassifier()
        categoria = classifier.classify("CHEVROLET SPIN 1.8", "CHEVROLET SPIN 1.8")
        assert categoria == "Van", f"SPIN deveria ser Van, mas foi classificado como {categoria}"
        print("[OK] SPIN corretamente classificado como Van")


class TestProfileRecommendations:
    """Testes de recomendação por perfil"""
    
    def test_familia_profile_prefers_suv(self):
        """Perfil família deve priorizar SUV e Van sobre Hatch"""
        engine = UnifiedRecommendationEngine()
        
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="familia",
            tem_criancas=True,
            prioridades={
                "seguranca": 5,
                "espaco": 5,
                "economia": 2,
                "performance": 2,
                "conforto": 4
            }
        )
        
        recs = engine.recommend(profile, limit=10)
        
        # Verificar que há recomendações
        assert len(recs) > 0, "Deveria ter recomendações para família"
        
        # Verificar que SUVs e Vans estão priorizados
        top_3 = recs[:3]
        suv_or_van_count = sum(1 for r in top_3 if r['car'].categoria in ['SUV', 'Van', 'Sedan'])
        
        assert suv_or_van_count >= 2, f"Top 3 para família deveria ter pelo menos 2 SUV/Van/Sedan, mas tem {suv_or_van_count}"
        print(f"[OK] Perfil familia priorizando corretamente (Top 3: {[r['car'].categoria for r in top_3]})")
    
    def test_primeiro_carro_prefers_hatch(self):
        """Perfil primeiro carro deve priorizar Hatch e Compacto"""
        engine = UnifiedRecommendationEngine()
        
        profile = UserProfile(
            orcamento_min=30000,
            orcamento_max=60000,
            uso_principal="primeiro_carro",
            primeiro_carro=True,
            prioridades={
                "economia": 5,
                "confiabilidade": 5,
                "custo_manutencao": 5,
                "performance": 1,
                "espaco": 2
            }
        )
        
        recs = engine.recommend(profile, limit=10)
        
        # Verificar que há recomendações
        assert len(recs) > 0, "Deveria ter recomendações para primeiro carro"
        
        # Verificar que Hatch/Compacto estão priorizados
        top_5 = recs[:5]
        small_cars_count = sum(1 for r in top_5 if r['car'].categoria in ['Hatch', 'Compacto'])
        
        assert small_cars_count >= 3, f"Top 5 para primeiro carro deveria ter pelo menos 3 Hatch/Compacto, mas tem {small_cars_count}"
        print(f"[OK] Perfil primeiro carro priorizando corretamente (Top 5: {[r['car'].categoria for r in top_5]})")
    
    def test_trabalho_prefers_sedan(self):
        """Perfil trabalho deve priorizar Sedan e Hatch"""
        engine = UnifiedRecommendationEngine()
        
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="trabalho",
            prioridades={
                "economia": 5,
                "conforto": 4,
                "performance": 3,
                "espaco": 2,
                "seguranca": 3
            }
        )
        
        recs = engine.recommend(profile, limit=10)
        
        # Verificar que há recomendações
        assert len(recs) > 0, "Deveria ter recomendações para trabalho"
        
        # Verificar que Sedan/Hatch estão priorizados
        top_5 = recs[:5]
        work_cars_count = sum(1 for r in top_5 if r['car'].categoria in ['Sedan', 'Hatch', 'Compacto'])
        
        assert work_cars_count >= 3, f"Top 5 para trabalho deveria ter pelo menos 3 Sedan/Hatch, mas tem {work_cars_count}"
        print(f"[OK] Perfil trabalho priorizando corretamente (Top 5: {[r['car'].categoria for r in top_5]})")
    
    def test_comercial_prefers_pickup(self):
        """Perfil comercial deve priorizar Pickup e Van"""
        engine = UnifiedRecommendationEngine()
        
        profile = UserProfile(
            orcamento_min=60000,
            orcamento_max=150000,
            uso_principal="comercial",
            prioridades={
                "espaco": 5,
                "confiabilidade": 5,
                "custo_manutencao": 4,
                "economia": 3,
                "performance": 3
            }
        )
        
        recs = engine.recommend(profile, limit=10)
        
        # Verificar que há recomendações
        assert len(recs) > 0, "Deveria ter recomendações para comercial"
        
        # Verificar que Pickup/Van estão priorizados
        top_3 = recs[:3]
        commercial_cars_count = sum(1 for r in top_3 if r['car'].categoria in ['Pickup', 'Van'])
        
        # Deve ter pelo menos 1 Pickup/Van no top 3
        assert commercial_cars_count >= 1, f"Top 3 para comercial deveria ter pelo menos 1 Pickup/Van, mas tem {commercial_cars_count}"
        print(f"[OK] Perfil comercial priorizando corretamente (Top 3: {[r['car'].categoria for r in top_3]})")


def run_all_tests():
    """Executar todos os testes"""
    print("=" * 70)
    print("TESTES DE CLASSIFICACAO E RECOMENDACAO")
    print("=" * 70)
    
    # Testes de classificação
    print("\n[TESTES DE CLASSIFICACAO]")
    classification_tests = TestCarClassification()
    classification_tests.test_tracker_is_suv()
    classification_tests.test_frontier_is_pickup()
    classification_tests.test_corolla_is_sedan()
    classification_tests.test_kwid_is_compacto()
    classification_tests.test_spin_is_van()
    
    # Testes de recomendação
    print("\n[TESTES DE RECOMENDACAO POR PERFIL]")
    profile_tests = TestProfileRecommendations()
    profile_tests.test_familia_profile_prefers_suv()
    profile_tests.test_primeiro_carro_prefers_hatch()
    profile_tests.test_trabalho_prefers_sedan()
    profile_tests.test_comercial_prefers_pickup()
    
    print("\n" + "=" * 70)
    print("TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()

