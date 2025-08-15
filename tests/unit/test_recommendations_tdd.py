"""
🧪 Testes Unitários TDD - Engine de Recomendação Prática

Seguindo metodologia XP com critérios reais:
- Red: Teste falha primeiro
- Green: Implementação mínima
- Refactor: Melhoria contínua

User Story: "Como usuário, quero receber recomendações baseadas em critérios 
práticos como motivo de compra, frequência de uso, confiabilidade e revenda"
"""

import pytest
from recommendations import CarRecommender


class TestRecommendationEngineCreation:
    """
    TDD Red-Green-Refactor: Criação do Engine Prático
    """
    
    @pytest.mark.unit
    @pytest.mark.tdd_red
    def test_engine_can_be_created_with_practical_data(self):
        """
        RED: Engine deve poder ser instanciado com dados práticos
        """
        engine = CarRecommender()
        assert engine is not None
        assert hasattr(engine, 'reliability_scores')
        assert hasattr(engine, 'resale_scores')
        assert hasattr(engine, 'maintenance_costs')
    
    @pytest.mark.unit
    @pytest.mark.tdd_green
    def test_engine_has_practical_methods(self):
        """
        GREEN: Engine deve ter métodos práticos
        """
        engine = CarRecommender()
        
        # Métodos principais
        assert hasattr(engine, 'recommend')
        assert hasattr(engine, '_calculate_comprehensive_score')
        assert hasattr(engine, '_generate_detailed_reasons')
        
        # Métodos de scoring práticos
        assert hasattr(engine, '_score_main_purpose')
        assert hasattr(engine, '_score_frequency')
        assert hasattr(engine, '_score_space_needs')
        assert hasattr(engine, '_score_fuel_priority')
        assert hasattr(engine, '_score_top_priority')
        assert hasattr(engine, '_score_brand_preference')
    
    @pytest.mark.unit
    @pytest.mark.tdd_refactor
    def test_engine_loads_realistic_data(self):
        """
        REFACTOR: Engine deve carregar dados realistas do mercado
        """
        engine = CarRecommender()
        
        # Verificar dados de confiabilidade
        assert engine.reliability_scores['toyota'] == 95  # Mais confiável
        assert engine.reliability_scores['honda'] == 92
        assert engine.reliability_scores['fiat'] == 65   # Menos confiável
        
        # Verificar dados de revenda
        assert engine.resale_scores['toyota'] == 90      # Melhor revenda
        assert engine.resale_scores['honda'] == 88
        assert engine.resale_scores['fiat'] == 68        # Pior revenda
        
        # Verificar custos de manutenção
        assert engine.maintenance_costs['chevrolet'] == 90  # Mais barato
        assert engine.maintenance_costs['toyota'] == 85
        assert engine.maintenance_costs['bmw'] == 40        # Mais caro


