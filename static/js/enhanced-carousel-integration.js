/**
 * Enhanced Carousel Integration for FacilIAuto
 * Integrates responsive carousel with image fallback system
 */

class EnhancedCarouselIntegration {
    constructor() {
        this.carousels = new Map();
        this.imageObserver = null;
        this.setupIntersectionObserver();
    }

    /**
     * Configura Intersection Observer para lazy loading
     */
    setupIntersectionObserver() {
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadImage(entry.target);
                        this.imageObserver.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.1
            });
        }
    }

    /**
     * Carrega uma imagem com lazy loading
     */
    loadImage(img) {
        const dataSrc = img.getAttribute('data-src');
        if (dataSrc && !img.src) {
            img.src = dataSrc;
            img.removeAttribute('data-src');

            // Adicionar classe de carregamento
            const container = img.closest('.car-image');
            if (container) {
                container.classList.add('loading');
            }
        }
    }

    /**
     * Inicializa carrosséis melhorados
     */
    initializeEnhancedCarousels() {
        const carouselElements = document.querySelectorAll('[data-carousel="responsive"]');

        carouselElements.forEach(element => {
            if (!this.carousels.has(element.id)) {
                const carousel = new ResponsiveCarousel(element, {
                    autoplay: element.dataset.autoplay === 'true',
                    autoplayInterval: parseInt(element.dataset.interval) || 5000,
                    showIndicators: element.dataset.indicators !== 'false',
                    showControls: element.dataset.controls !== 'false',
                    pauseOnHover: element.dataset.pauseOnHover !== 'false',
                    swipeEnabled: element.dataset.swipe !== 'false',
                    lazy: element.dataset.lazy !== 'false'
                });

                // Armazenar referência
                this.carousels.set(element.id, carousel);
                element.carouselInstance = carousel;

                // Configurar lazy loading para imagens do carrossel
                this.setupCarouselLazyLoading(element, carousel);

                // Configurar eventos personalizados
                this.setupCarouselEvents(element, carousel);
            }
        });
    }

    /**
     * Configura lazy loading específico para carrossel
     */
    setupCarouselLazyLoading(element, carousel) {
        const images = element.querySelectorAll('img[data-src]');

        images.forEach(img => {
            if (this.imageObserver) {
                this.imageObserver.observe(img);
            }
        });

        // Pré-carregar próxima imagem quando slide muda
        element.addEventListener('slideChange', (e) => {
            const { currentSlide } = e.detail;
            const nextSlideIndex = (currentSlide + 1) % carousel.slides.length;
            const nextSlide = carousel.slides[nextSlideIndex];

            if (nextSlide) {
                const nextImg = nextSlide.querySelector('img[data-src]');
                if (nextImg) {
                    this.loadImage(nextImg);
                }
            }
        });
    }

    /**
     * Configura eventos personalizados do carrossel
     */
    setupCarouselEvents(element, carousel) {
        // Evento de mudança de slide
        element.addEventListener('slideChange', (e) => {
            const { currentSlide, totalSlides } = e.detail;

            // Emitir evento personalizado para analytics
            this.trackCarouselInteraction(element.id, currentSlide, totalSlides);

            // Atualizar acessibilidade
            this.updateAccessibility(element, currentSlide, totalSlides);
        });

        // Eventos de toque/swipe
        element.addEventListener('touchstart', (e) => {
            this.handleTouchStart(e, element);
        }, { passive: true });

        element.addEventListener('touchend', (e) => {
            this.handleTouchEnd(e, element);
        }, { passive: true });
    }

    /**
     * Atualiza acessibilidade do carrossel
     */
    updateAccessibility(element, currentSlide, totalSlides) {
        // Atualizar aria-label
        element.setAttribute('aria-label', `Imagem ${currentSlide + 1} de ${totalSlides}`);

        // Atualizar slides para screen readers
        const slides = element.querySelectorAll('.carousel-item');
        slides.forEach((slide, index) => {
            slide.setAttribute('aria-hidden', index !== currentSlide);
        });
    }

    /**
     * Rastreia interações do carrossel
     */
    trackCarouselInteraction(carouselId, currentSlide, totalSlides) {
        // Implementar analytics se necessário
        console.log(`Carousel ${carouselId}: slide ${currentSlide + 1}/${totalSlides}`);
    }

    /**
     * Manipula início do toque
     */
    handleTouchStart(e, element) {
        const carousel = this.carousels.get(element.id);
        if (carousel && carousel.options.autoplay) {
            carousel.pauseAutoplay();
        }
    }

    /**
     * Manipula fim do toque
     */
    handleTouchEnd(e, element) {
        const carousel = this.carousels.get(element.id);
        if (carousel && carousel.options.autoplay) {
            // Retomar autoplay após 3 segundos
            setTimeout(() => {
                carousel.resumeAutoplay();
            }, 3000);
        }
    }

    /**
     * Otimiza performance dos carrosséis
     */
    optimizePerformance() {
        // Pausar carrosséis não visíveis
        if ('IntersectionObserver' in window) {
            const carouselObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const carousel = this.carousels.get(entry.target.id);
                    if (carousel) {
                        if (entry.isIntersecting) {
                            carousel.resumeAutoplay();
                        } else {
                            carousel.pauseAutoplay();
                        }
                    }
                });
            }, {
                threshold: 0.1
            });

            this.carousels.forEach((carousel, id) => {
                const element = document.getElementById(id);
                if (element) {
                    carouselObserver.observe(element);
                }
            });
        }
    }

    /**
     * Adiciona suporte a teclado melhorado
     */
    enhanceKeyboardSupport() {
        this.carousels.forEach((carousel, id) => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('keydown', (e) => {
                    switch (e.key) {
                        case 'ArrowLeft':
                        case 'ArrowUp':
                            e.preventDefault();
                            carousel.previousSlide();
                            break;
                        case 'ArrowRight':
                        case 'ArrowDown':
                            e.preventDefault();
                            carousel.nextSlide();
                            break;
                        case 'Home':
                            e.preventDefault();
                            carousel.goToSlide(0);
                            break;
                        case 'End':
                            e.preventDefault();
                            carousel.goToSlide(carousel.slides.length - 1);
                            break;
                        case ' ':
                        case 'Enter':
                            e.preventDefault();
                            carousel.toggleAutoplay();
                            break;
                    }
                });

                // Tornar focável
                element.setAttribute('tabindex', '0');
                element.setAttribute('role', 'region');
                element.setAttribute('aria-label', 'Galeria de imagens do veículo');
            }
        });
    }

    /**
     * Adiciona indicadores de progresso
     */
    addProgressIndicators() {
        this.carousels.forEach((carousel, id) => {
            const element = document.getElementById(id);
            if (element && carousel.options.autoplay) {
                const progressBar = document.createElement('div');
                progressBar.className = 'carousel-progress';
                progressBar.innerHTML = '<div class="carousel-progress-bar"></div>';

                element.appendChild(progressBar);

                // Animar barra de progresso
                element.addEventListener('slideChange', () => {
                    const bar = progressBar.querySelector('.carousel-progress-bar');
                    bar.style.animation = 'none';
                    setTimeout(() => {
                        bar.style.animation = `carousel-progress ${carousel.options.autoplayInterval}ms linear`;
                    }, 10);
                });
            }
        });
    }

    /**
     * Inicializa todas as funcionalidades
     */
    init() {
        // Aguardar carregamento do DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeAll();
            });
        } else {
            this.initializeAll();
        }
    }

    /**
     * Inicializa todas as funcionalidades
     */
    initializeAll() {
        this.initializeEnhancedCarousels();
        this.optimizePerformance();
        this.enhanceKeyboardSupport();
        this.addProgressIndicators();

        console.log('🎠 Enhanced Carousel Integration inicializado');
    }

    /**
     * Destrói todas as instâncias
     */
    destroy() {
        this.carousels.forEach(carousel => {
            carousel.destroy();
        });
        this.carousels.clear();

        if (this.imageObserver) {
            this.imageObserver.disconnect();
        }
    }
}

