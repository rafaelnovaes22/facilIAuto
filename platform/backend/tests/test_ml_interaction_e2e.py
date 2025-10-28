"""
🧪 XP Testing: Testes E2E para Sistema de ML - Coleta de Interações

Metodologia XP (Extreme Programming):
- Test-First: Testes definem comportamento esperado
- Simplicidade: Testes claros e diretos
- Feedback rápido: Execução rápida
- Cobertura: Cenários reais de uso

Autor: AI Engineer
Data: Outubro 2024
"""

import pytest
import json
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from models.interaction import (
    InteractionEvent,
    InteractionType,
    UserPreferencesSnapshot,
    CarSnapshot,
    InteractionStats
)
from services.interaction_service import InteractionService


class TestInteractionServiceE2E:
    """
    Testes E2E para InteractionService
    
    Cenários testados:
    1. Criação e inicialização do serviço
    2. Salvamento de interações
    3. Recuperação de dados
    4. Cálculo de estatísticas
    5. Preparação para treinamento
    """
    
    @pytest.fixture
    def temp_data_dir(self):
        """Cria diretório temporário para testes"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def interaction_service(self, temp_data_dir):
        """Cria instância do serviço com diretório temporário"""
        return InteractionService(data_dir=temp_data_dir)
    
    @pytest.fixture
    def sample_user_preferences(self):
        """Preferências de usuário de exemplo"""
        return UserPreferencesSnapshot(
            budget=120000,
            usage="urbano",
            priorities=["economia", "conforto"]
        )
    
    @pytest.fixture
    def sample_car_snapshot(self):
        """Snapshot de carro de exemplo"""
        return CarSnapshot(
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            preco=115990,
            categoria="Sedan",
            combustivel="Flex",
            cambio="Automático",
            quilometragem=25000
        )
    
    def test_service_initialization(self, interaction_service, temp_data_dir):
        """
        XP Test 1: Serviço deve inicializar corretamente
        
        Given: Um diretório vazio
        When: InteractionService é inicializado
        Then: Arquivo JSON deve ser criado com estrutura correta
        """
        # Verificar que arquivo foi criado
        interactions_file = Path(temp_data_dir) / "user_interactions.json"
        assert interactions_file.exists(), "Arquivo de interações deve ser criado"
        
        # Verificar estrutura do arquivo
        with open(interactions_file, 'r') as f:
            data = json.load(f)
        
        assert "interactions" in data, "Deve ter campo 'interactions'"
        assert "metadata" in data, "Deve ter campo 'metadata'"
        assert data["interactions"] == [], "Lista de interações deve estar vazia"
        assert data["metadata"]["total_count"] == 0, "Contador deve ser zero"
    
    def test_save_single_interaction(
        self, 
        interaction_service, 
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 2: Deve salvar uma interação corretamente
        
        Given: Um evento de interação válido
        When: save_interaction() é chamado
        Then: Evento deve ser persistido com ID único
        """
        # Criar evento
        event = InteractionEvent(
            session_id="sess_test_001",
            car_id="car_test_001",
            interaction_type=InteractionType.CLICK,
            user_preferences=sample_user_preferences,
            car_snapshot=sample_car_snapshot,
            recommendation_position=1,
            score=0.92
        )
        
        # Salvar
        result = interaction_service.save_interaction(event)
        
        # Verificar resultado
        assert result is True, "Salvamento deve retornar True"
        
        # Verificar que foi salvo
        interactions = interaction_service.get_all_interactions()
        assert len(interactions) == 1, "Deve ter exatamente 1 interação"
        
        saved = interactions[0]
        assert saved["session_id"] == "sess_test_001"
        assert saved["car_id"] == "car_test_001"
        assert saved["interaction_type"] == "click"
        assert "id" in saved, "Deve ter ID único"
        assert saved["id"] == "int_000001", "Primeiro ID deve ser int_000001"
    
    def test_save_multiple_interactions(
        self,
        interaction_service,
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 3: Deve salvar múltiplas interações sequencialmente
        
        Given: Múltiplos eventos de interação
        When: save_interaction() é chamado várias vezes
        Then: Todos eventos devem ser persistidos com IDs únicos
        """
        interaction_types = [
            InteractionType.CLICK,
            InteractionType.VIEW_DETAILS,
            InteractionType.WHATSAPP_CONTACT
        ]
        
        # Salvar 3 interações
        for i, int_type in enumerate(interaction_types):
            event = InteractionEvent(
                session_id=f"sess_test_{i:03d}",
                car_id=f"car_test_{i:03d}",
                interaction_type=int_type,
                user_preferences=sample_user_preferences,
                car_snapshot=sample_car_snapshot
            )
            result = interaction_service.save_interaction(event)
            assert result is True, f"Salvamento {i+1} deve ter sucesso"
        
        # Verificar que todas foram salvas
        interactions = interaction_service.get_all_interactions()
        assert len(interactions) == 3, "Deve ter 3 interações"
        
        # Verificar IDs únicos
        ids = [i["id"] for i in interactions]
        assert len(set(ids)) == 3, "IDs devem ser únicos"
        assert ids == ["int_000001", "int_000002", "int_000003"]
    
    def test_get_interactions_count(self, interaction_service, sample_user_preferences, sample_car_snapshot):
        """
        XP Test 4: Deve contar interações corretamente
        
        Given: N interações salvas
        When: get_interactions_count() é chamado
        Then: Deve retornar N
        """
        # Inicialmente zero
        assert interaction_service.get_interactions_count() == 0
        
        # Adicionar 5 interações
        for i in range(5):
            event = InteractionEvent(
                session_id=f"sess_{i}",
                car_id=f"car_{i}",
                interaction_type=InteractionType.CLICK,
                user_preferences=sample_user_preferences,
                car_snapshot=sample_car_snapshot
            )
            interaction_service.save_interaction(event)
        
        # Verificar contagem
        assert interaction_service.get_interactions_count() == 5
    
    def test_calculate_statistics(
        self,
        interaction_service,
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 5: Deve calcular estatísticas corretamente
        
        Given: Interações de diferentes tipos
        When: get_stats() é chamado
        Then: Estatísticas devem refletir os dados corretamente
        """
        # Criar interações variadas
        interactions_data = [
            ("sess_1", "car_1", InteractionType.CLICK),
            ("sess_1", "car_2", InteractionType.CLICK),
            ("sess_1", "car_2", InteractionType.VIEW_DETAILS),
            ("sess_2", "car_3", InteractionType.CLICK),
            ("sess_2", "car_3", InteractionType.WHATSAPP_CONTACT),
        ]
        
        for session_id, car_id, int_type in interactions_data:
            event = InteractionEvent(
                session_id=session_id,
                car_id=car_id,
                interaction_type=int_type,
                user_preferences=sample_user_preferences,
                car_snapshot=sample_car_snapshot,
                duration_seconds=30 if int_type == InteractionType.VIEW_DETAILS else None
            )
            interaction_service.save_interaction(event)
        
        # Obter estatísticas
        stats = interaction_service.get_stats()
        
        # Verificar contagens
        assert stats.total_interactions == 5
        assert stats.click_count == 3
        assert stats.view_details_count == 1
        assert stats.whatsapp_contact_count == 1
        
        # Verificar únicos
        assert stats.unique_sessions == 2  # sess_1 e sess_2
        assert stats.unique_cars == 3  # car_1, car_2, car_3
        
        # Verificar duração média
        assert stats.avg_duration_seconds == 30.0  # Apenas 1 com duração
    
    def test_get_interactions_by_session(
        self,
        interaction_service,
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 6: Deve filtrar interações por sessão
        
        Given: Interações de múltiplas sessões
        When: get_interactions_by_session() é chamado
        Then: Deve retornar apenas interações da sessão especificada
        """
        # Criar interações de 2 sessões
        for session_num in [1, 2]:
            for car_num in range(3):
                event = InteractionEvent(
                    session_id=f"sess_{session_num}",
                    car_id=f"car_{car_num}",
                    interaction_type=InteractionType.CLICK,
                    user_preferences=sample_user_preferences,
                    car_snapshot=sample_car_snapshot
                )
                interaction_service.save_interaction(event)
        
        # Filtrar por sessão 1
        sess1_interactions = interaction_service.get_interactions_by_session("sess_1")
        assert len(sess1_interactions) == 3
        assert all(i["session_id"] == "sess_1" for i in sess1_interactions)
        
        # Filtrar por sessão 2
        sess2_interactions = interaction_service.get_interactions_by_session("sess_2")
        assert len(sess2_interactions) == 3
        assert all(i["session_id"] == "sess_2" for i in sess2_interactions)
    
    def test_get_interactions_by_car(
        self,
        interaction_service,
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 7: Deve filtrar interações por carro
        
        Given: Interações com múltiplos carros
        When: get_interactions_by_car() é chamado
        Then: Deve retornar apenas interações do carro especificado
        """
        # Criar interações com 3 carros
        for car_num in range(3):
            for session_num in range(2):
                event = InteractionEvent(
                    session_id=f"sess_{session_num}",
                    car_id=f"car_{car_num}",
                    interaction_type=InteractionType.CLICK,
                    user_preferences=sample_user_preferences,
                    car_snapshot=sample_car_snapshot
                )
                interaction_service.save_interaction(event)
        
        # Filtrar por car_1
        car1_interactions = interaction_service.get_interactions_by_car("car_1")
        assert len(car1_interactions) == 2
        assert all(i["car_id"] == "car_1" for i in car1_interactions)
    
    def test_get_interactions_for_training_insufficient_data(
        self,
        interaction_service,
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 8: Não deve retornar dados se insuficientes para treinamento
        
        Given: Menos de 500 interações
        When: get_interactions_for_training() é chamado
        Then: Deve retornar None
        """
        # Adicionar apenas 100 interações
        for i in range(100):
            event = InteractionEvent(
                session_id=f"sess_{i}",
                car_id=f"car_{i % 10}",
                interaction_type=InteractionType.CLICK,
                user_preferences=sample_user_preferences,
                car_snapshot=sample_car_snapshot
            )
            interaction_service.save_interaction(event)
        
        # Tentar obter dados para treinamento
        training_data = interaction_service.get_interactions_for_training(min_count=500)
        assert training_data is None, "Não deve retornar dados com menos de 500 interações"
    
    def test_get_interactions_for_training_sufficient_data(
        self,
        interaction_service,
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 9: Deve retornar dados se suficientes para treinamento
        
        Given: 500+ interações
        When: get_interactions_for_training() é chamado
        Then: Deve retornar lista de interações
        """
        # Adicionar 550 interações
        for i in range(550):
            event = InteractionEvent(
                session_id=f"sess_{i % 100}",
                car_id=f"car_{i % 50}",
                interaction_type=InteractionType.CLICK,
                user_preferences=sample_user_preferences,
                car_snapshot=sample_car_snapshot
            )
            interaction_service.save_interaction(event)
        
        # Obter dados para treinamento
        training_data = interaction_service.get_interactions_for_training(min_count=500)
        assert training_data is not None, "Deve retornar dados com 500+ interações"
        assert len(training_data) == 550
    
    def test_interaction_with_duration(
        self,
        interaction_service,
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 10: Deve salvar e recuperar duração de visualização
        
        Given: Interação com duration_seconds
        When: Evento é salvo e recuperado
        Then: Duração deve ser preservada
        """
        event = InteractionEvent(
            session_id="sess_duration",
            car_id="car_duration",
            interaction_type=InteractionType.VIEW_DETAILS,
            user_preferences=sample_user_preferences,
            car_snapshot=sample_car_snapshot,
            duration_seconds=45
        )
        
        interaction_service.save_interaction(event)
        
        # Recuperar e verificar
        interactions = interaction_service.get_all_interactions()
        assert interactions[0]["duration_seconds"] == 45
    
    def test_interaction_with_position_and_score(
        self,
        interaction_service,
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 11: Deve salvar posição e score da recomendação
        
        Given: Interação com position e score
        When: Evento é salvo
        Then: Metadados devem ser preservados
        """
        event = InteractionEvent(
            session_id="sess_meta",
            car_id="car_meta",
            interaction_type=InteractionType.WHATSAPP_CONTACT,
            user_preferences=sample_user_preferences,
            car_snapshot=sample_car_snapshot,
            recommendation_position=1,
            score=0.95
        )
        
        interaction_service.save_interaction(event)
        
        # Recuperar e verificar
        interactions = interaction_service.get_all_interactions()
        assert interactions[0]["recommendation_position"] == 1
        assert interactions[0]["score"] == 0.95
    
    def test_empty_stats(self, interaction_service):
        """
        XP Test 12: Estatísticas vazias devem retornar valores padrão
        
        Given: Nenhuma interação salva
        When: get_stats() é chamado
        Then: Deve retornar InteractionStats com valores zero
        """
        stats = interaction_service.get_stats()
        
        assert stats.total_interactions == 0
        assert stats.click_count == 0
        assert stats.view_details_count == 0
        assert stats.whatsapp_contact_count == 0
        assert stats.unique_sessions == 0
        assert stats.unique_cars == 0
        assert stats.avg_duration_seconds is None
        assert stats.last_interaction is None
    
    def test_concurrent_saves(
        self,
        interaction_service,
        sample_user_preferences,
        sample_car_snapshot
    ):
        """
        XP Test 13: Deve lidar com salvamentos sequenciais rápidos
        
        Given: Múltiplos eventos salvos rapidamente
        When: save_interaction() é chamado em sequência
        Then: Todos devem ser salvos sem perda de dados
        """
        # Salvar 20 interações rapidamente
        for i in range(20):
            event = InteractionEvent(
                session_id=f"sess_{i}",
                car_id=f"car_{i}",
                interaction_type=InteractionType.CLICK,
                user_preferences=sample_user_preferences,
                car_snapshot=sample_car_snapshot
            )
            result = interaction_service.save_interaction(event)
            assert result is True
        
        # Verificar que todas foram salvas
        assert interaction_service.get_interactions_count() == 20
        interactions = interaction_service.get_all_interactions()
        assert len(interactions) == 20
        
        # Verificar IDs únicos
        ids = [i["id"] for i in interactions]
        assert len(set(ids)) == 20, "Todos IDs devem ser únicos"


class TestInteractionModelsE2E:
    """
    Testes E2E para modelos de interação
    
    Valida que os modelos Pydantic funcionam corretamente
    em cenários reais de uso.
    """
    
    def test_interaction_event_creation(self):
        """
        XP Test 14: Deve criar InteractionEvent com dados válidos
        
        Given: Dados válidos de interação
        When: InteractionEvent é instanciado
        Then: Objeto deve ser criado sem erros
        """
        event = InteractionEvent(
            session_id="sess_test",
            car_id="car_test",
            interaction_type=InteractionType.CLICK,
            user_preferences=UserPreferencesSnapshot(
                budget=100000,
                usage="urbano",
                priorities=["economia"]
            ),
            car_snapshot=CarSnapshot(
                marca="Fiat",
                modelo="Argo",
                ano=2023,
                preco=75000,
                categoria="Hatch",
                combustivel="Flex",
                cambio="Manual"
            )
        )
        
        assert event.session_id == "sess_test"
        assert event.car_id == "car_test"
        assert event.interaction_type == InteractionType.CLICK
        assert isinstance(event.timestamp, datetime)
    
    def test_interaction_event_serialization(self):
        """
        XP Test 15: Deve serializar InteractionEvent para dict
        
        Given: Um InteractionEvent válido
        When: .dict() é chamado
        Then: Deve retornar dicionário com todos os campos
        """
        event = InteractionEvent(
            session_id="sess_serial",
            car_id="car_serial",
            interaction_type=InteractionType.VIEW_DETAILS,
            user_preferences=UserPreferencesSnapshot(
                budget=120000,
                usage="misto",
                priorities=["conforto", "economia"]
            ),
            car_snapshot=CarSnapshot(
                marca="Toyota",
                modelo="Corolla",
                ano=2022,
                preco=115990,
                categoria="Sedan",
                combustivel="Flex",
                cambio="Automático",
                quilometragem=25000
            ),
            duration_seconds=45,
            recommendation_position=2,
            score=0.88
        )
        
        event_dict = event.dict()
        
        assert event_dict["session_id"] == "sess_serial"
        assert event_dict["car_id"] == "car_serial"
        assert event_dict["interaction_type"] == "view_details"
        assert event_dict["duration_seconds"] == 45
        assert event_dict["recommendation_position"] == 2
        assert event_dict["score"] == 0.88
        assert "user_preferences" in event_dict
        assert "car_snapshot" in event_dict


# Executar testes com pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
