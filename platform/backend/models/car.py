"""
Modelo de Carro para a plataforma unificada FacilIAuto
"""

from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime


class Car(BaseModel):
    """
    Modelo de carro com referência à concessionária de origem
    """
    # Identificação
    id: str
    dealership_id: str  # Referência à concessionária
    
    # Informações básicas
    nome: str
    marca: str
    modelo: str
    versao: Optional[str] = None
    ano: int
    
    # Preço e condições
    preco: float
    quilometragem: int
    
    # Características
    combustivel: str  # "Flex", "Gasolina", "Diesel", "Elétrico"
    cambio: Optional[str] = "Manual"  # "Manual", "Automático", "CVT"
    cor: Optional[str] = None
    portas: Optional[int] = 4
    
    # Categorização (para recomendação)
    categoria: str  # "Hatch", "Sedan", "SUV", "Pickup", "Compacto"
    
    # 📊 Data Analyst: Itens de segurança e conforto (FASE 1)
    itens_seguranca: List[str] = []  # Ex: ["ISOFIX", "6_airbags", "controle_estabilidade", "ABS", "camera_re"]
    itens_conforto: List[str] = []  # Ex: ["ar_condicionado", "direcao_eletrica", "vidro_eletrico", "sensor_estacionamento"]
    
    # Scores de IA (0.0 a 1.0)
    score_familia: float = 0.5
    score_economia: float = 0.5
    score_performance: float = 0.5
    score_conforto: float = 0.5
    score_seguranca: float = 0.5
    
    # 📊 Data Analyst: Métricas de "Carro Bom" (FASE 3)
    indice_revenda: float = 0.5              # 0-1 (liquidez + relação com FIPE)
    taxa_depreciacao_anual: float = 0.15     # % ao ano (ex: 0.15 = 15%/ano)
    custo_manutencao_anual: Optional[float] = None  # R$/ano estimado
    indice_confiabilidade: float = 0.5       # 0-1 (recalls, problemas conhecidos)
    
    # Mídia
    imagens: List[str] = []
    url_original: Optional[str] = None
    
    # Status
    disponivel: bool = True
    destaque: bool = False
    
    # Metadata
    data_scraping: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None
    
    # Informações da concessionária (denormalizado para performance)
    dealership_name: str
    dealership_city: str
    dealership_state: str
    dealership_phone: str
    dealership_whatsapp: str
    dealership_latitude: Optional[float] = None  # 🏗️ System Architecture: Para cálculo de distância
    dealership_longitude: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "robust_001",
                "dealership_id": "robustcar",
                "nome": "FIAT CRONOS DRIVE 1.3",
                "marca": "Fiat",
                "modelo": "Cronos",
                "versao": "Drive 1.3",
                "ano": 2022,
                "preco": 84990.0,
                "quilometragem": 35000,
                "combustivel": "Flex",
                "cambio": "Manual",
                "categoria": "Sedan",
                "score_familia": 0.8,
                "score_economia": 0.9,
                "imagens": ["https://example.com/car1.jpg"],
                "disponivel": True,
                "dealership_name": "RobustCar São Paulo",
                "dealership_city": "São Paulo",
                "dealership_state": "SP",
                "dealership_phone": "(11) 1234-5678",
                "dealership_whatsapp": "5511987654321"
            }
        }


class CarFilter(BaseModel):
    """Filtros para busca de carros"""
    preco_min: Optional[float] = None
    preco_max: Optional[float] = None
    marca: Optional[str] = None
    categoria: Optional[str] = None
    combustivel: Optional[str] = None
    ano_min: Optional[int] = None
    km_max: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    dealership_id: Optional[str] = None

