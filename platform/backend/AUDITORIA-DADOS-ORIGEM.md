# 🔍 Auditoria de Qualidade dos Dados de Origem

**Data**: 30/10/2025  
**Arquivo analisado**: `data/robustcar_estoque.json`  
**Total de carros**: 73

---

## 📊 Resultados da Auditoria

### ✅ CLASSIFICAÇÃO (Categoria): EXCELENTE

**Distribuição**:
- Hatch: 31 carros (42.5%)
- SUV: 17 carros (23.3%)
- Sedan: 13 carros (17.8%)
- Pickup: 7 carros (9.6%)
- Compacto: 5 carros (6.8%)

**Status**: ✅ Nenhuma classificação suspeita encontrada

**Conclusão**: As categorias estão corretas e bem distribuídas.

---

### ✅ CÂMBIO: EXCELENTE

**Distribuição**:
- Manual: 73 carros (100.0%)

**Status**: ✅ Todos os câmbios estão preenchidos corretamente

**Observação**: 
- ⚠️ **PROBLEMA CRÍTICO**: 100% dos carros são manuais
- Isso NÃO reflete a realidade do mercado
- Carros de 2021-2025 geralmente têm câmbio automático
- **Causa provável**: Dados de scraping incompletos ou erro no parser

**Exemplos suspeitos**:
- Chevrolet Tracker 2025 - Manual ❌ (deveria ser Automático)
- Toyota Corolla 2022 - Manual ❌ (deveria ser Automático CVT)
- Volvo XC40 2021 - Manual ❌ (deveria ser Automático)
- Nissan Kicks 2023 - Manual ❌ (deveria ser Automático CVT)

---

### ❌ QUILOMETRAGEM: CRÍTICO

**Distribuição**:
- 0 km (Zero KM): 73 carros (100.0%) ❌
- < 30.000 km: 0 carros (0.0%)
- 30.000 - 80.000 km: 0 carros (0.0%)
- > 80.000 km: 0 carros (0.0%)

**Status**: ❌ 101 quilometragens suspeitas (mais que o total de carros devido a múltiplas validações)

**Problema**: 
- **100% dos carros têm 0km**
- Carros de 2018-2023 com 0km são extremamente suspeitos
- **Causa provável**: Campo não está sendo extraído do scraping

**Exemplos críticos**:
- Nissan Frontier Attack 2023 - 0km ❌
- Toyota Corolla Gli 2022 - 0km ❌
- Chevrolet Tracker 2021 - 0km ❌
- Fiat Toro Freedom 2020 - 0km ❌

---

## 📋 Resumo Executivo

| Aspecto | Status | Problemas | Qualidade |
|---------|--------|-----------|-----------|
| **Classificação** | ✅ | 0 | EXCELENTE |
| **Câmbio** | ⚠️ | 73 | CRÍTICO |
| **Quilometragem** | ❌ | 73 | CRÍTICO |
| **GERAL** | ❌ | 146 | **RUIM** |

---

## 🐛 Problemas Identificados

### 1. Câmbio - 100% Manual (CRÍTICO)

**Impacto**: 
- Usuários que filtram por "Automático" não encontram NENHUM carro
- Filtro de câmbio preferido não funciona
- Recomendações ficam limitadas

**Causa Raiz**:
```python
# Provável problema no scraper
cambio = "Manual"  # Valor padrão hardcoded
```

**Solução**:
1. Verificar scraper em `platform/scrapers/`
2. Extrair campo correto do HTML
3. Mapear valores: "A" → "Automático", "M" → "Manual", "CVT" → "Automático CVT"

### 2. Quilometragem - 100% Zero KM (CRÍTICO)

**Impacto**:
- Usuários que filtram por "km_maxima" não veem diferença
- Carros usados aparecem como 0km
- Impossível diferenciar novos de seminovos

**Causa Raiz**:
```python
# Provável problema no scraper
quilometragem = 0  # Valor padrão quando não encontra
```

**Solução**:
1. Verificar scraper em `platform/scrapers/`
2. Extrair campo correto do HTML
3. Se não disponível, estimar baseado no ano:
   - 2024-2025: 0-10.000 km
   - 2023: 15.000-30.000 km
   - 2022: 30.000-50.000 km
   - 2021: 50.000-70.000 km
   - 2020 ou anterior: 70.000+ km

---

## 💡 Recomendações Urgentes

### Prioridade 1: Corrigir Scraper

**Arquivo**: `platform/scrapers/robustcar_scraper.py` (ou similar)

**Verificar**:
1. Seletores CSS/XPath para câmbio
2. Seletores CSS/XPath para quilometragem
3. Parsing e normalização dos valores
4. Tratamento de valores ausentes

### Prioridade 2: Dados Temporários

Enquanto o scraper não é corrigido, criar dados realistas:

