"""
🚗 CarFinder - Sistema de Recomendação Prático de Carros

Sistema focado nos critérios reais de escolha:
- Orçamento (filtro principal)
- Motivo real de compra
- Frequência de uso
- Necessidades práticas de espaço
- Economia de combustível
- Confiabilidade e custo de manutenção
- Valor de revenda
- Preferências pessoais ("eu quero")
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import sqlite3
import uvicorn
import logging
from datetime import datetime
import json

from recommendations import CarRecommender

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CarFinder API",
    description="Sistema prático de recomendação de carros baseado em necessidades reais",
    version="2.0.0"
)

# Modelos Pydantic atualizados
class QuestionnaireRequest(BaseModel):
    answers: Dict[str, Any] = Field(..., description="Respostas do questionário prático")
    details: Optional[str] = Field(None, description="Detalhes específicos do usuário")
    session_id: str = Field(..., description="ID da sessão")
    timestamp: Optional[str] = Field(None, description="Timestamp da submissão")

class CarResponse(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    price: int
    category: str
    fuel_type: str
    transmission: str
    consumption: float
    seats: int
    safety_rating: int
    region: str
    photo_url: Optional[str]
    available: bool
    # Novos campos práticos
    reliability_score: Optional[float] = Field(None, description="Score de confiabilidade (0-100)")
    resale_score: Optional[float] = Field(None, description="Score de revenda (0-100)")
    maintenance_cost: Optional[str] = Field(None, description="Custo de manutenção")

class RecommendationResponse(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    price: int
    category: str
    transmission: str
    consumption: float
    score: float
    reasons: List[str]
    photo_url: Optional[str]
    # Adicionais práticos
    reliability_score: Optional[float]
    resale_score: Optional[float]
    maintenance_cost: Optional[str]

class LeadRequest(BaseModel):
    car_id: int
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    message: Optional[str] = Field(None, max_length=500)

class RecommendationsResult(BaseModel):
    recommendations: List[RecommendationResponse]
    total_found: int
    session_id: str
    criteria_used: Dict[str, Any]

# Instanciar o recomendador
recommender = CarRecommender()

def init_db():
    """Inicializar banco SQLite com esquema atualizado"""
    conn = sqlite3.connect('carfinder.db')
    cursor = conn.cursor()
    
    # Tabela de carros com campos adicionais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price INTEGER NOT NULL,
            category TEXT NOT NULL,
            fuel_type TEXT DEFAULT 'flex',
            transmission TEXT NOT NULL,
            consumption REAL NOT NULL,
            seats INTEGER DEFAULT 5,
            safety_rating INTEGER DEFAULT 4,
            region TEXT DEFAULT 'sp',
            photo_url TEXT,
            available BOOLEAN DEFAULT 1,
            reliability_score REAL,
            resale_score REAL,
            maintenance_cost TEXT
        )
    ''')
    
    # Tabela de leads
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (car_id) REFERENCES cars (id)
        )
    ''')
    
    conn.commit()
    
    # Popular com carros se estiver vazio
    cursor.execute('SELECT COUNT(*) FROM cars')
    if cursor.fetchone()[0] == 0:
        seed_cars(cursor)
        conn.commit()
    
    conn.close()
    logger.info("Banco de dados inicializado com sucesso")

def seed_cars(cursor):
    """Popular banco com carros práticos e dados realistas"""
    cars_data = [
        # === CARROS PARA TRABALHO (UBER/99) ===
        {
            "brand": "Chevrolet", "model": "Onix", "year": 2022, "price": 45000,
            "category": "hatch", "fuel_type": "flex", "transmission": "manual",
            "consumption": 14.2, "seats": 5, "safety_rating": 4, "region": "sp",
            "reliability_score": 80, "resale_score": 78, "maintenance_cost": "Baixo"
        },
        {
            "brand": "Honda", "model": "City", "year": 2021, "price": 55000,
            "category": "sedan", "fuel_type": "flex", "transmission": "manual",
            "consumption": 13.8, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 92, "resale_score": 88, "maintenance_cost": "Médio"
        },
        {
            "brand": "Toyota", "model": "Etios", "year": 2020, "price": 42000,
            "category": "hatch", "fuel_type": "flex", "transmission": "manual",
            "consumption": 14.5, "seats": 5, "safety_rating": 4, "region": "sp",
            "reliability_score": 95, "resale_score": 85, "maintenance_cost": "Baixo"
        },
        {
            "brand": "Hyundai", "model": "HB20", "year": 2022, "price": 48000,
            "category": "hatch", "fuel_type": "flex", "transmission": "manual",
            "consumption": 13.9, "seats": 5, "safety_rating": 4, "region": "sp",
            "reliability_score": 88, "resale_score": 80, "maintenance_cost": "Médio"
        },
        
        # === CARROS FAMILIARES ===
        {
            "brand": "Honda", "model": "Civic", "year": 2020, "price": 85000,
            "category": "sedan", "fuel_type": "flex", "transmission": "automatic",
            "consumption": 11.5, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 92, "resale_score": 88, "maintenance_cost": "Médio"
        },
        {
            "brand": "Toyota", "model": "Corolla", "year": 2021, "price": 92000,
            "category": "sedan", "fuel_type": "flex", "transmission": "automatic",
            "consumption": 12.2, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 95, "resale_score": 90, "maintenance_cost": "Médio"
        },
        {
            "brand": "Volkswagen", "model": "Jetta", "year": 2019, "price": 78000,
            "category": "sedan", "fuel_type": "flex", "transmission": "automatic",
            "consumption": 11.8, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 78, "resale_score": 82, "maintenance_cost": "Alto"
        },
        {
            "brand": "Hyundai", "model": "Creta", "year": 2021, "price": 89000,
            "category": "suv", "fuel_type": "flex", "transmission": "automatic",
            "consumption": 10.8, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 88, "resale_score": 85, "maintenance_cost": "Médio"
        },
        
        # === PRIMEIRO CARRO ===
        {
            "brand": "Chevrolet", "model": "Onix Joy", "year": 2018, "price": 32000,
            "category": "hatch", "fuel_type": "flex", "transmission": "manual",
            "consumption": 13.8, "seats": 5, "safety_rating": 3, "region": "sp",
            "reliability_score": 75, "resale_score": 70, "maintenance_cost": "Baixo"
        },
        {
            "brand": "Ford", "model": "Ka", "year": 2019, "price": 35000,
            "category": "hatch", "fuel_type": "flex", "transmission": "manual",
            "consumption": 14.1, "seats": 5, "safety_rating": 4, "region": "sp",
            "reliability_score": 77, "resale_score": 72, "maintenance_cost": "Baixo"
        },
        {
            "brand": "Fiat", "model": "Argo", "year": 2018, "price": 38000,
            "category": "hatch", "fuel_type": "flex", "transmission": "manual",
            "consumption": 13.2, "seats": 5, "safety_rating": 4, "region": "sp",
            "reliability_score": 65, "resale_score": 68, "maintenance_cost": "Baixo"
        },
        
        # === UPGRADE/CONFORTO ===
        {
            "brand": "Honda", "model": "CR-V", "year": 2020, "price": 135000,
            "category": "suv", "fuel_type": "flex", "transmission": "automatic",
            "consumption": 9.8, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 92, "resale_score": 88, "maintenance_cost": "Alto"
        },
        {
            "brand": "Toyota", "model": "Hilux", "year": 2021, "price": 180000,
            "category": "pickup", "fuel_type": "diesel", "transmission": "automatic",
            "consumption": 11.5, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 95, "resale_score": 95, "maintenance_cost": "Médio"
        },
        {
            "brand": "Volkswagen", "model": "Tiguan", "year": 2020, "price": 125000,
            "category": "suv", "fuel_type": "flex", "transmission": "automatic",
            "consumption": 9.2, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 78, "resale_score": 80, "maintenance_cost": "Alto"
        },
        
        # === INVESTIMENTO/REVENDA ===
        {
            "brand": "Toyota", "model": "SW4", "year": 2020, "price": 220000,
            "category": "suv", "fuel_type": "diesel", "transmission": "automatic",
            "consumption": 10.2, "seats": 7, "safety_rating": 5, "region": "sp",
            "reliability_score": 95, "resale_score": 92, "maintenance_cost": "Alto"
        },
        {
            "brand": "Honda", "model": "HR-V", "year": 2021, "price": 95000,
            "category": "suv", "fuel_type": "flex", "transmission": "automatic",
            "consumption": 11.2, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 90, "resale_score": 86, "maintenance_cost": "Médio"
        },
        
        # === OPÇÕES PREMIUM ===
        {
            "brand": "BMW", "model": "X1", "year": 2019, "price": 150000,
            "category": "suv", "fuel_type": "flex", "transmission": "automatic",
            "consumption": 8.5, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 72, "resale_score": 75, "maintenance_cost": "Muito Alto"
        },
        {
            "brand": "Audi", "model": "A3", "year": 2020, "price": 140000,
            "category": "sedan", "fuel_type": "flex", "transmission": "automatic",
            "consumption": 9.8, "seats": 5, "safety_rating": 5, "region": "sp",
            "reliability_score": 75, "resale_score": 78, "maintenance_cost": "Muito Alto"
        },
        
        # === ECONÔMICOS ===
        {
            "brand": "Renault", "model": "Kwid", "year": 2020, "price": 28000,
            "category": "hatch", "fuel_type": "flex", "transmission": "manual",
            "consumption": 15.2, "seats": 5, "safety_rating": 3, "region": "sp",
            "reliability_score": 70, "resale_score": 65, "maintenance_cost": "Baixo"
        },
        {
            "brand": "Nissan", "model": "March", "year": 2019, "price": 33000,
            "category": "hatch", "fuel_type": "flex", "transmission": "manual",
            "consumption": 14.8, "seats": 5, "safety_rating": 4, "region": "sp",
            "reliability_score": 85, "resale_score": 75, "maintenance_cost": "Médio"
        }
    ]
    
    for car in cars_data:
        cursor.execute('''
            INSERT INTO cars (brand, model, year, price, category, fuel_type, transmission, 
                            consumption, seats, safety_rating, region, reliability_score, 
                            resale_score, maintenance_cost, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            car["brand"], car["model"], car["year"], car["price"],
            car["category"], car["fuel_type"], car["transmission"],
            car["consumption"], car["seats"], car["safety_rating"],
            car["region"], car["reliability_score"], car["resale_score"],
            car["maintenance_cost"], True
        ))
    
    logger.info(f"Cadastrados {len(cars_data)} carros com dados práticos")

def get_cars_from_db() -> List[Dict]:
    """Buscar carros do banco de dados"""
    conn = sqlite3.connect('carfinder.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM cars WHERE available = 1 ORDER BY brand, model
    ''')
    
    cars = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return cars

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Servir página inicial do questionário"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Página não encontrada")

@app.get("/results.html", response_class=HTMLResponse)
async def serve_results():
    """Servir página de resultados"""
    try:
        with open("static/results.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Página não encontrada")

@app.get("/admin.html", response_class=HTMLResponse)
async def serve_admin():
    """Servir dashboard administrativo"""
    try:
        with open("static/admin.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Página não encontrada")

@app.post("/api/recommendations", response_model=RecommendationsResult)
async def get_recommendations(request: QuestionnaireRequest):
    """
    Endpoint principal: processar questionário e retornar recomendações práticas
    """
    try:
        logger.info(f"Processando recomendações para sessão: {request.session_id}")
        logger.info(f"Respostas recebidas: {request.answers}")
        
        # Buscar carros do banco
        cars_data = get_cars_from_db()
        
        if not cars_data:
            logger.warning("Nenhum carro encontrado no banco de dados")
            return RecommendationsResult(
                recommendations=[],
                total_found=0,
                session_id=request.session_id,
                criteria_used=request.answers
            )
        
        # Gerar recomendações usando novo algoritmo
        recommendations = recommender.recommend(request.answers, cars_data)
        
        # Converter para formato de resposta
        formatted_recommendations = []
        for rec in recommendations:
            car = rec['car']
            formatted_rec = RecommendationResponse(
                id=car['id'],
                brand=car['brand'],
                model=car['model'],
                year=car['year'],
                price=car['price'],
                category=car['category'],
                transmission=car['transmission'],
                consumption=car['consumption'],
                score=rec['score'],
                reasons=rec['reasons'],
                photo_url=car.get('photo_url'),
                reliability_score=car.get('reliability_score'),
                resale_score=car.get('resale_score'),
                maintenance_cost=car.get('maintenance_cost')
            )
            formatted_recommendations.append(formatted_rec)
        
        logger.info(f"Geradas {len(formatted_recommendations)} recomendações")
        
        return RecommendationsResult(
            recommendations=formatted_recommendations,
            total_found=len(recommendations),
            session_id=request.session_id,
            criteria_used=request.answers
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar recomendações: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/cars/{car_id}", response_model=CarResponse)
async def get_car_details(car_id: int):
    """Buscar detalhes de um carro específico"""
    try:
        conn = sqlite3.connect('carfinder.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cars WHERE id = ? AND available = 1', (car_id,))
        car = cursor.fetchone()
        conn.close()
        
        if not car:
            raise HTTPException(status_code=404, detail="Carro não encontrado")
        
        return CarResponse(**dict(car))
        
    except Exception as e:
        logger.error(f"Erro ao buscar carro {car_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/api/leads")
async def create_lead(lead: LeadRequest):
    """Criar novo lead de interesse"""
    try:
        conn = sqlite3.connect('carfinder.db')
        cursor = conn.cursor()
        
        # Verificar se o carro existe
        cursor.execute('SELECT id FROM cars WHERE id = ? AND available = 1', (lead.car_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Carro não encontrado")
        
        # Inserir lead
        cursor.execute('''
            INSERT INTO leads (car_id, name, phone, email, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (lead.car_id, lead.name, lead.phone, lead.email, lead.message))
        
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Lead criado: {lead_id} para carro {lead.car_id}")
        
        return {"status": "success", "lead_id": lead_id, "message": "Interesse registrado com sucesso!"}
        
    except Exception as e:
        logger.error(f"Erro ao criar lead: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/admin/stats")
async def get_admin_stats():
    """Estatísticas para dashboard administrativo"""
    try:
        conn = sqlite3.connect('carfinder.db')
        cursor = conn.cursor()
        
        # Total de carros
        cursor.execute('SELECT COUNT(*) FROM cars WHERE available = 1')
        total_cars = cursor.fetchone()[0]
        
        # Total de leads
        cursor.execute('SELECT COUNT(*) FROM leads')
        total_leads = cursor.fetchone()[0]
        
        # Leads hoje
        cursor.execute('''
            SELECT COUNT(*) FROM leads 
            WHERE DATE(created_at) = DATE('now')
        ''')
        leads_today = cursor.fetchone()[0]
        
        # Carros mais procurados
        cursor.execute('''
            SELECT c.brand, c.model, COUNT(l.id) as lead_count
            FROM cars c
            LEFT JOIN leads l ON c.id = l.car_id
            WHERE c.available = 1
            GROUP BY c.id, c.brand, c.model
            ORDER BY lead_count DESC
            LIMIT 5
        ''')
        popular_cars = [
            {"brand": row[0], "model": row[1], "leads": row[2]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        # Taxa de conversão básica
        conversion_rate = (leads_today / max(1, total_cars)) * 100
        
        return {
            "total_cars": total_cars,
            "total_leads": total_leads,
            "leads_today": leads_today,
            "conversion_rate": round(conversion_rate, 2),
            "popular_cars": popular_cars
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/admin/leads")
async def get_admin_leads():
    """Lista de leads para administração"""
    try:
        conn = sqlite3.connect('carfinder.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                l.id, l.name, l.phone, l.email, l.message, l.created_at,
                l.car_id, c.brand, c.model, c.year, c.price
            FROM leads l
            JOIN cars c ON l.car_id = c.id
            ORDER BY l.created_at DESC
            LIMIT 100
        ''')
        
        leads = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {"leads": leads}
        
    except Exception as e:
        logger.error(f"Erro ao buscar leads: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/health")
async def health_check():
    """Health check do sistema"""
    try:
        # Testar conexão com banco
        conn = sqlite3.connect('carfinder.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM cars')
        car_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "ok",
            "service": "CarFinder",
            "version": "2.0.0",
            "database": "connected",
            "cars_available": car_count,
            "features": [
                "practical_questionnaire",
                "smart_recommendations", 
                "reliability_data",
                "resale_analysis",
                "maintenance_costs",
                "lead_generation"
            ]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Inicializar banco de dados
    init_db()
    
    # Executar servidor
    logger.info("🚗 Iniciando CarFinder v2.0 - Sistema Prático de Recomendação")
    logger.info("📊 Novos recursos: Confiabilidade, Revenda, Manutenção")
    logger.info("🎯 Critérios práticos: Motivo, Frequência, Espaço, Economia")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )