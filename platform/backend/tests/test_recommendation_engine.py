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
from models.user_profile import UserProfile, TCOBreakdown, FinancialCapacity
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


    def test_filter_by_preferences_marcas_preferidas(self, temp_data_dir, multiple_cars):
        """
        🔥 NOVO: Teste filtro obrigatório de marcas preferidas
        Quando marcas são especificadas, APENAS essas marcas devem retornar
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com marcas preferidas
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="familia",
            tamanho_familia=4,
            marcas_preferidas=["Toyota", "Honda"]
        )
        
        # Aplicar filtro
        filtered = engine.filter_by_preferences(multiple_cars, profile)
        
        # TODOS os carros devem ser Toyota ou Honda
        for car in filtered:
            assert car.marca in ["Toyota", "Honda"], f"Carro {car.marca} não deveria estar nos resultados"
        
        # Verificar que carros de outras marcas foram eliminados
        other_brands = [c for c in multiple_cars if c.marca not in ["Toyota", "Honda"]]
        assert len(other_brands) > 0, "Teste precisa ter carros de outras marcas"
        assert len(filtered) < len(multiple_cars), "Filtro não eliminou carros"
    
    def test_filter_by_preferences_marcas_rejeitadas(self, temp_data_dir, multiple_cars):
        """
        🔥 NOVO: Teste filtro obrigatório de marcas rejeitadas
        Marcas rejeitadas devem ser ELIMINADAS dos resultados
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com marcas rejeitadas
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="familia",
            tamanho_familia=4,
            marcas_rejeitadas=["Fiat", "Chevrolet"]
        )
        
        # Aplicar filtro
        filtered = engine.filter_by_preferences(multiple_cars, profile)
        
        # NENHUM carro deve ser Fiat ou Chevrolet
        for car in filtered:
            assert car.marca not in ["Fiat", "Chevrolet"], f"Carro {car.marca} deveria ter sido eliminado"
    
    def test_filter_by_preferences_tipos_preferidos(self, temp_data_dir, multiple_cars):
        """
        🔥 NOVO: Teste filtro obrigatório de tipos preferidos
        Quando tipos são especificados, APENAS esses tipos devem retornar
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com tipos preferidos
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="familia",
            tamanho_familia=4,
            tipos_preferidos=["SUV", "Sedan"]
        )
        
        # Aplicar filtro
        filtered = engine.filter_by_preferences(multiple_cars, profile)
        
        # TODOS os carros devem ser SUV ou Sedan
        for car in filtered:
            assert car.categoria in ["SUV", "Sedan"], f"Carro {car.categoria} não deveria estar nos resultados"
    
    def test_filter_by_preferences_combustivel(self, temp_data_dir, multiple_cars):
        """
        🔥 NOVO: Teste filtro obrigatório de combustível
        Quando combustível é especificado, APENAS esse combustível deve retornar
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com combustível preferido
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="trabalho",
            tamanho_familia=1,
            combustivel_preferido="Flex"
        )
        
        # Aplicar filtro
        filtered = engine.filter_by_preferences(multiple_cars, profile)
        
        # TODOS os carros devem ser Flex
        for car in filtered:
            assert car.combustivel == "Flex", f"Carro {car.combustivel} não deveria estar nos resultados"
    
    def test_filter_by_preferences_cambio(self, temp_data_dir, multiple_cars):
        """
        🔥 NOVO: Teste filtro obrigatório de câmbio
        Quando câmbio é especificado, APENAS esse câmbio deve retornar
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com câmbio preferido
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="trabalho",
            tamanho_familia=1,
            cambio_preferido="Automático"
        )
        
        # Aplicar filtro
        filtered = engine.filter_by_preferences(multiple_cars, profile)
        
        # TODOS os carros devem ter câmbio automático
        for car in filtered:
            assert car.cambio and "Automático" in car.cambio, f"Carro {car.cambio} não deveria estar nos resultados"
    
    def test_filter_by_preferences_multiplos_filtros(self, temp_data_dir, multiple_cars):
        """
        🔥 NOVO: Teste múltiplos filtros obrigatórios simultaneamente
        Todos os filtros devem ser aplicados em conjunto (AND lógico)
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com múltiplos filtros
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="familia",
            tamanho_familia=4,
            marcas_preferidas=["Toyota", "Honda"],
            tipos_preferidos=["SUV"],
            combustivel_preferido="Flex"
        )
        
        # Aplicar filtro
        filtered = engine.filter_by_preferences(multiple_cars, profile)
        
        # TODOS os carros devem atender TODOS os critérios
        for car in filtered:
            assert car.marca in ["Toyota", "Honda"], f"Marca {car.marca} incorreta"
            assert car.categoria == "SUV", f"Categoria {car.categoria} incorreta"
            assert car.combustivel == "Flex", f"Combustível {car.combustivel} incorreto"
    
    def test_recommend_with_mandatory_filters(self, temp_data_dir, multiple_cars):
        """
        🔥 NOVO: Teste integração completa com filtros obrigatórios
        Verificar que recommend() aplica todos os filtros corretamente
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        engine.all_cars = multiple_cars
        
        # Criar perfil com filtros obrigatórios
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="familia",
            tamanho_familia=4,
            ano_minimo=2018,
            km_maxima=80000,
            marcas_preferidas=["Toyota"],
            tipos_preferidos=["SUV"]
        )
        
        # Gerar recomendações
        recommendations = engine.recommend(profile, limit=10)
        
        # Verificar que TODOS os resultados atendem aos filtros
        for rec in recommendations:
            car = rec['car']
            assert car.preco >= 50000 and car.preco <= 150000, "Orçamento violado"
            assert car.ano >= 2018, "Ano mínimo violado"
            assert car.quilometragem <= 80000, "KM máxima violada"
            assert car.marca == "Toyota", "Marca preferida violada"
            assert car.categoria == "SUV", "Tipo preferido violado"
    
    def test_recommend_empty_results_when_no_match(self, temp_data_dir, multiple_cars):
        """
        🔥 NOVO: Teste que retorna lista vazia quando nenhum carro atende aos filtros
        Não deve haver fallback que ignora filtros obrigatórios
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        engine.all_cars = multiple_cars
        
        # Criar perfil com filtros impossíveis de atender
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=150000,
            uso_principal="familia",
            tamanho_familia=4,
            marcas_preferidas=["Ferrari"],  # Marca que não existe no estoque
            tipos_preferidos=["SUV"]
        )
        
        # Gerar recomendações
        recommendations = engine.recommend(profile, limit=10)
        
        # Deve retornar lista vazia
        assert len(recommendations) == 0, "Deveria retornar lista vazia quando nenhum carro atende aos filtros"
    
    def test_assess_financial_health_green_status(self, temp_data_dir):
        """
        Teste: Status verde (saudável) para TCO ≤20% da renda
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com renda de 8k-12k (média: 10k)
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000,
                is_disclosed=True
            )
        )
        
        # TCO de R$ 2.000 = 20% de R$ 10.000
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=200.0,
            insurance_monthly=150.0,
            ipva_monthly=50.0,
            total_monthly=2000.0,
            assumptions={}
        )
        
        # Avaliar saúde financeira
        health = engine.assess_financial_health(tco, profile)
        
        # Verificações
        assert health is not None
        assert health['status'] == 'healthy'
        assert health['color'] == 'green'
        assert health['message'] == 'Saudável'
        assert health['percentage'] == 20.0
    
    def test_assess_financial_health_yellow_status(self, temp_data_dir):
        """
        Teste: Status amarelo (atenção) para TCO entre 20-30% da renda
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com renda de 8k-12k (média: 10k)
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000,
                is_disclosed=True
            )
        )
        
        # TCO de R$ 2.500 = 25% de R$ 10.000
        tco = TCOBreakdown(
            financing_monthly=1500.0,
            fuel_monthly=500.0,
            maintenance_monthly=250.0,
            insurance_monthly=200.0,
            ipva_monthly=50.0,
            total_monthly=2500.0,
            assumptions={}
        )
        
        # Avaliar saúde financeira
        health = engine.assess_financial_health(tco, profile)
        
        # Verificações
        assert health is not None
        assert health['status'] == 'caution'
        assert health['color'] == 'yellow'
        assert health['message'] == 'Atenção'
        assert health['percentage'] == 25.0
    
    def test_assess_financial_health_red_status(self, temp_data_dir):
        """
        Teste: Status vermelho (alto comprometimento) para TCO >30% da renda
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com renda de 8k-12k (média: 10k)
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000,
                is_disclosed=True
            )
        )
        
        # TCO de R$ 3.500 = 35% de R$ 10.000
        tco = TCOBreakdown(
            financing_monthly=2000.0,
            fuel_monthly=700.0,
            maintenance_monthly=400.0,
            insurance_monthly=300.0,
            ipva_monthly=100.0,
            total_monthly=3500.0,
            assumptions={}
        )
        
        # Avaliar saúde financeira
        health = engine.assess_financial_health(tco, profile)
        
        # Verificações
        assert health is not None
        assert health['status'] == 'high_commitment'
        assert health['color'] == 'red'
        assert health['message'] == 'Alto comprometimento'
        assert health['percentage'] == 35.0
    
    def test_assess_financial_health_percentage_accuracy(self, temp_data_dir):
        """
        Teste: Precisão do cálculo de percentual
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com renda de 5k-8k (média: 6.5k)
        profile = UserProfile(
            orcamento_min=30000,
            orcamento_max=60000,
            uso_principal="trabalho",
            financial_capacity=FinancialCapacity(
                monthly_income_range="5000-8000",
                max_monthly_tco=1800,
                is_disclosed=True
            )
        )
        
        # TCO de R$ 1.300 = 20% de R$ 6.500
        tco = TCOBreakdown(
            financing_monthly=800.0,
            fuel_monthly=300.0,
            maintenance_monthly=100.0,
            insurance_monthly=80.0,
            ipva_monthly=20.0,
            total_monthly=1300.0,
            assumptions={}
        )
        
        # Avaliar saúde financeira
        health = engine.assess_financial_health(tco, profile)
        
        # Verificações de precisão
        assert health is not None
        assert health['percentage'] == 20.0
        assert health['status'] == 'healthy'
        
        # Testar com TCO diferente: R$ 1.950 = 30% de R$ 6.500
        tco2 = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=450.0,
            maintenance_monthly=150.0,
            insurance_monthly=120.0,
            ipva_monthly=30.0,
            total_monthly=1950.0,
            assumptions={}
        )
        
        health2 = engine.assess_financial_health(tco2, profile)
        assert health2 is not None
        assert health2['percentage'] == 30.0
        assert health2['status'] == 'caution'
    
    def test_assess_financial_health_no_financial_capacity(self, temp_data_dir):
        """
        Teste: Retornar None quando não há capacidade financeira informada
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil SEM capacidade financeira
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia"
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=200.0,
            insurance_monthly=150.0,
            ipva_monthly=50.0,
            total_monthly=2000.0,
            assumptions={}
        )
        
        # Avaliar saúde financeira
        health = engine.assess_financial_health(tco, profile)
        
        # Deve retornar None
        assert health is None
    
    def test_assess_financial_health_not_disclosed(self, temp_data_dir):
        """
        Teste: Retornar None quando capacidade financeira não foi divulgada
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        engine = UnifiedRecommendationEngine(data_dir=temp_data_dir)
        
        # Criar perfil com capacidade financeira não divulgada
        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=100000,
            uso_principal="familia",
            financial_capacity=FinancialCapacity(
                monthly_income_range="8000-12000",
                max_monthly_tco=3000,
                is_disclosed=False  # Não divulgado
            )
        )
        
        tco = TCOBreakdown(
            financing_monthly=1200.0,
            fuel_monthly=400.0,
            maintenance_monthly=200.0,
            insurance_monthly=150.0,
            ipva_monthly=50.0,
            total_monthly=2000.0,
            assumptions={}
        )
        
        # Avaliar saúde financeira
        health = engine.assess_financial_health(tco, profile)
        
        # Deve retornar None
        assert health is None
