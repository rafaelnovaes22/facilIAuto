"""
🧪 Tech Lead: Testes para Sistema de Feedback Iterativo - FASE 2

Testa:
- Modelo de feedback
- Algoritmo de ajuste de pesos
- Convergência
- Endpoints da API

Autor: Tech Lead
Data: Outubro 2024
"""

import pytest
from datetime import datetime

from models.feedback import (
    FeedbackAction,
    UserFeedback,
    UserInteractionHistory,
    WeightAdjustment,
    RefinementRequest
)
from models.user_profile import UserProfile
from services.feedback_engine import FeedbackEngine


class TestUserFeedback:
    """Testes para modelo UserFeedback"""
    
    def test_create_feedback_liked(self):
        """Criar feedback 'gostei'"""
        feedback = UserFeedback(
            user_id="user_123",
            car_id="car_001",
            action=FeedbackAction.LIKED,
            car_marca="Toyota",
            car_categoria="Sedan",
            car_preco=115990,
            car_ano=2022,
            car_score=0.92
        )
        
        assert feedback.user_id == "user_123"
        assert feedback.action == FeedbackAction.LIKED
        assert feedback.car_marca == "Toyota"
    
    def test_create_feedback_disliked(self):
        """Criar feedback 'não gostei'"""
        feedback = UserFeedback(
            user_id="user_123",
            car_id="car_002",
            action=FeedbackAction.DISLIKED
        )
        
        assert feedback.action == FeedbackAction.DISLIKED


class TestUserInteractionHistory:
    """Testes para histórico de interações"""
    
    def test_empty_history(self):
        """Histórico vazio inicial"""
        history = UserInteractionHistory(user_id="user_123")
        
        assert history.total_interactions == 0
        assert history.liked_count == 0
        assert history.disliked_count == 0
        assert len(history.feedbacks) == 0
    
    def test_add_liked_feedback(self):
        """Adicionar feedback 'gostei'"""
        history = UserInteractionHistory(user_id="user_123")
        
        feedback = UserFeedback(
            user_id="user_123",
            car_id="car_001",
            action=FeedbackAction.LIKED,
            car_marca="Toyota",
            car_categoria="SUV"
        )
        
        history.add_feedback(feedback)
        
        assert history.total_interactions == 1
        assert history.liked_count == 1
        assert history.disliked_count == 0
        assert len(history.feedbacks) == 1
    
    def test_pattern_detection_brands(self):
        """Detectar padrão de marcas preferidas"""
        history = UserInteractionHistory(user_id="user_123")
        
        # Gostar de 2 Toyotas
        history.add_feedback(UserFeedback(
            user_id="user_123",
            car_id="car_001",
            action=FeedbackAction.LIKED,
            car_marca="Toyota"
        ))
        
        history.add_feedback(UserFeedback(
            user_id="user_123",
            car_id="car_002",
            action=FeedbackAction.LIKED,
            car_marca="Toyota"
        ))
        
        assert "Toyota" in history.preferred_brands
    
    def test_pattern_detection_categories(self):
        """Detectar padrão de categorias preferidas"""
        history = UserInteractionHistory(user_id="user_123")
        
        # Gostar de SUVs
        history.add_feedback(UserFeedback(
            user_id="user_123",
            car_id="car_001",
            action=FeedbackAction.LIKED,
            car_categoria="SUV"
        ))
        
        assert "SUV" in history.preferred_categories