class TestPracticalMainPurpose:
    """
    TDD: Sistema de pontuação por motivo principal de compra
    User Story: "Quero que o sistema entenda POR QUE estou comprando"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_work_app_prioritizes_economy_and_reliability(self, recommendation_engine):
        """
        Trabalho com apps deve priorizar economia máxima e durabilidade
        """
        # Arrange - Carro ideal para Uber
        car_for_uber = {
            "brand": "toyota",
            "category": "hatch",
            "consumption": 14.5,  # Excelente economia
            "price": 45000,
            "year": 2021
        }
        
        # Act
        score = recommendation_engine._score_main_purpose(car_for_uber, "work_app")
        
        # Assert
        assert score >= 85  # Deve ter score muito alto
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_family_daily_prioritizes_space_and_safety(self, recommendation_engine):
        """
        Família deve priorizar espaço, segurança e conforto
        """
        # Arrange - Carro ideal para família
        family_car = {
            "brand": "honda",
            "category": "sedan",
            "consumption": 11.5,
            "price": 85000,
            "year": 2020,
            "seats": 5
        }
        
        # Act
        score = recommendation_engine._score_main_purpose(family_car, "family_daily")
        
        # Assert
        assert score >= 80  # Deve ter score alto para família
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_first_car_prioritizes_simplicity(self, recommendation_engine):
        """
        Primeiro carro deve priorizar simplicidade e confiabilidade
        """
        # Arrange - Carro ideal para iniciante
        first_car = {
            "brand": "toyota",
            "category": "hatch",
            "consumption": 13.5,
            "price": 35000,
            "year": 2019
        }
        
        # Act
        score = recommendation_engine._score_main_purpose(first_car, "first_car")
        
        # Assert
        assert score >= 85  # Toyota hatch econômico = ideal
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_investment_prioritizes_resale_value(self, recommendation_engine):
        """
        Investimento deve priorizar valor de revenda
        """
        # Arrange - Carro com boa revenda
        investment_car = {
            "brand": "toyota",
            "model": "corolla",
            "category": "sedan",
            "year": 2020,
            "price": 90000
        }
        
        # Act
        score = recommendation_engine._score_main_purpose(investment_car, "investment")
        
        # Assert
        assert score >= 85  # Toyota Corolla = excelente para revenda


class TestFrequencyScoring:
    """
    TDD: Sistema de pontuação por frequência de uso
    User Story: "Quero que considere COM QUE FREQUÊNCIA vou usar"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_daily_work_demands_max_reliability(self, recommendation_engine):
        """
        Uso diário para trabalho exige máxima confiabilidade
        """
        # Arrange - Carro muito confiável
        reliable_car = {
            "brand": "toyota",
            "consumption": 13.0
        }
        
        # Act
        score = recommendation_engine._score_frequency(reliable_car, "daily_work")
        
        # Assert
        assert score >= 85  # Toyota com bom consumo = perfeito para trabalho diário
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_occasional_use_prioritizes_reliability_over_economy(self, recommendation_engine):
        """
        Uso esporádico prioriza confiabilidade sobre economia
        """
        # Arrange - Carro confiável mas não muito econômico
        reliable_car = {
            "brand": "honda",
            "consumption": 10.0  # Consumo médio
        }
        
        # Act
        score = recommendation_engine._score_frequency(reliable_car, "occasional")
        
        # Assert
        assert score >= 80  # Honda confiável = bom para uso esporádico
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_weekend_use_has_flexibility(self, recommendation_engine):
        """
        Uso de fim de semana permite mais flexibilidade
        """
        # Arrange - Carro comum
        weekend_car = {
            "brand": "chevrolet",
            "consumption": 11.0
        }
        
        # Act
        score = recommendation_engine._score_frequency(weekend_car, "weekends")
        
        # Assert
        assert score >= 60  # Flexibilidade para diferentes tipos


