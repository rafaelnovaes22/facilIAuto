# 📚 Fase 1: Linguagem Acessível e Didática - Guia de Comunicação

## 🎯 Problema

**Jargões técnicos afastam usuários comuns:**

❌ **Exemplo ruim (técnico demais):**
```
"O Volkswagen Taos oferece ISOFIX em todos os assentos traseiros
e TCO de R$ 1.900/mês. Sistema ESP com 6 airbags e consumo de 11 km/L."
```

**Problemas:**
- "ISOFIX" → 90% dos usuários não sabem o que é
- "TCO" → Sigla técnica intimidadora
- "ESP" → Sistema desconhecido
- "km/L" → Entendido mas não contextualizado
- Linguagem fria e técnica

---

## ✅ Solução: Traduzir para Português Humano

✅ **Exemplo bom (didático):**
```
"O Volkswagen Taos é perfeito para quem tem crianças pequenas,
com pontos de fixação para cadeirinha em todos os bancos traseiros.
Você vai gastar em média R$ 1.900 por mês (incluindo parcela, combustível
e manutenção), o que cabe bem no seu orçamento."
```

**Melhorias:**
- ✅ "ISOFIX" → "pontos de fixação para cadeirinha"
- ✅ "TCO" → "quanto você vai gastar por mês"
- ✅ Explica o que está incluído no valor
- ✅ Conecta com a realidade do usuário ("cabe no seu orçamento")
- ✅ Linguagem quente e conversacional

---

## 📖 Glossário: Jargão → Português Claro

### Termos Técnicos de Segurança

| ❌ Jargão Técnico | ✅ Linguagem Acessível | 📝 Contexto |
|-------------------|------------------------|-------------|
| **ISOFIX** | "Pontos de fixação para cadeirinha de bebê" | Usar quando perfil tem crianças |
| **6 airbags** | "Seis bolsas de proteção em caso de batida" ou simplesmente "proteção reforçada" | Mencionar quantidade só se superior |
| **ABS** | "Freios seguros que evitam derrapagem" ou apenas "freios de segurança" | Só mencionar se usuário priorizou segurança |
| **ESP/ESC** | "Controle de estabilidade" ou "sistema que evita perder controle em curvas" | Simplificar ao máximo |
| **Crash test 5 estrelas** | "Aprovado com nota máxima em testes de colisão" | Traduzir para resultado prático |

**Regra geral:** Se o termo precisa de explicação, simplifique ou contextualize!

### Termos Financeiros

| ❌ Jargão Técnico | ✅ Linguagem Acessível | 📝 Quando Usar |
|-------------------|------------------------|----------------|
| **TCO (Total Cost of Ownership)** | "Custo mensal total" ou "Quanto você vai gastar por mês" | Sempre traduzir |
| **TCO breakdown** | "Incluindo parcela do financiamento, combustível, manutenção e seguro" | Explicar o que está incluído |
| **Budget percentage** | "X% da sua renda" ou "Y% do que você ganha" | Contextualizar com renda |
| **Financial health: green** | "Cabe tranquilamente no seu bolso" | Humanizar status |
| **Financial health: yellow** | "Vai apertar um pouco no fim do mês" | Ser honesto mas gentil |
| **Financial health: red** | "Pode comprometer seu orçamento" | Alertar sem assustar |
| **Down payment** | "Entrada" | Usar termo brasileiro |
| **Monthly installment** | "Parcela mensal" | Português direto |

### Termos Técnicos de Desempenho

| ❌ Jargão Técnico | ✅ Linguagem Acessível | 📝 Contexto |
|-------------------|------------------------|-------------|
| **11 km/L** | "Faz 11 km com 1 litro de gasolina" OU "Gasta cerca de R$ X por mês em combustível" | Contextualizar com valor em reais |
| **Consumo urbano vs. rodoviário** | "Na cidade gasta um pouco mais que na estrada" | Simplificar diferença |
| **150 cv de potência** | "Motor potente" ou "Boa força para subidas" | Traduzir para uso prático |
| **Torque** | Omitir (usuário comum não entende) | - |
| **0-100 em 9s** | "Acelera bem" ou omitir | Só para perfil "performance" |

