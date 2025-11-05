# Design Document - TCO Calculation Fixes

## Overview

This design addresses critical bugs and missing features in the Total Cost of Ownership (TCO) calculation and display system. The current implementation has incorrect budget validation logic, missing financial health indicators, lacks transparency in assumptions, and doesn't properly adjust for high-mileage vehicles.

The solution involves fixes to both backend (calculation logic) and frontend (display and validation) components, with a focus on accuracy, transparency, and user-friendly financial guidance.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
├─────────────────────────────────────────────────────────────┤
│  TCOBreakdownCard (Enhanced)                                │
│  - Budget Status Indicator (Fixed)                          │
│  - Financial Health Traffic Light (New)                     │
│  - Editable Parameters (New)                                │
│  - Transparent Assumptions Display (New)                    │
│  - High Mileage Badge (New)                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                      Backend API (FastAPI)                   │
├─────────────────────────────────────────────────────────────┤
│  /recommend endpoint (Enhanced)                             │
│  - TCO Calculation with correct logic                       │
│  - Budget validation fix                                    │
│  - Financial health assessment                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              TCO Calculator Service (Enhanced)               │
├─────────────────────────────────────────────────────────────┤
│  - High mileage adjustment logic                            │
│  - Correct financing calculations                           │
│  - Consumption-based fuel cost                              │
│  - Transparent assumption tracking                          │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Backend Components

#### 1. TCO Calculator Service (Enhanced)

**Location**: `platform/backend/services/tco_calculator.py` (needs to be created/found)

**Responsibilities**:
- Calculate monthly financing payment with correct formula
- Adjust maintenance costs based on vehicle mileage
- Calculate fuel costs based on consumption and usage
- Track all assumptions used in calculations
- Provide transparent breakdown of all costs

**Key Methods**:

```python
class TCOCalculator:
    def calculate_tco(
        self,
        car_price: float,
        car_category: str,
        fuel_efficiency_km_per_liter: float,
        car_age: int,
        car_mileage: int,  # NEW: for high mileage adjustment
        down_payment_percent: float = 0.20,
        financing_months: int = 60,
        annual_interest_rate: float = 0.12,
        monthly_km: int = 1000,
        fuel_price_per_liter: float = 5.20,
        state: str = "SP"
    ) -> TCOBreakdown:
        """
        Calculate TCO with high mileage adjustments and transparent assumptions
        """
        pass
    
    def adjust_maintenance_for_mileage(
        self,
        base_maintenance: float,
        mileage: int
    ) -> Tuple[float, str]:
        """
        Adjust maintenance costs based on vehicle mileage
        Returns: (adjusted_cost, explanation)
        
        Rules:
        - ≤100k km: base cost
        - 100k-150k km: +50%
        - >150k km: +100%
        """
        pass
    
    def validate_financing_terms(
        self,
        down_payment_percent: float,
        financing_months: int,
        annual_interest_rate: float
    ) -> Tuple[float, int, float]:
        """
        Validate and correct financing terms
        Returns: (validated_down_payment, validated_months, validated_rate)
        
        Rules:
        - down_payment: 0-100%
        - months: 12-84
        - rate: 0.5-5% monthly
        """
        pass
```

#### 2. Recommendation Engine (Enhanced)

**Location**: `platform/backend/services/unified_recommendation_engine.py`

**Changes**:
- Fix `calculate_tco_for_car()` to pass mileage parameter
- Fix budget validation logic in `recommend()` method
- Add financial health assessment logic
- Improve consumption justification logic

**Key Changes**:

```python
def calculate_tco_for_car(
    self,
    car: Car,
    profile: UserProfile
) -> Optional[TCOBreakdown]:
    """
    Enhanced TCO calculation with mileage adjustment
    """
    # Pass car.quilometragem to calculator
    tco = calculator.calculate_tco(
        car_price=car.preco,
        car_category=car.categoria,
        fuel_efficiency_km_per_liter=fuel_efficiency,
        car_age=car_age,
        car_mileage=car.quilometragem,  # NEW
        # ... other params
    )
    return tco

def assess_financial_health(
    self,
    tco: TCOBreakdown,
    profile: UserProfile
) -> Dict[str, Any]:
    """
    NEW: Assess financial health based on TCO vs income
    
    Returns:
        {
            "status": "healthy" | "caution" | "high_commitment",
            "percentage": float,  # TCO as % of income
            "color": "green" | "yellow" | "red",
            "message": str
        }
    """
    pass

def validate_budget_status(
    self,
    tco: TCOBreakdown,
    profile: UserProfile
) -> Tuple[bool, str]:
    """
    FIXED: Correct budget validation logic
    
    Returns:
        (fits_budget: bool, status_message: str)
    """
    if not profile.financial_capacity or not profile.financial_capacity.max_monthly_tco:
        return (None, "Orçamento não informado")
    
    max_budget = profile.financial_capacity.max_monthly_tco
    fits = tco.total_monthly <= max_budget
    
    if fits:
        return (True, "Dentro do orçamento")
    else:
        return (False, "Acima do orçamento")
```