class TestSpaceNeedsScoring:
    """
    TDD: Sistema de pontuação por necessidades de espaço
    User Story: "Quero carros adequados ao meu espaço/família real"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    @pytest.mark.parametrize("space_need,car_category,expected_min_score", [
        ("solo", "hatch", 95),          # Hatch perfeito para solo
        ("couple", "sedan", 95),        # Sedan perfeito para casal  
        ("small_family", "suv", 95),    # SUV perfeito para família pequena
        ("large_family", "suv", 95),    # SUV perfeito para família grande
        ("cargo", "pickup", 95),        # Pickup perfeito para carga
    ])
    def test_space_matching_perfect_scenarios(self, recommendation_engine, space_need, car_category, expected_min_score):
        """
        Combinações perfeitas de necessidade e categoria devem ter score alto
        """
        # Arrange
        car = {"category": car_category, "seats": 5}
        
        # Act
        score = recommendation_engine._score_space_needs(car, space_need)
        
        # Assert
        assert score >= expected_min_score
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_large_family_penalizes_small_cars(self, recommendation_engine):
        """
        Família grande deve penalizar carros pequenos
        """
        # Arrange - Hatch para família grande
        small_car = {"category": "hatch", "seats": 5}
        
        # Act
        score = recommendation_engine._score_space_needs(small_car, "large_family")
        
        # Assert
        assert score <= 50  # Deve ter score baixo


class TestFuelPriorityScoring:
    """
    TDD: Sistema de pontuação por prioridade de combustível
    User Story: "Quero que entenda o quanto me preocupo com economia"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_maximum_economy_demands_best_consumption(self, recommendation_engine):
        """
        Máxima economia deve exigir melhor consumo possível
        """
        # Arrange - Carro muito econômico
        very_economical = {"consumption": 15.0}
        
        # Act
        score = recommendation_engine._score_fuel_priority(very_economical, "maximum_economy")
        
        # Assert
        assert score == 100  # 15km/l = nota máxima
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_performance_first_allows_higher_consumption(self, recommendation_engine):
        """
        Performance primeiro permite consumo maior
        """
        # Arrange - Carro potente (consome mais)
        powerful_car = {"consumption": 8.0}
        
        # Act
        score = recommendation_engine._score_fuel_priority(powerful_car, "performance_first")
        
        # Assert
        assert score >= 75  # Performance permite consumo maior


class TestTopPriorityScoring:
    """
    TDD: Sistema de prioridade máxima do cliente
    User Story: "Quero que o sistema entenda minha MAIOR prioridade"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_reliability_priority_uses_brand_data(self, recommendation_engine):
        """
        Prioridade "não dar problema" deve usar dados de confiabilidade
        """
        # Arrange - Toyota (muito confiável)
        toyota_car = {"brand": "toyota"}
        
        # Act
        score = recommendation_engine._score_top_priority(toyota_car, "reliability")
        
        # Assert
        assert score == 95  # Score de confiabilidade do Toyota
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_resale_value_priority_considers_year(self, recommendation_engine):
        """
        Prioridade "revenda" deve considerar ano do carro
        """
        # Arrange - Honda novo (boa revenda)
        new_honda = {
            "brand": "honda",
            "year": 2022  # Bem novo
        }
        
        # Act
        score = recommendation_engine._score_top_priority(new_honda, "resale_value")
        
        # Assert
        assert score >= 90  # Honda novo = excelente revenda
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_economy_priority_combines_fuel_and_maintenance(self, recommendation_engine):
        """
        Prioridade "economia" deve combinar combustível + manutenção
        """
        # Arrange - Chevrolet econômico
        economical_car = {
            "brand": "chevrolet",  # Manutenção barata
            "consumption": 14.0    # Bom consumo
        }
        
        # Act
        score = recommendation_engine._score_top_priority(economical_car, "economy")
        
        # Assert
        assert score >= 85  # Chevrolet + bom consumo = muito econômico


class TestBrandPreferenceScoring:
    """
    TDD: Sistema de preferência de marca ("eu quero")
    User Story: "Quero que o sistema respeite minha preferência de marca"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_preferred_brand_gets_maximum_score(self, recommendation_engine):
        """
        Marca preferida deve ter score máximo
        """
        # Arrange
        toyota_car = {"brand": "toyota"}
        preferences = ["toyota", "honda"]
        
        # Act
        score = recommendation_engine._score_brand_preference(toyota_car, preferences)
        
        # Assert
        assert score == 100  # Marca na preferência = score máximo
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_non_preferred_brand_gets_penalty(self, recommendation_engine):
        """
        Marca não preferida deve ter penalização
        """
        # Arrange
        fiat_car = {"brand": "fiat"}
        preferences = ["toyota", "honda"]  # Fiat não está
        
        # Act
        score = recommendation_engine._score_brand_preference(fiat_car, preferences)
        
        # Assert
        assert score == 50  # Penalização por não estar na preferência
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_no_preference_gives_neutral_score(self, recommendation_engine):
        """
        "Sem preferência" deve dar score neutro para todas
        """
        # Arrange
        any_car = {"brand": "volkswagen"}
        preferences = ["no_preference"]
        
        # Act
        score = recommendation_engine._score_brand_preference(any_car, preferences)
        
        # Assert
        assert score == 75  # Score neutro


