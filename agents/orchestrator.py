#!/usr/bin/env python3
"""
🎭 FacilIAuto Agent Orchestrator
Sistema robusto de coordenação multi-agentes

Coordena todos os agentes especializados garantindo:
- Execução consistente e auditável
- Qualidade empresarial
- Sustentabilidade a longo prazo
- Recuperação automática de erros
"""

import asyncio
import logging
import uuid
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Status dos agentes"""
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    FAILED = "failed"
    MAINTENANCE = "maintenance"

class WorkflowStatus(Enum):
    """Status de workflows"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ValidationResult(Enum):
    """Resultado de validação"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"

@dataclass
class AgentCapability:
    """Definição de capacidade de agente"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    sla_response_time: int  # seconds
    dependencies: List[str] = None

@dataclass
class AgentMetrics:
    """Métricas de performance de agente"""
    agent_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_health_check: datetime = None
    resource_usage: Dict[str, float] = None

@dataclass
class WorkflowDefinition:
    """Definição de workflow"""
    workflow_id: str
    name: str
    description: str
    phases: List[Dict[str, Any]]
    success_criteria: List[str]
    rollback_strategy: str
    timeout: int = 3600  # seconds

@dataclass
class ExecutionContext:
    """Contexto de execução"""
    session_id: str
    workflow_id: str
    user_id: Optional[str] = None
    priority: int = 5  # 1-10, 10 = highest
    metadata: Dict[str, Any] = None
    created_at: datetime = None

class QualitySupervisor:
    """Supervisor de qualidade multi-camadas"""
    
    def __init__(self):
        self.quality_threshold = 0.8
        self.validation_rules = {}
        self.cross_validation_rules = {}
    
    def validate_agent_result(self, agent_id: str, result: Any, context: ExecutionContext) -> Dict[str, Any]:
        """Validação em múltiplas camadas"""
        validation_report = {
            'agent_id': agent_id,
            'session_id': context.session_id,
            'timestamp': datetime.utcnow(),
            'validations': {}
        }
        
        # Layer 1: Schema Validation
        schema_result = self._validate_schema(result, agent_id)
        validation_report['validations']['schema'] = schema_result
        
        # Layer 2: Business Rules  
        business_result = self._validate_business_rules(result, context)
        validation_report['validations']['business_rules'] = business_result
        
        # Layer 3: Quality Metrics
        quality_score = self._calculate_quality_score(result)
        validation_report['validations']['quality_score'] = {
            'score': quality_score,
            'threshold': self.quality_threshold,
            'passed': quality_score >= self.quality_threshold
        }
        
        # Overall result
        all_passed = all(
            v.get('passed', False) if isinstance(v, dict) else v 
            for v in validation_report['validations'].values()
        )
        
        validation_report['overall_result'] = ValidationResult.PASSED if all_passed else ValidationResult.FAILED
        
        return validation_report
    
    def _validate_schema(self, result: Any, agent_id: str) -> Dict[str, Any]:
        """Validação de schema"""
        try:
            # Simplified schema validation
            if result is None:
                return {'passed': False, 'error': 'Result is None'}
            
            if isinstance(result, dict):
                required_fields = self.validation_rules.get(agent_id, {}).get('required_fields', [])
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    return {'passed': False, 'error': f'Missing fields: {missing_fields}'}
            
            return {'passed': True}
            
        except Exception as e:
            return {'passed': False, 'error': f'Schema validation error: {str(e)}'}
    
    def _validate_business_rules(self, result: Any, context: ExecutionContext) -> Dict[str, Any]:
        """Validação de regras de negócio"""
        try:
            # Simplified business rule validation
            if isinstance(result, dict):
                # Example: Check if financial calculations are reasonable
                if 'preco' in result and result['preco'] < 0:
                    return {'passed': False, 'error': 'Price cannot be negative'}
                
                if 'roi' in result and result['roi'] > 10.0:  # 1000% ROI seems unrealistic
                    return {'passed': False, 'error': 'ROI seems unrealistic'}
            
            return {'passed': True}
            
        except Exception as e:
            return {'passed': False, 'error': f'Business rule validation error: {str(e)}'}
    
    def _calculate_quality_score(self, result: Any) -> float:
        """Cálculo de score de qualidade"""
        try:
            score = 1.0
            
            if isinstance(result, dict):
                # Penalize empty or null values
                total_fields = len(result)
                empty_fields = sum(1 for v in result.values() if v in [None, '', [], {}])
                
                if total_fields > 0:
                    score -= (empty_fields / total_fields) * 0.3
                
                # Bonus for rich content
                if len(result) >= 5:  # Rich response
                    score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5  # Default score on error

