# Design Document

## Overview

Este documento descreve o design técnico para corrigir a integração entre a faixa de salário selecionada pelo usuário e o cálculo de TCO no sistema de recomendações. A solução envolve modificações no frontend (React/TypeScript) e validações no backend (Python/FastAPI) para garantir que o `financial_capacity` seja corretamente enviado e processado.

## Architecture

### Current Flow (Broken)

```
User selects salary range
    ↓
formData.faixa_salarial = "5000-8000"
    ↓
toUserProfile() → UserProfile (missing financial_capacity)
    ↓
Backend receives profile WITHOUT financial_capacity
    ↓
TCO calculated but NOT validated against budget
    ↓
fits_budget = null (always)
    ↓
No budget tags shown to user ❌
```

### Fixed Flow

```
User selects salary range
    ↓
formData.faixa_salarial = "5000-8000"
    ↓
toUserProfile() → UserProfile WITH financial_capacity {
    monthly_income_range: "5000-8000",
    max_monthly_tco: 1950,  // (5000+8000)/2 * 0.30
    is_disclosed: true
}
    ↓
Backend receives profile WITH financial_capacity
    ↓
TCO calculated AND validated against max_monthly_tco
    ↓
fits_budget = true/false (based on comparison)
    ↓
Budget tags shown correctly ✅
```

## Components and Interfaces

### 1. Frontend: Salary Range Selector Component

**Location:** `platform/frontend/src/components/questionnaire/SalaryRangeSelector.tsx`

**Purpose:** Novo componente para coletar faixa salarial do usuário

**Interface:**

```typescript
interface SalaryRangeSelectorProps {
    value: string | null
    onChange: (range: string | null) => void
}

const SALARY_RANGES = [
    { value: "0-3000", label: "Até R$ 3.000", avgIncome: 1500 },
    { value: "3000-5000", label: "R$ 3.000 - R$ 5.000", avgIncome: 4000 },
    { value: "5000-8000", label: "R$ 5.000 - R$ 8.000", avgIncome: 6500 },
    { value: "8000-12000", label: "R$ 8.000 - R$ 12.000", avgIncome: 10000 },
    { value: "12000+", label: "Acima de R$ 12.000", avgIncome: 14000 },
]
```

**Features:**
- Radio buttons ou Select dropdown
- Opção "Prefiro não informar" (retorna `null`)
- Exibe TCO máximo recomendado ao selecionar (30% da renda média)
- Tooltip explicando por que pedimos essa informação

### 2. Frontend: Questionnaire Store Update

**Location:** `platform/frontend/src/store/questionnaireStore.ts`

**Changes:**

```typescript
// Adicionar helper function
const calculateFinancialCapacity = (
    faixaSalarial: string | null
): FinancialCapacity | null => {
    if (!faixaSalarial) {
        return null
    }

    const incomeBrackets: Record<string, [number, number]> = {
        "0-3000": [0, 3000],
        "3000-5000": [3000, 5000],
        "5000-8000": [5000, 8000],
        "8000-12000": [8000, 12000],
        "12000+": [12000, 16000],
    }

    const bracket = incomeBrackets[faixaSalarial]
    if (!bracket) {
        return null
    }

    const [minIncome, maxIncome] = bracket
    const avgIncome = (minIncome + maxIncome) / 2
    const maxMonthlyTco = avgIncome * 0.30

    return {
        monthly_income_range: faixaSalarial,
        max_monthly_tco: maxMonthlyTco,
        is_disclosed: true,
    }
}

// Atualizar toUserProfile()
toUserProfile: (): UserProfile => {
    const { formData } = get()

    return {
        // ... campos existentes ...
        financial_capacity: calculateFinancialCapacity(formData.faixa_salarial),
    }
}
```

### 3. Frontend: Types Update

**Location:** `platform/frontend/src/types/index.ts`

**Changes:**

