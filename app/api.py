from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import QuestionarioBusca, RespostaBusca
from app.busca_inteligente import processar_busca_inteligente
from app.database import get_carros, get_carro_by_id
from app.enhanced_api import buscar_carros_enhanced

app = FastAPI(
    title="FacilIAuto - Busca Inteligente de Carros",
    description="Sistema de recomendação de carros usando LangGraph",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve arquivos estáticos (CSS, JS, imagens)
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página inicial com o questionário"""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FacilIAuto - Encontre seu carro ideal</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .card-custom { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .step-indicator { background: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 20px; }
            .btn-custom { border-radius: 25px; padding: 10px 30px; }
            .progress-custom { height: 8px; border-radius: 10px; }
            
            /* Sistema de imagens melhorado */
            .car-image {
                position: relative;
                overflow: hidden;
                background: #f8f9fa;
                border-radius: 10px;
                min-height: 200px;
            }
            
            .car-image img {
                transition: opacity 0.3s ease;
                opacity: 0;
            }
            
            .car-image img.loaded {
                opacity: 1;
            }
            
            .error-placeholder {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 2px dashed #dee2e6;
                color: #6c757d;
                border-radius: 10px;
            }
            
            .error-placeholder i {
                color: #adb5bd;
            }
            
            /* Carrossel melhorado */
            .carousel {
                border-radius: 10px;
                overflow: hidden;
                background: #f8f9fa;
            }
            
            .carousel-item img {
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .carousel-item.active img {
                opacity: 1;
            }
            
            /* Animações */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .car-image.loaded img {
                animation: fadeIn 0.3s ease-out;
            }
            
            .fade-in {
                animation: fadeIn 0.5s ease-out;
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
        </style>
    </head>
    <body class="gradient-bg min-vh-100">
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="card card-custom">
                        <div class="card-body p-5">
                            <div class="text-center mb-4">
                                <h1 class="display-4 text-primary mb-3">
                                    <i class="fas fa-car text-primary"></i> FacilIAuto
                                </h1>
                                <p class="lead text-muted">Encontre o carro perfeito para seu perfil com nossa IA</p>
                            </div>
                            
                            <div class="step-indicator">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="badge bg-primary">Questionário Inteligente</span>
                                    <div class="progress flex-grow-1 mx-3 progress-custom">
                                        <div class="progress-bar" id="progressBar" style="width: 12.5%"></div>
                                    </div>
                                    <span class="text-muted"><span id="currentStep">1</span>/8</span>
                                </div>
                            </div>

                            <form id="questionarioForm">
                                <!-- Pergunta 1 -->
                                <div class="question-step" id="step1">
                                    <h4 class="mb-3"><i class="fas fa-star text-warning"></i> 1. Tem alguma marca ou modelo específico em mente?</h4>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Marca preferida (opcional)</label>
                                            <select class="form-select" name="marca_preferida">
                                                <option value="sem_preferencia">Nenhuma preferência</option>
                                                <option value="Toyota">Toyota</option>
                                                <option value="Honda">Honda</option>
                                                <option value="Volkswagen">Volkswagen</option>
                                                <option value="Hyundai">Hyundai</option>
                                                <option value="Chevrolet">Chevrolet</option>
                                                <option value="Ford">Ford</option>
                                                <option value="Nissan">Nissan</option>
                                                <option value="BMW">BMW</option>
                                                <option value="Fiat">Fiat</option>
                                                <option value="Jeep">Jeep</option>
                                            </select>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Modelo preferido (opcional)</label>
                                            <input type="text" class="form-control" name="modelo_especifico" placeholder="Ex: Corolla, Civic...">
                                        </div>
                                    </div>
                                </div>

                                <!-- Pergunta 2 -->
                                <div class="question-step d-none" id="step2">
                                    <h4 class="mb-3"><i class="fas fa-clock text-info"></i> 2. Qual a urgência da compra?</h4>
                                    <div class="row">
                                        <div class="col-12">
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" name="urgencia" value="imediato" required>
                                                <label class="form-check-label">Imediata (preciso comprar agora)</label>
                                            </div>
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" name="urgencia" value="proximo_mes">
                                                <label class="form-check-label">Próximo mês</label>
                                            </div>
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" name="urgencia" value="proximos_meses">
                                                <label class="form-check-label">Próximos meses</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio" name="urgencia" value="sem_pressa">
                                                <label class="form-check-label">Sem pressa (posso esperar)</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Pergunta 3 -->
                                <div class="question-step d-none" id="step3">
                                    <h4 class="mb-3"><i class="fas fa-map-marker-alt text-danger"></i> 3. Onde você está? Isso nos ajuda a encontrar opções próximas</h4>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <select class="form-select" name="regiao" required>
                                                <option value="SP" selected>São Paulo</option>
                                                <option value="RJ">Rio de Janeiro</option>
                                                <option value="MG">Minas Gerais</option>
                                                <option value="PR">Paraná</option>
                                                <option value="SC">Santa Catarina</option>
                                                <option value="RS">Rio Grande do Sul</option>
                                                <option value="BA">Bahia</option>
                                                <option value="PE">Pernambuco</option>
                                                <option value="CE">Ceará</option>
                                                <option value="GO">Goiás</option>
                                                <option value="MT">Mato Grosso</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <!-- Pergunta 4 -->
                                <div class="question-step d-none" id="step4">
                                    <h4 class="mb-3"><i class="fas fa-road text-success"></i> 4. Como você vai usar o carro?</h4>
                                    <div class="row">
                                        <div class="col-12">
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="checkbox" name="uso_principal" value="urbano">
                                                <label class="form-check-label">Uso urbano (cidade)</label>
                                            </div>
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="checkbox" name="uso_principal" value="viagem">
                                                <label class="form-check-label">Viagens longas</label>
                                            </div>
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="checkbox" name="uso_principal" value="trabalho">
                                                <label class="form-check-label">Trabalho/negócios</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="uso_principal" value="familia">
                                                <label class="form-check-label">Uso familiar</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Pergunta 5 -->
                                <div class="question-step d-none" id="step5">
                                    <h4 class="mb-3"><i class="fas fa-users text-primary"></i> 5. Necessidades da Família</h4>
                                    <div class="row">
                                        <div class="col-md-4 mb-3">
                                            <label class="form-label">Quantas pessoas você precisa transportar?</label>
                                            <select class="form-select" name="pessoas_transportar" required>
                                                <option value="2" selected>2 pessoas</option>
                                                <option value="3">3 pessoas</option>
                                                <option value="4">4 pessoas</option>
                                                <option value="5">5 pessoas</option>
                                                <option value="7">Mais de 5 pessoas</option>
                                            </select>
                                        </div>
                                        <div class="col-md-4 mb-3">
                                            <div class="form-check mt-4">
                                                <input class="form-check-input" type="checkbox" name="criancas">
                                                <label class="form-check-label">Transporto crianças</label>
                                            </div>
                                        </div>
                                        <div class="col-md-4 mb-3">
                                            <div class="form-check mt-4">
                                                <input class="form-check-input" type="checkbox" name="animais">
                                                <label class="form-check-label">Transporto animais</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Pergunta 6 -->
                                <div class="question-step d-none" id="step6">
                                    <h4 class="mb-3"><i class="fas fa-tachometer-alt text-warning"></i> 6. Suas necessidades de espaço e potência</h4>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Espaço para carga/bagagem</label>
                                            <select class="form-select" name="espaco_carga" required>
                                                <option value="medio" selected>Médio (bagagem para viagens)</option>
                                                <option value="pouco">Pouco (porta-malas básico)</option>
                                                <option value="muito">Muito (muito espaço/mudanças)</option>
                                            </select>
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Potência desejada</label>
                                            <select class="form-select" name="potencia_desejada" required>
                                                <option value="media" selected>Média (equilibrio)</option>
                                                <option value="economica">Econômica (cidade/economia)</option>
                                                <option value="alta">Alta (performance/subidas)</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <!-- Pergunta 7 -->
                                <div class="question-step d-none" id="step7">
                                    <h4 class="mb-3"><i class="fas fa-balance-scale text-info"></i> 7. Qualidade e Investimento</h4>
                                    <p class="text-muted mb-3">O que é mais importante para você?</p>
                                    <div class="row">
                                        <div class="col-12">
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" name="prioridade" value="economia" required>
                                                <label class="form-check-label">Economia (baixo consumo, preço acessível)</label>
                                            </div>
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" name="prioridade" value="conforto">
                                                <label class="form-check-label">Conforto (bancos, ar-condicionado, silêncio)</label>
                                            </div>
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" name="prioridade" value="seguranca">
                                                <label class="form-check-label">Segurança (airbags, freios, estrutura)</label>
                                            </div>
                                            <div class="form-check mb-2">
                                                <input class="form-check-input" type="radio" name="prioridade" value="performance">
                                                <label class="form-check-label">Performance (potência, dirigibilidade)</label>
                                            </div>
                                            <div class="form-check">
                                                <input class="form-check-input" type="radio" name="prioridade" value="equilibrio">
                                                <label class="form-check-label">Equilíbrio (um pouco de tudo)</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Pergunta 8 -->
                                <div class="question-step d-none" id="step8">
                                    <h4 class="mb-3"><i class="fas fa-dollar-sign text-success"></i> 8. Vamos definir sua faixa de investimento (opcional)</h4>
                                    <p class="text-muted mb-3">Deixe em branco para ver todas as opções disponíveis</p>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Valor mínimo (R$) - Opcional</label>
                                            <input type="number" class="form-control" name="orcamento_min" min="30000" max="500000" placeholder="Ex: 50000 (deixe vazio para sem limite)">
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Valor máximo (R$) - Opcional</label>
                                            <input type="number" class="form-control" name="orcamento_max" min="40000" max="500000" placeholder="Ex: 100000 (deixe vazio para sem limite)">
                                        </div>
                                    </div>
                                </div>

                                <div class="d-flex justify-content-between mt-4">
                                    <button type="button" class="btn btn-outline-secondary btn-custom" id="prevBtn" onclick="previousStep()" style="display: none;">
                                        <i class="fas fa-arrow-left"></i> Anterior
                                    </button>
                                    <button type="button" class="btn btn-primary btn-custom" id="nextBtn" onclick="nextStep()">
                                        Próximo <i class="fas fa-arrow-right"></i>
                                    </button>
                                    <button type="submit" class="btn btn-success btn-custom" id="submitBtn" style="display: none;">
                                        <i class="fas fa-search"></i> Encontrar Carros
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal de Resultados -->
        <div class="modal fade" id="resultadosModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Seus Carros Recomendados</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="resultadosContent">
                        <!-- Resultados serão inseridos aqui -->
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let currentStepNum = 1;
            const totalSteps = 8;

            function updateProgress() {
                const progress = (currentStepNum / totalSteps) * 100;
                document.getElementById('progressBar').style.width = progress + '%';
                document.getElementById('currentStep').textContent = currentStepNum;
            }

            function showStep(stepNum) {
                // Esconde todas as etapas
                for (let i = 1; i <= totalSteps; i++) {
                    document.getElementById('step' + i).classList.add('d-none');
                }
                
                // Mostra a etapa atual
                document.getElementById('step' + stepNum).classList.remove('d-none');
                
                // Controla botões
                document.getElementById('prevBtn').style.display = stepNum > 1 ? 'block' : 'none';
                document.getElementById('nextBtn').style.display = stepNum < totalSteps ? 'block' : 'none';
                document.getElementById('submitBtn').style.display = stepNum === totalSteps ? 'block' : 'none';
            }

            function nextStep() {
                if (validateCurrentStep() && currentStepNum < totalSteps) {
                    currentStepNum++;
                    showStep(currentStepNum);
                    updateProgress();
                }
            }

            function previousStep() {
                if (currentStepNum > 1) {
                    currentStepNum--;
                    showStep(currentStepNum);
                    updateProgress();
                }
            }

            function validateCurrentStep() {
                const currentStep = document.getElementById('step' + currentStepNum);
                const requiredFields = currentStep.querySelectorAll('[required]');
                
                for (let field of requiredFields) {
                    if (field.type === 'radio') {
                        const radioGroup = currentStep.querySelectorAll(`[name="${field.name}"]`);
                        const checked = Array.from(radioGroup).some(radio => radio.checked);
                        if (!checked) {
                            alert('Por favor, selecione uma opção.');
                            return false;
                        }
                    } else if (field.type === 'checkbox' && field.name === 'uso_principal') {
                        const checkboxes = currentStep.querySelectorAll('[name="uso_principal"]:checked');
                        if (checkboxes.length === 0) {
                            alert('Por favor, selecione pelo menos uma opção de uso.');
                            return false;
                        }
                    } else if (!field.value.trim()) {
                        alert('Por favor, preencha todos os campos obrigatórios.');
                        field.focus();
                        return false;
                    }
                }
                return true;
            }

            document.getElementById('questionarioForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                if (!validateCurrentStep()) return;
                
                const formData = new FormData(this);
                const data = {};
                
                // Processa campos simples
                for (let [key, value] of formData.entries()) {
                    if (key === 'uso_principal') {
                        if (!data[key]) data[key] = [];
                        data[key].push(value);
                    } else if (key === 'criancas' || key === 'animais') {
                        data[key] = true;
                    } else if (key === 'pessoas_transportar') {
                        data[key] = parseInt(value);
                    } else if (key === 'orcamento_min' || key === 'orcamento_max') {
                        // Permite valores vazios para orçamento
                        data[key] = value && value.trim() !== '' ? parseInt(value) : null;
                    } else if (key === 'modelo_especifico') {
                        // Se vazio, usar valor padrão
                        data[key] = value && value.trim() !== '' ? value.trim() : 'aberto_opcoes';
                    } else {
                        data[key] = value || null;
                    }
                }
                
                // Validação de orçamento: se um for preenchido, ambos devem ser
                if ((data.orcamento_min !== null && data.orcamento_max === null) ||
                    (data.orcamento_min === null && data.orcamento_max !== null)) {
                    alert('Se você preencher o orçamento, deve informar tanto o valor mínimo quanto o máximo.');
                    return;
                }
                
                // Validação: valor mínimo deve ser menor que o máximo
                if (data.orcamento_min !== null && data.orcamento_max !== null && 
                    data.orcamento_min >= data.orcamento_max) {
                    alert('O valor mínimo deve ser menor que o valor máximo.');
                    return;
                }
                
                // Define valores padrão para checkboxes não marcados
                if (!data.criancas) data.criancas = false;
                if (!data.animais) data.animais = false;
                if (!data.uso_principal) data.uso_principal = [];
                
                // Garantir que campos obrigatórios tenham valores válidos
                if (!data.marca_preferida || data.marca_preferida === 'null') {
                    data.marca_preferida = 'sem_preferencia';
                }
                if (!data.modelo_especifico || data.modelo_especifico === 'null') {
                    data.modelo_especifico = 'aberto_opcoes';
                }
                if (!data.regiao || data.regiao === 'null') {
                    alert('Por favor, selecione uma região.');
                    return;
                }
                if (!data.urgencia || data.urgencia === 'null') {
                    alert('Por favor, selecione uma urgência.');
                    return;
                }
                if (!data.uso_principal || data.uso_principal.length === 0) {
                    alert('Por favor, selecione pelo menos um tipo de uso.');
                    return;
                }
                if (!data.pessoas_transportar || isNaN(data.pessoas_transportar)) {
                    alert('Por favor, selecione o número de pessoas.');
                    return;
                }
                if (!data.espaco_carga || data.espaco_carga === 'null') {
                    alert('Por favor, selecione o espaço de carga.');
                    return;
                }
                if (!data.potencia_desejada || data.potencia_desejada === 'null') {
                    alert('Por favor, selecione a potência desejada.');
                    return;
                }
                if (!data.prioridade || data.prioridade === 'null') {
                    alert('Por favor, selecione uma prioridade.');
                    return;
                }
                
                console.log('📤 Dados a serem enviados:', data);
                
                try {
                    const response = await fetch('/buscar-carros', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Erro ${response.status}: ${response.statusText}`);
                    }
                    
                    const resultado = await response.json();
                    
                    // Verifica se a resposta tem a estrutura esperada
                    if (!resultado || typeof resultado !== 'object') {
                        throw new Error('Resposta inválida do servidor');
                    }
                    
                    mostrarResultados(resultado);
                } catch (error) {
                    console.error('Erro completo:', error);
                    alert('Erro ao buscar carros: ' + error.message);
                }
            });

            function mostrarResultados(resultado) {
                const content = document.getElementById('resultadosContent');
                
                let html = `
                    <div class="mb-4 p-3 bg-light rounded">
                        <h6>Seu Perfil:</h6>
                        <p class="mb-0">${resultado.resumo_perfil || 'Perfil não disponível'}</p>
                    </div>
                `;
                
                if (!resultado.recomendacoes || resultado.recomendacoes.length === 0) {
                    html += `
                        <div class="alert alert-warning">
                            <h5>Nenhum carro encontrado</h5>
                            <p>Não encontramos carros que atendam todos os seus critérios. Considere flexibilizar alguns parâmetros.</p>
                        </div>
                    `;
                } else {
                    html += '<div class="row">';
                    
                    resultado.recomendacoes.forEach((carro, index) => {
                        const badgeClass = index === 0 ? 'success' : index === 1 ? 'warning' : 'info';
                        const position = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
                        
                        // Processa fotos com sistema de fallback melhorado
                        let fotoHtml = '';
                        if (carro.fotos && carro.fotos.length > 0) {
                            if (carro.fotos.length === 1) {
                                fotoHtml = `
                                    <div class="car-image">
                                        <img src="${carro.fotos[0]}" 
                                             class="card-img-top" 
                                             style="height: 200px; object-fit: cover;" 
                                             alt="${carro.marca} ${carro.modelo}"
                                             data-marca="${carro.marca}"
                                             data-modelo="${carro.modelo}"
                                             data-categoria="${carro.categoria}">
                                        <div class="loading-spinner position-absolute top-50 start-50 translate-middle" style="display: none;">
                                            <div class="spinner-border text-primary" role="status"></div>
                                        </div>
                                    </div>
                                `;
                            } else {
                                // Carrossel Bootstrap simples e funcional
                                const carouselId = `carousel-${carro.id}`;
                                fotoHtml = `
                                    <div id="${carouselId}" class="carousel slide" data-bs-ride="carousel" style="height: 200px;">
                                        <div class="carousel-inner">
                                            ${carro.fotos.map((foto, idx) => `
                                                <div class="carousel-item ${idx === 0 ? 'active' : ''}">
                                                    <div class="car-image position-relative">
                                                        <img src="${foto}"
                                                             class="d-block w-100" 
                                                             style="height: 200px; object-fit: cover; border-radius: 10px 10px 0 0;" 
                                                             alt="${carro.marca} ${carro.modelo}"
                                                             data-marca="${carro.marca}"
                                                             data-modelo="${carro.modelo}"
                                                             data-categoria="${carro.categoria}"
                                                             onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                                        <div class="error-placeholder position-absolute top-0 start-0 w-100 h-100 d-none align-items-center justify-content-center bg-light">
                                                            <div class="text-center text-muted">
                                                                <i class="fas fa-car fa-2x mb-2"></i>
                                                                <div>${carro.marca} ${carro.modelo}</div>
                                                                <small>Imagem indisponível</small>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            `).join('')}
                                        </div>
                                        ${carro.fotos.length > 1 ? `
                                            <button class="carousel-control-prev" type="button" data-bs-target="#${carouselId}" data-bs-slide="prev">
                                                <span class="carousel-control-prev-icon"></span>
                                                <span class="visually-hidden">Anterior</span>
                                            </button>
                                            <button class="carousel-control-next" type="button" data-bs-target="#${carouselId}" data-bs-slide="next">
                                                <span class="carousel-control-next-icon"></span>
                                                <span class="visually-hidden">Próximo</span>
                                            </button>
                                            <div class="carousel-indicators">
                                                ${carro.fotos.map((_, idx) => `
                                                    <button type="button" data-bs-target="#${carouselId}" data-bs-slide-to="${idx}" 
                                                            class="${idx === 0 ? 'active' : ''}" aria-label="Slide ${idx + 1}"></button>
                                                `).join('')}
                                            </div>
                                        ` : ''}
                                    </div>
                                `;
                            }
                        } else {
                            // Placeholder melhorado se não houver fotos
                            fotoHtml = `
                                <div class="car-image error">
                                    <div class="error-placeholder d-flex align-items-center justify-content-center" style="height: 200px;">
                                        <div class="text-center text-muted">
                                            <i class="fas fa-car fa-3x mb-2"></i>
                                            <h6>${carro.marca} ${carro.modelo}</h6>
                                            <small>Foto não disponível</small>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }
                        
                        html += `
                            <div class="col-md-6 mb-4">
                                <div class="card h-100">
                                    ${fotoHtml}
                                    <div class="card-header d-flex justify-content-between align-items-center">
                                        <h6 class="mb-0">${position} ${carro.marca} ${carro.modelo}</h6>
                                        <span class="badge bg-${badgeClass}">${carro.score_compatibilidade}% compatível</span>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-6">
                                                <p class="h5 text-primary mb-0">R$ ${carro.preco.toLocaleString('pt-BR')}</p>
                                                ${carro.preco_promocional ? `<p class="text-muted"><del>R$ ${carro.preco_promocional.toLocaleString('pt-BR')}</del></p>` : ''}
                                            </div>
                                            <div class="col-6 text-end">
                                                <p class="text-muted mb-1">${carro.categoria} • ${carro.ano}</p>
                                                ${carro.versao ? `<p class="text-muted small mb-0">${carro.versao}</p>` : ''}
                                            </div>
                                        </div>
                                        
                                        ${carro.cor || carro.km ? `
                                            <div class="row mt-2">
                                                ${carro.cor ? `<div class="col-6"><small class="text-muted"><i class="fas fa-palette"></i> ${carro.cor}</small></div>` : ''}
                                                ${carro.km ? `<div class="col-6"><small class="text-muted"><i class="fas fa-tachometer-alt"></i> ${carro.km.toLocaleString('pt-BR')} km</small></div>` : ''}
                                            </div>
                                        ` : ''}
                                        
                                        ${carro.descricao ? `
                                            <p class="text-muted small mt-2">${carro.descricao}</p>
                                        ` : ''}
                                        
                                                                ${carro.razoes_recomendacao && carro.razoes_recomendacao.length > 0 ? `
                            <h6 class="mt-3">Por que recomendamos:</h6>
                            <ul class="list-unstyled">
                                ${carro.razoes_recomendacao.map(razao => `<li><i class="fas fa-check text-success"></i> ${razao}</li>`).join('')}
                            </ul>
                        ` : ''}
                        
                        ${carro.pontos_fortes && carro.pontos_fortes.length > 0 ? `
                            <h6 class="mt-3">Pontos fortes:</h6>
                            <ul class="list-unstyled">
                                ${carro.pontos_fortes.map(ponto => `<li><i class="fas fa-star text-warning"></i> ${ponto}</li>`).join('')}
                            </ul>
                        ` : ''}
                        
                        ${carro.consideracoes && carro.consideracoes.length > 0 ? `
                            <h6 class="mt-3">Considerações:</h6>
                            <ul class="list-unstyled">
                                ${carro.consideracoes.map(consideracao => `<li><i class="fas fa-info text-info"></i> ${consideracao}</li>`).join('')}
                            </ul>
                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                }
                
                if (resultado.sugestoes_gerais && resultado.sugestoes_gerais.length > 0) {
                    html += `
                        <div class="mt-4 p-3 bg-info bg-opacity-10 rounded">
                            <h6>Dicas personalizadas:</h6>
                            <ul>
                                ${resultado.sugestoes_gerais.map(sugestao => `<li>${sugestao}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
                
                content.innerHTML = html;
                
                // Processar imagens com sistema de fallback simplificado
                setTimeout(() => {
                    // Processar imagens com fallback básico
                    const images = content.querySelectorAll('img[data-marca][data-modelo]');
                    images.forEach(img => {
                        const marca = img.getAttribute('data-marca');
                        const modelo = img.getAttribute('data-modelo');
                        const categoria = img.getAttribute('data-categoria') || 'hatch';
                        
                        // Configurar fallback simples
                        img.onerror = function() {
                            console.warn(`Erro ao carregar: ${this.src}`);
                            // Tentar fallback por categoria com alta resolução
                            const fallbacks = {
                                'hatch': 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&h=800&fit=crop&crop=center&auto=format&q=85',
                                'sedan': 'https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&h=800&fit=crop&crop=center&auto=format&q=85',
                                'suv_compacto': 'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1200&h=800&fit=crop&crop=center&auto=format&q=85',
                                'suv_medio': 'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=1200&h=800&fit=crop&crop=center&auto=format&q=85',
                                'suv_premium': 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=1200&h=800&fit=crop&crop=center&auto=format&q=85',
                                'pickup': 'https://images.unsplash.com/photo-1563720223185-11003d516935?w=1200&h=800&fit=crop&crop=center&auto=format&q=85',
                                'crossover': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=1200&h=800&fit=crop&crop=center&auto=format&q=85',
                                'default': 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&h=800&fit=crop&crop=center&auto=format&q=85'
                            };
                            
                            if (this.src !== fallbacks[categoria] && this.src !== fallbacks['default']) {
                                this.src = fallbacks[categoria] || fallbacks['default'];
                            } else {
                                // Se o fallback também falhou, mostrar placeholder
                                this.style.display = 'none';
                                const placeholder = this.nextElementSibling;
                                if (placeholder && placeholder.classList.contains('error-placeholder')) {
                                    placeholder.style.display = 'flex';
                                }
                            }
                        };
                        
                        // Configurar carregamento bem-sucedido
                        img.onload = function() {
                            console.log(`✅ Imagem carregada: ${marca} ${modelo}`);
                            this.classList.add('loaded');
                            this.style.opacity = '1';
                        };
                        
                        // Se a imagem já está carregada (cache)
                        if (img.complete && img.naturalHeight !== 0) {
                            img.onload();
                        }
                    });
                    
                    console.log('✅ Sistema de imagens inicializado');
                }, 100);
                
                new bootstrap.Modal(document.getElementById('resultadosModal')).show();
            }

            // Inicializa
            showStep(1);
            updateProgress();
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/buscar-carros", response_model=RespostaBusca)
async def buscar_carros(questionario: QuestionarioBusca):
    """Endpoint principal para busca inteligente de carros"""
    try:
        print(f"📥 Dados recebidos: {questionario.model_dump()}")
        resultado = processar_busca_inteligente(questionario)
        
        # Verifica se o resultado tem a estrutura esperada
        if not resultado:
            raise HTTPException(status_code=500, detail="Resultado da busca é nulo")
        
        if not hasattr(resultado, 'recomendacoes'):
            raise HTTPException(status_code=500, detail="Resultado da busca não possui recomendações")
        
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Erro detalhado: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao processar busca: {str(e)}")

@app.get("/carros")
async def listar_carros():
    """Lista todos os carros disponíveis"""
    return get_carros()

@app.get("/carros/{carro_id}")
async def obter_carro(carro_id: int):
    """Obtém detalhes de um carro específico"""
    carro = get_carro_by_id(carro_id)
    if not carro:
        raise HTTPException(status_code=404, detail="Carro não encontrado")
    return carro

@app.post("/buscar-carros-enhanced")
async def buscar_carros_enhanced_endpoint(questionario: QuestionarioBusca):
    """Endpoint melhorado com sistema de fallback integrado"""
    try:
        return await buscar_carros_enhanced(questionario)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar busca: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy", "message": "FacilIAuto API está funcionando!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 