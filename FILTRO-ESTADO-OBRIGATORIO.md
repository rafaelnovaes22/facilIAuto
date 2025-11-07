# Filtro de Estado: De Priorização para Obrigatório

## Problema Identificado

O sistema estava **priorizando** carros por localização, mas não **filtrando**. Isso causava:

- ❌ Usuário seleciona "AC" (Acre) → Sistema mostra carros de SP
- ❌ Usuário seleciona "RJ" → Sistema mostra carros de todos os estados
- ❌ Mensagem "Nenhuma concessionária disponível em X" aparecia mesmo quando havia carros de outros estados

## Comportamento Anterior

### Quando usuário especificava estado:
- Sistema **priorizava** carros daquele estado (colocava no topo)
- Mas **mostrava carros de outros estados** também
- Mensagem de erro aparecia incorretamente

### Quando usuário NÃO especificava estado:
- Sistema mostrava todos os carros (correto ✅)

## Novo Comportamento

### Quando usuário especifica estado:
- Sistema **filtra** e mostra **APENAS** carros daquele estado
- Se não houver carros naquele estado → Mensagem clara: "Nenhuma concessionária disponível em {estado}"
- Sugestão: "Tente expandir seu orçamento ou selecionar um estado próximo"

### Quando usuário NÃO especifica estado:
- Sistema mostra **todos os carros** de qualquer localização
- Sem filtro geográfico aplicado
- Se não houver carros → Mensagem genérica sobre orçamento/filtros

## Alterações Técnicas

### 1. Novo Método: `filter_by_state()`

**Arquivo**: `platform/backend/services/unified_recommendation_engine.py`

```python
def filter_by_state(self, cars: List[Car], user_state: Optional[str]) -> List[Car]:
    """
    Filtrar carros por estado (hard constraint se especificado)
    
    Se o usuário especificar um estado, retorna APENAS carros daquele estado.
    Se não especificar, retorna todos os carros.
    """
    if not user_state:
        # Usuário não especificou estado - retornar todos
        return cars
    
    # Filtrar apenas carros do estado especificado
    filtered = [
        car for car in cars 
        if car.dealership_state and car.dealership_state.upper() == user_state.upper()
    ]
    
    print(f"[FILTRO] Estado {user_state}: {len(filtered)} carros (de {len(cars)} totais)")
    
    return filtered
```

### 2. Aplicação do Filtro no `recommend()`

**Posição**: Após `filter_by_must_haves`, antes de `filter_by_radius`

```python
# 4.5. 📍 Filtrar por estado (se especificado)
filtered_cars = self.filter_by_state(filtered_cars, profile.state)
```

### 3. Lógica de Mensagem na API

**Arquivo**: `platform/backend/api/main.py`

```python
if len(recommendations) == 0:
    # Verificar se o usuário especificou localização
    if profile.state:
        # Usuário especificou estado mas não há carros disponíveis
        return {
            "message": f"Nenhuma concessionária disponível em {profile.state}",
            "suggestion": "Tente expandir seu orçamento ou selecionar um estado próximo"
        }
    else:
        # Usuário NÃO especificou estado - não há carros em NENHUM lugar
        return {
            "message": "Nenhum carro encontrado com os filtros selecionados",
            "suggestion": "Tente aumentar seu orçamento ou ajustar suas preferências"
        }
```

## Método `prioritize_by_location()` Mantido

O método `prioritize_by_location()` foi **mantido** porque:
- Ainda é usado quando `profile.priorizar_proximas = True`
- Ordena carros por proximidade **dentro do mesmo estado**
- Útil para cidades grandes com múltiplas concessionárias

## Exemplos de Uso

### Exemplo 1: Usuário em SP
```json
{
  "state": "SP",
  "city": "São Paulo",
  "orcamento_min": 50000,
  "orcamento_max": 80000
}
```
**Resultado**: Apenas carros de concessionárias em SP

### Exemplo 2: Usuário sem estado
```json
{
  "orcamento_min": 50000,
  "orcamento_max": 80000
}
```
**Resultado**: Carros de TODOS os estados

### Exemplo 3: Usuário em AC (sem concessionárias)
```json
{
  "state": "AC",
  "city": "Rio Branco",
  "orcamento_min": 50000,
  "orcamento_max": 80000
}
```
**Resultado**: 
```json
{
  "total_recommendations": 0,
  "message": "Nenhuma concessionária disponível em AC",
  "suggestion": "Tente expandir seu orçamento ou selecionar um estado próximo"
}
```

## Impacto no Frontend

### LocationSelector (já está correto)
- Campo de estado é **opcional** (placeholder="Selecione")
- Texto: "Isso nos ajuda a priorizar concessionárias próximas (opcional)"
- Usuário pode deixar vazio

### Validação do Questionário
- Step 1 **NÃO exige** estado para avançar ✅
- Sistema funciona com ou sem estado ✅

## Testes

### Teste 1: Com Estado (SP)
```bash
python test_location_logic.py
```
**Esperado**: Apenas carros de SP

### Teste 2: Sem Estado
```bash
python test_location_logic.py
```
**Esperado**: Carros de todos os estados

### Teste 3: Estado Inexistente (AC)
```bash
python test_location_logic.py
```
**Esperado**: Mensagem "Nenhuma concessionária disponível em AC"

## Arquivos Modificados

1. `platform/backend/services/unified_recommendation_engine.py`
   - Novo método `filter_by_state()`
   - Aplicação do filtro no `recommend()`

2. `platform/backend/api/main.py`
   - Lógica de mensagem diferenciada (com/sem estado)

3. `test_location_logic.py`
   - Script de teste para validar comportamento

## Data
2025-11-06
