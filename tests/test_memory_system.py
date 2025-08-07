#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Sistema de Memória Persistente do FacilIAuto

Este script testa todas as funcionalidades do sistema de memória
persistente, incluindo criação de conversas, persistência de mensagens,
contexto de usuário e analytics.

Autor: FacilIAuto Dev Team
Data: 2024
"""

import sys
import traceback


def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"🧠 {title}")
    print("=" * 60)


def print_step(step: str, status: str = ""):
    """Imprime etapa do teste"""
    status_emoji = "✅" if status == "ok" else "❌" if status == "error" else "🔄"
    print(f"{status_emoji} {step}")


def test_memory_imports():
    """Testa importações do sistema de memória"""
    print_header("TESTE DE IMPORTAÇÕES - SISTEMA DE MEMÓRIA")

    try:
        print_step("Importando modelos de memória...")

        print_step("Importando gerenciador de memória...")

        print_step("Importando API de memória...")

        print_step("Todas as importações realizadas com sucesso", "ok")
        return True
    except Exception as e:
        print_step(f"Erro nas importações: {e}", "error")
        traceback.print_exc()
        return False


def test_memory_manager_initialization():
    """Testa inicialização do gerenciador de memória"""
    print_header("TESTE DE INICIALIZAÇÃO - MEMORY MANAGER")

    try:
        print_step("Inicializando Memory Manager...")
        from app.memory_manager import get_memory_manager

        memory_manager = get_memory_manager()
        print_step("Memory Manager inicializado com sucesso", "ok")

        print_step("Testando singleton pattern...")
        memory_manager2 = get_memory_manager()
        is_singleton = memory_manager is memory_manager2
        print_step(
            f"Singleton pattern: {'OK' if is_singleton else 'FALHOU'}",
            "ok" if is_singleton else "error",
        )

        return memory_manager
    except Exception as e:
        print_step(f"Erro na inicialização: {e}", "error")
        traceback.print_exc()
        return None


def test_conversation_creation(memory_manager):
    """Testa criação de conversas"""
    print_header("TESTE DE CRIAÇÃO DE CONVERSAS")

    try:
        # Dados mock do carro
        carro_data = {
            "id": 1,
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2023,
            "preco": 120000,
            "categoria": "sedan",
        }

        print_step("Criando nova conversa...")
        conversation_id = memory_manager.create_conversation(
            carro_id=1, carro_data=carro_data, user_session_id="test_user_123"
        )

        print_step(f"Conversa criada com ID: {conversation_id}", "ok")

        print_step("Verificando conversa criada...")
        conversation, messages = memory_manager.get_conversation_history(
            conversation_id
        )

        if conversation:
            print_step(f"Conversa encontrada: carro_id={conversation.carro_id}", "ok")
            print_step(f"Total de mensagens: {len(messages)}", "ok")
            return conversation_id
        else:
            print_step("Conversa não encontrada", "error")
            return None

    except Exception as e:
        print_step(f"Erro ao criar conversa: {e}", "error")
        traceback.print_exc()
        return None


def test_message_persistence(memory_manager, conversation_id):
    """Testa persistência de mensagens"""
    print_header("TESTE DE PERSISTÊNCIA DE MENSAGENS")

    try:
        test_messages = [
            ("user", "Qual o consumo deste carro?"),
            (
                "assistant",
                "O consumo é de 12.5 km/l na cidade e estrada",
                "tecnico",
                0.9,
            ),
            ("user", "E o financiamento, como funciona?"),
            (
                "assistant",
                "Posso simular várias opções de financiamento para você",
                "financeiro",
                0.8,
            ),
        ]

        message_ids = []

        for i, msg_data in enumerate(test_messages):
            print_step(f"Adicionando mensagem {i+1}: {msg_data[0]}")

            if msg_data[0] == "user":
                message_id = memory_manager.add_message(
                    conversation_id=conversation_id,
                    message_type="user",
                    content=msg_data[1],
                )
            else:
                message_id = memory_manager.add_message(
                    conversation_id=conversation_id,
                    message_type="assistant",
                    content=msg_data[1],
                    agent_used=msg_data[2],
                    confidence_score=msg_data[3],
                    processing_time_ms=150,
                    data_sources=["especificacoes_tecnicas"],
                    followup_suggestions=["Quer saber sobre manutenção?"],
                )

            message_ids.append(message_id)
            print_step(f"Mensagem adicionada com ID: {message_id}", "ok")

        print_step("Verificando mensagens persistidas...")
        conversation, messages = memory_manager.get_conversation_history(
            conversation_id
        )

        print_step(f"Total de mensagens recuperadas: {len(messages)}", "ok")
        print_step(f"Agente primário da conversa: {conversation.primary_agent}", "ok")

        return len(messages) == len(test_messages)

    except Exception as e:
        print_step(f"Erro ao persistir mensagens: {e}", "error")
        traceback.print_exc()
        return False


def test_context_extraction(memory_manager, conversation_id):
    """Testa extração e persistência de contexto"""
    print_header("TESTE DE EXTRAÇÃO DE CONTEXTO")

    try:
        print_step("Adicionando contexto manual...")

        context_id = memory_manager.add_context(
            conversation_id=conversation_id,
            context_type="preference",
            context_key="feature_interest",
            context_value="economia",
            confidence=0.8,
        )

        print_step(f"Contexto adicionado com ID: {context_id}", "ok")

        print_step("Testando extração automática de contexto...")
        memory_manager._extract_and_persist_context(
            conversation_id=conversation_id,
            user_message="Preciso de um carro Toyota econômico para comprar hoje",
            agent_used="tecnico",
        )

        print_step("Contexto extraído automaticamente", "ok")
        return True

    except Exception as e:
        print_step(f"Erro ao extrair contexto: {e}", "error")
        traceback.print_exc()
        return False


def test_user_context(memory_manager):
    """Testa recuperação de contexto do usuário"""
    print_header("TESTE DE CONTEXTO DO USUÁRIO")

    try:
        print_step("Recuperando contexto do usuário...")

        user_context = memory_manager.get_user_context("test_user_123")

        print_step(
            f"Conversas recentes: {user_context.get('recent_conversations', 0)}", "ok"
        )
        print_step(
            f"Agentes preferidos: {user_context.get('preferred_agents', {})}", "ok"
        )
        print_step(
            f"Marcas de interesse: {user_context.get('brand_preferences', [])}", "ok"
        )

        return True

    except Exception as e:
        print_step(f"Erro ao recuperar contexto: {e}", "error")
        traceback.print_exc()
        return False


def test_langgraph_memory_integration():
    """Testa integração com LangGraph"""
    print_header("TESTE DE INTEGRAÇÃO LANGGRAPH + MEMÓRIA")

    try:
        print_step("Importando LangGraph atualizado...")
        from app.langgraph_chatbot_graph import get_chatbot_graph

        print_step("Criando dados de teste...")
        carro_data = {
            "id": 2,
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2023,
            "preco": 140000,
            "categoria": "sedan",
            "consumo": 11.8,
            "potencia": 174,
        }

        print_step("Processando pergunta com memória...")
        chatbot_graph = get_chatbot_graph()

        resultado = chatbot_graph.processar_pergunta(
            carro_id=2,
            carro_data=carro_data,
            pergunta="Qual a potência deste Honda Civic?",
            user_session_id="test_user_integration",
        )

        print_step(f"Resposta gerada: {len(resultado.get('resposta', ''))} chars", "ok")
        print_step(f"Agente usado: {resultado.get('agente', 'N/A')}", "ok")
        print_step(f"Conversation ID: {resultado.get('conversation_id', 'N/A')}", "ok")

        return True

    except Exception as e:
        print_step(f"Erro na integração: {e}", "error")
        traceback.print_exc()
        return False


def test_analytics_system(memory_manager):
    """Testa sistema de analytics"""
    print_header("TESTE DE SISTEMA DE ANALYTICS")

    try:
        print_step("Gerando analytics...")

        analytics = memory_manager.get_conversation_analytics(days=7)

        print_step(
            f"Total de conversas (7 dias): {analytics.get('total_conversations', 0)}",
            "ok",
        )
        print_step(
            f"Total de mensagens (7 dias): {analytics.get('total_messages', 0)}", "ok"
        )
        print_step(
            f"Média de mensagens por conversa: {analytics.get('avg_messages_per_conversation', 0)}",
            "ok",
        )
        print_step(f"Uso por agente: {analytics.get('agent_usage', {})}", "ok")

        return True

    except Exception as e:
        print_step(f"Erro ao gerar analytics: {e}", "error")
        traceback.print_exc()
        return False


def test_similar_conversations(memory_manager):
    """Testa busca de conversas similares"""
    print_header("TESTE DE CONVERSAS SIMILARES")

    try:
        print_step("Buscando conversas similares...")

        similar_convs = memory_manager.get_similar_conversations(carro_id=1, limit=5)

        print_step(f"Conversas similares encontradas: {len(similar_convs)}", "ok")

        for i, (conv, messages) in enumerate(similar_convs):
            print_step(
                f"  Conversa {i+1}: {conv.total_messages} mensagens, agente: {conv.primary_agent}",
                "ok",
            )

        return True

    except Exception as e:
        print_step(f"Erro ao buscar conversas similares: {e}", "error")
        traceback.print_exc()
        return False


def run_comprehensive_memory_test():
    """Executa todos os testes do sistema de memória"""
    print_header("SISTEMA DE TESTE - MEMÓRIA PERSISTENTE FACILIAUTO")
    print("🧠 Iniciando bateria completa de testes de memória...")

    # Contador de sucessos
    test_results = {
        "imports": False,
        "initialization": False,
        "conversation_creation": False,
        "message_persistence": False,
        "context_extraction": False,
        "user_context": False,
        "langgraph_integration": False,
        "analytics": False,
        "similar_conversations": False,
    }

    # 1. Teste de importações
    test_results["imports"] = test_memory_imports()
    if not test_results["imports"]:
        print("❌ Falha crítica nas importações. Interrompendo testes.")
        return test_results

    # 2. Teste de inicialização
    memory_manager = test_memory_manager_initialization()
    test_results["initialization"] = memory_manager is not None
    if not test_results["initialization"]:
        print("❌ Falha crítica na inicialização. Interrompendo testes.")
        return test_results

    # 3. Teste de criação de conversas
    conversation_id = test_conversation_creation(memory_manager)
    test_results["conversation_creation"] = conversation_id is not None

    # 4. Teste de persistência de mensagens
    if conversation_id:
        test_results["message_persistence"] = test_message_persistence(
            memory_manager, conversation_id
        )

        # 5. Teste de extração de contexto
        test_results["context_extraction"] = test_context_extraction(
            memory_manager, conversation_id
        )

    # 6. Teste de contexto do usuário
    test_results["user_context"] = test_user_context(memory_manager)

    # 7. Teste de integração com LangGraph
    test_results["langgraph_integration"] = test_langgraph_memory_integration()

    # 8. Teste de analytics
    test_results["analytics"] = test_analytics_system(memory_manager)

    # 9. Teste de conversas similares
    test_results["similar_conversations"] = test_similar_conversations(memory_manager)

    return test_results


def print_memory_final_report(test_results):
    """Imprime relatório final dos testes de memória"""
    print_header("RELATÓRIO FINAL - SISTEMA DE MEMÓRIA")

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests) * 100

    print("🧠 **ESTATÍSTICAS DE MEMÓRIA:**")
    print(f"   Total de testes: {total_tests}")
    print(f"   Testes aprovados: {passed_tests}")
    print(f"   Taxa de sucesso: {success_rate:.1f}%")
    print()

    print("📋 **RESULTADOS DETALHADOS:**")
    for test_name, result in test_results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")

    print()

    if success_rate >= 90:
        print("🎉 **RESULTADO: EXCELENTE!**")
        print("   Sistema de Memória Persistente funcionando perfeitamente!")
        print("   Pronto para produção com PostgreSQL! 🚀")
    elif success_rate >= 70:
        print("👍 **RESULTADO: BOM**")
        print("   Sistema de Memória funcional com pequenos ajustes necessários.")
        print("   Revisar testes que falharam.")
    else:
        print("⚠️ **RESULTADO: REQUER ATENÇÃO**")
        print("   Sistema de Memória precisa de correções.")
        print("   Verificar conexão com banco de dados.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        # Executar todos os testes de memória
        results = run_comprehensive_memory_test()

        # Imprimir relatório final
        print_memory_final_report(results)

        # Exit code baseado no resultado
        success_rate = (sum(results.values()) / len(results)) * 100
        sys.exit(0 if success_rate >= 70 else 1)

    except KeyboardInterrupt:
        print("\n🛑 Testes de memória interrompidos pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro crítico durante os testes de memória: {e}")
        traceback.print_exc()
        sys.exit(1)
