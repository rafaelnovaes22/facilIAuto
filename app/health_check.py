"""
🏥 Sistema de Health Check Avançado - FacilIAuto
Diagnósticos detalhados de saúde do sistema e dependências
"""
import asyncio
import os
import platform
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil
from fastapi import HTTPException

from app.logging_config import get_logger, metrics_collector

logger = get_logger(__name__)


class HealthStatus:
    """Enum para status de saúde"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheckService:
    """
    Serviço de verificação de saúde do sistema
    """
    
    def __init__(self):
        self.startup_time = datetime.utcnow()
        self.last_health_check = None
        self.dependency_cache = {}
        self.cache_ttl = 30  # segundos
    
    async def get_full_health_report(self) -> Dict[str, Any]:
        """
        Retorna relatório completo de saúde do sistema
        
        Returns:
            Dicionário com status detalhado
        """
        start_time = time.time()
        
        try:
            # Coleta dados em paralelo
            system_info = await self._get_system_info()
            dependency_status = await self._check_dependencies()
            application_metrics = self._get_application_metrics()
            performance_metrics = self._get_performance_metrics()
            
            # Determina status geral
            overall_status = self._determine_overall_status(dependency_status)
            
            # Calcula tempo de verificação
            check_duration = round((time.time() - start_time) * 1000, 2)
            
            health_report = {
                "status": overall_status,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "uptime": self._get_uptime(),
                "check_duration_ms": check_duration,
                "version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development"),
                "system": system_info,
                "dependencies": dependency_status,
                "metrics": application_metrics,
                "performance": performance_metrics,
                "details": {
                    "startup_time": self.startup_time.isoformat() + "Z",
                    "last_check": datetime.utcnow().isoformat() + "Z",
                    "python_version": sys.version.split()[0],
                    "platform": platform.platform()
                }
            }
            
            self.last_health_check = datetime.utcnow()
            
            logger.info(
                f"Health check completed - Status: {overall_status}",
                status=overall_status,
                check_duration_ms=check_duration,
                dependencies_count=len(dependency_status)
            )
            
            return health_report
            
        except Exception as exc:
            logger.error(
                f"Health check failed: {type(exc).__name__}",
                exception_type=type(exc).__name__,
                exception_message=str(exc)
            )
            
            return {
                "status": HealthStatus.UNHEALTHY,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": f"Health check failed: {str(exc)}",
                "check_duration_ms": round((time.time() - start_time) * 1000, 2)
            }
    
    async def get_simple_health_check(self) -> Dict[str, Any]:
        """
        Retorna verificação simples e rápida de saúde
        
        Returns:
            Status básico para load balancers
        """
        try:
            # Verificações básicas e rápidas
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            # Considera unhealthy se memória > 90% ou disco > 95%
            if memory_usage > 90 or disk_usage > 95:
                status = HealthStatus.UNHEALTHY
            elif memory_usage > 80 or disk_usage > 85:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "status": status,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "uptime": self._get_uptime()
            }
            
        except Exception as exc:
            logger.error(f"Simple health check failed: {str(exc)}")
            return {
                "status": HealthStatus.UNHEALTHY,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "error": str(exc)
            }
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """
        Coleta informações do sistema
        
        Returns:
            Informações de CPU, memória, disco
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "cores": psutil.cpu_count(),
                    "cores_logical": psutil.cpu_count(logical=True)
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent,
                    "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 90 else "critical"
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2),
                    "status": "healthy" if disk.used / disk.total < 0.85 else "warning" if disk.used / disk.total < 0.95 else "critical"
                }
            }
            
        except Exception as exc:
            logger.error(f"Failed to collect system info: {str(exc)}")
            return {"error": str(exc)}
    
    async def _check_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """
        Verifica status das dependências externas
        
        Returns:
            Status de cada dependência
        """
        dependencies = {}
        
        # Verifica dependências em paralelo
        checks = [
            self._check_database(),
            self._check_langgraph_system(),
            self._check_memory_system(),
            self._check_file_system()
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        dep_names = ["database", "langgraph", "memory_system", "file_system"]
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                dependencies[dep_names[i]] = {
                    "status": HealthStatus.UNHEALTHY,
                    "error": str(result),
                    "last_checked": datetime.utcnow().isoformat() + "Z"
                }
            else:
                dependencies[dep_names[i]] = result
        
        return dependencies
    
    async def _check_database(self) -> Dict[str, Any]:
        """Verifica conectividade com banco de dados"""
        try:
            from app.database import get_carros
            
            start_time = time.time()
            # Tenta uma consulta simples
            carros = get_carros()
            # Verificar se retornou lista não vazia
            if not carros or len(carros) == 0:
                raise Exception("Nenhum carro encontrado no banco")
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "status": HealthStatus.HEALTHY,
                "response_time_ms": response_time,
                "records_available": len(carros) > 0,
                "last_checked": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as exc:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(exc),
                "last_checked": datetime.utcnow().isoformat() + "Z"
            }
    
    async def _check_langgraph_system(self) -> Dict[str, Any]:
        """Verifica sistema LangGraph"""
        try:
            from app.langgraph_chatbot_graph import FacilIAutoChatbotGraph
            
            start_time = time.time()
            graph = FacilIAutoChatbotGraph()
            
            # Verifica se consegue criar o grafo
            # Testar se o grafo já está compilado
            stats = graph.obter_estatisticas_grafo()
            if stats.get("status") != "compiled and ready":
                raise Exception(f"Grafo não está pronto: {stats.get('status', 'unknown')}")
            initialization_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "status": HealthStatus.HEALTHY,
                "initialization_time_ms": initialization_time,
                "agents_available": 6,  # Número de agentes configurados
                "graph_ready": app_graph is not None,
                "last_checked": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as exc:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(exc),
                "last_checked": datetime.utcnow().isoformat() + "Z"
            }
    
    async def _check_memory_system(self) -> Dict[str, Any]:
        """Verifica sistema de memória"""
        try:
            from app.memory_manager import get_memory_manager
            
            start_time = time.time()
            memory_manager = get_memory_manager()
            
            # Testa criação de conversa
            test_conversation = memory_manager.create_conversation(
                carro_id=1,
                carro_data={"marca": "Test", "modelo": "Health Check"},
                user_session_id="health_check"
            )
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "status": HealthStatus.HEALTHY,
                "response_time_ms": response_time,
                "manager_available": memory_manager is not None,
                "test_conversation_id": test_conversation.conversation_id if test_conversation else None,
                "last_checked": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as exc:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(exc),
                "last_checked": datetime.utcnow().isoformat() + "Z"
            }
    
    async def _check_file_system(self) -> Dict[str, Any]:
        """Verifica sistema de arquivos"""
        try:
            # Verifica se consegue ler/escrever em diretórios importantes
            directories = ["static", "logs"]
            status = {}
            
            for directory in directories:
                if os.path.exists(directory):
                    if os.path.isdir(directory):
                        if os.access(directory, os.R_OK | os.W_OK):
                            status[directory] = "accessible"
                        else:
                            status[directory] = "permission_denied"
                    else:
                        status[directory] = "not_directory"
                else:
                    status[directory] = "not_found"
            
            return {
                "status": HealthStatus.HEALTHY,
                "directories": status,
                "working_directory": os.getcwd(),
                "last_checked": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as exc:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error": str(exc),
                "last_checked": datetime.utcnow().isoformat() + "Z"
            }
    
    def _get_application_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas da aplicação
        
        Returns:
            Métricas coletadas pelo metrics_collector
        """
        try:
            return metrics_collector.get_metrics()
        except Exception as exc:
            logger.error(f"Failed to get application metrics: {str(exc)}")
            return {"error": str(exc)}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas de performance do sistema
        
        Returns:
            Métricas de performance
        """
        try:
            process = psutil.Process()
            
            return {
                "memory_usage_mb": round(process.memory_info().rss / (1024**2), 2),
                "cpu_percent": process.cpu_percent(),
                "threads_count": process.num_threads(),
                "file_descriptors": process.num_fds() if hasattr(process, 'num_fds') else None,
                "connections_count": len(process.connections()) if hasattr(process, 'connections') else None,
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat() + "Z"
            }
            
        except Exception as exc:
            logger.error(f"Failed to get performance metrics: {str(exc)}")
            return {"error": str(exc)}
    
    def _determine_overall_status(self, dependencies: Dict[str, Dict[str, Any]]) -> str:
        """
        Determina status geral baseado nas dependências
        
        Args:
            dependencies: Status das dependências
            
        Returns:
            Status geral do sistema
        """
        unhealthy_count = 0
        degraded_count = 0
        
        for dep_status in dependencies.values():
            if dep_status.get("status") == HealthStatus.UNHEALTHY:
                unhealthy_count += 1
            elif dep_status.get("status") == HealthStatus.DEGRADED:
                degraded_count += 1
        
        # Se alguma dependência crítica estiver unhealthy
        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        
        # Se há dependências degradadas
        if degraded_count > 0:
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def _get_uptime(self) -> str:
        """
        Calcula tempo de uptime da aplicação
        
        Returns:
            String formatada do uptime
        """
        uptime_delta = datetime.utcnow() - self.startup_time
        total_seconds = int(uptime_delta.total_seconds())
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


# Instância global do serviço
health_service = HealthCheckService()
