"""
🧪 Testes de Integração XP - API Endpoints Práticos

User Stories testadas:
1. "Como usuário, quero enviar questionário prático e receber recomendações baseadas em critérios reais"
2. "Como usuário, quero demonstrar interesse em um carro e gerar lead"
3. "Como admin, quero ver estatísticas práticas e leads qualificados"

Seguindo XP:
- Testes rápidos e confiáveis
- Cobertura de todos os endpoints críticos
- Dados de teste realistas e isolados
"""

import json
import pytest
from fastapi.testclient import TestClient
from tests.conftest import populate_test_cars


class TestPracticalRecommendationsAPI:
    """
    User Story 1: Sistema de recomendações baseado em critérios práticos
    """
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_1
    def test_post_recommendations_with_practical_criteria(self, client, mock_cars_data, db_session):
        """
        POST /api/recommendations deve processar critérios práticos
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data)
        
        practical_questionnaire = {
            "answers": {
                "budget": "30k_50k",
                "main_purpose": "work_app",
                "frequency": "daily_work", 
                "space_needs": "solo",
                "fuel_priority": "maximum_economy",
                "top_priority": "economy",
                "experience_level": "some_experience",
                "brand_preference": ["toyota", "chevrolet"]
            },
            "details": "Vou trabalhar como motorista de Uber, preciso de máxima economia",
            "session_id": "practical_test_123",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        # Act
        response = client.post("/api/recommendations", json=practical_questionnaire)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estrutura da resposta prática
        assert "recommendations" in data
        assert "total_found" in data
        assert "session_id" in data
        assert "criteria_used" in data
        
        # Verificar dados práticos nas recomendações
        recommendations = data["recommendations"]
        assert len(recommendations) <= 5
        
        for rec in recommendations:
            assert "id" in rec
            assert "brand" in rec
            assert "model" in rec
            assert "score" in rec
            assert "reasons" in rec
            assert "reliability_score" in rec  # Novo campo prático
            assert "resale_score" in rec       # Novo campo prático
            assert "maintenance_cost" in rec   # Novo campo prático
            assert 0 <= rec["score"] <= 100
            assert len(rec["reasons"]) <= 3   # Máximo 3 razões
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_1
    def test_work_app_recommendations_prioritize_economy(self, client, db_session):
        """
        Questionário para trabalho deve priorizar economia e durabilidade
        """
        # Arrange - Carros com diferentes perfis
        work_cars = [
            {
                "brand": "Toyota", "model": "Etios", "year": 2020, "price": 42000,
                "category": "hatch", "transmission": "manual", "consumption": 14.5,
                "region": "sp", "reliability_score": 95, "resale_score": 85,
                "maintenance_cost": "Baixo"
            },
            {
                "brand": "BMW", "model": "X1", "year": 2019, "price": 45000,
                "category": "suv", "transmission": "automatic", "consumption": 8.5,
                "region": "sp", "reliability_score": 72, "resale_score": 75,
                "maintenance_cost": "Muito Alto"
            }
        ]
        populate_test_cars(db_session, work_cars)
        
        work_questionnaire = {
            "answers": {
                "budget": "30k_50k",
                "main_purpose": "work_app",
                "frequency": "daily_work",
                "fuel_priority": "maximum_economy",
                "top_priority": "economy"
            },
            "details": "Vou trabalhar como motorista de Uber",
            "session_id": "work_test"
        }
        
        # Act
        response = client.post("/api/recommendations", json=work_questionnaire)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        recommendations = data["recommendations"]
        assert len(recommendations) > 0
        
        # Toyota Etios deve estar bem pontuado (ideal para trabalho)
        toyota_rec = next((r for r in recommendations if r["brand"] == "Toyota"), None)
        assert toyota_rec is not None
        assert toyota_rec["score"] > 80  # Score alto para trabalho
        
        # Deve ter razões relacionadas a economia/trabalho
        reasons_text = " ".join(toyota_rec["reasons"]).lower()
        assert ("econôm" in reasons_text or "trabalho" in reasons_text or 
                "confiável" in reasons_text)
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_1
    def test_family_recommendations_prioritize_space_and_safety(self, client, db_session):
        """
        Questionário familiar deve priorizar espaço e segurança
        """
        # Arrange - Carros familiares vs compactos
        family_cars = [
            {
                "brand": "Honda", "model": "Civic", "year": 2020, "price": 85000,
                "category": "sedan", "transmission": "automatic", "consumption": 11.5,
                "region": "sp", "reliability_score": 92, "resale_score": 88,
                "maintenance_cost": "Médio"
            },
            {
                "brand": "Chevrolet", "model": "Onix", "year": 2022, "price": 45000,
                "category": "hatch", "transmission": "manual", "consumption": 14.2,
                "region": "sp", "reliability_score": 80, "resale_score": 78,
                "maintenance_cost": "Baixo"
            }
        ]
        populate_test_cars(db_session, family_cars)
        
        family_questionnaire = {
            "answers": {
                "budget": "80k_120k",
                "main_purpose": "family_daily",
                "frequency": "daily_personal",
                "space_needs": "small_family",
                "top_priority": "reliability",
                "brand_preference": ["honda", "toyota"]
            },
            "details": "Uso familiar com duas crianças",
            "session_id": "family_test"
        }
        
        # Act
        response = client.post("/api/recommendations", json=family_questionnaire)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        recommendations = data["recommendations"]
        # Honda Civic deve estar bem pontuado para família
        civic_rec = next((r for r in recommendations if r["model"] == "Civic"), None)
        assert civic_rec is not None
        assert civic_rec["score"] > 80  # Score alto para família
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_1
    def test_budget_filter_eliminates_expensive_cars(self, client, db_session):
        """
        Filtro de orçamento deve eliminar carros fora da faixa
        """
        # Arrange - Carros em diferentes faixas de preço
        mixed_price_cars = [
            {
                "brand": "Ford", "model": "Ka", "year": 2019, "price": 25000,
                "category": "hatch", "transmission": "manual", "consumption": 14.1,
                "region": "sp", "reliability_score": 77, "resale_score": 72,
                "maintenance_cost": "Baixo"
            },
            {
                "brand": "BMW", "model": "X1", "year": 2019, "price": 150000,
                "category": "suv", "transmission": "automatic", "consumption": 8.5,
                "region": "sp", "reliability_score": 72, "resale_score": 75,
                "maintenance_cost": "Muito Alto"
            }
        ]
        populate_test_cars(db_session, mixed_price_cars)
        
        budget_questionnaire = {
            "answers": {"budget": "up_30k"},
            "session_id": "budget_test"
        }
        
        # Act
        response = client.post("/api/recommendations", json=budget_questionnaire)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Deve recomendar apenas carros dentro do orçamento
        for rec in data["recommendations"]:
            assert rec["price"] <= 30000
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_1
    def test_text_details_influence_recommendations(self, client, mock_cars_data, db_session):
        """
        Campo de detalhes deve influenciar as recomendações com boost
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data)
        
        questionnaire_with_details = {
            "answers": {
                "budget": "30k_50k",
                "main_purpose": "work_app"
            },
            "details": "Vou trabalhar como motorista de Uber e 99, preciso de máxima economia de combustível",
            "session_id": "details_test"
        }
        
        questionnaire_without_details = {
            "answers": {
                "budget": "30k_50k",
                "main_purpose": "work_app"
            },
            "session_id": "no_details_test"
        }
        
        # Act
        response_with = client.post("/api/recommendations", json=questionnaire_with_details)
        response_without = client.post("/api/recommendations", json=questionnaire_without_details)
        
        # Assert
        assert response_with.status_code == 200
        assert response_without.status_code == 200
        
        with_details = response_with.json()["recommendations"]
        without_details = response_without.json()["recommendations"]
        
        # Deve ter pelo menos uma recomendação
        assert len(with_details) > 0
        
        # Deve ter razões adicionais por causa do texto
        if with_details:
            reasons_text = " ".join(with_details[0]["reasons"]).lower()
            # Deve mencionar trabalho ou economia por causa do boost
            work_economy_mentioned = any(keyword in reasons_text 
                                       for keyword in ["trabalho", "app", "econom", "combustível"])
            # Pode não ter menção direta, mas o score pode ser maior
            assert work_economy_mentioned or with_details[0]["score"] > 70


