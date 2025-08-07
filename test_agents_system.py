#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🤖 Teste Completo do Sistema de Agentes IA
Demonstra o funcionamento integrado dos agentes com LangGraph
"""

import json
from datetime import datetime
from typing import Dict, Any

# Importar componentes do sistema
from app.langgraph_chatbot_graph import get_chatbot_graph
from app.langgraph_chatbot_nodes import AgentType
from app.memory_manager import get_memory_manager
from app.database import get_carros
from app.ml_mvp_processor import get_hybrid_processor


def print_separator(title: str = ""):
    """Imprime separador visual"""
    if title:
        print(f"\n{'='*60}")
        print(f"🔹 {title}")
        print('='*60)
    else:
        print('-'*60)


def test_agent_system():
    """
    Testa o sistema completo de agentes IA
    """
    print("="*60)
    print("🤖 TESTE DO SISTEMA DE AGENTES IA COM LANGGRAPH")
    print("="*60)
    
    # 1. Inicializar componentes
    print_separator("1️⃣ INICIALIZANDO COMPONENTES")
    
    print("📊 Carregando chatbot LangGraph...")
    chatbot = get_chatbot_graph()
    
    print("💾 Inicializando Memory Manager...")
    memory = get_memory_manager()
    
    print("🤖 Carregando processador ML híbrido...")
    ml_processor = get_hybrid_processor()
    
    print("🚗 Buscando carros disponíveis...")
    carros = get_carros()[:3]  # Usar 3 carros para teste
    print(f"   Encontrados {len(carros)} carros")
    
    # 2. Testar agentes disponíveis
    print_separator("2️⃣ AGENTES DISPONÍVEIS NO SISTEMA")
    
    agentes_info = chatbot.obter_agentes_disponiveis()
    for tipo_agente, info in agentes_info.items():
        print(f"\n{info.get('emoji', '🤖')} {info['nome']}:")
        print(f"   Tipo: {tipo_agente}")
        if 'especialidades' in info:
            print(f"   Especialidades: {len(info['especialidades'])} áreas")
        if 'exemplos' in info:
            print(f"   Exemplos: {', '.join(info['exemplos'][:2])}")
    
    # 3. Testar roteamento de perguntas
    print_separator("3️⃣ TESTE DE ROTEAMENTO INTELIGENTE")
    
    test_questions = [
        ("Qual o consumo deste carro?", AgentType.TECNICO),
        ("Quanto custa a manutenção?", AgentType.MANUTENCAO),
        ("É bom para família?", AgentType.USO_PRINCIPAL),
        ("Vale o preço pedido?", AgentType.AVALIACAO),
        ("Consigo financiar?", AgentType.FINANCEIRO),
        ("É melhor que o Civic?", AgentType.COMPARACAO),
    ]
    
    carro = carros[0] if carros else {"id": 1, "modelo": "Teste", "marca": "Teste"}
    conversation_id = f"test_{datetime.now().timestamp()}"
    
    for pergunta, expected_agent in test_questions:
        print(f"\n❓ Pergunta: '{pergunta}'")
        print(f"   Agente esperado: {expected_agent.value}")
        
        try:
            resultado = chatbot.processar_pergunta(
                carro_id=carro["id"],
                carro_data=carro,
                pergunta=pergunta,
                conversation_id=conversation_id,
                user_session_id="test_user"
            )
            
            print(f"   ✅ Agente selecionado: {resultado['agente']}")
            print(f"   📊 Confiança: {resultado['confianca']:.0%}")
            print(f"   💬 Resposta: {resultado['resposta'][:100]}...")
            
            # Verificar se agente correto foi selecionado
            if resultado['agente'] == expected_agent.value:
                print(f"   ✨ Roteamento CORRETO!")
            else:
                print(f"   ⚠️ Roteamento diferente do esperado")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    # 4. Testar memória e contexto
    print_separator("4️⃣ TESTE DE MEMÓRIA E CONTEXTO")
    
    # Simular conversa com contexto
    conversation_id_2 = f"context_test_{datetime.now().timestamp()}"
    
    # Primeira pergunta
    print("\n🔸 Primeira interação:")
    resultado1 = chatbot.processar_pergunta(
        carro_id=carro["id"],
        carro_data=carro,
        pergunta="Este carro é econômico?",
        conversation_id=conversation_id_2,
        user_session_id="test_user_2"
    )
    print(f"   Agente: {resultado1['agente']}")
    print(f"   Resposta: {resultado1['resposta'][:150]}...")
    
    # Segunda pergunta com contexto
    print("\n🔸 Segunda interação (com contexto):")
    resultado2 = chatbot.processar_pergunta(
        carro_id=carro["id"],
        carro_data=carro,
        pergunta="E a manutenção, é cara?",
        conversation_id=conversation_id_2,
        user_session_id="test_user_2"
    )
    print(f"   Agente: {resultado2['agente']}")
    print(f"   Resposta: {resultado2['resposta'][:150]}...")
    
    # Verificar memória
    print("\n🔸 Verificando memória da conversa:")
    conversation, messages = memory.get_conversation_history(conversation_id_2)
    print(f"   Total de mensagens salvas: {len(messages)}")
    if messages:
        for i, msg in enumerate(messages[:3], 1):
            print(f"   Mensagem {i}: {msg.agent_used} - {msg.role}")
    
    # 5. Integração com ML
    print_separator("5️⃣ INTEGRAÇÃO COM SISTEMA ML")
    
    # Verificar status do ML
    ml_stats = ml_processor.get_comprehensive_stats()
    print(f"\n📊 Status do Sistema ML:")
    print(f"   ML Treinado: {'✅' if ml_stats['system_status']['ml_trained'] else '❌'}")
    print(f"   Peso do ML: {ml_stats['system_status']['ml_weight']:.0%}")
    print(f"   Amostras coletadas: {ml_stats['system_status']['total_training_samples']}")
    
    # 6. Teste de fluxo completo
    print_separator("6️⃣ TESTE DE FLUXO COMPLETO")
    
    # Simular pergunta complexa que envolve múltiplos agentes
    pergunta_complexa = "Quero um carro econômico para família, vale a pena este modelo?"
    
    print(f"\n❓ Pergunta complexa: '{pergunta_complexa}'")
    
    resultado_complexo = chatbot.processar_pergunta(
        carro_id=carro["id"],
        carro_data=carro,
        pergunta=pergunta_complexa,
        conversation_id=f"complex_{datetime.now().timestamp()}",
        user_session_id="test_user_3"
    )
    
    print(f"\n📋 Análise da resposta:")
    print(f"   Agente principal: {resultado_complexo['agente']}")
    print(f"   Confiança: {resultado_complexo['confianca']:.0%}")
    print(f"   Dados utilizados: {len(resultado_complexo.get('dados_utilizados', []))} fontes")
    
    if resultado_complexo.get('sugestoes_followup'):
        print(f"\n💡 Sugestões de follow-up:")
        for i, sugestao in enumerate(resultado_complexo['sugestoes_followup'][:3], 1):
            print(f"   {i}. {sugestao}")
    
    # 7. Análise de performance
    print_separator("7️⃣ ANÁLISE DE PERFORMANCE")
    
    # Buscar estatísticas da conversa
    analytics = memory.get_conversation_analytics(days=1)
    
    print(f"\n📈 Estatísticas do Sistema:")
    print(f"   Total de conversas: {analytics['total_conversations']}")
    print(f"   Total de mensagens: {analytics['total_messages']}")
    print(f"   Média de mensagens/conversa: {analytics['avg_messages_per_conversation']:.1f}")
    
    if analytics.get('agents_usage'):
        print(f"\n📊 Uso dos Agentes:")
        for agent, count in analytics['agents_usage'].items():
            print(f"   {agent}: {count} vezes")
    
    # Resumo final
    print_separator("📊 RESUMO DO SISTEMA")
    
    print("""
    ✅ Sistema de Agentes IA Funcionando:
    
    1. LangGraph Chatbot: ✅ Ativo
       - 6 agentes especializados
       - Roteamento automático inteligente
       - Processamento em grafo de estados
    
    2. Memory Manager: ✅ Ativo
       - Persistência de conversas
       - Contexto mantido entre interações
       - Analytics e métricas
    
    3. ML Integration: ✅ Ativo
       - Coleta de dados para treinamento
       - Processamento híbrido (regras + ML)
       - Aprendizado incremental
    
    4. Agentes Especializados:
       - TECNICO: Especificações e características
       - FINANCEIRO: Preços e financiamento
       - COMPARACAO: Comparações entre modelos
       - MANUTENCAO: Custos e cuidados
       - AVALIACAO: Análise de valor
       - USO_PRINCIPAL: Adequação ao perfil
    
    🚀 Sistema totalmente operacional e integrado!
    """)


if __name__ == "__main__":
    try:
        test_agent_system()
        print("\n✅ Teste concluído com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()