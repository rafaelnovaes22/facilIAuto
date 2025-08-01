from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from app.models import QuestionarioBusca, CarroRecomendacao, RespostaBusca
from app.database import get_carros, get_carro_by_id
import json

class EstadoBuscaDict(TypedDict):
    questionario: QuestionarioBusca
    carros_disponiveis: List[Dict[str, Any]]
    carros_filtrados: List[Dict[str, Any]]
    pontuacoes: List[Dict[str, Any]]
    recomendacoes_finais: List[CarroRecomendacao]
    resumo_perfil: str
    sugestoes_personalizadas: List[str]

def filtrar_carros_basicos(state: EstadoBuscaDict) -> EstadoBuscaDict:
    """Filtra carros baseado em critérios básicos: orçamento e região"""
    carros = get_carros()
    questionario = state["questionario"]
    
    carros_filtrados = []
    
    for carro in carros:
        # Filtro de orçamento (opcional)
        if questionario.orcamento_min is not None and questionario.orcamento_max is not None:
            if not (questionario.orcamento_min <= carro["preco"] <= questionario.orcamento_max):
                continue
            
        # Filtro de região
        if questionario.regiao not in carro["regiao"]:
            continue
            
        # Todos os carros usados estão disponíveis (removido filtro de urgência)
        carros_filtrados.append(carro)
    
    return {**state, "carros_filtrados": carros_filtrados}

def calcular_scores_compatibilidade(state: EstadoBuscaDict) -> EstadoBuscaDict:
    """Calcula scores de compatibilidade baseado no perfil do usuário"""
    questionario = state["questionario"]
    scores = []
    
    for carro in state["carros_filtrados"]:
        score = 0.0
        razoes = []
        pontos_fortes = []
        consideracoes = []
        
        # Garante que o carro tem todas as propriedades necessárias
        if not carro:
            continue
        
        # Score por marca/modelo preferido (Sistema Avançado - peso alto: 20%)
        marca_score = 0
        modelo_score = 0
        
        # Marca principal (prioridade máxima)
        if questionario.marca_preferida and questionario.marca_preferida != "sem_preferencia":
            if questionario.marca_preferida.upper() == carro["marca"].upper():
                marca_score += 20
                razoes.append(f"Marca preferida: {carro['marca']}")
        
        # Marcas alternativas (prioridade secundária)
        if hasattr(questionario, 'marcas_alternativas') and questionario.marcas_alternativas:
            for marca_alt in questionario.marcas_alternativas:
                if marca_alt.upper() == carro["marca"].upper() and marca_score == 0:
                    marca_score += 12  # Menos que a preferida, mas ainda significativo
                    razoes.append(f"Marca alternativa escolhida: {carro['marca']}")
                    break
        
        # Modelo específico (prioridade máxima)
        if questionario.modelo_especifico and questionario.modelo_especifico != "aberto_opcoes":
            if questionario.modelo_especifico.lower() in carro["modelo"].lower():
                modelo_score += 15
                razoes.append(f"Modelo específico: {carro['modelo']}")
        
        # Modelos alternativos
        if hasattr(questionario, 'modelos_alternativos') and questionario.modelos_alternativos:
            for modelo_alt in questionario.modelos_alternativos:
                if modelo_alt.lower() in carro["modelo"].lower() and modelo_score == 0:
                    modelo_score += 8  # Peso menor que o modelo principal
                    razoes.append(f"Modelo alternativo: {carro['modelo']}")
                    break
        
        # Aplicar scores de marca e modelo
        score += marca_score
        score += modelo_score
        
        # Score por uso principal (peso: 15%)
        uso_match = len(set(questionario.uso_principal) & set(carro["uso_recomendado"]))
        if uso_match > 0:
            uso_score = (uso_match / len(questionario.uso_principal)) * 15
            score += uso_score
            razoes.append(f"Adequado para: {', '.join(set(questionario.uso_principal) & set(carro['uso_recomendado']))}")
        
        # Score por capacidade de pessoas (peso: 10%)
        if carro["capacidade_pessoas"] >= questionario.pessoas_transportar:
            score += 10
            pontos_fortes.append(f"Comporta {carro['capacidade_pessoas']} pessoas")
        else:
            consideracoes.append(f"Capacidade limitada: {carro['capacidade_pessoas']} pessoas")
        
        # Score por espaço de carga (peso: 10%)
        if questionario.espaco_carga == "pequeno" and carro["porta_malas"] >= 250:
            score += 10
        elif questionario.espaco_carga == "medio" and carro["porta_malas"] >= 400:
            score += 10
        elif questionario.espaco_carga == "grande" and carro["porta_malas"] >= 500:
            score += 10
        
        # Score por potência desejada (peso: 10%)
        if questionario.potencia_desejada == "economica" and carro["potencia"] <= 120:
            score += 10
            pontos_fortes.append("Motor econômico")
        elif questionario.potencia_desejada == "media" and 120 < carro["potencia"] <= 170:
            score += 10
            pontos_fortes.append("Potência equilibrada")
        elif questionario.potencia_desejada == "alta" and carro["potencia"] > 170:
            score += 10
            pontos_fortes.append("Alta performance")
        
        # Score por prioridade (peso: 15%)
        if questionario.prioridade == "economia" and carro["economia"] >= 4:
            score += 15
            pontos_fortes.append("Excelente economia de combustível")
        elif questionario.prioridade == "conforto" and carro["conforto"] >= 4:
            score += 15
            pontos_fortes.append("Alto nível de conforto")
        elif questionario.prioridade == "seguranca" and carro["seguranca"] >= 4:
            score += 15
            pontos_fortes.append("Excelente segurança")
        elif questionario.prioridade == "performance" and carro["performance"] >= 4:
            score += 15
            pontos_fortes.append("Alta performance")
        elif questionario.prioridade == "equilibrio":
            media_atributos = (carro["economia"] + carro["conforto"] + carro["seguranca"] + carro["performance"]) / 4
            if media_atributos >= 3.5:
                score += 15
                pontos_fortes.append("Excelente equilíbrio geral")
        
        # Score por preço dentro do orçamento (peso: 10%)
        if questionario.orcamento_min is not None and questionario.orcamento_max is not None:
            orcamento_medio = (questionario.orcamento_max + questionario.orcamento_min) / 2
            if carro["preco"] <= orcamento_medio:
                score += 10
                pontos_fortes.append("Preço atrativo dentro do orçamento")
        
        # Score por crianças/família (peso: 10%)
        if questionario.criancas and carro["seguranca"] >= 4:
            score += 5
            pontos_fortes.append("Segurança adequada para crianças")
        if questionario.criancas and "familia" in carro["uso_recomendado"]:
            score += 5
            pontos_fortes.append("Recomendado para famílias")
        
        # Score por urgência do processo de compra (peso: 5%)
        if questionario.urgencia == "hoje_amanha":
            # Prioriza carros em destaque (mais confiáveis para compra rápida)
            if carro.get("destaque", False):
                score += 5
                pontos_fortes.append("Ideal para compra imediata")
            # Boost para carros com menos quilometragem (menos riscos)
            if carro.get("km", 0) < 50000:
                score += 3
                pontos_fortes.append("Baixa quilometragem - compra segura")
        elif questionario.urgencia == "esta_semana":
            if carro.get("destaque", False):
                score += 3
                pontos_fortes.append("Boa opção para esta semana")
        elif questionario.urgencia == "sem_pressa":
            # Para quem não tem pressa, inclui mais opções variadas
            razoes.append("Tempo disponível para análise detalhada")
        
        scores.append({
            "carro": carro,
            "score": min(score, 100),  # Máximo 100
            "razoes": razoes,
            "pontos_fortes": pontos_fortes,
            "consideracoes": consideracoes
        })
    
    # Ordena por score decrescente
    scores.sort(key=lambda x: x["score"], reverse=True)
    return {**state, "pontuacoes": scores}