### Termos de Conforto e Espaço

| ❌ Jargão Técnico | ✅ Linguagem Acessível | 📝 Contexto |
|-------------------|------------------------|-------------|
| **Porta-malas de 450L** | "Porta-malas espaçoso" ou "Cabe até 4 malas grandes" | Visualizar capacidade |
| **Entre-eixos de 2.700mm** | Omitir OU "Espaço interno generoso" | Traduzir para benefício |
| **5 lugares** | "Cabe a família inteira confortavelmente" (se família de 4-5) | Contextualizar com perfil |
| **Ar-condicionado dual zone** | "Ar-condicionado com controle separado" OU apenas "ar-condicionado" | Simplificar se não for diferencial |
| **Direção elétrica** | Omitir (padrão hoje) OU "Direção leve e fácil" | Só mencionar se diferencial |

### Categorias de Veículos

| Categoria | Explicação Didática | Quando Explicar |
|-----------|---------------------|-----------------|
| **SUV** | "Carro mais alto, com boa visibilidade e espaço" | Se usuário não selecionou preferência |
| **Hatch** | "Compacto, fácil de estacionar" | Sempre contextualizar |
| **Sedan** | "Carro tradicional de 4 portas com porta-malas separado" | Se usuário não familiar |
| **Pickup** | "Caminhonete" (termo brasileiro) | - |
| **SUV Compacto** | "SUV menor, mais econômico" | Diferenciar de SUV médio/grande |

---

## 🎨 Prompt Engineering Atualizado

### System Prompt Revisado

```
Você é um assistente especialista em recomendação de veículos, mas
fala de forma SIMPLES e DIDÁTICA, como um amigo ajudando outro amigo.

REGRAS DE LINGUAGEM:
1. Use português coloquial brasileiro (você, seu, sua)
2. Evite siglas e jargões técnicos
3. Traduza termos técnicos para benefícios práticos:
   - ISOFIX → "pontos de fixação para cadeirinha"
   - TCO → "custo mensal total" ou "quanto vai gastar por mês"
   - ABS → "freios de segurança"
   - km/L → contextualize com custo em reais
4. Explique números em contexto:
   - "R$ 1.900/mês" → "R$ 1.900/mês (incluindo tudo: parcela, gasolina, manutenção)"
   - "24% da renda" → "menos de um quarto do que você ganha"
5. Use linguagem visual e concreta:
   - "450L" → "cabe 4 malas grandes"
   - "6 airbags" → "proteção reforçada em caso de batida"
6. Seja honesto mas gentil:
   - ❌ "Financial health: red"
   - ✅ "Vai apertar um pouco o orçamento, mas é viável"

ESTRUTURA DA JUSTIFICATIVA:
1ª frase: Por que este carro é adequado para o uso do usuário (família, trabalho, etc)
2ª frase: Destaque financeiro (se cabe no orçamento, é econômico, etc)
3ª frase (opcional): Diferencial importante (segurança, espaço, confiabilidade)

TAMANHO: 2-3 frases (150-300 caracteres)
TOM: Amigável, claro, honesto
```

### Exemplos de Input/Output Revisados

---

#### **Exemplo 1: Família com Crianças**

**Input:**
```
Carro: Volkswagen Taos 1.4 TSI 2023 - R$ 85.000
Segurança: 6 airbags, ABS, ESP, ISOFIX
Consumo: 11 km/L cidade

Usuário:
- Uso: família (4 pessoas, 2 crianças de 3 e 5 anos)
- Orçamento: R$ 60k - R$ 100k
- Prioridades: segurança=5, espaço=5, economia=4
- Renda: R$ 8.000/mês

Análise:
- TCO mensal: R$ 1.900 (24% da renda)
- Principais forças: Segurança, Espaço, Preço adequado
```

**Output ANTES (técnico):**
```
"O Volkswagen Taos oferece categoria SUV ideal para família com ISOFIX
em todos os assentos. TCO de R$ 1.900/mês (24% da renda) e consumo de 11 km/L."
```

