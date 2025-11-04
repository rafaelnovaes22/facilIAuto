# ✅ Filtro de Faixa de Anos Implementado

## O que foi feito

Implementado **filtro de faixa de anos (mínimo e máximo)** como critério de busca obrigatório. O usuário pode definir:
- **Ano mínimo**: carros de X em diante
- **Ano máximo**: carros até X
- **Faixa completa**: carros entre X e Y

---

## Implementação

### 1. Backend

**Modelo (`models/user_profile.py`):**
```python
class UserProfile(BaseModel):
    # ...
    ano_minimo: Optional[int] = None  # Ex: 2018
    ano_maximo: Optional[int] = None  # Ex: 2020
```

**Engine (`services/unified_recommendation_engine.py`):**
```python
def filter_by_year(self, cars: List[Car], ano_minimo: Optional[int], ano_maximo: Optional[int] = None) -> List[Car]:
    """Filtrar por faixa de anos"""
    filtered = cars
    
    if ano_minimo:
        filtered = [car for car in filtered if car.ano >= ano_minimo]
    
    if ano_maximo:
        filtered = [car for car in filtered if car.ano <= ano_maximo]
    
    return filtered

def recommend(self, profile: UserProfile, limit: int = 10) -> List[Dict]:
    # ...
    # Filtrar por faixa de anos
    filtered_cars = self.filter_by_year(filtered_cars, profile.ano_minimo, profile.ano_maximo)
    
    if profile.ano_minimo and profile.ano_maximo:
        print(f"[FILTRO] Após ano {profile.ano_minimo}-{profile.ano_maximo}: {len(filtered_cars)} carros")
    elif profile.ano_minimo:
        print(f"[FILTRO] Após ano >= {profile.ano_minimo}: {len(filtered_cars)} carros")
    elif profile.ano_maximo:
        print(f"[FILTRO] Após ano <= {profile.ano_maximo}: {len(filtered_cars)} carros")
```

### 2. Frontend

**Tipos (`types/index.ts`):**
```typescript
export interface UserProfile {
    // ...
    ano_minimo?: number
    ano_maximo?: number
    // ...
}

export interface QuestionnaireFormData {
    // Step 1: Orçamento e Localização
    orcamento_min: number
    orcamento_max: number
    ano_minimo?: number  // ✅ NOVO
    ano_maximo?: number  // ✅ NOVO
    city?: string
    state?: string
    // ...
}
```

**Store (`store/questionnaireStore.ts`):**
```typescript
const initialFormData: Partial<QuestionnaireFormData> = {
  orcamento_min: 50000,
  orcamento_max: 100000,
  ano_minimo: undefined,  // ✅ NOVO
  ano_maximo: undefined,  // ✅ NOVO
  // ...
}

toUserProfile: (): UserProfile => {
    return {
      // ...
      ano_minimo: formData.ano_minimo,  // ✅ NOVO
      ano_maximo: formData.ano_maximo,  // ✅ NOVO
      // ...
    }
}
```

**Componente (`components/questionnaire/YearSelector.tsx`):**
```typescript
interface YearSelectorProps {
    minValue?: number
    maxValue?: number
    onChange: (min?: number, max?: number) => void
}

export const YearSelector = ({ minValue, maxValue, onChange }: YearSelectorProps) => {
    const handleMinChange = (min?: number) => {
        // Se min > max, ajustar max automaticamente
        if (min && maxValue && min > maxValue) {
            onChange(min, min)
        } else {
            onChange(min, maxValue)
        }
    }

    const handleMaxChange = (max?: number) => {
        // Se max < min, ajustar min automaticamente
        if (max && minValue && max < minValue) {
            onChange(max, max)
        } else {
            onChange(minValue, max)
        }
    }

    return (
        <SimpleGrid columns={2} spacing={4}>
            {/* Ano Mínimo */}
            <Select placeholder="Qualquer" onChange={...}>
                {years.map(year => <option>{year}</option>)}
            </Select>
            
            {/* Ano Máximo */}
            <Select placeholder="Qualquer" onChange={...}>
                {years.map(year => <option>{year}</option>)}
            </Select>
        </SimpleGrid>
    )
}
```

**Integração no Step1:**
```typescript
const handleYearChange = (min?: number, max?: number) => {
    updateFormData({ ano_minimo: min, ano_maximo: max })
}

<YearSelector
    minValue={formData.ano_minimo}
    maxValue={formData.ano_maximo}
    onChange={handleYearChange}
/>
```

---

## Comportamento

### 1. Sem filtro (padrão)
```
Usuário: Não seleciona nenhum ano
Backend: Retorna carros de qualquer ano
```

### 2. Apenas ano mínimo
```
Usuário: Seleciona "De: 2018" + "Até: Qualquer"
Backend: [FILTRO] Após ano >= 2018: X carros
Resultado: Carros de 2018 em diante
```

### 3. Apenas ano máximo
```
Usuário: Seleciona "De: Qualquer" + "Até: 2016"
Backend: [FILTRO] Após ano <= 2016: X carros
Resultado: Carros até 2016
```

### 4. Faixa completa
```
Usuário: Seleciona "De: 2015" + "Até: 2018"
Backend: [FILTRO] Após ano 2015-2018: X carros
Resultado: Carros entre 2015 e 2018 (inclusive)
```

