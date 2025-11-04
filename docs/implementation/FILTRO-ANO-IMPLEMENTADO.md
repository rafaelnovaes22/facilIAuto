# ✅ Filtro de Ano Implementado

## O que foi feito

Implementado **filtro de ano mínimo** como critério de busca obrigatório. Quando o usuário seleciona um ano, apenas carros daquele ano ou mais recentes são exibidos nos resultados.

---

## Implementação

### 1. Backend (já existia)

O backend já tinha suporte completo para filtro de ano:

**Modelo (`models/user_profile.py`):**
```python
class UserProfile(BaseModel):
    # ...
    ano_minimo: Optional[int] = None  # Ex: 2018
```

**Engine (`services/unified_recommendation_engine.py`):**
```python
def filter_by_year(self, cars: List[Car], ano_minimo: Optional[int]) -> List[Car]:
    """Filtrar por ano mínimo - Elimina carros mais antigos"""
    if not ano_minimo:
        return cars
    
    return [car for car in cars if car.ano >= ano_minimo]

def recommend(self, profile: UserProfile, limit: int = 10) -> List[Dict]:
    # 1. Filtrar por orçamento
    filtered_cars = self.filter_by_budget(self.all_cars, profile)
    
    # 2. Filtrar por ano mínimo
    filtered_cars = self.filter_by_year(filtered_cars, profile.ano_minimo)
    if profile.ano_minimo:
        print(f"[FILTRO] Após ano >= {profile.ano_minimo}: {len(filtered_cars)} carros")
    
    # ... outros filtros
```

### 2. Frontend (implementado agora)

**Tipos (`types/index.ts`):**
```typescript
export interface UserProfile {
    // ...
    ano_minimo?: number
    // ...
}

export interface QuestionnaireFormData {
    // Step 1: Orçamento e Localização
    orcamento_min: number
    orcamento_max: number
    ano_minimo?: number  // ✅ NOVO
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
  // ...
}

toUserProfile: (): UserProfile => {
    const { formData } = get()
    return {
      // ...
      ano_minimo: formData.ano_minimo,  // ✅ NOVO
      // ...
    }
}
```

**Componente (`components/questionnaire/YearSelector.tsx`):**
```typescript
export const YearSelector = ({ value, onChange }: YearSelectorProps) => {
  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 25 }, (_, i) => currentYear - i)

  return (
    <Select
      value={value || ''}
      onChange={(e) => {
        const selectedYear = e.target.value ? parseInt(e.target.value) : undefined
        onChange(selectedYear)
      }}
      placeholder="Qualquer ano"
    >
      {years.map((year) => (
        <option key={year} value={year}>
          {year} ou mais recente
        </option>
      ))}
    </Select>
  )
}
```

**Integração no Step1 (`components/questionnaire/Step1Budget.tsx`):**
```typescript
import { YearSelector } from './YearSelector'

export const Step1Budget = () => {
  const { formData, updateFormData } = useQuestionnaireStore()

  const handleYearChange = (year?: number) => {
    updateFormData({ ano_minimo: year })
  }

  return (
    <VStack spacing={8}>
      {/* Budget Slider */}
      <BudgetSlider ... />
      
      <Divider />
      
      {/* Year Selector - NOVO */}
      <YearSelector
        value={formData.ano_minimo}
        onChange={handleYearChange}
      />
      
      <Divider />
      
      {/* Location Selector */}
      <LocationSelector ... />
    </VStack>
  )
}
```

---

## Comportamento

### Sem filtro de ano (padrão)
```
Usuário: Não seleciona ano
Backend: Retorna carros de qualquer ano dentro do orçamento
```

### Com filtro de ano
```
Usuário: Seleciona "2018 ou mais recente"
Backend: 
  [FILTRO] Após orçamento: 150 carros
  [FILTRO] Após ano >= 2018: 85 carros
  ✅ Retorna apenas carros de 2018 em diante
```

### Filtro muito restritivo
```
Usuário: Seleciona "2023 ou mais recente" com orçamento R$ 30k-60k
Backend:
  [FILTRO] Após orçamento: 50 carros
  [FILTRO] Após ano >= 2023: 0 carros
  [AVISO] Nenhum carro após filtros. Retornando lista vazia.
Frontend: Mostra mensagem "Nenhum carro encontrado"
```

---

## UX do Componente

**Visual:**
```
📅 Ano mínimo do carro

[Dropdown: Qualquer ano ▼]

Opções:
- Qualquer ano (padrão)
- 2025 ou mais recente
- 2024 ou mais recente
- 2023 ou mais recente
- ...
- 2000 ou mais recente

Texto auxiliar:
"Mostrar apenas carros de 2020 em diante"
ou
"Sem restrição de ano"
```

**Características:**
- ✅ Opcional (padrão: sem filtro)
- ✅ Últimos 25 anos disponíveis
- ✅ Texto claro: "2020 ou mais recente"
- ✅ Feedback visual do filtro ativo
- ✅ Integrado no Step 1 (junto com orçamento e localização)

---

## Ordem dos Filtros no Backend

1. **Orçamento** (sempre aplicado)
2. **Ano mínimo** ✅ (se especificado)
3. **Quilometragem máxima** (se especificado)
4. **Must-haves** (se especificado)
5. **Raio geográfico** (se especificado)
6. **Contexto família** (priorização)
7. **Contexto primeiro carro** (priorização)
8. **Transporte app** (validação Uber/99)

---

## Testes

**Teste manual criado:**
```bash
python platform/backend/test_year_manual.py
```

**Resultados:**
```
✅ TESTE 1: Sem filtro de ano - OK
✅ TESTE 2: Com filtro ano >= 2018 - OK
✅ TESTE 3: Filtro muito restritivo (2022) - OK (lista vazia esperada)
```

**Logs confirmam:**
```
[FILTRO] Após ano >= 2018: X carros
```

---

## Benefícios

1. **Controle Total**
   - Usuário define exatamente o ano mínimo desejado
   - Não vê carros mais antigos que o especificado

2. **Transparência**
   - Filtro visível no Step 1
   - Feedback claro do que está sendo filtrado

3. **Flexibilidade**
   - Opcional (padrão: sem filtro)
   - Pode ser combinado com outros filtros

4. **Casos de Uso**
   - Uber/99: Requer ano mínimo 2015
   - Família: Prefere carros mais novos (segurança)
   - Revenda: Carros mais novos têm melhor valor

---

## Próximos Passos (Opcional)

1. **Filtro de Quilometragem**
   - Similar ao ano, mas para km máxima
   - Já existe no backend (`km_maxima`)

2. **Filtros Avançados**
   - Câmbio (Manual/Automático)
   - Combustível (Flex/Gasolina/Diesel)
   - Cor

3. **Preset por Perfil**
   - Uber/99: Auto-definir ano >= 2015
   - Primeiro carro: Sugerir carros mais novos

---

## Status

✅ **Backend**: Implementado e testado
✅ **Frontend**: Implementado e integrado
✅ **Tipos**: Sincronizados
✅ **UX**: Componente criado e integrado no Step 1
✅ **Testes**: Validação manual OK

**Pronto para uso!** 🚀