#### 3. API Endpoint (Enhanced)

**Location**: `platform/backend/api/main.py`

**Changes**:
- Add financial health assessment to recommendation response
- Fix budget percentage calculation
- Add consumption justification logic

### Frontend Components

#### 1. TCOBreakdownCard (Enhanced)

**Location**: `platform/frontend/src/components/results/TCOBreakdownCard.tsx`

**New Features**:
- Financial health traffic light indicator
- Editable parameters (km/month, fuel price)
- High mileage badge
- Transparent assumptions display
- Fixed budget status logic

**New Props**:

```typescript
interface TCOBreakdownCardProps {
    tco: TCOBreakdown
    fits_budget?: boolean
    budget_percentage?: number
    financial_health?: {  // NEW
        status: 'healthy' | 'caution' | 'high_commitment'
        percentage: number
        color: 'green' | 'yellow' | 'red'
        message: string
    }
    car_mileage?: number  // NEW: for high mileage badge
    onParametersChange?: (params: {  // NEW: for editable params
        monthly_km: number
        fuel_price: number
    }) => void
}
```

**New UI Elements**:

1. **Financial Health Indicator** (Traffic Light):
```tsx
<HStack>
    <Icon 
        as={FaCircle} 
        color={`${financial_health.color}.500`} 
        boxSize={3} 
    />
    <Text fontSize="sm" fontWeight="semibold">
        {financial_health.percentage.toFixed(0)}% da renda
    </Text>
    <Badge colorScheme={financial_health.color}>
        {financial_health.message}
    </Badge>
</HStack>
```

2. **High Mileage Badge**:
```tsx
{car_mileage && car_mileage > 100000 && (
    <Badge colorScheme="orange" fontSize="xs">
        <Icon as={FaExclamationTriangle} mr={1} />
        Quilometragem alta ({(car_mileage / 1000).toFixed(0)}k km)
    </Badge>
)}
```

3. **Editable Parameters**:
```tsx
<VStack align="stretch" spacing={2}>
    <FormControl>
        <FormLabel fontSize="xs">Km rodados por mês</FormLabel>
        <NumberInput 
            value={monthlyKm} 
            onChange={(value) => handleParamChange('monthly_km', value)}
            min={500}
            max={5000}
        >
            <NumberInputField />
        </NumberInput>
    </FormControl>
    
    <FormControl>
        <FormLabel fontSize="xs">Preço do combustível (R$/L)</FormLabel>
        <NumberInput 
            value={fuelPrice} 
            onChange={(value) => handleParamChange('fuel_price', value)}
            min={3.00}
            max={10.00}
            step={0.10}
        >
            <NumberInputField />
        </NumberInput>
    </FormControl>
</VStack>
```

4. **Transparent Assumptions**:
```tsx
<Box bg="blue.50" p={3} borderRadius="md">
    <Text fontSize="xs" fontWeight="bold" mb={2}>
        Premissas do cálculo:
    </Text>
    <VStack align="stretch" spacing={1} fontSize="xs">
        <HStack justify="space-between">
            <Text>Consumo estimado:</Text>
            <Text fontWeight="semibold">
                {tco.assumptions.fuel_efficiency} km/L
            </Text>
        </HStack>
        <HStack justify="space-between">
            <Text>Km por mês:</Text>
            <Text fontWeight="semibold">
                {tco.assumptions.monthly_km} km
            </Text>
        </HStack>
        <HStack justify="space-between">
            <Text>Preço combustível:</Text>
            <Text fontWeight="semibold">
                R$ {tco.assumptions.fuel_price_per_liter.toFixed(2)}/L
            </Text>
        </HStack>
        <HStack justify="space-between">
            <Text>Entrada:</Text>
            <Text fontWeight="semibold">
                {(tco.assumptions.down_payment_percent * 100).toFixed(0)}%
            </Text>
        </HStack>
        <HStack justify="space-between">
            <Text>Prazo:</Text>
            <Text fontWeight="semibold">
                {tco.assumptions.financing_months}x
            </Text>
        </HStack>
    </VStack>
</Box>
```

#### 2. CarCard (Enhanced)

**Location**: `platform/frontend/src/components/results/CarCard.tsx`

**Changes**:
- Fix budget status display logic
- Add financial health indicator
- Add high mileage badge
- Improve consumption justification

