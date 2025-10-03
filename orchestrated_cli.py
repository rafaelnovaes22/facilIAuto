#!/usr/bin/env python3
"""
🎭 FacilIAuto Orchestrated CLI
Interface de linha de comando que integra o Agent Orchestrator com os agentes especializados

Este script permite executar workflows orquestrados usando os contextos dos agentes reais.
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestrator import (
    AgentOrchestrator, 
    ExecutionContext, 
    AgentCapability,
    WorkflowDefinition
)

class FacilIAutoAgent:
    """Wrapper para agentes especializados baseados em contexto"""
    
    def __init__(self, agent_id: str, context_path: str):
        self.agent_id = agent_id
        self.context_path = context_path
        self.context = self._load_context()
    
    def _load_context(self):
        """Carrega contexto do agente"""
        if os.path.exists(self.context_path):
            with open(self.context_path, 'r', encoding='utf-8') as f:
                return f.read()
        return f"Context for {self.agent_id} not found"
    
    async def execute(self, task: str, inputs: dict) -> dict:
        """Executa tarefa do agente baseada no contexto"""
        # Simula execução baseada no contexto real
        await asyncio.sleep(0.2)  # Simulate processing
        
        return {
            'agent_id': self.agent_id,
            'task': task,
            'status': 'completed',
            'result': f"Task '{task}' executed by {self.agent_id}",
            'context_loaded': len(self.context) > 0,
            'timestamp': datetime.utcnow().isoformat()
        }

class FacilIAutoOrchestratedCLI:
    """CLI orquestrado para FacilIAuto"""
    
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.agents = {}
        self._initialize_agents()
        self._initialize_workflows()
    
    def _initialize_agents(self):
        """Inicializa agentes baseados nos contextos reais"""
        agent_dirs = [
            'AI Engineer',
            'Business Analyst', 
            'Tech Lead',
            'Marketing Strategist',
            'UX Especialist',
            'Data Analyst',
            'Sales Coach',
            'Operations Manager',
            'Content Creator',
            'Financial Advisor',
            'System Archictecture',
            'Product Manager'
        ]
        
        for agent_dir in agent_dirs:
            context_path = os.path.join(agent_dir, 'context.md')
            if os.path.exists(context_path):
                # Normalize agent ID
                agent_id = agent_dir.lower().replace(' ', '_').replace('archictecture', 'architect')
                
                # Create agent instance
                agent = FacilIAutoAgent(agent_id, context_path)
                self.agents[agent_id] = agent
                
                # Register with orchestrator
                capabilities = self._extract_capabilities_from_context(agent.context, agent_id)
                self.orchestrator.register_agent(
                    agent_id,
                    agent,
                    capabilities
                )
                
                print(f"✅ Agent {agent_id} registrado com contexto de {len(agent.context)} caracteres")
    
    def _extract_capabilities_from_context(self, context: str, agent_id: str) -> list:
        """Extrai capacidades do contexto do agente"""
        # Parse context to find capabilities
        capabilities = []
        
        # Default capability based on agent type
        if 'ai_engineer' in agent_id:
            capabilities.append(AgentCapability(
                name='machine_learning',
                description='Desenvolvimento e otimização de modelos ML',
                input_schema={'model_type': 'str', 'data': 'dict'},
                output_schema={'model': 'dict', 'accuracy': 'float'},
                sla_response_time=120
            ))
        elif 'business_analyst' in agent_id:
            capabilities.append(AgentCapability(
                name='business_analysis',
                description='Análise de negócio e ROI',
                input_schema={'business_data': 'dict'},
                output_schema={'analysis': 'dict', 'recommendations': 'list'},
                sla_response_time=60
            ))
        elif 'tech_lead' in agent_id:
            capabilities.append(AgentCapability(
                name='technical_leadership',
                description='Liderança técnica e arquitetura',
                input_schema={'requirements': 'dict'},
                output_schema={'architecture': 'dict', 'plan': 'dict'},
                sla_response_time=90
            ))
        elif 'marketing' in agent_id:
            capabilities.append(AgentCapability(
                name='marketing_strategy',
                description='Estratégia de marketing',
                input_schema={'market_data': 'dict', 'budget': 'float'},
                output_schema={'strategy': 'dict', 'campaign': 'dict'},
                sla_response_time=75
            ))
        else:
            # Generic capability
            capabilities.append(AgentCapability(
                name=f'{agent_id}_specialty',
                description=f'Especialidade do {agent_id}',
                input_schema={'task': 'str'},
                output_schema={'result': 'dict'},
                sla_response_time=60
            ))
        
        return capabilities
    
    def _initialize_workflows(self):
        """Inicializa workflows específicos do FacilIAuto"""
        
        # Workflow: Startup Validation
        startup_validation = WorkflowDefinition(
            workflow_id='startup_validation',
            name='FacilIAuto Startup Validation',
            description='Validação completa da startup FacilIAuto',
            phases=[
                {
                    'name': 'market_validation',
                    'agents': ['business_analyst', 'data_analyst'],
                    'parallel': True,
                    'timeout': 180
                },
                {
                    'name': 'technical_validation',
                    'agents': ['ai_engineer', 'tech_lead'],
                    'parallel': True,
                    'timeout': 240
                },
                {
                    'name': 'business_model_validation',
                    'agents': ['business_analyst', 'financial_advisor'],
                    'parallel': True,
                    'timeout': 200
                }
            ],
            success_criteria=['market_validated', 'tech_validated', 'business_validated'],
            rollback_strategy='checkpoint_recovery',
            timeout=900
        )
        
        self.orchestrator.register_workflow(startup_validation)
        
        # Workflow: Product Development
        product_development = WorkflowDefinition(
            workflow_id='product_development',
            name='FacilIAuto Product Development',
            description='Desenvolvimento completo do produto FacilIAuto',
            phases=[
                {
                    'name': 'requirements_analysis',
                    'agents': ['product_manager', 'business_analyst'],
                    'parallel': False,
                    'timeout': 300
                },
                {
                    'name': 'system_design',
                    'agents': ['system_architect', 'tech_lead'],
                    'parallel': True,
                    'timeout': 400
                },
                {
                    'name': 'ai_development',
                    'agents': ['ai_engineer', 'data_analyst'],
                    'parallel': True,
                    'timeout': 600
                },
                {
                    'name': 'ux_design',
                    'agents': ['ux_especialist', 'product_manager'],
                    'parallel': True,
                    'timeout': 350
                }
            ],
            success_criteria=['requirements_complete', 'design_approved', 'ai_functional', 'ux_validated'],
            rollback_strategy='phase_rollback',
            timeout=2100
        )
        
        self.orchestrator.register_workflow(product_development)
        
        # Workflow: Go-to-Market
        go_to_market = WorkflowDefinition(
            workflow_id='go_to_market',
            name='FacilIAuto Go-to-Market',
            description='Estratégia completa de entrada no mercado',
            phases=[
                {
                    'name': 'market_strategy',
                    'agents': ['marketing_strategist', 'business_analyst'],
                    'parallel': True,
                    'timeout': 240
                },
                {
                    'name': 'sales_strategy',
                    'agents': ['sales_coach', 'operations_manager'],
                    'parallel': True,
                    'timeout': 200
                },
                {
                    'name': 'content_creation',
                    'agents': ['content_creator', 'marketing_strategist'],
                    'parallel': True,
                    'timeout': 300
                },
                {
                    'name': 'launch_execution',
                    'agents': ['operations_manager', 'marketing_strategist', 'sales_coach'],
                    'parallel': True,
                    'timeout': 180
                }
            ],
            success_criteria=['strategy_defined', 'content_ready', 'launch_executed'],
            rollback_strategy='restart',
            timeout=1200
        )
        
        self.orchestrator.register_workflow(go_to_market)
    
    async def execute_workflow(self, workflow_id: str, user_inputs: dict = None):
        """Executa workflow orquestrado"""
        if workflow_id not in self.orchestrator.workflows:
            available = list(self.orchestrator.workflows.keys())
            print(f"❌ Workflow '{workflow_id}' não encontrado.")
            print(f"📋 Workflows disponíveis: {', '.join(available)}")
            return None
        
        # Create execution context
        context = ExecutionContext(
            session_id=f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            workflow_id=workflow_id,
            user_id='cli_user',
            priority=8,
            metadata={
                'cli_execution': True,
                'user_inputs': user_inputs or {},
                'project': 'FacilIAuto'
            },
            created_at=datetime.utcnow()
        )
        
        print(f"🎭 Iniciando workflow: {workflow_id}")
        print(f"🆔 Session ID: {context.session_id}")
        
        try:
            result = await self.orchestrator.execute_workflow(
                workflow_id,
                context,
                user_inputs or {}
            )
            
            print(f"\n✅ Workflow concluído!")
            print(f"📊 Status: {result['status'].value}")
            print(f"⏱️  Duração: {(result.get('completed_at', datetime.utcnow()) - result['started_at']).total_seconds():.2f}s")
            print(f"🔧 Fases executadas: {len(result['phase_results'])}")
            
            # Show phase results
            for phase_name, phase_result in result['phase_results'].items():
                status_icon = "✅" if phase_result['status'] == 'completed' else "❌"
                print(f"  {status_icon} {phase_name}: {len(phase_result['agent_results'])} agentes")
            
            # Show audit trail
            audit_trail = self.orchestrator.get_audit_trail(context.session_id)
            print(f"\n📋 Decisões auditadas: {len(audit_trail)}")
            
            return result
            
        except Exception as e:
            print(f"❌ Erro na execução: {str(e)}")
            return None
    
    def list_workflows(self):
        """Lista workflows disponíveis"""
        print("🎭 Workflows Disponíveis:")
        print("─" * 50)
        
        for workflow_id, workflow in self.orchestrator.workflows.items():
            print(f"📋 {workflow_id}")
            print(f"   📝 {workflow.name}")
            print(f"   🎯 {workflow.description}")
            print(f"   ⏱️  {len(workflow.phases)} fases, timeout: {workflow.timeout}s")
            print()
    
    def list_agents(self):
        """Lista agentes disponíveis"""
        print("🤖 Agentes Registrados:")
        print("─" * 50)
        
        status = self.orchestrator.get_system_status()
        for agent_id, agent_info in status['agents'].items():
            metrics = agent_info['metrics']
            print(f"🔧 {agent_id}")
            print(f"   📊 Status: {agent_info['status']}")
            print(f"   📈 Requests: {metrics['total_requests']} (sucesso: {metrics['successful_requests']})")
            if metrics['total_requests'] > 0:
                success_rate = (metrics['successful_requests'] / metrics['total_requests']) * 100
                print(f"   ✅ Taxa de sucesso: {success_rate:.1f}%")
            print()
    
    def system_status(self):
        """Mostra status do sistema"""
        status = self.orchestrator.get_system_status()
        
        print("🎭 Status do Sistema Orquestrado")
        print("─" * 50)
        print(f"🔧 Status: {status['orchestrator']['status']}")
        print(f"🤖 Agentes: {status['orchestrator']['registered_agents']}")
        print(f"📋 Workflows: {status['orchestrator']['registered_workflows']}")
        print(f"🔄 Sessões ativas: {status['orchestrator']['active_sessions']}")
        print(f"💾 Uso de recursos: {status['resource_usage']}")

async def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(
        description='🎭 FacilIAuto Orchestrated CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python orchestrated_cli.py --list-workflows
  python orchestrated_cli.py --execute startup_validation
  python orchestrated_cli.py --execute product_development --input '{"budget": 500000}'
  python orchestrated_cli.py --status
        """
    )
    
    parser.add_argument('--list-workflows', action='store_true',
                       help='Lista workflows disponíveis')
    parser.add_argument('--list-agents', action='store_true',
                       help='Lista agentes registrados')
    parser.add_argument('--execute', type=str,
                       help='Executa workflow específico')
    parser.add_argument('--input', type=str,
                       help='Inputs para o workflow (JSON string)')
    parser.add_argument('--status', action='store_true',
                       help='Mostra status do sistema')
    
    args = parser.parse_args()
    
    # Initialize CLI
    print("🎭 Inicializando FacilIAuto Orchestrated CLI...")
    cli = FacilIAutoOrchestratedCLI()
    
    if args.list_workflows:
        cli.list_workflows()
    
    elif args.list_agents:
        cli.list_agents()
    
    elif args.execute:
        # Parse inputs if provided
        user_inputs = {}
        if args.input:
            try:
                import json
                user_inputs = json.loads(args.input)
            except json.JSONDecodeError:
                print("❌ Erro: Input deve ser um JSON válido")
                return
        
        # Execute workflow
        await cli.execute_workflow(args.execute, user_inputs)
    
    elif args.status:
        cli.system_status()
    
    else:
        # Interactive mode
        print("\n🎭 Modo Interativo - FacilIAuto Orchestrator")
        print("Comandos disponíveis:")
        print("  1. list-workflows - Lista workflows")
        print("  2. list-agents - Lista agentes")
        print("  3. execute <workflow_id> - Executa workflow")
        print("  4. status - Status do sistema")
        print("  5. quit - Sair")
        
        while True:
            try:
                command = input("\n🎭 > ").strip().split()
                
                if not command:
                    continue
                
                if command[0] == 'quit':
                    break
                elif command[0] == 'list-workflows':
                    cli.list_workflows()
                elif command[0] == 'list-agents':
                    cli.list_agents()
                elif command[0] == 'execute' and len(command) > 1:
                    await cli.execute_workflow(command[1])
                elif command[0] == 'status':
                    cli.system_status()
                else:
                    print("❌ Comando não reconhecido")
            
            except KeyboardInterrupt:
                print("\n👋 Saindo...")
                break
            except Exception as e:
                print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 CLI encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {str(e)}")
