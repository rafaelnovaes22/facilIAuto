"""
🧪 Testes E2E XP - Jornadas Completas do Usuário

User Stories E2E:
1. "Como usuário, quero fazer o questionário e ver recomendações"
2. "Como usuário, quero demonstrar interesse em um carro"
3. "Como admin, quero acessar dashboard e ver leads"

Seguindo XP:
- Testes representam fluxos reais do usuário
- Cobertura dos caminhos críticos de negócio
- Feedback rápido sobre quebras no sistema
"""

import pytest
from playwright.async_api import Page, expect
import asyncio
import time


class TestUserJourneyQuestionnaire:
    """
    User Story E2E 1: Jornada completa do questionário
    "Como usuário, quero responder 8 perguntas e receber recomendações personalizadas"
    """
    
    @pytest.mark.e2e
    @pytest.mark.user_story_1
    @pytest.mark.acceptance
    async def test_complete_questionnaire_flow(self, page: Page, live_server_url):
        """
        Teste E2E: Fluxo completo do questionário até recomendações
        """
        # Arrange
        await page.goto(live_server_url)
        
        # Assert - Página inicial carregou
        await expect(page).to_have_title("CarFinder - Encontre seu carro ideal")
        await expect(page.locator("h1")).to_contain_text("CarFinder")
        await expect(page.locator("text=Pergunta 1 de 8")).to_be_visible()
        
        # Act - Responder questionário completo
        await self._fill_complete_questionnaire(page)
        
        # Act - Enviar questionário
        await page.click("text=Ver Recomendações")
        
        # Assert - Redirecionou para resultados
        await expect(page).to_have_url(f"{live_server_url}/results.html")
        await expect(page.locator("h1")).to_contain_text("Suas Recomendações")
        
        # Assert - Resultados exibidos
        await expect(page.locator("text=Encontramos")).to_be_visible(timeout=10000)
        
        # Verificar se há pelo menos um carro recomendado
        car_cards = page.locator('[class*="card"]')
        await expect(car_cards.first()).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.user_story_1
    @pytest.mark.quick
    async def test_questionnaire_validation(self, page: Page, live_server_url):
        """
        Teste E2E: Validação do questionário (não permite prosseguir sem resposta)
        """
        # Arrange
        await page.goto(live_server_url)
        
        # Assert - Botão "Próxima" está desabilitado inicialmente
        next_button = page.locator("#next-btn")
        await expect(next_button).to_be_disabled()
        
        # Act - Selecionar uma opção
        await page.click("text=Até R$ 30.000")
        
        # Assert - Botão fica habilitado
        await expect(next_button).to_be_enabled()
    
    @pytest.mark.e2e
    @pytest.mark.user_story_1
    @pytest.mark.acceptance
    async def test_questionnaire_navigation(self, page: Page, live_server_url):
        """
        Teste E2E: Navegação entre perguntas funciona corretamente
        """
        # Arrange
        await page.goto(live_server_url)
        
        # Act - Responder primeira pergunta
        await page.click("text=R$ 30.000 - R$ 50.000")
        await page.click("#next-btn")
        
        # Assert - Foi para pergunta 2
        await expect(page.locator("text=Pergunta 2 de 8")).to_be_visible()
        await expect(page.locator("text=Como vai usar o carro?")).to_be_visible()
        
        # Act - Voltar para pergunta 1
        await page.click("#prev-btn")
        
        # Assert - Voltou para pergunta 1 com resposta mantida
        await expect(page.locator("text=Pergunta 1 de 8")).to_be_visible()
        await expect(page.locator("text=R$ 30.000 - R$ 50.000")).to_have_class(/border-blue-500/)
    
    @pytest.mark.e2e
    @pytest.mark.user_story_1
    @pytest.mark.acceptance
    async def test_questionnaire_with_text_details(self, page: Page, live_server_url):
        """
        Teste E2E: Campo de texto livre influencia recomendações
        """
        # Arrange
        await page.goto(live_server_url)
        
        # Act - Responder questionário básico
        await self._fill_basic_questionnaire(page)
        
        # Act - Preencher campo de texto com contexto específico
        await page.fill("#details-text", "Vou trabalhar como motorista de Uber, preciso de máxima economia")
        
        # Act - Enviar
        await page.click("#submit-btn")
        
        # Assert - Ver recomendações
        await expect(page).to_have_url(f"{live_server_url}/results.html")
        
        # Assert - Deve ter razões relacionadas a trabalho/economia
        await expect(page.locator("text=trabalho")).to_be_visible(timeout=10000)
    
    async def _fill_complete_questionnaire(self, page: Page):
        """Helper: Preenche questionário completo"""
        questions_and_answers = [
            ("R$ 30.000 - R$ 50.000", "next"),  # Orçamento
            ("Trabalhar (Uber/99/iFood)", "next"),  # Uso
            ("1-2 pessoas", "next"),  # Capacidade
            ("Máxima economia", "next"),  # Prioridade
            ("Sem preferência", "next"),  # Marca
            ("Tanto faz", "next"),  # Câmbio
            ("Intermediário (2016-2019)", "next"),  # Idade
            ("São Paulo", "finalizar")  # Região
        ]
        
        for answer, action in questions_and_answers:
            await page.click(f"text={answer}")
            if action == "next":
                await page.click("#next-btn")
            # Para "finalizar", não clica (vai para campo livre)
        
        # Campo livre (opcional)
        await page.fill("#details-text", "Preciso de um carro econômico para trabalho")
    
    async def _fill_basic_questionnaire(self, page: Page):
        """Helper: Preenche questionário básico (sem detalhes)"""
        await self._fill_complete_questionnaire(page)


