"""
Scoring Agent Orchestrator - Coordenador central de agentes de scoring

Responsável por:
- Coordenar execução paralela de múltiplos agentes
- Agregar resultados com pesos otimizados
- Gerenciar fallbacks quando agentes falham
- Coletar métricas de performance
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from models.car import Car
from models.user_profile import UserProfile
from services.agents.cache_manager import CacheManager, get_cache_manager


logger = logging.getLogger(__name__)


class ScoringAgentOrchestrator:
    """
    Orquestrador central para coordenar agentes de scoring

    Executa múltiplos agentes em paralelo e agrega os resultados.
    """

    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        enable_parallel: bool = True
    ):
        """
        Inicializa o orquestrador

        Args:
            cache_manager: Gerenciador de cache (opcional)
            enable_parallel: Se deve executar agentes em paralelo
        """
        self.cache_manager = cache_manager or get_cache_manager(enable_redis=False)
        self.enable_parallel = enable_parallel

        # Registro de agentes
        self.agents: Dict[str, Any] = {}

        # Métricas globais
        self.metrics = {
            'total_orchestrations': 0,
            'total_cars_scored': 0,
            'total_latency_ms': 0.0,
            'failed_orchestrations': 0,
            'last_update': None
        }

    def register_agent(self, name: str, agent: Any):
        """
        Registra um agente no orquestrador

        Args:
            name: Nome identificador do agente (ex: "economy", "maintenance")
            agent: Instância do agente (deve herdar de BaseAgent)
        """
        self.agents[name] = agent
        logger.info(f"[Orchestrator] Agente registrado: {name}")

    def unregister_agent(self, name: str):
        """
        Remove um agente do orquestrador

        Args:
            name: Nome do agente a remover
        """
        if name in self.agents:
            del self.agents[name]
            logger.info(f"[Orchestrator] Agente removido: {name}")

    async def calculate_advanced_scores(
        self,
        car: Car,
        profile: UserProfile,
        agent_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calcula scores avançados usando agentes especializados

        Executa agentes em paralelo (se habilitado) e retorna resultados agregados.

        Args:
            car: Veículo a ser avaliado
            profile: Perfil do usuário
            agent_names: Lista de agentes a executar (None = todos)

        Returns:
            dict: Resultados com scores e metadata:
                {
                    'scores': {'economy': 0.85, 'maintenance': 0.70, ...},
                    'metadata': {
                        'agents_used': ['economy', 'maintenance'],
                        'execution_time_ms': 47.3,
                        'cache_hits': 2,
                        'failed_agents': []
                    }
                }
        """
        start_time = time.time()

        try:
            # Determinar quais agentes executar
            if agent_names is None:
                agent_names = list(self.agents.keys())

            # Filtrar apenas agentes registrados
            agents_to_run = {
                name: self.agents[name]
                for name in agent_names
                if name in self.agents
            }

            if not agents_to_run:
                logger.warning(
                    f"[Orchestrator] Nenhum agente disponível para {car.nome}"
                )
                return self._get_empty_result()

            # Executar agentes
            if self.enable_parallel and len(agents_to_run) > 1:
                results = await self._execute_parallel(car, profile, agents_to_run)
            else:
                results = await self._execute_sequential(car, profile, agents_to_run)

            # Processar resultados
            scores, metadata = self._process_results(
                results,
                car,
                start_time
            )

            # Registrar métricas
            self._record_orchestration_metrics(
                success=True,
                latency_ms=(time.time() - start_time) * 1000
            )

            return {
                'scores': scores,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(
                f"[Orchestrator] Erro na orquestração para {car.nome}: {e}"
            )

            # Registrar falha
            self._record_orchestration_metrics(
                success=False,
                latency_ms=(time.time() - start_time) * 1000
            )

            return self._get_empty_result()

    async def _execute_parallel(
        self,
        car: Car,
        profile: UserProfile,
        agents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa agentes em paralelo usando asyncio.gather

        Args:
            car: Veículo
            profile: Perfil do usuário
            agents: Dicionário {nome: agente}

        Returns:
            dict: Resultados {nome: (score, exception)}
        """
        # Criar tasks para cada agente
        tasks = {
            name: agent.calculate_score_with_cache(car, profile)
            for name, agent in agents.items()
        }

        # Executar em paralelo (return_exceptions=True para não falhar tudo)
        results_list = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )

        # Mapear resultados de volta aos nomes
        results = {}
        for name, result in zip(tasks.keys(), results_list):
            if isinstance(result, Exception):
                logger.warning(f"[Orchestrator] Agente {name} falhou: {result}")
                results[name] = (None, result)
            else:
                results[name] = (result, None)

        return results

    async def _execute_sequential(
        self,
        car: Car,
        profile: UserProfile,
        agents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa agentes sequencialmente (fallback ou debug)

        Args:
            car: Veículo
            profile: Perfil do usuário
            agents: Dicionário {nome: agente}

        Returns:
            dict: Resultados {nome: (score, exception)}
        """
        results = {}

        for name, agent in agents.items():
            try:
                score = await agent.calculate_score_with_cache(car, profile)
                results[name] = (score, None)
            except Exception as e:
                logger.warning(f"[Orchestrator] Agente {name} falhou: {e}")
                results[name] = (None, e)

        return results

    def _process_results(
        self,
        results: Dict[str, tuple],
        car: Car,
        start_time: float
    ) -> tuple:
        """
        Processa resultados dos agentes com fallback

        Args:
            results: Resultados brutos {nome: (score, exception)}
            car: Veículo (para fallback)
            start_time: Timestamp de início

        Returns:
            tuple: (scores_dict, metadata_dict)
        """
        scores = {}
        failed_agents = []
        cache_hits = 0

        for agent_name, (score, exception) in results.items():
            if exception is not None or score is None:
                # Falha - usar fallback
                failed_agents.append(agent_name)
                scores[agent_name] = self._get_fallback_score(agent_name, car)
                logger.debug(
                    f"[Orchestrator] Usando fallback para {agent_name}: "
                    f"{scores[agent_name]}"
                )
            else:
                # Sucesso
                scores[agent_name] = score

                # Verificar se foi cache hit (simplificado)
                agent = self.agents.get(agent_name)
                if agent and hasattr(agent, 'metrics'):
                    if agent.metrics.get('cache_hits', 0) > 0:
                        cache_hits += 1

        # Metadata
        execution_time_ms = (time.time() - start_time) * 1000
        metadata = {
            'agents_used': list(results.keys()),
            'execution_time_ms': round(execution_time_ms, 2),
            'cache_hits': cache_hits,
            'failed_agents': failed_agents,
            'timestamp': datetime.now().isoformat()
        }

        return scores, metadata

    def _get_fallback_score(self, agent_name: str, car: Car) -> float:
        """
        Retorna score de fallback para um agente específico

        Tenta usar atributos do carro quando possível, senão retorna 0.5

        Args:
            agent_name: Nome do agente
            car: Veículo

        Returns:
            float: Score de fallback
        """
        # Mapeamento de agentes para atributos do carro
        fallback_map = {
            'economy': lambda: getattr(car, 'score_economia', 0.5),
            'maintenance': lambda: 0.5,  # Sem dados no carro
            'resale': lambda: getattr(car, 'indice_revenda', 0.5),
            'safety': lambda: getattr(car, 'score_seguranca', 0.5),
            'comfort': lambda: getattr(car, 'score_conforto', 0.5),
            'performance': lambda: getattr(car, 'score_performance', 0.5),
            'family': lambda: getattr(car, 'score_familia', 0.5)
        }

        fallback_fn = fallback_map.get(agent_name, lambda: 0.5)

        try:
            return fallback_fn()
        except Exception:
            return 0.5

    def _get_empty_result(self) -> Dict[str, Any]:
        """
        Retorna resultado vazio quando orquestração falha

        Returns:
            dict: Resultado vazio
        """
        return {
            'scores': {},
            'metadata': {
                'agents_used': [],
                'execution_time_ms': 0.0,
                'cache_hits': 0,
                'failed_agents': [],
                'error': 'Orchestration failed'
            }
        }

    def _record_orchestration_metrics(self, success: bool, latency_ms: float):
        """
        Registra métricas de orquestração

        Args:
            success: Se a orquestração foi bem-sucedida
            latency_ms: Latência em milissegundos
        """
        self.metrics['total_orchestrations'] += 1

        if success:
            self.metrics['total_cars_scored'] += 1
        else:
            self.metrics['failed_orchestrations'] += 1

        self.metrics['total_latency_ms'] += latency_ms
        self.metrics['last_update'] = datetime.now()

    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas do orquestrador

        Returns:
            dict: Métricas agregadas incluindo métricas de cada agente
        """
        total_orchestrations = self.metrics['total_orchestrations']

        orchestrator_metrics = {
            'total_orchestrations': total_orchestrations,
            'success_rate': (
                self.metrics['total_cars_scored'] / total_orchestrations
                if total_orchestrations > 0 else 0.0
            ),
            'avg_latency_ms': (
                self.metrics['total_latency_ms'] / total_orchestrations
                if total_orchestrations > 0 else 0.0
            ),
            'failed_orchestrations': self.metrics['failed_orchestrations'],
            'last_update': self.metrics['last_update']
        }

        # Adicionar métricas de cada agente
        agent_metrics = {}
        for name, agent in self.agents.items():
            if hasattr(agent, 'get_metrics'):
                agent_metrics[name] = agent.get_metrics()

        return {
            'orchestrator': orchestrator_metrics,
            'agents': agent_metrics,
            'cache': self.cache_manager.get_stats() if self.cache_manager else {}
        }

    def reset_metrics(self):
        """Reseta todas as métricas (orquestrador + agentes)"""
        self.metrics = {
            'total_orchestrations': 0,
            'total_cars_scored': 0,
            'total_latency_ms': 0.0,
            'failed_orchestrations': 0,
            'last_update': None
        }

        # Resetar métricas dos agentes
        for agent in self.agents.values():
            if hasattr(agent, 'reset_metrics'):
                agent.reset_metrics()

        # Resetar métricas do cache
        if self.cache_manager:
            self.cache_manager.reset_stats()


# Singleton global (opcional)
_orchestrator_instance = None


def get_scoring_orchestrator(
    cache_manager: Optional[CacheManager] = None,
    enable_parallel: bool = True
) -> ScoringAgentOrchestrator:
    """
    Retorna instância singleton do ScoringAgentOrchestrator

    Args:
        cache_manager: Gerenciador de cache
        enable_parallel: Se deve executar em paralelo

    Returns:
        ScoringAgentOrchestrator: Instância singleton
    """
    global _orchestrator_instance

    if _orchestrator_instance is None:
        _orchestrator_instance = ScoringAgentOrchestrator(
            cache_manager=cache_manager,
            enable_parallel=enable_parallel
        )

    return _orchestrator_instance