class TestBudgetFiltering:
    """
    TDD: Filtro rigoroso por orçamento
    User Story: "Não quero ver carros fora do meu orçamento"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_budget_filter_eliminates_expensive_cars(self, recommendation_engine):
        """
        Filtro de orçamento deve eliminar carros caros
        """
        # Arrange
        cars = [
            {"id": 1, "price": 25000},  # Dentro do orçamento
            {"id": 2, "price": 35000},  # Dentro do orçamento
            {"id": 3, "price": 60000},  # Fora do orçamento
        ]
        budget = "up_30k"  # Até 30k
        
        # Act
        filtered = recommendation_engine._filter_by_budget(cars, budget)
        
        # Assert
        assert len(filtered) == 1  # Só o de 25k
        assert filtered[0]["id"] == 1
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_budget_filter_respects_ranges(self, recommendation_engine):
        """
        Filtro deve respeitar faixas específicas
        """
        # Arrange
        cars = [
            {"id": 1, "price": 25000},  # Fora da faixa
            {"id": 2, "price": 35000},  # Dentro da faixa
            {"id": 3, "price": 45000},  # Dentro da faixa
            {"id": 4, "price": 55000},  # Fora da faixa
        ]
        budget = "30k_50k"  # 30k-50k
        
        # Act
        filtered = recommendation_engine._filter_by_budget(cars, budget)
        
        # Assert
        assert len(filtered) == 2  # IDs 2 e 3
        assert all(30000 <= car["price"] <= 50000 for car in filtered)


class TestTextBoostFeature:
    """
    TDD: Sistema de boost baseado em texto livre
    User Story: "Quero que entenda melhor minhas necessidades pelo texto"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_uber_keywords_boost_economical_cars(self, recommendation_engine):
        """
        Palavras de trabalho com apps devem dar boost em carros adequados
        """
        # Arrange
        scored_cars = [
            {
                'car': {
                    'consumption': 14.0,
                    'brand': 'toyota'
                },
                'score': 80.0,
                'reasons': ['Econômico']
            }
        ]
        text = "Vou trabalhar como motorista de Uber e preciso economizar"
        
        # Act
        boosted = recommendation_engine._apply_text_boost(scored_cars, text)
        
        # Assert
        assert boosted[0]['score'] > 80.0  # Score aumentou
        assert any("trabalho com apps" in reason for reason in boosted[0]['reasons'])
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_economy_keywords_boost_efficient_cars(self, recommendation_engine):
        """
        Palavras de economia devem dar boost em carros eficientes
        """
        # Arrange
        scored_cars = [
            {
                'car': {'consumption': 13.5},
                'score': 75.0,
                'reasons': ['Bom carro']
            }
        ]
        text = "Preciso de máxima economia de combustível"
        
        # Act
        boosted = recommendation_engine._apply_text_boost(scored_cars, text)
        
        # Assert
        assert boosted[0]['score'] > 75.0
        assert any("economia de combustível" in reason for reason in boosted[0]['reasons'])
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_family_keywords_boost_family_cars(self, recommendation_engine):
        """
        Palavras de família devem dar boost em carros familiares
        """
        # Arrange
        scored_cars = [
            {
                'car': {
                    'category': 'sedan',
                    'brand': 'honda'
                },
                'score': 75.0,
                'reasons': ['Bom sedan']
            }
        ]
        text = "Vou usar para a família, tenho dois filhos pequenos"
        
        # Act
        boosted = recommendation_engine._apply_text_boost(scored_cars, text)
        
        # Assert
        assert boosted[0]['score'] > 75.0
        assert any("família" in reason for reason in boosted[0]['reasons'])


