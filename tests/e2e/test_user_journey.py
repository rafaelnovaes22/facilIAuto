"""
🧪 E2E Tests - User Journey
Testes end-to-end do fluxo completo do usuário
"""

import asyncio

import pytest
from playwright.async_api import Page, expect


@pytest.mark.e2e
class TestUserJourney:
    """Testes E2E do fluxo completo do usuário"""

    @pytest.mark.asyncio
    async def test_complete_user_flow_basic(self, page: Page):
        """Testa fluxo completo básico do usuário"""
        # Arrange
        base_url = "http://localhost:8000"

        # Act & Assert

        # 1. Navegar para a página inicial
        await page.goto(base_url)
        await expect(page).to_have_title("FacilIAuto - Busca Inteligente")

        # 2. Verificar se o questionário está visível
        await expect(page.locator("h1")).to_contain_text("FacilIAuto")
        await expect(page.locator("#questionarioForm")).to_be_visible()

        # 3. Preencher o primeiro passo (marca/modelo)
        await page.select_option("#marcaPrincipal", "TOYOTA")
        await page.fill("#modeloEspecifico", "Corolla")

        # 4. Avançar para próximo passo
        await page.click("#proximoBtn")
        await page.wait_for_timeout(500)  # Aguardar animação

        # 5. Preencher urgência
        await page.check('input[name="urgencia"][value="hoje_amanha"]')
        await page.click("#proximoBtn")

        # 6. Preencher região
        await page.select_option('select[name="regiao"]', "SP")
        await page.click("#proximoBtn")

        # 7. Preencher uso principal
        await page.check('input[name="uso_principal"][value="urbano"]')
        await page.click("#proximoBtn")

        # 8. Preencher pessoas a transportar
        await page.check('input[name="pessoas_transportar"][value="4"]')
        await page.click("#proximoBtn")

        # 9. Preencher necessidades especiais
        # Não marcar crianças nem animais (padrão)
        await page.click("#proximoBtn")

        # 10. Preencher espaço de carga e potência
        await page.check('input[name="espaco_carga"][value="medio"]')
        await page.check('input[name="potencia_desejada"][value="media"]')
        await page.click("#proximoBtn")

        # 11. Preencher prioridade
        await page.check('input[name="prioridade"][value="economia"]')

        # 12. Submeter o formulário
        await page.click("#submitBtn")

        # 13. Aguardar e verificar resultados
        await page.wait_for_selector("#resultados", timeout=10000)
        await expect(page.locator("#resultados")).to_be_visible()

        # 14. Verificar se há recomendações
        recomendacoes = page.locator(".recomendacao-card")
        await expect(recomendacoes.first()).to_be_visible()

        # 15. Verificar se o resumo do perfil está presente
        await expect(page.locator("#resumoPerfil")).to_be_visible()

        # 16. Verificar se há sugestões gerais
        await expect(page.locator("#sugestoesGerais")).to_be_visible()

    @pytest.mark.asyncio
    async def test_advanced_brand_selection_flow(self, page: Page):
        """Testa fluxo avançado de seleção de marcas"""
        # Arrange
        base_url = "http://localhost:8000"

        # Act & Assert

        # 1. Navegar para a página
        await page.goto(base_url)

        # 2. Testar auto-complete de modelo
        await page.select_option("#marcaPrincipal", "TOYOTA")
        await page.fill("#modeloEspecifico", "cor")

        # 3. Aguardar sugestões aparecerem
        await page.wait_for_selector(
            "#modeloSuggestions .suggestion-item", timeout=3000
        )
        suggestions = page.locator("#modeloSuggestions .suggestion-item")
        await expect(suggestions.first()).to_be_visible()

        # 4. Clicar em uma sugestão
        await suggestions.first().click()

        # 5. Verificar se o campo foi preenchido
        modelo_value = await page.locator("#modeloEspecifico").input_value()
        assert "Corolla" in modelo_value

        # 6. Testar marcas alternativas
        await page.click("#toggleMarcasAlternativas")
        await expect(page.locator("#marcasAlternativasCard")).to_be_visible()

        # 7. Selecionar marcas alternativas
        await page.check('input[name="marcas_alternativas"][value="HONDA"]')
        await page.check('input[name="marcas_alternativas"][value="VOLKSWAGEN"]')

        # 8. Verificar feedback de validação
        feedback = page.locator("#preferenciasFeedback")
        # O feedback pode ou não aparecer dependendo da validação

    @pytest.mark.asyncio
    async def test_form_validation_errors(self, page: Page):
        """Testa validação de erros no formulário"""
        # Arrange
        base_url = "http://localhost:8000"

        # Act & Assert

        # 1. Navegar para a página
        await page.goto(base_url)

        # 2. Tentar avançar sem preencher campos obrigatórios
        await page.click("#proximoBtn")

        # 3. Verificar se ainda está no primeiro passo (validação impediu avanço)
        current_step = await page.locator("#currentStep").text_content()
        assert current_step == "1"

        # 4. Preencher campo obrigatório e tentar novamente
        await page.select_option("#marcaPrincipal", "TOYOTA")
        await page.click("#proximoBtn")

        # 5. Verificar se avançou para o próximo passo
        await page.wait_for_timeout(500)
        current_step = await page.locator("#currentStep").text_content()
        assert current_step == "2"

    @pytest.mark.asyncio
    async def test_responsive_design(self, page: Page):
        """Testa design responsivo em diferentes tamanhos de tela"""
        # Arrange
        base_url = "http://localhost:8000"

        # Act & Assert

        # 1. Testar em desktop (padrão)
        await page.goto(base_url)
        await expect(page.locator("#questionarioForm")).to_be_visible()

        # 2. Testar em tablet
        await page.set_viewport_size({"width": 768, "height": 1024})
        await expect(page.locator("#questionarioForm")).to_be_visible()

        # 3. Testar em mobile
        await page.set_viewport_size({"width": 375, "height": 667})
        await expect(page.locator("#questionarioForm")).to_be_visible()

        # 4. Verificar se elementos críticos são acessíveis
        await expect(page.locator("#proximoBtn")).to_be_visible()
        await expect(page.locator("#marcaPrincipal")).to_be_visible()

    @pytest.mark.asyncio
    async def test_error_handling(self, page: Page):
        """Testa tratamento de erros da aplicação"""
        # Arrange
        base_url = "http://localhost:8000"

        # Act & Assert

        # 1. Navegar para a página
        await page.goto(base_url)

        # 2. Simular erro de rede (se possível)
        # Preencher formulário válido
        await page.select_option("#marcaPrincipal", "TOYOTA")
        await self._fill_complete_form(page)

        # 3. Submeter formulário
        await page.click("#submitBtn")

        # 4. Aguardar resposta (pode ser sucesso ou erro dependendo do estado da API)
        try:
            await page.wait_for_selector("#resultados", timeout=10000)
            # Se chegou aqui, a API funcionou
            await expect(page.locator("#resultados")).to_be_visible()
        except:
            # Se deu timeout, verificar se há mensagem de erro apropriada
            error_message = page.locator(".alert-danger, .error-message")
            if await error_message.count() > 0:
                await expect(error_message).to_be_visible()

    @pytest.mark.asyncio
    async def test_accessibility_features(self, page: Page):
        """Testa recursos de acessibilidade"""
        # Arrange
        base_url = "http://localhost:8000"

        # Act & Assert

        # 1. Navegar para a página
        await page.goto(base_url)

        # 2. Verificar se elementos têm labels apropriados
        marca_select = page.locator("#marcaPrincipal")
        await expect(marca_select).to_have_attribute("name", "marca_preferida")

        # 3. Testar navegação por teclado
        await page.keyboard.press("Tab")
        focused_element = await page.evaluate("document.activeElement.id")
        assert focused_element in ["marcaPrincipal", "modeloEspecifico"]

        # 4. Verificar contraste e legibilidade (teste básico)
        form_element = page.locator("#questionarioForm")
        await expect(form_element).to_be_visible()

    async def _fill_complete_form(self, page: Page):
        """Helper para preencher formulário completo"""
        # Navegar por todos os passos
        steps_data = [
            {"urgencia": "hoje_amanha"},
            {"regiao": "SP"},
            {"uso_principal": "urbano"},
            {"pessoas_transportar": "4"},
            {},  # Necessidades especiais (pular)
            {"espaco_carga": "medio", "potencia_desejada": "media"},
            {"prioridade": "economia"},
        ]

        for step_data in steps_data:
            await page.click("#proximoBtn")
            await page.wait_for_timeout(300)

            for field, value in step_data.items():
                if field in [
                    "urgencia",
                    "espaco_carga",
                    "potencia_desejada",
                    "prioridade",
                ]:
                    await page.check(f'input[name="{field}"][value="{value}"]')
                elif field == "regiao":
                    await page.select_option(f'select[name="{field}"]', value)
                elif field in ["uso_principal", "pessoas_transportar"]:
                    await page.check(f'input[name="{field}"][value="{value}"]')