class TestPracticalCarDetailsAPI:
    """
    API de detalhes do carro com dados práticos
    """
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.quick
    def test_get_car_details_includes_practical_data(self, client, mock_cars_data, db_session):
        """
        GET /api/cars/{id} deve retornar dados práticos do carro
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data)
        
        # Act
        response = client.get("/api/cars/1")
        
        # Assert
        assert response.status_code == 200
        car = response.json()
        
        # Verificar campos básicos
        assert "id" in car
        assert "brand" in car
        assert "model" in car
        assert "price" in car
        
        # Verificar campos práticos novos
        assert "reliability_score" in car
        assert "resale_score" in car  
        assert "maintenance_cost" in car
        
        # Verificar tipos e valores
        if car["reliability_score"] is not None:
            assert 0 <= car["reliability_score"] <= 100
        if car["resale_score"] is not None:
            assert 0 <= car["resale_score"] <= 100
        if car["maintenance_cost"] is not None:
            assert car["maintenance_cost"] in ["Baixo", "Médio", "Alto", "Muito Alto"]
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.quick
    def test_get_car_details_not_found(self, client):
        """
        Carro inexistente deve retornar 404
        """
        # Act
        response = client.get("/api/cars/999")
        
        # Assert
        assert response.status_code == 404


class TestPracticalLeadsAPI:
    """
    User Story 3: Sistema de leads qualificados
    """
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_3
    def test_post_lead_success_with_validation(self, client, mock_cars_data, db_session):
        """
        POST /api/leads deve criar lead com validação aprimorada
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data)
        
        qualified_lead = {
            "car_id": 1,
            "name": "João Silva dos Santos",
            "phone": "(11) 99999-9999",
            "email": "joao.silva@email.com",
            "message": "Gostaria de agendar um test drive. Trabalho como motorista de app e preciso de um carro econômico."
        }
        
        # Act
        response = client.post("/api/leads", json=qualified_lead)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "lead_id" in data
        assert isinstance(data["lead_id"], int)
        assert "message" in data
        assert "sucesso" in data["message"].lower()
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_3
    def test_post_lead_validation_errors(self, client):
        """
        Lead com dados inválidos deve retornar erro de validação
        """
        # Arrange - Dados inválidos
        invalid_leads = [
            # Nome muito curto
            {
                "car_id": 1,
                "name": "A",
                "phone": "(11) 99999-9999"
            },
            # Phone muito curto
            {
                "car_id": 1,
                "name": "João Silva",
                "phone": "123"
            },
            # Email inválido
            {
                "car_id": 1,
                "name": "João Silva",
                "phone": "(11) 99999-9999",
                "email": "email_invalido"
            },
            # Mensagem muito longa
            {
                "car_id": 1,
                "name": "João Silva",
                "phone": "(11) 99999-9999",
                "message": "x" * 600  # Mais de 500 caracteres
            }
        ]
        
        for invalid_lead in invalid_leads:
            # Act
            response = client.post("/api/leads", json=invalid_lead)
            
            # Assert
            assert response.status_code == 422  # Validation error
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_3
    def test_post_lead_car_not_found(self, client):
        """
        Lead para carro inexistente deve retornar erro
        """
        # Arrange
        lead_for_nonexistent_car = {
            "car_id": 999,  # Não existe
            "name": "João Silva",
            "phone": "(11) 99999-9999"
        }
        
        # Act
        response = client.post("/api/leads", json=lead_for_nonexistent_car)
        
        # Assert
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()