class ResourceManager:
    """Gerenciador inteligente de recursos"""
    
    def __init__(self):
        self.resource_limits = {
            'max_concurrent_workflows': 50,
            'max_concurrent_agents': 100,
            'memory_limit_mb': 4096,
            'cpu_limit_percent': 80
        }
        self.current_usage = {
            'active_workflows': 0,
            'active_agents': 0,
            'memory_usage_mb': 0,
            'cpu_usage_percent': 0
        }
        self.lock = threading.Lock()
    
    @contextmanager
    def allocate_resources(self, workflow_id: str, estimated_resources: Dict[str, Any]):
        """Context manager para alocação de recursos"""
        try:
            with self.lock:
                if not self._can_allocate(estimated_resources):
                    raise ResourceExhaustionError("Insufficient resources")
                
                self._reserve_resources(estimated_resources)
                logger.info(f"Resources allocated for workflow {workflow_id}")
            
            yield
            
        finally:
            with self.lock:
                self._release_resources(estimated_resources)
                logger.info(f"Resources released for workflow {workflow_id}")
    
    def _can_allocate(self, estimated_resources: Dict[str, Any]) -> bool:
        """Verifica se pode alocar recursos"""
        estimated_workflows = estimated_resources.get('workflows', 1)
        estimated_agents = estimated_resources.get('agents', 5)
        
        if (self.current_usage['active_workflows'] + estimated_workflows > 
            self.resource_limits['max_concurrent_workflows']):
            return False
            
        if (self.current_usage['active_agents'] + estimated_agents > 
            self.resource_limits['max_concurrent_agents']):
            return False
        
        return True
    
    def _reserve_resources(self, resources: Dict[str, Any]):
        """Reserva recursos"""
        self.current_usage['active_workflows'] += resources.get('workflows', 1)
        self.current_usage['active_agents'] += resources.get('agents', 5)
    
    def _release_resources(self, resources: Dict[str, Any]):
        """Libera recursos"""
        self.current_usage['active_workflows'] -= resources.get('workflows', 1)
        self.current_usage['active_agents'] -= resources.get('agents', 5)
        
        # Ensure non-negative values
        self.current_usage['active_workflows'] = max(0, self.current_usage['active_workflows'])
        self.current_usage['active_agents'] = max(0, self.current_usage['active_agents'])