```typescript
// Adicionar ao UserProfile
export interface UserProfile {
    // ... campos existentes ...
    financial_capacity?: FinancialCapacity | null
}

// Adicionar novo tipo
export interface FinancialCapacity {
    monthly_income_range: string  // "3000-5000", "5000-8000", etc.
    max_monthly_tco: number       // 30% da renda média
    is_disclosed: boolean         // true se informado, false se pulou
}
```

### 4. Frontend: Step1Budget Component Update

**Location:** `platform/frontend/src/components/questionnaire/Step1Budget.tsx`

**Changes:**

```typescript
import { SalaryRangeSelector } from './SalaryRangeSelector'

export const Step1Budget = () => {
    const { formData, updateFormData } = useQuestionnaireStore()

    const handleSalaryChange = (range: string | null) => {
        updateFormData({ faixa_salarial: range })
    }

    return (
        <VStack spacing={8} align="stretch" maxW="700px" mx="auto">
            {/* ... componentes existentes ... */}
            
            {/* Divider */}
            <Divider />
            
            {/* Salary Range Selector */}
            <SalaryRangeSelector
                value={formData.faixa_salarial || null}
                onChange={handleSalaryChange}
            />
        </VStack>
    )
}
```

### 5. Frontend: Results Display Update

**Location:** `platform/frontend/src/components/results/CarCard.tsx`

**Changes:**

```typescript
// Adicionar exibição de tags de orçamento
{recommendation.fits_budget !== null && (
    <Badge
        colorScheme={recommendation.fits_budget ? 'green' : 'yellow'}
        fontSize="sm"
        px={3}
        py={1}
    >
        {recommendation.fits_budget ? '✓ Dentro do orçamento' : '⚠ Acima do orçamento'}
    </Badge>
)}

// Adicionar tooltip com TCO detalhado
{recommendation.tco_breakdown && (
    <Tooltip
        label={
            <VStack align="start" spacing={1}>
                <Text>Financiamento: R$ {recommendation.tco_breakdown.financing_monthly.toFixed(2)}</Text>
                <Text>Combustível: R$ {recommendation.tco_breakdown.fuel_monthly.toFixed(2)}</Text>
                <Text>Manutenção: R$ {recommendation.tco_breakdown.maintenance_monthly.toFixed(2)}</Text>
                <Text>Seguro: R$ {recommendation.tco_breakdown.insurance_monthly.toFixed(2)}</Text>
                <Text>IPVA: R$ {recommendation.tco_breakdown.ipva_monthly.toFixed(2)}</Text>
                <Divider />
                <Text fontWeight="bold">Total: R$ {recommendation.tco_breakdown.total_monthly.toFixed(2)}/mês</Text>
            </VStack>
        }
    >
        <InfoIcon />
    </Tooltip>
)}
```

### 6. Backend: Validation Update

**Location:** `platform/backend/models/user_profile.py`

**Changes:** Nenhuma mudança necessária - o modelo já está correto

**Location:** `platform/backend/services/unified_recommendation_engine.py`

**Changes:** Nenhuma mudança necessária - a lógica já está implementada corretamente

**Validation to Add:** Adicionar validação no endpoint da API

```python
# platform/backend/api/main.py

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_cars(profile: UserProfile):
    """
    Gerar recomendações personalizadas
    """
    # Validar financial_capacity se fornecido
    if profile.financial_capacity:
        fc = profile.financial_capacity
        
        # Validar que is_disclosed está consistente
        if fc.is_disclosed and not fc.monthly_income_range:
            raise HTTPException(
                status_code=400,
                detail="monthly_income_range é obrigatório quando is_disclosed=true"
            )
        
        # Validar que max_monthly_tco é positivo
        if fc.max_monthly_tco is not None and fc.max_monthly_tco < 0:
            raise HTTPException(
                status_code=400,
                detail="max_monthly_tco deve ser maior ou igual a zero"
            )
        
        # Validar faixa salarial válida
        valid_ranges = ["0-3000", "3000-5000", "5000-8000", "8000-12000", "12000+"]
        if fc.monthly_income_range and fc.monthly_income_range not in valid_ranges:
            raise HTTPException(
                status_code=400,
                detail=f"monthly_income_range inválido. Opções: {valid_ranges}"
            )
    
    # ... resto da lógica existente ...
```