class TestFeedbackEngine:
    """Testes para FeedbackEngine"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.engine = FeedbackEngine()
    
    def test_add_feedback_creates_history(self):
        """Adicionar feedback cria histórico"""
        feedback = UserFeedback(
            user_id="user_new",
            car_id="car_001",
            action=FeedbackAction.LIKED
        )
        
        history = self.engine.add_feedback(feedback)
        
        assert "user_new" in self.engine.user_histories
        assert history.total_interactions == 1
    
    def test_analyze_patterns_empty(self):
        """Analisar padrões sem feedbacks"""
        patterns = self.engine.analyze_feedback_patterns([])
        
        assert patterns["total_feedbacks"] == 0
        assert patterns["liked_count"] == 0
    
    def test_analyze_patterns_with_data(self):
        """Analisar padrões com dados"""
        feedbacks = [
            UserFeedback(
                user_id="user_123",
                car_id="car_001",
                action=FeedbackAction.LIKED,
                car_marca="Toyota",
                car_preco=115990
            ),
            UserFeedback(
                user_id="user_123",
                car_id="car_002",
                action=FeedbackAction.LIKED,
                car_marca="Honda",
                car_preco=120000
            ),
            UserFeedback(
                user_id="user_123",
                car_id="car_003",
                action=FeedbackAction.DISLIKED,
                car_marca="Fiat"
            )
        ]
        
        patterns = self.engine.analyze_feedback_patterns(feedbacks)
        
        assert patterns["total_feedbacks"] == 3
        assert patterns["liked_count"] == 2
        assert patterns["disliked_count"] == 1
        assert "Toyota" in patterns["preferred_brands"]
        assert "Fiat" in patterns["rejected_brands"]
    
    def test_infer_priority_changes_spacious_cars(self):
        """Inferir aumento de prioridade de espaço para SUVs"""
        profile = UserProfile(
            orcamento_min=80000,
            orcamento_max=120000,
            uso_principal="familia"
        )
        
        # Gostar de SUVs
        feedbacks = [
            UserFeedback(
                user_id="user_123",
                car_id="car_001",
                action=FeedbackAction.LIKED,
                car_categoria="SUV"
            ),
            UserFeedback(
                user_id="user_123",
                car_id="car_002",
                action=FeedbackAction.LIKED,
                car_categoria="Van"
            )
        ]
        
        adjustments = self.engine.infer_priority_changes(feedbacks, profile)
        
        assert "espaco" in adjustments
        assert adjustments["espaco"] > 0  # Deve aumentar
    
    def test_adjust_weights_insufficient_feedback(self):
        """Ajustar pesos com poucos feedbacks não altera"""
        profile = UserProfile(
            orcamento_min=80000,
            orcamento_max=120000,
            uso_principal="familia"
        )
        
        # Apenas 1 feedback (mínimo é 2)
        feedbacks = [
            UserFeedback(
                user_id="user_123",
                car_id="car_001",
                action=FeedbackAction.LIKED
            )
        ]
        
        adjustment = self.engine.adjust_weights(profile, feedbacks)
        
        assert adjustment.confidence_score == 0.0
        assert "Poucos feedbacks" in adjustment.adjustment_reason
    
    def test_adjust_weights_with_sufficient_feedback(self):
        """Ajustar pesos com feedbacks suficientes"""
        profile = UserProfile(
            orcamento_min=80000,
            orcamento_max=120000,
            uso_principal="familia",
            prioridades={
                "economia": 3,
                "espaco": 3,
                "performance": 3,
                "conforto": 3,
                "seguranca": 3
            }
        )
        
        # Gostar de SUVs (deve aumentar espaço)
        feedbacks = [
            UserFeedback(
                user_id="user_123",
                car_id=f"car_00{i}",
                action=FeedbackAction.LIKED,
                car_categoria="SUV"
            )
            for i in range(3)
        ]
        
        adjustment = self.engine.adjust_weights(profile, feedbacks)
        
        # Espaço deve ter aumentado
        assert adjustment.adjusted_weights["espaco"] > adjustment.original_weights["espaco"]
        assert adjustment.confidence_score > 0
    
    def test_check_convergence_not_converged(self):
        """Verificar convergência - não convergiu"""
        recommendations = [
            {"score": 0.65},
            {"score": 0.60},
            {"score": 0.55}
        ]
        
        converged, best_score = self.engine.check_convergence(
            recommendations,
            target_score=0.85
        )
        
        assert not converged
        assert best_score == 0.65
    
    def test_check_convergence_converged(self):
        """Verificar convergência - convergiu!"""
        recommendations = [
            {"score": 0.90},
            {"score": 0.87},
            {"score": 0.86},
            {"score": 0.85}
        ]
        
        converged, best_score = self.engine.check_convergence(
            recommendations,
            target_score=0.85
        )
        
        assert converged
        assert best_score == 0.90
    
    def test_generate_insights_with_patterns(self):
        """Gerar insights baseado em padrões"""
        feedbacks = [
            UserFeedback(
                user_id="user_123",
                car_id="car_001",
                action=FeedbackAction.LIKED,
                car_marca="Toyota",
                car_categoria="SUV",
                car_preco=115000
            ),
            UserFeedback(
                user_id="user_123",
                car_id="car_002",
                action=FeedbackAction.LIKED,
                car_marca="Toyota",
                car_categoria="SUV",
                car_preco=120000
            )
        ]
        
        profile = UserProfile(
            orcamento_min=80000,
            orcamento_max=120000,
            uso_principal="familia"
        )
        
        adjustment = self.engine.adjust_weights(profile, feedbacks)
        insights = self.engine.generate_insights(feedbacks, adjustment)
        
        assert len(insights) > 0
        # Deve mencionar Toyota ou SUV
        insights_text = " ".join(insights)
        assert "Toyota" in insights_text or "SUV" in insights_text


class TestWeightAdjustment:
    """Testes para modelo WeightAdjustment"""
    
    def test_create_weight_adjustment(self):
        """Criar ajuste de pesos"""
        adjustment = WeightAdjustment(
            user_id="user_123",
            original_weights={"economia": 0.3, "espaco": 0.2},
            adjusted_weights={"economia": 0.25, "espaco": 0.30},
            adjustment_reason="Usuário prefere espaço",
            confidence_score=0.75,
            feedbacks_analyzed=5
        )
        
        assert adjustment.user_id == "user_123"
        assert adjustment.confidence_score == 0.75
        assert adjustment.feedbacks_analyzed == 5


if __name__ == "__main__":
    print("🧪 Tech Lead: Executando testes FASE 2 - Feedback Iterativo")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "--tb=short"])