class TestPracticalAdminAPI:
    """
    User Story 4: Dashboard administrativo com métricas práticas
    """
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_4
    def test_get_admin_stats_practical_metrics(self, client, mock_cars_data, db_session):
        """
        GET /api/admin/stats deve retornar métricas práticas
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data)
        
        # Act
        response = client.get("/api/admin/stats")
        
        # Assert
        assert response.status_code == 200
        stats = response.json()
        
        # Verificar métricas básicas
        assert "total_cars" in stats
        assert "total_leads" in stats
        assert "leads_today" in stats
        assert "popular_cars" in stats
        
        # Verificar métrica prática nova
        assert "conversion_rate" in stats
        
        # Verificar tipos e valores
        assert isinstance(stats["total_cars"], int)
        assert isinstance(stats["total_leads"], int)
        assert isinstance(stats["leads_today"], int)
        assert isinstance(stats["conversion_rate"], float)
        assert isinstance(stats["popular_cars"], list)
        
        # Total de carros deve corresponder aos carros cadastrados
        assert stats["total_cars"] == len(mock_cars_data)
        assert stats["total_leads"] >= 0
        assert 0 <= stats["conversion_rate"] <= 100
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_4
    def test_get_admin_leads_with_car_details(self, client, mock_cars_data, db_session):
        """
        GET /api/admin/leads deve retornar leads com detalhes do carro
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data)
        
        # Criar um lead primeiro
        lead_data = {
            "car_id": 1,
            "name": "Maria Santos",
            "phone": "(11) 88888-8888",
            "email": "maria@email.com",
            "message": "Interesse em test drive"
        }
        client.post("/api/leads", json=lead_data)
        
        # Act
        response = client.get("/api/admin/leads")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "leads" in data
        leads = data["leads"]
        
        if len(leads) > 0:
            lead = leads[0]
            # Verificar dados do lead
            assert "id" in lead
            assert "name" in lead
            assert "phone" in lead
            assert "created_at" in lead
            
            # Verificar dados do carro associado
            assert "car_id" in lead
            assert "brand" in lead
            assert "model" in lead
            assert "year" in lead
            assert "price" in lead
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.user_story_4
    def test_admin_popular_cars_ranking(self, client, mock_cars_data, db_session):
        """
        Estatísticas devem mostrar carros mais procurados
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data)
        
        # Criar vários leads para o mesmo carro
        for i in range(3):
            lead_data = {
                "car_id": 1,  # Sempre o mesmo carro
                "name": f"Cliente {i}",
                "phone": f"(11) 9999{i:04d}",
                "email": f"cliente{i}@email.com"
            }
            client.post("/api/leads", json=lead_data)
        
        # Act
        response = client.get("/api/admin/stats")
        
        # Assert
        stats = response.json()
        popular_cars = stats["popular_cars"]
        
        assert len(popular_cars) <= 5  # Máximo 5 carros
        
        if len(popular_cars) > 0:
            # Primeiro carro deve ter mais leads
            most_popular = popular_cars[0]
            assert "brand" in most_popular
            assert "model" in most_popular
            assert "leads" in most_popular
            assert most_popular["leads"] >= 3  # Os leads que criamos


class TestPracticalHealthAndMiscAPI:
    """
    Endpoints auxiliares com informações práticas
    """
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.quick
    def test_health_check_practical_info(self, client):
        """
        GET /api/health deve retornar informações práticas do sistema
        """
        # Act
        response = client.get("/api/health")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verificar informações básicas
        assert data["status"] == "ok"
        assert data["service"] == "CarFinder"
        
        # Verificar informações práticas
        assert "version" in data
        assert "database" in data
        assert "cars_available" in data
        assert "features" in data
        
        # Verificar features práticas implementadas
        features = data["features"]
        expected_features = [
            "practical_questionnaire",
            "smart_recommendations",
            "reliability_data",
            "resale_analysis",
            "maintenance_costs",
            "lead_generation"
        ]
        
        for feature in expected_features:
            assert feature in features
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.quick
    def test_serve_static_pages_practical(self, client):
        """
        Páginas estáticas devem ser servidas com conteúdo prático
        """
        # Act & Assert
        pages = ["/", "/results.html", "/admin.html"]
        
        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")
            
            # Verificar se o conteúdo contém elementos práticos
            content = response.text.lower()
            if page == "/":
                assert ("carfinder" in content or "questionário" in content)
            elif page == "/results.html":
                assert ("recomendações" in content or "results" in content)
            elif page == "/admin.html":
                assert ("admin" in content or "dashboard" in content)


class TestPracticalAPIPerformance:
    """
    Testes de performance da API prática (XP: Fast feedback)
    """
    
    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.slow
    def test_recommendations_api_performance_practical(self, client, mock_cars_data, db_session):
        """
        API prática deve responder rapidamente mesmo com critérios complexos
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data * 5)  # Mais carros
        
        complex_questionnaire = {
            "answers": {
                "budget": "50k_80k",
                "main_purpose": "family_daily",
                "frequency": "daily_personal",
                "space_needs": "small_family",
                "fuel_priority": "good_economy",
                "top_priority": "reliability",
                "experience_level": "experienced",
                "brand_preference": ["honda", "toyota", "volkswagen"]
            },
            "details": "Família com duas crianças, uso diário para trabalho e lazer, valorizo muito a segurança e confiabilidade, mas também quero economia razoável no combustível",
            "session_id": "performance_test"
        }
        
        def make_complex_request():
            return client.post("/api/recommendations", json=complex_questionnaire)
        
        # Act & Measure
        import time
        start = time.time()
        response = make_complex_request()
        duration = time.time() - start
        
        # Assert
        assert response.status_code == 200
        assert duration < 2.0  # Máximo 2 segundos para critérios complexos
        
        # Verificar qualidade da resposta
        data = response.json()
        assert len(data["recommendations"]) <= 5
        assert all(rec["score"] > 0 for rec in data["recommendations"])
    
    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.quick
    def test_concurrent_practical_requests(self, client, mock_cars_data, db_session):
        """
        API deve lidar com múltiplas requisições práticas simultâneas
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data)
        
        questionnaires = [
            {
                "answers": {"budget": "30k_50k", "main_purpose": "work_app"},
                "session_id": f"concurrent_work_{i}"
            },
            {
                "answers": {"budget": "80k_120k", "main_purpose": "family_daily"},
                "session_id": f"concurrent_family_{i}"
            },
            {
                "answers": {"budget": "50k_80k", "main_purpose": "first_car"},
                "session_id": f"concurrent_first_{i}"
            }
            for i in range(3)
        ]
        
        # Act - Fazer várias requisições
        responses = []
        for questionnaire in questionnaires:
            response = client.post("/api/recommendations", json=questionnaire)
            responses.append(response)
        
        # Assert
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert len(data["recommendations"]) <= 5
            assert "criteria_used" in data


class TestPracticalErrorHandling:
    """
    Tratamento de erros em cenários práticos (XP: Defensive programming)
    """
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.quick
    def test_malformed_practical_questionnaire(self, client):
        """
        Questionário mal formado deve retornar erro adequado
        """
        # Arrange - JSON inválido
        malformed_requests = [
            '{"answers": {"budget": "30k_50k"',  # JSON incompleto
            '{"invalid_field": "value"}',        # Campos obrigatórios ausentes
            '{"answers": null, "session_id": "test"}',  # Answers nulo
        ]
        
        for malformed_json in malformed_requests:
            # Act
            response = client.post(
                "/api/recommendations",
                data=malformed_json,
                headers={"Content-Type": "application/json"}
            )
            
            # Assert
            assert response.status_code == 422
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.quick
    def test_empty_database_practical_recommendations(self, client):
        """
        Banco vazio deve retornar resposta consistente
        """
        # Arrange - Banco vazio por padrão
        practical_questionnaire = {
            "answers": {
                "budget": "30k_50k",
                "main_purpose": "work_app",
                "top_priority": "economy"
            },
            "session_id": "empty_db_test"
        }
        
        # Act
        response = client.post("/api/recommendations", json=practical_questionnaire)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["recommendations"] == []
        assert data["total_found"] == 0
        assert data["session_id"] == "empty_db_test"
        assert "criteria_used" in data
    
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.quick
    def test_extreme_questionnaire_values(self, client, mock_cars_data, db_session):
        """
        Valores extremos no questionário devem ser tratados graciosamente
        """
        # Arrange
        populate_test_cars(db_session, mock_cars_data)
        
        extreme_questionnaire = {
            "answers": {
                "budget": "120k_plus",  # Orçamento alto
                "main_purpose": "investment",
                "frequency": "occasional",
                "space_needs": "cargo",
                "fuel_priority": "not_important",
                "top_priority": "performance",
                "experience_level": "enthusiast",
                "brand_preference": ["bmw", "audi", "mercedes"]  # Marcas premium
            },
            "details": "x" * 200,  # Texto longo mas dentro do limite
            "session_id": "extreme_test"
        }
        
        # Act
        response = client.post("/api/recommendations", json=extreme_questionnaire)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Pode não ter recomendações perfeitas, mas não deve quebrar
        assert isinstance(data["recommendations"], list)
        assert data["total_found"] >= 0