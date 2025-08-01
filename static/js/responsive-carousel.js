/**
 * Sistema de carrossel responsivo melhorado para o FacilIAuto
 * Inclui navegação por toque, indicadores, autoplay e responsividade
 */

class ResponsiveCarousel {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            autoplay: options.autoplay || false,
            autoplayInterval: options.autoplayInterval || 5000,
            showIndicators: options.showIndicators !== false,
            showControls: options.showControls !== false,
            pauseOnHover: options.pauseOnHover !== false,
            swipeEnabled: options.swipeEnabled !== false,
            lazy: options.lazy !== false,
            ...options
        };

        this.currentSlide = 0;
        this.slides = [];
        this.isPlaying = false;
        this.autoplayTimer = null;
        this.touchStartX = 0;
        this.touchEndX = 0;

        this.init();
    }

    init() {
        this.setupCarousel();
        this.setupControls();
        this.setupIndicators();
        this.setupTouchEvents();
        this.setupKeyboardEvents();
        this.setupAutoplay();
        this.setupResponsive();

        // Inicializar com primeira imagem
        this.goToSlide(0);
    }

    setupCarousel() {
        this.container.classList.add('responsive-carousel');

        // Encontrar slides existentes ou criar estrutura
        const existingSlides = this.container.querySelectorAll('.carousel-item');
        if (existingSlides.length > 0) {
            this.slides = Array.from(existingSlides);
        } else {
            // Criar slides a partir de imagens
            const images = this.container.querySelectorAll('img');
            images.forEach((img, index) => {
                const slide = document.createElement('div');
                slide.className = `carousel-item ${index === 0 ? 'active' : ''}`;
                slide.appendChild(img.cloneNode(true));
                this.slides.push(slide);
            });
        }

        // Criar estrutura do carrossel
        const carouselInner = this.container.querySelector('.carousel-inner') ||
            document.createElement('div');
        carouselInner.className = 'carousel-inner';
        carouselInner.innerHTML = '';

        this.slides.forEach(slide => {
            carouselInner.appendChild(slide);
        });

        this.container.innerHTML = '';
        this.container.appendChild(carouselInner);
        this.carouselInner = carouselInner;
    }

    setupControls() {
        if (!this.options.showControls || this.slides.length <= 1) return;

        // Botão anterior
        const prevBtn = document.createElement('button');
        prevBtn.className = 'carousel-control carousel-control-prev';
        prevBtn.innerHTML = `
            <span class="carousel-control-prev-icon">
                <i class="fas fa-chevron-left"></i>
            </span>
            <span class="visually-hidden">Anterior</span>
        `;
        prevBtn.addEventListener('click', () => this.previousSlide());

        // Botão próximo
        const nextBtn = document.createElement('button');
        nextBtn.className = 'carousel-control carousel-control-next';
        nextBtn.innerHTML = `
            <span class="carousel-control-next-icon">
                <i class="fas fa-chevron-right"></i>
            </span>
            <span class="visually-hidden">Próximo</span>
        `;
        nextBtn.addEventListener('click', () => this.nextSlide());

        this.container.appendChild(prevBtn);
        this.container.appendChild(nextBtn);

        this.prevBtn = prevBtn;
        this.nextBtn = nextBtn;
    }

    setupIndicators() {
        if (!this.options.showIndicators || this.slides.length <= 1) return;

        const indicators = document.createElement('div');
        indicators.className = 'carousel-indicators';

        this.slides.forEach((_, index) => {
            const indicator = document.createElement('button');
            indicator.className = `carousel-indicator ${index === 0 ? 'active' : ''}`;
            indicator.setAttribute('data-slide', index);
            indicator.innerHTML = `<span class="visually-hidden">Slide ${index + 1}</span>`;
            indicator.addEventListener('click', () => this.goToSlide(index));
            indicators.appendChild(indicator);
        });

        this.container.appendChild(indicators);
        this.indicators = indicators.querySelectorAll('.carousel-indicator');
    }

    setupTouchEvents() {
        if (!this.options.swipeEnabled) return;

        this.container.addEventListener('touchstart', (e) => {
            this.touchStartX = e.touches[0].clientX;
        }, { passive: true });

        this.container.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].clientX;
            this.handleSwipe();
        }, { passive: true });

        // Suporte para mouse drag
        let isDragging = false;

        this.container.addEventListener('mousedown', (e) => {
            isDragging = true;
            this.touchStartX = e.clientX;
            this.container.style.cursor = 'grabbing';
        });

        this.container.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            e.preventDefault();
        });

        this.container.addEventListener('mouseup', (e) => {
            if (!isDragging) return;
            isDragging = false;
            this.touchEndX = e.clientX;
            this.handleSwipe();
            this.container.style.cursor = '';
        });

        this.container.addEventListener('mouseleave', () => {
            isDragging = false;
            this.container.style.cursor = '';
        });
    }

    handleSwipe() {
        const swipeThreshold = 50;
        const diff = this.touchStartX - this.touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                this.nextSlide();
            } else {
                this.previousSlide();
            }
        }
    }

    setupKeyboardEvents() {
        this.container.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previousSlide();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.nextSlide();
                    break;
                case ' ':
                    e.preventDefault();
                    this.toggleAutoplay();
                    break;
            }
        });

        // Tornar o container focável
        this.container.setAttribute('tabindex', '0');
    }

    setupAutoplay() {
        if (!this.options.autoplay) return;

        if (this.options.pauseOnHover) {
            this.container.addEventListener('mouseenter', () => this.pauseAutoplay());
            this.container.addEventListener('mouseleave', () => this.resumeAutoplay());
        }

        this.startAutoplay();
    }

    setupResponsive() {
        // Observer para mudanças de tamanho
        if (window.ResizeObserver) {
            const resizeObserver = new ResizeObserver(() => {
                this.updateLayout();
            });
            resizeObserver.observe(this.container);
        } else {
            window.addEventListener('resize', () => this.updateLayout());
        }

        // Configuração inicial
        this.updateLayout();
    }

    updateLayout() {
        // Atualizar layout responsivo
        const containerWidth = this.container.offsetWidth;
        const containerHeight = this.container.offsetHeight;

        // Ajustar altura baseada na largura e contexto
        if (containerWidth < 576) {
            // Mobile - altura melhorada
            this.container.style.setProperty('--carousel-height', '280px');
            this.adjustControlsForMobile();
        } else if (containerWidth < 768) {
            // Tablet - altura melhorada
            this.container.style.setProperty('--carousel-height', '320px');
            this.adjustControlsForTablet();
        } else if (containerWidth < 992) {
            // Desktop pequeno - altura melhorada
            this.container.style.setProperty('--carousel-height', '380px');
            this.adjustControlsForDesktop();
        } else {
            // Desktop grande - altura melhorada
            this.container.style.setProperty('--carousel-height', '420px');
            this.adjustControlsForDesktop();
        }

        // Ajustar aspect ratio se necessário
        this.maintainAspectRatio();
    }

    adjustControlsForMobile() {
        const controls = this.container.querySelectorAll('.carousel-control');
        controls.forEach(control => {
            control.style.width = '32px';
            control.style.height = '32px';
            control.style.fontSize = '12px';
        });

        const indicators = this.container.querySelectorAll('.carousel-indicator');
        indicators.forEach(indicator => {
            indicator.style.width = '6px';
            indicator.style.height = '6px';
        });
    }

    adjustControlsForTablet() {
        const controls = this.container.querySelectorAll('.carousel-control');
        controls.forEach(control => {
            control.style.width = '36px';
            control.style.height = '36px';
            control.style.fontSize = '14px';
        });

        const indicators = this.container.querySelectorAll('.carousel-indicator');
        indicators.forEach(indicator => {
            indicator.style.width = '8px';
            indicator.style.height = '8px';
        });
    }

    adjustControlsForDesktop() {
        const controls = this.container.querySelectorAll('.carousel-control');
        controls.forEach(control => {
            control.style.width = '40px';
            control.style.height = '40px';
            control.style.fontSize = '16px';
        });

        const indicators = this.container.querySelectorAll('.carousel-indicator');
        indicators.forEach(indicator => {
            indicator.style.width = '10px';
            indicator.style.height = '10px';
        });
    }

    maintainAspectRatio() {
        // Manter aspect ratio 4:3 para consistência visual
        const width = this.container.offsetWidth;
        const idealHeight = Math.floor(width * 0.75);
        const maxHeight = parseInt(this.container.style.getPropertyValue('--carousel-height')) || 250;

        if (idealHeight < maxHeight) {
            this.container.style.setProperty('--carousel-height', `${idealHeight}px`);
        }
    }

    goToSlide(index) {
        if (index < 0 || index >= this.slides.length) return;

        // Remover classe active de todos os slides
        this.slides.forEach(slide => slide.classList.remove('active'));

        // Ativar slide atual
        this.slides[index].classList.add('active');
        this.currentSlide = index;

        // Atualizar indicadores
        if (this.indicators) {
            this.indicators.forEach(indicator => indicator.classList.remove('active'));
            this.indicators[index].classList.add('active');
        }

        // Lazy loading da próxima imagem
        if (this.options.lazy) {
            this.lazyLoadNextImage();
        }

        // Emitir evento personalizado
        this.container.dispatchEvent(new CustomEvent('slideChange', {
            detail: { currentSlide: index, totalSlides: this.slides.length }
        }));
    }

    nextSlide() {
        const nextIndex = (this.currentSlide + 1) % this.slides.length;
        this.goToSlide(nextIndex);
    }

    previousSlide() {
        const prevIndex = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
        this.goToSlide(prevIndex);
    }

    startAutoplay() {
        if (this.slides.length <= 1) return;

        this.isPlaying = true;
        this.autoplayTimer = setInterval(() => {
            this.nextSlide();
        }, this.options.autoplayInterval);
    }

    pauseAutoplay() {
        this.isPlaying = false;
        if (this.autoplayTimer) {
            clearInterval(this.autoplayTimer);
            this.autoplayTimer = null;
        }
    }

    resumeAutoplay() {
        if (this.options.autoplay && !this.isPlaying) {
            this.startAutoplay();
        }
    }

    toggleAutoplay() {
        if (this.isPlaying) {
            this.pauseAutoplay();
        } else {
            this.resumeAutoplay();
        }
    }

    lazyLoadNextImage() {
        const nextIndex = (this.currentSlide + 1) % this.slides.length;
        const nextSlide = this.slides[nextIndex];
        const img = nextSlide.querySelector('img[data-src]');

        if (img && !img.src) {
            img.src = img.getAttribute('data-src');
            img.removeAttribute('data-src');
        }
    }

    destroy() {
        if (this.autoplayTimer) {
            clearInterval(this.autoplayTimer);
        }

        // Remover event listeners
        this.container.removeEventListener('touchstart', this.handleTouchStart);
        this.container.removeEventListener('touchend', this.handleTouchEnd);

        // Limpar referências
        this.container = null;
        this.slides = null;
        this.indicators = null;
    }
}

