"""
🤖 ML System: Modelos de Interação para Coleta de Dados

Captura interações dos usuários com veículos para treinamento de ML.

Autor: AI Engineer
Data: Outubro 2024
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class InteractionType(str, Enum):
    """Tipos de interação do usuário com veículos"""
    CLICK = "click"                      # Clicou no card do carro
    VIEW_DETAILS = "view_details"        # Visualizou detalhes do carro
    WHATSAPP_CONTACT = "whatsapp_contact"  # Clicou para contatar via WhatsApp


class UserPreferencesSnapshot(BaseModel):
    """
    Snapshot das preferências do usuário no momento da interação
    """
    budget: float = Field(..., description="Orçamento do usuário")
    usage: str = Field(..., description="Tipo de uso: urbano, misto, estrada")
    priorities: List[str] = Field(default_factory=list, description="Prioridades: economia, conforto, desempenho")
    
    class Config:
        json_schema_extra = {
            "example": {
                "budget": 120000,
                "usage": "urbano",
                "priorities": ["economia", "conforto"]
            }
        }


class CarSnapshot(BaseModel):
    """
    Snapshot dos dados do carro no momento da interação
    """
    marca: str
    modelo: str
    ano: int
    preco: float
    categoria: str
    combustivel: str
    cambio: str
    quilometragem: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "marca": "Toyota",
                "modelo": "Corolla",
                "ano": 2022,
                "preco": 115990,
                "categoria": "Sedan",
                "combustivel": "Flex",
                "cambio": "Automático",
                "quilometragem": 25000
            }
        }


class InteractionEvent(BaseModel):
    """
    Evento de interação do usuário com um veículo
    
    Este modelo captura todas as informações necessárias para
    treinar o modelo de ML posteriormente.
    """
    # Identificadores
    session_id: str = Field(..., description="ID único da sessão do usuário (anônimo)")
    car_id: str = Field(..., description="ID do carro com o qual o usuário interagiu")
    
    # Tipo e timing
    interaction_type: InteractionType = Field(..., description="Tipo de interação")
    timestamp: datetime = Field(default_factory=datetime.now, description="Momento da interação")
    duration_seconds: Optional[int] = Field(None, description="Duração da visualização em segundos")
    
    # Contexto da interação
    user_preferences: UserPreferencesSnapshot = Field(..., description="Preferências do usuário no momento")
    car_snapshot: Optional[CarSnapshot] = Field(None, description="Dados do carro no momento")
    
    # Metadados adicionais
    recommendation_position: Optional[int] = Field(None, description="Posição do carro na lista de recomendações (1-N)")
    score: Optional[float] = Field(None, description="Score de recomendação calculado pelo sistema de regras")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "car_id": "car_robust_001",
                "interaction_type": "whatsapp_contact",
                "timestamp": "2024-10-14T15:30:00Z",
                "duration_seconds": 45,
                "user_preferences": {
                    "budget": 120000,
                    "usage": "urbano",
                    "priorities": ["economia", "conforto"]
                },
                "car_snapshot": {
                    "marca": "Toyota",
                    "modelo": "Corolla",
                    "ano": 2022,
                    "preco": 115990,
                    "categoria": "Sedan",
                    "combustivel": "Flex",
                    "cambio": "Automático",
                    "quilometragem": 25000
                },
                "recommendation_position": 1,
                "score": 0.92
            }
        }


class InteractionStats(BaseModel):
    """
    Estatísticas agregadas de interações
    """
    total_interactions: int = 0
    click_count: int = 0
    view_details_count: int = 0
    whatsapp_contact_count: int = 0
    unique_sessions: int = 0
    unique_cars: int = 0
    avg_duration_seconds: Optional[float] = None
    last_interaction: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_interactions": 1250,
                "click_count": 800,
                "view_details_count": 350,
                "whatsapp_contact_count": 100,
                "unique_sessions": 450,
                "unique_cars": 120,
                "avg_duration_seconds": 32.5,
                "last_interaction": "2024-10-14T15:30:00Z"
            }
        }
