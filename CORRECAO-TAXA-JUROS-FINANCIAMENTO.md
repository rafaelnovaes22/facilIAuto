# Correção: Taxa de Juros de Financiamento

## Problema Identificado

A taxa de juros usada nos cálculos de TCO estava **muito abaixo** da realidade do mercado brasileiro:

- ❌ **Taxa anterior**: 12% a.a. (1% a.m.)
- ✅ **Taxa real mercado 2025**: 20-29.5% a.a. (1.5-2.24% a.m.)
- **Diferença**: Subestimava o custo do financiamento em ~50%

## Pesquisa de Mercado (2025)

### Taxas Praticadas

**Financiamento de Veículos Usados**:
- Mínimo: 1.5% a.m. (19.56% a.a.)
- Máximo: 2.24% a.m. (30.5% a.a.)
- **Média**: ~2% a.m. (26.82% a.a.)

### Fontes
- Bancos tradicionais: Santander, Itaú, Bradesco, Caixa
- Financeiras: BV, Omni, Aymoré
- Banco Central: Taxa média de financiamento de veículos

## Decisão: Taxa de 24% a.a. (2% a.m.)

Escolhemos **24% a.a. (2% a.m.)** como taxa padrão porque:

1. **Conservadora**: Está na média do mercado
2. **Realista**: Reflete taxas praticadas em 2025
3. **Justa**: Não subestima nem superestima custos
4. **Arredondada**: Fácil de entender (2% ao mês)

## Impacto nos Cálculos

### Exemplo: Carro de R$ 80.000

**Condições**:
- Valor: R$ 80.000
- Entrada: 20% (R$ 16.000)
- Financiado: R$ 64.000
- Prazo: 60 meses

**ANTES (12% a.a. = 1% a.m.)**:
- Parcela: ~R$ 1.422/mês
- Total pago: R$ 85.320
- Juros totais: R$ 21.320

**DEPOIS (24% a.a. = 2% a.m.)**:
- Parcela: ~R$ 1.688/mês
- Total pago: R$ 101.280
- Juros totais: R$ 37.280

**Diferença**: +R$ 266/mês (+18.7%)

## Correções Aplicadas

### 1. TCOCalculator - Valor Padrão

**Arquivo**: `platform/backend/services/tco_calculator.py`

**ANTES**:
```python
assumptions: Dict[str, Any] = {
    "annual_interest_rate": 12.0,
}
```

**DEPOIS**:
```python
assumptions: Dict[str, Any] = {
    "annual_interest_rate": 24.0,  # 24% a.a. (2% a.m.) - média mercado 2025
}
```

### 2. TCOCalculator - Parâmetro Default

**ANTES**:
```python
def __init__(
    self,
    annual_interest_rate: float = 0.12,
):
```

**DEPOIS**:
```python
def __init__(
    self,
    annual_interest_rate: float = 0.24,  # 24% a.a. (2% a.m.)
):
```

### 3. UnifiedRecommendationEngine

**Arquivo**: `platform/backend/services/unified_recommendation_engine.py`

**ANTES**:
```python
TCOCalculator(
    annual_interest_rate=0.12,
)
```

**DEPOIS**:
```python
TCOCalculator(
    annual_interest_rate=0.24,  # 24% a.a. (2% a.m.) - média mercado 2025
)
```

### 4. Validação

**ANTES**:
```python
if monthly_rate < 0.005 or monthly_rate > 0.05:
    annual_interest_rate = 0.12  # Default 12% ao ano (1% ao mês)
```

**DEPOIS**:
```python
if monthly_rate < 0.005 or monthly_rate > 0.05:
    annual_interest_rate = 0.24  # Default 24% ao ano (2% ao mês)
```

### 5. Teste Atualizado

**Arquivo**: `platform/backend/tests/test_financial_models.py`

**ANTES**:
```python
assert tco.assumptions["annual_interest_rate"] == 12.0
```

**DEPOIS**:
```python
assert tco.assumptions["annual_interest_rate"] == 24.0  # Atualizado para 24% a.a.
```

## Impacto no Usuário

### Custo Mensal Estimado

**Antes (subestimado)**:
- Financiamento: R$ 1.422/mês
- Combustível: R$ 170/mês
- Manutenção: R$ 200/mês
- Seguro: R$ 250/mês
- IPVA: R$ 100/mês
- **Total**: R$ 2.142/mês ❌

**Depois (realista)**:
- Financiamento: R$ 1.688/mês (+R$ 266)
- Combustível: R$ 178/mês (gasolina atualizada)
- Manutenção: R$ 200/mês
- Seguro: R$ 250/mês
- IPVA: R$ 100/mês
- **Total**: R$ 2.416/mês ✅

**Diferença**: +R$ 274/mês (+12.8%)

### Benefício

Agora o usuário tem uma **estimativa realista** do custo mensal, evitando surpresas desagradáveis ao contratar o financiamento.

## Transparência

O sistema já mostra a taxa de juros nas premissas do cálculo:

```
Premissas do cálculo:
- Taxa de juros: 24.0% a.a.
```

Usuário pode ver exatamente qual taxa está sendo usada.

## Futuras Melhorias

### Variação por Perfil de Crédito

Implementar taxas diferentes baseadas no perfil:

```python
INTEREST_RATES = {
    "excellent": 0.18,  # 18% a.a. (1.5% a.m.)
    "good": 0.24,       # 24% a.a. (2% a.m.)
    "fair": 0.30,       # 30% a.a. (2.5% a.m.)
}
```

### Variação por Tipo de Veículo

- Veículos novos: 15-20% a.a.
- Veículos seminovos (até 3 anos): 20-24% a.a.
- Veículos usados (3-10 anos): 24-30% a.a.

### Integração com APIs Bancárias

Buscar taxas reais em tempo real de:
- Banco Central
- Bancos parceiros
- Financeiras

## Arquivos Modificados

1. `platform/backend/services/tco_calculator.py`
   - Valor padrão: 12% → 24% a.a.
   - Parâmetro default: 0.12 → 0.24
   - Validação fallback: 0.12 → 0.24

2. `platform/backend/services/unified_recommendation_engine.py`
   - Taxa na criação do TCOCalculator: 0.12 → 0.24

3. `platform/backend/tests/test_financial_models.py`
   - Teste atualizado: 12.0 → 24.0

## Referências

- Banco Central do Brasil: https://www.bcb.gov.br/
- Taxas médias de financiamento de veículos (2025)
- Pesquisa de mercado: Bancos e financeiras

## Data
2025-11-06
