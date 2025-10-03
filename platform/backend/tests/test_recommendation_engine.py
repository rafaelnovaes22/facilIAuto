"""
Testes Unitários para UnifiedRecommendationEngine (TDD)
"""
import pytest
import json
import os
import tempfile
import shutil
from models.car import Car
from models.dealership import Dealership
from models.user_profile import UserProfile
from services.unified_recommendation_engine import UnifiedRecommendationEngine


class TestUnifiedRecommendationEngine:
    """Testes para o engine de recomendação unificado"""
    
    @pytest.fixture
    def temp_data_dir(self, sample_dealership, sample_car):
        """Criar diretório temporário com dados de teste"""
        temp_dir = tempfile.mkdtemp()
        
        # Criar dealerships.json
        dealerships_data = [sample_dealership.model_dump()]
        with open(os.path.join(temp_dir, "dealerships.json"), 'w', encoding='utf-8') as f:
            json.dump(dealerships_data, f, default=str)
        
        # Criar estoque
        cars_data = [sample_car.model_dump()]
        with open(os.path.join(temp_dir, f"{sample_dealership.id}_estoque.json"), 'w', encoding='utf-8') as f:
            json.dump(cars_data, f, default=str)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_engine_initialization(self, temp_data_dir):
        """Teste: inicializar engine com sucesso"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        assert engine is not None
        assert len(engine.dealerships) > 0
        assert len(engine.all_cars) > 0
    
    def test_load_dealerships(self, temp_data_dir):
        """Teste: carregar concessionárias"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        assert len(engine.dealerships) == 1
        assert engine.dealerships[0].id == "test_dealer"
    
    def test_load_all_cars(self, temp_data_dir):
        """Teste: carregar todos os carros"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        assert len(engine.all_cars) == 1
        assert engine.all_cars[0].dealership_id == "test_dealer"
    
    def test_filter_by_budget(self, temp_data_dir, sample_user_profile, multiple_cars):
        """Teste: filtrar carros por orçamento"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        engine.all_cars = multiple_cars  # Substituir com carros de teste
        
        filtered = engine.filter_by_budget(engine.all_cars, sample_user_profile)
        
        # Todos os carros filtrados devem estar dentro do orçamento
        for car in filtered:
            assert sample_user_profile.orcamento_min <= car.preco <= sample_user_profile.orcamento_max
    
    def test_prioritize_by_location(self, temp_data_dir, multiple_cars):
        """Teste: priorizar carros por localização"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar carros de diferentes localizações
        cars_sp = [c for c in multiple_cars[:3]]
        for car in cars_sp:
            car.dealership_city = "São Paulo"
            car.dealership_state = "SP"
        
        cars_rj = [c for c in multiple_cars[3:6]]
        for car in cars_rj:
            car.dealership_city = "Rio de Janeiro"
            car.dealership_state = "RJ"
        
        all_test_cars = cars_sp + cars_rj
        
        prioritized = engine.prioritize_by_location(all_test_cars, "São Paulo", "SP")
        
        # Primeiros devem ser de São Paulo
        assert prioritized[0].dealership_city == "São Paulo"
        assert prioritized[1].dealership_city == "São Paulo"
    
    def test_calculate_match_score(self, temp_data_dir, sample_car, sample_user_profile):
        """Teste: calcular score de compatibilidade"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        score = engine.calculate_match_score(sample_car, sample_user_profile)
        
        # Score deve estar entre 0.0 e 1.0
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)
    
    def test_score_category_by_usage(self, temp_data_dir, sample_car):
        """Teste: score de categoria por uso"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Perfil família deve valorizar Sedan/SUV
        profile_familia = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia"
        )
        
        sample_car.categoria = "SUV"
        score_suv = engine.score_category_by_usage(sample_car, profile_familia)
        
        sample_car.categoria = "Compacto"
        score_compacto = engine.score_category_by_usage(sample_car, profile_familia)
        
        # SUV deve ter score maior que Compacto para família
        assert score_suv > score_compacto
    
    def test_score_priorities(self, temp_data_dir, sample_car, sample_user_profile):
        """Teste: score baseado em prioridades"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        score = engine.score_priorities(sample_car, sample_user_profile)
        
        assert 0.0 <= score <= 1.0
    
    def test_score_preferences_marca_preferida(self, temp_data_dir, sample_car):
        """Teste: marca preferida aumenta score"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        profile_sem_preferencia = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia"
        )
        
        profile_com_preferencia = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            marcas_preferidas=["Fiat"]
        )
        
        score_sem = engine.score_preferences(sample_car, profile_sem_preferencia)
        score_com = engine.score_preferences(sample_car, profile_com_preferencia)
        
        # Score com marca preferida deve ser maior
        assert score_com > score_sem
    
    def test_score_preferences_marca_rejeitada(self, temp_data_dir, sample_car):
        """Teste: marca rejeitada diminui score"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        profile_rejeitada = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            marcas_rejeitadas=["Fiat"]
        )
        
        score = engine.score_preferences(sample_car, profile_rejeitada)
        
        # Score deve ser baixo para marca rejeitada
        assert score < 0.5
    
    def test_score_budget_position(self, temp_data_dir, sample_car):
        """Teste: posição no orçamento afeta score"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Carro no meio do orçamento
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia"
        )
        
        sample_car.preco = 75000  # Meio do orçamento
        score_meio = engine.score_budget_position(sample_car, profile)
        
        sample_car.preco = 51000  # Extremo inferior
        score_extremo = engine.score_budget_position(sample_car, profile)
        
        # Meio do orçamento deve ter score maior
        assert score_meio > score_extremo
    
    def test_recommend_basic(self, temp_data_dir, sample_user_profile):
        """Teste: gerar recomendações básicas"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        recommendations = engine.recommend(sample_user_profile, limit=5)
        
        # Deve retornar lista
        assert isinstance(recommendations, list)
        
        # Se houver resultados, validar estrutura
        if recommendations:
            rec = recommendations[0]
            assert 'car' in rec
            assert 'score' in rec
            assert 'match_percentage' in rec
            assert 'justificativa' in rec
            assert 0.0 <= rec['score'] <= 1.0
    
    def test_recommend_limit(self, temp_data_dir, sample_user_profile, multiple_cars):
        """Teste: limitar número de recomendações"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        engine.all_cars = multiple_cars
        
        recommendations = engine.recommend(sample_user_profile, limit=3)
        
        # Deve retornar no máximo 3
        assert len(recommendations) <= 3
    
    def test_recommend_score_threshold(self, temp_data_dir, sample_user_profile, multiple_cars):
        """Teste: filtrar por score mínimo"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        engine.all_cars = multiple_cars
        
        recommendations = engine.recommend(
            sample_user_profile,
            limit=10,
            score_threshold=0.8
        )
        
        # Todos devem ter score >= 0.8
        for rec in recommendations:
            assert rec['score'] >= 0.8
    
    def test_recommend_sorted_by_score(self, temp_data_dir, sample_user_profile, multiple_cars):
        """Teste: recomendações ordenadas por score"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        engine.all_cars = multiple_cars
        
        recommendations = engine.recommend(sample_user_profile, limit=5)
        
        if len(recommendations) > 1:
            # Verificar ordem decrescente de score
            for i in range(len(recommendations) - 1):
                assert recommendations[i]['score'] >= recommendations[i + 1]['score']
    
    def test_recommend_only_disponivel(self, temp_data_dir, sample_user_profile, multiple_cars):
        """Teste: recomendar apenas carros disponíveis"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Marcar alguns como indisponíveis
        multiple_cars[0].disponivel = False
        multiple_cars[1].disponivel = False
        engine.all_cars = multiple_cars
        
        recommendations = engine.recommend(sample_user_profile)
        
        # Nenhum indisponível deve aparecer
        for rec in recommendations:
            assert rec['car'].disponivel is True
    
    def test_generate_justification(self, temp_data_dir, sample_car, sample_user_profile):
        """Teste: gerar justificativa da recomendação"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        justification = engine.generate_justification(sample_car, sample_user_profile, 0.85)
        
        assert isinstance(justification, str)
        assert len(justification) > 0
    
    def test_get_stats(self, temp_data_dir):
        """Teste: obter estatísticas gerais"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        stats = engine.get_stats()
        
        assert 'total_dealerships' in stats
        assert 'active_dealerships' in stats
        assert 'total_cars' in stats
        assert 'available_cars' in stats
        assert stats['total_dealerships'] >= 0
    
    def test_group_by_state(self, temp_data_dir):
        """Teste: agrupar concessionárias por estado"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        grouped = engine._group_by_state()
        
        assert isinstance(grouped, dict)
        if engine.dealerships:
            assert len(grouped) > 0
    
    def test_group_by_category(self, temp_data_dir, multiple_cars):
        """Teste: agrupar carros por categoria"""
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        engine.all_cars = multiple_cars
        
        grouped = engine._group_by_category()
        
        assert isinstance(grouped, dict)
        assert len(grouped) > 0

