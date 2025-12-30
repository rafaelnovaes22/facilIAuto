"""
Base Agent - Classe abstrata para agentes de scoring

Define a interface comum e comportamento base para todos os agentes
especializados de cálculo de score.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import time

from models.car import Car
from models.user_profile import UserProfile


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Classe base abstrata para agentes de scoring

    Todos os agentes especializados (EconomyAgent, MaintenanceAgent, etc.)
    devem herdar desta classe e implementar o método calculate_score().
    """

    def __init__(self, cache_manager=None, name: str = None):
        """
        Inicializa o agente base

        Args:
            cache_manager: Gerenciador de cache (opcional)
            name: Nome do agente (para logging e métricas)
        """
        self.cache_manager = cache_manager
        self.name = name or self.__class__.__name__
        self.metrics = {
            'total_calls': 0,
            'success_calls': 0,
            'failed_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_latency_ms': 0.0,
            'last_update': None
        }

    @abstractmethod
    async def calculate_score(
        self,
        car: Car,
        profile: UserProfile
    ) -> float:
        """
        Calcula o score para um carro baseado no perfil do usuário

        Este método DEVE ser implementado por todas as subclasses.

        Args:
            car: Veículo a ser avaliado
            profile: Perfil do usuário com preferências e requisitos

        Returns:
            float: Score normalizado entre 0.0 e 1.0

        Raises:
            NotImplementedError: Se não foi implementado pela subclasse
        """
        raise NotImplementedError(
            f"{self.name} deve implementar o método calculate_score()"
        )

    async def calculate_score_with_cache(
        self,
        car: Car,
        profile: UserProfile
    ) -> float:
        """
        Calcula score com suporte a cache

        Verifica cache antes de calcular. Se cache miss, calcula e armazena.

        Args:
            car: Veículo a ser avaliado
            profile: Perfil do usuário

        Returns:
            float: Score normalizado entre 0.0 e 1.0
        """
        start_time = time.time()

        try:
            # 1. Tentar obter do cache
            cache_key = self._build_cache_key(car, profile)

            if self.cache_manager:
                cached_value = await self.cache_manager.get(cache_key)

                if cached_value is not None:
                    self._record_metrics(
                        success=True,
                        latency_ms=(time.time() - start_time) * 1000,
                        cache_hit=True
                    )
                    logger.debug(f"[{self.name}] Cache HIT para {car.nome}")
                    return cached_value

            # 2. Cache miss - calcular score
            logger.debug(f"[{self.name}] Cache MISS para {car.nome}, calculando...")
            score = await self.calculate_score(car, profile)

            # 3. Validar resultado
            if not self._validate_score(score):
                logger.warning(
                    f"[{self.name}] Score inválido {score} para {car.nome}, "
                    f"usando fallback"
                )
                score = self._get_fallback_score(car)

            # 4. Salvar no cache
            if self.cache_manager:
                ttl = self._get_cache_ttl()
                await self.cache_manager.set(cache_key, score, ttl=ttl)

            # 5. Registrar métricas
            self._record_metrics(
                success=True,
                latency_ms=(time.time() - start_time) * 1000,
                cache_hit=False
            )

            return score

        except Exception as e:
            logger.error(f"[{self.name}] Erro ao calcular score para {car.nome}: {e}")

            # Registrar falha
            self._record_metrics(
                success=False,
                latency_ms=(time.time() - start_time) * 1000,
                cache_hit=False
            )

            # Retornar fallback
            return self._get_fallback_score(car)

    def _build_cache_key(self, car: Car, profile: UserProfile) -> str:
        """
        Constrói chave de cache única para este carro e perfil

        Formato: {agent_name}:{car_id}:{profile_hash}

        Args:
            car: Veículo
            profile: Perfil do usuário

        Returns:
            str: Chave de cache única
        """
        # Hash do perfil (simplificado - apenas campos relevantes)
        profile_hash = hash((
            profile.uso_principal,
            profile.orcamento_min,
            profile.orcamento_max,
            getattr(profile, 'state', 'SP')
        ))

        return f"{self.name}:{car.id}:{profile_hash}"

    def _validate_score(self, score: float) -> bool:
        """
        Valida se o score está no formato correto

        Args:
            score: Score a validar

        Returns:
            bool: True se válido, False caso contrário
        """
        # Verificar tipo
        if not isinstance(score, (int, float)):
            return False

        # Verificar range (0-1)
        if not 0.0 <= score <= 1.0:
            return False

        # Verificar NaN/Inf
        import math
        if not math.isfinite(score):
            return False

        return True

    def _get_fallback_score(self, car: Car) -> float:
        """
        Retorna score de fallback quando cálculo falha

        Por padrão, retorna 0.5 (neutro). Subclasses podem sobrescrever
        para usar valores mais específicos (ex: car.score_economia).

        Args:
            car: Veículo

        Returns:
            float: Score de fallback (padrão: 0.5)
        """
        return 0.5

    def _get_cache_ttl(self) -> int:
        """
        Retorna TTL do cache em segundos

        Por padrão, retorna 86400 (1 dia). Subclasses podem sobrescrever
        para usar TTLs diferentes.

        Returns:
            int: TTL em segundos
        """
        return 86400  # 1 dia

    def _record_metrics(
        self,
        success: bool,
        latency_ms: float,
        cache_hit: bool
    ):
        """
        Registra métricas de execução

        Args:
            success: Se a execução foi bem-sucedida
            latency_ms: Latência em milissegundos
            cache_hit: Se foi cache hit ou miss
        """
        self.metrics['total_calls'] += 1

        if success:
            self.metrics['success_calls'] += 1
        else:
            self.metrics['failed_calls'] += 1

        if cache_hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1

        self.metrics['total_latency_ms'] += latency_ms
        self.metrics['last_update'] = datetime.now()

    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas do agente

        Returns:
            dict: Métricas incluindo:
                - total_calls: Total de chamadas
                - success_rate: Taxa de sucesso (0-1)
                - avg_latency_ms: Latência média
                - cache_hit_rate: Taxa de cache hit (0-1)
        """
        total = self.metrics['total_calls']

        if total == 0:
            return {
                'total_calls': 0,
                'success_calls': 0,
                'failed_calls': 0,
                'success_rate': 0.0,
                'avg_latency_ms': 0.0,
                'cache_hits': 0,
                'cache_misses': 0,
                'cache_hit_rate': 0.0,
                'last_update': None
            }

        return {
            'total_calls': total,
            'success_calls': self.metrics['success_calls'],
            'failed_calls': self.metrics['failed_calls'],
            'success_rate': self.metrics['success_calls'] / total,
            'avg_latency_ms': self.metrics['total_latency_ms'] / total,
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_rate': self.metrics['cache_hits'] / total,
            'last_update': self.metrics['last_update']
        }

    def reset_metrics(self):
        """Reseta as métricas do agente"""
        self.metrics = {
            'total_calls': 0,
            'success_calls': 0,
            'failed_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_latency_ms': 0.0,
            'last_update': None
        }
