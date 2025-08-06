import re
from typing import Any, Dict, List, Tuple

from langchain_core.messages import AIMessage

from app.langgraph_chatbot_state import (
    AgentType,
    ChatbotState,
    adicionar_resposta_agente,
)
from app.uso_principal_processor import UsoMatcher


class ChatbotKeywords:
    """Classe para gerenciar palavras-chave dos agentes"""

    TECNICO = [
        "motor",
        "potencia",
        "potência",
        "cv",
        "hp",
        "cilindros",
        "consumo",
        "combustivel",
        "combustível",
        "gasolina",
        "etanol",
        "flex",
        "diesel",
        "cambio",
        "câmbio",
        "automatico",
        "automático",
        "manual",
        "cvt",
        "transmissao",
        "transmissão",
        "tração",
        "velocidade",
        "aceleração",
        "dimensões",
        "tamanho",
        "comprimento",
        "largura",
        "altura",
        "peso",
        "porta-malas",
        "porta malas",
        "bagageiro",
        "capacidade",
        "suspensao",
        "suspensão",
        "freios",
        "abs",
        "airbag",
        "segurança",
    ]

    FINANCEIRO = [
        "financiamento",
        "financiar",
        "parcelamento",
        "parcela",
        "entrada",
        "credito",
        "crédito",
        "banco",
        "taxa",
        "juros",
        "cdc",
        "leasing",
        "consórcio",
        "consorcio",
        "documentação",
        "documentacao",
        "cpf",
        "renda",
        "comprovante",
        "avalista",
        "fiador",
        "score",
        "serasa",
        "spc",
        "prestação",
        "prestacao",
        "simulação",
        "simulacao",
        "quanto",
        "valor",
        "preço",
        "preco",
        "custo",
        "pagar",
    ]

    COMPARACAO = [
        "comparar",
        "comparação",
        "comparacao",
        "versus",
        "vs",
        "ou",
        "melhor",
        "diferença",
        "diferenca",
        "escolher",
        "decidir",
        "alternativa",
        "similar",
        "parecido",
        "concorrente",
        "qual",
        "entre",
        "opção",
        "opcao",
        "duvida",
        "dúvida",
    ]

    MANUTENCAO = [
        "manutenção",
        "manutencao",
        "revisão",
        "revisao",
        "custo",
        "peças",
        "pecas",
        "oficina",
        "mecanico",
        "mecânico",
        "problema",
        "defeito",
        "reparo",
        "concerto",
        "conserto",
        "garantia",
        "recall",
        "assistencia",
        "assistência",
        "óleo",
        "oleo",
        "filtro",
        "pneu",
        "freio",
        "embreagem",
    ]

    AVALIACAO = [
        "avaliação",
        "avaliacao",
        "valor",
        "preço",
        "preco",
        "mercado",
        "valorização",
        "valorizacao",
        "desvalorização",
        "desvalorizacao",
        "revenda",
        "venda",
        "fipe",
        "tabela",
        "depreciação",
        "depreciacao",
        "investimento",
        "custo",
        "benefício",
        "beneficio",
        "vale",
        "pena",
    ]

    USO_PRINCIPAL = [
        "urbano",
        "cidade",
        "transito",
        "trânsito",
        "estacionamento",
        "viagem",
        "viagens",
        "estrada",
        "rodovia",
        "longa distancia",
        "longa distância",
        "trabalho",
        "profissional",
        "negócios",
        "negocios",
        "comercial",
        "familia",
        "família",
        "crianças",
        "criancas",
        "filhos",
        "familiar",
    ]


