"""
API REST - FacilIAuto Platform
FastAPI backend para sistema de recomendação multi-tenant
"""
from fastapi import FastAPI, HTTPException, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import sys
import os
import shutil
import uuid

# Adicionar backend ao path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from models.car import Car, CarFilter
from models.dealership import Dealership
from models.user_profile import UserProfile
from models.feedback import (
    UserFeedback, 
    RefinementRequest, 
    RefinementResponse,
    FeedbackAction
)
from models.interaction import InteractionEvent, InteractionStats
from services.unified_recommendation_engine import UnifiedRecommendationEngine
from services.feedback_engine import FeedbackEngine
from services.interaction_service import InteractionService
from services.app_transport_validator import validator as app_transport_validator
from services.fuel_price_service import fuel_price_service
from services.context_based_recommendation_skill import create_context_skill
from services.search_intent_classifier import create_intent_classifier

# Inicializar app
app = FastAPI(
    title="FacilIAuto API",
    description="API REST para plataforma multi-tenant de recomendação automotiva",
    version="1.0.0"
)

# Montar arquivos estáticos para imagens
from fastapi.staticfiles import StaticFiles
images_dir = os.path.join(backend_dir, "data", "images")
os.makedirs(images_dir, exist_ok=True)
app.mount("/static/images", StaticFiles(directory=images_dir), name="images")

# CORS - Configuração para produção
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Desenvolvimento local
    "http://localhost:5173",  # Vite dev server
    "https://*.railway.app",  # Railway (wildcard não funciona, adicionar manualmente)
    "https://faciliauto-frontend-production.up.railway.app",  # Frontend Railway
    "https://faciliauto.vercel.app",  # Vercel (se usar)
]

# Em produção, Railway injeta variáveis de ambiente
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    ALLOWED_ORIGINS.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar engines
print("[STARTUP] Inicializando engines...")
data_dir = os.path.join(backend_dir, "data")
print(f"[STARTUP] Data directory: {data_dir}")

try:
    print("[STARTUP] Carregando UnifiedRecommendationEngine...")
    # 🤖 FASE 1: Habilitar LLM para justificativas (configurável via .env)
    use_llm = os.getenv("LLM_ENABLED", "true").lower() == "true"
    engine = UnifiedRecommendationEngine(data_dir=data_dir, use_llm=use_llm)
    print(f"[STARTUP] Engine carregado com {len(engine.all_cars)} carros")
    
    print("[STARTUP] Inicializando FeedbackEngine...")
    feedback_engine = FeedbackEngine()
    
    print("[STARTUP] Inicializando InteractionService...")
    interaction_service = InteractionService(data_dir=os.path.join(data_dir, "interactions"))
    
    print("[STARTUP] Inicializando Context-Based Recommendation Skill...")
    context_skill = create_context_skill(data_dir=data_dir)
    
    print("[STARTUP] Inicializando Search Intent Classifier...")
    intent_classifier = create_intent_classifier()
    
    print("[STARTUP] ✅ Todos os engines inicializados com sucesso!")
except Exception as e:
    print(f"[STARTUP] ❌ ERRO ao inicializar engines: {e}")
    import traceback
    traceback.print_exc()
    raise


@app.get("/")
def read_root():
    """Health check"""
    return {
        "status": "online",
        "service": "FacilIAuto API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check detalhado"""
    stats = engine.get_stats()
    return {
        "status": "healthy",
        "dealerships": stats['active_dealerships'],
        "cars": stats['available_cars']
    }


@app.get("/api/health")
def health_check_api():
    """Health check detalhado (rota com prefixo /api)"""
    stats = engine.get_stats()
    return {
        "status": "healthy",
        "dealerships": stats['active_dealerships'],
        "cars": stats['available_cars']
    }


def _list_dealerships_impl(active_only: bool = True):
    """Implementação interna de listagem de concessionárias"""
    print(f"[API] Listando concessionárias (active_only={active_only})")
    dealerships = engine.dealerships
    
    if active_only:
        dealerships = [d for d in dealerships if d.active]
    
    print(f"[API] Retornando {len(dealerships)} concessionárias")
    return dealerships


@app.get("/dealerships", response_model=List[Dealership])
def list_dealerships(
    active_only: bool = Query(True, description="Apenas concessionárias ativas")
):
    """
    Listar concessionárias (rota sem prefixo - compatibilidade)
    """
    return _list_dealerships_impl(active_only)


@app.get("/api/dealerships", response_model=List[Dealership])
def list_dealerships_api(
    active_only: bool = Query(True, description="Apenas concessionárias ativas")
):
    """
    Listar concessionárias (rota com prefixo /api)
    """
    return _list_dealerships_impl(active_only)


@app.get("/dealerships/{dealership_id}", response_model=Dealership)
def get_dealership(dealership_id: str):
    """
    Obter detalhes de uma concessionária
    """
    for dealer in engine.dealerships:
        if dealer.id == dealership_id:
            return dealer
    
    raise HTTPException(status_code=404, detail="Concessionária não encontrada")


@app.get("/cars", response_model=List[Car])
def list_cars(
    dealership_id: Optional[str] = None,
    marca: Optional[str] = None,
    categoria: Optional[str] = None,
    preco_min: Optional[float] = None,
    preco_max: Optional[float] = None,
    limit: int = Query(50, le=200)
):
    """
    Listar carros com filtros opcionais
    """
    cars = engine.all_cars
    
    # Aplicar filtros
    if dealership_id:
        cars = [c for c in cars if c.dealership_id == dealership_id]
    
    if marca:
        cars = [c for c in cars if c.marca.lower() == marca.lower()]
    
    if categoria:
        cars = [c for c in cars if c.categoria.lower() == categoria.lower()]
    
    if preco_min:
        cars = [c for c in cars if c.preco >= preco_min]
    
    if preco_max:
        cars = [c for c in cars if c.preco <= preco_max]
    
    # Apenas disponíveis
    cars = [c for c in cars if c.disponivel]
    
    return cars[:limit]


@app.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: str):
    """
    Obter detalhes de um carro específico
    """
    for car in engine.all_cars:
        if car.id == car_id:
            return car
    
    raise HTTPException(status_code=404, detail="Carro não encontrado")