## Data Models

### Frontend: QuestionnaireFormData

```typescript
{
    // Step 1
    orcamento_min: 50000,
    orcamento_max: 100000,
    faixa_salarial: "5000-8000",  // NOVO
    city: "São Paulo",
    state: "SP",
    
    // Step 2
    uso_principal: "familia",
    tamanho_familia: 4,
    tem_criancas: true,
    tem_idosos: false,
    
    // Step 3
    prioridades: {
        economia: 4,
        espaco: 5,
        performance: 2,
        conforto: 4,
        seguranca: 5
    },
    
    // Step 4
    tipos_preferidos: ["SUV"],
    marcas_preferidas: [],
    cambio_preferido: undefined
}
```

### Backend: UserProfile (sent to API)

```python
{
    "orcamento_min": 50000,
    "orcamento_max": 100000,
    "city": "São Paulo",
    "state": "SP",
    "priorizar_proximas": true,
    "uso_principal": "familia",
    "frequencia_uso": "diaria",
    "tamanho_familia": 4,
    "necessita_espaco": true,
    "tem_criancas": true,
    "tem_idosos": false,
    "prioridades": {
        "economia": 4,
        "espaco": 5,
        "performance": 2,
        "conforto": 4,
        "seguranca": 5
    },
    "marcas_preferidas": [],
    "marcas_rejeitadas": [],
    "tipos_preferidos": ["SUV"],
    "cambio_preferido": null,
    "ano_minimo": null,
    "ano_maximo": null,
    "km_maxima": null,
    "must_haves": [],
    "primeiro_carro": false,
    "experiencia_anos": null,
    "financial_capacity": {  // NOVO
        "monthly_income_range": "5000-8000",
        "max_monthly_tco": 1950.0,
        "is_disclosed": true
    }
}
```

### Backend: Recommendation Response

```python
{
    "total_recommendations": 5,
    "profile_summary": {
        "budget_range": "R$ 50.000 - R$ 100.000",
        "usage": "familia",
        "location": "São Paulo, SP",
        "top_priorities": ["seguranca", "espaco", "economia"]
    },
    "recommendations": [
        {
            "car": { /* car object */ },
            "match_score": 0.87,
            "match_percentage": 87,
            "justification": "Categoria SUV ideal para familia. Excelente espaço para família. Concessionária em São Paulo.",
            "tco_breakdown": {
                "financing_monthly": 1400.0,
                "fuel_monthly": 400.0,
                "maintenance_monthly": 150.0,
                "insurance_monthly": 200.0,
                "ipva_monthly": 117.0,
                "total_monthly": 2267.0,
                "assumptions": { /* ... */ }
            },
            "fits_budget": false,  // 2267 > 1950
            "budget_percentage": 34.9,  // (2267 / 6500) * 100
            "financial_health": {
                "status": "high_commitment",
                "percentage": 34.9,
                "color": "red",
                "message": "Alto comprometimento"
            }
        }
    ],
    "execution_time_ms": 45
}
```

## Error Handling

### Frontend Errors

1. **Invalid Salary Range:**
   - Validation: Check if selected range is in valid options
   - Error: Show toast "Faixa salarial inválida"
   - Recovery: Reset to null

2. **API Error (400 - Invalid financial_capacity):**
   - Error: Show toast with backend error message
   - Recovery: Allow user to edit salary range

3. **Network Error:**
   - Error: Show toast "Erro de conexão. Tente novamente."
   - Recovery: Retry button

### Backend Errors

1. **Invalid monthly_income_range:**
   - HTTP 400: "monthly_income_range inválido. Opções: [...]"

2. **Negative max_monthly_tco:**
   - HTTP 400: "max_monthly_tco deve ser maior ou igual a zero"

3. **Inconsistent is_disclosed:**
   - HTTP 400: "monthly_income_range é obrigatório quando is_disclosed=true"