def router_node(state: ChatbotState) -> ChatbotState:
    """
    Nó de roteamento que analisa a pergunta e decide qual agente usar
    """
    pergunta = state["pergunta_atual"].lower()

    # Calcular confiança para cada agente
    confidencias = {}

    # Agente Técnico
    matches_tecnico = sum(
        1 for keyword in ChatbotKeywords.TECNICO if keyword in pergunta
    )
    confidencias[AgentType.TECNICO] = min(
        matches_tecnico / len(ChatbotKeywords.TECNICO) * 3, 1.0
    )

    # Agente Financeiro
    matches_financeiro = sum(
        1 for keyword in ChatbotKeywords.FINANCEIRO if keyword in pergunta
    )
    confidencias[AgentType.FINANCEIRO] = min(
        matches_financeiro / len(ChatbotKeywords.FINANCEIRO) * 3, 1.0
    )

    # Agente Comparação
    matches_comparacao = sum(
        1 for keyword in ChatbotKeywords.COMPARACAO if keyword in pergunta
    )
    confidencias[AgentType.COMPARACAO] = min(
        matches_comparacao / len(ChatbotKeywords.COMPARACAO) * 3, 1.0
    )

    # Agente Manutenção
    matches_manutencao = sum(
        1 for keyword in ChatbotKeywords.MANUTENCAO if keyword in pergunta
    )
    confidencias[AgentType.MANUTENCAO] = min(
        matches_manutencao / len(ChatbotKeywords.MANUTENCAO) * 3, 1.0
    )

    # Agente Avaliação
    matches_avaliacao = sum(
        1 for keyword in ChatbotKeywords.AVALIACAO if keyword in pergunta
    )
    confidencias[AgentType.AVALIACAO] = min(
        matches_avaliacao / len(ChatbotKeywords.AVALIACAO) * 3, 1.0
    )

    # Agente Uso Principal - novo agente especializado
    matches_uso = sum(
        1 for keyword in ChatbotKeywords.USO_PRINCIPAL if keyword in pergunta
    )
    # Boost para perguntas específicas sobre adequação de uso
    if any(
        phrase in pergunta
        for phrase in ["adequado para", "serve para", "é bom para", "recomendado para"]
    ):
        matches_uso += 2
    confidencias[AgentType.USO_PRINCIPAL] = min(
        matches_uso / len(ChatbotKeywords.USO_PRINCIPAL) * 3, 1.0
    )

    # Encontrar o agente com maior confiança
    melhor_agente = max(confidencias.items(), key=lambda x: x[1])
    agente_selecionado, melhor_confianca = melhor_agente

    # Se confiança muito baixa, usar resposta genérica
    if melhor_confianca < 0.3:
        agente_selecionado = AgentType.FINALIZER
        melhor_confianca = 0.5

    state["agente_selecionado"] = agente_selecionado
    state["confianca_agente"] = melhor_confianca

    return state


def tecnico_agent_node(state: ChatbotState) -> ChatbotState:
    """
    Nó do agente técnico especializado
    """
    carro = state["carro_data"]
    pergunta = state["pergunta_atual"].lower()

    # Determinar tipo de especificação solicitada
    if any(word in pergunta for word in ["motor", "potencia", "potência", "cv", "hp"]):
        resposta = _responder_motor_potencia(carro)
    elif any(word in pergunta for word in ["consumo", "combustivel", "combustível"]):
        resposta = _responder_consumo_combustivel(carro)
    elif any(word in pergunta for word in ["cambio", "câmbio", "transmissao"]):
        resposta = _responder_cambio(carro)
    elif any(word in pergunta for word in ["dimensões", "tamanho", "porta-malas"]):
        resposta = _responder_dimensoes(carro)
    elif any(word in pergunta for word in ["segurança", "seguranca", "airbag", "abs"]):
        resposta = _responder_seguranca(carro)
    else:
        resposta = _responder_geral_tecnico(carro)

    sugestoes = [
        "Quer saber sobre o consumo de combustível?",
        "Gostaria de conhecer as dimensões do veículo?",
        "Tem dúvidas sobre o sistema de segurança?",
    ]

    return adicionar_resposta_agente(
        state,
        resposta,
        AgentType.TECNICO,
        0.9,
        dados_utilizados=["especificacoes_tecnicas", "dados_fabricante"],
        sugestoes=sugestoes,
    )


def financeiro_agent_node(state: ChatbotState) -> ChatbotState:
    """
    Nó do agente financeiro especializado
    """
    carro = state["carro_data"]
    pergunta = state["pergunta_atual"].lower()

    if any(
        word in pergunta for word in ["simulação", "simulacao", "parcela", "prestação"]
    ):
        resposta = _simular_financiamento(carro)
    elif any(
        word in pergunta for word in ["documentação", "documentacao", "documento"]
    ):
        resposta = _documentacao_necessaria()
    elif any(word in pergunta for word in ["consórcio", "consorcio"]):
        resposta = _explicar_consorcio(carro)
    elif any(word in pergunta for word in ["leasing"]):
        resposta = _explicar_leasing(carro)
    elif any(word in pergunta for word in ["score", "serasa", "spc", "credito"]):
        resposta = _orientacoes_credito()
    else:
        resposta = _opcoes_financiamento_geral(carro)

    sugestoes = [
        "Quer simular diferentes prazos de financiamento?",
        "Gostaria de saber sobre consórcio?",
        "Tem dúvidas sobre a documentação necessária?",
    ]

    return adicionar_resposta_agente(
        state,
        resposta,
        AgentType.FINANCEIRO,
        0.9,
        dados_utilizados=["preco_veiculo", "tabelas_financiamento"],
        sugestoes=sugestoes,
    )


