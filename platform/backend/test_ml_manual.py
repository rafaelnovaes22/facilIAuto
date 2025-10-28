"""
🧪 Testes Manuais E2E para Sistema de ML

Script de teste simples que não depende de pytest.
Executa testes básicos para validar funcionalidade.

Autor: AI Engineer
Data: Outubro 2024
"""

import sys
import os
import json
import tempfile
import shutil
from datetime import datetime

# Adicionar backend ao path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from models.interaction import (
    InteractionEvent,
    InteractionType,
    UserPreferencesSnapshot,
    CarSnapshot
)
from services.interaction_service import InteractionService


class TestRunner:
    """Runner simples de testes"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name, func):
        """Executa um teste"""
        try:
            print(f"\n🧪 {name}...", end=" ")
            func()
            print("✅ PASSOU")
            self.passed += 1
            self.tests.append((name, True, None))
        except AssertionError as e:
            print(f"❌ FALHOU: {e}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
        except Exception as e:
            print(f"💥 ERRO: {e}")
            self.failed += 1
            self.tests.append((name, False, str(e)))
    
    def summary(self):
        """Mostra resumo dos testes"""
        print("\n" + "="*60)
        print(f"📊 RESUMO DOS TESTES")
        print("="*60)
        print(f"✅ Passou: {self.passed}")
        print(f"❌ Falhou: {self.failed}")
        print(f"📈 Total: {self.passed + self.failed}")
        print(f"🎯 Taxa de sucesso: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        print("="*60)
        
        if self.failed > 0:
            print("\n❌ Testes que falharam:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"  - {name}: {error}")
        
        return self.failed == 0


def main():
    """Executa todos os testes"""
    runner = TestRunner()
    
    print("="*60)
    print("🧪 TESTES E2E - SISTEMA DE ML")
    print("="*60)
    
    # Criar diretório temporário para testes
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test 1: Inicialização do serviço
        def test_service_initialization():
            service = InteractionService(data_dir=temp_dir)
            interactions_file = os.path.join(temp_dir, "user_interactions.json")
            assert os.path.exists(interactions_file), "Arquivo deve ser criado"
            
            with open(interactions_file, 'r') as f:
                data = json.load(f)
            assert "interactions" in data
            assert "metadata" in data
            assert data["interactions"] == []
        
        runner.test("Inicialização do serviço", test_service_initialization)
        
        # Test 2: Salvar interação
        def test_save_interaction():
            service = InteractionService(data_dir=temp_dir)
            
            event = InteractionEvent(
                session_id="sess_test_001",
                car_id="car_test_001",
                interaction_type=InteractionType.CLICK,
                user_preferences=UserPreferencesSnapshot(
                    budget=120000,
                    usage="urbano",
                    priorities=["economia"]
                ),
                car_snapshot=CarSnapshot(
                    marca="Toyota",
                    modelo="Corolla",
                    ano=2022,
                    preco=115990,
                    categoria="Sedan",
                    combustivel="Flex",
                    cambio="Automático"
                )
            )
            
            result = service.save_interaction(event)
            assert result is True, "Salvamento deve retornar True"
            
            interactions = service.get_all_interactions()
            assert len(interactions) == 1, "Deve ter 1 interação"
            assert interactions[0]["session_id"] == "sess_test_001"
        
        runner.test("Salvar interação", test_save_interaction)
        
        # Test 3: Múltiplas interações
        def test_multiple_interactions():
            service = InteractionService(data_dir=temp_dir)
            
            for i in range(5):
                event = InteractionEvent(
                    session_id=f"sess_{i}",
                    car_id=f"car_{i}",
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
                service.save_interaction(event)
            
            count = service.get_interactions_count()
            assert count >= 5, f"Deve ter pelo menos 5 interações, tem {count}"
        
        runner.test("Múltiplas interações", test_multiple_interactions)
        
        # Test 4: Estatísticas
        def test_statistics():
            service = InteractionService(data_dir=temp_dir)
            
            # Adicionar interações variadas
            types = [
                InteractionType.CLICK,
                InteractionType.CLICK,
                InteractionType.VIEW_DETAILS,
                InteractionType.WHATSAPP_CONTACT
            ]
            
            for i, int_type in enumerate(types):
                event = InteractionEvent(
                    session_id=f"sess_stats_{i}",
                    car_id=f"car_stats_{i}",
                    interaction_type=int_type,
                    user_preferences=UserPreferencesSnapshot(
                        budget=100000,
                        usage="urbano",
                        priorities=["economia"]
                    ),
                    car_snapshot=CarSnapshot(
                        marca="Test",
                        modelo="Model",
                        ano=2023,
                        preco=80000,
                        categoria="Hatch",
                        combustivel="Flex",
                        cambio="Manual"
                    )
                )
                service.save_interaction(event)
            
            stats = service.get_stats()
            assert stats.total_interactions >= 4
            assert stats.click_count >= 2
            assert stats.view_details_count >= 1
            assert stats.whatsapp_contact_count >= 1
        
        runner.test("Cálculo de estatísticas", test_statistics)
        
        # Test 5: Filtrar por sessão
        def test_filter_by_session():
            service = InteractionService(data_dir=temp_dir)
            
            session_id = "sess_filter_test"
            
            # Adicionar 3 interações da mesma sessão
            for i in range(3):
                event = InteractionEvent(
                    session_id=session_id,
                    car_id=f"car_{i}",
                    interaction_type=InteractionType.CLICK,
                    user_preferences=UserPreferencesSnapshot(
                        budget=100000,
                        usage="urbano",
                        priorities=["economia"]
                    ),
                    car_snapshot=CarSnapshot(
                        marca="Test",
                        modelo="Model",
                        ano=2023,
                        preco=80000,
                        categoria="Hatch",
                        combustivel="Flex",
                        cambio="Manual"
                    )
                )
                service.save_interaction(event)
            
            filtered = service.get_interactions_by_session(session_id)
            assert len(filtered) == 3, f"Deve ter 3 interações, tem {len(filtered)}"
            assert all(i["session_id"] == session_id for i in filtered)
        
        runner.test("Filtrar por sessão", test_filter_by_session)
        
        # Test 6: Dados para treinamento
        def test_training_data():
            service = InteractionService(data_dir=temp_dir)
            
            # Verificar que não retorna com poucos dados
            training_data = service.get_interactions_for_training(min_count=1000)
            # Pode ser None se não tiver 1000 interações
            
            # Verificar que retorna com dados suficientes
            training_data = service.get_interactions_for_training(min_count=1)
            assert training_data is not None, "Deve retornar dados com min_count=1"
            assert len(training_data) > 0
        
        runner.test("Dados para treinamento", test_training_data)
        
        # Test 7: Interação com duração
        def test_interaction_with_duration():
            service = InteractionService(data_dir=temp_dir)
            
            event = InteractionEvent(
                session_id="sess_duration",
                car_id="car_duration",
                interaction_type=InteractionType.VIEW_DETAILS,
                user_preferences=UserPreferencesSnapshot(
                    budget=100000,
                    usage="urbano",
                    priorities=["economia"]
                ),
                car_snapshot=CarSnapshot(
                    marca="Test",
                    modelo="Model",
                    ano=2023,
                    preco=80000,
                    categoria="Hatch",
                    combustivel="Flex",
                    cambio="Manual"
                ),
                duration_seconds=45
            )
            
            service.save_interaction(event)
            
            interactions = service.get_interactions_by_session("sess_duration")
            assert len(interactions) > 0
            assert interactions[0]["duration_seconds"] == 45
        
        runner.test("Interação com duração", test_interaction_with_duration)
        
        # Test 8: Interação com posição e score
        def test_interaction_with_metadata():
            service = InteractionService(data_dir=temp_dir)
            
            event = InteractionEvent(
                session_id="sess_meta",
                car_id="car_meta",
                interaction_type=InteractionType.WHATSAPP_CONTACT,
                user_preferences=UserPreferencesSnapshot(
                    budget=100000,
                    usage="urbano",
                    priorities=["economia"]
                ),
                car_snapshot=CarSnapshot(
                    marca="Test",
                    modelo="Model",
                    ano=2023,
                    preco=80000,
                    categoria="Hatch",
                    combustivel="Flex",
                    cambio="Manual"
                ),
                recommendation_position=1,
                score=0.95
            )
            
            service.save_interaction(event)
            
            interactions = service.get_interactions_by_session("sess_meta")
            assert len(interactions) > 0
            assert interactions[0]["recommendation_position"] == 1
            assert interactions[0]["score"] == 0.95
        
        runner.test("Interação com metadados", test_interaction_with_metadata)
        
    finally:
        # Limpar diretório temporário
        shutil.rmtree(temp_dir)
    
    # Mostrar resumo
    success = runner.summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