// CSS adicional para funcionalidades avançadas
const enhancedCarouselCSS = `
    /* Barra de progresso do autoplay */
    .carousel-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: rgba(255, 255, 255, 0.3);
        z-index: 15;
    }
    
    .carousel-progress-bar {
        height: 100%;
        background: #007bff;
        width: 0;
    }
    
    @keyframes carousel-progress {
        from { width: 0; }
        to { width: 100%; }
    }
    
    /* Melhorias de acessibilidade */
    .responsive-carousel:focus {
        outline: 2px solid #007bff;
        outline-offset: 2px;
    }
    
    .responsive-carousel[aria-label] {
        position: relative;
    }
    
    /* Indicadores melhorados */
    .responsive-carousel .carousel-indicators {
        padding: 5px 10px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
    }
    
    /* Controles com melhor contraste */
    .responsive-carousel .carousel-control:focus {
        outline: 2px solid #fff;
        outline-offset: 2px;
    }
    
    /* Animações suaves para mudanças de tamanho */
    .responsive-carousel {
        transition: height 0.3s ease;
    }
    
    /* Estados de carregamento melhorados */
    .carousel-item.loading {
        position: relative;
    }
    
    .carousel-item.loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 30px;
        height: 30px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-top: 3px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        z-index: 10;
    }
    
    @keyframes spin {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }
`;

// Adicionar CSS ao documento
function addEnhancedCarouselCSS() {
    const style = document.createElement('style');
    style.textContent = enhancedCarouselCSS;
    document.head.appendChild(style);
}

// Instância global
const enhancedCarouselIntegration = new EnhancedCarouselIntegration();

// Inicializar
addEnhancedCarouselCSS();
enhancedCarouselIntegration.init();

// Exportar para uso global
window.EnhancedCarouselIntegration = EnhancedCarouselIntegration;
window.enhancedCarouselIntegration = enhancedCarouselIntegration;