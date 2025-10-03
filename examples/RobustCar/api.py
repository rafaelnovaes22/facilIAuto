#!/usr/bin/env python3
"""
🚀 RobustCar API - FastAPI Backend
Agente Responsável: Tech Lead 💻

API REST para conectar frontend React com sistema de recomendação
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
import json
from datetime import datetime
import logging

from recommendation_engine import (
    RobustCarRecommendationEngine, 
    UserProfile, 
    CarRecommendation,
    CarData
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global engine instance
engine: Optional[RobustCarRecommendationEngine] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler para FastAPI"""
    # Startup
    global engine
    try:
        # Buscar arquivo de estoque mais recente
        import glob
        import os
        
        estoque_files = glob.glob("robustcar_estoque_*.json")
        if not estoque_files:
            logger.error("Nenhum arquivo de estoque encontrado")
            yield
            return
        
        # Usar arquivo mais recente
        latest_file = max(estoque_files, key=os.path.getctime)
        logger.info(f"Carregando estoque de: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            carros_data = json.load(f)
        
        # Inicializar engine
        engine = RobustCarRecommendationEngine(carros_data)
        logger.info(f"✅ Engine inicializada com {len(carros_data)} carros")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar engine: {e}")
        engine = None
    
    yield
    
    # Shutdown (cleanup se necessário)
    logger.info("🔄 Finalizando aplicação")

# FastAPI app
app = FastAPI(
    title="RobustCar Recommendation API",
    description="Sistema de recomendação de carros para RobustCar",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models para API
class QuestionnaireRequest(BaseModel):
    """Request do questionário do usuário"""
    orcamento_min: float
    orcamento_max: float
    uso_principal: str  # trabalho, familia, lazer, primeiro_carro
    tamanho_familia: int = 1
    prioridades: Dict[str, int]  # economia, espaco, performance, conforto, seguranca (1-5)
    marcas_preferidas: List[str] = []
    tipos_preferidos: List[str] = []  # hatch, sedan, suv
    combustivel_preferido: str = "Flex"
    idade_usuario: int = 30
    experiencia_conducao: str = "intermediario"  # iniciante, intermediario, experiente

class CarResponse(BaseModel):
    """Response de um carro"""
    id: str
    nome: str
    marca: str
    modelo: str
    ano: int
    preco: float
    quilometragem: int
    combustivel: str
    cambio: str
    cor: str
    categoria: str
    imagens: List[str]
    url_original: str
    disponivel: bool

class RecommendationResponse(BaseModel):
    """Response de uma recomendação"""
    carro: CarResponse
    score: float
    justificativa: str
    pontos_fortes: List[str]
    pontos_atencao: List[str]
    match_percentage: int

class EstoqueStats(BaseModel):
    """Estatísticas do estoque"""
    total_carros: int
    preco_medio: float
    por_marca: Dict[str, int]
    por_categoria: Dict[str, int]
    por_faixa_preco: Dict[str, int]
    ultima_atualizacao: str

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "RobustCar Recommendation API",
        "version": "1.0.0",
        "status": "online",
        "carros_disponivel": len(engine.estoque) if engine else 0
    }

@app.get("/health")
async def health_check():
    """Health check do sistema"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine não inicializada")
    
    return {
        "status": "healthy",
        "carros_estoque": len(engine.estoque),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/estoque/stats", response_model=EstoqueStats)
async def get_estoque_stats():
    """Obter estatísticas do estoque"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine não inicializada")
    
    estoque = engine.estoque
    
    if not estoque:
        raise HTTPException(status_code=404, detail="Estoque vazio")
    
    # Calcular estatísticas
    carros_com_preco = [c for c in estoque if c.preco > 0]
    preco_medio = sum(c.preco for c in carros_com_preco) / len(carros_com_preco) if carros_com_preco else 0
    
    # Por marca
    por_marca = {}
    for carro in estoque:
        marca = carro.marca
        por_marca[marca] = por_marca.get(marca, 0) + 1
    
    # Por categoria
    por_categoria = {}
    for carro in estoque:
        categoria = carro.categoria or "Indefinido"
        por_categoria[categoria] = por_categoria.get(categoria, 0) + 1
    
    # Por faixa de preço
    por_faixa_preco = {
        "até_30k": len([c for c in estoque if 0 < c.preco <= 30000]),
        "30k_50k": len([c for c in estoque if 30000 < c.preco <= 50000]),
        "50k_80k": len([c for c in estoque if 50000 < c.preco <= 80000]),
        "80k_120k": len([c for c in estoque if 80000 < c.preco <= 120000]),
        "120k_mais": len([c for c in estoque if c.preco > 120000])
    }
    
    return EstoqueStats(
        total_carros=len(estoque),
        preco_medio=preco_medio,
        por_marca=por_marca,
        por_categoria=por_categoria,
        por_faixa_preco=por_faixa_preco,
        ultima_atualizacao=datetime.now().isoformat()
    )