class TestCompleteRecommendationFlow:
    """
    TDD: Fluxo completo com critérios práticos
    User Story: "Quero recomendações baseadas em TODOS os critérios práticos"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_work_app_questionnaire_realistic_flow(self, recommendation_engine):
        """
        Fluxo completo para motorista de app
        """
        # Arrange - Respostas de motorista Uber
        answers = {
            "budget": "30k_50k",
            "main_purpose": "work_app",
            "frequency": "daily_work",
            "space_needs": "solo",
            "fuel_priority": "maximum_economy",
            "top_priority": "economy",
            "experience_level": "some_experience",
            "brand_preference": ["toyota", "chevrolet"]
        }
        
        cars_data = [
            {
                "id": 1, "brand": "toyota", "model": "etios",
                "price": 42000, "category": "hatch", "consumption": 14.5,
                "year": 2020, "seats": 5
            },
            {
                "id": 2, "brand": "bmw", "model": "x1",
                "price": 45000, "category": "suv", "consumption": 8.5,
                "year": 2020, "seats": 5
            }
        ]
        
        # Act
        recommendations = recommendation_engine.recommend(answers, cars_data)
        
        # Assert
        assert len(recommendations) > 0
        # Toyota Etios deve estar em primeiro (perfeito para Uber)
        best_rec = recommendations[0]
        assert best_rec['car']['brand'] == 'toyota'
        assert best_rec['score'] > 85  # Score muito alto
        assert any("econom" in reason.lower() for reason in best_rec['reasons'])
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_family_questionnaire_realistic_flow(self, recommendation_engine):
        """
        Fluxo completo para família
        """
        # Arrange - Respostas de família
        answers = {
            "budget": "80k_120k",
            "main_purpose": "family_daily",
            "frequency": "daily_personal",
            "space_needs": "small_family",
            "fuel_priority": "good_economy",
            "top_priority": "reliability",
            "experience_level": "experienced",
            "brand_preference": ["honda", "toyota"]
        }
        
        cars_data = [
            {
                "id": 1, "brand": "honda", "model": "civic",
                "price": 85000, "category": "sedan", "consumption": 11.5,
                "year": 2020, "seats": 5
            },
            {
                "id": 2, "brand": "chevrolet", "model": "onix",
                "price": 45000, "category": "hatch", "consumption": 14.2,
                "year": 2022, "seats": 5
            }
        ]
        
        # Act
        recommendations = recommendation_engine.recommend(answers, cars_data)
        
        # Assert
        assert len(recommendations) > 0
        # Honda Civic deve estar bem pontuado (boa para família)
        civic_rec = next(r for r in recommendations if r['car']['model'] == 'civic')
        assert civic_rec['score'] > 80
        assert any("família" in reason.lower() or "confia" in reason.lower() 
                  for reason in civic_rec['reasons'])


class TestReasonGeneration:
    """
    TDD: Geração de razões práticas e detalhadas
    User Story: "Quero entender POR QUE cada carro foi recomendado"
    """
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_generates_practical_reasons(self, recommendation_engine):
        """
        Deve gerar razões práticas baseadas nos critérios
        """
        # Arrange
        car = {
            "brand": "toyota",
            "consumption": 14.0,
            "category": "hatch",
            "price": 45000,
            "year": 2021
        }
        answers = {
            "main_purpose": "work_app",
            "top_priority": "reliability"
        }
        score = 90.0
        
        # Act
        reasons = recommendation_engine._generate_detailed_reasons(car, answers, score)
        
        # Assert
        assert len(reasons) <= 3  # Máximo 3 razões
        assert len(reasons) > 0   # Pelo menos 1 razão
        assert all(isinstance(reason, str) for reason in reasons)
        
        # Deve ter razões específicas
        reason_text = " ".join(reasons).lower()
        assert ("excelente compatibilidade" in reason_text or 
                "muito boa opção" in reason_text or
                "confiável" in reason_text or
                "econôm" in reason_text)
    
    @pytest.mark.unit
    @pytest.mark.user_story_2
    def test_reasons_match_car_strengths(self, recommendation_engine):
        """
        Razões devem corresponder aos pontos fortes do carro
        """
        # Arrange - Toyota muito confiável e econômico
        toyota_car = {
            "brand": "toyota",
            "consumption": 15.0,  # Muito econômico
            "year": 2021
        }
        answers = {"top_priority": "reliability"}
        score = 95.0
        
        # Act
        reasons = recommendation_engine._generate_detailed_reasons(toyota_car, answers, score)
        
        # Assert
        reason_text = " ".join(reasons).lower()
        # Deve mencionar confiabilidade E economia
        assert ("confiável" in reason_text or "durabilidade" in reason_text)
        assert ("econôm" in reason_text or "combustível" in reason_text)


class TestPerformanceAndEdgeCases:
    """
    TDD: Performance e casos extremos
    XP Principle: Test edge cases and performance
    """
    
    @pytest.mark.unit
    @pytest.mark.quick
    def test_empty_cars_list_returns_empty(self, recommendation_engine):
        """
        Lista vazia de carros deve retornar vazio
        """
        # Arrange
        answers = {"budget": "30k_50k"}
        empty_cars = []
        
        # Act
        recommendations = recommendation_engine.recommend(answers, empty_cars)
        
        # Assert
        assert recommendations == []
    
    @pytest.mark.unit
    @pytest.mark.quick
    def test_invalid_budget_filters_nothing(self, recommendation_engine):
        """
        Orçamento inválido não deve quebrar o sistema
        """
        # Arrange
        cars = [{"id": 1, "price": 40000}]
        invalid_budget = "invalid_range"
        
        # Act
        filtered = recommendation_engine._filter_by_budget(cars, invalid_budget)
        
        # Assert
        assert filtered == cars  # Retorna todos se orçamento inválido
    
    @pytest.mark.unit
    @pytest.mark.performance
    def test_recommendation_performance_large_dataset(self, recommendation_engine):
        """
        Sistema deve ser rápido mesmo com muitos carros
        """
        # Arrange - Dataset grande
        large_dataset = []
        for i in range(100):
            large_dataset.append({
                "id": i,
                "brand": "toyota",
                "model": f"model_{i}",
                "price": 40000 + (i * 1000),
                "category": "hatch",
                "consumption": 12.0 + (i * 0.1),
                "year": 2020,
                "seats": 5
            })
        
        answers = {
            "budget": "30k_50k",
            "main_purpose": "work_app"
        }
        
        # Act & Assert - Não deve demorar muito
        import time
        start = time.time()
        recommendations = recommendation_engine.recommend(answers, large_dataset)
        duration = time.time() - start
        
        assert duration < 1.0  # Menos de 1 segundo
        assert len(recommendations) <= 5  # Máximo 5 recomendações
    
    @pytest.mark.unit
    @pytest.mark.quick
    def test_missing_car_fields_handled_gracefully(self, recommendation_engine):
        """
        Campos ausentes no carro devem ser tratados sem erro
        """
        # Arrange - Carro com campos mínimos
        incomplete_car = {
            "id": 1,
            "brand": "toyota",
            "price": 40000
            # Faltam vários campos
        }
        answers = {"budget": "30k_50k", "main_purpose": "work_app"}
        
        # Act & Assert - Não deve lançar exceção
        try:
            score = recommendation_engine._calculate_comprehensive_score(incomplete_car, answers)
            assert isinstance(score, (int, float))
            assert 0 <= score <= 100
        except Exception as e:
            pytest.fail(f"Sistema não deveria quebrar com campos ausentes: {e}")


# Fixture para compatibilidade
@pytest.fixture
def recommendation_engine():
    """Fixture para engine de recomendação"""
    return CarRecommender()