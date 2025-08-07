"""
Extensão do Memory Manager para integração com ML
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np

from app.memory_models import ConversationContext
from app.memory_manager import get_memory_manager

logger = logging.getLogger(__name__)


class MemoryMLExtension:
    """
    Extensão do Memory Manager para funcionalidades de ML
    """

    def __init__(self):
        self.memory = get_memory_manager()

    def log_ml_feedback(
        self, session_id: str, carro_id: str, score: float, action: Optional[str] = None
    ) -> bool:
        """
        Registra feedback para ML
        """
        try:
            return self.memory.add_context(
                conversation_id=f"{session_id}_{carro_id}",
                context_type="ml_feedback",
                context_key="feedback",
                context_value=json.dumps(
                    {
                        "score": score,
                        "action": action,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                confidence=1.0,
            )
        except Exception as e:
            logger.error(f"Erro ao registrar ML feedback: {e}")
            return False

    def persist_ml_data(self, conversation_id: str, ml_data: Dict[str, Any]) -> bool:
        """
        Persiste dados de ML completos
        """
        try:
            return self.memory.add_context(
                conversation_id=conversation_id,
                context_type="ml_training",
                context_key="training_data",
                context_value=json.dumps(ml_data),
                confidence=1.0,
            )
        except Exception as e:
            logger.error(f"Erro ao persistir ML data: {e}")
            return False

    def get_recent_ml_feedback(self, days: int = 30) -> List[Dict]:
        """
        Busca feedback recente para treinamento
        """
        try:
            with self.memory.Session() as session:
                since_date = datetime.now() - timedelta(days=days)

                results = (
                    session.query(ConversationContext)
                    .filter(
                        ConversationContext.context_type.in_(
                            ["ml_feedback", "ml_training"]
                        ),
                        ConversationContext.created_at >= since_date,
                    )
                    .all()
                )

                return [json.loads(r.context_value) for r in results]
        except Exception as e:
            logger.error(f"Erro ao buscar ML feedback: {e}")
            return []

    def persist_recommendation_result(
        self,
        conversation_id: str,
        carro_id: str,
        score: float,
        method: str,
        processing_time_ms: int,
    ) -> bool:
        """
        Persiste resultado de recomendação
        """
        try:
            return self.memory.add_context(
                conversation_id=conversation_id,
                context_type="recommendation",
                context_key="result",
                context_value=json.dumps(
                    {
                        "carro_id": carro_id,
                        "score": score,
                        "method": method,
                        "processing_time_ms": processing_time_ms,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                confidence=1.0,
            )
        except Exception as e:
            logger.error(f"Erro ao persistir resultado: {e}")
            return False

    def get_ml_performance_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de performance do ML
        """
        try:
            with self.memory.Session() as session:
                # Buscar resultados recentes
                results = (
                    session.query(ConversationContext)
                    .filter(ConversationContext.context_type == "recommendation")
                    .limit(100)
                    .all()
                )

                if not results:
                    return {}

                ml_results = []
                rule_results = []

                for r in results:
                    data = json.loads(r.context_value)
                    if data.get("method") in ["super_hybrid", "smart_ml"]:
                        ml_results.append(data.get("score", 0))
                    else:
                        rule_results.append(data.get("score", 0))

                return {
                    "ml_count": len(ml_results),
                    "rule_count": len(rule_results),
                    "ml_avg_score": np.mean(ml_results) if ml_results else 0,
                    "rule_avg_score": np.mean(rule_results) if rule_results else 0,
                    "accuracy": 0.75,  # Placeholder - calcular baseado em feedback real
                }
        except Exception as e:
            logger.error(f"Erro ao calcular ML stats: {e}")
            return {}

    def save_ml_training_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Salva métricas de treinamento
        """
        try:
            return self.memory.add_context(
                conversation_id="ml_training",
                context_type="metrics",
                context_key="training_result",
                context_value=json.dumps(metrics),
                confidence=1.0,
            )
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {e}")
            return False


# Singleton da extensão
_ml_extension_instance = None


def get_memory_ml_extension() -> MemoryMLExtension:
    """
    Retorna instância singleton da extensão ML
    """
    global _ml_extension_instance
    if _ml_extension_instance is None:
        _ml_extension_instance = MemoryMLExtension()
    return _ml_extension_instance
