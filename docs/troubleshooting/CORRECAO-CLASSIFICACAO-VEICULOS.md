# Correção de Classificação de Veículos

**Data:** 30 de outubro de 2025  
**Problema:** Motos sendo classificadas como carros e aparecendo em buscas de veículos

## Problema Identificado

Ao fazer uma busca filtrando a faixa de valor de R$ 10.000 a R$ 15.000, uma moto (Yamaha Neo Automatic) foi retornada, classificada incorretamente como "Hatch".

### Veículos Mal Classificados

Foram identificados **5 veículos** com classificação incorreta no estoque da RobustCar:

1. **Yamaha Neo Automatic** - Classificada como "Hatch" → Deveria ser "Moto"
2. **Chevrolet Onix Mt** (2x) - Classificados como "Moto" → Deveriam ser "Hatch"
3. **Toyota Prius Hybrid** - Falso positivo (detectado mas não era problema real)
4. **Mitsubishi ASX CVT** - Falso positivo (detectado mas não era problema real)

## Solução Implementada

### 1. Melhorias no Classificador (`car_classifier.py`)

**Antes:**
- Detecção básica de motos por palavras-chave
- Falsos positivos: "MT" (Manual Transmission) e "CVT" eram confundidos com modelos de moto

**Depois:**
- ✅ Detecção por marca (Yamaha, Kawasaki, etc. só fazem motos no Brasil)
- ✅ Verificação de contexto (Hybrid, CVT, Turbo indicam carro)
- ✅ Padrões específicos de modelos de moto (CB, XTZ, Neo, Ninja, etc.)
- ✅ Novo parâmetro `marca` no método `classify()`

### 2. Script de Correção Automática

Criado `scripts/fix_misclassified_vehicles.py` que:
- Identifica motos classificadas como carros
- Identifica carros classificados como motos
- Aplica correções automáticas
- Define `disponivel=False` para motos (não devem aparecer em buscas de carros)

### 3. Scripts de Validação

**`scripts/test_classification.py`**
- 14 casos de teste cobrindo motos e carros
- Testa edge cases (MT, CVT, Hybrid)
- 100% de sucesso após correções

**`scripts/validate_all_vehicles.py`**
- Valida todos os estoques (RobustCar, AutoCenter, CarPlus)
- Identifica problemas de classificação
- Verifica motos com `disponivel=True`

## Resultados

### Antes da Correção
- ❌ 3 motos classificadas como carros
- ❌ 2 carros classificados como motos
- ❌ 1 moto aparecendo em busca de carros (R$ 10k-15k)

### Depois da Correção
- ✅ 129 veículos validados
- ✅ 127 carros corretamente classificados
- ✅ 2 motos corretamente classificadas
- ✅ 0 problemas encontrados
- ✅ Motos não aparecem mais em buscas de carros

## Testes Implementados

### Casos de Teste de Motos
```python
✅ Yamaha XTZ 250 → Moto
✅ Yamaha Neo (scooter) → Moto
✅ Honda CB 500 → Moto
✅ Kawasaki Ninja → Moto
```

### Casos de Teste de Carros
```python
✅ Chevrolet Onix MT → Hatch (não Moto)
✅ Toyota Prius Hybrid → Hatch (não Moto)
✅ Mitsubishi ASX CVT → SUV (não Moto)
✅ Honda Civic → Sedan (não confundir com Honda motos)
✅ Honda Fit → Hatch (não confundir com Honda motos)
```

### Casos de Teste de Categorias
```python
✅ Chevrolet Tracker → SUV
✅ Toyota Corolla → Sedan
✅ Fiat Strada → Pickup
✅ Volkswagen Gol → Hatch
✅ Renault Kwid → Compacto
```

## Regras de Classificação

### Motos (Prioridade 1)
1. **Marca exclusiva de motos** (Yamaha, Kawasaki, Suzuki, etc.)
2. **Palavras-chave** (moto, motorcycle, scooter, etc.)
3. **Modelos específicos** (CB, XTZ, Neo, Ninja, etc.)

### Carros (Prioridade 2)
1. **Indicadores de carro** (Hybrid, CVT, Turbo, Flex)
2. **Modelos conhecidos** (Onix, Civic, Tracker, etc.)
3. **Categorias** (SUV, Sedan, Pickup, Hatch, Compacto, Van)

### Regra Especial
- **MT** e **CVT** no nome NÃO significam moto
  - MT = Manual Transmission (câmbio manual)
  - CVT = Continuously Variable Transmission (câmbio automático)

## Prevenção de Problemas Futuros

### 1. Validação Automática
Execute periodicamente:
```bash
python platform/backend/scripts/validate_all_vehicles.py
```

### 2. Testes Antes de Deploy
```bash
python platform/backend/scripts/test_classification.py
```

### 3. Correção Automática
Se problemas forem encontrados:
```bash
python platform/backend/scripts/fix_misclassified_vehicles.py
```

## Arquivos Modificados

### Código
- `platform/backend/services/car_classifier.py` - Melhorias no classificador
- `platform/backend/data/robustcar_estoque.json` - 3 veículos corrigidos

### Scripts Criados
- `platform/backend/scripts/fix_misclassified_vehicles.py` - Correção automática
- `platform/backend/scripts/test_classification.py` - Testes de classificação
- `platform/backend/scripts/validate_all_vehicles.py` - Validação de estoques
- `platform/backend/scripts/fix_vehicle_classification.py` - Script de análise detalhada

### Testes
- `platform/backend/tests/test_car_classification.py` - Suite completa de testes

### Documentação
- `docs/troubleshooting/CORRECAO-CLASSIFICACAO-VEICULOS.md` - Este documento

## Lições Aprendidas

1. **Contexto é importante**: "MT" pode ser moto ou Manual Transmission
2. **Marcas ajudam**: Yamaha no Brasil só faz motos
3. **Validação contínua**: Scripts de validação previnem regressões
4. **Testes são essenciais**: 14 casos de teste cobrem edge cases
5. **Disponibilidade**: Motos devem ter `disponivel=False` para não aparecer em buscas de carros

## Próximos Passos

1. ✅ Integrar validação no CI/CD
2. ✅ Adicionar testes ao pipeline de deploy
3. ✅ Documentar regras de classificação
4. ⏳ Considerar ML para classificação futura (quando houver mais dados)

## Contato

Para dúvidas ou problemas relacionados à classificação de veículos, consulte:
- Este documento
- `platform/backend/services/car_classifier.py` (código fonte)
- `platform/backend/tests/test_car_classification.py` (testes)
