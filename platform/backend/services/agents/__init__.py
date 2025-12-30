"""
Agents Package - Sistema de agentes especializados para scoring

Este pacote contém a arquitetura de sub-agentes para cálculo avançado
de scores de compatibilidade de veículos.

Estrutura:
- BaseAgent: Classe base abstrata para todos os agentes
- CacheManager: Sistema de cache em múltiplas camadas
- ScoringAgentOrchestrator: Coordenador central de agentes

Agentes especializados (implementados em sprints futuros):
- EconomyAgent: Score de economia baseado em consumo real
- MaintenanceAgent: Score de manutenção com dados reais
- ResaleAgent: Índice de revenda com dados de mercado
- WeightOptimizerAgent: Otimização de pesos com ML
"""

from services.agents.base_agent import BaseAgent
from services.agents.cache_manager import CacheManager, get_cache_manager
from services.agents.scoring_orchestrator import (
    ScoringAgentOrchestrator,
    get_scoring_orchestrator
)
from services.agents.economy_agent import EconomyAgent
from services.agents.maintenance_agent import MaintenanceAgent
from services.agents.resale_agent import ResaleAgent
from services.agents.weight_optimizer_agent import WeightOptimizerAgent
from services.agents.financing_agent import FinancingAgent


__all__ = [
    # Classes base
    'BaseAgent',
    'CacheManager',
    'ScoringAgentOrchestrator',

    # Agentes especializados
    'EconomyAgent',
    'MaintenanceAgent',
    'ResaleAgent',
    'WeightOptimizerAgent',
    'FinancingAgent',

    # Funções helper
    'get_cache_manager',
    'get_scoring_orchestrator',
]

__version__ = '0.1.0'
