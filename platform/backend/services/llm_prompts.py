"""
Templates de prompts para LLM - Linguagem Didática e Acessível

Este módulo contém todos os prompts usados para gerar justificativas
de recomendação de veículos usando linguagem simples e sem jargões técnicos.
"""

# =============================================================================
# PROMPT SYSTEM - Instruções base para o LLM
# =============================================================================

SYSTEM_PROMPT_DIDATICO = """Você é um assistente especialista em recomendação de veículos, mas fala de forma SIMPLES e DIDÁTICA, como um amigo ajudando outro amigo.

REGRAS DE LINGUAGEM:
1. Use português coloquial brasileiro (você, seu, sua)
2. Evite siglas e jargões técnicos sem explicar
3. Traduza termos técnicos para benefícios práticos:
   - ISOFIX → "pontos de fixação para cadeirinha de bebê"
   - TCO → "custo mensal total" ou "quanto você vai gastar por mês"
   - ABS/ESP → "freios de segurança" ou "controle de estabilidade"
   - km/L → contextualize com custo em reais ou consumo mensal
4. Explique números em contexto:
   - "R$ 1.900/mês" → "R$ 1.900/mês (incluindo tudo: parcela, gasolina, manutenção)"
   - "24% da renda" → "menos de um quarto do que você ganha"
5. Use linguagem visual e concreta:
   - "450L porta-malas" → "cabe 4 malas grandes"
   - "6 airbags" → "proteção reforçada em caso de batida"
6. Seja honesto mas gentil com limitações financeiras ou técnicas

ESTRUTURA DA JUSTIFICATIVA (2-3 frases):
- 1ª frase: Por que este carro é adequado para o uso do usuário
- 2ª frase: Destaque financeiro (se cabe no orçamento, custo mensal)
- 3ª frase (opcional): Diferencial importante (segurança, espaço, confiabilidade)

TAMANHO: 150-300 caracteres (2-3 frases completas)
TOM: Amigável, claro, honesto

NÃO FAÇA:
- Não use emojis
- Não use formatação markdown
- Não invente dados que não foram fornecidos
- Não seja genérico ("ótimo veículo") - seja específico
- Não use superlativos injustificados ("excelente", "perfeito")
"""

# =============================================================================
# PROMPT USER - Template principal
# =============================================================================

USER_PROMPT_TEMPLATE = """Explique por que este carro é recomendado para este usuário:

CARRO:
- Modelo: {car_nome}
- Preço: R$ {car_preco:,.2f}
- Categoria: {car_categoria}
- Ano: {car_ano}
- Consumo: {car_consumo_cidade} km/L (cidade), {car_consumo_estrada} km/L (estrada)
- Segurança: {car_seguranca}
- Conforto: {car_conforto}
- Concessionária: {dealership_nome} em {dealership_cidade}

USUÁRIO:
- Uso principal: {uso_principal}
- Tamanho da família: {tamanho_familia} pessoas
- Tem crianças: {tem_criancas}
- Orçamento: R$ {orcamento_min:,.2f} - R$ {orcamento_max:,.2f}
- Prioridades: {prioridades_str}
- Renda mensal: {renda_mensal}

ANÁLISE:
- Score de compatibilidade: {score_percent}%
- Ranking: #{position} de {total_results} recomendações
- Custo mensal estimado: R$ {tco_mensal:,.2f}
- Percentual da renda: {tco_percent}%
- Principais pontos fortes: {top_features}

{context_hint}

Gere uma explicação contextual em português brasileiro (2-3 frases).
"""

# =============================================================================
# CONTEXTOS ESPECÍFICOS - Adicionar ao prompt conforme uso
# =============================================================================

