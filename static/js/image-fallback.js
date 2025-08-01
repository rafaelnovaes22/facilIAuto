/**
 * Sistema de fallback de imagens para o FacilIAuto
 * Trata erros de carregamento de imagem e fornece fallbacks apropriados
 */

class ImageFallbackSystem {
    constructor() {
        this.fallbackUrls = new Map();
        this.failedUrls = new Set();
        this.loadingImages = new Set();
        this.retryAttempts = new Map();
        this.maxRetries = 2;
        this.retryDelay = 1000; // 1 segundo

        // Estatísticas de uso
        this.stats = {
            totalRequests: 0,
            successfulLoads: 0,
            fallbacksUsed: 0,
            errorsEncountered: 0
        };

        // URLs de fallback de alta qualidade por categoria
        this.categoryFallbacks = {
            'hatch': [
                'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=600&h=450&fit=crop&crop=center&auto=format&q=85'
            ],
            'sedan': [
                'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=600&h=450&fit=crop&crop=center&auto=format&q=85'
            ],
            'suv_compacto': [
                'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=600&h=450&fit=crop&crop=center&auto=format&q=85'
            ],
            'suv_medio': [
                'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=600&h=450&fit=crop&crop=center&auto=format&q=85'
            ],
            'suv_premium': [
                'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=600&h=450&fit=crop&crop=center&auto=format&q=85'
            ],
            'pickup': [
                'https://images.unsplash.com/photo-1563720223185-11003d516935?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=600&h=450&fit=crop&crop=center&auto=format&q=85'
            ],
            'crossover': [
                'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1494976688153-c91c18894e15?w=600&h=450&fit=crop&crop=center&auto=format&q=85'
            ],
            'default': [
                'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=600&h=450&fit=crop&crop=center&auto=format&q=85',
                'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=600&h=450&fit=crop&crop=center&auto=format&q=85'
            ]
        };

        // Cores por marca para placeholders (expandido)
        this.brandColors = {
            'TOYOTA': '#CC0000',
            'HONDA': '#E60012',
            'VOLKSWAGEN': '#1E3A8A',
            'HYUNDAI': '#002C5F',
            'CHEVROLET': '#FCC200',
            'FORD': '#003478',
            'NISSAN': '#C3002F',
            'BMW': '#0066B2',
            'FIAT': '#8B0000',
            'JEEP': '#1B4332',
            'RENAULT': '#FFCC00',
            'KIA': '#05141F',
            'MITSUBISHI': '#E60012',
            'PEUGEOT': '#0066CC',
            'CAOA': '#FF6600',
            'AUDI': '#BB0A30',
            'MERCEDES': '#00ADEF'
        };
    }

    /**
     * Gera URLs de fallback baseadas na marca, modelo e categoria
     */
    generateFallback(marca, modelo, categoria = 'hatch', failedUrls = []) {
        const key = `${marca}-${modelo}-${categoria}`;

        // Obter opções de fallback por categoria
        const categoryOptions = this.categoryFallbacks[categoria] || this.categoryFallbacks['default'];

        // Filtrar URLs que já falharam
        const availableOptions = categoryOptions.filter(url => !failedUrls.includes(url) && !this.failedUrls.has(url));

        // Se ainda há opções disponíveis, usar a primeira
        if (availableOptions.length > 0) {
            return availableOptions[0];
        }

        // Se todas as opções da categoria falharam, usar placeholder personalizado
        const brandColor = this.brandColors[marca.toUpperCase()] || '#666666';
        const textColor = this.isDarkColor(brandColor) ? 'FFFFFF' : '000000';
        const placeholder = `https://via.placeholder.com/600x450/${brandColor.replace('#', '')}/${textColor}?text=${encodeURIComponent(marca + ' ' + modelo)}`;

        return placeholder;
    }

    /**
     * Obtém múltiplas opções de fallback
     */
    getFallbackOptions(marca, modelo, categoria = 'hatch') {
        const categoryOptions = this.categoryFallbacks[categoria] || this.categoryFallbacks['default'];
        const brandColor = this.brandColors[marca.toUpperCase()] || '#666666';
        const textColor = this.isDarkColor(brandColor) ? 'FFFFFF' : '000000';

        const options = [...categoryOptions];

        // Adicionar placeholder personalizado
        options.push(`https://via.placeholder.com/600x450/${brandColor.replace('#', '')}/${textColor}?text=${encodeURIComponent(marca + ' ' + modelo)}`);

        // Adicionar fallback final genérico
        options.push('https://via.placeholder.com/600x450/CCCCCC/666666?text=Sem+Imagem');

        return options;
    }