## Testing Strategy

### Unit Tests (Frontend)

**File:** `platform/frontend/src/store/__tests__/questionnaireStore.test.ts`

```typescript
describe('calculateFinancialCapacity', () => {
    it('should calculate correct max_monthly_tco for 5000-8000', () => {
        const result = calculateFinancialCapacity('5000-8000')
        expect(result).toEqual({
            monthly_income_range: '5000-8000',
            max_monthly_tco: 1950,
            is_disclosed: true
        })
    })
    
    it('should return null when faixa_salarial is null', () => {
        const result = calculateFinancialCapacity(null)
        expect(result).toBeNull()
    })
    
    it('should handle all salary ranges correctly', () => {
        const ranges = [
            { input: '0-3000', expected: 450 },
            { input: '3000-5000', expected: 1200 },
            { input: '5000-8000', expected: 1950 },
            { input: '8000-12000', expected: 3000 },
            { input: '12000+', expected: 4200 }
        ]
        
        ranges.forEach(({ input, expected }) => {
            const result = calculateFinancialCapacity(input)
            expect(result?.max_monthly_tco).toBe(expected)
        })
    })
})
```

### Integration Tests (Backend)

**File:** `platform/backend/tests/test_budget_salary_integration.py`

```python
def test_recommendation_with_financial_capacity():
    """Teste: Recomendações com capacidade financeira informada"""
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=100000,
        uso_principal="familia",
        tamanho_familia=4,
        prioridades={
            "economia": 4,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        financial_capacity=FinancialCapacity(
            monthly_income_range="5000-8000",
            max_monthly_tco=1950.0,
            is_disclosed=True
        )
    )
    
    engine = UnifiedRecommendationEngine()
    recommendations = engine.recommend(profile, limit=10)
    
    # Verificar que todos os carros têm TCO <= 1950 * 1.10 (tolerância)
    for rec in recommendations:
        assert rec['tco_breakdown'] is not None
        assert rec['tco_breakdown'].total_monthly <= 1950 * 1.10
        assert rec['fits_budget'] is not None


def test_recommendation_without_financial_capacity():
    """Teste: Recomendações sem capacidade financeira informada"""
    profile = UserProfile(
        orcamento_min=50000,
        orcamento_max=100000,
        uso_principal="familia",
        tamanho_familia=4,
        prioridades={
            "economia": 4,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        financial_capacity=None  # Não informado
    )
    
    engine = UnifiedRecommendationEngine()
    recommendations = engine.recommend(profile, limit=10)
    
    # Verificar que fits_budget é None para todos
    for rec in recommendations:
        assert rec['fits_budget'] is None


def test_api_validation_invalid_income_range():
    """Teste: API rejeita faixa salarial inválida"""
    response = client.post("/recommend", json={
        "orcamento_min": 50000,
        "orcamento_max": 100000,
        "uso_principal": "familia",
        "tamanho_familia": 4,
        "prioridades": {
            "economia": 4,
            "espaco": 5,
            "performance": 2,
            "conforto": 4,
            "seguranca": 5
        },
        "financial_capacity": {
            "monthly_income_range": "invalid-range",
            "max_monthly_tco": 2000,
            "is_disclosed": True
        }
    })
    
    assert response.status_code == 400
    assert "monthly_income_range inválido" in response.json()["detail"]
```

### E2E Tests (Cypress)

**File:** `platform/frontend/cypress/e2e/budget-salary-flow.cy.ts`