def _recommend_cars_impl(profile: UserProfile):
    """
    Implementação interna de recomendações (compartilhada entre rotas)
    """
    # 🐛 DEBUG: Log do perfil recebido
    print(f"\n[API] Recebendo requisição de recomendação")
    print(f"[API] Orçamento: R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}")
    print(f"[API] Ano: {profile.ano_minimo} a {profile.ano_maximo}")
    print(f"[API] Estado: {profile.state}, Cidade: {profile.city}")
    print(f"[API] Uso principal: {profile.uso_principal}")
    
    # Validar orçamento
    if profile.orcamento_max < profile.orcamento_min:
        raise HTTPException(
            status_code=400,
            detail="Orçamento máximo deve ser maior que o mínimo"
        )
    
    # 💰 Validar financial_capacity (Requirements 6.1-6.5)
    if profile.financial_capacity:
        fc = profile.financial_capacity
        
        # Lista de faixas salariais válidas (case-sensitive)
        valid_ranges = ["0-3000", "3000-5000", "5000-8000", "8000-12000", "12000+"]
        
        # Requirement 6.3: Validar que max_monthly_tco é positivo quando fornecido
        # (Validação antes de outras para capturar valores negativos)
        if fc.max_monthly_tco is not None and fc.max_monthly_tco < 0:
            raise HTTPException(
                status_code=400,
                detail="max_monthly_tco deve ser maior ou igual a zero"
            )
        
        # Requirement 6.4: Validar consistência - se is_disclosed=true, monthly_income_range deve existir
        if fc.is_disclosed and not fc.monthly_income_range:
            raise HTTPException(
                status_code=400,
                detail="monthly_income_range é obrigatório quando is_disclosed=true"
            )
        
        # Requirement 6.2: Validar que monthly_income_range está em lista de opções válidas (case-sensitive)
        if fc.monthly_income_range and fc.monthly_income_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail=f"monthly_income_range inválido. Opções válidas: {', '.join(valid_ranges)}"
            )
    
    # Gerar recomendações - os 5 melhores
    recommendations = engine.recommend(
        profile=profile,
        limit=5,
        score_threshold=0.2
    )
    
    # 🐛 DEBUG: Log dos resultados
    print(f"[API] Engine retornou {len(recommendations)} recomendações")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"[API]   {i}. {rec['car'].nome} ({rec['car'].ano})")
    
    # Requirement 2.1: Melhorar resposta quando não há recomendações
    if len(recommendations) == 0:
        # 🔍 DIAGNÓSTICO: Verificar se o problema é localização ou filtros
        # Verificar se existem concessionárias no local especificado
        has_dealerships_in_location = False
        has_cars_in_location = False
        
        if profile.state:
            # Verificar se há concessionárias no estado
            dealerships_in_state = [
                d for d in engine.dealerships 
                if d.active and d.state and d.state.upper() == profile.state.upper()
            ]
            has_dealerships_in_location = len(dealerships_in_state) > 0
            
            # Se há concessionárias, verificar se há carros (ignorando orçamento)
            if has_dealerships_in_location:
                if profile.city:
                    # Verificar cidade específica
                    cars_in_city = [
                        c for c in engine.all_cars 
                        if c.disponivel 
                        and c.dealership_city 
                        and c.dealership_city.lower() == profile.city.lower()
                        and c.dealership_state 
                        and c.dealership_state.upper() == profile.state.upper()
                    ]
                    has_cars_in_location = len(cars_in_city) > 0
                else:
                    # Verificar estado
                    cars_in_state = [
                        c for c in engine.all_cars 
                        if c.disponivel 
                        and c.dealership_state 
                        and c.dealership_state.upper() == profile.state.upper()
                    ]
                    has_cars_in_location = len(cars_in_state) > 0
        
        # Determinar mensagem apropriada baseada no diagnóstico
        if profile.city and profile.state:
            location_str = f"{profile.city}, {profile.state}"
            
            if not has_dealerships_in_location:
                # Caso 1: Não há concessionárias no estado
                print(f"[API] ⚠️ Nenhuma concessionária encontrada em {profile.state}")
                message = f"Nenhuma concessionária disponível em {profile.state}"
                suggestion = "Tente selecionar um estado próximo"
            elif not has_cars_in_location:
                # Caso 2: Há concessionárias mas não na cidade específica
                print(f"[API] ⚠️ Nenhuma concessionária encontrada em {profile.city}")
                message = f"Nenhuma concessionária disponível em {profile.city}"
                suggestion = "Tente buscar em cidades próximas ou expandir para todo o estado"
            else:
                # Caso 3: Há concessionárias e carros, mas não na faixa de preço
                print(f"[API] ⚠️ Há carros em {location_str}, mas não na faixa R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}")
                message = f"Nenhum carro encontrado na faixa de R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}"
                suggestion = "Tente expandir seu orçamento ou ajustar seus filtros"
            
            return {
                "total_recommendations": 0,
                "profile_summary": {
                    "budget_range": f"R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}",
                    "usage": profile.uso_principal,
                    "location": location_str,
                    "top_priorities": []
                },
                "recommendations": [],
                "message": message,
                "suggestion": suggestion
            }
        elif profile.state:
            # Usuário especificou apenas estado
            if not has_dealerships_in_location:
                # Caso 1: Não há concessionárias no estado
                print(f"[API] ⚠️ Nenhuma concessionária encontrada em {profile.state}")
                message = f"Nenhuma concessionária disponível em {profile.state}"
                suggestion = "Tente selecionar um estado próximo"
            elif not has_cars_in_location:
                # Caso 2: Há concessionárias mas sem carros disponíveis
                print(f"[API] ⚠️ Concessionárias em {profile.state} não têm carros disponíveis")
                message = f"Nenhum carro disponível em {profile.state}"
                suggestion = "Tente selecionar um estado próximo ou ajustar seus filtros"
            else:
                # Caso 3: Há carros, mas não na faixa de preço
                print(f"[API] ⚠️ Há carros em {profile.state}, mas não na faixa R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}")
                message = f"Nenhum carro encontrado na faixa de R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}"
                suggestion = "Tente expandir seu orçamento ou ajustar seus filtros"
            
            return {
                "total_recommendations": 0,
                "profile_summary": {
                    "budget_range": f"R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}",
                    "usage": profile.uso_principal,
                    "location": f"{profile.city or 'N/A'}, {profile.state}",
                    "top_priorities": []
                },
                "recommendations": [],
                "message": message,
                "suggestion": suggestion
            }
        else:
            # Usuário NÃO especificou estado - problema é com filtros/orçamento
            print(f"[API] ⚠️ Nenhuma recomendação encontrada (sem filtro de localização)")
            print(f"[API] Possíveis razões: orçamento muito restrito ou filtros muito específicos")
            
            return {
                "total_recommendations": 0,
                "profile_summary": {
                    "budget_range": f"R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}",
                    "usage": profile.uso_principal,
                    "location": "Qualquer localização",
                    "top_priorities": []
                },
                "recommendations": [],
                "message": "Nenhum carro encontrado com os filtros selecionados",
                "suggestion": "Tente aumentar seu orçamento ou ajustar suas preferências"
            }
    
    # Extrair top priorities do perfil (do dicionário prioridades)
    priority_labels = {
        'economia': 'Economia',
        'espaco': 'Espaço',
        'performance': 'Performance',
        'conforto': 'Conforto',
        'seguranca': 'Segurança'
    }
    
    # Ordenar prioridades por valor (maior para menor) e pegar top 3
    sorted_priorities = sorted(
        profile.prioridades.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    top_priorities = [
        priority_labels.get(key, key.capitalize()) 
        for key, value in sorted_priorities[:3] 
        if value > 0
    ]
    
    # Formatar resposta
    return {
        "total_recommendations": len(recommendations),
        "profile_summary": {
            "budget_range": f"R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}",
            "usage": profile.uso_principal,
            "location": f"{profile.city or 'N/A'}, {profile.state or 'N/A'}",
            "top_priorities": top_priorities
        },
        "recommendations": [
            {
                "car": {
                    "id": rec['car'].id,
                    "nome": rec['car'].nome,
                    "marca": rec['car'].marca,
                    "modelo": rec['car'].modelo,
                    "ano": rec['car'].ano,
                    "preco": rec['car'].preco,
                    "quilometragem": rec['car'].quilometragem,
                    "combustivel": rec['car'].combustivel,
                    "cambio": rec['car'].cambio,
                    "cor": rec['car'].cor,
                    "portas": rec['car'].portas,
                    "categoria": rec['car'].categoria,
                    "imagens": rec['car'].imagens,
                    "disponivel": rec['car'].disponivel,
                    "destaque": rec['car'].destaque,
                    "dealership_id": rec['car'].dealership_id,
                    "dealership_name": rec['car'].dealership_name,
                    "dealership_city": rec['car'].dealership_city,
                    "dealership_state": rec['car'].dealership_state,
                    "dealership_phone": rec['car'].dealership_phone,
                    "dealership_whatsapp": rec['car'].dealership_whatsapp,
                    "score_familia": rec['car'].score_familia,
                    "score_economia": rec['car'].score_economia,
                    "score_performance": rec['car'].score_performance,
                    "score_conforto": rec['car'].score_conforto,
                    "score_seguranca": rec['car'].score_seguranca,
                    # Adicionar categorias de transporte aceitas se for transporte_passageiros
                    "app_transport_categories": (
                        app_transport_validator.get_accepted_categories(
                            rec['car'].marca,
                            rec['car'].modelo,
                            rec['car'].ano
                        ) if profile.uso_principal == "transporte_passageiros" and app_transport_validator.app_vehicles_data else []
                    ) if profile.uso_principal == "transporte_passageiros" else None
                },
                "match_score": rec['score'],
                "match_percentage": rec['match_percentage'],
                "justification": rec['justificativa'],
                # 💰 TCO Information (Requirements 1.1-1.5, 2.1-2.5)
                "tco_breakdown": rec.get('tco_breakdown').model_dump() if rec.get('tco_breakdown') else None,
                "fits_budget": rec.get('fits_budget'),
                "budget_percentage": round(rec.get('budget_percentage'), 1) if rec.get('budget_percentage') is not None else None,
                # 🚦 Financial Health Indicator (Requirements 2.1-2.5)
                "financial_health": rec.get('financial_health')
            }
            for rec in recommendations
        ]
    }

@app.post("/recommend")
def recommend_cars(profile: UserProfile):
    """
    Gerar recomendações personalizadas baseadas no perfil do usuário
    (Rota sem prefixo - mantida para compatibilidade)
    """
    try:
        return _recommend_cars_impl(profile)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] /recommend: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar recomendações: {str(e)}")