**Output DEPOIS (didático):**
```
"O Volkswagen Taos é perfeito para sua família de 4, com bastante espaço
e pontos de fixação para cadeirinha nos bancos de trás. Você vai gastar
cerca de R$ 1.900 por mês (incluindo tudo), o que cabe tranquilamente
no seu orçamento de R$ 8 mil."
```

---

#### **Exemplo 2: Primeiro Carro**

**Input:**
```
Carro: Renault Kwid 1.0 2022 - R$ 48.000
Consumo: 15 km/L
Categoria: Hatch compacto

Usuário:
- Uso: primeiro_carro
- Orçamento: R$ 30k - R$ 60k
- Prioridades: economia=5, custo_manutencao=5
- Renda: R$ 3.500/mês

Análise:
- TCO mensal: R$ 1.050 (30% da renda)
- Score: 0.82 (82%)
```

**Output ANTES (técnico):**
```
"Categoria hatch compacto ideal para primeiro carro. TCO de R$ 1.050/mês
(30% da renda). Excelente economia de 15 km/L."
```

**Output DEPOIS (didático):**
```
"O Renault Kwid é uma ótima escolha para quem está começando:
compacto (fácil de estacionar) e muito econômico (gasta só R$ 300 de
gasolina por mês). Por R$ 48 mil, você fica com folga no orçamento
para eventuais imprevistos."
```

---

#### **Exemplo 3: Comercial/Delivery**

**Input:**
```
Carro: Fiat Fiorino 1.4 2021 - R$ 62.000
Capacidade: 650 kg de carga
Consumo: 14 km/L

Usuário:
- Uso: comercial (entregas urbanas)
- Orçamento: R$ 50k - R$ 80k
- Prioridades: economia=5, custo_manutencao=5
- Renda: R$ 5.000/mês (do negócio)

Análise:
- TCO mensal: R$ 1.400 (28% da renda)
- Adequação comercial: 0.95
```

**Output ANTES (técnico):**
```
"Categoria furgão com capacidade de carga de 650kg. TCO operacional
de R$ 1.400/mês. Consumo urbano de 14 km/L adequado para rotas de entrega."
```

**Output DEPOIS (didático):**
```
"A Fiat Fiorino é ideal para entregas na cidade: carrega até 650 kg
(bastante espaço para mercadorias) e é econômica (14 km/L). Com custo
de R$ 1.400/mês, sobra boa margem de lucro nas entregas."
```

---

#### **Exemplo 4: Transporte por App (Uber/99)**

**Input:**
```
Carro: Toyota Corolla 2.0 2020 - R$ 95.000
Categoria: Sedan
Homologado: Uber, 99
Consumo: 12.5 km/L
Confiabilidade: 0.92

Usuário:
- Uso: transporte_passageiros (Uber/99)
- Orçamento: R$ 70k - R$ 110k
- Prioridades: confiabilidade=5, economia=5, revenda=4
- Renda mensal esperada: R$ 6.000 (do app)

Análise:
- TCO mensal: R$ 2.100 (35% da renda)
- Adequação para app: aprovado
```

**Output ANTES (técnico):**
```
"Sedan homologado para apps de transporte com índice de confiabilidade 0.92.
TCO de R$ 2.100/mês (35% da renda projetada). Consumo de 12.5 km/L adequado
para alta quilometragem."
```

**Output DEPOIS (didático):**
```
"O Toyota Corolla é aprovado pela Uber e 99, e é conhecido pela durabilidade
(essencial para quem roda muito). Gastando R$ 2.100/mês com o carro, você
precisa trabalhar cerca de 150-180 horas por mês para ter bom lucro."
```

---

#### **Exemplo 5: Situação Financeira Apertada**

**Input:**
```
Carro: Chevrolet Onix 1.0 2021 - R$ 72.000
Consumo: 13 km/L

Usuário:
- Uso: trabalho
- Orçamento: R$ 60k - R$ 80k
- Prioridades: economia=5
- Renda: R$ 4.000/mês

Análise:
- TCO mensal: R$ 1.600 (40% da renda)
- Financial health: red (acima de 30%)
```