def gerar_recomendacoes_finais(state: EstadoBuscaDict) -> EstadoBuscaDict:
    """Gera as recomendações finais com análise detalhada"""
    recomendacoes = []
    
    # Pega os top 5 carros com melhor score
    top_carros = state["pontuacoes"][:5]
    
    for item in top_carros:
        carro = item["carro"]
        recomendacao = {
            "id": carro["id"],
            "marca": carro["marca"],
            "modelo": carro["modelo"],
            "versao": carro.get("versao"),
            "ano": carro["ano"],
            "preco": carro["preco"],
            "preco_promocional": carro.get("preco_promocional"),
            "categoria": carro["categoria"],
            "cor": carro.get("cor"),
            "km": carro.get("km"),
            "score_compatibilidade": round(item["score"], 1),
            "razoes_recomendacao": item.get("razoes", []),
            "pontos_fortes": item.get("pontos_fortes", []),
            "consideracoes": item.get("consideracoes", []),
            "fotos": carro.get("fotos", []),
            "descricao": carro.get("descricao"),
            "opcionais": carro.get("opcionais", [])
        }
        recomendacoes.append(recomendacao)
    
    return {**state, "recomendacoes_finais": recomendacoes}

def gerar_resumo_perfil(state: EstadoBuscaDict) -> EstadoBuscaDict:
    """Gera resumo do perfil do usuário"""
    q = state["questionario"]
    
    resumo = f"Perfil do usuário: "
    resumo += f"Busca por {', '.join(q.uso_principal)} "
    resumo += f"na região {q.regiao}, "
    resumo += f"para {q.pessoas_transportar} pessoas, "
    
    # Incluir orçamento apenas se fornecido
    if q.orcamento_min is not None and q.orcamento_max is not None:
        resumo += f"com orçamento entre R$ {q.orcamento_min:,} e R$ {q.orcamento_max:,}, "
    else:
        resumo += f"sem restrição de orçamento, "
    
    resumo += f"priorizando {q.prioridade}, "
    
    # Mapear urgência para descrição amigável
    urgencia_map = {
        "hoje_amanha": "compra imediata",
        "esta_semana": "finalizar esta semana", 
        "ate_15_dias": "até 15 dias",
        "sem_pressa": "sem pressa"
    }
    urgencia_texto = urgencia_map.get(q.urgencia, q.urgencia)
    resumo += f"com urgência de {urgencia_texto}."
    
    if q.marca_preferida:
        resumo += f" Preferência por marca: {q.marca_preferida}."
    
    return {**state, "resumo_perfil": resumo}