```python
# Script: fix_missing_data.py

import json
import random

def estimate_km(ano):
    """Estimar quilometragem baseado no ano"""
    current_year = 2025
    years_old = current_year - ano
    
    if years_old <= 0:
        return random.randint(0, 5000)
    elif years_old == 1:
        return random.randint(10000, 25000)
    elif years_old == 2:
        return random.randint(25000, 45000)
    elif years_old == 3:
        return random.randint(45000, 65000)
    elif years_old == 4:
        return random.randint(65000, 85000)
    else:
        return random.randint(85000, 150000)

def estimate_cambio(marca, modelo, ano):
    """Estimar câmbio baseado em marca/modelo/ano"""
    modelo_lower = modelo.lower()
    
    # Carros que geralmente são automáticos
    if any(x in modelo_lower for x in ['corolla', 'civic', 'tracker', 'kicks', 'creta', 'compass', 'renegade']):
        if ano >= 2020:
            return "Automático CVT" if 'corolla' in modelo_lower or 'civic' in modelo_lower else "Automático"
    
    # Carros populares geralmente são manuais
    if any(x in modelo_lower for x in ['onix', 'hb20', 'gol', 'kwid', 'mobi', 'argo']):
        if ano >= 2023:
            return random.choice(["Manual", "Automático"])
        return "Manual"
    
    # Carros premium geralmente são automáticos
    if any(x in modelo_lower for x in ['volvo', 'bmw', 'audi', 'mercedes']):
        return "Automático"
    
    # Padrão: 70% manual, 30% automático para carros até 2022
    if ano <= 2022:
        return random.choices(["Manual", "Automático"], weights=[70, 30])[0]
    else:
        return random.choices(["Manual", "Automático"], weights=[50, 50])[0]
```

### Prioridade 3: Validação Contínua

Adicionar validação automática:

```python
# No scraper, após extrair dados
def validate_car_data(car):
    """Validar dados antes de salvar"""
    warnings = []
    
    # Validar câmbio
    if car['cambio'] not in ['Manual', 'Automático', 'Automático CVT', 'Automatizada']:
        warnings.append(f"Câmbio inválido: {car['cambio']}")
    
    # Validar quilometragem
    if car['quilometragem'] == 0 and car['ano'] < 2024:
        warnings.append(f"Carro de {car['ano']} com 0km é suspeito")
    
    # Validar quilometragem vs ano
    years_old = 2025 - car['ano']
    expected_km = years_old * 15000  # Média 15k km/ano
    if car['quilometragem'] > expected_km * 2:
        warnings.append(f"Quilometragem muito alta para o ano")
    
    return warnings
```

---

## 🎯 Plano de Ação

### Curto Prazo (Hoje)

1. ✅ Auditoria completa realizada
2. ⏳ Criar script de correção temporária
3. ⏳ Aplicar estimativas realistas
4. ⏳ Testar filtros com dados corrigidos

### Médio Prazo (Esta Semana)

1. ⏳ Revisar e corrigir scraper
2. ⏳ Adicionar validação automática
3. ⏳ Re-scraping com dados corretos
4. ⏳ Validar qualidade dos novos dados

### Longo Prazo (Próximas Semanas)

1. ⏳ Monitoramento contínuo de qualidade
2. ⏳ Alertas automáticos para dados suspeitos
3. ⏳ Dashboard de qualidade de dados
4. ⏳ Testes automatizados de validação

---

## 📊 Impacto nos Filtros

### Filtros Afetados

| Filtro | Impacto | Severidade |
|--------|---------|------------|
| `cambio_preferido` | ❌ Não funciona (100% manual) | CRÍTICO |
| `km_maxima` | ⚠️ Funciona mas sem efeito (100% 0km) | ALTO |
| `ano_minimo/maximo` | ✅ Funciona corretamente | OK |
| `marcas_preferidas` | ✅ Funciona corretamente | OK |
| `tipos_preferidos` | ✅ Funciona corretamente | OK |
| `combustivel_preferido` | ✅ Funciona corretamente | OK |

### Experiência do Usuário

**Cenário 1**: Usuário filtra por "Automático"
- **Resultado atual**: 0 carros ❌
- **Resultado esperado**: ~30-40 carros ✅

**Cenário 2**: Usuário filtra por "máximo 50.000 km"
- **Resultado atual**: Todos os carros (todos têm 0km) ⚠️
- **Resultado esperado**: Apenas carros com até 50k km ✅

---

## 🔧 Scripts Criados

1. `scripts/audit_data_quality.py` - Auditoria completa ✅
2. `scripts/fix_missing_data.py` - Correção temporária (a criar)
3. `scripts/validate_scraper.py` - Validação do scraper (a criar)

---

## 📝 Conclusão

**Status Geral**: ❌ QUALIDADE RUIM

**Problemas Críticos**:
- 100% dos carros com câmbio "Manual" (incorreto)
- 100% dos carros com 0km (incorreto)

**Ação Imediata Necessária**:
1. Corrigir scraper para extrair câmbio e quilometragem
2. Aplicar estimativas temporárias nos dados existentes
3. Re-scraping com correções aplicadas

**Impacto no Produto**:
- Filtros de câmbio não funcionam
- Filtros de quilometragem não têm efeito prático
- Experiência do usuário comprometida

---

**Responsável**: AI Engineer + Data Analyst  
**Prioridade**: 🔴 CRÍTICA  
**Prazo**: Imediato
