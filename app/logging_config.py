"""
🔍 Sistema de Logging Estruturado - FacilIAuto
Implementa logs JSON com correlation ID e contexto automático
"""
import json
import logging
import time
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

# Context variables para rastreamento de requisições
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
request_start_time_var: ContextVar[Optional[float]] = ContextVar('request_start_time', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Formatter customizado para logs estruturados em JSON
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata o log em JSON estruturado
        """
        # Dados básicos do log
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adiciona correlation_id se disponível
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id
            
        # Adiciona tempo de request se disponível
        start_time = request_start_time_var.get()
        if start_time:
            log_data["request_duration_ms"] = round((time.time() - start_time) * 1000, 2)
        
        # Adiciona contexto extra se fornecido
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
            
        # Adiciona informações de exceção se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data, ensure_ascii=False)


class ContextLogger:
    """
    Logger wrapper que automaticamente adiciona contexto às mensagens
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log_with_context(self, level: int, message: str, **kwargs) -> None:
        """Log com contexto automático"""
        extra_data = kwargs.copy()
        
        # Cria um LogRecord customizado
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        
        # Adiciona dados extras
        if extra_data:
            record.extra_data = extra_data
            
        self.logger.handle(record)
    
    def info(self, message: str, **kwargs) -> None:
        """Log nível INFO"""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log nível ERROR"""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log nível WARNING"""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log nível DEBUG"""
        self._log_with_context(logging.DEBUG, message, **kwargs)


def setup_logging(level: str = "INFO", enable_structured: bool = True) -> None:
    """
    Configura o sistema de logging
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        enable_structured: Se True, usa formato JSON estruturado
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Remove handlers existentes
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configura handler console
    console_handler = logging.StreamHandler()
    
    if enable_structured:
        # Usa formatter estruturado
        formatter = StructuredFormatter()
    else:
        # Usa formatter padrão para desenvolvimento
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Configura logger raiz
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Silencia logs excessivos de libraries externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> ContextLogger:
    """
    Retorna um logger contextualizado
    
    Args:
        name: Nome do logger (geralmente __name__)
    
    Returns:
        ContextLogger configurado
    """
    return ContextLogger(name)


def generate_correlation_id() -> str:
    """
    Gera um correlation ID único para rastreamento de requisições
    
    Returns:
        UUID4 como string
    """
    return str(uuid.uuid4())


def set_correlation_context(correlation_id: str, start_time: Optional[float] = None) -> None:
    """
    Define o contexto de correlação para a requisição atual
    
    Args:
        correlation_id: ID único da requisição
        start_time: Timestamp de início da requisição
    """
    correlation_id_var.set(correlation_id)
    if start_time is None:
        start_time = time.time()
    request_start_time_var.set(start_time)


def clear_correlation_context() -> None:
    """
    Limpa o contexto de correlação
    """
    correlation_id_var.set(None)
    request_start_time_var.set(None)


# Configurações de metrics simples
class MetricsCollector:
    """
    Coletor simples de métricas para monitoramento básico
    """
    
    def __init__(self):
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0
        self.endpoint_stats: Dict[str, Dict[str, Any]] = {}
    
    def record_request(self, endpoint: str, response_time: float, status_code: int) -> None:
        """
        Registra uma requisição
        
        Args:
            endpoint: Nome do endpoint
            response_time: Tempo de resposta em segundos
            status_code: Código de status HTTP
        """
        self.request_count += 1
        self.total_response_time += response_time
        
        if status_code >= 400:
            self.error_count += 1
        
        # Stats por endpoint
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                "count": 0,
                "total_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "errors": 0
            }
        
        stats = self.endpoint_stats[endpoint]
        stats["count"] += 1
        stats["total_time"] += response_time
        stats["min_time"] = min(stats["min_time"], response_time)
        stats["max_time"] = max(stats["max_time"], response_time)
        
        if status_code >= 400:
            stats["errors"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas coletadas
        
        Returns:
            Dicionário com métricas
        """
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        # Calcula médias por endpoint
        endpoint_metrics = {}
        for endpoint, stats in self.endpoint_stats.items():
            if stats["count"] > 0:
                endpoint_metrics[endpoint] = {
                    "requests": stats["count"],
                    "avg_response_time": stats["total_time"] / stats["count"],
                    "min_response_time": stats["min_time"],
                    "max_response_time": stats["max_time"],
                    "error_rate": stats["errors"] / stats["count"],
                    "errors": stats["errors"]
                }
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "avg_response_time": avg_response_time,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "endpoints": endpoint_metrics
        }
    
    def reset(self) -> None:
        """Reset todas as métricas"""
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0
        self.endpoint_stats.clear()


# Instância global do coletor de métricas
metrics_collector = MetricsCollector()