@app.get("/search/contextual")
def contextual_search(
    query: str = Query(..., description="Query de busca do usuário (ex: 'carros para fazer uber')"),
    max_results: int = Query(10, description="Número máximo de resultados"),
    budget_min: Optional[float] = Query(None, description="Orçamento mínimo"),
    budget_max: Optional[float] = Query(None, description="Orçamento máximo"),
    location: Optional[str] = Query(None, description="Localização do usuário")
):
    """
    🎯 Busca contextual usando Context-Based Recommendation Skill
    
    Esta rota utiliza a skill de recomendação baseada em contexto para:
    1. Analisar a intenção da busca do usuário
    2. Classificar o tipo de uso pretendido  
    3. Aplicar conhecimento da base de perfis de uso
    4. Recomendar carros adequados ao contexto
    
    Exemplos de queries:
    - "carros para fazer uber"
    - "carro para trabalho diário"  
    - "SUV para família com crianças"
    - "pickup para entregas"
    - "primeiro carro econômico"
    """
    try:
        # Preparar dados do usuário
        user_data = {}
        if budget_min is not None:
            user_data['budget_min'] = budget_min
        if budget_max is not None:
            user_data['budget_max'] = budget_max
        if location:
            user_data['location'] = location
            
        # Obter recomendações contextuais
        recommendations = context_skill.recommend_by_context(
            query=query,
            user_data=user_data,
            max_results=max_results
        )
        
        # Analisar contexto para insights
        context = context_skill.analyze_search_context(query, user_data)
        
        return {
            "query": query,
            "context_analysis": {
                "detected_intent": context.detected_intent.value,
                "confidence": round(context.confidence, 2),
                "profile_match": context.profile_match,
                "extracted_entities": context.extracted_entities
            },
            "total_results": len(recommendations),
            "recommendations": [
                {
                    "car": {
                        "id": rec.car.id,
                        "nome": rec.car.nome,
                        "marca": rec.car.marca,
                        "modelo": rec.car.modelo,
                        "ano": rec.car.ano,
                        "preco": rec.car.preco,
                        "quilometragem": rec.car.quilometragem,
                        "combustivel": rec.car.combustivel,
                        "categoria": rec.car.categoria,
                        "imagens": rec.car.imagens[:3] if rec.car.imagens else [],
                        "dealership_name": rec.car.dealership_name,
                        "dealership_city": rec.car.dealership_city,
                        "dealership_state": rec.car.dealership_state,
                        "dealership_phone": rec.car.dealership_phone,
                        "dealership_whatsapp": rec.car.dealership_whatsapp
                    },
                    "scores": {
                        "base_score": round(rec.base_score, 2),
                        "context_boost": round(rec.context_boost, 2),
                        "final_score": round(rec.final_score, 2)
                    },
                    "reasoning": rec.reasoning,
                    "profile_alignment": {
                        key: round(value, 2) for key, value in rec.profile_alignment.items()
                    }
                }
                for rec in recommendations
            ]
        }
        
    except Exception as e:
        print(f"[API ERROR] /search/contextual: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro na busca contextual: {str(e)}")