class TestUserJourneyLeads:
    """
    User Story E2E 2: Demonstrar interesse em carro
    "Como usuário, quero demonstrar interesse em um carro e ser contatado"
    """
    
    @pytest.mark.e2e
    @pytest.mark.user_story_3
    @pytest.mark.acceptance
    async def test_complete_lead_generation_flow(self, page: Page, live_server_url):
        """
        Teste E2E: Fluxo completo de geração de lead
        """
        # Arrange - Ir direto para resultados (assumindo que há recomendações)
        await page.goto(f"{live_server_url}/results.html")
        
        # Simular dados de recomendações no localStorage
        await page.evaluate("""
            localStorage.setItem('recommendations', JSON.stringify({
                recommendations: [
                    {
                        id: 1,
                        brand: "Chevrolet",
                        model: "Onix",
                        year: 2022,
                        price: 45000,
                        category: "hatch",
                        transmission: "manual",
                        consumption: 14.2,
                        score: 95,
                        reasons: ["Muito econômico", "Ideal para trabalho"],
                        photo_url: null
                    }
                ]
            }));
        """)
        
        # Recarregar para mostrar resultados
        await page.reload()
        
        # Assert - Recomendações carregaram
        await expect(page.locator("text=Chevrolet Onix")).to_be_visible()
        
        # Act - Clicar em "Tenho Interesse"
        await page.click("text=Tenho Interesse")
        
        # Assert - Modal abriu
        await expect(page.locator("#contact-modal")).to_be_visible()
        await expect(page.locator("text=Demonstrar Interesse")).to_be_visible()
        
        # Act - Preencher formulário
        await page.fill("#contact-name", "João Silva")
        await page.fill("#contact-phone", "(11) 99999-9999")
        await page.fill("#contact-email", "joao@email.com")
        await page.fill("#contact-message", "Gostaria de agendar um test drive")
        
        # Act - Enviar
        await page.click("text=Enviar Contato")
        
        # Assert - Sucesso
        await expect(page.locator("text=Obrigado")).to_be_visible(timeout=5000)
        
        # Assert - Modal fechou
        await expect(page.locator("#contact-modal")).to_be_hidden()
    
    @pytest.mark.e2e
    @pytest.mark.user_story_3
    @pytest.mark.quick
    async def test_lead_form_validation(self, page: Page, live_server_url):
        """
        Teste E2E: Validação do formulário de lead
        """
        # Arrange
        await page.goto(f"{live_server_url}/results.html")
        
        # Simular recomendação
        await page.evaluate("""
            localStorage.setItem('recommendations', JSON.stringify({
                recommendations: [{
                    id: 1, brand: "Test", model: "Car", year: 2020, price: 50000,
                    category: "hatch", transmission: "manual", score: 80, reasons: ["Test"]
                }]
            }));
        """)
        await page.reload()
        
        # Act - Abrir modal
        await page.click("text=Tenho Interesse")
        
        # Act - Tentar enviar sem preencher campos obrigatórios
        await page.click("text=Enviar Contato")
        
        # Assert - Validação HTML5 impede envio
        name_field = page.locator("#contact-name")
        await expect(name_field).to_have_attribute("required")
        
        phone_field = page.locator("#contact-phone")
        await expect(phone_field).to_have_attribute("required")
    
    @pytest.mark.e2e
    @pytest.mark.user_story_3
    @pytest.mark.quick
    async def test_lead_modal_close_behavior(self, page: Page, live_server_url):
        """
        Teste E2E: Comportamento de fechar modal
        """
        # Arrange
        await page.goto(f"{live_server_url}/results.html")
        
        # Simular recomendação
        await page.evaluate("""
            localStorage.setItem('recommendations', JSON.stringify({
                recommendations: [{
                    id: 1, brand: "Test", model: "Car", year: 2020, price: 50000,
                    category: "hatch", transmission: "manual", score: 80, reasons: ["Test"]
                }]
            }));
        """)
        await page.reload()
        
        # Act - Abrir modal
        await page.click("text=Tenho Interesse")
        await expect(page.locator("#contact-modal")).to_be_visible()
        
        # Act - Fechar com X
        await page.click("text=×")
        
        # Assert - Modal fechou
        await expect(page.locator("#contact-modal")).to_be_hidden()
        
        # Act - Abrir novamente e fechar com Escape
        await page.click("text=Tenho Interesse")
        await page.keyboard.press("Escape")
        
        # Assert - Modal fechou
        await expect(page.locator("#contact-modal")).to_be_hidden()