**Fixed Budget Status Logic**:

```typescript
// BEFORE (WRONG):
const budgetStatus = fits_budget ? "Dentro do orçamento" : "Acima do orçamento"

// AFTER (CORRECT):
const getBudgetStatus = () => {
    if (!tco_breakdown || !fits_budget !== undefined) {
        return null
    }
    return fits_budget ? "Dentro do orçamento" : "Acima do orçamento"
}

const getBudgetColor = () => {
    if (fits_budget === undefined) return "gray"
    return fits_budget ? "green" : "orange"
}
```

**Consumption Justification Logic**:

```typescript
const getConsumptionDescription = (consumption: number) => {
    if (consumption >= 12) {
        return `Bom consumo na categoria (${consumption.toFixed(1)} km/L)`
    } else if (consumption >= 10) {
        return `Consumo moderado (${consumption.toFixed(1)} km/L)`
    } else {
        return `Consumo elevado (${consumption.toFixed(1)} km/L)`
    }
}
```

## Data Models

### Enhanced TCOBreakdown

```typescript
interface TCOBreakdown {
    financing_monthly: number
    fuel_monthly: number
    maintenance_monthly: number
    insurance_monthly: number
    ipva_monthly: number
    total_monthly: number
    assumptions: {
        down_payment_percent: number
        financing_months: number
        annual_interest_rate: number  // NEW
        monthly_km: number
        fuel_price_per_liter: number
        fuel_efficiency: number  // NEW: actual consumption used
        state: string
        maintenance_adjustment?: {  // NEW
            factor: number  // 1.0, 1.5, or 2.0
            reason: string  // "Quilometragem alta"
        }
    }
}
```

### Enhanced Recommendation

```typescript
interface Recommendation {
    car: Car
    match_score: number
    match_percentage: number
    justification: string
    tco_breakdown?: TCOBreakdown
    fits_budget?: boolean
    budget_percentage?: number
    financial_health?: {  // NEW
        status: 'healthy' | 'caution' | 'high_commitment'
        percentage: number
        color: 'green' | 'yellow' | 'red'
        message: string
    }
}
```

## Error Handling

### Backend Validation

1. **Financing Terms Validation**:
```python
def validate_financing_terms(down_payment, months, rate):
    # Ensure down_payment is 0-100%
    if down_payment < 0 or down_payment > 1:
        down_payment = 0.20  # Default 20%
    
    # Ensure months is reasonable
    if months < 12 or months > 84:
        months = 60  # Default 60 months
    
    # Ensure rate is reasonable (monthly)
    monthly_rate = rate / 12 if rate > 0.1 else rate
    if monthly_rate < 0.005 or monthly_rate > 0.05:
        monthly_rate = 0.01  # Default 1% monthly
    
    return down_payment, months, monthly_rate
```

2. **TCO Calculation Fallback**:
```python
try:
    tco = calculator.calculate_tco(...)
except Exception as e:
    logger.error(f"TCO calculation failed: {e}")
    # Return None, don't block recommendation
    return None
```

### Frontend Error Handling

1. **Missing TCO Data**:
```typescript
if (!tco_breakdown) {
    return (
        <Box p={3} bg="gray.50" borderRadius="md">
            <Text fontSize="sm" color="gray.600">
                Custo mensal não disponível para este veículo
            </Text>
        </Box>
    )
}
```

2. **Invalid Parameter Input**:
```typescript
const handleParamChange = (param: string, value: number) => {
    // Validate ranges
    if (param === 'monthly_km' && (value < 500 || value > 5000)) {
        toast.error('Km mensal deve estar entre 500 e 5.000')
        return
    }
    
    if (param === 'fuel_price' && (value < 3.00 || value > 10.00)) {
        toast.error('Preço do combustível deve estar entre R$ 3,00 e R$ 10,00')
        return
    }
    
    // Update and recalculate
    onParametersChange({ ...params, [param]: value })
}
```

## Testing Strategy

### Backend Tests