@app.get("/search/intent-analysis") 
def analyze_search_intent(
    query: str = Query(..., description="Query para análise de intenção")
):
    """
    🧠 Análise de intenção de busca usando Search Intent Classifier
    
    Esta rota analisa uma query de busca e retorna:
    1. Intenção principal detectada
    2. Confiança da classificação
    3. Intenções secundárias
    4. Entidades extraídas (marcas, modelos, preços, etc.)
    5. Palavras-chave importantes
    6. Persona inferida do usuário
    7. Fatores de prioridade recomendados
    """
    try:
        # Analisar intenção
        analysis = intent_classifier.classify_intent(query)
        
        return {
            "query": query,
            "analysis": {
                "primary_intent": {
                    "category": analysis.primary_intent.value,
                    "confidence": round(analysis.confidence, 3)
                },
                "secondary_intents": [
                    {
                        "category": intent.value,
                        "confidence": round(confidence, 3)
                    }
                    for intent, confidence in analysis.secondary_intents
                ],
                "entities": [
                    {
                        "type": entity.type,
                        "value": entity.value,
                        "confidence": entity.confidence,
                        "context": entity.context[:50] + "..." if len(entity.context) > 50 else entity.context
                    }
                    for entity in analysis.entities
                ],
                "keywords": analysis.keywords,
                "user_persona": analysis.user_persona,
                "priority_factors": {
                    key: round(value, 2) 
                    for key, value in analysis.priority_factors.items()
                }
            }
        }
        
    except Exception as e:
        print(f"[API ERROR] /search/intent-analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro na análise de intenção: {str(e)}")


