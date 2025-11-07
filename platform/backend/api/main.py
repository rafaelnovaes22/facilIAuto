"""
API REST - FacilIAuto Platform
FastAPI backend para sistema de recomendação multi-tenant
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sys
import os

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

# Inicializar app
app = FastAPI(
    title="FacilIAuto API",
    description="API REST para plataforma multi-tenant de recomendação automotiva",
    version="1.0.0"
)

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
    engine = UnifiedRecommendationEngine(data_dir=data_dir)
    print(f"[STARTUP] Engine carregado com {len(engine.all_cars)} carros")
    
    print("[STARTUP] Inicializando FeedbackEngine...")
    feedback_engine = FeedbackEngine()
    
    print("[STARTUP] Inicializando InteractionService...")
    interaction_service = InteractionService(data_dir=os.path.join(data_dir, "interactions"))
    
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
    
    # Gerar recomendações - apenas os 3 melhores
    recommendations = engine.recommend(
        profile=profile,
        limit=3,
        score_threshold=0.2
    )
    
    # 🐛 DEBUG: Log dos resultados
    print(f"[API] Engine retornou {len(recommendations)} recomendações")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"[API]   {i}. {rec['car'].nome} ({rec['car'].ano})")
    
    # Requirement 2.1: Melhorar resposta quando não há concessionárias na região
    if len(recommendations) == 0:
        print(f"[API] ⚠️ Nenhuma recomendação encontrada para {profile.state}")
        print(f"[API] Possíveis razões: sem concessionárias no estado ou sem carros no orçamento")
        
        # Retornar 200 com lista vazia e mensagem explicativa
        return {
            "total_recommendations": 0,
            "profile_summary": {
                "budget_range": f"R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}",
                "usage": profile.uso_principal,
                "location": f"{profile.city or 'N/A'}, {profile.state or 'N/A'}",
                "top_priorities": []
            },
            "recommendations": [],
            "message": f"Nenhuma concessionária disponível em {profile.state}",
            "suggestion": "Tente expandir seu orçamento ou selecionar um estado próximo"
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