```typescript
describe('Budget Salary Integration', () => {
    it('should show budget tags when salary is informed', () => {
        cy.visit('/')
        cy.get('[data-testid="start-questionnaire"]').click()
        
        // Step 1: Orçamento + Salário
        cy.get('[data-testid="budget-min"]').type('50000')
        cy.get('[data-testid="budget-max"]').type('100000')
        cy.get('[data-testid="salary-range"]').select('5000-8000')
        cy.get('[data-testid="next-button"]').click()
        
        // Step 2-4: Preencher resto do questionário
        // ...
        
        // Verificar resultados
        cy.get('[data-testid="recommendation-card"]').should('exist')
        cy.get('[data-testid="budget-tag"]').should('be.visible')
        cy.get('[data-testid="budget-tag"]').should('contain', 'orçamento')
    })
    
    it('should NOT show budget tags when salary is not informed', () => {
        cy.visit('/')
        cy.get('[data-testid="start-questionnaire"]').click()
        
        // Step 1: Orçamento SEM Salário
        cy.get('[data-testid="budget-min"]').type('50000')
        cy.get('[data-testid="budget-max"]').type('100000')
        cy.get('[data-testid="skip-salary"]').click()
        cy.get('[data-testid="next-button"]').click()
        
        // Step 2-4: Preencher resto do questionário
        // ...
        
        // Verificar resultados
        cy.get('[data-testid="recommendation-card"]').should('exist')
        cy.get('[data-testid="budget-tag"]').should('not.exist')
    })
})
```

## Performance Considerations

1. **Frontend Calculation:**
   - `calculateFinancialCapacity()` é executado apenas uma vez ao chamar `toUserProfile()`
   - Complexidade: O(1)
   - Impacto: Negligível

2. **Backend Filtering:**
   - Filtro de TCO é aplicado após cálculo de TCO para cada carro
   - Complexidade: O(n) onde n = número de carros após filtros anteriores
   - Impacto: Baixo (já calculamos TCO de qualquer forma)

3. **API Response Size:**
   - Adicionar `financial_capacity` ao request: +100 bytes
   - Adicionar `fits_budget` e `financial_health` ao response: +50 bytes por recomendação
   - Impacto: Negligível

## Security Considerations

1. **Data Privacy:**
   - Faixa salarial é sensível - não logar em produção
   - Não armazenar faixa salarial no backend (apenas usar para cálculo)
   - Não enviar faixa salarial para analytics

2. **Input Validation:**
   - Validar que `monthly_income_range` está em lista de opções válidas
   - Validar que `max_monthly_tco` é positivo
   - Validar consistência entre `is_disclosed` e `monthly_income_range`

3. **Error Messages:**
   - Não expor detalhes internos em mensagens de erro
   - Usar mensagens genéricas para usuário final

## Migration Plan

### Phase 1: Frontend Changes (1-2 days)
1. Criar `SalaryRangeSelector` component
2. Adicionar `calculateFinancialCapacity()` helper
3. Atualizar `toUserProfile()` no store
4. Atualizar `Step1Budget` component
5. Adicionar testes unitários

### Phase 2: Backend Validation (1 day)
1. Adicionar validação no endpoint `/recommend`
2. Adicionar testes de integração
3. Testar com Postman/curl

### Phase 3: Results Display (1 day)
1. Atualizar `CarCard` component para mostrar tags
2. Adicionar tooltips com TCO detalhado
3. Adicionar testes E2E

### Phase 4: Testing & QA (1 day)
1. Executar todos os testes
2. Testar manualmente fluxo completo
3. Verificar logs e métricas

### Total Estimated Time: 4-5 days

## Rollback Plan

Se houver problemas após deploy:

1. **Frontend:** Reverter commit que adiciona `financial_capacity` ao `toUserProfile()`
2. **Backend:** Backend já suporta `financial_capacity` opcional, então não precisa rollback
3. **Monitoring:** Monitorar logs de erro 400 relacionados a `financial_capacity`

## Success Metrics

1. **Functional:**
   - 100% dos usuários que informam salário veem tags de orçamento
   - 0% dos usuários que não informam salário veem tags de orçamento
   - TCO máximo calculado corretamente para todas as faixas

2. **Technical:**
   - 0 erros 400 relacionados a `financial_capacity` inválido
   - Tempo de resposta da API < 100ms (sem degradação)
   - Cobertura de testes >= 80%

3. **User Experience:**
   - Taxa de preenchimento de faixa salarial >= 60%
   - Taxa de conversão (ver recomendações → contatar concessionária) aumenta >= 10%
