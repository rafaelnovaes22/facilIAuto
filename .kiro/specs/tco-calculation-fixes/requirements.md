# Requirements Document

## Introduction

This specification addresses critical issues in the Total Cost of Ownership (TCO) calculation and display system. The current implementation has incorrect budget validation logic, missing financial health indicators, and lacks transparency in calculation assumptions. Users are seeing cars marked as "above budget" when they're actually within their stated budget, and the system doesn't properly evaluate financial health based on income-to-TCO ratios.

## Glossary

- **TCO System**: The Total Cost of Ownership calculation and display system that estimates monthly vehicle costs
- **Budget Validator**: Component that determines if a vehicle's TCO fits within user's stated monthly budget
- **Financial Health Indicator**: Visual system (traffic light) showing if TCO is healthy relative to user income
- **Calculation Engine**: Backend service that computes TCO based on vehicle price, financing terms, and operating costs
- **Assumption Display**: UI component showing the parameters used in TCO calculations (fuel consumption, km/month, etc.)
- **High Mileage Adjuster**: Logic that increases maintenance cost estimates for vehicles with >100k km

## Requirements

### Requirement 1: Accurate Budget Validation

**User Story:** As a car buyer, I want to see accurate budget status for each vehicle, so that I can quickly identify which cars fit my monthly budget.

#### Acceptance Criteria

1. WHEN the TCO System calculates a vehicle's monthly cost, THE Budget Validator SHALL compare the total monthly cost against the user's stated monthly budget limit
2. WHEN a vehicle's monthly TCO is less than or equal to the user's budget, THE TCO System SHALL display "Dentro do orçamento" status
3. WHEN a vehicle's monthly TCO exceeds the user's budget, THE TCO System SHALL display "Acima do orçamento" status
4. THE Budget Validator SHALL use the complete monthly TCO (financing + fuel + insurance + maintenance) for comparison
5. THE TCO System SHALL display the exact monthly cost value alongside the budget status

### Requirement 2: Financial Health Assessment

**User Story:** As a car buyer, I want to understand if a vehicle is financially healthy for my income level, so that I can make responsible purchasing decisions.

#### Acceptance Criteria

1. WHEN the user provides an income range, THE Financial Health Indicator SHALL calculate TCO as a percentage of the midpoint income
2. WHEN TCO is ≤20% of income, THE Financial Health Indicator SHALL display a green indicator with "Saudável" status
3. WHEN TCO is between 20-30% of income, THE Financial Health Indicator SHALL display a yellow indicator with "Atenção" status
4. WHEN TCO is >30% of income, THE Financial Health Indicator SHALL display a red indicator with "Alto comprometimento" status
5. THE Financial Health Indicator SHALL display the exact percentage value alongside the color indicator

### Requirement 3: Transparent Calculation Assumptions

**User Story:** As a car buyer, I want to see what assumptions are used in TCO calculations, so that I can understand and trust the estimates.

#### Acceptance Criteria

1. THE Assumption Display SHALL show fuel consumption estimate (km/L) used in calculations
2. THE Assumption Display SHALL show monthly distance estimate (km/month) used in calculations
3. THE Assumption Display SHALL show fuel price (R$/L) used in calculations
4. THE Assumption Display SHALL show financing terms (down payment %, interest rate, term) used in calculations
5. THE Assumption Display SHALL be visible in an expandable section of the TCO breakdown

### Requirement 4: High Mileage Cost Adjustment

**User Story:** As a car buyer, I want maintenance costs to reflect vehicle mileage, so that I get realistic cost estimates for high-mileage vehicles.

#### Acceptance Criteria

1. WHEN a vehicle has mileage ≤100,000 km, THE High Mileage Adjuster SHALL use standard maintenance cost estimates
2. WHEN a vehicle has mileage between 100,001-150,000 km, THE High Mileage Adjuster SHALL increase maintenance costs by 50%
3. WHEN a vehicle has mileage >150,000 km, THE High Mileage Adjuster SHALL increase maintenance costs by 100%
4. THE TCO System SHALL display a "Quilometragem alta" badge when mileage >100,000 km
5. THE Assumption Display SHALL show the adjusted maintenance cost estimate with explanation

### Requirement 5: Correct Financing Display

**User Story:** As a car buyer, I want to see correct financing terms, so that I'm not confused by display errors.

#### Acceptance Criteria

1. THE TCO System SHALL display down payment percentage as a whole number between 0-100
2. THE TCO System SHALL format down payment percentage with "%" symbol (e.g., "20%")
3. THE TCO System SHALL validate that down payment percentage is ≤100% before display
4. WHEN financing data contains errors, THE TCO System SHALL use default values (20% down, 1.5% monthly rate, 60 months)
5. THE TCO System SHALL display financing term in months with "x" notation (e.g., "60x")

### Requirement 6: Editable TCO Parameters

**User Story:** As a car buyer, I want to adjust TCO calculation parameters, so that I can see costs based on my actual usage patterns.

#### Acceptance Criteria

1. THE TCO System SHALL allow users to edit monthly distance (km/month) parameter
2. THE TCO System SHALL allow users to edit fuel price (R$/L) parameter
3. WHEN a user changes a parameter, THE Calculation Engine SHALL recalculate TCO in real-time
4. THE TCO System SHALL validate that monthly distance is between 500-5,000 km/month
5. THE TCO System SHALL validate that fuel price is between R$3.00-R$10.00/L

### Requirement 7: Consumption Justification Accuracy

**User Story:** As a car buyer, I want realistic fuel economy descriptions, so that I have accurate expectations.

#### Acceptance Criteria

1. WHEN a vehicle has consumption ≥12 km/L, THE TCO System SHALL display "Bom consumo na categoria"
2. WHEN a vehicle has consumption between 10-12 km/L, THE TCO System SHALL display "Consumo moderado"
3. WHEN a vehicle has consumption <10 km/L, THE TCO System SHALL display "Consumo elevado"
4. THE TCO System SHALL display the actual consumption value (km/L) alongside the description
5. THE TCO System SHALL NOT use terms like "Excelente economia" without data to support the claim