def comparacao_agent_node(state: ChatbotState) -> ChatbotState:
    """
    Nó do agente de comparação especializado
    """
    carro = state["carro_data"]

    # Buscar veículos similares para comparação
    carros_similares = _buscar_similares(carro)
    resposta = _gerar_comparacao(carro, carros_similares)

    sugestoes = [
        "Quer comparar com outra categoria?",
        "Gostaria de ver mais alternativas?",
        "Tem algum modelo específico em mente?",
    ]

    return adicionar_resposta_agente(
        state,
        resposta,
        AgentType.COMPARACAO,
        0.8,
        dados_utilizados=["banco_veiculos", "especificacoes_mercado"],
        sugestoes=sugestoes,
    )


def manutencao_agent_node(state: ChatbotState) -> ChatbotState:
    """
    Nó do agente de manutenção especializado
    """
    carro = state["carro_data"]
    resposta = _orientacoes_manutencao(carro)

    sugestoes = [
        "Quer saber sobre custos específicos?",
        "Gostaria de dicas de prevenção?",
        "Tem dúvidas sobre garantia?",
    ]

    return adicionar_resposta_agente(
        state,
        resposta,
        AgentType.MANUTENCAO,
        0.8,
        dados_utilizados=["tabela_manutencao", "historico_marca"],
        sugestoes=sugestoes,
    )


def avaliacao_agent_node(state: ChatbotState) -> ChatbotState:
    """
    Nó do agente de avaliação especializado
    """
    carro = state["carro_data"]
    resposta = _avaliacao_mercado(carro)

    sugestoes = [
        "Quer saber sobre depreciação?",
        "Gostaria de comparar com tabela FIPE?",
        "Tem dúvidas sobre revenda?",
    ]

    return adicionar_resposta_agente(
        state,
        resposta,
        AgentType.AVALIACAO,
        0.8,
        dados_utilizados=["tabela_fipe", "historico_precos"],
        sugestoes=sugestoes,
    )


def finalizer_node(state: ChatbotState) -> ChatbotState:
    """
    Nó finalizador para respostas genéricas e formatação final
    """
    carro = state["carro_data"]

    if not state["resposta_final"]:
        # Gerar resposta genérica
        resposta = f"""🤖 **Assistente Geral**

Oi! Sou especialista em informações sobre o **{carro.get('marca')} {carro.get('modelo')}**.

Posso te ajudar com:

🔧 **Especificações técnicas** - motor, consumo, potência
💰 **Financiamento** - simulações, documentação, consórcio  
⚖️ **Comparações** - outros modelos similares
🛠️ **Manutenção** - custos, cuidados, revisões
📊 **Avaliação** - valor de mercado, revenda

**❓ Como posso te ajudar especificamente com este veículo?**

Ou use os botões rápidos para perguntas comuns! 😊"""

        state = adicionar_resposta_agente(
            state,
            resposta,
            AgentType.FINALIZER,
            0.5,
            dados_utilizados=["dados_veiculo"],
            sugestoes=[
                "Quais são as especificações técnicas?",
                "Como funciona o financiamento?",
                "Quanto custa a manutenção?",
            ],
        )

    return state


# ============= FUNÇÕES AUXILIARES =============


def _responder_motor_potencia(carro: Dict[str, Any]) -> str:
    potencia = carro.get("potencia", "N/A")
    combustivel = carro.get("combustivel", "flex").title()

    return f"""🔧 **Especificações do Motor**

**Potência:** {potencia} cv
**Combustível:** {combustivel}
**Ano:** {carro.get('ano')}

{_get_contexto_motor(carro)}

💡 **Dica:** Este motor oferece um bom equilíbrio entre economia e performance para uso urbano."""


def _responder_consumo_combustivel(carro: Dict[str, Any]) -> str:
    consumo = carro.get("consumo", "N/A")
    combustivel = carro.get("combustivel", "flex").title()

    contexto_consumo = ""
    if isinstance(consumo, (int, float)) and consumo > 0:
        if consumo >= 14:
            contexto_consumo = "✅ **Excelente** economia de combustível!"
        elif consumo >= 12:
            contexto_consumo = "👍 **Boa** economia para a categoria."
        elif consumo >= 10:
            contexto_consumo = "⚖️ Consumo **moderado** para o porte."
        else:
            contexto_consumo = "⚠️ Consumo mais elevado, mas com boa performance."

    return f"""⛽ **Consumo e Combustível**

**Consumo médio:** {consumo} km/l (cidade/estrada)
**Tipo de combustível:** {combustivel}

{contexto_consumo}

📊 **Estimativa mensal** (1.500 km):
- Gasolina (R$ 5,50/L): ~R$ {round(1500 / consumo * 5.5) if isinstance(consumo, (int, float)) and consumo > 0 else 'N/A'}
- Etanol (R$ 3,80/L): ~R$ {round(1500 / consumo * 3.8) if isinstance(consumo, (int, float)) and consumo > 0 else 'N/A'}"""