// CSS para o carrossel responsivo
const carouselCSS = `
    .responsive-carousel {
        position: relative;
        width: 100%;
        height: var(--carousel-height, 350px);
        overflow: hidden;
        border-radius: 10px;
        background: #f8f9fa;
        cursor: grab;
    }
    
    .responsive-carousel:active {
        cursor: grabbing;
    }
    
    .responsive-carousel .carousel-inner {
        position: relative;
        width: 100%;
        height: 100%;
    }
    
    .responsive-carousel .carousel-item {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        transition: opacity 0.5s ease-in-out;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .responsive-carousel .carousel-item.active {
        opacity: 1;
    }
    
    .responsive-carousel .carousel-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 10px;
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
        image-rendering: optimize-quality;
        filter: contrast(1.05) saturate(1.1);
    }
    
    .responsive-carousel .carousel-control {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        width: 40px;
        height: 40px;
        background: rgba(0, 0, 0, 0.6);
        border: none;
        border-radius: 50%;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        z-index: 10;
        opacity: 0.8;
    }
    
    .responsive-carousel .carousel-control:hover {
        background: rgba(0, 0, 0, 0.8);
        opacity: 1;
        transform: translateY(-50%) scale(1.1);
    }
    
    .responsive-carousel .carousel-control-prev {
        left: 10px;
    }
    
    .responsive-carousel .carousel-control-next {
        right: 10px;
    }
    
    .responsive-carousel .carousel-indicators {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 8px;
        z-index: 10;
    }
    
    .responsive-carousel .carousel-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        border: 2px solid rgba(255, 255, 255, 0.5);
        background: transparent;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .responsive-carousel .carousel-indicator.active {
        background: white;
        border-color: white;
    }
    
    .responsive-carousel .carousel-indicator:hover {
        border-color: white;
        transform: scale(1.2);
    }
    
    /* Responsividade */
    @media (max-width: 576px) {
        .responsive-carousel {
            --carousel-height: 280px;
        }
        
        .responsive-carousel .carousel-control {
            width: 35px;
            height: 35px;
        }
        
        .responsive-carousel .carousel-control-prev {
            left: 5px;
        }
        
        .responsive-carousel .carousel-control-next {
            right: 5px;
        }
        
        .responsive-carousel .carousel-indicator {
            width: 8px;
            height: 8px;
        }
    }
    
    @media (max-width: 768px) {
        .responsive-carousel {
            --carousel-height: 320px;
        }
    }
    
    @media (min-width: 992px) {
        .responsive-carousel {
            --carousel-height: 420px;
        }
    }
    
    /* Animações de entrada */
    @keyframes slideInFromRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInFromLeft {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    /* Estados de carregamento */
    .responsive-carousel .carousel-item.loading {
        background: #f8f9fa;
    }
    
    .responsive-carousel .carousel-item.loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 40px;
        height: 40px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }
`;

// Função para inicializar carrosséis automaticamente
function initializeCarousels() {
    const carousels = document.querySelectorAll('[data-carousel="responsive"]');

    carousels.forEach(carousel => {
        const options = {
            autoplay: carousel.dataset.autoplay === 'true',
            autoplayInterval: parseInt(carousel.dataset.interval) || 5000,
            showIndicators: carousel.dataset.indicators !== 'false',
            showControls: carousel.dataset.controls !== 'false',
            pauseOnHover: carousel.dataset.pauseOnHover !== 'false',
            swipeEnabled: carousel.dataset.swipe !== 'false',
            lazy: carousel.dataset.lazy !== 'false'
        };

        new ResponsiveCarousel(carousel, options);
    });
}

// Adicionar CSS ao documento
function addCarouselCSS() {
    const style = document.createElement('style');
    style.textContent = carouselCSS;
    document.head.appendChild(style);
}

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        addCarouselCSS();
        initializeCarousels();
    });
} else {
    addCarouselCSS();
    initializeCarousels();
}

// Exportar para uso global
window.ResponsiveCarousel = ResponsiveCarousel;
window.initializeCarousels = initializeCarousels;