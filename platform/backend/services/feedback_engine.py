"""
📊 Data Analyst + 🤖 AI Engineer: Engine de Feedback Iterativo (FASE 2)

Analisa feedback do usuário e ajusta pesos automaticamente
para convergir até o match ideal.

Autor: Data Analyst + AI Engineer
Data: Outubro 2024
"""

from typing import List, Dict, Tuple, Optional
from collections import Counter
import statistics

from models.feedback import (
    UserFeedback, 
    UserInteractionHistory, 
    WeightAdjustment,
    FeedbackAction
)
from models.user_profile import UserProfile
from models.car import Car


class FeedbackEngine:
    """
    Engine que analisa feedback e ajusta pesos de recomendação
    """
    
    # Configurações de ajuste
    LEARNING_RATE = 0.15  # Taxa de aprendizado (quanto ajustar por iteração)
    MIN_FEEDBACKS = 2     # Mínimo de feedbacks para ajustar
    MAX_WEIGHT = 0.50     # Peso máximo para um critério
    MIN_WEIGHT = 0.05     # Peso mínimo para um critério
    
    def __init__(self):
        self.user_histories: Dict[str, UserInteractionHistory] = {}
    
    def add_feedback(self, feedback: UserFeedback) -> UserInteractionHistory:
        """
        Adicionar feedback e atualizar histórico do usuário
        """
        if feedback.user_id not in self.user_histories:
            self.user_histories[feedback.user_id] = UserInteractionHistory(
                user_id=feedback.user_id
            )
        
        history = self.user_histories[feedback.user_id]
        history.add_feedback(feedback)
        
        return history
    
    def analyze_feedback_patterns(
        self, 
        feedbacks: List[UserFeedback]
    ) -> Dict[str, any]:
        """
        📊 Data Analyst: Analisar padrões de feedback
        
        Identifica:
        - Características dos carros curtidos vs rejeitados
        - Padrões de preferência
        - Tendências de comportamento
        """
        liked = [f for f in feedbacks if f.action == FeedbackAction.LIKED]
        disliked = [f for f in feedbacks if f.action == FeedbackAction.DISLIKED]
        
        patterns = {
            "total_feedbacks": len(feedbacks),
            "liked_count": len(liked),
            "disliked_count": len(disliked),
            "patterns": {}
        }
        
        if not liked:
            return patterns
        
        # Padrão 1: Marcas preferidas
        liked_brands = [f.car_marca for f in liked if f.car_marca]
        disliked_brands = [f.car_marca for f in disliked if f.car_marca]
        
        liked_brand_counts = Counter(liked_brands)
        patterns["preferred_brands"] = [
            brand for brand, count in liked_brand_counts.most_common(3)
        ]
        patterns["rejected_brands"] = list(set(disliked_brands) - set(liked_brands))
        
        # Padrão 2: Categorias preferidas
        liked_categories = [f.car_categoria for f in liked if f.car_categoria]
        patterns["preferred_categories"] = list(set(liked_categories))
        
        # Padrão 3: Faixa de preço preferida
        liked_prices = [f.car_preco for f in liked if f.car_preco]
        if liked_prices:
            patterns["avg_price_liked"] = statistics.mean(liked_prices)
            patterns["price_range_liked"] = {
                "min": min(liked_prices),
                "max": max(liked_prices)
            }
        
        # Padrão 4: Ano preferido
        liked_years = [f.car_ano for f in liked if f.car_ano]
        if liked_years:
            patterns["avg_year_liked"] = statistics.mean(liked_years)
        
        # Padrão 5: Scores dos carros curtidos
        liked_scores = [f.car_score for f in liked if f.car_score]
        if liked_scores:
            patterns["avg_score_liked"] = statistics.mean(liked_scores)
            patterns["best_score_liked"] = max(liked_scores)
        
        return patterns
    
    def infer_priority_changes(
        self, 
        feedbacks: List[UserFeedback],
        current_profile: UserProfile
    ) -> Dict[str, float]:
        """
        🤖 AI Engineer: Inferir mudanças de prioridade baseado em feedback
        
        Analisa características dos carros curtidos e infere
        quais prioridades devem ser ajustadas.
        
        Exemplo:
        - Se curtiu carros potentes: aumentar peso de "performance"
        - Se curtiu SUVs espaçosos: aumentar peso de "espaco"
        - Se curtiu carros econômicos: aumentar peso de "economia"
        """
        liked = [f for f in feedbacks if f.action == FeedbackAction.LIKED]
        
        if len(liked) < self.MIN_FEEDBACKS:
            return {}  # Poucos feedbacks, não ajustar ainda
        
        priority_adjustments = {}
        
        # Análise 1: Categoria → Espaço
        liked_categories = [f.car_categoria for f in liked if f.car_categoria]
        spacious_categories = ["SUV", "Van", "Pickup"]
        
        if any(cat in spacious_categories for cat in liked_categories):
            # Usuário prefere carros espaçosos
            priority_adjustments["espaco"] = +0.10  # Aumentar 10%
        
        # Análise 2: Score de economia alto → Economia
        liked_with_economy = [
            f for f in liked 
            if hasattr(f, 'car_score_economia') and f.car_score_economia > 0.7
        ]
        if len(liked_with_economy) > len(liked) * 0.6:  # Mais de 60%
            priority_adjustments["economia"] = +0.10
        
        # Análise 3: Carros novos → pode reduzir economia, aumentar conforto
        liked_years = [f.car_ano for f in liked if f.car_ano]
        if liked_years and statistics.mean(liked_years) >= 2022:
            priority_adjustments["conforto"] = +0.05
            priority_adjustments["economia"] = -0.05
        
        # Análise 4: Marcas premium → performance/conforto
        premium_brands = ["Toyota", "Honda", "Volkswagen", "BMW", "Mercedes"]
        liked_brands = [f.car_marca for f in liked if f.car_marca]
        premium_liked = [b for b in liked_brands if b in premium_brands]
        
        if len(premium_liked) > len(liked_brands) * 0.5:
            priority_adjustments["performance"] = +0.05
            priority_adjustments["conforto"] = +0.05
        
        return priority_adjustments
    
    def adjust_weights(
        self,
        current_profile: UserProfile,
        feedbacks: List[UserFeedback]
    ) -> WeightAdjustment:
        """
        📊 Data Analyst: Ajustar pesos de prioridades baseado em feedback
        
        Retorna:
            WeightAdjustment com pesos originais, ajustados e explicação
        """
        # Pesos atuais (normalizados)
        current_priorities = current_profile.prioridades.copy()
        total = sum(current_priorities.values())
        
        original_weights = {
            k: v / total for k, v in current_priorities.items()
        }
        
        # Inferir mudanças necessárias
        adjustments = self.infer_priority_changes(feedbacks, current_profile)
        
        if not adjustments:
            # Sem ajustes necessários
            return WeightAdjustment(
                user_id=current_profile.__dict__.get('user_id', 'unknown'),
                original_weights=original_weights,
                adjusted_weights=original_weights,
                adjustment_reason="Poucos feedbacks para ajustar pesos",
                confidence_score=0.0,
                feedbacks_analyzed=len(feedbacks)
            )
        
        # Aplicar ajustes com learning rate
        adjusted_weights = original_weights.copy()
        reasons = []
        
        for priority, change in adjustments.items():
            if priority in adjusted_weights:
                new_weight = adjusted_weights[priority] + (change * self.LEARNING_RATE)
                new_weight = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, new_weight))
                adjusted_weights[priority] = new_weight
                
                if change > 0:
                    reasons.append(f"Aumentou '{priority}' (+{change:.0%})")
                else:
                    reasons.append(f"Reduziu '{priority}' ({change:.0%})")
        
        # Normalizar pesos ajustados
        total_adjusted = sum(adjusted_weights.values())
        adjusted_weights = {
            k: v / total_adjusted for k, v in adjusted_weights.items()
        }
        
        # Calcular confiança (baseado em quantidade de feedbacks)
        confidence = min(1.0, len(feedbacks) / 10.0)  # Max confiança com 10 feedbacks
        
        adjustment_reason = ". ".join(reasons) if reasons else "Nenhum ajuste necessário"
        
        return WeightAdjustment(
            user_id=current_profile.__dict__.get('user_id', 'unknown'),
            original_weights=original_weights,
            adjusted_weights=adjusted_weights,
            adjustment_reason=adjustment_reason,
            confidence_score=confidence,
            feedbacks_analyzed=len(feedbacks)
        )
    
    def update_profile_from_weights(
        self,
        profile: UserProfile,
        weight_adjustment: WeightAdjustment
    ) -> UserProfile:
        """
        Atualizar perfil do usuário com pesos ajustados
        """
        # Converter pesos (0-1) de volta para escala (1-5)
        adjusted_priorities = {}
        
        for priority, weight in weight_adjustment.adjusted_weights.items():
            # Escalar de 0-1 para 1-5
            scaled_value = 1 + (weight * 20)  # weight * 20 dá range de 0-4, +1 = 1-5
            scaled_value = max(1, min(5, int(round(scaled_value))))
            adjusted_priorities[priority] = scaled_value
        
        # Criar novo perfil com prioridades ajustadas
        profile_dict = profile.model_dump()
        profile_dict['prioridades'] = adjusted_priorities
        
        return UserProfile(**profile_dict)
    
    def check_convergence(
        self,
        recommendations: List[Dict],
        target_score: float = 0.85
    ) -> Tuple[bool, float]:
        """
        Verificar se convergiu (encontrou match ideal)
        
        Returns:
            (converged: bool, best_score: float)
        """
        if not recommendations:
            return False, 0.0
        
        # Pegar melhor score
        best_score = max(rec['score'] for rec in recommendations)
        
        # Convergiu se:
        # 1. Melhor score >= target
        # 2. Tem pelo menos 3 recomendações com score >= 80% do target
        good_matches = [
            rec for rec in recommendations 
            if rec['score'] >= (target_score * 0.8)
        ]
        
        converged = best_score >= target_score and len(good_matches) >= 3
        
        return converged, best_score
    
    def generate_insights(
        self,
        feedbacks: List[UserFeedback],
        weight_adjustment: WeightAdjustment
    ) -> List[str]:
        """
        Gerar insights sobre as preferências do usuário
        """
        patterns = self.analyze_feedback_patterns(feedbacks)
        insights = []
        
        # Insight 1: Marcas preferidas
        if patterns.get("preferred_brands"):
            brands = ", ".join(patterns["preferred_brands"][:2])
            insights.append(f"Você prefere marcas: {brands}")
        
        # Insight 2: Categorias
        if patterns.get("preferred_categories"):
            cats = ", ".join(patterns["preferred_categories"])
            insights.append(f"Você gosta de: {cats}")
        
        # Insight 3: Faixa de preço
        if patterns.get("avg_price_liked"):
            avg_price = patterns["avg_price_liked"]
            insights.append(f"Sua faixa de preço preferida: R$ {avg_price:,.0f}")
        
        # Insight 4: Ajustes de peso
        if weight_adjustment.adjusted_weights != weight_adjustment.original_weights:
            # Encontrar maior mudança
            changes = {}
            for key in weight_adjustment.adjusted_weights:
                orig = weight_adjustment.original_weights.get(key, 0)
                adj = weight_adjustment.adjusted_weights[key]
                changes[key] = adj - orig
            
            top_increase = max(changes.items(), key=lambda x: x[1])
            if top_increase[1] > 0.05:  # Mudança significativa
                priority_names = {
                    "economia": "Economia",
                    "espaco": "Espaço",
                    "performance": "Performance",
                    "conforto": "Conforto",
                    "seguranca": "Segurança"
                }
                priority_label = priority_names.get(top_increase[0], top_increase[0])
                insights.append(f"{priority_label} é mais importante para você do que pensávamos")
        
        return insights if insights else ["Continue dando feedback para entendermos melhor suas preferências"]