**Output ANTES (técnico):**
```
"Categoria hatch com TCO de R$ 1.600/mês representando 40% da renda mensal.
Status financeiro: red zone. Consumo de 13 km/L."
```

**Output DEPOIS (didático e honesto):**
```
"O Chevrolet Onix é econômico (13 km/L), mas o custo mensal de R$ 1.600
vai comprometer 40% da sua renda, o que pode apertar o orçamento. Considere
negociar uma entrada maior ou procurar opções um pouco mais baratas."
```

---

## 🔧 Implementação no Código

### Atualizar `llm_prompts.py`

```python
SYSTEM_PROMPT = """
Você é um assistente especialista em recomendação de veículos, mas
fala de forma SIMPLES e DIDÁTICA, como um amigo ajudando outro amigo.

REGRAS DE LINGUAGEM:
1. Use português coloquial brasileiro (você, seu, sua)
2. Evite siglas e jargões técnicos
3. Traduza termos técnicos para benefícios práticos:
   - ISOFIX → "pontos de fixação para cadeirinha"
   - TCO → "custo mensal total" ou "quanto vai gastar por mês"
   - ABS/ESP → "freios de segurança" ou "sistemas de segurança"
   - km/L → contextualize com custo em reais ou consumo mensal
4. Explique números em contexto:
   - "R$ 1.900/mês" → "R$ 1.900/mês (incluindo tudo: parcela, gasolina, manutenção)"
   - "24% da renda" → "menos de um quarto do que você ganha"
5. Use linguagem visual e concreta:
   - "450L porta-malas" → "cabe 4 malas grandes"
   - "6 airbags" → "proteção reforçada"
6. Seja honesto mas gentil com limitações financeiras

ESTRUTURA: 2-3 frases
- 1ª: Por que é adequado para o uso
- 2ª: Destaque financeiro
- 3ª (opcional): Diferencial importante

TOM: Amigável, claro, honesto
"""

# Glossário de traduções
TERM_TRANSLATIONS = {
    "ISOFIX": "pontos de fixação para cadeirinha de bebê",
    "TCO": "custo mensal total",
    "ABS": "freios de segurança",
    "ESP": "controle de estabilidade",
    "ESC": "controle de estabilidade",
    "airbag": "bolsa de proteção",
    "SUV": "carro mais alto com boa visibilidade",
    "hatch": "compacto e fácil de estacionar",
    "sedan": "carro tradicional de 4 portas",
    "pickup": "caminhonete",
}

# Contextos de uso em linguagem simples
USAGE_DESCRIPTIONS = {
    "familia": "sua família",
    "trabalho": "seu dia a dia",
    "lazer": "passeios e viagens",
    "comercial": "seu negócio",
    "primeiro_carro": "quem está começando",
    "transporte_passageiros": "trabalhar com aplicativos de transporte",
}

# Faixas de custo em linguagem acessível
def get_financial_health_description(percentage: float) -> str:
    """Traduz % da renda para linguagem acessível"""
    if percentage <= 20:
        return "cabe tranquilamente no seu bolso"
    elif percentage <= 30:
        return "cabe no seu orçamento com alguma folga"
    elif percentage <= 40:
        return "vai comprometer parte significativa da renda, mas é viável"
    else:
        return "pode apertar bastante o orçamento"

# Tradução de consumo para custo mensal
def translate_fuel_consumption(kmpl: float, monthly_km: int = 1000) -> str:
    """Traduz km/L para custo mensal estimado"""
    fuel_price = 5.20  # Média nacional
    monthly_cost = (monthly_km / kmpl) * fuel_price
    return f"gasta cerca de R$ {monthly_cost:.0f} de gasolina por mês (rodando {monthly_km} km)"
```

### Adicionar Helper no `llm_justification_service.py`