@app.get("/carros/buscar")
async def buscar_carros(
    marca: Optional[str] = None,
    categoria: Optional[str] = None,
    preco_min: Optional[float] = None,
    preco_max: Optional[float] = None,
    limit: int = 20
):
    """Buscar carros com filtros"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine não inicializada")
    
    carros_filtrados = engine.estoque.copy()
    
    # Aplicar filtros
    if marca:
        carros_filtrados = [c for c in carros_filtrados if marca.lower() in c.marca.lower()]
    
    if categoria:
        carros_filtrados = [c for c in carros_filtrados if categoria.lower() in c.categoria.lower()]
    
    if preco_min:
        carros_filtrados = [c for c in carros_filtrados if c.preco >= preco_min]
    
    if preco_max:
        carros_filtrados = [c for c in carros_filtrados if c.preco <= preco_max]
    
    # Limitar resultados
    carros_filtrados = carros_filtrados[:limit]
    
    # Converter para response model
    carros_response = []
    for carro in carros_filtrados:
        carros_response.append(CarResponse(
            id=carro.id,
            nome=carro.nome,
            marca=carro.marca,
            modelo=carro.modelo,
            ano=carro.ano,
            preco=carro.preco,
            quilometragem=carro.quilometragem,
            combustivel=carro.combustivel,
            cambio=carro.cambio,
            cor=carro.cor,
            categoria=carro.categoria,
            imagens=carro.imagens,
            url_original=carro.url_original,
            disponivel=carro.disponivel
        ))
    
    return {
        "carros": carros_response,
        "total": len(carros_response),
        "filtros_aplicados": {
            "marca": marca,
            "categoria": categoria,
            "preco_min": preco_min,
            "preco_max": preco_max
        }
    }

@app.post("/recomendar", response_model=List[RecommendationResponse])
async def recomendar_carros(request: QuestionnaireRequest):
    """Endpoint principal - gerar recomendações baseadas no questionário"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine não inicializada")
    
    try:
        # Converter request para UserProfile
        perfil = UserProfile(
            orcamento_min=request.orcamento_min,
            orcamento_max=request.orcamento_max,
            uso_principal=request.uso_principal,
            tamanho_familia=request.tamanho_familia,
            prioridades=request.prioridades,
            marcas_preferidas=request.marcas_preferidas,
            tipos_preferidos=request.tipos_preferidos,
            combustivel_preferido=request.combustivel_preferido,
            idade_usuario=request.idade_usuario,
            experiencia_conducao=request.experiencia_conducao
        )
        
        # Gerar recomendações
        recomendacoes = engine.recomendar(perfil, limite=5)
        
        if not recomendacoes:
            raise HTTPException(
                status_code=404, 
                detail="Nenhuma recomendação encontrada para este perfil. Tente ajustar seus critérios."
            )
        
        # Converter para response model
        response_list = []
        for rec in recomendacoes:
            carro_response = CarResponse(
                id=rec.carro.id,
                nome=rec.carro.nome,
                marca=rec.carro.marca,
                modelo=rec.carro.modelo,
                ano=rec.carro.ano,
                preco=rec.carro.preco,
                quilometragem=rec.carro.quilometragem,
                combustivel=rec.carro.combustivel,
                cambio=rec.carro.cambio,
                cor=rec.carro.cor,
                categoria=rec.carro.categoria,
                imagens=rec.carro.imagens,
                url_original=rec.carro.url_original,
                disponivel=rec.carro.disponivel
            )
            
            rec_response = RecommendationResponse(
                carro=carro_response,
                score=rec.score,
                justificativa=rec.justificativa,
                pontos_fortes=rec.pontos_fortes,
                pontos_atencao=rec.pontos_atencao,
                match_percentage=rec.match_percentage
            )
            
            response_list.append(rec_response)
        
        logger.info(f"Recomendações geradas: {len(response_list)} para perfil {perfil.uso_principal}")
        return response_list
        
    except Exception as e:
        logger.error(f"Erro ao gerar recomendações: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/marcas")
async def get_marcas():
    """Obter lista de marcas disponíveis"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine não inicializada")
    
    marcas = set(carro.marca for carro in engine.estoque if carro.marca != "Genérica")
    return {"marcas": sorted(list(marcas))}

@app.get("/categorias")
async def get_categorias():
    """Obter lista de categorias disponíveis"""
    if not engine:
        raise HTTPException(status_code=503, detail="Engine não inicializada")
    
    categorias = set(carro.categoria for carro in engine.estoque if carro.categoria)
    return {"categorias": sorted(list(categorias))}

@app.post("/admin/atualizar-estoque")
async def atualizar_estoque():
    """Endpoint admin para forçar atualização do estoque"""
    global engine
    
    try:
        # Executar scraper
        import subprocess
        result = subprocess.run(["python", "robustcar_scraper.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Erro no scraping: {result.stderr}")
        
        # Recarregar engine
        import glob
        import os
        
        estoque_files = glob.glob("robustcar_estoque_*.json")
        if estoque_files:
            latest_file = max(estoque_files, key=os.path.getctime)
            engine = RobustCarRecommendationEngine(latest_file)
            
            return {
                "status": "success",
                "message": f"Estoque atualizado com {len(engine.estoque)} carros",
                "arquivo": latest_file,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Nenhum arquivo de estoque gerado")
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout no scraping")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