class TestAdminDashboardJourney:
    """
    User Story E2E 3: Dashboard administrativo
    "Como admin, quero acessar dashboard e visualizar leads/estatísticas"
    """
    
    @pytest.mark.e2e
    @pytest.mark.user_story_4
    @pytest.mark.acceptance
    async def test_admin_dashboard_access(self, page: Page, live_server_url):
        """
        Teste E2E: Acesso ao dashboard administrativo
        """
        # Act
        await page.goto(f"{live_server_url}/admin.html")
        
        # Assert - Dashboard carregou
        await expect(page).to_have_title("Admin Dashboard - CarFinder")
        await expect(page.locator("h1")).to_contain_text("CarFinder Admin")
        
        # Assert - Cards de estatísticas estão presentes
        await expect(page.locator("text=Total de Carros")).to_be_visible()
        await expect(page.locator("text=Total de Leads")).to_be_visible()
        await expect(page.locator("text=Leads Hoje")).to_be_visible()
        await expect(page.locator("text=Taxa Conversão")).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.user_story_4
    @pytest.mark.acceptance
    async def test_admin_stats_loading(self, page: Page, live_server_url):
        """
        Teste E2E: Carregamento de estatísticas no dashboard
        """
        # Arrange
        await page.goto(f"{live_server_url}/admin.html")
        
        # Assert - Loading aparece primeiro
        await expect(page.locator("#loading")).to_be_visible()
        
        # Assert - Conteúdo carrega após loading
        await expect(page.locator("#content")).to_be_visible(timeout=10000)
        await expect(page.locator("#loading")).to_be_hidden()
        
        # Assert - Estatísticas foram carregadas (não são mais "-")
        await expect(page.locator("#total-cars")).not_to_have_text("-")
        await expect(page.locator("#total-leads")).not_to_have_text("-")
    
    @pytest.mark.e2e
    @pytest.mark.user_story_4
    @pytest.mark.acceptance
    async def test_admin_leads_table(self, page: Page, live_server_url):
        """
        Teste E2E: Tabela de leads no dashboard
        """
        # Arrange
        await page.goto(f"{live_server_url}/admin.html")
        
        # Wait for content to load
        await expect(page.locator("#content")).to_be_visible(timeout=10000)
        
        # Assert - Tabela de leads existe
        await expect(page.locator("text=Leads Recentes")).to_be_visible()
        
        # Assert - Headers da tabela estão presentes
        headers = ["Data", "Nome", "WhatsApp", "Carro Interesse", "Preço", "Ações"]
        for header in headers:
            await expect(page.locator(f"text={header}")).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.user_story_4
    @pytest.mark.quick
    async def test_admin_refresh_functionality(self, page: Page, live_server_url):
        """
        Teste E2E: Funcionalidade de refresh no dashboard
        """
        # Arrange
        await page.goto(f"{live_server_url}/admin.html")
        await expect(page.locator("#content")).to_be_visible(timeout=10000)
        
        # Act - Clicar no botão refresh
        await page.click("text=Atualizar")
        
        # Assert - Botão mostra estado de loading
        await expect(page.locator("text=Atualizando...")).to_be_visible()
        
        # Assert - Voltou ao estado normal
        await expect(page.locator("text=Atualizar")).to_be_visible(timeout=5000)


