# Implementation Plan

- [x] 1. Create/enhance TCO Calculator service





  - Create or locate `platform/backend/services/tco_calculator.py` with enhanced calculation logic
  - Implement high mileage adjustment method that increases maintenance costs by 50% for 100k-150k km and 100% for >150k km
  - Implement financing terms validation to prevent display errors like "2000% de entrada"
  - Add transparent assumption tracking to all calculations
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 2. Fix backend recommendation engine TCO logic





  - [x] 2.1 Update `calculate_tco_for_car()` method to pass vehicle mileage to calculator


    - Pass `car.quilometragem` parameter to TCO calculator
    - Handle cases where mileage data is missing
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 2.2 Implement financial health assessment logic


    - Create `assess_financial_health()` method that calculates TCO as % of income
    - Implement traffic light logic: green (≤20%), yellow (20-30%), red (>30%)
    - Return status, percentage, color, and message
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 2.3 Fix budget validation logic


    - Create `validate_budget_status()` method with correct comparison logic
    - Compare `tco.total_monthly` against `profile.financial_capacity.max_monthly_tco`
    - Return correct "Dentro do orçamento" or "Acima do orçamento" status
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 2.4 Enhance `recommend()` method to include financial health data


    - Call `assess_financial_health()` for each recommendation
    - Call `validate_budget_status()` for each recommendation
    - Include financial_health in recommendation response
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3_

- [x] 3. Update API endpoint response format





  - Modify `/recommend` endpoint to include `financial_health` in recommendation objects
  - Ensure `fits_budget` uses corrected validation logic
  - Fix `budget_percentage` calculation to use income midpoint
  - Add error handling for missing TCO data
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Enhance TCOBreakdownCard component





  - [x] 4.1 Add financial health traffic light indicator


    - Display colored circle icon (green/yellow/red)
    - Show percentage of income with formatted text
    - Display status badge with appropriate message
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  


  - [x] 4.2 Add high mileage badge

    - Check if `car_mileage > 100000`
    - Display orange badge with warning icon and mileage
    - Show badge in prominent location
    - _Requirements: 4.4_
  

  - [x] 4.3 Add transparent assumptions display section

    - Create expandable section showing all calculation parameters
    - Display fuel consumption, km/month, fuel price, financing terms
    - Show maintenance adjustment factor if applicable
    - Use clear, user-friendly labels
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  

  - [x] 4.4 Fix budget status display logic

    - Correct the budget status badge to show accurate "Dentro" or "Acima" based on `fits_budget` prop
    - Update badge color scheme (green for within, orange for above)
    - Handle cases where budget data is not available
    - _Requirements: 1.2, 1.3, 1.5_
  
  - [ ]* 4.5 Implement editable parameters feature
    - Add input fields for monthly_km (500-5000 range)
    - Add input field for fuel_price (R$3.00-10.00 range)
    - Implement validation and error messages
    - Add debounced onChange handler to trigger recalculation
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 5. Update CarCard component





  - [x] 5.1 Fix budget status display


    - Implement `getBudgetStatus()` helper function
    - Implement `getBudgetColor()` helper function
    - Update badge rendering to use corrected logic
    - _Requirements: 1.2, 1.3, 1.5_
  
  - [x] 5.2 Add financial health indicator preview


    - Display small traffic light indicator on card
    - Show percentage of income if available
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 5.3 Improve consumption justification


    - Implement `getConsumptionDescription()` helper
    - Use realistic descriptions: "Bom consumo" (≥12 km/L), "Moderado" (10-12), "Elevado" (<10)
    - Display actual consumption value alongside description
    - Remove misleading terms like "Excelente economia" without data
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 5.4 Add high mileage badge to card preview

    - Show small badge if mileage > 100k km
    - Use warning color and icon
    - _Requirements: 4.4_

- [x] 6. Update TypeScript type definitions





  - Add `financial_health` field to `Recommendation` interface
  - Add `maintenance_adjustment` to `TCOBreakdown.assumptions`
  - Add `fuel_efficiency` to `TCOBreakdown.assumptions`
  - Add `annual_interest_rate` to `TCOBreakdown.assumptions`
  - Ensure all new fields are properly typed and optional where appropriate
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.5_

- [x] 7. Write backend tests






  - [x]* 7.1 Test high mileage adjustment logic

    - Test no adjustment for ≤100k km
    - Test +50% adjustment for 100k-150k km
    - Test +100% adjustment for >150k km
    - _Requirements: 4.1, 4.2, 4.3_
  

  - [x] 7.2 Test budget validation logic






    - Test "Dentro do orçamento" for TCO ≤ max_monthly_tco
    - Test "Acima do orçamento" for TCO > max_monthly_tco
    - Test handling of missing financial_capacity
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  
  - [x] 7.3 Test financial health assessment






    - Test green status for ≤20% of income
    - Test yellow status for 20-30% of income
    - Test red status for >30% of income
    - Test percentage calculation accuracy

    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 7.4 Test financing terms validation






    - Test down_payment validation (0-100%)
    - Test months validation (12-84)
    - Test interest rate validation
    - Test default value fallbacks
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_






- [x] 8. Write frontend tests











  - [x] 8.1 Test TCOBreakdownCard budget status display






    - Test "Dentro do orçamento" badge rendering
    - Test "Acima do orçamento" badge rendering
    - Test missing budget data handling
    - _Requirements: 1.2, 1.3, 1.5_
  
  - [x] 8.2 Test financial health indicator






    - Test green indicator for healthy status
    - Test yellow indicator for caution status
    - Test red indicator for high commitment status
    - Test percentage display formatting
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 8.3 Test high mileage badge






    - Test badge appears for mileage > 100k
    - Test badge does not appear for mileage ≤ 100k
    - Test mileage formatting in badge
    - _Requirements: 4.4_
  
  - [x] 8.4 Test editable parameters






    - Test km/month input validation
    - Test fuel price input validation
    - Test onChange callback triggering
    - Test error message display
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 8.5 Test consumption description logic






    - Test "Bom consumo" for ≥12 km/L
    - Test "Consumo moderado" for 10-12 km/L
    - Test "Consumo elevado" for <10 km/L
    - Test consumption value display
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9. Integration testing and validation





  - Test complete flow from API to UI with real data
  - Verify all budget statuses are correct across multiple vehicles
  - Verify financial health indicators match expected calculations
  - Verify high mileage badges appear correctly
  - Test with edge cases (very high/low income, extreme mileage, etc.)
  - _Requirements: All requirements_