    /**
     * Verifica se uma cor é escura
     */
    isDarkColor(hexColor) {
        const hex = hexColor.replace('#', '');
        const r = parseInt(hex.substr(0, 2), 16);
        const g = parseInt(hex.substr(2, 2), 16);
        const b = parseInt(hex.substr(4, 2), 16);
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        return luminance < 0.5;
    }

    /**
     * Configura tratamento de erro robusto para uma imagem
     */
    setupImageErrorHandling(img, marca, modelo, categoria) {
        const container = img.closest('.car-image') || img.parentElement;
        const originalSrc = img.src;
        const imageKey = `${originalSrc}-${marca}-${modelo}`;

        // Atualizar estatísticas
        this.stats.totalRequests++;

        // Adicionar classes CSS se não existirem
        if (container && !container.classList.contains('car-image')) {
            container.classList.add('car-image');
        }

        // Inicializar contador de tentativas
        if (!this.retryAttempts.has(imageKey)) {
            this.retryAttempts.set(imageKey, 0);
        }

        // Evento de carregamento bem-sucedido
        img.onload = () => {
            this.loadingImages.delete(originalSrc);
            this.stats.successfulLoads++;

            if (container) {
                container.classList.remove('loading', 'error');
                container.classList.add('loaded');
            }

            img.style.opacity = '1';

            // Limpar contador de tentativas
            this.retryAttempts.delete(imageKey);

            console.log(`✅ Imagem carregada: ${img.src}`);

            // Emitir evento personalizado
            img.dispatchEvent(new CustomEvent('imageLoaded', {
                detail: { src: img.src, marca, modelo, categoria }
            }));
        };

        // Evento de erro de carregamento com retry logic
        img.onerror = () => {
            console.warn(`❌ Erro ao carregar imagem: ${img.src}`);
            this.failedUrls.add(img.src);
            this.loadingImages.delete(originalSrc);
            this.stats.errorsEncountered++;

            const currentAttempts = this.retryAttempts.get(imageKey) || 0;

            // Tentar retry se ainda não excedeu o limite
            if (currentAttempts < this.maxRetries && img.src === originalSrc) {
                this.retryAttempts.set(imageKey, currentAttempts + 1);

                console.log(`🔄 Tentativa ${currentAttempts + 1}/${this.maxRetries} para: ${originalSrc}`);

                setTimeout(() => {
                    img.src = originalSrc + (originalSrc.includes('?') ? '&' : '?') + `retry=${currentAttempts + 1}&t=${Date.now()}`;
                }, this.retryDelay * (currentAttempts + 1)); // Delay exponencial

                return;
            }

            // Se ainda não tentamos fallback ou retry falhou
            if (img.src === originalSrc || img.src.includes('retry=')) {
                const failedUrls = Array.from(this.failedUrls);
                const fallbackUrl = this.generateFallback(marca, modelo, categoria, failedUrls);

                console.log(`🔄 Tentando fallback: ${fallbackUrl}`);
                this.stats.fallbacksUsed++;

                img.src = fallbackUrl;
                return;
            }

            // Se o fallback também falhou, tentar próxima opção
            const fallbackOptions = this.getFallbackOptions(marca, modelo, categoria);
            const currentIndex = fallbackOptions.indexOf(img.src);

            if (currentIndex >= 0 && currentIndex < fallbackOptions.length - 1) {
                const nextFallback = fallbackOptions[currentIndex + 1];
                console.log(`🔄 Tentando próximo fallback: ${nextFallback}`);
                img.src = nextFallback;
                return;
            }

            // Todas as opções falharam, mostrar placeholder
            this.showErrorPlaceholder(img, marca, modelo, container);
        };

        // Mostrar estado de carregamento
        if (container) {
            container.classList.add('loading');
            this.showLoadingSpinner(container);
        }
        this.loadingImages.add(originalSrc);

        // Timeout para imagens que demoram muito
        setTimeout(() => {
            if (this.loadingImages.has(originalSrc)) {
                console.warn(`⏰ Timeout para imagem: ${originalSrc}`);
                img.onerror();
            }
        }, 15000); // 15 segundos
    }