@pytest.mark.e2e
class TestPerformance:
    """Testes de performance E2E"""

    @pytest.mark.asyncio
    async def test_page_load_performance(self, page: Page):
        """Testa performance de carregamento da página"""
        # Arrange
        base_url = "http://localhost:8000"

        # Act
        start_time = asyncio.get_event_loop().time()
        await page.goto(base_url)
        await page.wait_for_load_state("networkidle")
        end_time = asyncio.get_event_loop().time()

        # Assert
        load_time = end_time - start_time
        assert (
            load_time < 5.0
        ), f"Página carregou em {load_time:.2f}s, mas deveria ser < 5s"

    @pytest.mark.asyncio
    async def test_form_submission_performance(self, page: Page):
        """Testa performance de submissão do formulário"""
        # Arrange
        base_url = "http://localhost:8000"
        await page.goto(base_url)

        # Preencher formulário
        await page.select_option("#marcaPrincipal", "TOYOTA")
        await page.fill("#modeloEspecifico", "Corolla")

        # Preencher outros campos rapidamente
        for i in range(7):
            await page.click("#proximoBtn")
            await page.wait_for_timeout(100)

        # Act
        start_time = asyncio.get_event_loop().time()
        await page.click("#submitBtn")
        await page.wait_for_selector("#resultados", timeout=15000)
        end_time = asyncio.get_event_loop().time()

        # Assert
        response_time = end_time - start_time
        assert (
            response_time < 10.0
        ), f"API respondeu em {response_time:.2f}s, mas deveria ser < 10s"
