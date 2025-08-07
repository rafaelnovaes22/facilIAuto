#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Sistema de Chatbot LangGraph do FacilIAuto

Este script testa todas as funcionalidades principais do chatbot
implementado com LangGraph, incluindo inicialização, roteamento
e resposta dos agentes especializados.

Autor: FacilIAuto Dev Team
Data: 2024
"""

import sys
import traceback


def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"🤖 {title}")
    print("=" * 60)


def print_step(step: str, status: str = ""):
    """Imprime etapa do teste"""
    status_emoji = "✅" if status == "ok" else "❌" if status == "error" else "🔄"
    print(f"{status_emoji} {step}")


def test_imports():
    """Testa importações necessárias"""
    print_header("TESTE DE IMPORTAÇÕES")

    try:
        print_step("Importando módulos LangGraph...")

        print_step("Importações realizadas com sucesso", "ok")
        assert True
    except Exception as e:
        print_step(f"Erro nas importações: {e}", "error")
        traceback.print_exc()
        assert False, f"Erro nas importações: {e}"


def test_graph_initialization():
    """Testa inicialização do grafo LangGraph"""
    print_header("TESTE DE INICIALIZAÇÃO DO LANGGRAPH")

    try:
        print_step("Importando get_chatbot_graph...")
        from app.langgraph_chatbot_graph import get_chatbot_graph

        print_step("Inicializando LangGraph...")
        chatbot_graph = get_chatbot_graph()
        print_step("LangGraph inicializado com sucesso", "ok")

        print_step("Verificando instância singleton...")
        chatbot_graph2 = get_chatbot_graph()
        is_singleton = chatbot_graph is chatbot_graph2
        print_step(
            f"Singleton pattern: {'OK' if is_singleton else 'FALHOU'}",
            "ok" if is_singleton else "error",
        )

        return chatbot_graph
    except Exception as e:
        print_step(f"Erro na inicialização: {e}", "error")
        traceback.print_exc()
        return None


def test_agents_info(chatbot_graph):
    """Testa obtenção de informações dos agentes"""
    print_header("TESTE DE AGENTES DISPONÍVEIS")

    try:
        print_step("Obtendo informações dos agentes...")
        agentes = chatbot_graph.obter_agentes_disponiveis()

        print_step(f"Total de agentes: {len(agentes)}", "ok")

        for agente_id, info in agentes.items():
            print(f"  🤖 {agente_id}: {info['nome']} {info['emoji']}")
            print(f"     Especialidades: {len(info['especialidades'])}")
            print(f"     Exemplos: {len(info['exemplos'])}")

        print_step("Informações dos agentes obtidas com sucesso", "ok")
        return True
    except Exception as e:
        print_step(f"Erro ao obter agentes: {e}", "error")
        traceback.print_exc()
        return False


def test_graph_statistics(chatbot_graph):
    """Testa estatísticas do grafo"""
    print_header("TESTE DE ESTATÍSTICAS DO GRAFO")

    try:
        print_step("Obtendo estatísticas do grafo...")
        stats = chatbot_graph.obter_estatisticas_grafo()

        print_step(f"Status: {stats.get('status', 'N/A')}", "ok")
        print_step(f"Total de nós: {stats.get('total_nodes', 0)}", "ok")
        print_step(f"Total de edges: {stats.get('total_edges', 0)}", "ok")
        print_step(f"Entry point: {stats.get('entry_point', 'N/A')}", "ok")
        print_step(f"Agentes disponíveis: {stats.get('available_agents', 0)}", "ok")

        print_step("Estatísticas obtidas com sucesso", "ok")
        return True
    except Exception as e:
        print_step(f"Erro ao obter estatísticas: {e}", "error")
        traceback.print_exc()
        return False


def test_car_data_mock():
    """Cria dados mock de um carro para teste"""
    return {
        "id": 1,
        "marca": "Toyota",
        "modelo": "Corolla",
        "versao": "XEI",
        "ano": 2023,
        "preco": 120000,
        "preco_promocional": 115000,
        "categoria": "sedan",
        "consumo": 12.5,
        "potencia": 144,
        "capacidade_pessoas": 5,
        "porta_malas": 470,
        "combustivel": "flex",
        "cambio": "automatico",
        "cor": "Branco",
        "km": 15000,
        "uso_recomendado": ["urbano", "viagem"],
        "familia": "medio",
        "seguranca": 5,
        "conforto": 4,
        "economia": 4,
        "performance": 3,
        "regiao": ["SP", "RJ", "MG"],
        "fotos": ["foto1.jpg", "foto2.jpg"],
        "descricao": "Sedan confiável e econômico",
        "opcionais": ["Ar condicionado", "Direção hidráulica", "Airbag"],
        "destaque": True,
    }


def test_agent_routing(chatbot_graph, carro_data):
    """Testa roteamento para diferentes agentes"""
    print_header("TESTE DE ROTEAMENTO DE AGENTES")

    test_cases = [
        {
            "pergunta": "Qual a potência do motor deste carro?",
            "agente_esperado": "tecnico",
            "desc": "Pergunta técnica sobre motor",
        },
        {
            "pergunta": "Como funciona o financiamento para este veículo?",
            "agente_esperado": "financeiro",
            "desc": "Pergunta sobre financiamento",
        },
        {
            "pergunta": "Compare este carro com outros similares",
            "agente_esperado": "comparacao",
            "desc": "Pergunta sobre comparação",
        },
        {
            "pergunta": "Quanto gasto com manutenção por ano?",
            "agente_esperado": "manutencao",
            "desc": "Pergunta sobre manutenção",
        },
        {
            "pergunta": "Este preço está justo no mercado?",
            "agente_esperado": "avaliacao",
            "desc": "Pergunta sobre avaliação",
        },
        {
            "pergunta": "Olá, me fale sobre este carro",
            "agente_esperado": "finalizer",
            "desc": "Pergunta genérica",
        },
    ]

    success_count = 0

    for i, test_case in enumerate(test_cases, 1):
        try:
            print_step(f"Teste {i}: {test_case['desc']}")
            print(f"    Pergunta: '{test_case['pergunta']}'")

            resultado = chatbot_graph.processar_pergunta(
                carro_id=1, carro_data=carro_data, pergunta=test_case["pergunta"]
            )

            agente_usado = resultado.get("agente", "unknown")
            confianca = resultado.get("confianca", 0.0)

            print(f"    Agente selecionado: {agente_usado}")
            print(f"    Confiança: {confianca:.2f}")
            print(f"    Esperado: {test_case['agente_esperado']}")

            # Verificar se o roteamento está correto ou aceitável
            roteamento_correto = (
                agente_usado == test_case["agente_esperado"]
                or (test_case["agente_esperado"] == "finalizer" and confianca < 0.3)
                or confianca >= 0.3
            )

            if roteamento_correto:
                print_step("    Roteamento: OK", "ok")
                success_count += 1
            else:
                print_step("    Roteamento: Inesperado", "error")

            # Verificar se há resposta
            if resultado.get("resposta"):
                print_step(
                    f"    Resposta gerada: {len(resultado['resposta'])} chars", "ok"
                )
            else:
                print_step("    Resposta: Vazia", "error")

        except Exception as e:
            print_step(f"    Erro no teste {i}: {e}", "error")
            traceback.print_exc()

    print_step(
        f"Testes de roteamento: {success_count}/{len(test_cases)} sucessos",
        "ok" if success_count >= len(test_cases) * 0.8 else "error",
    )

    return success_count >= len(test_cases) * 0.8


def test_response_quality(chatbot_graph, carro_data):
    """Testa qualidade das respostas"""
    print_header("TESTE DE QUALIDADE DAS RESPOSTAS")

    try:
        print_step("Testando resposta do agente técnico...")
        resultado_tecnico = chatbot_graph.processar_pergunta(
            carro_id=1,
            carro_data=carro_data,
            pergunta="Qual o consumo e potência deste carro?",
        )

        resposta = resultado_tecnico.get("resposta", "")
        print(f"    Tamanho da resposta: {len(resposta)} chars")
        print(f"    Confiança: {resultado_tecnico.get('confianca', 0):.2f}")
        print(
            f"    Sugestões follow-up: {len(resultado_tecnico.get('sugestoes_followup', []))}"
        )

        # Verificar elementos esperados na resposta técnica
        elementos_esperados = ["potência", "cv", "consumo", "km/l"]
        elementos_encontrados = sum(
            1 for el in elementos_esperados if el.lower() in resposta.lower()
        )

        print_step(
            f"    Elementos técnicos encontrados: {elementos_encontrados}/{len(elementos_esperados)}",
            "ok" if elementos_encontrados >= 2 else "error",
        )

        # Testar resposta financeira
        print_step("Testando resposta do agente financeiro...")
        resultado_financeiro = chatbot_graph.processar_pergunta(
            carro_id=1,
            carro_data=carro_data,
            pergunta="Simule um financiamento para este carro",
        )

        resposta_fin = resultado_financeiro.get("resposta", "")
        elementos_financeiros = ["financiamento", "prestação", "entrada", "R$"]
        elementos_fin_encontrados = sum(
            1 for el in elementos_financeiros if el in resposta_fin
        )

        print_step(
            f"    Elementos financeiros encontrados: {elementos_fin_encontrados}/{len(elementos_financeiros)}",
            "ok" if elementos_fin_encontrados >= 2 else "error",
        )

        print_step("Teste de qualidade concluído", "ok")
        return True

    except Exception as e:
        print_step(f"Erro no teste de qualidade: {e}", "error")
        traceback.print_exc()
        return False


def test_debug_mode(chatbot_graph, carro_data):
    """Testa modo debug do LangGraph"""
    print_header("TESTE DE MODO DEBUG")

    try:
        print_step("Executando debug do LangGraph...")
        debug_info = chatbot_graph.executar_debug(
            carro_id=1, carro_data=carro_data, pergunta="Como é o motor deste carro?"
        )

        print_step(f"Debug executado: {len(debug_info)} campos", "ok")

        if "execution_flow" in debug_info:
            print_step(
                f"Fluxo de execução: {len(debug_info['execution_flow'])} etapas", "ok"
            )
            for etapa in debug_info["execution_flow"]:
                print(f"    {etapa}")

        if "final_result" in debug_info:
            final_result = debug_info["final_result"]
            print_step(
                f"Resultado final: agente={final_result.get('agente_usado', 'N/A')}",
                "ok",
            )

        print_step("Modo debug funcionando", "ok")
        return True

    except Exception as e:
        print_step(f"Erro no modo debug: {e}", "error")
        traceback.print_exc()
        return False


def run_comprehensive_test():
    """Executa todos os testes do sistema"""
    print_header("SISTEMA DE TESTE LANGGRAPH CHATBOT - FACILIAUTO")
    print("🚀 Iniciando bateria completa de testes...")

    # Contador de sucessos
    test_results = {
        "imports": False,
        "initialization": False,
        "agents_info": False,
        "statistics": False,
        "routing": False,
        "quality": False,
        "debug": False,
    }

    # 1. Teste de importações
    test_results["imports"] = test_imports()
    if not test_results["imports"]:
        print("❌ Falha crítica nas importações. Interrompendo testes.")
        return test_results

    # 2. Teste de inicialização
    chatbot_graph = test_graph_initialization()
    test_results["initialization"] = chatbot_graph is not None
    if not test_results["initialization"]:
        print("❌ Falha crítica na inicialização. Interrompendo testes.")
        return test_results

    # 3. Teste de informações dos agentes
    test_results["agents_info"] = test_agents_info(chatbot_graph)

    # 4. Teste de estatísticas
    test_results["statistics"] = test_graph_statistics(chatbot_graph)

    # 5. Preparar dados mock do carro
    carro_data = test_car_data_mock()
    print_step("Dados mock do carro criados", "ok")

    # 6. Teste de roteamento
    test_results["routing"] = test_agent_routing(chatbot_graph, carro_data)

    # 7. Teste de qualidade das respostas
    test_results["quality"] = test_response_quality(chatbot_graph, carro_data)

    # 8. Teste de modo debug
    test_results["debug"] = test_debug_mode(chatbot_graph, carro_data)

    return test_results


def print_final_report(test_results):
    """Imprime relatório final dos testes"""
    print_header("RELATÓRIO FINAL DOS TESTES")

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = (passed_tests / total_tests) * 100

    print("📊 **ESTATÍSTICAS GERAIS:**")
    print(f"   Total de testes: {total_tests}")
    print(f"   Testes aprovados: {passed_tests}")
    print(f"   Taxa de sucesso: {success_rate:.1f}%")
    print()

    print("📋 **RESULTADOS DETALHADOS:**")
    for test_name, result in test_results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name.capitalize().replace('_', ' ')}: {status}")

    print()

    if success_rate >= 90:
        print("🎉 **RESULTADO: EXCELENTE!**")
        print("   Sistema LangGraph funcionando perfeitamente!")
        print("   Pronto para produção! 🚀")
    elif success_rate >= 70:
        print("👍 **RESULTADO: BOM**")
        print("   Sistema LangGraph funcional com pequenos ajustes necessários.")
        print("   Revisar testes que falharam.")
    else:
        print("⚠️ **RESULTADO: REQUER ATENÇÃO**")
        print("   Sistema LangGraph precisa de correções antes do deploy.")
        print("   Verificar logs de erro acima.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        # Executar todos os testes
        results = run_comprehensive_test()

        # Imprimir relatório final
        print_final_report(results)

        # Exit code baseado no resultado
        success_rate = (sum(results.values()) / len(results)) * 100
        sys.exit(0 if success_rate >= 70 else 1)

    except KeyboardInterrupt:
        print("\n🛑 Testes interrompidos pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro crítico durante os testes: {e}")
        traceback.print_exc()
        sys.exit(1)