    /**
     * Mostra spinner de carregamento
     */
    showLoadingSpinner(container) {
        let spinner = container.querySelector('.loading-spinner');
        if (!spinner) {
            spinner = document.createElement('div');
            spinner.className = 'loading-spinner position-absolute top-50 start-50 translate-middle';
            spinner.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
            `;
            container.appendChild(spinner);
        }
        spinner.style.display = 'block';
    }

    /**
     * Mostra placeholder de erro
     */
    showErrorPlaceholder(img, marca, modelo, container) {
        if (container) {
            container.classList.add('error');
            container.classList.remove('loading');

            // Criar placeholder se não existir
            let placeholder = container.querySelector('.error-placeholder');
            if (!placeholder) {
                placeholder = document.createElement('div');
                placeholder.className = 'error-placeholder';
                placeholder.innerHTML = `
                    <div class="text-center text-muted p-4">
                        <i class="fas fa-car fa-3x mb-3"></i>
                        <h6>${marca} ${modelo}</h6>
                        <small>Imagem indisponível</small>
                    </div>
                `;
                container.appendChild(placeholder);
            }

            img.style.display = 'none';
        }
    }

    /**
     * Cria elemento de imagem com fallback automático
     */
    createImageWithFallback(src, marca, modelo, categoria, className = '', style = '') {
        const container = document.createElement('div');
        container.className = 'car-image position-relative';

        const img = document.createElement('img');
        img.src = src;
        img.className = className;
        img.style.cssText = style;
        img.alt = `${marca} ${modelo}`;

        // Spinner de carregamento
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner position-absolute top-50 start-50 translate-middle';
        spinner.style.display = 'none';
        spinner.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        `;

        container.appendChild(img);
        container.appendChild(spinner);

        // Configurar tratamento de erro
        this.setupImageErrorHandling(img, marca, modelo, categoria);

        return container;
    }

    /**
     * Cria carrossel de imagens com fallback
     */
    createCarouselWithFallback(images, marca, modelo, categoria, carouselId) {
        const carousel = document.createElement('div');
        carousel.id = carouselId;
        carousel.className = 'carousel slide';
        carousel.setAttribute('data-bs-ride', 'carousel');

        // Inner do carrossel
        const carouselInner = document.createElement('div');
        carouselInner.className = 'carousel-inner';

        images.forEach((imageSrc, index) => {
            const carouselItem = document.createElement('div');
            carouselItem.className = `carousel-item ${index === 0 ? 'active' : ''}`;

            const imageContainer = this.createImageWithFallback(
                imageSrc,
                marca,
                modelo,
                categoria,
                'd-block w-100',
                'height: 350px; object-fit: cover; border-radius: 10px 10px 0 0;'
            );

            carouselItem.appendChild(imageContainer);
            carouselInner.appendChild(carouselItem);
        });

        carousel.appendChild(carouselInner);

        // Controles do carrossel (apenas se mais de uma imagem)
        if (images.length > 1) {
            const prevButton = document.createElement('button');
            prevButton.className = 'carousel-control-prev';
            prevButton.type = 'button';
            prevButton.setAttribute('data-bs-target', `#${carouselId}`);
            prevButton.setAttribute('data-bs-slide', 'prev');
            prevButton.innerHTML = '<span class="carousel-control-prev-icon"></span>';

            const nextButton = document.createElement('button');
            nextButton.className = 'carousel-control-next';
            nextButton.type = 'button';
            nextButton.setAttribute('data-bs-target', `#${carouselId}`);
            nextButton.setAttribute('data-bs-slide', 'next');
            nextButton.innerHTML = '<span class="carousel-control-next-icon"></span>';

            carousel.appendChild(prevButton);
            carousel.appendChild(nextButton);
        }

        return carousel;
    }

    /**
     * Processa todas as imagens em um container
     */
    processImagesInContainer(container) {
        const images = container.querySelectorAll('img[data-marca][data-modelo]');

        images.forEach(img => {
            const marca = img.getAttribute('data-marca');
            const modelo = img.getAttribute('data-modelo');
            const categoria = img.getAttribute('data-categoria') || 'hatch';

            this.setupImageErrorHandling(img, marca, modelo, categoria);
        });
    }

    /**
     * Obtém estatísticas de uso do sistema
     */
    getStats() {
        const totalRequests = this.stats.totalRequests;
        const successRate = totalRequests > 0 ? (this.stats.successfulLoads / totalRequests * 100).toFixed(2) : 0;
        const fallbackRate = totalRequests > 0 ? (this.stats.fallbacksUsed / totalRequests * 100).toFixed(2) : 0;

        return {
            totalRequests,
            successfulLoads: this.stats.successfulLoads,
            fallbacksUsed: this.stats.fallbacksUsed,
            errorsEncountered: this.stats.errorsEncountered,
            successRate: `${successRate}%`,
            fallbackRate: `${fallbackRate}%`,
            failedUrlsCount: this.failedUrls.size,
            cacheSize: this.fallbackUrls.size
        };
    }

    /**
     * Limpa cache e estatísticas
     */
    clearCache() {
        this.fallbackUrls.clear();
        this.failedUrls.clear();
        this.retryAttempts.clear();
        this.stats = {
            totalRequests: 0,
            successfulLoads: 0,
            fallbacksUsed: 0,
            errorsEncountered: 0
        };
        console.log('🧹 Cache e estatísticas limpos');
    }

    /**
     * Pré-carrega imagens de fallback para melhor performance
     */
    preloadFallbackImages() {
        const imagesToPreload = new Set();

        // Coletar todas as URLs de fallback únicas
        Object.values(this.categoryFallbacks).forEach(categoryUrls => {
            categoryUrls.forEach(url => imagesToPreload.add(url));
        });

        // Pré-carregar imagens
        imagesToPreload.forEach(url => {
            const img = new Image();
            img.src = url;
        });

        console.log(`🚀 Pré-carregadas ${imagesToPreload.size} imagens de fallback`);
    }

    /**
     * Integração com carrossel responsivo
     */
    integrateWithCarousel(carouselElement) {
        if (!carouselElement) return;

        // Escutar eventos do carrossel
        carouselElement.addEventListener('slide.bs.carousel', (event) => {
            const nextSlide = event.relatedTarget;
            const images = nextSlide.querySelectorAll('img[data-marca][data-modelo]');

            // Processar imagens do próximo slide
            images.forEach(img => {
                const marca = img.getAttribute('data-marca');
                const modelo = img.getAttribute('data-modelo');
                const categoria = img.getAttribute('data-categoria') || 'hatch';

                if (!img.complete || img.naturalHeight === 0) {
                    this.setupImageErrorHandling(img, marca, modelo, categoria);
                }
            });
        });

        console.log('🎠 Integração com carrossel configurada');
    }

    /**
     * Inicializa o sistema para toda a página
     */
    init() {
        // Processar imagens existentes
        this.processImagesInContainer(document);

        // Observer para novas imagens adicionadas dinamicamente
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.processImagesInContainer(node);

                        // Integrar com carrosséis recém-adicionados
                        const carousels = node.querySelectorAll ? node.querySelectorAll('.carousel') : [];
                        carousels.forEach(carousel => this.integrateWithCarousel(carousel));
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Pré-carregar imagens de fallback
        this.preloadFallbackImages();

        // Integrar com carrosséis existentes
        document.querySelectorAll('.carousel').forEach(carousel => {
            this.integrateWithCarousel(carousel);
        });

        // Log de inicialização com estatísticas
        console.log('🖼️ Sistema de fallback de imagens inicializado');

        // Mostrar estatísticas após 5 segundos
        setTimeout(() => {
            const stats = this.getStats();
            console.log('📊 Estatísticas do sistema de imagens:', stats);
        }, 5000);
    }
}

// CSS para o sistema de fallback
const fallbackCSS = `
    .car-image {
        position: relative;
        overflow: hidden;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
    .car-image img {
        transition: opacity 0.3s ease;
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
        image-rendering: optimize-quality;
    }
    
    .car-image.loading img {
        opacity: 0.7;
    }
    
    .car-image.loading .loading-spinner {
        display: block !important;
    }
    
    .car-image.error .error-placeholder {
        display: flex !important;
        align-items: center;
        justify-content: center;
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: #f8f9fa;
        color: #6c757d;
    }
    
    .car-image.error img {
        display: none !important;
    }
    
    .car-image .error-placeholder {
        display: none;
    }
    
    .car-image.loaded {
        background: transparent;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .car-image.loaded img {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Carrossel melhorado */
    .carousel-control-prev,
    .carousel-control-next {
        width: 40px;
        height: 40px;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(0,0,0,0.6);
        border-radius: 50%;
        opacity: 0.8;
        transition: opacity 0.3s ease;
    }
    
    .carousel-control-prev {
        left: 10px;
    }
    
    .carousel-control-next {
        right: 10px;
    }
    
    .carousel-control-prev:hover,
    .carousel-control-next:hover {
        opacity: 1;
        background: rgba(0,0,0,0.8);
    }
`;

// Adicionar CSS ao documento
function addFallbackCSS() {
    const style = document.createElement('style');
    style.textContent = fallbackCSS;
    document.head.appendChild(style);
}

// Instância global
const imageFallback = new ImageFallbackSystem();

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        addFallbackCSS();
        imageFallback.init();
    });
} else {
    addFallbackCSS();
    imageFallback.init();
}

// Exportar para uso global
window.ImageFallbackSystem = ImageFallbackSystem;
window.imageFallback = imageFallback;