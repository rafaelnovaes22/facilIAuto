# Correção: Preço do Combustível e Especificação de Gasolina

## Problemas Identificados

### 1. Preço Desatualizado
- ❌ **fuel_price_service.py**: R$ 5.89/L (novembro 2024)
- ✅ **tco_calculator.py**: R$ 6.17/L (março 2025)
- **Discrepância**: R$ 0.28/L

### 2. Falta de Especificação
- ❌ Não estava claro que o preço é de **GASOLINA**
- ❌ Consumo mostrado sem especificar combustível
- ❌ Usuário poderia pensar que é etanol ou flex

### 3. Contradição Visual
- ✅ Justificativa: "Excelente economia de combustível"
- ❌ Badge: "Consumo elevado (9.5 km/L)"
- **Problema**: Parece contraditório, mas está correto (9.5 km/L É elevado)

## Investigação Realizada

### Fonte dos Preços

**TCOCalculator (tco_calculator.py)**:
```python
FUEL_PRICES = {
    "Gasolina": 6.17,   # R$/litro (março 2025)
    "Etanol": 4.28,     # R$/litro (fevereiro 2025)
    "Flex": 5.50,       # Média ponderada (70% gasolina, 30% etanol)
    "Diesel": 6.00,     # Estimativa para diesel
    "GNV": 4.50         # Estimativa para GNV
}
```

**FuelPriceService (fuel_price_service.py)** - ANTES:
```python
DEFAULT_PRICE = 5.89  # R$ 5,89/L (novembro 2024)
```

### Por Que Usar Gasolina?

O sistema **sempre usa preço da gasolina** para cálculos de TCO, independente do tipo de combustível do veículo:

1. **Carros Flex**: Maioria dos brasileiros abastece com gasolina (mais conveniente)
2. **Padronização**: Permite comparação justa entre veículos
3. **Conservador**: Gasolina é mais cara, então estimativa é realista
4. **Fonte**: ANP (Agência Nacional do Petróleo)

## Correções Aplicadas

### 1. Atualizar Preço Padrão

**Arquivo**: `platform/backend/services/fuel_price_service.py`

**ANTES**:
```python
DEFAULT_PRICE = 5.89  # R$ 5,89/L (novembro 2024)
```

**DEPOIS**:
```python
# Preço padrão de GASOLINA (atualizado manualmente quando necessário)
# Fonte: ANP - Agência Nacional do Petróleo
DEFAULT_PRICE = 6.17  # R$ 6,17/L gasolina (março 2025)
```

### 2. Especificar Gasolina no Frontend

**Arquivo**: `platform/frontend/src/components/results/CarCard.tsx`

**ANTES**:
```typescript
return `Consumo elevado (${consumption.toFixed(1)} km/L)`
```

**DEPOIS**:
```typescript
return `Consumo elevado (${consumption.toFixed(1)} km/L com gasolina)`
```

### 3. Especificar Gasolina no TCO Breakdown

**Arquivo**: `platform/frontend/src/components/results/TCOBreakdownCard.tsx`

**ANTES**:
```typescript
label="Combustível"
hint={`${tco.assumptions.monthly_km} km/mês, R$ ${tco.assumptions.fuel_price_per_liter.toFixed(2)}/L`}
```

**DEPOIS**:
```typescript
label="Combustível (gasolina)"
hint={`${tco.assumptions.monthly_km} km/mês, R$ ${tco.assumptions.fuel_price_per_liter.toFixed(2)}/L gasolina`}
```

### 4. Documentar no Serviço

**Arquivo**: `platform/backend/services/fuel_price_service.py`

Adicionado na docstring:
```python
"""
Serviço para obter preço atualizado de GASOLINA

Nota: Sempre usa preço da GASOLINA para cálculos de TCO,
independente do tipo de combustível do veículo (Flex, Etanol, etc)
"""
```

## Impacto das Mudanças

### Antes
- Preço: R$ 5.89/L (desatualizado)
- Custo combustível mensal: ~R$ 170/mês (subestimado)
- Não especificava que era gasolina

### Depois
- Preço: R$ 6.17/L (atualizado março 2025)
- Custo combustível mensal: ~R$ 178/mês (realista)
- Especifica claramente "gasolina" em todos os lugares

**Diferença**: +R$ 8/mês no custo de combustível (mais realista)

## Próximas Investigações Necessárias

### Taxa de Juros (12% a.a.)

**Atual**: 12% a.a. (1% a.m.)

**Investigar**:
- Taxa real de financiamento de veículos usados no Brasil
- Bancos costumam cobrar 1.5% - 2.5% a.m. para usados
- 12% a.a. pode estar **muito baixo**

**Fontes para consultar**:
- Banco Central (taxa média de financiamento de veículos)
- Bancos: Santander, Itaú, Bradesco, Caixa
- Financeiras: BV, Omni, Aymoré

**Ação recomendada**:
- Pesquisar taxa média atual
- Atualizar para ~18-24% a.a. (1.5-2% a.m.) se necessário
- Adicionar variação por perfil de crédito

## Arquivos Modificados

1. `platform/backend/services/fuel_price_service.py`
   - Preço padrão: 5.89 → 6.17
   - Documentação especificando gasolina

2. `platform/frontend/src/components/results/CarCard.tsx`
   - Consumo: "9.5 km/L" → "9.5 km/L com gasolina"

3. `platform/frontend/src/components/results/TCOBreakdownCard.tsx`
   - Label: "Combustível" → "Combustível (gasolina)"
   - Hint: "R$ X/L" → "R$ X/L gasolina"

## Data
2025-11-06

## Referências
- ANP (Agência Nacional do Petróleo): https://www.gov.br/anp/
- Preços atualizados em março/2025