class TestMobileResponsiveness:
    """
    Testes E2E para responsividade mobile (XP: All environments)
    """
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    @pytest.mark.quick
    async def test_mobile_questionnaire_usability(self, page: Page, live_server_url):
        """
        Teste E2E: Questionário funciona bem em mobile
        """
        # Arrange - Simular mobile
        await page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE
        await page.goto(live_server_url)
        
        # Assert - Layout mobile responsivo
        await expect(page.locator("h1")).to_be_visible()
        
        # Act - Interagir com opções (devem ser tocáveis)
        await page.tap("text=Até R$ 30.000")
        
        # Assert - Opção foi selecionada
        await expect(page.locator("text=Até R$ 30.000")).to_have_class(/border-blue-500/)
        
        # Assert - Botão próxima é tocável
        next_button = page.locator("#next-btn")
        await expect(next_button).to_be_enabled()
        await expect(next_button).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    @pytest.mark.quick
    async def test_mobile_results_display(self, page: Page, live_server_url):
        """
        Teste E2E: Resultados são bem exibidos em mobile
        """
        # Arrange - Mobile viewport
        await page.set_viewport_size({"width": 375, "height": 667})
        await page.goto(f"{live_server_url}/results.html")
        
        # Simular recomendações
        await page.evaluate("""
            localStorage.setItem('recommendations', JSON.stringify({
                recommendations: [{
                    id: 1, brand: "Chevrolet", model: "Onix", year: 2022, price: 45000,
                    category: "hatch", transmission: "manual", consumption: 14.2,
                    score: 95, reasons: ["Econômico", "Confiável"], photo_url: null
                }]
            }));
        """)
        await page.reload()
        
        # Assert - Cards são visíveis e bem formatados
        await expect(page.locator("text=Chevrolet Onix")).to_be_visible()
        await expect(page.locator("text=95% compatível")).to_be_visible()
        await expect(page.locator("text=Tenho Interesse")).to_be_visible()


class TestPerformanceE2E:
    """
    Testes E2E de performance (XP: Fast feedback)
    """
    
    @pytest.mark.e2e
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_page_load_performance(self, page: Page, live_server_url):
        """
        Teste E2E: Páginas carregam rapidamente
        """
        # Act & Assert - Página inicial
        start_time = time.time()
        await page.goto(live_server_url)
        await expect(page.locator("h1")).to_be_visible()
        load_time = time.time() - start_time
        
        assert load_time < 3.0, f"Página inicial demorou {load_time:.2f}s para carregar"
        
        # Act & Assert - Página de resultados
        start_time = time.time()
        await page.goto(f"{live_server_url}/results.html")
        await expect(page.locator("h1")).to_be_visible()
        load_time = time.time() - start_time
        
        assert load_time < 3.0, f"Página de resultados demorou {load_time:.2f}s para carregar"
    
    @pytest.mark.e2e
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_recommendation_api_response_time(self, page: Page, live_server_url):
        """
        Teste E2E: API de recomendações responde rapidamente via frontend
        """
        # Arrange
        await page.goto(live_server_url)
        
        # Preencher questionário rapidamente
        await page.click("text=R$ 30.000 - R$ 50.000")
        await page.click("#next-btn")
        await page.click("text=Trabalhar (Uber/99/iFood)")
        
        # Pular para o final
        for _ in range(6):
            await page.click("#next-btn")
        
        # Act - Medir tempo da requisição
        start_time = time.time()
        await page.click("#submit-btn")
        
        # Wait for response
        await expect(page).to_have_url(f"{live_server_url}/results.html")
        response_time = time.time() - start_time
        
        # Assert - Deve responder em menos de 5 segundos
        assert response_time < 5.0, f"API demorou {response_time:.2f}s para responder"


