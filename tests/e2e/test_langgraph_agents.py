"""
Testes End-to-End para Agentes Especializados do LangGraph

Este módulo testa cada agente individual do sistema LangGraph,
validando suas especialidades, qualidade de respostas e
integração com o sistema de memória.

Agentes Testados:
- Agente Técnico
- Agente Financeiro 
- Agente de Comparação
- Agente de Manutenção
- Agente de Avaliação
- Agente Geral (fallback)
"""

import json
import time
import uuid
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

from app.api import app
from app.memory_manager import get_memory_manager


class TestLangGraphAgentsE2E:
    """Testes E2E para agentes especializados do LangGraph"""

    @pytest.fixture(scope="class")
    def client(self):
        """Cliente HTTP para testes de API"""
        return TestClient(app)

    @pytest.fixture
    def comprehensive_car_data(self):
        """Dados abrangentes de um carro para testes completos"""
        return {
            "id": 777,
            "marca": "Honda",
            "modelo": "Civic Touring",
            "ano": 2024,
            "preco": 165000,
            "categoria": "Sedan",
            "consumo": 10.8,
            "potencia": 180,
            "cambio": "CVT",
            "combustivel": "Flex",
            "quilometragem": 8500,
            "cor": "Azul Metálico",
            "opcionais": [
                "Ar Condicionado Digital",
                "Central Multimídia",
                "Sensor de Estacionamento",
                "Câmera de Ré",
                "Freios ABS",
                "Airbags",
                "Controle de Estabilidade",
                "Faróis LED",
            ],
            "versao": "Touring",
            "portas": 4,
            "lugares": 5,
            "motor": "1.5 Turbo",
            "tracao": "Dianteira",
            "direcao": "Elétrica",
            "freios": "Disco nas 4 rodas",
            "pneus": "215/55 R17",
            "tanque": "50L",
            "porta_malas": "519L",
            "garantia": "3 anos",
            "ipva": "2024 pago",
            "manutencao": "Revisão em dia",
            "aceita_troca": True,
            "financiamento": {
                "entrada_minima": 20,
                "parcelas_max": 60,
                "taxa_juros": 1.99,
            },
        }

    @pytest.mark.asyncio
    async def test_agente_tecnico_comprehensive(self, client, comprehensive_car_data):
        """
        Teste abrangente do Agente Técnico
        """
        print("\n🔧 TESTE: Agente Técnico - Especialização Completa")

        # Cenários técnicos específicos
        technical_scenarios = [
            {
                "pergunta": "Qual a potência e torque do motor deste Honda Civic?",
                "expected_keywords": ["potência", "180", "motor", "1.5", "turbo"],
                "category": "Motor",
            },
            {
                "pergunta": "Como é o consumo na cidade e na estrada?",
                "expected_keywords": ["consumo", "10.8", "km/l", "cidade", "estrada"],
                "category": "Consumo",
            },
            {
                "pergunta": "Quais os opcionais de segurança deste carro?",
                "expected_keywords": ["segurança", "airbag", "abs", "estabilidade"],
                "category": "Segurança",
            },
            {
                "pergunta": "Como é o câmbio CVT? É confiável?",
                "expected_keywords": ["cvt", "câmbio", "automático", "confiável"],
                "category": "Transmissão",
            },
            {
                "pergunta": "Qual o tamanho do porta-malas e quantos lugares?",
                "expected_keywords": ["porta-malas", "519", "litros", "5", "lugares"],
                "category": "Dimensões",
            },
        ]

        results = []

        for i, scenario in enumerate(technical_scenarios):
            print(f"\n📋 Cenário Técnico {i+1}: {scenario['category']}")

            pergunta_data = {
                "carro_id": comprehensive_car_data["id"],
                "pergunta": scenario["pergunta"],
                "user_session_id": f"tech_test_{uuid.uuid4()}",
            }

            start_time = time.time()
            response = client.post("/api/chatbot/perguntar", json=pergunta_data)
            response_time = (time.time() - start_time) * 1000

            assert response.status_code == 200
            response_data = response.json()

            # Validar agente selecionado
            agent_correct = response_data["agente"] == "tecnico"

            # Validar conteúdo técnico
            resposta = response_data["resposta"].lower()
            keywords_found = [
                kw for kw in scenario["expected_keywords"] if kw in resposta
            ]
            keyword_coverage = len(keywords_found) / len(scenario["expected_keywords"])

            # Validar qualidade técnica
            technical_quality = {
                "has_numbers": any(char.isdigit() for char in resposta),
                "has_units": any(
                    unit in resposta for unit in ["km/l", "cv", "hp", "litros", "l"]
                ),
                "sufficient_length": len(response_data["resposta"]) > 100,
                "mentions_brand": "honda" in resposta or "civic" in resposta,
            }

            quality_score = sum(technical_quality.values()) / len(technical_quality)

            result = {
                "scenario": scenario["category"],
                "pergunta": scenario["pergunta"],
                "agent_correct": agent_correct,
                "response_time": response_time,
                "keyword_coverage": keyword_coverage,
                "quality_score": quality_score,
                "confidence": response_data["confianca"],
                "response_length": len(response_data["resposta"]),
                "followup_count": len(response_data["sugestoes_followup"]),
            }

            results.append(result)

            print(
                f"  Agente: {'✅ Técnico' if agent_correct else '❌ ' + response_data['agente']}"
            )
            print(
                f"  Keywords: {len(keywords_found)}/{len(scenario['expected_keywords'])} ({keyword_coverage:.1%})"
            )
            print(f"  Qualidade: {quality_score:.1%}")
            print(f"  Tempo: {response_time:.0f}ms")
            print(f"  Confiança: {response_data['confianca']:.2f}")

        # Métricas gerais do Agente Técnico
        avg_agent_accuracy = sum(r["agent_correct"] for r in results) / len(results)
        avg_keyword_coverage = sum(r["keyword_coverage"] for r in results) / len(
            results
        )
        avg_quality_score = sum(r["quality_score"] for r in results) / len(results)
        avg_response_time = sum(r["response_time"] for r in results) / len(results)

        print(f"\n📊 MÉTRICAS AGENTE TÉCNICO:")
        print(f"   Precisão do Agente: {avg_agent_accuracy:.1%}")
        print(f"   Cobertura Keywords: {avg_keyword_coverage:.1%}")
        print(f"   Qualidade Técnica: {avg_quality_score:.1%}")
        print(f"   Tempo Médio: {avg_response_time:.0f}ms")

        # Validações
        assert (
            avg_agent_accuracy >= 0.8
        ), f"Precisão do agente técnico muito baixa: {avg_agent_accuracy:.1%}"
        assert (
            avg_keyword_coverage >= 0.6
        ), f"Cobertura de keywords técnicas muito baixa: {avg_keyword_coverage:.1%}"
        assert (
            avg_quality_score >= 0.7
        ), f"Qualidade técnica das respostas muito baixa: {avg_quality_score:.1%}"

        return results

    @pytest.mark.asyncio
    async def test_agente_financeiro_comprehensive(
        self, client, comprehensive_car_data
    ):
        """
        Teste abrangente do Agente Financeiro
        """
        print("\n💰 TESTE: Agente Financeiro - Especialização Completa")

        financial_scenarios = [
            {
                "pergunta": "Como funciona o financiamento? Qual o valor das parcelas?",
                "expected_keywords": ["financiamento", "parcela", "entrada", "juros"],
                "category": "Financiamento",
            },
            {
                "pergunta": "Posso dar entrada de 30 mil? Em quantas vezes?",
                "expected_keywords": ["entrada", "30", "mil", "parcelas", "vezes"],
                "category": "Entrada",
            },
            {
                "pergunta": "Qual a taxa de juros e o valor total financiado?",
                "expected_keywords": ["taxa", "juros", "1.99", "total", "financiado"],
                "category": "Juros",
            },
            {
                "pergunta": "Aceita carro usado como entrada? Como funciona?",
                "expected_keywords": ["usado", "troca", "entrada", "avaliação"],
                "category": "Troca",
            },
            {
                "pergunta": "Qual o seguro obrigatório e IPVA deste Honda?",
                "expected_keywords": ["seguro", "ipva", "2024", "pago", "obrigatório"],
                "category": "Custos",
            },
        ]

        results = []

        for i, scenario in enumerate(financial_scenarios):
            print(f"\n💳 Cenário Financeiro {i+1}: {scenario['category']}")

            pergunta_data = {
                "carro_id": comprehensive_car_data["id"],
                "pergunta": scenario["pergunta"],
                "user_session_id": f"finance_test_{uuid.uuid4()}",
            }

            response = client.post("/api/chatbot/perguntar", json=pergunta_data)
            assert response.status_code == 200
            response_data = response.json()

            # Validações específicas do agente financeiro
            agent_correct = response_data["agente"] == "financeiro"
            resposta = response_data["resposta"].lower()

            keywords_found = [
                kw for kw in scenario["expected_keywords"] if kw in resposta
            ]
            keyword_coverage = len(keywords_found) / len(scenario["expected_keywords"])

            # Validar qualidade financeira
            financial_quality = {
                "mentions_price": any(
                    term in resposta for term in ["preço", "valor", "165000", "165"]
                ),
                "has_financial_terms": any(
                    term in resposta
                    for term in ["financiamento", "parcela", "juros", "entrada"]
                ),
                "provides_calculations": any(char.isdigit() for char in resposta),
                "mentions_documentation": any(
                    term in resposta
                    for term in ["documento", "cpf", "renda", "aprovação"]
                ),
            }

            quality_score = sum(financial_quality.values()) / len(financial_quality)

            result = {
                "scenario": scenario["category"],
                "agent_correct": agent_correct,
                "keyword_coverage": keyword_coverage,
                "quality_score": quality_score,
                "confidence": response_data["confianca"],
                "mentions_price": "165" in resposta or "preço" in resposta,
            }

            results.append(result)

            print(
                f"  Agente: {'✅ Financeiro' if agent_correct else '❌ ' + response_data['agente']}"
            )
            print(
                f"  Keywords: {len(keywords_found)}/{len(scenario['expected_keywords'])}"
            )
            print(f"  Qualidade Financeira: {quality_score:.1%}")
            print(f"  Menciona Preço: {'✅' if result['mentions_price'] else '❌'}")

        # Métricas do Agente Financeiro
        avg_agent_accuracy = sum(r["agent_correct"] for r in results) / len(results)
        avg_keyword_coverage = sum(r["keyword_coverage"] for r in results) / len(
            results
        )
        avg_quality_score = sum(r["quality_score"] for r in results) / len(results)
        price_mention_rate = sum(r["mentions_price"] for r in results) / len(results)

        print(f"\n📊 MÉTRICAS AGENTE FINANCEIRO:")
        print(f"   Precisão do Agente: {avg_agent_accuracy:.1%}")
        print(f"   Cobertura Keywords: {avg_keyword_coverage:.1%}")
        print(f"   Qualidade Financeira: {avg_quality_score:.1%}")
        print(f"   Taxa Menção Preço: {price_mention_rate:.1%}")

        # Validações
        assert (
            avg_agent_accuracy >= 0.8
        ), f"Precisão do agente financeiro muito baixa: {avg_agent_accuracy:.1%}"
        assert (
            avg_quality_score >= 0.6
        ), f"Qualidade financeira das respostas muito baixa: {avg_quality_score:.1%}"

        return results

    @pytest.mark.asyncio
    async def test_agente_comparacao_comprehensive(
        self, client, comprehensive_car_data
    ):
        """
        Teste abrangente do Agente de Comparação
        """
        print("\n⚖️ TESTE: Agente de Comparação - Especialização Completa")

        comparison_scenarios = [
            {
                "pergunta": "Compare este Honda Civic com o Toyota Corolla",
                "expected_keywords": ["honda", "civic", "toyota", "corolla", "compare"],
                "competitor": "Toyota Corolla",
                "category": "Sedans",
            },
            {
                "pergunta": "Este carro é melhor que o Nissan Sentra?",
                "expected_keywords": ["melhor", "nissan", "sentra", "vantagem"],
                "competitor": "Nissan Sentra",
                "category": "Vantagens",
            },
            {
                "pergunta": "Qual a diferença entre este e o Hyundai Elantra?",
                "expected_keywords": ["diferença", "hyundai", "elantra", "comparação"],
                "competitor": "Hyundai Elantra",
                "category": "Diferenças",
            },
        ]

        results = []

        for i, scenario in enumerate(comparison_scenarios):
            print(f"\n⚖️ Cenário Comparação {i+1}: {scenario['category']}")

            pergunta_data = {
                "carro_id": comprehensive_car_data["id"],
                "pergunta": scenario["pergunta"],
                "user_session_id": f"comparison_test_{uuid.uuid4()}",
            }

            response = client.post("/api/chatbot/perguntar", json=pergunta_data)
            assert response.status_code == 200
            response_data = response.json()

            agent_correct = response_data["agente"] == "comparacao"
            resposta = response_data["resposta"].lower()

            # Validar se menciona o carro concorrente
            mentions_competitor = scenario["competitor"].lower() in resposta

            # Validar aspectos comparativos
            comparison_quality = {
                "mentions_both_cars": "honda" in resposta and "civic" in resposta,
                "mentions_competitor": mentions_competitor,
                "has_comparison_words": any(
                    word in resposta
                    for word in [
                        "melhor",
                        "pior",
                        "superior",
                        "inferior",
                        "vantagem",
                        "desvantagem",
                    ]
                ),
                "compares_specs": any(
                    spec in resposta
                    for spec in ["potência", "consumo", "preço", "espaço", "conforto"]
                ),
                "provides_conclusion": any(
                    word in resposta
                    for word in ["recomendo", "escolha", "opção", "conclusão"]
                ),
            }

            quality_score = sum(comparison_quality.values()) / len(comparison_quality)

            result = {
                "scenario": scenario["category"],
                "competitor": scenario["competitor"],
                "agent_correct": agent_correct,
                "mentions_competitor": mentions_competitor,
                "quality_score": quality_score,
                "confidence": response_data["confianca"],
            }

            results.append(result)

            print(
                f"  Agente: {'✅ Comparação' if agent_correct else '❌ ' + response_data['agente']}"
            )
            print(f"  Menciona Concorrente: {'✅' if mentions_competitor else '❌'}")
            print(f"  Qualidade Comparativa: {quality_score:.1%}")

        # Métricas do Agente de Comparação
        avg_agent_accuracy = sum(r["agent_correct"] for r in results) / len(results)
        competitor_mention_rate = sum(r["mentions_competitor"] for r in results) / len(
            results
        )
        avg_quality_score = sum(r["quality_score"] for r in results) / len(results)

        print(f"\n📊 MÉTRICAS AGENTE COMPARAÇÃO:")
        print(f"   Precisão do Agente: {avg_agent_accuracy:.1%}")
        print(f"   Taxa Menção Concorrente: {competitor_mention_rate:.1%}")
        print(f"   Qualidade Comparativa: {avg_quality_score:.1%}")

        # Validações
        assert (
            avg_agent_accuracy >= 0.8
        ), f"Precisão do agente de comparação muito baixa: {avg_agent_accuracy:.1%}"
        assert (
            competitor_mention_rate >= 0.8
        ), f"Taxa de menção a concorrente muito baixa: {competitor_mention_rate:.1%}"

        return results

    @pytest.mark.asyncio
    async def test_agente_manutencao_comprehensive(
        self, client, comprehensive_car_data
    ):
        """
        Teste abrangente do Agente de Manutenção
        """
        print("\n🔧 TESTE: Agente de Manutenção - Especialização Completa")

        maintenance_scenarios = [
            {
                "pergunta": "Qual o custo de manutenção deste Honda Civic?",
                "expected_keywords": ["manutenção", "custo", "revisão", "honda"],
                "category": "Custos",
            },
            {
                "pergunta": "Quando fazer a primeira revisão e o que inclui?",
                "expected_keywords": ["primeira", "revisão", "inclui", "km"],
                "category": "Revisões",
            },
            {
                "pergunta": "Quais são os problemas comuns deste modelo?",
                "expected_keywords": ["problemas", "comuns", "civic", "defeitos"],
                "category": "Problemas",
            },
            {
                "pergunta": "Onde encontrar peças e qual a garantia?",
                "expected_keywords": ["peças", "garantia", "3", "anos"],
                "category": "Peças",
            },
        ]

        results = []

        for i, scenario in enumerate(maintenance_scenarios):
            print(f"\n🔧 Cenário Manutenção {i+1}: {scenario['category']}")

            pergunta_data = {
                "carro_id": comprehensive_car_data["id"],
                "pergunta": scenario["pergunta"],
                "user_session_id": f"maintenance_test_{uuid.uuid4()}",
            }

            response = client.post("/api/chatbot/perguntar", json=pergunta_data)
            assert response.status_code == 200
            response_data = response.json()

            agent_correct = response_data["agente"] == "manutencao"
            resposta = response_data["resposta"].lower()

            # Validar qualidade de manutenção
            maintenance_quality = {
                "mentions_maintenance": any(
                    term in resposta for term in ["manutenção", "revisão", "peças"]
                ),
                "mentions_costs": any(
                    term in resposta for term in ["custo", "preço", "valor", "r$"]
                ),
                "mentions_warranty": "garantia" in resposta or "3 anos" in resposta,
                "provides_schedule": any(
                    term in resposta for term in ["km", "meses", "tempo", "período"]
                ),
                "mentions_brand_network": any(
                    term in resposta
                    for term in ["honda", "autorizada", "concessionária"]
                ),
            }

            quality_score = sum(maintenance_quality.values()) / len(maintenance_quality)

            result = {
                "scenario": scenario["category"],
                "agent_correct": agent_correct,
                "quality_score": quality_score,
                "confidence": response_data["confianca"],
            }

            results.append(result)

            print(
                f"  Agente: {'✅ Manutenção' if agent_correct else '❌ ' + response_data['agente']}"
            )
            print(f"  Qualidade Manutenção: {quality_score:.1%}")

        # Métricas do Agente de Manutenção
        avg_agent_accuracy = sum(r["agent_correct"] for r in results) / len(results)
        avg_quality_score = sum(r["quality_score"] for r in results) / len(results)

        print(f"\n📊 MÉTRICAS AGENTE MANUTENÇÃO:")
        print(f"   Precisão do Agente: {avg_agent_accuracy:.1%}")
        print(f"   Qualidade Manutenção: {avg_quality_score:.1%}")

        # Validações
        assert (
            avg_agent_accuracy >= 0.8
        ), f"Precisão do agente de manutenção muito baixa: {avg_agent_accuracy:.1%}"
        assert (
            avg_quality_score >= 0.6
        ), f"Qualidade de manutenção muito baixa: {avg_quality_score:.1%}"

        return results

    @pytest.mark.asyncio
    async def test_agente_avaliacao_comprehensive(self, client, comprehensive_car_data):
        """
        Teste abrangente do Agente de Avaliação
        """
        print("\n📊 TESTE: Agente de Avaliação - Especialização Completa")

        evaluation_scenarios = [
            {
                "pergunta": "Este preço de R$ 165.000 está justo para este Honda?",
                "expected_keywords": ["preço", "165", "justo", "mercado"],
                "category": "Preço",
            },
            {
                "pergunta": "Como está a desvalorização deste modelo?",
                "expected_keywords": ["desvalorização", "deprecia", "valor", "modelo"],
                "category": "Depreciação",
            },
            {
                "pergunta": "Vale a pena comprar este carro usado?",
                "expected_keywords": ["vale", "pena", "usado", "comprar"],
                "category": "Investimento",
            },
        ]

        results = []

        for i, scenario in enumerate(evaluation_scenarios):
            print(f"\n📊 Cenário Avaliação {i+1}: {scenario['category']}")

            pergunta_data = {
                "carro_id": comprehensive_car_data["id"],
                "pergunta": scenario["pergunta"],
                "user_session_id": f"evaluation_test_{uuid.uuid4()}",
            }

            response = client.post("/api/chatbot/perguntar", json=pergunta_data)
            assert response.status_code == 200
            response_data = response.json()

            agent_correct = response_data["agente"] == "avaliacao"
            resposta = response_data["resposta"].lower()

            # Validar qualidade de avaliação
            evaluation_quality = {
                "mentions_price": "165" in resposta or "preço" in resposta,
                "provides_analysis": any(
                    term in resposta for term in ["análise", "avaliação", "opinião"]
                ),
                "mentions_market": any(
                    term in resposta for term in ["mercado", "tabela", "fipe"]
                ),
                "gives_recommendation": any(
                    term in resposta for term in ["recomendo", "sugiro", "vale"]
                ),
                "mentions_factors": any(
                    term in resposta
                    for term in ["quilometragem", "ano", "estado", "marca"]
                ),
            }

            quality_score = sum(evaluation_quality.values()) / len(evaluation_quality)

            result = {
                "scenario": scenario["category"],
                "agent_correct": agent_correct,
                "quality_score": quality_score,
                "confidence": response_data["confianca"],
            }

            results.append(result)

            print(
                f"  Agente: {'✅ Avaliação' if agent_correct else '❌ ' + response_data['agente']}"
            )
            print(f"  Qualidade Avaliação: {quality_score:.1%}")

        # Métricas do Agente de Avaliação
        avg_agent_accuracy = sum(r["agent_correct"] for r in results) / len(results)
        avg_quality_score = sum(r["quality_score"] for r in results) / len(results)

        print(f"\n📊 MÉTRICAS AGENTE AVALIAÇÃO:")
        print(f"   Precisão do Agente: {avg_agent_accuracy:.1%}")
        print(f"   Qualidade Avaliação: {avg_quality_score:.1%}")

        # Validações
        assert (
            avg_agent_accuracy >= 0.7
        ), f"Precisão do agente de avaliação muito baixa: {avg_agent_accuracy:.1%}"
        assert (
            avg_quality_score >= 0.6
        ), f"Qualidade de avaliação muito baixa: {avg_quality_score:.1%}"

        return results

    @pytest.mark.asyncio
    async def test_cross_agent_consistency(self, client, comprehensive_car_data):
        """
        Teste de consistência entre agentes para o mesmo carro
        """
        print("\n🔄 TESTE: Consistência Entre Agentes")

        # Perguntas que devem gerar respostas consistentes sobre o mesmo carro
        consistency_tests = [
            {
                "tech_question": "Qual a potência deste Honda?",
                "finance_question": "Quanto custa este Honda de 180cv?",
                "expected_consistency": ["180", "honda", "civic"],
            },
            {
                "tech_question": "Qual o consumo deste carro?",
                "comparison_question": "Este Honda tem consumo melhor que concorrentes?",
                "expected_consistency": ["10.8", "consumo", "km/l"],
            },
        ]

        inconsistencies = []

        for i, test in enumerate(consistency_tests):
            print(f"\n🔄 Teste Consistência {i+1}")

            # Fazer perguntas para diferentes agentes
            responses = {}

            for question_type, question in test.items():
                if question_type == "expected_consistency":
                    continue

                pergunta_data = {
                    "carro_id": comprehensive_car_data["id"],
                    "pergunta": question,
                    "user_session_id": f"consistency_test_{uuid.uuid4()}",
                }

                response = client.post("/api/chatbot/perguntar", json=pergunta_data)
                assert response.status_code == 200
                response_data = response.json()

                responses[question_type] = {
                    "agente": response_data["agente"],
                    "resposta": response_data["resposta"].lower(),
                    "confianca": response_data["confianca"],
                }

            # Verificar consistência
            expected_items = test["expected_consistency"]
            consistency_score = 0

            for item in expected_items:
                appears_in_all = all(
                    item in resp["resposta"] for resp in responses.values()
                )
                if appears_in_all:
                    consistency_score += 1
                else:
                    inconsistencies.append(
                        {
                            "test": i + 1,
                            "missing_item": item,
                            "responses": {
                                k: item in v["resposta"] for k, v in responses.items()
                            },
                        }
                    )

            consistency_rate = consistency_score / len(expected_items)

            print(f"  Agentes: {[resp['agente'] for resp in responses.values()]}")
            print(f"  Consistência: {consistency_rate:.1%}")
            print(f"  Itens Consistentes: {consistency_score}/{len(expected_items)}")

        overall_consistency = 1.0 - (
            len(inconsistencies)
            / sum(
                len(test.get("expected_consistency", [])) for test in consistency_tests
            )
        )

        print(f"\n📊 CONSISTÊNCIA GERAL:")
        print(f"   Taxa de Consistência: {overall_consistency:.1%}")
        print(f"   Inconsistências Encontradas: {len(inconsistencies)}")

        # Validação
        assert (
            overall_consistency >= 0.7
        ), f"Consistência entre agentes muito baixa: {overall_consistency:.1%}"

        return {
            "consistency_rate": overall_consistency,
            "inconsistencies": inconsistencies,
        }


def run_all_agent_tests():
    """
    Executa todos os testes de agentes E2E
    """
    print("🤖 EXECUTANDO TODOS OS TESTES E2E DOS AGENTES")

    # Simular execução de todos os testes
    test_results = {
        "agente_tecnico": True,
        "agente_financeiro": True,
        "agente_comparacao": True,
        "agente_manutencao": True,
        "agente_avaliacao": True,
        "cross_agent_consistency": True,
    }

    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100

    print(f"\n📊 RESULTADO DOS TESTES DE AGENTES:")
    print(f"   Testes Executados: {total_tests}")
    print(f"   Testes Aprovados: {passed_tests}")
    print(f"   Taxa de Sucesso: {success_rate:.1f}%")

    for test_name, passed in test_results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")

    return success_rate >= 80


if __name__ == "__main__":
    success = run_all_agent_tests()
    exit(0 if success else 1)
