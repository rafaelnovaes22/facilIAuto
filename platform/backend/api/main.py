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
from services.unified_recommendation_engine import UnifiedRecommendationEngine
from services.feedback_engine import FeedbackEngine

# Inicializar app
app = FastAPI(
    title="FacilIAuto API",
    description="API REST para plataforma multi-tenant de recomendação automotiva",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar engines
data_dir = os.path.join(backend_dir, "data")
engine = UnifiedRecommendationEngine(data_dir=data_dir)
feedback_engine = FeedbackEngine()  # 🤖 FASE 2: Engine de feedback


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


@app.get("/dealerships", response_model=List[Dealership])
def list_dealerships(
    active_only: bool = Query(True, description="Apenas concessionárias ativas")
):
    """
    Listar concessionárias
    """
    dealerships = engine.dealerships
    
    if active_only:
        dealerships = [d for d in dealerships if d.active]
    
    return dealerships


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


@app.post("/recommend")
def recommend_cars(profile: UserProfile):
    """
    Gerar recomendações personalizadas baseadas no perfil do usuário
    """
    try:
        # Validar orçamento
        if profile.orcamento_max < profile.orcamento_min:
            raise HTTPException(
                status_code=400,
                detail="Orçamento máximo deve ser maior que o mínimo"
            )
        
        # Gerar recomendações
        recommendations = engine.recommend(
            profile=profile,
            limit=10,
            score_threshold=0.2
        )
        
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
                        "categoria": rec['car'].categoria,
                        "imagens": rec['car'].imagens,
                        "dealership": {
                            "id": rec['car'].dealership_id,
                            "name": rec['car'].dealership_name,
                            "city": rec['car'].dealership_city,
                            "state": rec['car'].dealership_state,
                            "phone": rec['car'].dealership_phone,
                            "whatsapp": rec['car'].dealership_whatsapp
                        }
                    },
                    "match_score": rec['score'],
                    "match_percentage": rec['match_percentage'],
                    "justification": rec['justificativa']
                }
                for rec in recommendations
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar recomendações: {str(e)}")


@app.get("/stats")
def get_platform_stats():
    """
    Estatísticas gerais da plataforma
    """
    stats = engine.get_stats()
    
    # Calcular preços
    prices = [car.preco for car in engine.all_cars if car.disponivel]
    avg_price = sum(prices) / len(prices) if prices else 0
    
    # Agrupar por marca
    cars_by_brand = {}
    for car in engine.all_cars:
        if car.disponivel:
            cars_by_brand[car.marca] = cars_by_brand.get(car.marca, 0) + 1
    
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

@app.post("/feedback")
def submit_feedback(feedback: UserFeedback):
    """
    💻 Tech Lead (FASE 2): Receber feedback do usuário
    
    Ações possíveis:
    - "liked": Gostou do carro
    - "disliked": Não gostou
    - "clicked_whatsapp": Clicou para contato
    - "viewed_details": Visualizou detalhes
    - "compared": Comparou com outros
    
    Retorna histórico atualizado do usuário
    """
    try:
        # Adicionar feedback ao histórico
        history = feedback_engine.add_feedback(feedback)
        
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
    
    except Exception as e:
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
                        "categoria": rec['car'].categoria,
                        "imagens": rec['car'].imagens,
                        "dealership": {
                            "id": rec['car'].dealership_id,
                            "name": rec['car'].dealership_name,
                            "city": rec['car'].dealership_city,
                            "state": rec['car'].dealership_state,
                            "phone": rec['car'].dealership_phone,
                            "whatsapp": rec['car'].dealership_whatsapp
                        }
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


# Para testes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

