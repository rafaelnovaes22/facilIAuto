"""
Modelo de Concessionária para a plataforma unificada FacilIAuto
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class Dealership(BaseModel):
    """
    Modelo representando uma concessionária na plataforma
    """
    id: str  # "robustcar", "autocenter", "carplus"
    name: str  # "RobustCar São Paulo"
    city: str
    state: str  # "SP", "RJ", "MG"
    region: str  # "Sudeste", "Sul", "Nordeste"
    
    # Contato
    phone: str
    whatsapp: str
    email: Optional[str] = None
    website: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#0ea5e9"  # Default azul
    
    # Address
    address: Optional[str] = None
    zip_code: Optional[str] = None
    
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

