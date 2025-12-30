"""
Testes para LLMJustificationService (Fase 1)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.llm_justification_service import LLMJustificationService
from models.car import Car
from models.user_profile import UserProfile


class TestLLMJustificationService:
    """Testes do serviço de justificativas LLM"""

    @pytest.fixture
    def mock_groq_client(self):
        """Mock do cliente Groq"""
        with patch('services.llm_justification_service.Groq') as mock:
            client = MagicMock()
            mock.return_value = client

            # Mock da resposta
            response = MagicMock()
            response.choices = [MagicMock()]
            response.choices[0].message.content = (
                "O Volkswagen Taos é perfeito para sua família de 4 pessoas, "
                "com bastante espaço e pontos de fixação para cadeirinha nos bancos de trás. "
                "Você vai gastar cerca de R$ 1.900 por mês (incluindo tudo)."
            )

            client.chat.completions.create.return_value = response

            yield client

    @pytest.fixture
    def mock_openai_client(self):
        """Mock do cliente OpenAI"""
        with patch('services.llm_justification_service.OpenAI') as mock:
            client = MagicMock()
            mock.return_value = client

            # Mock da resposta
            response = MagicMock()
            response.choices = [MagicMock()]
            response.choices[0].message.content = (
                "O Honda HR-V combina espaço e segurança ideal para sua família. "
                "O consumo de 12.5 km/L e custo mensal de R$ 1.650 permitem viagens "
                "sem peso no bolso."
            )

            client.chat.completions.create.return_value = response

            yield client

    @pytest.fixture
    def sample_car(self):
        """Carro de teste"""
        return Car(
            id="test-car-1",
            nome="Volkswagen Taos 1.4 TSI",
            marca="Volkswagen",
            modelo="Taos",
            ano=2023,
            preco=85000,
            quilometragem=20000,
            combustivel="Flex",
            categoria="SUV Compacto",
            consumo_cidade=11.0,
            consumo_estrada=13.5,
            itens_seguranca=["6 airbags", "ABS", "Controle de estabilidade", "ISOFIX"],
            itens_conforto=["Ar-condicionado", "Direção elétrica", "Vidros elétricos"],
            dealership_id="dealer-1",
            dealership_name="Concessionária Teste",
            dealership_city="São Paulo",
            dealership_state="SP",
            dealership_phone="(11) 9999-9999",
            dealership_whatsapp="5511999999999"
        )

    @pytest.fixture
    def sample_profile(self):
        """Perfil de usuário de teste"""
        return UserProfile(
            orcamento_min=60000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            tem_criancas=True,
            prioridades={"economia": 5, "seguranca": 5, "espaco": 4}
        )

    def test_service_initialization_with_groq(self, monkeypatch):
        """Testa inicialização do serviço com Groq"""
        monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
        monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")

        with patch('services.llm_justification_service.GROQ_AVAILABLE', True):
            with patch('services.llm_justification_service.OPENAI_AVAILABLE', True):
                with patch('services.llm_justification_service.Groq'):
                    with patch('services.llm_justification_service.OpenAI'):
                        service = LLMJustificationService(
                            primary_provider="groq",
                            fallback_provider="openai"
                        )

                        assert service.primary_provider == "groq"
                        assert service.fallback_provider == "openai"

    def test_generate_justification_via_groq(
        self,
        sample_car,
        sample_profile,
        mock_groq_client,
        monkeypatch
    ):
        """Testa geração de justificativa via Groq (primário)"""
        monkeypatch.setenv("GROQ_API_KEY", "test_key")

        with patch('services.llm_justification_service.GROQ_AVAILABLE', True):
            with patch('services.llm_justification_service.Groq', return_value=mock_groq_client):
                service = LLMJustificationService(primary_provider="groq")
                service.primary_client = mock_groq_client

                result = service.generate_justification(
                    car=sample_car,
                    profile=sample_profile,
                    score=0.88,
                    position=1,
                    total_results=5,
                    tco_breakdown={"total_mensal": 1900}
                )

                # Verificar que retornou texto válido
                assert result is not None
                assert len(result) > 50
                assert "Volkswagen Taos" in result or "família" in result

                # Verificar que Groq foi chamado
                assert mock_groq_client.chat.completions.create.called

    def test_fallback_to_openai_when_groq_fails(
        self,
        sample_car,
        sample_profile,
        mock_openai_client,
        monkeypatch
    ):
        """Testa fallback para OpenAI quando Groq falha"""
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")

        with patch('services.llm_justification_service.GROQ_AVAILABLE', False):
            with patch('services.llm_justification_service.OPENAI_AVAILABLE', True):
                with patch('services.llm_justification_service.OpenAI', return_value=mock_openai_client):
                    service = LLMJustificationService(
                        primary_provider="groq",
                        fallback_provider="openai"
                    )
                    service.primary_client = None  # Simular Groq indisponível
                    service.fallback_client = mock_openai_client

                    result = service.generate_justification(
                        car=sample_car,
                        profile=sample_profile,
                        score=0.85,
                        position=1,
                        total_results=5,
                        tco_breakdown={"total_mensal": 1650}
                    )

                    # Verificar que usou OpenAI
                    assert result is not None
                    assert len(result) > 50

    def test_fallback_to_template_when_all_llms_fail(
        self,
        sample_car,
        sample_profile
    ):
        """Testa fallback para templates quando todos os LLMs falham"""
        service = LLMJustificationService()
        service.primary_client = None
        service.fallback_client = None

        result = service.generate_justification(
            car=sample_car,
            profile=sample_profile,
            score=0.80,
            position=1,
            total_results=5,
            tco_breakdown={"total_mensal": 1800}
        )

        # Deve retornar justificativa template
        assert result is not None
        assert len(result) > 0
        # Template menciona uso ou orçamento
        assert ("família" in result.lower() or
                "orçamento" in result.lower() or
                "custo" in result.lower())

    def test_validate_output_rejects_empty(self):
        """Testa que validação rejeita output vazio"""
        service = LLMJustificationService()

        assert not service._validate_output("")
        assert not service._validate_output("   ")
        assert not service._validate_output(None)

    def test_validate_output_rejects_too_short(self):
        """Testa que validação rejeita output muito curto"""
        service = LLMJustificationService()

        assert not service._validate_output("Bom carro")  # < 50 chars

    def test_validate_output_accepts_valid(self):
        """Testa que validação aceita output válido"""
        service = LLMJustificationService()

        valid_text = (
            "O Volkswagen Taos é perfeito para sua família de 4 pessoas, "
            "com bastante espaço interno."
        )

        assert service._validate_output(valid_text)

    def test_simplify_text_removes_technical_terms(self):
        """Testa que pós-processamento remove termos técnicos"""
        service = LLMJustificationService()

        text_with_jargon = (
            "Este carro tem ISOFIX, TCO de R$ 1.900 e ABS/ESP."
        )

        result = service._simplify_text(text_with_jargon)

        # Termos técnicos devem ser substituídos
        assert "ISOFIX" not in result or "pontos de fixação" in result
        assert "TCO" not in result or "custo mensal" in result

    def test_metrics_tracking(self, sample_car, sample_profile):
        """Testa que métricas são rastreadas"""
        service = LLMJustificationService()
        service.primary_client = None
        service.fallback_client = None

        # Gerar algumas justificativas (vai usar template)
        for i in range(3):
            service.generate_justification(
                car=sample_car,
                profile=sample_profile,
                score=0.8,
                position=i + 1,
                total_results=5,
                tco_breakdown={}
            )

        metrics = service.get_metrics()

        assert metrics["total_calls"] == 3
        assert metrics["template_usage_rate"] == 1.0  # 100% template

    def test_different_contexts_family(self, sample_car):
        """Testa justificativa para contexto familiar"""
        service = LLMJustificationService()
        service.primary_client = None
        service.fallback_client = None

        profile = UserProfile(
            orcamento_min=60000,
            orcamento_max=100000,
            uso_principal="familia",
            tamanho_familia=4,
            tem_criancas=True
        )

        result = service.generate_justification(
            car=sample_car,
            profile=profile,
            score=0.85,
            position=1,
            total_results=5,
            tco_breakdown={}
        )

        # Deve mencionar família
        assert "família" in result.lower() or "familiar" in result.lower()

    def test_different_contexts_commercial(self, sample_car):
        """Testa justificativa para contexto comercial"""
        service = LLMJustificationService()
        service.primary_client = None
        service.fallback_client = None

        profile = UserProfile(
            orcamento_min=50000,
            orcamento_max=80000,
            uso_principal="comercial",
            tamanho_familia=1,
            prioridades={"economia": 5, "custo_manutencao": 5}
        )

        result = service.generate_justification(
            car=sample_car,
            profile=profile,
            score=0.80,
            position=1,
            total_results=5,
            tco_breakdown={}
        )

        # Deve mencionar comercial ou custo
        assert ("comercial" in result.lower() or
                "custo" in result.lower() or
                "economia" in result.lower())

    def test_template_fallback_with_tco(self, sample_car, sample_profile):
        """Testa que template fallback usa informações de TCO"""
        service = LLMJustificationService()
        service.primary_client = None
        service.fallback_client = None

        tco_breakdown = {
            "total_mensal": 1900,
            "financiamento": 1200,
            "combustivel": 400,
            "manutencao": 200,
            "seguro": 100
        }

        result = service.generate_justification(
            car=sample_car,
            profile=sample_profile,
            score=0.85,
            position=1,
            total_results=5,
            tco_breakdown=tco_breakdown
        )

        # Deve mencionar valores ou custos
        assert "R$" in result or "custo" in result.lower()