def _responder_cambio(carro: Dict[str, Any]) -> str:
    cambio = carro.get("cambio", "manual").title()

    vantagens = {
        "Manual": "• Maior controle sobre o veículo\n• Menor custo de manutenção\n• Economia de combustível",
        "Automatico": "• Maior conforto no trânsito\n• Facilidade de condução\n• Ideal para uso urbano",
        "Cvt": "• Aceleração contínua suave\n• Ótima economia de combustível\n• Tecnologia moderna",
    }

    return f"""⚙️ **Sistema de Transmissão**

**Tipo de câmbio:** {cambio}

**Vantagens deste sistema:**
{vantagens.get(cambio, '• Sistema confiável e eficiente')}

💡 **Para você:** {_get_dica_cambio(cambio)}"""


def _responder_dimensoes(carro: Dict[str, Any]) -> str:
    porta_malas = carro.get("porta_malas", "N/A")
    capacidade = carro.get("capacidade_pessoas", 5)
    categoria = carro.get("categoria", "sedan").title()

    return f"""📏 **Dimensões e Espaço**

**Categoria:** {categoria}
**Capacidade:** {capacidade} pessoas
**Porta-malas:** {porta_malas} litros

{_get_contexto_espaco(carro)}

🎒 **Capacidade prática:**
{_get_exemplos_bagagem(porta_malas)}"""


def _responder_seguranca(carro: Dict[str, Any]) -> str:
    seguranca = carro.get("seguranca", 3)
    ano = carro.get("ano")

    return f"""🛡️ **Segurança e Proteção**

**Nível de segurança:** {"★" * seguranca}{"☆" * (5-seguranca)} ({seguranca}/5)
**Ano:** {ano}

**Itens de segurança esperados:**
{_get_itens_seguranca(ano, seguranca)}

🚨 **Importante:** Sempre verifique os itens específicos deste veículo com o vendedor."""


def _responder_geral_tecnico(carro: Dict[str, Any]) -> str:
    return f"""🔧 **Resumo Técnico - {carro.get('marca')} {carro.get('modelo')}**

• **Motor:** {carro.get('potencia', 'N/A')} cv, {carro.get('combustivel', 'flex').title()}
• **Câmbio:** {carro.get('cambio', 'manual').title()}  
• **Consumo:** {carro.get('consumo', 'N/A')} km/l
• **Capacidade:** {carro.get('capacidade_pessoas', 5)} pessoas
• **Porta-malas:** {carro.get('porta_malas', 'N/A')} litros

❓ **Precisa de mais detalhes?** Pergunte sobre consumo, motor, câmbio ou segurança!"""


def _simular_financiamento(carro: Dict[str, Any]) -> str:
    preco = carro.get("preco_promocional", carro.get("preco", 0))

    # Simulações com diferentes entradas e prazos
    sim_0_48_prestacao = preco * 0.024  # 2.4% estimado para 48x sem entrada
    sim_30_48_valor_financiado = preco * 0.7
    sim_30_48_prestacao = sim_30_48_valor_financiado * 0.0215  # 2.15% para 48x com 30%
    sim_30_36_prestacao = sim_30_48_valor_financiado * 0.0275  # 2.75% para 36x com 30%

    return f"""💰 **Simulação de Financiamento**

**Valor do veículo:** R$ {preco:,.2f}

📊 **Opções populares:**

**1️⃣ Sem entrada (48 meses)**
• Entrada: R$ 0
• 48x de R$ {sim_0_48_prestacao:,.0f}

**2️⃣ Entrada 30% (48 meses)**
• Entrada: R$ {preco * 0.3:,.0f}
• 48x de R$ {sim_30_48_prestacao:,.0f}

**3️⃣ Entrada 30% (36 meses)**
• Entrada: R$ {preco * 0.3:,.0f}
• 36x de R$ {sim_30_36_prestacao:,.0f}

⚠️ **Importante:** 
• Taxas variam conforme seu perfil de crédito
• Simulação com taxa estimada de 1,2% a.m.
• Valores finais dependem da aprovação bancária"""


def _documentacao_necessaria() -> str:
    return """📋 **Documentação para Financiamento**

**👤 Documentos Pessoais:**
• RG e CPF (originais + cópias)
• Comprovante de residência (até 3 meses)
• Comprovante de estado civil
• CNH (se for o condutor principal)

**💼 Comprovação de Renda:**
• 3 últimos holerites OU
• Declaração Imposto de Renda OU
• Extrato bancário (6 meses) para autônomos

**⚠️ Observações importantes:**
• Score mínimo geralmente 300-400
• Renda comprovada mínima 3x o valor da prestação
• Não ter nome negativado (ou regularizar antes)

💡 **Dica:** Tenha toda documentação em mãos para agilizar o processo!"""


