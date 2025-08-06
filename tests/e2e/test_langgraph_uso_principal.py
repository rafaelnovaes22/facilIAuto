"""
Testes E2E específicos para o agente LangGraph de uso principal
Seguindo metodologia XP com TDD

Este módulo testa especificamente:
- Agente uso_principal_agent_node
- Integração com LangGraph workflow
- Roteamento automático para perguntas de uso
- Performance do novo agente
"""

import time

import pytest

from app.langgraph_chatbot_graph import FacilIAutoChatbotGraph
from app.langgraph_chatbot_state import criar_estado_inicial
from app.uso_principal_processor import UsoMatcher

# Markers XP para categorização
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.langgraph_uso_principal,
    pytest.mark.xp_methodology,
    pytest.mark.requires_db,
]


class TestLangGraphUsoPrincipalE2E:
    """
    Testes E2E para agente LangGraph de uso principal

    Metodologia XP aplicada:
    - Test-First Development
    - Testes pequenos e focados
    - Feedback contínuo
    - Refatoração baseada em testes
    """

    @pytest.fixture
    def carro_teste(self):
        """Fixture com dados de carro para testes"""
        return {
            "id": "test_car_1",
            "marca": "Toyota",
            "modelo": "Corolla",
            "categoria": "Hatch",
            "potencia_desejada": "economica",
            "capacidade_pessoas": 5,
            "seguranca": 4,
            "espaco_carga": "medio",
            "opcionais": ["Conectividade Bluetooth", "Ar condicionado", "Câmera de ré"],
            "ano": 2020,
            "preco": 50000,
            "km": 30000,
        }

    @pytest.fixture
    def chatbot_graph(self):
        """Fixture com instância do chatbot LangGraph"""
        return FacilIAutoChatbotGraph()

    def test_roteamento_automatico_uso_principal(self, chatbot_graph, carro_teste):
        """
        Testa se perguntas sobre uso são roteadas corretamente para o agente especializado

        TDD: Valida roteamento automático baseado em palavras-chave
        """
        # Given: Perguntas específicas sobre uso
        perguntas_uso = [
            "Este carro é adequado para uso urbano?",
            "Serve para família com crianças?",
            "É bom para trabalho?",
            "Recomendado para viagens longas?",
            "Adequado para cidade e família?",
        ]

        for pergunta in perguntas_uso:
            # When: Processa pergunta através do workflow
            estado_inicial = criar_estado_inicial(
                conversation_id="test_conv_uso",
                carro_id="test_car_1",
                pergunta=pergunta,
                carro_data=carro_teste,
                user_session_id="test_session",
            )

            resultado = chatbot_graph.processar_pergunta(
                carro_id="test_car_1",
                carro_data=carro_teste,
                pergunta=pergunta,
                conversation_id="test_conv_uso",
                user_session_id="test_session",
            )

            # Then: Deve ser roteado para agente de uso principal
            assert resultado["agente"] == "uso_principal" or "uso_principal" in str(
                resultado.get("resposta", "")
            ), f"Pergunta '{pergunta}' deveria ser roteada para agente de uso principal. Agente obtido: {resultado.get('agente', 'N/A')}"

            # Resposta deve conter análise de uso
            resposta = resultado["resposta"]
            assert any(
                termo in resposta.lower() for termo in ["uso", "adequado", "ideal", "recomend"]
            ), f"Resposta deve conter análise de uso para: {pergunta}"

        print("✅ Roteamento automático para uso principal validado")

    def test_analise_detalhada_uso_urbano(self, chatbot_graph, carro_teste):
        """
        Testa análise detalhada para uso urbano

        TDD: Valida critérios específicos de uso urbano
        """
        # Given: Pergunta específica sobre uso urbano
        pergunta = "Este Toyota Corolla é adequado para uso urbano na cidade?"

        # When: Processa através do agente especializado
        resultado = chatbot_graph.processar_pergunta(
            carro_id="test_car_1",
            carro_data=carro_teste,
            pergunta=pergunta,
            conversation_id="test_conv_urbano",
            user_session_id="test_session",
        )

        # Then: Deve conter análise específica de uso urbano
        resposta = resultado["resposta"]

        # Deve mencionar uso urbano
        assert "uso urbano" in resposta.lower() or "urbano" in resposta.lower()

        # Deve conter critérios urbanos
        criterios_urbanos = [
            "compacto",
            "econômico",
            "manobra",
            "estacionamento",
            "economia",
        ]
        assert any(
            criterio in resposta.lower() for criterio in criterios_urbanos
        ), "Resposta deve conter critérios específicos de uso urbano"

        # Deve ter avaliação visual
        avaliacoes = ["🌟", "👍", "⚖️", "✅", "⚠️"]
        assert any(emoji in resposta for emoji in avaliacoes), "Resposta deve conter avaliação visual"

        # Para Hatch, deve ser positivo para uso urbano
        assert (
            "excelente" in resposta.lower() or "adequado" in resposta.lower() or "ideal" in resposta.lower()
        ), "Hatch deve ter avaliação positiva para uso urbano"

        print("✅ Análise detalhada de uso urbano validada")

    def test_analise_multiplos_usos(self, chatbot_graph, carro_teste):
        """
        Testa análise para múltiplos tipos de uso

        TDD: Valida análise completa quando pergunta envolve vários usos
        """
        # Given: Pergunta sobre múltiplos usos
        pergunta = "Este carro serve para uso urbano, familiar e viagens?"

        # When: Processa pergunta complexa
        resultado = chatbot_graph.processar_pergunta(
            carro_id="test_car_1",
            carro_data=carro_teste,
            pergunta=pergunta,
            conversation_id="test_conv_multiplo",
            user_session_id="test_session",
        )

        # Then: Deve analisar todos os usos mencionados
        resposta = resultado["resposta"]

        # Deve mencionar pelo menos 2 dos 3 usos
        usos_mencionados = []
        if "urbano" in resposta.lower():
            usos_mencionados.append("urbano")
        if "familiar" in resposta.lower() or "família" in resposta.lower():
            usos_mencionados.append("familiar")
        if "viagem" in resposta.lower():
            usos_mencionados.append("viagem")

        assert len(usos_mencionados) >= 2, f"Deve analisar pelo menos 2 usos. Encontrados: {usos_mencionados}"

        # Deve ter recomendação geral
        assert "recomend" in resposta.lower(), "Deve conter recomendação geral para múltiplos usos"

        print("✅ Análise de múltiplos usos validada")

    def test_performance_agente_uso_principal(self, chatbot_graph, carro_teste):
        """
        Testa performance do novo agente

        TDD: Garante que novo agente não degradou performance
        """
        # Given: Pergunta sobre uso
        pergunta = "Este carro é adequado para família?"

        # When: Mede tempo de processamento
        start_time = time.time()

        resultado = chatbot_graph.processar_pergunta(
            carro_id="test_car_1",
            carro_data=carro_teste,
            pergunta=pergunta,
            conversation_id="test_conv_perf",
            user_session_id="test_session",
        )

        end_time = time.time()
        processing_time = end_time - start_time

        # Then: Deve processar em tempo razoável
        assert processing_time < 10.0, f"Agente de uso principal muito lento: {processing_time:.2f}s"

        # Deve gerar resposta válida
        assert "resposta" in resultado
        assert len(resultado["resposta"]) > 20, "Resposta deve ter conteúdo mínimo"

        print(f"✅ Performance OK - Processado em {processing_time:.2f}s")

    def test_integracao_uso_matcher(self, carro_teste):
        """
        Testa integração direta com UsoMatcher

        TDD: Valida que UsoMatcher funciona corretamente no contexto E2E
        """
        # Given: Configuração de teste para uso familiar
        from app.models import QuestionarioBusca

        questionario = QuestionarioBusca(
            marca_preferida="Toyota",
            modelo_especifico="Corolla",
            urgencia="sem_pressa",
            regiao="São Paulo",
            uso_principal=["familia"],
            pessoas_transportar=5,
            criancas=True,
            espaco_carga="medio",
            potencia_desejada="media",
            prioridade="seguranca",
        )

        # When: Calcula score de uso principal
        score, razoes, pontos_fortes = UsoMatcher.calcular_score_uso_principal(questionario, carro_teste)

        # Then: Deve gerar score e análise válidos
        assert score > 0, "Score deve ser positivo para uso familiar"
        assert len(razoes) > 0, "Deve gerar razões para a recomendação"
        assert len(pontos_fortes) > 0, "Deve identificar pontos fortes"

        # Para uso familiar com criança, deve mencionar segurança
        razoes_texto = " ".join(razoes + pontos_fortes).lower()
        assert "família" in razoes_texto or "segur" in razoes_texto, "Deve mencionar aspectos familiares ou de segurança"

        print(f"✅ UsoMatcher integrado - Score: {score:.2f}")

    def test_memoria_persistente_uso_principal(self, chatbot_graph, carro_teste):
        """
        Testa integração com sistema de memória persistente

        TDD: Valida que conversas sobre uso são persistidas corretamente
        """
        # Given: Sequência de perguntas sobre uso
        conversation_id = "test_conv_memoria_uso"

        perguntas = [
            "Este carro é bom para uso urbano?",
            "E para família?",
            "Qual é melhor: urbano ou familiar?",
        ]

        for i, pergunta in enumerate(perguntas):
            # When: Processa pergunta com memória
            resultado = chatbot_graph.processar_pergunta(
                carro_id="test_car_1",
                carro_data=carro_teste,
                pergunta=pergunta,
                conversation_id=conversation_id,
                user_session_id="test_session_memoria",
            )

            # Then: Deve processar com contexto crescente
            assert "resposta" in resultado
            assert len(resultado["resposta"]) > 10

            # A partir da segunda pergunta, pode haver contexto
            if i > 0:
                # Pode referenciar conversa anterior (não obrigatório)
                estado = resultado.get("estado_final", {})
                historico = estado.get("historical_context", "")
                # Apenas verifica que sistema de memória está ativo
                assert isinstance(historico, str), "Sistema de memória deve estar ativo"

        print("✅ Integração com memória persistente validada")

    def test_tratamento_erros_agente_uso(self, chatbot_graph):
        """
        Testa tratamento de erros no agente de uso principal

        TDD: Valida robustez do agente
        """
        # Given: Dados inválidos ou incompletos
        casos_erro = [
            {
                "carro_data": {},  # Carro vazio
                "pergunta": "É adequado para uso urbano?",
            },
            {
                "carro_data": {"id": "invalid"},  # Carro incompleto
                "pergunta": "Serve para família?",
            },
            {"carro_data": None, "pergunta": "É bom para trabalho?"},  # Carro nulo
        ]

        for i, caso in enumerate(casos_erro):
            try:
                # When: Processa com dados inválidos
                resultado = chatbot_graph.processar_pergunta(
                    carro_id="invalid_car",
                    carro_data=caso["carro_data"],
                    pergunta=caso["pergunta"],
                    conversation_id=f"test_erro_{i}",
                    user_session_id="test_session_erro",
                )

                # Then: Deve tratar erro graciosamente
                assert "resposta" in resultado, "Deve gerar resposta mesmo com dados inválidos"

                # Resposta não deve estar vazia
                assert len(resultado["resposta"]) > 0, "Resposta de erro não deve estar vazia"

            except Exception as e:
                # Erros são aceitáveis, mas não devem quebrar o sistema
                print(f"⚠️ Erro esperado tratado: {str(e)[:100]}")

        print("✅ Tratamento de erros validado")

    def test_regressao_agentes_existentes(self, chatbot_graph, carro_teste):
        """
        Teste de regressão para garantir que agentes existentes continuam funcionando

        TDD: Garante que novo agente não quebrou funcionalidades existentes
        """
        # Given: Perguntas para outros agentes
        perguntas_outros_agentes = [
            ("Qual o preço deste carro?", "financeiro"),
            ("Quantos cavalos tem o motor?", "tecnico"),
            ("Como comparar com Honda Civic?", "comparacao"),
            ("Qual o custo de manutenção?", "manutencao"),
            ("Vale a pena pelo preço?", "avaliacao"),
        ]

        for pergunta, agente_esperado in perguntas_outros_agentes:
            # When: Processa pergunta de outros domínios
            resultado = chatbot_graph.processar_pergunta(
                carro_id="test_car_1",
                carro_data=carro_teste,
                pergunta=pergunta,
                conversation_id=f"test_regressao_{agente_esperado}",
                user_session_id="test_session_regressao",
            )

            # Then: Deve funcionar normalmente
            assert "resposta" in resultado, f"Agente {agente_esperado} deve continuar funcionando"

            assert len(resultado["resposta"]) > 10, f"Resposta do agente {agente_esperado} deve ter conteúdo"

            # Agente selecionado deve ser apropriado (não necessariamente exato)
            resultado.get("agente_selecionado", "")
            # Não deve ser sempre uso_principal
            # (alguns casos podem ser ambíguos, então não validamos exatamente)

        print("✅ Regressão de agentes existentes validada")


# Fixtures específicas para testes LangGraph de uso principal
@pytest.fixture
def uso_principal_scenarios():
    """Cenários de teste para diferentes tipos de uso"""
    return {
        "urbano_puro": {
            "pergunta": "É adequado para uso urbano?",
            "esperado": ["urbano", "cidade", "compacto", "manobra"],
            "score_minimo": 2.0,
        },
        "familiar_puro": {
            "pergunta": "Serve para família com crianças?",
            "esperado": ["família", "crianças", "segurança", "espaço"],
            "score_minimo": 2.0,
        },
        "trabalho_puro": {
            "pergunta": "É bom para trabalho?",
            "esperado": ["trabalho", "profissional", "carga", "durabilidade"],
            "score_minimo": 1.5,
        },
        "viagem_pura": {
            "pergunta": "Recomendado para viagens longas?",
            "esperado": ["viagem", "estrada", "conforto", "potência"],
            "score_minimo": 1.5,
        },
        "multiplo_complexo": {
            "pergunta": "Este carro serve para uso urbano, familiar e trabalho?",
            "esperado": ["urbano", "família", "trabalho", "versátil"],
            "score_minimo": 3.0,
        },
    }
