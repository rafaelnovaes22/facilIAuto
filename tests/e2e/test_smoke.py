"""
🧪 Smoke Test E2E - FacilIAuto
Teste crítico para validar fluxo principal: questionário → busca → resultados
"""
import pytest
from playwright.sync_api import Page, expect


class TestSmokeE2E:
    """
    Smoke test minimalista e robusto para validar fluxo crítico
    """

    def test_complete_user_flow_smoke(self, enhanced_page: Page, live_server: str):
        """
        🎯 SMOKE TEST CRÍTICO: Fluxo completo do usuário

        Fluxo testado:
        1. Acessa página principal
        2. Preenche questionário (8 steps)
        3. Submete busca
        4. Valida resultados

        Este teste DEVE sempre passar para garantir que a funcionalidade core funciona.
        """
        page = enhanced_page

        print("\n🚀 [SMOKE] Iniciando teste crítico do fluxo principal")

        try:
            # =================
            # 📄 PASSO 1: Acessar página principal
            # =================
            print("📄 [SMOKE] Passo 1: Acessando página principal...")
            page.goto(live_server, wait_until="domcontentloaded")

            # Validar que a página carregou
            expect(page).to_have_title("FacilIAuto - Encontre seu carro ideal")
            page.wait_for_selector("#step1", state="visible", timeout=10000)

            print("✅ [SMOKE] Página principal carregada com sucesso")

            # =================
            # 📝 PASSO 2: Preencher questionário
            # =================
            print("📝 [SMOKE] Passo 2: Preenchendo questionário...")

            # STEP 1: Marca/Modelo (opcional)
            page.wait_for_selector("#step1", state="visible")
            print("  📍 [SMOKE] Step 1 visível - Marca/Modelo")
            self._safe_click(page, 'button:has-text("Próximo")')

            # STEP 2: Urgência
            page.wait_for_selector("#step2", state="visible", timeout=10000)
            print("  📍 [SMOKE] Step 2 visível - Urgência")
            self._safe_click(page, 'input[value="ate_15_dias"]')
            self._safe_click(page, 'button:has-text("Próximo")')

            # STEP 3: Localização
            page.wait_for_selector("#step3", state="visible", timeout=10000)
            print("  📍 [SMOKE] Step 3 visível - Localização")
            page.select_option('select[name="regiao"]', "SP")
            self._safe_click(page, 'button:has-text("Próximo")')

            # STEP 4: Uso Principal
            page.wait_for_selector("#step4", state="visible", timeout=10000)
            print("  📍 [SMOKE] Step 4 visível - Uso Principal")
            self._safe_click(page, 'input[value="urbano"]')
            self._safe_click(page, 'button:has-text("Próximo")')

            # STEP 5: Pessoas
            page.wait_for_selector("#step5", state="visible", timeout=10000)
            print("  📍 [SMOKE] Step 5 visível - Pessoas")
            page.select_option('select[name="pessoas_transportar"]', "2")
            self._safe_click(page, 'button:has-text("Próximo")')

            # STEP 6: Espaço e Potência
            page.wait_for_selector("#step6", state="visible", timeout=10000)
            print("  📍 [SMOKE] Step 6 visível - Espaço e Potência")
            # Selects já têm valores padrão corretos - apenas verificar se estão visíveis
            page.wait_for_selector(
                'select[name="espaco_carga"]', state="visible", timeout=10000
            )
            page.wait_for_selector(
                'select[name="potencia_desejada"]', state="visible", timeout=10000
            )
            print("  ✅ [SMOKE] Selects de espaço e potência verificados")
            self._safe_click(page, 'button:has-text("Próximo")')

            # STEP 7: Prioridades
            page.wait_for_selector("#step7", state="visible", timeout=10000)
            print("  📍 [SMOKE] Step 7 visível - Prioridades")
            self._safe_click(page, 'input[value="economia"]')
            self._safe_click(page, 'button:has-text("Próximo")')

            # STEP 8: Orçamento
            page.wait_for_selector("#step8", state="visible", timeout=10000)
            print("  📍 [SMOKE] Step 8 visível - Orçamento")
            page.fill('input[name="orcamento_min"]', "30000")
            page.fill('input[name="orcamento_max"]', "80000")

            print("✅ [SMOKE] Questionário preenchido com sucesso")

            # =================
            # 🔍 PASSO 3: Submeter busca
            # =================
            print("🔍 [SMOKE] Passo 3: Submetendo busca...")

            # Clicar no botão de buscar (pode ter textos diferentes)
            buscar_button_selectors = [
                'button:has-text("Buscar Carros")',
                'button:has-text("Encontrar Carros")',
                'button:has-text("Buscar")',
                'button[type="submit"]',
            ]

            buscar_clicked = False
            for selector in buscar_button_selectors:
                try:
                    page.click(selector, timeout=2000)
                    buscar_clicked = True
                    print(f"  ✅ [SMOKE] Clicou em buscar usando: {selector}")
                    break
                except:
                    continue

            if not buscar_clicked:
                raise Exception("❌ [SMOKE] Não conseguiu encontrar botão de buscar")

            # =================
            # 📊 PASSO 4: Validar resultados
            # =================
            print("📊 [SMOKE] Passo 4: Validando resultados...")

            # Aguardar modal de resultados aparecer
            page.wait_for_selector("#resultadosModal", state="visible", timeout=30000)
            print("  ✅ [SMOKE] Modal de resultados apareceu")

            # Validar conteúdo do modal
            page.wait_for_selector("#resultadosContent", state="visible", timeout=10000)

            # Verificar se há conteúdo (texto ou cards)
            modal_content = page.locator("#resultadosContent").inner_text()

            if len(modal_content.strip()) == 0:
                # Se não há texto, verificar se há cards/elementos visuais
                cards = page.locator("#resultadosContent .card").count()
                if cards == 0:
                    # Última tentativa: verificar qualquer elemento filho
                    children = page.locator("#resultadosContent > *").count()
                    if children == 0:
                        raise Exception("❌ [SMOKE] Modal de resultados está vazio")
                    print(f"  ✅ [SMOKE] Modal contém {children} elementos")
                else:
                    print(f"  ✅ [SMOKE] Modal contém {cards} cards de resultados")
            else:
                print(
                    f"  ✅ [SMOKE] Modal contém conteúdo (primeiros 100 chars): {modal_content[:100]}"
                )

            print("✅ [SMOKE] Resultados validados com sucesso")

            # =================
            # 🎉 SUCESSO TOTAL
            # =================
            print("🎉 [SMOKE] TESTE SMOKE PASSOU COM SUCESSO!")
            print("✅ [SMOKE] Fluxo crítico funcionando perfeitamente")

        except Exception as e:
            print(f"❌ [SMOKE] FALHA CRÍTICA: {str(e)}")

            # Capturar informações de debug
            try:
                # Screenshot para debug
                page.screenshot(path="smoke_test_failure.png", full_page=True)
                print("📸 [SMOKE] Screenshot salvo: smoke_test_failure.png")

                # Log do HTML atual
                current_url = page.url
                print(f"🌐 [SMOKE] URL atual: {current_url}")

                # Verificar se algum step está visível
                for i in range(1, 9):
                    try:
                        step_visible = page.locator(f"#step{i}").is_visible()
                        if step_visible:
                            print(f"👁️ [SMOKE] Step {i} ainda visível")
                    except:
                        pass

            except Exception as debug_error:
                print(f"⚠️ [SMOKE] Erro ao capturar debug info: {debug_error}")

            # Re-raise para falhar o teste
            raise e

    def _safe_click(self, page: Page, selector: str, timeout: int = 10000) -> None:
        """
        Clique seguro com retry e validação

        Args:
            page: Página do Playwright
            selector: Seletor CSS
            timeout: Timeout em milissegundos
        """
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # Aguardar elemento estar visível e habilitado
                page.wait_for_selector(selector, state="visible", timeout=timeout)

                # Aguardar um pouco para estabilizar
                import time

                time.sleep(0.5)

                # Tentar clicar
                page.click(selector)
                return

            except Exception as e:
                if attempt == max_retries - 1:
                    print(
                        f"❌ [SMOKE] Falha ao clicar em '{selector}' após {max_retries} tentativas: {e}"
                    )
                    raise e
                else:
                    print(
                        f"⚠️ [SMOKE] Tentativa {attempt + 1} falhou para '{selector}', tentando novamente..."
                    )
                    import time

                    time.sleep(1)

    def _safe_fill(
        self, page: Page, selector: str, value: str, timeout: int = 10000
    ) -> None:
        """
        Preenchimento seguro com retry

        Args:
            page: Página do Playwright
            selector: Seletor CSS
            value: Valor a preencher
            timeout: Timeout em milissegundos
        """
        try:
            page.wait_for_selector(selector, state="visible", timeout=timeout)
            page.fill(selector, value)
        except Exception as e:
            print(f"❌ [SMOKE] Falha ao preencher '{selector}' com '{value}': {e}")
            raise e
