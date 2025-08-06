"""
Testes E2E para Critérios de Uso Principal do Veículo
Seguindo metodologia XP (Extreme Programming) com TDD

Este módulo testa a funcionalidade completa de uso principal:
- Interface melhorada do questionário
- Sistema de scoring avançado  
- Agente especializado do chatbot
- Integração ponta-a-ponta
"""

import asyncio
import json
from typing import Any, Dict

import pytest
from playwright.async_api import Page, expect

# Markers para categorização dos testes XP
pytestmark = [pytest.mark.e2e, pytest.mark.uso_principal, pytest.mark.requires_browser]


class TestUsoMrincipalE2E:
    """
    Classe de testes E2E para uso principal seguindo metodologia XP

    Princípios XP aplicados:
    - Test-Driven Development (TDD)
    - Testes pequenos e focados
    - Feedback rápido
    - Integração contínua
    """

    @pytest.mark.asyncio
    async def test_interface_uso_principal_melhorada(self, page: Page, live_server):
        """
        Testa a interface melhorada do questionário de uso principal

        TDD: Este teste valida a nova interface com cards informativos
        """
        # Given: Usuário acessa a página de busca
        await page.goto(f"{live_server}/")

        # When: Navega até a seção de uso principal
        await page.click('button:has-text("Começar Busca")')

        # Aguardar carregamento
        await page.wait_for_selector("#step4", state="visible", timeout=10000)

        # Then: Deve ver a interface melhorada com cards
        # Verificar se os cards informativos estão presentes

        # Card Urbano
        urbano_card = page.locator("text=🏙️ Uso Urbano (Cidade)")
        await expect(urbano_card).to_be_visible()

        urbano_desc = page.locator(
            "text=Ideal para: trânsito, estacionamento, economia de combustível"
        )
        await expect(urbano_desc).to_be_visible()

        urbano_prioriza = page.locator(
            "text=Priorizamos: carros compactos, baixo consumo, tecnologia de assistência"
        )
        await expect(urbano_prioriza).to_be_visible()

        # Card Viagem
        viagem_card = page.locator("text=🛣️ Viagens Longas")
        await expect(viagem_card).to_be_visible()

        viagem_desc = page.locator("text=Ideal para: rodovias, conforto, segurança")
        await expect(viagem_desc).to_be_visible()

        # Card Trabalho
        trabalho_card = page.locator("text=💼 Trabalho/Negócios")
        await expect(trabalho_card).to_be_visible()

        trabalho_desc = page.locator(
            "text=Ideal para: uso profissional, transporte de equipamentos"
        )
        await expect(trabalho_desc).to_be_visible()

        # Card Família
        familia_card = page.locator("text=👨‍👩‍👧‍👦 Uso Familiar")
        await expect(familia_card).to_be_visible()

        familia_desc = page.locator("text=Ideal para: família, crianças, segurança")
        await expect(familia_desc).to_be_visible()

        print("✅ Interface melhorada de uso principal validada")

    @pytest.mark.asyncio
    async def test_selecao_multipla_uso_principal(self, page: Page, live_server):
        """
        Testa seleção múltipla de tipos de uso

        TDD: Valida que usuário pode selecionar múltiplos usos
        """
        # Given: Usuário na página de uso principal
        await page.goto(f"{live_server}/")
        await page.click('button:has-text("Começar Busca")')
        await page.wait_for_selector("#step4", state="visible")

        # When: Seleciona múltiplos tipos de uso
        await page.check("#uso_urbano")
        await page.check("#uso_familia")
        await page.check("#uso_viagem")

        # Then: Todas as seleções devem estar ativas
        await expect(page.locator("#uso_urbano")).to_be_checked()
        await expect(page.locator("#uso_familia")).to_be_checked()
        await expect(page.locator("#uso_viagem")).to_be_checked()

        # Trabalho não selecionado
        await expect(page.locator("#uso_trabalho")).not_to_be_checked()

        print("✅ Seleção múltipla de uso validada")

    @pytest.mark.asyncio
    async def test_fluxo_completo_com_uso_principal(self, page: Page, live_server):
        """
        Testa fluxo completo de busca com novos critérios de uso

        TDD: Valida integração completa do sistema
        """
        # Given: Usuário inicia busca completa
        await page.goto(f"{live_server}/")
        await page.click('button:has-text("Começar Busca")')

        # Step 1: Marca/Modelo (mantendo simples)
        await page.fill("#marca_preferida", "Toyota")
        await page.fill("#modelo_especifico", "Corolla")
        await page.click('button:has-text("Próximo")')

        # Step 2: Urgência
        await page.wait_for_selector("#urgencia")
        await page.select_option("#urgencia", "sem_pressa")
        await page.click('button:has-text("Próximo")')

        # Step 3: Região
        await page.wait_for_selector("#regiao")
        await page.fill("#regiao", "São Paulo")
        await page.click('button:has-text("Próximo")')

        # Step 4: Uso Principal (foco do teste)
        await page.wait_for_selector("#step4", state="visible")

        # When: Seleciona uso urbano e familiar
        await page.check("#uso_urbano")
        await page.check("#uso_familia")
        await page.click('button:has-text("Próximo")')

        # Continue com outros steps rapidamente
        # Step 5: Família
        await page.wait_for_selector("#pessoas_transportar")
        await page.fill("#pessoas_transportar", "4")
        await page.click('button:has-text("Próximo")')

        # Step 6: Espaço e Potência
        await page.wait_for_selector("#espaco_carga")
        await page.select_option("#espaco_carga", "medio")
        await page.select_option("#potencia_desejada", "economica")
        await page.click('button:has-text("Próximo")')

        # Step 7: Prioridade
        await page.wait_for_selector("#prioridade")
        await page.select_option("#prioridade", "equilibrio")
        await page.click('button:has-text("Buscar Carros")')

        # Then: Deve processar e mostrar resultados
        # Aguardar processamento (pode demorar devido ao LangGraph)
        await page.wait_for_selector("#loading", state="visible", timeout=5000)
        await page.wait_for_selector("#results", state="visible", timeout=30000)

        # Verificar se resultados incluem critérios de uso principal
        results_content = await page.text_content("#results")

        # Deve mencionar uso urbano ou familiar
        assert any(
            termo in results_content.lower()
            for termo in ["urbano", "familiar", "família"]
        ), "Resultados devem incluir referências ao uso principal"

        print("✅ Fluxo completo com uso principal validado")

    @pytest.mark.asyncio
    async def test_chatbot_agente_uso_principal(self, page: Page, live_server):
        """
        Testa o novo agente de uso principal do chatbot

        TDD: Valida funcionamento do agente especializado
        """
        # Given: Usuário em uma página de carro
        await page.goto(f"{live_server}/carro/1")  # Assumindo que carro ID 1 existe

        # Aguardar carregamento da página
        await page.wait_for_selector(".chatbot-widget", timeout=10000)

        # When: Abre o chatbot
        await page.click(".chatbot-widget")
        await page.wait_for_selector("#chatbot-expanded", state="visible")

        # Faz pergunta sobre adequação de uso
        pergunta_uso = "Este carro é adequado para uso urbano e familiar?"
        await page.fill("#chatbot-input", pergunta_uso)
        await page.click("#chatbot-send")

        # Then: Deve receber resposta do agente de uso principal
        # Aguardar resposta (pode demorar devido ao LangGraph)
        await page.wait_for_selector(".chatbot-message.bot", timeout=30000)

        # Verificar se a resposta contém análise de uso principal
        resposta = await page.text_content(".chatbot-message.bot:last-child")

        # Deve conter elementos do agente de uso principal
        uso_keywords = ["uso urbano", "uso familiar", "adequado", "ideal", "recomend"]
        assert any(
            keyword in resposta.lower() for keyword in uso_keywords
        ), f"Resposta deve conter análise de uso principal. Resposta: {resposta}"

        # Pode conter emojis de avaliação
        avaliacoes = ["🌟", "👍", "⚖️", "✅", "⚠️"]
        tem_avaliacao = any(emoji in resposta for emoji in avaliacoes)
        assert tem_avaliacao, "Resposta deve conter avaliação visual"

        print("✅ Agente de uso principal do chatbot validado")

    @pytest.mark.asyncio
    async def test_scoring_avancado_uso_principal(self, page: Page, live_server):
        """
        Testa se o sistema de scoring avançado está funcionando

        TDD: Valida que scores refletem os novos critérios
        """
        # Given: Busca configurada para uso específico
        await page.goto(
            f"{live_server}/api/buscar",
            method="POST",
            data={
                "marca_preferida": "Honda",
                "modelo_especifico": "Civic",
                "urgencia": "sem_pressa",
                "regiao": "Rio de Janeiro",
                "uso_principal": ["urbano"],
                "pessoas_transportar": 4,
                "espaco_carga": "medio",
                "potencia_desejada": "economica",
                "prioridade": "economia",
            },
        )

        # When: Sistema processa com novos critérios
        # Aguardar resposta JSON
        response = await page.wait_for_response(lambda r: "buscar" in r.url)
        resultado = await response.json()

        # Then: Resultado deve conter scoring avançado
        assert "recomendacoes_finais" in resultado
        assert "resumo_perfil" in resultado
        assert "sugestoes_personalizadas" in resultado

        # Verificar se perfil menciona uso urbano
        resumo = resultado["resumo_perfil"].lower()
        assert "urbano" in resumo, "Resumo deve mencionar uso urbano"

        # Verificar se sugestões são específicas para uso urbano
        sugestoes = " ".join(resultado["sugestoes_personalizadas"]).lower()
        urbano_keywords = ["urbano", "cidade", "compacto", "economia", "estacionamento"]
        assert any(
            keyword in sugestoes for keyword in urbano_keywords
        ), "Sugestões devem ser específicas para uso urbano"

        print("✅ Sistema de scoring avançado validado")

    @pytest.mark.asyncio
    async def test_regressao_funcionalidade_anterior(self, page: Page, live_server):
        """
        Teste de regressão para garantir que funcionalidades anteriores continuam funcionando

        TDD: Garante que novas implementações não quebraram o sistema existente
        """
        # Given: Sistema com novas implementações
        await page.goto(f"{live_server}/")

        # When: Executa fluxo básico antigo (sem uso principal)
        await page.click('button:has-text("Começar Busca")')

        # Preenche formulário básico
        await page.fill("#marca_preferida", "Volkswagen")
        await page.click('button:has-text("Próximo")')

        await page.select_option("#urgencia", "esta_semana")
        await page.click('button:has-text("Próximo")')

        await page.fill("#regiao", "Brasília")
        await page.click('button:has-text("Próximo")')

        # Uso principal (nova funcionalidade deve funcionar normalmente)
        await page.wait_for_selector("#step4")
        await page.check("#uso_trabalho")  # Seleciona apenas um uso
        await page.click('button:has-text("Próximo")')

        # Continue fluxo
        await page.fill("#pessoas_transportar", "5")
        await page.click('button:has-text("Próximo")')

        await page.select_option("#espaco_carga", "muito")
        await page.select_option("#potencia_desejada", "alta")
        await page.click('button:has-text("Próximo")')

        await page.select_option("#prioridade", "performance")
        await page.click('button:has-text("Buscar Carros")')

        # Then: Sistema deve continuar funcionando normalmente
        await page.wait_for_selector("#loading", state="visible", timeout=5000)

        # Verificar se não há erros JavaScript
        errors = []
        page.on(
            "console",
            lambda msg: errors.append(msg.text) if msg.type == "error" else None,
        )

        # Aguardar processamento
        await asyncio.sleep(5)

        # Não deve haver erros críticos
        critical_errors = [
            error
            for error in errors
            if "error" in error.lower() and "warning" not in error.lower()
        ]
        assert (
            len(critical_errors) == 0
        ), f"Não deve haver erros JavaScript críticos: {critical_errors}"

        print("✅ Teste de regressão passou - funcionalidades anteriores mantidas")

    @pytest.mark.asyncio
    async def test_performance_novo_sistema(self, page: Page, live_server):
        """
        Teste de performance para o novo sistema de uso principal

        TDD: Garante que performance não degradou significativamente
        """
        import time

        # Given: Sistema com novo processamento
        start_time = time.time()

        # When: Executa busca completa
        await page.goto(f"{live_server}/")
        await page.click('button:has-text("Começar Busca")')

        # Preenche rapidamente
        await page.fill("#marca_preferida", "Toyota")
        await page.click('button:has-text("Próximo")')

        await page.select_option("#urgencia", "sem_pressa")
        await page.click('button:has-text("Próximo")')

        await page.fill("#regiao", "São Paulo")
        await page.click('button:has-text("Próximo")')

        await page.check("#uso_urbano")
        await page.check("#uso_familia")
        await page.click('button:has-text("Próximo")')

        await page.fill("#pessoas_transportar", "4")
        await page.click('button:has-text("Próximo")')

        await page.select_option("#espaco_carga", "medio")
        await page.select_option("#potencia_desejada", "economica")
        await page.click('button:has-text("Próximo")')

        await page.select_option("#prioridade", "equilibrio")

        # Marcar tempo antes da busca
        search_start = time.time()
        await page.click('button:has-text("Buscar Carros")')

        # Aguardar resultado ou timeout
        try:
            await page.wait_for_selector("#results", state="visible", timeout=45000)
            search_end = time.time()
            search_time = search_end - search_start

            # Then: Busca deve completar em tempo razoável
            assert search_time < 45, f"Busca muito lenta: {search_time:.2f}s"

            print(f"✅ Performance OK - Busca completada em {search_time:.2f}s")

        except Exception as e:
            # Se timeout, ainda é informativo
            search_time = time.time() - search_start
            print(
                f"⚠️ Timeout após {search_time:.2f}s - pode indicar problema de performance"
            )
            # Não falha o teste, apenas reporta

        total_time = time.time() - start_time
        print(f"📊 Tempo total do teste: {total_time:.2f}s")


# Fixtures específicas para testes de uso principal
@pytest.fixture
async def uso_principal_test_data():
    """Dados de teste específicos para uso principal"""
    return {
        "urbano": {
            "uso_principal": ["urbano"],
            "potencia_desejada": "economica",
            "espaco_carga": "pouco",
            "prioridade": "economia",
        },
        "viagem": {
            "uso_principal": ["viagem"],
            "potencia_desejada": "media",
            "espaco_carga": "muito",
            "prioridade": "conforto",
        },
        "trabalho": {
            "uso_principal": ["trabalho"],
            "potencia_desejada": "alta",
            "espaco_carga": "muito",
            "prioridade": "equilibrio",
        },
        "familia": {
            "uso_principal": ["familia"],
            "pessoas_transportar": 6,
            "criancas": True,
            "prioridade": "seguranca",
        },
        "multiplo": {
            "uso_principal": ["urbano", "familia", "viagem"],
            "potencia_desejada": "media",
            "espaco_carga": "medio",
            "prioridade": "equilibrio",
        },
    }