1. **TCO Calculator Tests** (`test_tco_calculator.py`):
```python
def test_high_mileage_adjustment():
    """Test maintenance cost adjustment for high mileage vehicles"""
    calculator = TCOCalculator()
    
    # Low mileage: no adjustment
    tco_low = calculator.calculate_tco(price=50000, mileage=50000, ...)
    assert tco_low.maintenance_monthly == base_maintenance
    
    # Medium mileage: +50%
    tco_medium = calculator.calculate_tco(price=50000, mileage=120000, ...)
    assert tco_medium.maintenance_monthly == base_maintenance * 1.5
    
    # High mileage: +100%
    tco_high = calculator.calculate_tco(price=50000, mileage=180000, ...)
    assert tco_high.maintenance_monthly == base_maintenance * 2.0

def test_budget_validation():
    """Test correct budget status determination"""
    profile = UserProfile(
        financial_capacity=FinancialCapacity(
            max_monthly_tco=3000,
            is_disclosed=True
        )
    )
    
    # Within budget
    tco_within = TCOBreakdown(total_monthly=2800, ...)
    fits, msg = engine.validate_budget_status(tco_within, profile)
    assert fits == True
    assert msg == "Dentro do orçamento"
    
    # Above budget
    tco_above = TCOBreakdown(total_monthly=3200, ...)
    fits, msg = engine.validate_budget_status(tco_above, profile)
    assert fits == False
    assert msg == "Acima do orçamento"

def test_financial_health_assessment():
    """Test financial health traffic light logic"""
    profile = UserProfile(
        financial_capacity=FinancialCapacity(
            monthly_income_range="8000-12000",
            max_monthly_tco=3000,  # 30% of 10k
            is_disclosed=True
        )
    )
    
    # Healthy: ≤20%
    tco_healthy = TCOBreakdown(total_monthly=2000, ...)
    health = engine.assess_financial_health(tco_healthy, profile)
    assert health['status'] == 'healthy'
    assert health['color'] == 'green'
    assert health['percentage'] == 20.0
    
    # Caution: 20-30%
    tco_caution = TCOBreakdown(total_monthly=2500, ...)
    health = engine.assess_financial_health(tco_caution, profile)
    assert health['status'] == 'caution'
    assert health['color'] == 'yellow'
    assert health['percentage'] == 25.0
    
    # High: >30%
    tco_high = TCOBreakdown(total_monthly=3500, ...)
    health = engine.assess_financial_health(tco_high, profile)
    assert health['status'] == 'high_commitment'
    assert health['color'] == 'red'
    assert health['percentage'] == 35.0
```

### Frontend Tests

1. **TCOBreakdownCard Tests** (`TCOBreakdownCard.test.tsx`):
```typescript
describe('TCOBreakdownCard', () => {
    it('displays correct budget status', () => {
        const { getByText } = render(
            <TCOBreakdownCard 
                tco={mockTCO} 
                fits_budget={true} 
            />
        )
        expect(getByText('Dentro do orçamento')).toBeInTheDocument()
    })
    
    it('shows financial health indicator', () => {
        const { getByText } = render(
            <TCOBreakdownCard 
                tco={mockTCO}
                financial_health={{
                    status: 'healthy',
                    percentage: 20,
                    color: 'green',
                    message: 'Saudável'
                }}
            />
        )
        expect(getByText('20% da renda')).toBeInTheDocument()
        expect(getByText('Saudável')).toBeInTheDocument()
    })
    
    it('displays high mileage badge', () => {
        const { getByText } = render(
            <TCOBreakdownCard 
                tco={mockTCO}
                car_mileage={137842}
            />
        )
        expect(getByText(/Quilometragem alta/)).toBeInTheDocument()
    })
    
    it('allows editing parameters', async () => {
        const onParamsChange = jest.fn()
        const { getByLabelText } = render(
            <TCOBreakdownCard 
                tco={mockTCO}
                onParametersChange={onParamsChange}
            />
        )
        
        const kmInput = getByLabelText('Km rodados por mês')
        fireEvent.change(kmInput, { target: { value: '1500' } })
        
        await waitFor(() => {
            expect(onParamsChange).toHaveBeenCalledWith({
                monthly_km: 1500,
                fuel_price: 5.20
            })
        })
    })
})
```

## Implementation Notes

### Priority Order

1. **Critical Fixes** (Must have):
   - Fix budget validation logic (Requirement 1)
   - Fix financing display (Requirement 5)
   - Add high mileage adjustment (Requirement 4)

2. **Important Features** (Should have):
   - Financial health indicator (Requirement 2)
   - Transparent assumptions display (Requirement 3)
   - Accurate consumption descriptions (Requirement 7)

3. **Nice to Have** (Could have):
   - Editable parameters (Requirement 6)
   - Real-time TCO recalculation

### Performance Considerations

- TCO calculation should not significantly slow down recommendations
- Cache TCO calculations for same car/profile combination
- Editable parameters should debounce API calls (500ms delay)

### Backward Compatibility

- All new fields in TCOBreakdown should be optional
- Frontend should gracefully handle missing financial_health data
- API should continue to work for clients not sending financial_capacity

## Deployment Strategy

1. **Backend First**: Deploy TCO calculator fixes and enhanced API
2. **Frontend Second**: Deploy enhanced UI components
3. **Gradual Rollout**: Monitor error rates and user feedback
4. **A/B Testing**: Compare old vs new TCO display for user comprehension