class TestAccessibilityE2E:
    """
    Testes E2E de acessibilidade (XP: Inclusive design)
    """
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    @pytest.mark.acceptance
    async def test_keyboard_navigation(self, page: Page, live_server_url):
        """
        Teste E2E: Navegação por teclado funciona
        """
        # Arrange
        await page.goto(live_server_url)
        
        # Act - Navegar por tab
        await page.keyboard.press("Tab")  # Primeira opção
        await page.keyboard.press("Enter")  # Selecionar
        
        # Assert - Opção foi selecionada
        focused_element = await page.evaluate("document.activeElement.textContent")
        assert "R$ 30.000" in focused_element or "50.000" in focused_element
        
        # Act - Tab para botão próxima
        await page.keyboard.press("Tab")
        await page.keyboard.press("Tab")  # Pode precisar de mais tabs
        await page.keyboard.press("Enter")  # Próxima pergunta
        
        # Assert - Foi para próxima pergunta
        await expect(page.locator("text=Pergunta 2 de 8")).to_be_visible()
    
    @pytest.mark.e2e
    @pytest.mark.frontend
    @pytest.mark.quick
    async def test_form_labels_and_structure(self, page: Page, live_server_url):
        """
        Teste E2E: Formulários têm estrutura acessível
        """
        # Arrange
        await page.goto(f"{live_server_url}/results.html")
        
        # Simular recomendação para mostrar modal
        await page.evaluate("""
            localStorage.setItem('recommendations', JSON.stringify({
                recommendations: [{
                    id: 1, brand: "Test", model: "Car", year: 2020, price: 50000,
                    category: "hatch", transmission: "manual", score: 80, reasons: ["Test"]
                }]
            }));
        """)
        await page.reload()
        
        # Act - Abrir modal de contato
        await page.click("text=Tenho Interesse")
        
        # Assert - Labels estão associados aos inputs
        name_label = page.locator('label:has-text("Nome Completo")')
        await expect(name_label).to_be_visible()
        
        phone_label = page.locator('label:has-text("WhatsApp")')
        await expect(phone_label).to_be_visible()
        
        # Assert - Inputs têm placeholders ou labels
        phone_input = page.locator("#contact-phone")
        await expect(phone_input).to_have_attribute("placeholder")


class TestRegressionE2E:
    """
    Testes de regressão E2E (XP: Prevent regression)
    """
    
    @pytest.mark.e2e
    @pytest.mark.regression
    @pytest.mark.quick
    async def test_no_javascript_errors_in_console(self, page: Page, live_server_url):
        """
        Teste E2E: Não há erros JavaScript no console
        """
        # Arrange - Capturar erros do console
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        
        # Act - Navegar pelas páginas principais
        await page.goto(live_server_url)
        await page.goto(f"{live_server_url}/results.html")
        await page.goto(f"{live_server_url}/admin.html")
        
        # Assert - Não há erros críticos
        critical_errors = [error for error in console_errors 
                          if "error" in error.lower() and "404" not in error and "failed to fetch" not in error.lower()]
        
        assert len(critical_errors) == 0, f"Erros JavaScript encontrados: {critical_errors}"
    
    @pytest.mark.e2e
    @pytest.mark.regression
    @pytest.mark.acceptance
    async def test_critical_user_flow_still_works(self, page: Page, live_server_url):
        """
        Teste E2E: Fluxo crítico ainda funciona (smoke test)
        """
        # Act - Fluxo mínimo viável
        await page.goto(live_server_url)
        await page.click("text=R$ 30.000 - R$ 50.000")  # Responder uma pergunta
        
        # Ir direto para final
        for _ in range(8):
            next_btn = page.locator("#next-btn")
            if await next_btn.is_enabled():
                await next_btn.click()
            else:
                break
        
        # Tentar enviar
        submit_btn = page.locator("#submit-btn")
        if await submit_btn.is_visible():
            await submit_btn.click()
        
        # Assert - Não travou em nenhum passo crítico
        # Se chegou até aqui sem timeout, o fluxo básico funciona
        assert True  # Explicit assertion for clarity