def _explicar_consorcio(carro: Dict[str, Any]) -> str:
    preco = carro.get("preco_promocional", carro.get("preco", 0))
    prestacao_consorcio = preco / 100  # 100 meses típico

    return f"""🎯 **Consórcio de Veículos**

**Como funciona:**
• Grupo de pessoas compra o mesmo bem
• Mensalmente alguém é contemplado
• Você pode ser sorteado ou dar lance

**Para este veículo:**
• Valor da carta: R$ {preco:,.2f}
• Prestação aproximada: R$ {prestacao_consorcio:,.0f}/mês
• Prazo típico: 100 meses

**✅ Vantagens:**
• Sem juros, apenas taxa administrativa
• Pode dar lance para antecipar
• Valor menor que financiamento

**⚠️ Desvantagens:**
• Não leva o carro imediatamente
• Depende de sorteio ou lance alto
• Prazo mais longo"""


def _explicar_leasing(carro: Dict[str, Any]) -> str:
    preco = carro.get("preco_promocional", carro.get("preco", 0))

    return f"""🏢 **Leasing Operacional**

**O que é:**
• Aluguel de longo prazo (2-5 anos)
• Inclui manutenção e seguros
• Opção de compra no final

**Características:**
• Valor do veículo: R$ {preco:,.2f}
• Prestação estimada: R$ {preco * 0.03:,.0f}/mês*
• Incluso: seguro, manutenção, documentação

**✅ Vantagens:**
• Sem entrada alta
• Manutenção incluída
• Troca garantida no final
• Dedução fiscal (PJ)

**⚠️ Desvantagens:**
• Não é proprietário durante o contrato
• Restrições de quilometragem
• Geralmente para PJ

*Valores estimados, variam por empresa"""


def _orientacoes_credito() -> str:
    return """📊 **Orientações de Crédito**

**🎯 Score Ideal:**
• 700+ = Melhores taxas e condições
• 500-699 = Boas opções disponíveis  
• 300-499 = Possível com restrições
• <300 = Dificuldade, considere melhorar

**🔧 Como melhorar o score:**
• Quite débitos em atraso
• Mantenha dados atualizados nos órgãos
• Use cartão de crédito responsavelmente
• Tenha relacionamento bancário

**💡 Dicas para aprovação:**
• Comprove renda estável
• Tenha histórico bancário positivo
• Evite comprometer mais de 30% da renda
• Consider ter um avalista"""


def _opcoes_financiamento_geral(carro: Dict[str, Any]) -> str:
    preco = carro.get("preco_promocional", carro.get("preco", 0))

    return f"""💰 **Opções de Financiamento - {carro.get('marca')} {carro.get('modelo')}**

**Valor:** R$ {preco:,.2f}

**🏦 1. Financiamento Bancário (CDC)**
• ✅ Leva o carro na hora
• ✅ Vira proprietário imediatamente  
• ⚠️ Juros + altos

**🎯 2. Consórcio**
• ✅ Sem juros, só taxa admin
• ✅ Valor total menor
• ⚠️ Precisa aguardar contemplação

**💵 3. À Vista**
• ✅ Melhor preço
• ✅ Sem burocracias
• ✅ Proprietário imediato"""