class ErrorHandler:
    """Sistema inteligente de recuperação de erros"""
    
    def __init__(self):
        self.retry_policies = {
            'default': {'max_retries': 3, 'backoff_multiplier': 2, 'initial_delay': 1},
            'network': {'max_retries': 5, 'backoff_multiplier': 1.5, 'initial_delay': 0.5},
            'resource': {'max_retries': 2, 'backoff_multiplier': 3, 'initial_delay': 5}
        }
        self.circuit_breakers = {}
    
    async def handle_agent_failure(self, agent_id: str, error: Exception, context: ExecutionContext) -> Dict[str, Any]:
        """Recuperação inteligente de falhas de agente"""
        error_type = self._classify_error(error)
        
        recovery_result = {
            'agent_id': agent_id,
            'error_type': error_type,
            'original_error': str(error),
            'recovery_attempted': False,
            'recovery_successful': False,
            'final_result': None
        }
        
        try:
            # Get retry policy
            policy = self.retry_policies.get(error_type, self.retry_policies['default'])
            
            # Attempt recovery
            if error_type in ['network', 'timeout', 'temporary']:
                recovery_result['recovery_attempted'] = True
                result = await self._retry_with_backoff(agent_id, context, policy)
                recovery_result['recovery_successful'] = True
                recovery_result['final_result'] = result
            
            elif error_type == 'resource':
                recovery_result['recovery_attempted'] = True
                # Wait and retry once
                await asyncio.sleep(policy['initial_delay'])
                result = await self._execute_agent_with_fallback(agent_id, context)
                recovery_result['recovery_successful'] = True
                recovery_result['final_result'] = result
            
            else:
                # Critical error - escalate
                recovery_result['escalated'] = True
                logger.error(f"Critical error in agent {agent_id}: {error}")
        
        except Exception as recovery_error:
            recovery_result['recovery_error'] = str(recovery_error)
            logger.error(f"Recovery failed for agent {agent_id}: {recovery_error}")
        
        return recovery_result
    
    def _classify_error(self, error: Exception) -> str:
        """Classifica tipo de erro"""
        error_str = str(error).lower()
        
        if 'timeout' in error_str or 'connection' in error_str:
            return 'network'
        elif 'memory' in error_str or 'resource' in error_str:
            return 'resource'
        elif 'temporary' in error_str or 'retry' in error_str:
            return 'temporary'
        else:
            return 'unknown'
    
    async def _retry_with_backoff(self, agent_id: str, context: ExecutionContext, policy: Dict[str, Any]) -> Any:
        """Retry com backoff exponencial"""
        delay = policy['initial_delay']
        
        for attempt in range(policy['max_retries']):
            try:
                await asyncio.sleep(delay)
                result = await self._execute_agent(agent_id, context)
                return result
                
            except Exception as e:
                if attempt == policy['max_retries'] - 1:
                    raise e
                
                delay *= policy['backoff_multiplier']
                logger.warning(f"Retry {attempt + 1} for agent {agent_id} failed: {e}")
    
    async def _execute_agent(self, agent_id: str, context: ExecutionContext) -> Any:
        """Executa agente (placeholder)"""
        # This would be replaced with actual agent execution
        await asyncio.sleep(0.1)  # Simulate work
        return {'agent_id': agent_id, 'result': 'success', 'timestamp': datetime.utcnow()}
    
    async def _execute_agent_with_fallback(self, agent_id: str, context: ExecutionContext) -> Any:
        """Executa agente com fallback"""
        try:
            return await self._execute_agent(agent_id, context)
        except Exception:
            # Try fallback strategy
            return await self._execute_fallback_strategy(agent_id, context)
    
    async def _execute_fallback_strategy(self, agent_id: str, context: ExecutionContext) -> Any:
        """Estratégia de fallback"""
        return {
            'agent_id': agent_id,
            'result': 'fallback_executed',
            'timestamp': datetime.utcnow(),
            'note': 'Primary agent failed, fallback strategy used'
        }

class AuditLogger:
    """Sistema de auditoria empresarial"""
    
    def __init__(self):
        self.audit_store = []
        self.audit_lock = threading.Lock()
    
    def log_decision(self, decision_point: str, inputs: Dict[str, Any], decision: Any, rationale: str, context: ExecutionContext):
        """Log decisões com contexto completo"""
        with self.audit_lock:
            audit_entry = {
                'audit_id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': context.session_id,
                'workflow_id': context.workflow_id,
                'decision_point': decision_point,
                'inputs': inputs,
                'decision': decision,
                'rationale': rationale,
                'user_id': context.user_id,
                'metadata': context.metadata or {}
            }
            
            self.audit_store.append(audit_entry)
            
            # Log for monitoring
            logger.info(f"Decision logged: {decision_point} for session {context.session_id}")
    
    def get_audit_trail(self, session_id: str) -> List[Dict[str, Any]]:
        """Recupera trilha de auditoria para sessão"""
        with self.audit_lock:
            return [entry for entry in self.audit_store if entry['session_id'] == session_id]
    
    def generate_audit_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Gera relatório de auditoria"""
        with self.audit_lock:
            relevant_entries = [
                entry for entry in self.audit_store
                if start_time <= datetime.fromisoformat(entry['timestamp']) <= end_time
            ]
            
            report = {
                'report_id': str(uuid.uuid4()),
                'generated_at': datetime.utcnow().isoformat(),
                'period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'total_decisions': len(relevant_entries),
                'unique_sessions': len(set(entry['session_id'] for entry in relevant_entries)),
                'unique_workflows': len(set(entry['workflow_id'] for entry in relevant_entries)),
                'decisions_by_point': self._group_by_decision_point(relevant_entries),
                'entries': relevant_entries
            }
            
            return report
    
    def _group_by_decision_point(self, entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Agrupa decisões por ponto de decisão"""
        groups = {}
        for entry in entries:
            point = entry['decision_point']
            groups[point] = groups.get(point, 0) + 1
        return groups

