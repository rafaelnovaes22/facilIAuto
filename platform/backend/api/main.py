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
from services.unified_recommendation_engine import UnifiedRecommendationEngine

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

# Inicializar engine
data_dir = os.path.join(backend_dir, "data")
engine = UnifiedRecommendationEngine(data_dir=data_dir)


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
        
        # Formatar resposta
        return {
            "total_recommendations": len(recommendations),
            "profile_summary": {
                "budget_range": f"R$ {profile.orcamento_min:,.0f} - R$ {profile.orcamento_max:,.0f}",
                "usage": profile.uso_principal,
                "location": f"{profile.city or 'N/A'}, {profile.state or 'N/A'}"
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
    
    return {
        "platform": {
            "total_dealerships": stats['total_dealerships'],
            "active_dealerships": stats['active_dealerships'],
            "total_cars": stats['total_cars'],
            "available_cars": stats['available_cars']
        },
        "dealerships_by_state": stats['dealerships_by_state'],
        "cars_by_category": stats['cars_by_category']
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


# Para testes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