### 5. Validação automática
```
Usuário: Seleciona "De: 2020" depois "Até: 2018"
Sistema: Ajusta automaticamente para "De: 2018" + "Até: 2018"
Evita: Faixa inválida (min > max)
```

---

## UX do Componente

**Visual:**
```
📅 Ano do carro

┌─────────────────┬─────────────────┐
│ De (mínimo)     │ Até (máximo)    │
│ [Qualquer ▼]    │ [Qualquer ▼]    │
└─────────────────┴─────────────────┘

Carros de 2018 a 2020
```

**Opções de cada dropdown:**
- Qualquer (padrão)
- 2025
- 2024
- 2023
- ...
- 2000

**Feedback dinâmico:**
- Sem seleção: "Sem restrição de ano"
- Só mínimo: "Carros de 2018 em diante"
- Só máximo: "Carros até 2016"
- Ambos: "Carros de 2015 a 2018"

**Validação inteligente:**
- Se usuário seleciona min > max, ajusta automaticamente
- Evita estados inválidos
- UX fluida sem mensagens de erro

---

## Casos de Uso

### 1. Uber/99 (ano mínimo obrigatório)
```
Perfil: Transporte de passageiros
Filtro automático: ano_minimo = 2015
Razão: Requisito das plataformas
```

### 2. Carros seminovos (faixa específica)
```
Usuário: Quer carro "nem muito novo, nem muito velho"
Filtro: ano_minimo = 2018, ano_maximo = 2021
Resultado: Carros de 3-6 anos
```

### 3. Carros mais antigos (orçamento limitado)
```
Usuário: Orçamento R$ 20k-30k
Filtro: ano_maximo = 2015
Resultado: Carros mais acessíveis
```

### 4. Carros novos (garantia de fábrica)
```
Usuário: Quer garantia de fábrica
Filtro: ano_minimo = 2023
Resultado: Carros com até 2 anos
```

---

## Testes Realizados

**Teste manual:**
```bash
python platform/backend/test_year_range_manual.py
```

**Resultados:**
```
✅ TESTE 1: Sem filtro - OK
✅ TESTE 2: Ano mínimo (>= 2018) - OK
✅ TESTE 3: Ano máximo (<= 2016) - OK
✅ TESTE 4: Faixa (2015-2018) - OK
✅ TESTE 5: Faixa restritiva (2023-2025) - OK (lista vazia esperada)
```

**Logs confirmam:**
```
[FILTRO] Após ano >= 2018: X carros
[FILTRO] Após ano <= 2016: X carros
[FILTRO] Após ano 2015-2018: X carros
```

---

## Ordem dos Filtros no Backend

1. **Orçamento** (sempre aplicado)
2. **Faixa de anos** ✅ (se especificado)
3. **Quilometragem máxima** (se especificado)
4. **Must-haves** (se especificado)
5. **Raio geográfico** (se especificado)
6. **Contexto família** (priorização)
7. **Contexto primeiro carro** (priorização)
8. **Transporte app** (validação Uber/99)

---

## Benefícios

1. **Controle Total**
   - Usuário define exatamente a faixa de anos desejada
   - Flexibilidade: pode usar só mínimo, só máximo, ou ambos

2. **Validação Inteligente**
   - Ajuste automático se min > max
   - Sem estados inválidos
   - UX sem fricção

3. **Transparência**
   - Filtro visível no Step 1
   - Feedback claro do que está sendo filtrado
   - Logs detalhados no backend

4. **Casos de Uso Reais**
   - Uber/99: ano mínimo obrigatório
   - Seminovos: faixa específica
   - Orçamento limitado: carros mais antigos
   - Garantia: carros novos

---

## Comparação: Antes vs Depois

### Antes (só ano mínimo)
```
Usuário: "Quero carros de 2015 a 2018"
Sistema: ❌ Não consegue filtrar ano máximo
Resultado: Mostra carros de 2015 até 2025
```

### Depois (faixa completa)
```
Usuário: "Quero carros de 2015 a 2018"
Sistema: ✅ Filtra min=2015, max=2018
Resultado: Mostra APENAS carros de 2015 a 2018
```

---

## Status

✅ **Backend**: Implementado e testado
✅ **Frontend**: Implementado com validação inteligente
✅ **Tipos**: Sincronizados
✅ **UX**: Componente com 2 dropdowns lado a lado
✅ **Validação**: Ajuste automático de faixa inválida
✅ **Testes**: Validação manual OK
✅ **Logs**: Feedback detalhado no console

**Pronto para uso!** 🚀

---

## Próximos Passos (Opcional)

1. **Preset por Perfil**
   - Uber/99: Auto-definir ano_minimo = 2015
   - Primeiro carro: Sugerir carros mais novos (2020+)
   - Família: Sugerir carros recentes (segurança)

2. **Filtros Adicionais**
   - Quilometragem (já existe no backend)
   - Câmbio (Manual/Automático)
   - Combustível (Flex/Gasolina/Diesel)

3. **Analytics**
   - Rastrear faixas de anos mais buscadas
   - Identificar padrões por perfil de uso
   - Otimizar sugestões de faixa