class AgentOrchestrator:
    """Maestro central do sistema multi-agentes"""
    
    def __init__(self):
        self.agents = {}
        self.workflows = {}
        self.active_sessions = {}
        self.agent_metrics = {}
        
        # Core components
        self.resource_manager = ResourceManager()
        self.quality_supervisor = QualitySupervisor()
        self.error_handler = ErrorHandler()
        self.audit_logger = AuditLogger()
        
        # Thread pool for concurrent execution
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        # Initialize built-in workflows
        self._initialize_workflows()
        
        logger.info("Agent Orchestrator initialized successfully")
    
    def register_agent(self, agent_id: str, agent_instance: Any, capabilities: List[AgentCapability]):
        """Registra agente no orquestrador"""
        self.agents[agent_id] = {
            'instance': agent_instance,
            'capabilities': capabilities,
            'status': AgentStatus.HEALTHY,
            'registered_at': datetime.utcnow()
        }
        
        self.agent_metrics[agent_id] = AgentMetrics(agent_id=agent_id)
        
        logger.info(f"Agent {agent_id} registered with {len(capabilities)} capabilities")
    
    def register_workflow(self, workflow_def: WorkflowDefinition):
        """Registra workflow no orquestrador"""
        self.workflows[workflow_def.workflow_id] = workflow_def
        logger.info(f"Workflow {workflow_def.workflow_id} registered: {workflow_def.name}")
    
    async def execute_workflow(self, workflow_id: str, context: ExecutionContext, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Executa workflow completo com orquestração"""
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow_def = self.workflows[workflow_id]
        session_id = context.session_id
        
        # Initialize session
        self.active_sessions[session_id] = {
            'workflow_id': workflow_id,
            'status': WorkflowStatus.RUNNING,
            'started_at': datetime.utcnow(),
            'context': context,
            'phase_results': {},
            'audit_trail': []
        }
        
        execution_result = {
            'session_id': session_id,
            'workflow_id': workflow_id,
            'status': WorkflowStatus.RUNNING,
            'started_at': datetime.utcnow(),
            'phase_results': {},
            'errors': [],
            'audit_trail': []
        }
        
        try:
            # Estimate resources needed
            estimated_resources = self._estimate_workflow_resources(workflow_def)
            
            # Allocate resources
            with self.resource_manager.allocate_resources(workflow_id, estimated_resources):
                
                # Execute phases
                for phase in workflow_def.phases:
                    phase_result = await self._execute_phase(phase, context, inputs, execution_result)
                    execution_result['phase_results'][phase['name']] = phase_result
                    
                    # Update session
                    self.active_sessions[session_id]['phase_results'] = execution_result['phase_results']
                    
                    # Validate phase result
                    if not self._validate_phase_success(phase_result):
                        raise WorkflowExecutionError(f"Phase {phase['name']} failed validation")
                
                # Workflow completed successfully
                execution_result['status'] = WorkflowStatus.COMPLETED
                execution_result['completed_at'] = datetime.utcnow()
                
                # Final audit log
                self.audit_logger.log_decision(
                    'workflow_completion',
                    {'workflow_id': workflow_id, 'inputs': inputs},
                    {'status': 'completed', 'phase_count': len(workflow_def.phases)},
                    f"Workflow {workflow_id} completed successfully",
                    context
                )
        
        except Exception as e:
            # Handle workflow failure
            execution_result['status'] = WorkflowStatus.FAILED
            execution_result['error'] = str(e)
            execution_result['failed_at'] = datetime.utcnow()
            
            # Attempt recovery
            recovery_result = await self._attempt_workflow_recovery(workflow_id, context, e)
            execution_result['recovery_attempt'] = recovery_result
            
            # Audit failure
            self.audit_logger.log_decision(
                'workflow_failure',
                {'workflow_id': workflow_id, 'inputs': inputs},
                {'status': 'failed', 'error': str(e)},
                f"Workflow {workflow_id} failed: {str(e)}",
                context
            )
            
            logger.error(f"Workflow {workflow_id} failed: {e}")
        
        finally:
            # Cleanup session
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['status'] = execution_result['status']
                self.active_sessions[session_id]['completed_at'] = datetime.utcnow()
        
        return execution_result
    
    async def _execute_phase(self, phase: Dict[str, Any], context: ExecutionContext, inputs: Dict[str, Any], workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma fase do workflow"""
        phase_name = phase['name']
        required_agents = phase.get('agents', [])
        is_parallel = phase.get('parallel', False)
        timeout = phase.get('timeout', 300)
        
        phase_result = {
            'phase': phase_name,
            'started_at': datetime.utcnow(),
            'agent_results': {},
            'status': 'running'
        }
        
        try:
            if is_parallel:
                # Execute agents in parallel
                tasks = []
                for agent_id in required_agents:
                    task = asyncio.create_task(
                        self._execute_agent_with_timeout(agent_id, context, inputs, timeout)
                    )
                    tasks.append((agent_id, task))
                
                # Wait for all tasks with timeout
                for agent_id, task in tasks:
                    try:
                        result = await asyncio.wait_for(task, timeout=timeout)
                        phase_result['agent_results'][agent_id] = result
                    except asyncio.TimeoutError:
                        phase_result['agent_results'][agent_id] = {'error': 'timeout', 'timeout': timeout}
                    except Exception as e:
                        phase_result['agent_results'][agent_id] = {'error': str(e)}
            
            else:
                # Execute agents sequentially
                current_inputs = inputs.copy()
                
                for agent_id in required_agents:
                    try:
                        result = await self._execute_agent_with_timeout(agent_id, context, current_inputs, timeout)
                        phase_result['agent_results'][agent_id] = result
                        
                        # Chain results for next agent
                        if isinstance(result, dict):
                            current_inputs.update(result)
                            
                    except Exception as e:
                        phase_result['agent_results'][agent_id] = {'error': str(e)}
                        # Stop sequential execution on error
                        break
            
            # Validate phase results
            validation_results = {}
            for agent_id, result in phase_result['agent_results'].items():
                if 'error' not in result:
                    validation = self.quality_supervisor.validate_agent_result(agent_id, result, context)
                    validation_results[agent_id] = validation
            
            phase_result['validations'] = validation_results
            phase_result['status'] = 'completed'
            phase_result['completed_at'] = datetime.utcnow()
            
            # Audit phase completion
            self.audit_logger.log_decision(
                f'phase_completion_{phase_name}',
                {'phase': phase_name, 'agents': required_agents},
                phase_result,
                f"Phase {phase_name} completed with {len(required_agents)} agents",
                context
            )
        
        except Exception as e:
            phase_result['status'] = 'failed'
            phase_result['error'] = str(e)
            phase_result['failed_at'] = datetime.utcnow()
            
            logger.error(f"Phase {phase_name} failed: {e}")
        
        return phase_result
    
    async def _execute_agent_with_timeout(self, agent_id: str, context: ExecutionContext, inputs: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Executa agente com timeout e error handling"""
        try:
            # Check agent health
            if not self._is_agent_healthy(agent_id):
                raise AgentUnavailableError(f"Agent {agent_id} is not healthy")
            
            # Execute agent
            start_time = time.time()
            
            # This is a placeholder - in real implementation, this would call the actual agent
            result = await self._simulate_agent_execution(agent_id, inputs)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Update metrics
            self._update_agent_metrics(agent_id, execution_time, success=True)
            
            return result
            
        except Exception as e:
            # Handle agent failure
            self._update_agent_metrics(agent_id, 0, success=False)
            recovery_result = await self.error_handler.handle_agent_failure(agent_id, e, context)
            
            if recovery_result['recovery_successful']:
                return recovery_result['final_result']
            else:
                raise e
    
    async def _simulate_agent_execution(self, agent_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simula execução de agente (placeholder)"""
        # Simulate processing time
        await asyncio.sleep(0.1 + (hash(agent_id) % 10) / 20)  # 0.1-0.6 seconds
        
        # Simulate different agent behaviors
        agent_responses = {
            'business_analyst': {
                'market_analysis': 'positive',
                'roi_projection': 380,
                'market_size': 50000000,
                'recommendations': ['focus_on_mobile', 'target_SMB']
            },
            'ai_engineer': {
                'model_accuracy': 0.87,
                'processing_time': 2.1,
                'recommendations_generated': 5,
                'algorithm_performance': 'optimal'
            },
            'tech_lead': {
                'architecture_review': 'approved',
                'scalability_assessment': 'high',
                'technical_debt': 'low',
                'deployment_ready': True
            },
            'marketing_strategist': {
                'campaign_strategy': 'multi_channel',
                'target_audience': ['small_dealerships', 'medium_dealerships'],
                'budget_allocation': {'digital': 70, 'traditional': 30},
                'expected_conversion': 0.12
            }
        }
        
        base_result = agent_responses.get(agent_id, {
            'status': 'completed',
            'agent_id': agent_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Add some randomness for testing
        if hash(agent_id + str(time.time())) % 20 == 0:  # 5% chance of simulated error
            raise Exception(f"Simulated error in agent {agent_id}")
        
        return base_result
    
    def _is_agent_healthy(self, agent_id: str) -> bool:
        """Verifica se agente está saudável"""
        if agent_id not in self.agents:
            return False
        
        agent_info = self.agents[agent_id]
        return agent_info['status'] == AgentStatus.HEALTHY
    
    def _update_agent_metrics(self, agent_id: str, execution_time: float, success: bool):
        """Atualiza métricas do agente"""
        if agent_id in self.agent_metrics:
            metrics = self.agent_metrics[agent_id]
            metrics.total_requests += 1
            
            if success:
                metrics.successful_requests += 1
                # Update rolling average
                if metrics.avg_response_time == 0:
                    metrics.avg_response_time = execution_time
                else:
                    metrics.avg_response_time = (metrics.avg_response_time + execution_time) / 2
            else:
                metrics.failed_requests += 1
            
            metrics.last_health_check = datetime.utcnow()
    
    def _estimate_workflow_resources(self, workflow_def: WorkflowDefinition) -> Dict[str, Any]:
        """Estima recursos necessários para workflow"""
        total_agents = sum(len(phase.get('agents', [])) for phase in workflow_def.phases)
        
        return {
            'workflows': 1,
            'agents': total_agents,
            'estimated_duration': workflow_def.timeout,
            'memory_mb': total_agents * 50,  # Estimate 50MB per agent
            'cpu_percent': min(80, total_agents * 5)  # Estimate 5% CPU per agent
        }
    
    def _validate_phase_success(self, phase_result: Dict[str, Any]) -> bool:
        """Valida se fase foi bem-sucedida"""
        if phase_result['status'] != 'completed':
            return False
        
        # Check if any agent failed
        for agent_id, result in phase_result.get('agent_results', {}).items():
            if 'error' in result:
                return False
        
        # Check validation results
        validations = phase_result.get('validations', {})
        for agent_id, validation in validations.items():
            if validation.get('overall_result') == ValidationResult.FAILED:
                return False
        
        return True
    
    async def _attempt_workflow_recovery(self, workflow_id: str, context: ExecutionContext, error: Exception) -> Dict[str, Any]:
        """Tenta recuperação de workflow"""
        recovery_result = {
            'attempted': True,
            'strategy': 'restart_from_checkpoint',
            'successful': False,
            'error': str(error)
        }
        
        try:
            # Simple recovery strategy: log and prepare for manual intervention
            logger.warning(f"Workflow {workflow_id} recovery attempted for error: {error}")
            
            # In a real implementation, this would implement sophisticated recovery
            # For now, just log the attempt
            recovery_result['manual_intervention_required'] = True
            recovery_result['recovery_ticket_id'] = str(uuid.uuid4())
            
        except Exception as recovery_error:
            recovery_result['recovery_error'] = str(recovery_error)
        
        return recovery_result
    
    def register_context_skill(self, context_skill_instance):
        """Registra a Context-Based Recommendation Skill"""
        skill_capabilities = [
            AgentCapability(
                name="contextual_search",
                description="Busca contextual de veículos baseada em intenção",
                input_schema={
                    "query": "string",
                    "user_data": "object"
                },
                output_schema={
                    "recommendations": "array",
                    "context_analysis": "object"
                },
                sla_response_time=30
            ),
            AgentCapability(
                name="intent_classification", 
                description="Classificação de intenção de busca",
                input_schema={
                    "query": "string"
                },
                output_schema={
                    "intent": "string",
                    "confidence": "float",
                    "entities": "array"
                },
                sla_response_time=10
            )
        ]
        
        self.register_agent("context_recommendation_skill", context_skill_instance, skill_capabilities)
        logger.info("Context-Based Recommendation Skill registrada no orquestrador")

    def _initialize_workflows(self):
        """Inicializa workflows built-in"""
        
        # Workflow: Contextual Vehicle Search
        contextual_search = WorkflowDefinition(
            workflow_id='contextual_vehicle_search',
            name='Busca Contextual de Veículos',
            description='Workflow para busca inteligente baseada em contexto',
            phases=[
                {
                    'name': 'intent_analysis',
                    'agents': ['context_recommendation_skill'],
                    'parallel': False,
                    'timeout': 30
                },
                {
                    'name': 'recommendation_generation',
                    'agents': ['context_recommendation_skill', 'ai_engineer'],
                    'parallel': True,
                    'timeout': 60
                },
                {
                    'name': 'result_validation',
                    'agents': ['business_analyst', 'tech_lead'],
                    'parallel': True,
                    'timeout': 30
                }
            ],
            success_criteria=['intent_detected', 'recommendations_generated'],
            rollback_strategy='fallback_to_standard_search',
            timeout=180
        )
        
        self.register_workflow(contextual_search)
        
        # Workflow: Product Launch
        product_launch = WorkflowDefinition(
            workflow_id='product_launch',
            name='Product Launch Workflow',
            description='Complete product launch coordination',
            phases=[
                {
                    'name': 'discovery',
                    'agents': ['business_analyst', 'market_researcher'],
                    'parallel': True,
                    'timeout': 300
                },
                {
                    'name': 'technical_design',
                    'agents': ['system_architect', 'tech_lead'],
                    'parallel': True,
                    'timeout': 600
                },
                {
                    'name': 'implementation',
                    'agents': ['ai_engineer', 'tech_lead'],
                    'parallel': False,
                    'timeout': 1200
                },
                {
                    'name': 'marketing_launch',
                    'agents': ['marketing_strategist', 'content_creator'],
                    'parallel': True,
                    'timeout': 300
                }
            ],
            success_criteria=['all_phases_complete', 'quality_gates_passed'],
            rollback_strategy='checkpoint_recovery',
            timeout=3600
        )
        
        self.register_workflow(product_launch)
        
        # Workflow: Customer Acquisition
        customer_acquisition = WorkflowDefinition(
            workflow_id='customer_acquisition',
            name='Customer Acquisition Campaign',
            description='End-to-end customer acquisition workflow',
            phases=[
                {
                    'name': 'market_analysis',
                    'agents': ['business_analyst', 'data_analyst'],
                    'parallel': True,
                    'timeout': 240
                },
                {
                    'name': 'strategy_development',
                    'agents': ['marketing_strategist', 'sales_coach'],
                    'parallel': False,
                    'timeout': 300
                },
                {
                    'name': 'execution',
                    'agents': ['marketing_strategist', 'operations_manager'],
                    'parallel': True,
                    'timeout': 600
                }
            ],
            success_criteria=['all_phases_complete'],
            rollback_strategy='restart',
            timeout=1800
        )
        
        self.register_workflow(customer_acquisition)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        return {
            'orchestrator': {
                'status': 'healthy',
                'uptime': datetime.utcnow(),
                'active_sessions': len(self.active_sessions),
                'registered_agents': len(self.agents),
                'registered_workflows': len(self.workflows)
            },
            'agents': {
                agent_id: {
                    'status': info['status'].value,
                    'registered_at': info['registered_at'],
                    'metrics': asdict(self.agent_metrics.get(agent_id, AgentMetrics(agent_id)))
                }
                for agent_id, info in self.agents.items()
            },
            'resource_usage': self.resource_manager.current_usage,
            'recent_audit_entries': len(self.audit_logger.audit_store)
        }
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de sessão específica"""
        return self.active_sessions.get(session_id)
    
    def get_audit_trail(self, session_id: str) -> List[Dict[str, Any]]:
        """Retorna trilha de auditoria para sessão"""
        return self.audit_logger.get_audit_trail(session_id)

# Custom Exceptions
class AgentOrchestratorError(Exception):
    """Base exception for orchestrator errors"""
    pass

class AgentUnavailableError(AgentOrchestratorError):
    """Agent is not available"""
    pass

class WorkflowExecutionError(AgentOrchestratorError):
    """Workflow execution failed"""
    pass

class ResourceExhaustionError(AgentOrchestratorError):
    """System resources exhausted"""
    pass

# Example usage and testing
async def main():
    """Exemplo de uso do orquestrador"""
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Register some mock agents (in real implementation, these would be actual agent instances)
    mock_agents = [
        'business_analyst', 'ai_engineer', 'tech_lead', 'marketing_strategist',
        'system_architect', 'market_researcher', 'content_creator', 'data_analyst',
        'sales_coach', 'operations_manager'
    ]
    
    for agent_id in mock_agents:
        orchestrator.register_agent(
            agent_id, 
            f"MockAgent_{agent_id}",  # This would be actual agent instance
            [AgentCapability(
                name=f"{agent_id}_capability",
                description=f"Primary capability of {agent_id}",
                input_schema={},
                output_schema={},
                sla_response_time=30
            )]
        )
    
    # Create execution context
    context = ExecutionContext(
        session_id=str(uuid.uuid4()),
        workflow_id='product_launch',
        user_id='test_user',
        priority=8,
        metadata={'test_run': True},
        created_at=datetime.utcnow()
    )
    
    # Execute workflow
    print("🎭 Starting Product Launch Workflow...")
    result = await orchestrator.execute_workflow(
        'product_launch',
        context,
        {'product_name': 'FacilIAuto', 'target_market': 'automotive'}
    )
    
    print(f"✅ Workflow completed with status: {result['status']}")
    print(f"📊 Phases executed: {len(result['phase_results'])}")
    
    # Show system status
    status = orchestrator.get_system_status()
    print(f"🔧 System Status: {status['orchestrator']['status']}")
    print(f"🤖 Active Agents: {status['orchestrator']['registered_agents']}")
    
    # Show audit trail
    audit_trail = orchestrator.get_audit_trail(context.session_id)
    print(f"📋 Audit Entries: {len(audit_trail)}")
    
    return result

if __name__ == "__main__":
    # Run example
    result = asyncio.run(main())
    print(f"\n🎉 Orchestrator demo completed successfully!")
    print(f"📄 Final result status: {result['status']}")