def _buscar_similares(carro: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Simulação de carros similares baseado na categoria
    categoria = carro.get("categoria", "").lower()

    if "sedan" in categoria:
        return [
            {
                "marca": "Toyota",
                "modelo": "Corolla",
                "preco": 120000,
                "consumo": 12.5,
                "potencia": 144,
            },
            {
                "marca": "Honda",
                "modelo": "Civic",
                "preco": 140000,
                "consumo": 11.8,
                "potencia": 174,
            },
            {
                "marca": "Nissan",
                "modelo": "Sentra",
                "preco": 110000,
                "consumo": 13.2,
                "potencia": 130,
            },
        ]
    elif "suv" in categoria:
        return [
            {
                "marca": "Volkswagen",
                "modelo": "T-Cross",
                "preco": 95000,
                "consumo": 11.2,
                "potencia": 128,
            },
            {
                "marca": "Hyundai",
                "modelo": "Creta",
                "preco": 105000,
                "consumo": 12.8,
                "potencia": 130,
            },
            {
                "marca": "Jeep",
                "modelo": "Renegade",
                "preco": 115000,
                "consumo": 10.5,
                "potencia": 140,
            },
        ]
    else:
        return [
            {
                "marca": "Volkswagen",
                "modelo": "Polo",
                "preco": 70000,
                "consumo": 14.1,
                "potencia": 116,
            },
            {
                "marca": "Chevrolet",
                "modelo": "Onix",
                "preco": 75000,
                "consumo": 13.8,
                "potencia": 116,
            },
            {
                "marca": "Fiat",
                "modelo": "Argo",
                "preco": 68000,
                "consumo": 13.5,
                "potencia": 109,
            },
        ]


def _gerar_comparacao(carro: Dict[str, Any], similares: List[Dict[str, Any]]) -> str:
    if not similares:
        return f"""⚖️ **Análise Comparativa - {carro.get('marca')} {carro.get('modelo')}**

Este veículo tem bom posicionamento em sua categoria. Para comparações específicas, posso ajudar com modelos que você tenha em mente!"""

    comparacao = f"""⚖️ **Comparação - {carro.get('marca')} {carro.get('modelo')}**

**🎯 Seu veículo:**
• Preço: R$ {carro.get('preco', 0):,.2f}
• Consumo: {carro.get('consumo', 'N/A')} km/l
• Potência: {carro.get('potencia', 'N/A')} cv

**🔄 Principais concorrentes:**
"""

    for i, similar in enumerate(similares[:3], 1):
        comparacao += f"""
**{i}. {similar['marca']} {similar['modelo']}**
• Preço: R$ {similar['preco']:,.2f}
• Consumo: {similar['consumo']} km/l
• Potência: {similar['potencia']} cv
"""

    return comparacao


def _orientacoes_manutencao(carro: Dict[str, Any]) -> str:
    marca = carro.get("marca", "").upper()
    modelo = carro.get("modelo", "")
    ano = carro.get("ano", 2020)
    km = carro.get("km", 0)

    return f"""🔧 **Manutenção - {marca} {modelo}**

**📊 Perfil de manutenção da marca:**
{_get_perfil_marca(marca)}

**💰 Custos estimados anuais:**
{_get_custos_estimados(marca, ano)}

**💡 Dicas importantes:**
• Sempre use peças originais ou equivalentes
• Mantenha histórico de manutenções
• Procure oficinas especializadas na marca"""


def _avaliacao_mercado(carro: Dict[str, Any]) -> str:
    marca = carro.get("marca", "")
    modelo = carro.get("modelo", "")
    ano = carro.get("ano", 2020)
    preco = carro.get("preco", 0)
    km = carro.get("km", 0)

    return f"""📊 **Avaliação de Mercado - {marca} {modelo} {ano}**

**💰 Análise de Preço:**
• Preço atual: R$ {preco:,.2f}
• Posição: {_avaliar_preco_mercado(ano, preco)}
• Km: {km:,} km {_avaliar_quilometragem(km, ano)}

**🎯 Conclusão:**
{_conclusao_avaliacao(marca, modelo, ano, preco)}"""


# Funções auxiliares simplificadas
def _get_contexto_motor(carro):
    potencia = carro.get("potencia", 0)
    if potencia >= 150:
        return "🏎️ Motor com ótima performance"
    elif potencia >= 120:
        return "🚗 Motor com boa performance"
    else:
        return "🌱 Motor econômico"


def _get_dica_cambio(cambio):
    return "Sistema confiável para suas necessidades."


def _get_contexto_espaco(carro):
    return "🚗 Categoria versátil com bom aproveitamento interno."


def _get_exemplos_bagagem(porta_malas):
    return "• Consulte especificações detalhadas"


def _get_itens_seguranca(ano, nivel):
    return "• Freios ABS\n• Airbags frontais\n• Cintos de 3 pontos"


def _get_perfil_marca(marca):
    return "⚖️ Boa confiabilidade geral"


def _get_custos_estimados(marca, ano):
    return "• Manutenção básica: R$ 2.000/ano\n• Revisões: R$ 800/ano"


def _avaliar_preco_mercado(ano, preco):
    return "Preço justo para o ano" if ano >= 2020 else "Avalie bem o custo-benefício"


def _avaliar_quilometragem(km, ano):
    return "✅ Baixa" if km <= (2024 - ano) * 10000 else "⚖️ Adequada"


def _conclusao_avaliacao(marca, modelo, ano, preco):
    return "Boa compra para suas necessidades."


def uso_principal_agent_node(state: ChatbotState) -> ChatbotState:
    """
    Nó do agente especializado em adequação de uso principal
    """
    carro = state["carro_data"]
    pergunta = state["pergunta_atual"].lower()

    # Detectar tipo de uso mencionado na pergunta
    tipos_uso_mencionados = []
    if any(word in pergunta for word in ["urbano", "cidade", "transito", "trânsito"]):
        tipos_uso_mencionados.append("urbano")
    if any(word in pergunta for word in ["viagem", "estrada", "rodovia"]):
        tipos_uso_mencionados.append("viagem")
    if any(word in pergunta for word in ["trabalho", "profissional", "negócios"]):
        tipos_uso_mencionados.append("trabalho")
    if any(word in pergunta for word in ["familia", "família", "crianças", "filhos"]):
        tipos_uso_mencionados.append("familia")

    # Se não detectou uso específico, analisar todos
    if not tipos_uso_mencionados:
        tipos_uso_mencionados = ["urbano", "viagem", "trabalho", "familia"]

    resposta_partes = []
    resposta_partes.append(
        f"🎯 **Adequação do {carro['marca']} {carro['modelo']} para diferentes usos:**\n"
    )

    for uso in tipos_uso_mencionados:
        analise = _analisar_adequacao_uso(carro, uso)
        resposta_partes.append(analise)

    # Adicionar recomendação geral
    recomendacao = _gerar_recomendacao_uso_geral(carro, tipos_uso_mencionados)
    resposta_partes.append(f"\n💡 **Recomendação:**\n{recomendacao}")

    resposta_final = "\n".join(resposta_partes)

    return adicionar_resposta_agente(state, "uso_principal", resposta_final)


def _analisar_adequacao_uso(carro: Dict[str, Any], uso: str) -> str:
    """Analisa a adequação do carro para um tipo específico de uso"""
    categoria = carro.get("categoria", "")

    if uso == "urbano":
        pontos_positivos = []
        pontos_atencao = []

        # Análise para uso urbano
        if categoria in ["Hatch", "Sedan Compacto"]:
            pontos_positivos.append("Categoria ideal para manobras urbanas")
        elif categoria in ["SUV Grande", "Pickup"]:
            pontos_atencao.append("Veículo grande para uso urbano")

        if carro.get("potencia_desejada") == "economica":
            pontos_positivos.append("Motor econômico reduz custos")

        opcoes_urbanas = ["conectividade", "sensor", "camera"]
        opcionais = carro.get("opcionais", [])
        tech_count = sum(
            1
            for tech in opcoes_urbanas
            if any(tech in opcional.lower() for opcional in opcionais)
        )
        if tech_count > 0:
            pontos_positivos.append("Tecnologias que auxiliam no trânsito")

        resultado = f"🏙️ **USO URBANO:**\n"
        if pontos_positivos:
            resultado += f"✅ {'; '.join(pontos_positivos)}\n"
        if pontos_atencao:
            resultado += f"⚠️ {'; '.join(pontos_atencao)}\n"

        # Score de adequação
        score_urbano = len(pontos_positivos) * 2 - len(pontos_atencao)
        if score_urbano >= 4:
            resultado += "🌟 **Excelente para uso urbano**"
        elif score_urbano >= 2:
            resultado += "👍 **Adequado para uso urbano**"
        else:
            resultado += "⚖️ **Considere outros fatores**"

    elif uso == "viagem":
        pontos_positivos = []
        pontos_atencao = []

        # Análise para viagens
        if categoria in ["SUV", "Sedan Médio", "SUV Médio"]:
            pontos_positivos.append("Categoria oferece bom espaço interno")

        if carro.get("espaco_carga") in ["medio", "muito"]:
            pontos_positivos.append("Porta-malas adequado para bagagens")

        if carro.get("potencia_desejada") in ["media", "alta"]:
            pontos_positivos.append("Potência adequada para rodovia")
        elif carro.get("potencia_desejada") == "economica":
            pontos_atencao.append("Motor pode ser limitado em ultrapassagens")

        if carro.get("seguranca", 0) >= 4:
            pontos_positivos.append("Alta segurança para rodovias")

        resultado = f"🛣️ **VIAGENS LONGAS:**\n"
        if pontos_positivos:
            resultado += f"✅ {'; '.join(pontos_positivos)}\n"
        if pontos_atencao:
            resultado += f"⚠️ {'; '.join(pontos_atencao)}\n"

        score_viagem = len(pontos_positivos) * 2 - len(pontos_atencao)
        if score_viagem >= 4:
            resultado += "🌟 **Excelente para viagens**"
        elif score_viagem >= 2:
            resultado += "👍 **Adequado para viagens**"
        else:
            resultado += "⚖️ **Considere outros fatores**"

    elif uso == "trabalho":
        pontos_positivos = []
        pontos_atencao = []

        # Análise para trabalho
        if categoria in ["SUV", "Pickup", "Van"]:
            pontos_positivos.append("Categoria versátil para uso profissional")

        if carro.get("espaco_carga") == "muito":
            pontos_positivos.append("Grande capacidade de carga")

        # Verificar durabilidade
        km = carro.get("km", 0)
        if km <= 80000:
            pontos_positivos.append("Quilometragem adequada para uso profissional")
        else:
            pontos_atencao.append("Quilometragem alta para uso intensivo")

        # Verificar idade
        from datetime import datetime

        idade = datetime.now().year - carro.get("ano", 2020)
        if idade <= 8:
            pontos_positivos.append("Veículo relativamente novo")

        resultado = f"💼 **TRABALHO/NEGÓCIOS:**\n"
        if pontos_positivos:
            resultado += f"✅ {'; '.join(pontos_positivos)}\n"
        if pontos_atencao:
            resultado += f"⚠️ {'; '.join(pontos_atencao)}\n"

        score_trabalho = len(pontos_positivos) * 2 - len(pontos_atencao)
        if score_trabalho >= 4:
            resultado += "🌟 **Excelente para trabalho**"
        elif score_trabalho >= 2:
            resultado += "👍 **Adequado para trabalho**"
        else:
            resultado += "⚖️ **Considere outros fatores**"

    elif uso == "familia":
        pontos_positivos = []
        pontos_atencao = []

        # Análise para família
        if carro.get("capacidade_pessoas", 0) >= 5:
            pontos_positivos.append("Comporta toda a família")
        else:
            pontos_atencao.append("Espaço limitado para família grande")

        if carro.get("seguranca", 0) >= 4:
            pontos_positivos.append("Alta segurança protege a família")
        elif carro.get("seguranca", 0) < 3:
            pontos_atencao.append("Segurança pode ser melhor para família")

        if categoria in ["SUV", "Minivan"]:
            pontos_positivos.append("Facilita acesso de crianças e idosos")

        # Verificar itens de conforto
        opcionais = carro.get("opcionais", [])
        conforto_familia = ["ar_condicionado", "vidros_eletricos", "direcao_assistida"]
        conforto_count = sum(
            1
            for item in conforto_familia
            if any(item in opcional.lower() for opcional in opcionais)
        )
        if conforto_count > 1:
            pontos_positivos.append("Bons itens de conforto familiar")

        resultado = f"👨‍👩‍👧‍👦 **USO FAMILIAR:**\n"
        if pontos_positivos:
            resultado += f"✅ {'; '.join(pontos_positivos)}\n"
        if pontos_atencao:
            resultado += f"⚠️ {'; '.join(pontos_atencao)}\n"

        score_familia = len(pontos_positivos) * 2 - len(pontos_atencao)
        if score_familia >= 4:
            resultado += "🌟 **Excelente para família**"
        elif score_familia >= 2:
            resultado += "👍 **Adequado para família**"
        else:
            resultado += "⚖️ **Considere outros fatores**"

    else:
        resultado = f"❓ **Uso {uso} não reconhecido**"

    return resultado + "\n"


def _gerar_recomendacao_uso_geral(
    carro: Dict[str, Any], usos_analisados: List[str]
) -> str:
    """Gera uma recomendação geral baseada nos usos analisados"""
    categoria = carro.get("categoria", "")

    # Recomendações específicas por categoria
    if categoria == "Hatch":
        return "Este hatch é **ideal para uso urbano** e adequado para viagens curtas. Perfeito para quem valoriza economia e praticidade na cidade."

    elif categoria in ["SUV", "SUV Médio"]:
        return "Este SUV oferece **versatilidade para múltiplos usos**. Excelente para família e viagens, também adequado para trabalho e cidade."

    elif categoria == "Sedan Compacto":
        return "Este sedan combina **economia urbana com conforto**. Ideal para uso diário na cidade e adequado para viagens ocasionais."

    elif categoria == "Sedan Médio":
        return "Este sedan oferece **equilíbrio entre todos os usos**. Confortável para família, adequado para trabalho e viagens longas."

    elif categoria == "Pickup":
        return "Esta pickup é **excelente para trabalho** e adequada para família aventureira. Ideal para quem precisa de capacidade de carga."

    else:
        # Recomendação genérica baseada nos usos analisados
        usos_principais = []
        if "urbano" in usos_analisados:
            usos_principais.append("uso urbano")
        if "viagem" in usos_analisados:
            usos_principais.append("viagens")
        if "trabalho" in usos_analisados:
            usos_principais.append("trabalho")
        if "familia" in usos_analisados:
            usos_principais.append("uso familiar")

        if len(usos_principais) > 1:
            return f"Este veículo oferece boa versatilidade para {', '.join(usos_principais)}."
        elif usos_principais:
            return f"Este veículo é adequado principalmente para {usos_principais[0]}."
        else:
            return "Analise bem suas necessidades específicas antes da decisão."
