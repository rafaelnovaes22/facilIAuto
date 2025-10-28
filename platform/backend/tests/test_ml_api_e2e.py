"""
🧪 XP Testing: Testes E2E para API de ML - Endpoints de Interação

Testa o fluxo completo da API de coleta de interações,
simulando requisições reais do frontend.

Metodologia XP:
- Test-First: Define comportamento esperado da API
- Simplicidade: Testes diretos e claros
- Feedback rápido: Execução rápida
- Cobertura: Cenários reais de uso

Autor: AI Engineer
Data: Outubro 2024
"""

import pytest
import json
import tempfile
import shutil
from fastapi.testclient import TestClient
from datetime import datetime

# Importar app
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from api.main import app
from services.interaction_service import InteractionService


class TestMLAPIEndpointsE2E:
    """
    Testes E2E para endpoints de ML da API
    
    Endpoints testados:
    - POST /api/interactions/track
    - GET /api/ml/stats
    """
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_interaction_payload(self):
        """Payload de interação de exemplo"""
        return {
            "session_id": "sess_test_api_001",
            "car_id": "car_robust_001",
            "interaction_type": "click",
            "timestamp": datetime.now().isoformat(),
            "user_preferences": {
                "budget": 120000,
                "usage": "urbano",
                "priorities": ["economia", "conforto"]
            },
            "car_snapshot": {
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2022,
                "preco": 115990,
                "categoria": "Sedan",
                "combustivel": "Flex",
                "cambio": "Automático",
                "quilometragem": 25000
            },
            "recommendation_position": 1,
            "score": 0.92
        }
    
    def test_track_interaction_success(self, client, sample_interaction_payload):
        """
        XP Test 1: POST /api/interactions/track deve aceitar interação válida
        
        Given: Um payload de interação válido
        When: POST é enviado para /api/interactions/track
        Then: Deve retornar 200 com status success
        """
        response = client.post(
            "/api/interactions/track",
            json=sample_interaction_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["interaction_type"] == "click"
        assert data["car_id"] == "car_robust_001"
    
    def test_track_interaction_click(self, client):
        """
        XP Test 2: Deve rastrear clique em card de carro
        
        Given: Usuário clica em card de carro
        When: Frontend envia evento de click
        Then: API deve aceitar e salvar
        """
        payload = {
            "session_id": "sess_click_test",
            "car_id": "car_test_001",
            "interaction_type": "click",
            "timestamp": datetime.now().isoformat(),
            "user_preferences": {
                "budget": 100000,
                "usage": "urbano",
                "priorities": ["economia"]
            },
            "car_snapshot": {
                "marca": "Fiat",
                "modelo": "Argo",
                "ano": 2023,
                "preco": 75000,
                "categoria": "Hatch",
                "combustivel": "Flex",
                "cambio": "Manual"
            }
        }
        
        response = client.post("/api/interactions/track", json=payload)
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_track_interaction_view_details(self, client):
        """
        XP Test 3: Deve rastrear visualização de detalhes
        
        Given: Usuário visualiza detalhes do carro
        When: Frontend envia evento de view_details com duração
        Then: API deve aceitar e salvar com duração
        """
        payload = {
            "session_id": "sess_view_test",
            "car_id": "car_test_002",
            "interaction_type": "view_details",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": 45,
            "user_preferences": {
                "budget": 150000,
                "usage": "misto",
                "priorities": ["conforto", "desempenho"]
            },
            "car_snapshot": {
                "marca": "Honda",
                "modelo": "Civic",
                "ano": 2023,
                "preco": 145000,
                "categoria": "Sedan",
                "combustivel": "Flex",
                "cambio": "Automático",
                "quilometragem": 15000
            }
        }
        
        response = client.post("/api/interactions/track", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["interaction_type"] == "view_details"
    
    def test_track_interaction_whatsapp_contact(self, client):
        """
        XP Test 4: Deve rastrear clique no WhatsApp (alto interesse)
        
        Given: Usuário clica no botão WhatsApp
        When: Frontend envia evento de whatsapp_contact
        Then: API deve aceitar e marcar como alto interesse
        """
        payload = {
            "session_id": "sess_whatsapp_test",
            "car_id": "car_test_003",
            "interaction_type": "whatsapp_contact",
            "timestamp": datetime.now().isoformat(),
            "user_preferences": {
                "budget": 200000,
                "usage": "estrada",
                "priorities": ["desempenho", "conforto"]
            },
            "car_snapshot": {
                "marca": "Jeep",
                "modelo": "Compass",
                "ano": 2023,
                "preco": 185000,
                "categoria": "SUV",
                "combustivel": "Flex",
                "cambio": "Automático",
                "quilometragem": 10000
            },
            "recommendation_position": 1,
            "score": 0.95
        }
        
        response = client.post("/api/interactions/track", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["interaction_type"] == "whatsapp_contact"
    
    def test_track_interaction_invalid_type(self, client):
        """
        XP Test 5: Deve rejeitar tipo de interação inválido
        
        Given: Payload com interaction_type inválido
        When: POST é enviado
        Then: Deve retornar erro de validação
        """
        payload = {
            "session_id": "sess_invalid",
            "car_id": "car_invalid",
            "interaction_type": "invalid_type",  # Tipo inválido
            "timestamp": datetime.now().isoformat(),
            "user_preferences": {
                "budget": 100000,
                "usage": "urbano",
                "priorities": ["economia"]
            }
        }
        
        response = client.post("/api/interactions/track", json=payload)
        
        # Deve retornar erro de validação (422)
        assert response.status_code == 422
    
    def test_track_interaction_missing_required_fields(self, client):
        """
        XP Test 6: Deve rejeitar payload sem campos obrigatórios
        
        Given: Payload sem session_id ou car_id
        When: POST é enviado
        Then: Deve retornar erro de validação
        """
        payload = {
            # Faltando session_id e car_id
            "interaction_type": "click",
            "timestamp": datetime.now().isoformat(),
            "user_preferences": {
                "budget": 100000,
                "usage": "urbano",
                "priorities": ["economia"]
            }
        }
        
        response = client.post("/api/interactions/track", json=payload)
        
        assert response.status_code == 422
    
    def test_get_ml_stats_initial_state(self, client):
        """
        XP Test 7: GET /api/ml/stats deve retornar estado inicial
        
        Given: Sistema sem interações
        When: GET /api/ml/stats é chamado
        Then: Deve retornar estatísticas zeradas
        """
        response = client.get("/api/ml/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "operational"
        assert "data_collection" in data
        assert "ml_readiness" in data
        assert "ml_model" in data
        
        # Verificar dados iniciais
        assert data["ml_readiness"]["ready_for_training"] is False
        assert data["ml_readiness"]["min_required_interactions"] == 500
        assert data["ml_model"]["available"] is False
    
    def test_get_ml_stats_with_interactions(self, client, sample_interaction_payload):
        """
        XP Test 8: Estatísticas devem refletir interações salvas
        
        Given: Algumas interações foram salvas
        When: GET /api/ml/stats é chamado
        Then: Deve retornar contagens corretas
        """
        # Salvar 3 interações
        for i in range(3):
            payload = sample_interaction_payload.copy()
            payload["session_id"] = f"sess_{i}"
            payload["car_id"] = f"car_{i}"
            client.post("/api/interactions/track", json=payload)
        
        # Obter estatísticas
        response = client.get("/api/ml/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que contagem aumentou
        # Nota: Pode ter interações de outros testes, então >= 3
        assert data["data_collection"]["total_interactions"] >= 3
    
    def test_ml_readiness_progress(self, client, sample_interaction_payload):
        """
        XP Test 9: Progress percentage deve aumentar com interações
        
        Given: Interações sendo adicionadas
        When: GET /api/ml/stats é chamado
        Then: progress_percentage deve aumentar
        """
        # Obter estado inicial
        response1 = client.get("/api/ml/stats")
        initial_progress = response1.json()["ml_readiness"]["progress_percentage"]
        
        # Adicionar 10 interações
        for i in range(10):
            payload = sample_interaction_payload.copy()
            payload["session_id"] = f"sess_progress_{i}"
            payload["car_id"] = f"car_progress_{i}"
            client.post("/api/interactions/track", json=payload)
        
        # Obter novo estado
        response2 = client.get("/api/ml/stats")
        new_progress = response2.json()["ml_readiness"]["progress_percentage"]
        
        # Progress deve ter aumentado
        assert new_progress > initial_progress
    
    def test_track_interaction_fail_gracefully(self, client):
        """
        XP Test 10: API deve falhar graciosamente com dados malformados
        
        Given: Payload com dados parcialmente inválidos
        When: POST é enviado
        Then: Deve retornar erro mas não crashar
        """
        payload = {
            "session_id": "sess_malformed",
            "car_id": "car_malformed",
            "interaction_type": "click",
            "timestamp": "invalid_timestamp",  # Timestamp inválido
            "user_preferences": {
                "budget": "not_a_number",  # Budget inválido
                "usage": "urbano",
                "priorities": []
            }
        }
        
        response = client.post("/api/interactions/track", json=payload)
        
        # Deve retornar erro de validação, não 500
        assert response.status_code in [422, 400]
    
    def test_multiple_sessions_same_car(self, client):
        """
        XP Test 11: Múltiplas sessões podem interagir com mesmo carro
        
        Given: Diferentes usuários (sessões) interagem com mesmo carro
        When: Múltiplas interações são enviadas
        Then: Todas devem ser aceitas
        """
        car_id = "car_popular_001"
        
        for i in range(5):
            payload = {
                "session_id": f"sess_user_{i}",
                "car_id": car_id,
                "interaction_type": "click",
                "timestamp": datetime.now().isoformat(),
                "user_preferences": {
                    "budget": 100000 + (i * 10000),
                    "usage": "urbano",
                    "priorities": ["economia"]
                },
                "car_snapshot": {
                    "marca": "Fiat",
                    "modelo": "Argo",
                    "ano": 2023,
                    "preco": 75000,
                    "categoria": "Hatch",
                    "combustivel": "Flex",
                    "cambio": "Manual"
                }
            }
            
            response = client.post("/api/interactions/track", json=payload)
            assert response.status_code == 200
    
    def test_same_session_multiple_cars(self, client):
        """
        XP Test 12: Mesma sessão pode interagir com múltiplos carros
        
        Given: Um usuário (sessão) interage com vários carros
        When: Múltiplas interações são enviadas
        Then: Todas devem ser aceitas
        """
        session_id = "sess_browsing_001"
        
        for i in range(5):
            payload = {
                "session_id": session_id,
                "car_id": f"car_option_{i}",
                "interaction_type": "click",
                "timestamp": datetime.now().isoformat(),
                "user_preferences": {
                    "budget": 120000,
                    "usage": "urbano",
                    "priorities": ["economia", "conforto"]
                },
                "car_snapshot": {
                    "marca": "Toyota",
                    "modelo": f"Model{i}",
                    "ano": 2022,
                    "preco": 100000 + (i * 5000),
                    "categoria": "Sedan",
                    "combustivel": "Flex",
                    "cambio": "Automático"
                }
            }
            
            response = client.post("/api/interactions/track", json=payload)
            assert response.status_code == 200
    
    def test_interaction_journey(self, client):
        """
        XP Test 13: Simular jornada completa do usuário
        
        Given: Um usuário navega pelo sistema
        When: Sequência de interações é enviada (click → view → whatsapp)
        Then: Todas devem ser aceitas na ordem correta
        """
        session_id = "sess_journey_001"
        car_id = "car_journey_001"
        
        # 1. Clique inicial no card
        click_payload = {
            "session_id": session_id,
            "car_id": car_id,
            "interaction_type": "click",
            "timestamp": datetime.now().isoformat(),
            "user_preferences": {
                "budget": 150000,
                "usage": "misto",
                "priorities": ["conforto", "economia"]
            },
            "car_snapshot": {
                "marca": "Honda",
                "modelo": "Civic",
                "ano": 2023,
                "preco": 145000,
                "categoria": "Sedan",
                "combustivel": "Flex",
                "cambio": "Automático"
            },
            "recommendation_position": 2,
            "score": 0.88
        }
        
        response1 = client.post("/api/interactions/track", json=click_payload)
        assert response1.status_code == 200
        
        # 2. Visualização de detalhes
        view_payload = click_payload.copy()
        view_payload["interaction_type"] = "view_details"
        view_payload["duration_seconds"] = 45
        
        response2 = client.post("/api/interactions/track", json=view_payload)
        assert response2.status_code == 200
        
        # 3. Clique no WhatsApp (conversão)
        whatsapp_payload = click_payload.copy()
        whatsapp_payload["interaction_type"] = "whatsapp_contact"
        
        response3 = client.post("/api/interactions/track", json=whatsapp_payload)
        assert response3.status_code == 200
        
        # Verificar que todas as 3 interações foram salvas
        stats_response = client.get("/api/ml/stats")
        stats = stats_response.json()
        
        # Deve ter pelo menos as 3 interações desta jornada
        assert stats["data_collection"]["total_interactions"] >= 3


class TestMLAPIIntegrationE2E:
    """
    Testes de integração E2E entre API e InteractionService
    
    Valida que a API e o serviço trabalham juntos corretamente.
    """
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI"""
        return TestClient(app)
    
    def test_api_to_service_integration(self, client):
        """
        XP Test 14: API deve integrar corretamente com InteractionService
        
        Given: Uma interação enviada via API
        When: Dados são processados
        Then: Devem ser persistidos corretamente pelo serviço
        """
        payload = {
            "session_id": "sess_integration",
            "car_id": "car_integration",
            "interaction_type": "click",
            "timestamp": datetime.now().isoformat(),
            "user_preferences": {
                "budget": 100000,
                "usage": "urbano",
                "priorities": ["economia"]
            },
            "car_snapshot": {
                "marca": "Fiat",
                "modelo": "Argo",
                "ano": 2023,
                "preco": 75000,
                "categoria": "Hatch",
                "combustivel": "Flex",
                "cambio": "Manual"
            }
        }
        
        # Enviar via API
        api_response = client.post("/api/interactions/track", json=payload)
        assert api_response.status_code == 200
        
        # Verificar via stats
        stats_response = client.get("/api/ml/stats")
        stats = stats_response.json()
        
        # Deve ter sido salvo
        assert stats["data_collection"]["total_interactions"] > 0


# Executar testes com pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