```python
def _simplify_text(self, text: str) -> str:
    """
    Pós-processa texto do LLM para garantir linguagem acessível
    """
    # Substituir siglas comuns que podem escapar
    replacements = {
        r'\bTCO\b': 'custo mensal total',
        r'\bISOFIX\b': 'pontos de fixação para cadeirinha',
        r'\bABS\b': 'freios de segurança',
        r'\bESP\b': 'controle de estabilidade',
        r'\bkm/L\b': 'quilômetros por litro',
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text
```

---

## ✅ Checklist de Validação

Após gerar cada justificativa, validar:

### Linguagem Acessível
- [ ] Sem siglas técnicas sem explicação (TCO, ISOFIX, ABS, ESP)
- [ ] Valores em reais contextualizados ("incluindo tudo", "X% da sua renda")
- [ ] Consumo traduzido para custo mensal ou uso prático
- [ ] Categorias explicadas ou contextualizadas (SUV = carro alto, hatch = compacto)

### Tom e Estrutura
- [ ] Usa "você", "seu", "sua" (coloquial)
- [ ] 2-3 frases completas (150-300 caracteres)
- [ ] Tom amigável mas profissional
- [ ] Honesto sobre limitações (financeiras, de desempenho)

### Precisão
- [ ] Todos os dados mencionados estão corretos
- [ ] Não inventa informações
- [ ] Não usa superlativos injustificados ("excelente", "perfeito")

---

## 📊 Teste A/B

Após implementar, fazer teste com usuários reais:

**Grupo A:** Justificativas técnicas (baseline)
**Grupo B:** Justificativas didáticas (nova)

**Métricas:**
1. Taxa de conversão (quantos pedem mais informações)
2. Tempo na página de resultados
3. Feedback qualitativo ("entendi a explicação?")
4. NPS (Net Promoter Score)

**Hipótese:** Linguagem acessível aumenta conversão em 20-30%

---

## 🎯 Exemplos para Teste Manual

Para validar se as justificativas estão didáticas, testar com:

### Perfis de Teste

1. **Mãe de primeira viagem** (nunca comprou carro)
   - Usar: "pontos de fixação para cadeirinha", não "ISOFIX"
   - Contextualizar custo: "menos de R$ 2 mil por mês"

2. **Jovem no primeiro emprego**
   - Evitar: jargões técnicos
   - Foco: facilidade de uso e economia

3. **Empresário iniciante** (delivery)
   - Traduzir: capacidade de carga em termos práticos
   - Exemplo: "cabe até 100 caixas de pizza"

4. **Motorista de app** (Uber/99)
   - Contextualizar: custo vs. rendimento do app
   - Exemplo: "precisa trabalhar X horas para pagar o carro"

---

## 📖 Documentação para o Usuário Final

### Tooltip Helper (sugestão para frontend)

Adicionar tooltips explicativos na interface:

```tsx
<Tooltip label="Quanto você vai gastar por mês com o carro, incluindo parcela, combustível, manutenção e seguro">
  <Text>Custo mensal total: R$ 1.900</Text>
</Tooltip>

<Tooltip label="Pontos de fixação que garantem segurança máxima para cadeirinhas de bebê">
  <Icon as={InfoIcon} />
</Tooltip>
```

### Glossário na UI (opcional)

Página de ajuda com glossário simples:
- "O que significa custo mensal total?"
- "Como é calculado o consumo?"
- "O que são pontos de fixação para cadeirinha?"

---

## 🚀 Impacto Esperado

### Antes (Linguagem Técnica)
- ❌ Usuários confusos com siglas
- ❌ Não entendem se carro cabe no orçamento
- ❌ Não sabem o que é ISOFIX, TCO, ABS
- ❌ Taxa de conversão: baseline

### Depois (Linguagem Acessível)
- ✅ Explicações claras e contextualizadas
- ✅ Entendimento financeiro claro ("cabe no bolso?")
- ✅ Traduções práticas de termos técnicos
- ✅ Taxa de conversão: +20-30% (estimado)

---

**Resumo:** Falar a língua do usuário, não a língua do manual técnico! 🗣️

**Status:** 📋 Guia aprovado - pronto para integrar ao plano da Fase 1
