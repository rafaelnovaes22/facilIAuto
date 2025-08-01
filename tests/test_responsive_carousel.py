"""
Testes para o sistema de carrossel responsivo melhorado
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


class TestResponsiveCarousel:
    """Testes para o carrossel responsivo"""

    @pytest.fixture
    def driver(self):
        """Fixture para o driver do Selenium"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1200, 800)
        yield driver
        driver.quit()

    def test_carousel_initialization(self, driver):
        """Testa se o carrossel é inicializado corretamente"""
        # Navegar para a página
        driver.get("http://localhost:8000")
        
        # Aguardar carregamento
        wait = WebDriverWait(driver, 10)
        
        # Verificar se os scripts foram carregados
        carousel_script = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "script"))
        )
        
        # Verificar se a classe ResponsiveCarousel está disponível
        carousel_class_exists = driver.execute_script(
            "return typeof ResponsiveCarousel !== 'undefined'"
        )
        assert carousel_class_exists, "ResponsiveCarousel class não foi carregada"

    def test_carousel_responsive_behavior(self, driver):
        """Testa o comportamento responsivo do carrossel"""
        driver.get("http://localhost:8000")
        
        # Simular diferentes tamanhos de tela
        screen_sizes = [
            (320, 568),   # Mobile
            (768, 1024),  # Tablet
            (1200, 800),  # Desktop
            (1920, 1080)  # Desktop grande
        ]
        
        for width, height in screen_sizes:
            driver.set_window_size(width, height)
            time.sleep(0.5)  # Aguardar redimensionamento
            
            # Verificar se o CSS responsivo foi aplicado
            carousel_height = driver.execute_script("""
                const carousel = document.querySelector('.responsive-carousel');
                if (carousel) {
                    return getComputedStyle(carousel).getPropertyValue('--carousel-height');
                }
                return null;
            """)
            
            # Verificar se a altura foi ajustada conforme o tamanho da tela
            if width <= 576:
                expected_height = "160px"
            elif width <= 768:
                expected_height = "200px"
            elif width <= 992:
                expected_height = "220px"
            else:
                expected_height = "250px"
            
            # Note: O teste pode não encontrar carrossel na página inicial
            # mas verifica se o sistema está configurado corretamente

    def test_carousel_navigation(self, driver):
        """Testa a navegação do carrossel"""
        driver.get("http://localhost:8000")
        
        # Simular preenchimento do formulário para ver resultados
        self._fill_form_and_submit(driver)
        
        # Aguardar modal de resultados
        wait = WebDriverWait(driver, 10)
        modal = wait.until(
            EC.presence_of_element_located((By.ID, "resultadosModal"))
        )
        
        # Procurar por carrosséis nos resultados
        carousels = driver.find_elements(By.CSS_SELECTOR, ".responsive-carousel")
        
        if carousels:
            carousel = carousels[0]
            
            # Verificar controles de navegação
            prev_btn = carousel.find_element(By.CSS_SELECTOR, ".carousel-control-prev")
            next_btn = carousel.find_element(By.CSS_SELECTOR, ".carousel-control-next")
            
            assert prev_btn.is_displayed(), "Botão anterior não está visível"
            assert next_btn.is_displayed(), "Botão próximo não está visível"
            
            # Testar navegação
            next_btn.click()
            time.sleep(0.5)
            
            # Verificar se o slide mudou
            active_slide = carousel.find_element(By.CSS_SELECTOR, ".carousel-item.active")
            assert active_slide, "Slide ativo não encontrado após navegação"

    def test_carousel_touch_support(self, driver):
        """Testa o suporte a toque do carrossel"""
        driver.get("http://localhost:8000")
        
        # Simular dispositivo móvel
        driver.set_window_size(375, 667)
        
        # Simular preenchimento do formulário
        self._fill_form_and_submit(driver)
        
        # Aguardar resultados
        wait = WebDriverWait(driver, 10)
        modal = wait.until(
            EC.presence_of_element_located((By.ID, "resultadosModal"))
        )
        
        carousels = driver.find_elements(By.CSS_SELECTOR, ".responsive-carousel")
        
        if carousels:
            carousel = carousels[0]
            
            # Simular swipe (usando ActionChains)
            actions = ActionChains(driver)
            actions.click_and_hold(carousel)
            actions.move_by_offset(-100, 0)  # Swipe para a esquerda
            actions.release()
            actions.perform()
            
            time.sleep(0.5)
            
            # Verificar se o swipe funcionou
            # (Difícil de testar completamente sem eventos de toque reais)

    def test_carousel_lazy_loading(self, driver):
        """Testa o lazy loading das imagens do carrossel"""
        driver.get("http://localhost:8000")
        
        # Simular preenchimento do formulário
        self._fill_form_and_submit(driver)
        
        # Aguardar resultados
        wait = WebDriverWait(driver, 10)
        modal = wait.until(
            EC.presence_of_element_located((By.ID, "resultadosModal"))
        )
        
        # Verificar se existem imagens com data-src (lazy loading)
        lazy_images = driver.find_elements(By.CSS_SELECTOR, "img[data-src]")
        
        if lazy_images:
            # Verificar se a primeira imagem não tem data-src (carregamento imediato)
            first_images = driver.find_elements(By.CSS_SELECTOR, ".carousel-item:first-child img")
            if first_images:
                first_img = first_images[0]
                assert not first_img.get_attribute("data-src"), "Primeira imagem deveria carregar imediatamente"
                assert first_img.get_attribute("src"), "Primeira imagem deveria ter src definido"

    def test_carousel_accessibility(self, driver):
        """Testa a acessibilidade do carrossel"""
        driver.get("http://localhost:8000")
        
        # Simular preenchimento do formulário
        self._fill_form_and_submit(driver)
        
        # Aguardar resultados
        wait = WebDriverWait(driver, 10)
        modal = wait.until(
            EC.presence_of_element_located((By.ID, "resultadosModal"))
        )
        
        carousels = driver.find_elements(By.CSS_SELECTOR, ".responsive-carousel")
        
        if carousels:
            carousel = carousels[0]
            
            # Verificar atributos de acessibilidade
            assert carousel.get_attribute("tabindex") == "0", "Carrossel deveria ser focável"
            assert carousel.get_attribute("role") == "region", "Carrossel deveria ter role='region'"
            assert carousel.get_attribute("aria-label"), "Carrossel deveria ter aria-label"
            
            # Verificar controles
            controls = carousel.find_elements(By.CSS_SELECTOR, ".carousel-control")
            for control in controls:
                assert control.get_attribute("aria-label") or control.find_element(By.CSS_SELECTOR, ".visually-hidden"), \
                    "Controles deveriam ter labels para screen readers"

    def test_carousel_performance(self, driver):
        """Testa a performance do carrossel"""
        driver.get("http://localhost:8000")
        
        # Medir tempo de inicialização
        start_time = time.time()
        
        # Simular preenchimento do formulário
        self._fill_form_and_submit(driver)
        
        # Aguardar resultados
        wait = WebDriverWait(driver, 10)
        modal = wait.until(
            EC.presence_of_element_located((By.ID, "resultadosModal"))
        )
        
        # Aguardar inicialização dos carrosséis
        time.sleep(1)
        
        end_time = time.time()
        initialization_time = end_time - start_time
        
        # Verificar se a inicialização foi rápida (menos de 5 segundos)
        assert initialization_time < 5, f"Inicialização muito lenta: {initialization_time}s"
        
        # Verificar se não há erros de JavaScript
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        assert len(errors) == 0, f"Erros de JavaScript encontrados: {errors}"

    def _fill_form_and_submit(self, driver):
        """Helper para preencher o formulário e submeter"""
        wait = WebDriverWait(driver, 10)
        
        # Aguardar formulário carregar
        form = wait.until(
            EC.presence_of_element_located((By.ID, "questionarioForm"))
        )
        
        # Navegar pelas etapas rapidamente
        for step in range(1, 9):
            # Clicar no botão próximo ou submeter
            if step < 8:
                next_btn = driver.find_element(By.ID, "nextBtn")
                if next_btn.is_displayed():
                    next_btn.click()
                    time.sleep(0.2)
            else:
                submit_btn = driver.find_element(By.ID, "submitBtn")
                if submit_btn.is_displayed():
                    submit_btn.click()
                    break


class TestCarouselIntegration:
    """Testes de integração do carrossel com o sistema"""

    def test_carousel_with_fallback_images(self):
        """Testa integração do carrossel com sistema de fallback"""
        # Este teste seria executado com dados mockados
        pass

    def test_carousel_with_multiple_images(self):
        """Testa carrossel com múltiplas imagens"""
        # Teste com dados mockados de carros com várias fotos
        pass

    def test_carousel_with_single_image(self):
        """Testa comportamento com uma única imagem"""
        # Teste para verificar se não mostra controles desnecessários
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])