CONTEXT_HINTS = {
    "familia": """
ATENÇÃO: Este é uso FAMILIAR. Foque em:
- Espaço interno e porta-malas (mencione se cabe cadeirinhas, carrinho de bebê)
- Segurança (se tem pontos de fixação para cadeirinha, quantos airbags)
- Conforto para viagens (ar-condicionado, espaço para as pernas)
- Economia (se for prioridade alta, contextualize consumo em R$/mês)
""",

    "comercial": """
ATENÇÃO: Este é uso COMERCIAL. Foque em:
- Capacidade de carga (em kg ou quantas caixas/volumes cabem)
- Custo operacional (TCO baixo é crítico - mencione em R$/mês)
- Robustez e confiabilidade (durabilidade para alto km rodado)
- Adequação para a operação (entregas urbanas, transporte de mercadorias)
""",

    "primeiro_carro": """
ATENÇÃO: Este é o PRIMEIRO CARRO. Foque em:
- Facilidade de dirigir e estacionar (compacto, leve, direção fácil)
- Custo de manutenção acessível (mencione se é econômico para manter)
- Boa revenda futura (valorização no mercado de usados)
- Seguros mais baratos (veículos menores têm seguro mais em conta)
""",

    "trabalho": """
ATENÇÃO: Este é uso para TRABALHO diário. Foque em:
- Economia de combustível (custo mensal de gasolina)
- Confiabilidade (não deixa na mão no dia a dia)
- Conforto para trajetos diários (ar-condicionado, bancos confortáveis)
- Custo-benefício (valor justo pelo que oferece)
""",

    "lazer": """
ATENÇÃO: Este é uso para LAZER e viagens. Foque em:
- Conforto em viagens longas (espaço, suspensão, ar-condicionado)
- Porta-malas espaçoso (para bagagens de fim de semana)
- Performance razoável (para estradas e subidas)
- Versatilidade (serve para cidade e estrada)
""",

    "transporte_passageiros": """
ATENÇÃO: Este é para TRANSPORTE POR APLICATIVO (Uber/99). Foque em:
- Homologação para apps (mencione se é aceito pela Uber/99)
- Durabilidade (essencial para quem roda muito km/mês)
- Custo operacional (TCO em R$/mês vs. rendimento esperado do app)
- Conforto para passageiros (espaço traseiro, ar-condicionado)
- Contextualize: "trabalhando X horas/mês você cobre os custos"
"""
}

# =============================================================================
# TRADUÇÕES - Glossário de termos técnicos para linguagem acessível
# =============================================================================

TERM_TRANSLATIONS = {
    "ISOFIX": "pontos de fixação para cadeirinha de bebê",
    "TCO": "custo mensal total",
    "ABS": "freios de segurança",
    "ESP": "controle de estabilidade",
    "ESC": "controle de estabilidade",
    "airbag": "bolsa de proteção",
    "airbags": "bolsas de proteção",
    "SUV": "carro mais alto com boa visibilidade",
    "hatch": "compacto e fácil de estacionar",
    "sedan": "carro tradicional de 4 portas",
    "pickup": "caminhonete",
    "km/L": "quilômetros por litro",
}

# =============================================================================
# DESCRIÇÕES DE USO - Em linguagem simples
# =============================================================================

USAGE_DESCRIPTIONS = {
    "familia": "sua família",
    "trabalho": "seu dia a dia de trabalho",
    "lazer": "passeios e viagens",
    "comercial": "seu negócio",
    "primeiro_carro": "quem está começando",
    "transporte_passageiros": "trabalhar com aplicativos de transporte",
}

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_financial_health_description(percentage: float) -> str:
    """
    Traduz percentual da renda em linguagem acessível

    Args:
        percentage: Percentual do custo mensal em relação à renda (0-100)

    Returns:
        Descrição em português claro
    """
    if percentage <= 20:
        return "cabe tranquilamente no seu bolso"
    elif percentage <= 30:
        return "cabe no seu orçamento com alguma folga"
    elif percentage <= 40:
        return "vai comprometer parte da renda, mas é viável"
    else:
        return "pode apertar bastante o orçamento"


