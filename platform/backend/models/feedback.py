"""
🤖 AI Engineer: Modelos de Feedback para Sistema Iterativo (FASE 2)

Permite que usuários refinem recomendações através de feedback
até encontrar o match ideal.

Autor: AI Engineer
Data: Outubro 2024
"""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class FeedbackAction(str, Enum):
    """Ações possíveis de feedback do usuário"""
    LIKED = "liked"                    # Gostou do carro
    DISLIKED = "disliked"              # Não gostou do carro
    CLICKED_WHATSAPP = "clicked_whatsapp"  # Clicou para contato
    VIEWED_DETAILS = "viewed_details"   # Visualizou detalhes
    COMPARED = "compared"              # Comparou com outros


class UserFeedback(BaseModel):
    """
    Feedback do usuário sobre uma recomendação específica
    """
    user_id: str
    car_id: str
    action: FeedbackAction
    timestamp: datetime = datetime.now()
    
    # Informações adicionais do carro (para análise)
    car_marca: Optional[str] = None
    car_categoria: Optional[str] = None
    car_preco: Optional[float] = None
    car_ano: Optional[int] = None
    car_score: Optional[float] = None
    
    # Contexto da recomendação
    recommendation_position: Optional[int] = None  # Posição na lista (1-10)
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "car_id": "car_robust_001",
                "action": "liked",
                "car_marca": "Toyota",
                "car_categoria": "Sedan",
                "car_preco": 115990,
                "car_ano": 2022,
                "car_score": 0.92,
                "recommendation_position": 1,
                "session_id": "session_abc123"
            }
        }


class UserInteractionHistory(BaseModel):
    """
    Histórico completo de interações de um usuário
    """
    user_id: str
    feedbacks: List[UserFeedback] = []
    total_interactions: int = 0
    liked_count: int = 0
    disliked_count: int = 0
    clicked_whatsapp_count: int = 0
    
    # Padrões identificados
    preferred_brands: List[str] = []
    preferred_categories: List[str] = []
    avg_price_liked: Optional[float] = None
    avg_year_liked: Optional[float] = None
    
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    def add_feedback(self, feedback: UserFeedback):
        """Adicionar feedback e atualizar estatísticas"""
        self.feedbacks.append(feedback)
        self.total_interactions += 1
        
        if feedback.action == FeedbackAction.LIKED:
            self.liked_count += 1
        elif feedback.action == FeedbackAction.DISLIKED:
            self.disliked_count += 1
        elif feedback.action == FeedbackAction.CLICKED_WHATSAPP:
            self.clicked_whatsapp_count += 1
        
        self.updated_at = datetime.now()
        
        # Atualizar padrões
        self._update_patterns()
    
    def _update_patterns(self):
        """Identificar padrões de preferência"""
        liked_feedbacks = [f for f in self.feedbacks if f.action == FeedbackAction.LIKED]
        
        if not liked_feedbacks:
            return
        
        # Marcas preferidas
        brands = [f.car_marca for f in liked_feedbacks if f.car_marca]
        self.preferred_brands = list(set(brands))
        
        # Categorias preferidas
        categories = [f.car_categoria for f in liked_feedbacks if f.car_categoria]
        self.preferred_categories = list(set(categories))
        
        # Preço médio dos carros curtidos
        prices = [f.car_preco for f in liked_feedbacks if f.car_preco]
        if prices:
            self.avg_price_liked = sum(prices) / len(prices)
        
        # Ano médio dos carros curtidos
        years = [f.car_ano for f in liked_feedbacks if f.car_ano]
        if years:
            self.avg_year_liked = sum(years) / len(years)


class WeightAdjustment(BaseModel):
    """
    Ajuste de pesos baseado em feedback
    """
    user_id: str
    original_weights: Dict[str, float]
    adjusted_weights: Dict[str, float]
    adjustment_reason: str
    confidence_score: float  # 0-1 (confiança no ajuste)
    feedbacks_analyzed: int
    timestamp: datetime = datetime.now()
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "original_weights": {
                    "economia": 0.3,
                    "espaco": 0.2,
                    "performance": 0.2,
                    "conforto": 0.15,
                    "seguranca": 0.15
                },
                "adjusted_weights": {
                    "economia": 0.25,
                    "espaco": 0.15,
                    "performance": 0.25,  # Aumentou (usuário gostou de carros potentes)
                    "conforto": 0.20,     # Aumentou
                    "seguranca": 0.15
                },
                "adjustment_reason": "Usuário curtiu carros com maior performance e conforto",
                "confidence_score": 0.75,
                "feedbacks_analyzed": 5
            }
        }


class RefinementRequest(BaseModel):
    """
    Requisição de refinamento de recomendações
    """
    user_id: str
    session_id: Optional[str] = None
    current_profile: Dict  # UserProfile como dict
    feedbacks: List[UserFeedback]
    max_iterations: int = 5  # Máximo de iterações
    target_score: float = 0.85  # Score mínimo desejado
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "session_id": "session_abc",
                "current_profile": {
                    "orcamento_min": 80000,
                    "orcamento_max": 120000,
                    "uso_principal": "familia"
                },
                "feedbacks": [
                    {
                        "user_id": "user_123",
                        "car_id": "car_001",
                        "action": "liked",
                        "car_categoria": "SUV"
                    }
                ],
                "max_iterations": 5,
                "target_score": 0.85
            }
        }


class RefinementResponse(BaseModel):
    """
    Resposta com recomendações refinadas
    """
    user_id: str
    session_id: str
    iteration: int
    converged: bool  # True se encontrou match ideal
    best_score: float
    weight_adjustments: WeightAdjustment
    recommendations: List[Dict]
    insights: List[str]  # Insights sobre as preferências
    next_steps: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "session_id": "session_abc",
                "iteration": 3,
                "converged": True,
                "best_score": 0.89,
                "weight_adjustments": {},
                "recommendations": [],
                "insights": [
                    "Você prefere SUVs com boa performance",
                    "Conforto é mais importante que economia para você"
                ],
                "next_steps": "Encontramos o match ideal! 3 carros com score > 85%"
            }
        }