@app.get("/validate/app-transport")
def validate_app_transport(
    marca: str = Query(..., description="Marca do veículo"),
    modelo: str = Query(..., description="Modelo do veículo"), 
    ano: int = Query(..., description="Ano de fabricação"),
    categoria: str = Query("uberx_99pop", description="Categoria desejada: uberx_99pop, uber_comfort, uber_black")
):
    """
    🚗 Validação de critérios REAIS da Uber/99
    
    Valida se um veículo específico atende aos requisitos das plataformas
    de transporte usando dados oficiais atualizados.
    
    Retorna:
    - ✅ Se é aceito na categoria solicitada
    - 📋 Todas as categorias aceitas
    - 📊 Detalhes dos requisitos
    - 💰 Estimativa de ganhos por categoria
    """
    try:
        # Validar categoria específica
        from services.app_transport_validator import validator as app_validator
        
        is_valid, accepted_category = app_validator.is_valid_for_app_transport(
            marca=marca,
            modelo=modelo, 
            ano=ano,
            categoria_desejada=categoria
        )
        
        # Obter todas as categorias aceitas
        all_categories = app_validator.get_accepted_categories(
            marca=marca,
            modelo=modelo,
            ano=ano
        )
        
        # Obter detalhes dos requisitos
        requirements = app_validator.get_requirements_for_category(categoria)
        
        # Analisar por que pode ter sido rejeitado
        rejection_reasons = []
        if not is_valid:
            if ano < requirements.get('ano_minimo_fabricacao', 2015):
                rejection_reasons.append(f"Ano muito antigo (mínimo: {requirements.get('ano_minimo_fabricacao')})")
            
            current_year = datetime.now().year
            vehicle_age = current_year - ano
            if vehicle_age > requirements.get('idade_maxima_anos', 10):
                rejection_reasons.append(f"Veículo muito antigo (máximo: {requirements.get('idade_maxima_anos')} anos)")
                
            modelo_completo = f"{marca} {modelo}"
            modelos_aceitos = requirements.get('modelos_aceitos', [])
            if modelos_aceitos and not any(modelo_aceito.lower() in modelo_completo.lower() for modelo_aceito in modelos_aceitos):
                rejection_reasons.append("Modelo não está na lista de aceitos")
                
        # Estimativas de ganho (valores aproximados)
        earnings_estimates = {
            'uberx_99pop': {
                'corrida_media': 12.50,
                'corridas_dia_estimado': 15,
                'ganho_bruto_dia': 187.50,
                'ganho_bruto_mes': 5625
            },
            'uber_comfort': {
                'corrida_media': 16.80,
                'corridas_dia_estimado': 12,
                'ganho_bruto_dia': 201.60,
                'ganho_bruto_mes': 6048
            },
            'uber_black': {
                'corrida_media': 24.50,
                'corridas_dia_estimado': 8,
                'ganho_bruto_dia': 196.00,
                'ganho_bruto_mes': 5880
            }
        }
        
        return {
            "vehicle": {
                "marca": marca,
                "modelo": modelo,
                "ano": ano
            },
            "validation": {
                "categoria_solicitada": categoria,
                "is_valid": is_valid,
                "accepted_category": accepted_category,
                "all_categories": all_categories,
                "rejection_reasons": rejection_reasons if not is_valid else []
            },
            "requirements": requirements,
            "earnings_estimate": {
                category: earnings_estimates.get(category, {})
                for category in all_categories
            } if all_categories else {},
            "recommendations": [
                "💡 UberX/99Pop: Maior volume de corridas, menor valor médio",
                "💼 Uber Comfort: Equilíbrio entre volume e valor",
                "👔 Uber Black: Menor volume, maior valor médio",
                "📊 Considere custos: combustível, manutenção, seguro",
                "📱 Apps múltiplos aumentam oportunidades"
            ] if is_valid else [
                "🔍 Verifique modelos similares aceitos",
                "📅 Considere carros mais novos",
                "💰 Avalie custo-benefício vs outros usos",
                "📋 Consulte requisitos locais da sua cidade"
            ]
        }
        
    except Exception as e:
        print(f"[API ERROR] /validate/app-transport: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro na validação: {str(e)}")


@app.post("/api/recommend")
def recommend_cars_api(profile: UserProfile):
    """
    Gerar recomendações personalizadas baseadas no perfil do usuário
    (Rota com prefixo /api - nova rota para produção)
    """
    try:
        return _recommend_cars_impl(profile)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] /api/recommend: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar recomendações: {str(e)}")


def _get_platform_stats_impl():
    """Implementação interna de estatísticas da plataforma"""
    print(f"[API] Obtendo estatísticas da plataforma")
    stats = engine.get_stats()
    
    # Calcular preços
    prices = [car.preco for car in engine.all_cars if car.disponivel]
    avg_price = sum(prices) / len(prices) if prices else 0
    
    # Agrupar por marca
    cars_by_brand = {}
    for car in engine.all_cars:
        if car.disponivel:
            cars_by_brand[car.marca] = cars_by_brand.get(car.marca, 0) + 1
    
    print(f"[API] Stats: {stats['available_cars']} carros disponíveis, {stats['active_dealerships']} concessionárias ativas")
    
    return {
        "total_dealerships": stats['total_dealerships'],
        "active_dealerships": stats['active_dealerships'],
        "total_cars": stats['total_cars'],
        "available_cars": stats['available_cars'],
        "avg_price": round(avg_price, 2),
        "price_range": {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0
        },
        "cars_by_category": stats['cars_by_category'],
        "cars_by_brand": cars_by_brand,
        "last_updated": "2024-10-06T00:00:00"
    }