def translate_fuel_consumption(
    kmpl: float,
    monthly_km: int = 1000,
    fuel_price: float = 5.20
) -> str:
    """
    Traduz consumo de combustível para custo mensal estimado

    Args:
        kmpl: Consumo em km/L
        monthly_km: Quilometragem mensal estimada
        fuel_price: Preço do combustível por litro

    Returns:
        Descrição do custo mensal em português
    """
    if kmpl <= 0:
        return "consumo não informado"

    monthly_cost = (monthly_km / kmpl) * fuel_price

    return (f"gasta cerca de R$ {monthly_cost:.0f} de gasolina por mês "
            f"(rodando {monthly_km} km)")


def get_context_hint(uso_principal: str) -> str:
    """
    Retorna hint de contexto baseado no uso principal

    Args:
        uso_principal: Tipo de uso (familia, comercial, etc.)

    Returns:
        Hint de contexto para adicionar ao prompt
    """
    return CONTEXT_HINTS.get(uso_principal, "")


def build_prioridades_string(prioridades: dict) -> str:
    """
    Constrói string legível das prioridades do usuário

    Args:
        prioridades: Dict com prioridades e valores (0-5)

    Returns:
        String formatada, ex: "economia (alta), segurança (alta), espaço (média)"
    """
    if not prioridades:
        return "não especificadas"

    # Mapear valores numéricos para texto
    priority_map = {
        5: "muito alta",
        4: "alta",
        3: "média",
        2: "baixa",
        1: "muito baixa",
        0: "não prioritário"
    }

    # Filtrar apenas prioridades com valor > 0
    active_priorities = {k: v for k, v in prioridades.items() if v > 0}

    if not active_priorities:
        return "não especificadas"

    # Ordenar por valor (maior primeiro)
    sorted_priorities = sorted(
        active_priorities.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Construir string
    parts = []
    for key, value in sorted_priorities[:3]:  # Máximo 3 prioridades
        priority_text = priority_map.get(value, "média")
        parts.append(f"{key} ({priority_text})")

    return ", ".join(parts)


def format_safety_features(itens_seguranca: list) -> str:
    """
    Formata itens de segurança em linguagem acessível

    Args:
        itens_seguranca: Lista de itens de segurança

    Returns:
        String formatada e legível
    """
    if not itens_seguranca:
        return "itens de segurança padrão"

    # Traduzir itens técnicos
    translated = []
    for item in itens_seguranca[:4]:  # Máximo 4 itens
        item_lower = item.lower()
        if "isofix" in item_lower:
            translated.append("pontos de fixação para cadeirinha")
        elif "airbag" in item_lower:
            # Extrair número se houver
            import re
            match = re.search(r'(\d+)', item)
            if match:
                num = match.group(1)
                translated.append(f"{num} airbags")
            else:
                translated.append("airbags")
        elif "abs" in item_lower:
            translated.append("freios ABS")
        elif "esp" in item_lower or "esc" in item_lower:
            translated.append("controle de estabilidade")
        else:
            translated.append(item)

    return ", ".join(translated)


def format_comfort_features(itens_conforto: list) -> str:
    """
    Formata itens de conforto em linguagem acessível

    Args:
        itens_conforto: Lista de itens de conforto

    Returns:
        String formatada e legível
    """
    if not itens_conforto:
        return "itens de conforto padrão"

    # Filtrar itens mais relevantes
    relevant = []
    for item in itens_conforto:
        item_lower = item.lower()
        if "ar" in item_lower and "condicionado" in item_lower:
            relevant.append("ar-condicionado")
        elif "direção" in item_lower:
            relevant.append("direção elétrica")
        elif "banco" in item_lower:
            relevant.append("bancos ajustáveis")
        elif "vidro" in item_lower and "elétric" in item_lower:
            continue  # Omitir (padrão hoje)
        else:
            relevant.append(item)

    return ", ".join(relevant[:3])  # Máximo 3 itens
