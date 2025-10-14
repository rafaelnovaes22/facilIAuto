"""
Modelo de Concessionária para a plataforma unificada FacilIAuto
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Any
from datetime import datetime


class Dealership(BaseModel):
    """
    Modelo representando uma concessionária na plataforma
    """
    id: str  # "robustcar", "autocenter", "carplus"
    name: str = Field(alias="nome")  # "RobustCar São Paulo"
    city: str = Field(alias="cidade")
    state: str = Field(alias="estado")  # "SP", "RJ", "MG"
    region: str = Field(default="Sudeste", alias="regiao")  # "Sudeste", "Sul", "Nordeste"
    
    # Contato
    phone: str = Field(alias="telefone")
    whatsapp: str
    email: Optional[str] = None
    website: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#0ea5e9"  # Default azul
    
    # Address
    address: Optional[str] = None
    zip_code: Optional[str] = None
    
    # 🏗️ System Architecture: Coordenadas geográficas (FASE 1)
    latitude: Optional[float] = None  # Ex: -23.5505 (São Paulo)
    longitude: Optional[float] = None  # Ex: -46.6333 (São Paulo)
    
    # Carros da concessionária (armazenados no mesmo JSON)
    carros: List[Any] = []  # Lista de carros (dict ou Car objects)
    
    # Status
    active: bool = True
    verified: bool = False
    premium: bool = False
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Stats (opcional, calculado dinamicamente)
    total_cars: Optional[int] = 0
    avg_price: Optional[float] = 0
    
    class Config:
        populate_by_name = True  # Aceitar tanto 'name' quanto 'nome'
        json_schema_extra = {
            "example": {
                "id": "robustcar",
                "name": "RobustCar São Paulo",
                "city": "São Paulo",
                "state": "SP",
                "region": "Sudeste",
                "phone": "(11) 1234-5678",
                "whatsapp": "5511987654321",
                "email": "contato@robustcar.com.br",
                "website": "https://robustcar.com.br",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "active": True,
                "verified": True,
                "premium": False
            }
        }


class DealershipStats(BaseModel):
    """Estatísticas de uma concessionária"""
    dealership_id: str
    total_cars: int
    active_cars: int
    avg_price: float
    price_min: float
    price_max: float
    total_recommendations: int
    conversion_rate: float
    last_updated: datetime