@app.get("/stats")
def get_platform_stats():
    """
    Estatísticas gerais da plataforma (rota sem prefixo - compatibilidade)
    """
    from fastapi.responses import JSONResponse
    data = _get_platform_stats_impl()
    return JSONResponse(
        content=data,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/api/stats")
def get_platform_stats_api():
    """
    Estatísticas gerais da plataforma (rota com prefixo /api)
    """
    from fastapi.responses import JSONResponse
    data = _get_platform_stats_impl()
    return JSONResponse(
        content=data,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/categories")
def list_categories():
    """
    Listar categorias de carros disponíveis
    """
    categories = set(car.categoria for car in engine.all_cars if car.disponivel)
    return sorted(list(categories))


@app.get("/brands")
def list_brands():
    """
    Listar marcas de carros disponíveis
    """
    brands = set(car.marca for car in engine.all_cars if car.disponivel)
    return sorted(list(brands))


@app.get("/brands-models")
def list_brands_with_models():
    """
    Listar marcas de carros disponíveis com seus modelos correspondentes
    
    Retorna um dicionário onde:
    - Chave: marca (ex: "Fiat", "Chevrolet")
    - Valor: lista de modelos únicos disponíveis para aquela marca
    
    Exemplo de resposta:
    {
        "Fiat": ["Cronos", "Argo", "Toro"],
        "Chevrolet": ["Onix", "Tracker", "S10"]
    }
    """
    from collections import defaultdict
    
    brands_models = defaultdict(set)
    
    # Agrupar modelos por marca
    for car in engine.all_cars:
        if car.disponivel:
            brands_models[car.marca].add(car.modelo)
    
    # Converter sets para listas ordenadas
    result = {
        marca: sorted(list(modelos))
        for marca, modelos in sorted(brands_models.items())
    }
    
    return result


# ========================================
# 📸 FASE 2: Endpoints de Imagens (Concessionárias)
# ========================================

@app.post("/api/dealerships/{dealership_id}/cars/{car_id}/images")
async def upload_car_image(
    dealership_id: str, 
    car_id: str, 
    file: UploadFile = File(...)
):
    """
    Upload de imagem para um carro específico
    """
    # Validar se carro existe e pertence à concessionária
    car_found = None
    for car in engine.all_cars:
        if car.id == car_id:
            if car.dealership_id != dealership_id:
                raise HTTPException(status_code=403, detail="Carro não pertence a esta concessionária")
            car_found = car
            break
    
    if not car_found:
        raise HTTPException(status_code=404, detail="Carro não encontrado")
    
    # Validar tipo de arquivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    # Criar diretório se não existir
    # Estrutura: data/images/{dealership_id}/{car_id}/
    car_images_dir = os.path.join(images_dir, dealership_id, car_id)
    os.makedirs(car_images_dir, exist_ok=True)
    
    # Gerar nome único para o arquivo
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(car_images_dir, filename)
    
    # Salvar arquivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar imagem: {str(e)}")
    
    # Gerar URL pública
    # URL base deve ser configurada via env var em produção
    base_url = os.getenv("API_URL", "http://localhost:8000")
    image_url = f"{base_url}/static/images/{dealership_id}/{car_id}/{filename}"
    
    # Atualizar modelo do carro
    if not car_found.imagens:
        car_found.imagens = []
    car_found.imagens.append(image_url)
    
    # Persistir alterações (simulado por enquanto, idealmente salvar no DB/JSON)
    # engine.save_car(car_found) # TODO: Implementar persistência
    
    return {
        "status": "success",
        "filename": filename,
        "url": image_url,
        "car_id": car_id
    }


# ========================================
# 🤖 FASE 2: Endpoints de Feedback
# ========================================

def _submit_feedback_impl(feedback: UserFeedback):
    """Implementação interna de submissão de feedback"""
    print(f"[API] Recebendo feedback: user={feedback.user_id}, action={feedback.action}, car={feedback.car_id}")
    
    # Adicionar feedback ao histórico
    history = feedback_engine.add_feedback(feedback)
    
    print(f"[API] Feedback processado: {history.total_interactions} interações totais")
    
    return {
        "status": "success",
        "message": "Feedback recebido com sucesso",
        "user_id": feedback.user_id,
        "action": feedback.action,
        "car_id": feedback.car_id,
        "history": {
            "total_interactions": history.total_interactions,
            "liked_count": history.liked_count,
            "disliked_count": history.disliked_count,
            "clicked_whatsapp": history.clicked_whatsapp_count,
            "preferred_brands": history.preferred_brands,
            "preferred_categories": history.preferred_categories
        }
    }


@app.post("/feedback")
def submit_feedback(feedback: UserFeedback):
    """
    💻 Tech Lead (FASE 2): Receber feedback do usuário (rota sem prefixo - compatibilidade)
    
    Ações possíveis:
    - "liked": Gostou do carro
    - "disliked": Não gostou
    - "clicked_whatsapp": Clicou para contato
    - "viewed_details": Visualizou detalhes
    - "compared": Comparou com outros
    
    Retorna histórico atualizado do usuário
    """
    try:
        return _submit_feedback_impl(feedback)
    except Exception as e:
        print(f"[API ERROR] /feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar feedback: {str(e)}")


@app.post("/api/feedback")
def submit_feedback_api(feedback: UserFeedback):
    """
    💻 Tech Lead (FASE 2): Receber feedback do usuário (rota com prefixo /api)
    
    Ações possíveis:
    - "liked": Gostou do carro
    - "disliked": Não gostou
    - "clicked_whatsapp": Clicou para contato
    - "viewed_details": Visualizou detalhes
    - "compared": Comparou com outros
    
    Retorna histórico atualizado do usuário
    """
    try:
        return _submit_feedback_impl(feedback)
    except Exception as e:
        print(f"[API ERROR] /api/feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar feedback: {str(e)}")


@app.post("/refine-recommendations")
def refine_recommendations(request: RefinementRequest):
    """
    💻 Tech Lead + 📊 Data Analyst (FASE 2): Refinar recomendações baseado em feedback
    
    Sistema iterativo que:
    1. Analisa feedback do usuário
    2. Ajusta pesos de prioridades automaticamente
    3. Gera novas recomendações
    4. Repete até convergir (encontrar match ideal)
    
    Convergência acontece quando:
    - Melhor score >= target_score (padrão: 85%)
    - Pelo menos 3 carros com score >= 80% do target
    
    Retorna:
        RefinementResponse com recomendações refinadas, insights e próximos passos
    """
    try:
        # Validar request
        if not request.feedbacks:
            raise HTTPException(
                status_code=400,
                detail="Nenhum feedback fornecido. Forneça pelo menos 1 feedback."
            )
        
        # Converter dict para UserProfile
        current_profile = UserProfile(**request.current_profile)
        
        # Analisar feedback e ajustar pesos
        weight_adjustment = feedback_engine.adjust_weights(
            current_profile,
            request.feedbacks
        )
        
        # Atualizar perfil com pesos ajustados
        updated_profile = feedback_engine.update_profile_from_weights(
            current_profile,
            weight_adjustment
        )
        
        # Gerar novas recomendações com perfil ajustado
        recommendations = engine.recommend(
            updated_profile,
            limit=10,
            score_threshold=0.3  # Mais permissivo para feedback
        )
        
        # Verificar convergência
        converged, best_score = feedback_engine.check_convergence(
            recommendations,
            target_score=request.target_score
        )
        
        # Gerar insights
        insights = feedback_engine.generate_insights(
            request.feedbacks,
            weight_adjustment
        )
        
        # Determinar próximos passos
        if converged:
            next_steps = f"✅ Encontramos o match ideal! {len([r for r in recommendations if r['score'] >= request.target_score])} carros com score >= {request.target_score:.0%}"
        else:
            next_steps = f"Continue dando feedback. Melhor match atual: {best_score:.0%}. Meta: {request.target_score:.0%}"
        
        # Formatar resposta
        return {
            "user_id": request.user_id,
            "session_id": request.session_id or "default_session",
            "iteration": len(request.feedbacks),
            "converged": converged,
            "best_score": round(best_score, 2),
            "target_score": request.target_score,
            "weight_adjustments": {
                "original_weights": weight_adjustment.original_weights,
                "adjusted_weights": weight_adjustment.adjusted_weights,
                "adjustment_reason": weight_adjustment.adjustment_reason,
                "confidence_score": weight_adjustment.confidence_score
            },
            "recommendations": [
                {
                    "car": {
                        "id": rec['car'].id,
                        "nome": rec['car'].nome,
                        "marca": rec['car'].marca,
                        "modelo": rec['car'].modelo,
                        "ano": rec['car'].ano,
                        "preco": rec['car'].preco,
                        "quilometragem": rec['car'].quilometragem,
                        "combustivel": rec['car'].combustivel,
                        "cambio": rec['car'].cambio,
                        "cor": rec['car'].cor,
                        "portas": rec['car'].portas,
                        "categoria": rec['car'].categoria,
                        "imagens": rec['car'].imagens,
                        "disponivel": rec['car'].disponivel,
                        "destaque": rec['car'].destaque,
                        "dealership_id": rec['car'].dealership_id,
                        "dealership_name": rec['car'].dealership_name,
                        "dealership_city": rec['car'].dealership_city,
                        "dealership_state": rec['car'].dealership_state,
                        "dealership_phone": rec['car'].dealership_phone,
                        "dealership_whatsapp": rec['car'].dealership_whatsapp,
                        "score_familia": rec['car'].score_familia,
                        "score_economia": rec['car'].score_economia,
                        "score_performance": rec['car'].score_performance,
                        "score_conforto": rec['car'].score_conforto,
                        "score_seguranca": rec['car'].score_seguranca
                    },
                    "match_score": round(rec['score'], 2),
                    "match_percentage": rec['match_percentage'],
                    "justification": rec['justificativa'],
                    "improved": rec['score'] > 0.7  # Marcar se é bom match
                }
                for rec in recommendations[:10]
            ],
            "insights": insights,
            "next_steps": next_steps,
            "updated_profile": {
                "prioridades": updated_profile.prioridades,
                "marcas_preferidas": updated_profile.marcas_preferidas,
                "tipos_preferidos": updated_profile.tipos_preferidos
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao refinar recomendações: {str(e)}")


@app.get("/feedback/history/{user_id}")
def get_feedback_history(user_id: str):
    """
    Obter histórico de feedback de um usuário
    """
    if user_id not in feedback_engine.user_histories:
        raise HTTPException(status_code=404, detail="Histórico não encontrado")
    
    history = feedback_engine.user_histories[user_id]
    
    return {
        "user_id": user_id,
        "total_interactions": history.total_interactions,
        "liked_count": history.liked_count,
        "disliked_count": history.disliked_count,
        "clicked_whatsapp_count": history.clicked_whatsapp_count,
        "preferred_brands": history.preferred_brands,
        "preferred_categories": history.preferred_categories,
        "avg_price_liked": history.avg_price_liked,
        "avg_year_liked": history.avg_year_liked,
        "recent_feedbacks": [
            {
                "car_id": f.car_id,
                "action": f.action,
                "timestamp": f.timestamp,
                "car_marca": f.car_marca,
                "car_categoria": f.car_categoria
            }
            for f in history.feedbacks[-10:]  # Últimos 10
        ]
    }


# ========================================
# 🤖 ML SYSTEM: Endpoints de Coleta de Interações
# ========================================

@app.post("/api/interactions/track")
async def track_interaction(event: InteractionEvent):
    """
    🤖 ML System: Registrar interação do usuário com veículo
    
    Este endpoint coleta dados de interações para treinamento futuro
    de modelos de Machine Learning. Não afeta a experiência do usuário
    se falhar (fail gracefully).
    
    Tipos de interação:
    - "click": Usuário clicou no card do carro
    - "view_details": Usuário visualizou detalhes do carro
    - "whatsapp_contact": Usuário clicou para contatar via WhatsApp
    
    Args:
        event: Evento de interação com dados do usuário e carro
        
    Returns:
        Status da operação (sempre retorna sucesso para não bloquear UI)
    """
    try:
        # Salvar interação
        success = interaction_service.save_interaction(event)
        
        if success:
            return {
                "status": "success",
                "message": "Interação registrada com sucesso",
                "interaction_type": event.interaction_type,
                "car_id": event.car_id
            }
        else:
            # Logar erro mas não falhar
            print(f"[AVISO] Falha ao salvar interação, mas continuando...")
            return {
                "status": "partial_success",
                "message": "Interação recebida mas não persistida"
            }
    
    except Exception as e:
        # Nunca falhar - apenas logar
        print(f"[ERRO] Erro ao processar interação: {e}")
        return {
            "status": "error",
            "message": "Erro ao processar interação, mas operação continua"
        }


@app.get("/api/ml/stats")
async def get_ml_stats():
    """
    🤖 ML System: Obter estatísticas do sistema de ML
    
    Retorna informações sobre:
    - Total de interações coletadas
    - Distribuição por tipo de interação
    - Sessões e carros únicos
    - Status de prontidão para treinamento
    
    Returns:
        Estatísticas agregadas do sistema ML
    """
    try:
        # Obter estatísticas
        stats = interaction_service.get_stats()
        total_count = interaction_service.get_interactions_count()
        
        # Verificar se há dados suficientes para treinamento
        min_required = 500
        ready_for_training = total_count >= min_required
        
        return {
            "status": "operational",
            "data_collection": {
                "total_interactions": stats.total_interactions,
                "click_count": stats.click_count,
                "view_details_count": stats.view_details_count,
                "whatsapp_contact_count": stats.whatsapp_contact_count,
                "unique_sessions": stats.unique_sessions,
                "unique_cars": stats.unique_cars,
                "avg_duration_seconds": stats.avg_duration_seconds,
                "last_interaction": stats.last_interaction.isoformat() if stats.last_interaction else None
            },
            "ml_readiness": {
                "ready_for_training": ready_for_training,
                "min_required_interactions": min_required,
                "progress_percentage": min(100, (total_count / min_required) * 100),
                "interactions_needed": max(0, min_required - total_count)
            },
            "ml_model": {
                "available": False,  # Será True quando modelo for treinado
                "version": None,
                "last_trained": None
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter estatísticas de ML: {str(e)}"
        )


@app.get("/api/ml/export-data")
async def export_ml_data(
    limit: Optional[int] = Query(None, description="Limitar número de interações retornadas")
):
    """
    🤖 ML System: Exportar dados de interações para análise
    
    Permite download dos dados coletados para análise offline
    ou treinamento de modelos.
    
    Args:
        limit: Número máximo de interações a retornar (None = todas)
        
    Returns:
        Dados de interações em formato JSON
    """
    try:
        # Obter todas as interações
        interactions = interaction_service.get_all_interactions()
        
        # Aplicar limite se especificado
        if limit:
            interactions = interactions[-limit:]  # Últimas N interações
        
        # Obter estatísticas
        stats = interaction_service.get_stats()
        
        return {
            "status": "success",
            "exported_at": datetime.now().isoformat(),
            "total_interactions": len(interactions),
            "data": {
                "interactions": interactions,
                "statistics": {
                    "total": stats.total_interactions,
                    "by_type": {
                        "click": stats.click_count,
                        "view_details": stats.view_details_count,
                        "whatsapp_contact": stats.whatsapp_contact_count
                    },
                    "unique_sessions": stats.unique_sessions,
                    "unique_cars": stats.unique_cars,
                    "avg_duration_seconds": stats.avg_duration_seconds
                }
            },
            "metadata": {
                "version": "1.0",
                "format": "json",
                "encoding": "utf-8"
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao exportar dados de ML: {str(e)}"
        )


# ⛽ Fuel Price Management Endpoints

@app.get("/fuel-price")
def get_fuel_price():
    """
    Obter preço atual do combustível
    
    Returns:
        Informações sobre o preço atual e sua fonte
    """
    return fuel_price_service.get_price_info()


@app.post("/fuel-price/update")
def update_fuel_price(new_price: float):
    """
    Atualizar preço do combustível manualmente
    
    Args:
        new_price: Novo preço em R$/L
        
    Returns:
        Confirmação da atualização
        
    Note:
        Requer autenticação em produção
    """
    try:
        fuel_price_service.update_default_price(new_price)
        return {
            "success": True,
            "message": f"Preço atualizado para R$ {new_price:.2f}/L",
            "price_info": fuel_price_service.get_price_info()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Para testes e produção
if __name__ == "__main__":
    import uvicorn
    # Railway fornece a porta via variável de ambiente PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
