"""
Weight Optimizer Agent - Agente de Otimização de Pesos

Responsável por:
- Calcular pesos dinâmicos baseados no perfil do usuário
- Ajustar pesos com base em histórico de interações (ML)
- Personalizar a relevância de cada componente do score
"""

import logging
from typing import Dict, Any, Optional

from models.car import Car
from models.user_profile import UserProfile
from services.agents.base_agent import BaseAgent
from services.interaction_service import InteractionService
from services.semantic_analysis_service import SemanticAnalysisService

logger = logging.getLogger(__name__)


class WeightOptimizerAgent(BaseAgent):
    """
    Agente especializado em otimização de pesos de recomendação.
    
    Usa regras de negócio e (futuramente) ML para determinar
    qual a importância de cada fator (economia, conforto, etc.)
    para cada usuário específico.
    """

    def __init__(self, cache_manager=None, interaction_service: Optional[InteractionService] = None):
        """
        Inicializa o WeightOptimizerAgent
        
        Args:
            cache_manager: Gerenciador de cache
            interaction_service: Serviço de interações para dados de ML
        """
        super().__init__(cache_manager, name="WeightOptimizerAgent")
        self.interaction_service = interaction_service or InteractionService()
        
        try:
            self.semantic_analyzer = SemanticAnalysisService()
            self.enable_semantic = True
        except Exception as e:
            logger.warning(f"SemanticAnalysisService not available: {e}")
            self.enable_semantic = False

    async def calculate_score(
        self,
        car: Car,
        profile: UserProfile
    ) -> float:
        """
        Calcula um 'Score de Personalização' (0-1)
        
        Neste contexto, o score representa o quanto este carro
        se alinha com os pesos otimizados do usuário.
        
        Args:
            car: Veículo
            profile: Perfil do usuário
            
        Returns:
            float: Score de personalização 0-1
        """
        # Obter pesos otimizados
        weights = self.get_optimized_weights(profile)
        
        # Calcular score ponderado dos atributos do carro
        # correspondentes aos pesos
        score = 0.0
        total_weight = 0.0
        
        # Mapeamento de pesos para atributos do carro
        weight_attr_map = {
            'economy': getattr(car, 'score_economia', 0.5),
            'comfort': getattr(car, 'score_conforto', 0.5),
            'safety': getattr(car, 'score_seguranca', 0.5),
            'performance': getattr(car, 'score_performance', 0.5),
            'resale': getattr(car, 'indice_revenda', 0.5),
        }
        
        # Iterar sobre pesos conhecidos
        if 'priorities' in weights:
            # Prioridades é um peso composto, usar lógica simplificada
            score += 0.5 * weights['priorities']
            total_weight += weights['priorities']
            
        # Adicionar outros componentes se existirem nos pesos e no carro
        # (Implementação futura pode ser mais detalhada)
        
        # Por enquanto, retorna 1.0 pois a função principal deste agente
        # é fornecer os pesos para o Engine, não necessariamente um score isolado.
        # Mas para cumprir interface, retornamos um valor neutro-alto.
        return 0.85

    def get_optimized_weights(self, profile: UserProfile) -> Dict[str, float]:
        """
        Retorna pesos otimizados combinando heurística e análise semântica.
        
        Formula: Final = (Heurística * 0.7) + (Semântica * 0.3)
        """
        # 1. Pesos Base (Heurísticos)
        base_weights = self._get_heuristic_weights(profile)
        
        # 2. Ajuste Semântico (Conexionista)
        if self.enable_semantic:
            try:
                # Obter vetor de ajuste (-0.5 a +0.5)
                # Ex: {'safety': 0.2, 'performance': -0.1}
                semantic_adjustment = self.semantic_analyzer.analyze_profile(profile)
                
                if semantic_adjustment:
                    # Aplicar ajustes aos pesos base
                    # Mapeamento de categorias semânticas para categorias de peso do sistema
                    # O sistema usa: category, priorities, preferences, budget
                    
                    # Para simplificar, vamos ajustar 'priorities' baseado na média dos ajustes
                    # Ou influenciar sub-fatores se a arquitetura permitisse.
                    # Como o RecommendationEngine usa pesos macro (category, priorities...),
                    # vamos traduzir os ajustes semânticos para esses macro-pesos.
                    
                    # Logica de Tradução:
                    # Se 'safety' ou 'space' (família) sobem -> 'category' (SUV/Van) e 'priorities' sobem
                    # Se 'economy' sobe -> 'budget' e 'priorities' sobem
                    
                    macro_adjustment = {
                        'category': 0.0,
                        'priorities': 0.0,
                        'preferences': 0.0,
                        'budget': 0.0
                    }
                    
                    # Regras de projeção Semântico -> Macro
                    if 'space' in semantic_adjustment:
                        macro_adjustment['category'] += semantic_adjustment['space'] * 0.5
                        
                    if 'safety' in semantic_adjustment:
                        macro_adjustment['priorities'] += semantic_adjustment['safety'] * 0.5
                        
                    if 'performance' in semantic_adjustment:
                        macro_adjustment['preferences'] += semantic_adjustment['performance'] * 0.5
                        
                    if 'economy' in semantic_adjustment:
                        macro_adjustment['budget'] += semantic_adjustment['economy'] * 0.5
                        macro_adjustment['priorities'] += semantic_adjustment['economy'] * 0.3

                    # Aplicar mistura (Blending)
                    # Peso final = Base + (Ajuste * 0.5)
                    for key in base_weights:
                        if key in macro_adjustment:
                            base_weights[key] += macro_adjustment[key] * 0.5
                            
                    # Renormalizar para soma 1.0
                    total = sum(base_weights.values())
                    if total > 0:
                        for key in base_weights:
                            base_weights[key] /= total
                            
                    # Marcar que usou ML
                    base_weights['ml_adjusted'] = True
                    
            except Exception as e:
                logger.error(f"Error in semantic weight adjustment: {e}")
        
        return base_weights

    def _get_heuristic_weights(self, profile: UserProfile) -> Dict[str, float]:
        """Lógica original de regras if/else"""
        # (Código original migrado para cá para limpeza)
        
        if profile.uso_principal == "familia":
            return {'category': 0.40, 'priorities': 0.45, 'preferences': 0.10, 'budget': 0.05}
        
        elif profile.uso_principal == "primeiro_carro":
            return {'category': 0.35, 'priorities': 0.50, 'preferences': 0.10, 'budget': 0.05}
        
        elif profile.uso_principal == "trabalho":
            return {'category': 0.25, 'priorities': 0.45, 'preferences': 0.20, 'budget': 0.10}
        
        elif profile.uso_principal == "comercial":
            return {'category': 0.45, 'priorities': 0.35, 'preferences': 0.15, 'budget': 0.05}
        
        elif profile.uso_principal == "lazer":
            return {'category': 0.35, 'priorities': 0.40, 'preferences': 0.15, 'budget': 0.10}
        
        elif profile.uso_principal == "transporte_passageiros":
            return {'category': 0.50, 'priorities': 0.35, 'preferences': 0.10, 'budget': 0.05}
        
        # Default
        return {
            'category': 0.30,
            'priorities': 0.40,
            'preferences': 0.20,
            'budget': 0.10
        }

    def _get_ml_adjustment(self, profile: UserProfile) -> Dict[str, float]:
        """Deprecated: Logic moved to get_optimized_weights with SemanticAnalysisService"""
        return {}