def gerar_sugestoes_gerais(state: EstadoBuscaDict) -> EstadoBuscaDict:
    """Gera sugestões gerais baseadas no perfil"""
    sugestoes = []
    q = state["questionario"]
    
    # Sugestões baseadas na urgência
    if q.urgencia == "hoje_amanha":
        sugestoes.append("Para compra imediata, tenha documentos em mãos e confirme a situação financeira antecipadamente")
        sugestoes.append("Priorize carros em destaque que passaram por revisão técnica")
    elif q.urgencia == "esta_semana":
        sugestoes.append("Aproveite a semana para testar os carros e negociar condições de pagamento")
    elif q.urgencia == "ate_15_dias":
        sugestoes.append("Você tem tempo para comparar opções e buscar o melhor custo-benefício")
    elif q.urgencia == "sem_pressa":
        sugestoes.append("Sem pressa você pode encontrar oportunidades únicas e negociar melhores preços")
    
    if q.criancas:
        sugestoes.append("Para segurança das crianças, considere modelos com 5 estrelas em segurança")
    
    if "urbano" in q.uso_principal:
        sugestoes.append("Para uso urbano, priorize carros com boa economia de combustível e facilidade de estacionamento")
    
    if "viagem" in q.uso_principal:
        sugestoes.append("Para viagens, considere conforto, porta-malas amplo e economia em estrada")
    
    if q.prioridade == "economia":
        sugestoes.append("Considere também os custos de manutenção e seguro além do preço de compra")
    
    if len(state["carros_filtrados"]) < 3:
        sugestoes.append("Considere flexibilizar alguns critérios para ter mais opções disponíveis")
    
    # Garante que sempre temos uma lista
    sugestoes_finais = sugestoes if sugestoes else ["Analise cuidadosamente as opções disponíveis e teste os carros antes da compra"]
    return {**state, "sugestoes_personalizadas": sugestoes_finais}

def criar_grafo_busca():
    """Cria o grafo LangGraph para busca inteligente"""
    workflow = StateGraph(EstadoBuscaDict)
    
    # Adiciona os nós
    workflow.add_node("filtrar_basicos", filtrar_carros_basicos)
    workflow.add_node("calcular_scores", calcular_scores_compatibilidade)
    workflow.add_node("gerar_recomendacoes", gerar_recomendacoes_finais)
    workflow.add_node("gerar_resumo", gerar_resumo_perfil)
    workflow.add_node("gerar_sugestoes", gerar_sugestoes_gerais)
    
    # Define o fluxo
    workflow.set_entry_point("filtrar_basicos")
    workflow.add_edge("filtrar_basicos", "calcular_scores")
    workflow.add_edge("calcular_scores", "gerar_recomendacoes")
    workflow.add_edge("gerar_recomendacoes", "gerar_resumo")
    workflow.add_edge("gerar_resumo", "gerar_sugestoes")
    workflow.add_edge("gerar_sugestoes", END)
    
    return workflow.compile()

def processar_busca_inteligente(questionario: QuestionarioBusca) -> RespostaBusca:
    """Função principal que executa a busca inteligente"""
    grafo = criar_grafo_busca()
    
    # Cria o estado inicial
    estado: EstadoBuscaDict = {
        "questionario": questionario,
        "carros_disponiveis": [],
        "carros_filtrados": [],
        "pontuacoes": [],
        "recomendacoes_finais": [],
        "resumo_perfil": "",
        "sugestoes_personalizadas": []
    }
    
    # Executa o grafo
    resultado = grafo.invoke(estado)
    
    # Converte as recomendações de dict para CarroRecomendacao
    recomendacoes = []
    for rec_dict in resultado["recomendacoes_finais"]:
        rec = CarroRecomendacao(**rec_dict)
        recomendacoes.append(rec)
    
    # Retorna a resposta estruturada
    return RespostaBusca(
        recomendacoes=recomendacoes,
        resumo_perfil=resultado["resumo_perfil"],
        sugestoes_gerais=resultado["sugestoes_personalizadas"]
    ) 