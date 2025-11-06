import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { TCOBreakdownCard } from './TCOBreakdownCard'
import type { TCOBreakdown } from '@/types'

// Mock TCO data for testing
const mockTCO: TCOBreakdown = {
    financing_monthly: 1500,
    fuel_monthly: 400,
    maintenance_monthly: 200,
    insurance_monthly: 300,
    ipva_monthly: 100,
    total_monthly: 2500,
    assumptions: {
        down_payment_percent: 0.2,
        financing_months: 60,
        annual_interest_rate: 0.12,
        monthly_km: 1000,
        fuel_price_per_liter: 5.2,
        fuel_efficiency: 12,
        state: 'SP',
    },
}

describe('TCOBreakdownCard - Budget Status Display', () => {
    it('should display "Dentro do orçamento" badge when fits_budget is true', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                fits_budget={true}
            />
        )

        const badge = screen.getByText('Dentro do orçamento')
        expect(badge).toBeInTheDocument()
    })

    it('should display "Acima do orçamento" badge when fits_budget is false', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                fits_budget={false}
            />
        )

        const badge = screen.getByText('Acima do orçamento')
        expect(badge).toBeInTheDocument()
    })

    it('should not display budget badge when fits_budget is undefined', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
            />
        )

        const withinBudget = screen.queryByText('Dentro do orçamento')
        const aboveBudget = screen.queryByText('Acima do orçamento')

        expect(withinBudget).not.toBeInTheDocument()
        expect(aboveBudget).not.toBeInTheDocument()
    })
})

describe('TCOBreakdownCard - Financial Health Indicator', () => {
    it('should display green indicator for healthy status', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                financial_health={{
                    status: 'healthy',
                    percentage: 20,
                    color: 'green',
                    message: 'Saudável',
                }}
            />
        )

        // Check percentage display
        expect(screen.getByText('20% da renda')).toBeInTheDocument()

        // Check status badge
        expect(screen.getByText('Saudável')).toBeInTheDocument()
    })

    it('should display yellow indicator for caution status', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                financial_health={{
                    status: 'caution',
                    percentage: 25,
                    color: 'yellow',
                    message: 'Atenção',
                }}
            />
        )

        // Check percentage display
        expect(screen.getByText('25% da renda')).toBeInTheDocument()

        // Check status badge
        expect(screen.getByText('Atenção')).toBeInTheDocument()
    })

    it('should display red indicator for high commitment status', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                financial_health={{
                    status: 'high_commitment',
                    percentage: 35,
                    color: 'red',
                    message: 'Alto comprometimento',
                }}
            />
        )

        // Check percentage display
        expect(screen.getByText('35% da renda')).toBeInTheDocument()

        // Check status badge
        expect(screen.getByText('Alto comprometimento')).toBeInTheDocument()
    })

    it('should format percentage display correctly with no decimals', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                financial_health={{
                    status: 'healthy',
                    percentage: 18.7,
                    color: 'green',
                    message: 'Saudável',
                }}
            />
        )

        // Should round to 19% (no decimals)
        expect(screen.getByText('19% da renda')).toBeInTheDocument()
    })

    it('should not display financial health indicator when not provided', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
            />
        )

        // Should not find any financial health text
        expect(screen.queryByText(/% da renda/)).not.toBeInTheDocument()
        expect(screen.queryByText('Saudável')).not.toBeInTheDocument()
        expect(screen.queryByText('Atenção')).not.toBeInTheDocument()
        expect(screen.queryByText('Alto comprometimento')).not.toBeInTheDocument()
    })
})

describe('TCOBreakdownCard - High Mileage Badge', () => {
    it('should display high mileage badge when mileage > 100k km', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                car_mileage={137842}
            />
        )

        // Check badge appears
        const badge = screen.getByText(/Quilometragem alta/)
        expect(badge).toBeInTheDocument()

        // Check mileage formatting (137842 / 1000 = 137.842, rounded to 138k)
        expect(screen.getByText(/138k km/)).toBeInTheDocument()
    })

    it('should display high mileage badge for exactly 100001 km', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                car_mileage={100001}
            />
        )

        // Check badge appears
        expect(screen.getByText(/Quilometragem alta/)).toBeInTheDocument()
        expect(screen.getByText(/100k km/)).toBeInTheDocument()
    })

    it('should not display high mileage badge when mileage ≤ 100k km', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                car_mileage={100000}
            />
        )

        // Badge should not appear
        expect(screen.queryByText(/Quilometragem alta/)).not.toBeInTheDocument()
    })

    it('should not display high mileage badge when mileage is low', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                car_mileage={50000}
            />
        )

        // Badge should not appear
        expect(screen.queryByText(/Quilometragem alta/)).not.toBeInTheDocument()
    })

    it('should not display high mileage badge when car_mileage is not provided', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
            />
        )

        // Badge should not appear
        expect(screen.queryByText(/Quilometragem alta/)).not.toBeInTheDocument()
    })

    it('should format mileage correctly in badge (150k km)', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                car_mileage={150000}
            />
        )

        // Check formatting: 150000 / 1000 = 150k
        expect(screen.getByText(/150k km/)).toBeInTheDocument()
    })

    it('should format mileage correctly in badge (180.5k km)', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
                car_mileage={180500}
            />
        )

        // Check formatting: 180500 / 1000 = 180.5, rounded to 181k
        expect(screen.getByText(/181k km/)).toBeInTheDocument()
    })
})

describe('TCOBreakdownCard - Editable Parameters', () => {
    it('should validate km/month input within valid range (500-5000)', () => {
        const onParametersChange = vi.fn()

        render(
            <TCOBreakdownCard
                tco={mockTCO}
                onParametersChange={onParametersChange}
            />
        )

        // Expand the details to access editable parameters
        const expandButton = screen.getByText('Ver detalhamento')
        expandButton.click()

        // Find the km/month input
        const kmInput = screen.getByLabelText(/Km rodados por mês/i)

        // Test valid input (1500 km)
        fireEvent.change(kmInput, { target: { value: '1500' } })

        // Should accept valid value
        expect(kmInput).toHaveValue(1500)
    })

    it('should reject km/month input below minimum (< 500)', () => {
        const onParametersChange = vi.fn()

        render(
            <TCOBreakdownCard
                tco={mockTCO}
                onParametersChange={onParametersChange}
            />
        )

        // Expand the details
        const expandButton = screen.getByText('Ver detalhamento')
        expandButton.click()

        // Find the km/month input
        const kmInput = screen.getByLabelText(/Km rodados por mês/i)

        // Test invalid input (below minimum)
        fireEvent.change(kmInput, { target: { value: '400' } })

        // Should show error message
        expect(screen.getByText(/Km mensal deve estar entre 500 e 5.000/i)).toBeInTheDocument()

        // Should not call onChange callback
        expect(onParametersChange).not.toHaveBeenCalled()
    })

    it('should reject km/month input above maximum (> 5000)', () => {
        const onParametersChange = vi.fn()

        render(
            <TCOBreakdownCard
                tco={mockTCO}
                onParametersChange={onParametersChange}
            />
        )

        // Expand the details
        const expandButton = screen.getByText('Ver detalhamento')
        expandButton.click()

        // Find the km/month input
        const kmInput = screen.getByLabelText(/Km rodados por mês/i)

        // Test invalid input (above maximum)
        fireEvent.change(kmInput, { target: { value: '6000' } })

        // Should show error message
        expect(screen.getByText(/Km mensal deve estar entre 500 e 5.000/i)).toBeInTheDocument()

        // Should not call onChange callback
        expect(onParametersChange).not.toHaveBeenCalled()
    })

    it('should validate fuel price input within valid range (R$3.00-10.00)', () => {
        const onParametersChange = vi.fn()

        render(
            <TCOBreakdownCard
                tco={mockTCO}
                onParametersChange={onParametersChange}
            />
        )

        // Expand the details
        const expandButton = screen.getByText('Ver detalhamento')
        expandButton.click()

        // Find the fuel price input
        const fuelPriceInput = screen.getByLabelText(/Preço do combustível/i)

        // Test valid input (R$ 5.50)
        fireEvent.change(fuelPriceInput, { target: { value: '5.50' } })

        // Should accept valid value
        expect(fuelPriceInput).toHaveValue(5.50)
    })

    it('should reject fuel price input below minimum (< R$3.00)', () => {
        const onParametersChange = vi.fn()

        render(
            <TCOBreakdownCard
                tco={mockTCO}
                onParametersChange={onParametersChange}
            />
        )

        // Expand the details
        const expandButton = screen.getByText('Ver detalhamento')
        expandButton.click()

        // Find the fuel price input
        const fuelPriceInput = screen.getByLabelText(/Preço do combustível/i)

        // Test invalid input (below minimum)
        fireEvent.change(fuelPriceInput, { target: { value: '2.50' } })

        // Should show error message
        expect(screen.getByText(/Preço do combustível deve estar entre R\$ 3,00 e R\$ 10,00/i)).toBeInTheDocument()

        // Should not call onChange callback
        expect(onParametersChange).not.toHaveBeenCalled()
    })

    it('should reject fuel price input above maximum (> R$10.00)', () => {
        const onParametersChange = vi.fn()

        render(
            <TCOBreakdownCard
                tco={mockTCO}
                onParametersChange={onParametersChange}
            />
        )

        // Expand the details
        const expandButton = screen.getByText('Ver detalhamento')
        expandButton.click()

        // Find the fuel price input
        const fuelPriceInput = screen.getByLabelText(/Preço do combustível/i)

        // Test invalid input (above maximum)
        fireEvent.change(fuelPriceInput, { target: { value: '12.00' } })

        // Should show error message
        expect(screen.getByText(/Preço do combustível deve estar entre R\$ 3,00 e R\$ 10,00/i)).toBeInTheDocument()

        // Should not call onChange callback
        expect(onParametersChange).not.toHaveBeenCalled()
    })

    it('should trigger onChange callback when valid parameters are changed', () => {
        const onParametersChange = vi.fn()

        render(
            <TCOBreakdownCard
                tco={mockTCO}
                onParametersChange={onParametersChange}
            />
        )

        // Expand the details
        const expandButton = screen.getByText('Ver detalhamento')
        expandButton.click()

        // Change km/month
        const kmInput = screen.getByLabelText(/Km rodados por mês/i)
        fireEvent.change(kmInput, { target: { value: '1500' } })

        // Should call onChange with updated parameters
        expect(onParametersChange).toHaveBeenCalledWith({
            monthly_km: 1500,
            fuel_price: 5.2, // Original value
        })

        // Change fuel price
        const fuelPriceInput = screen.getByLabelText(/Preço do combustível/i)
        fireEvent.change(fuelPriceInput, { target: { value: '6.00' } })

        // Should call onChange with updated parameters
        expect(onParametersChange).toHaveBeenCalledWith({
            monthly_km: 1500, // Updated value
            fuel_price: 6.00,
        })
    })

    it('should display error message when validation fails', () => {
        const onParametersChange = vi.fn()

        render(
            <TCOBreakdownCard
                tco={mockTCO}
                onParametersChange={onParametersChange}
            />
        )

        // Expand the details
        const expandButton = screen.getByText('Ver detalhamento')
        expandButton.click()

        // Try to enter invalid km/month
        const kmInput = screen.getByLabelText(/Km rodados por mês/i)
        fireEvent.change(kmInput, { target: { value: '100' } })

        // Error message should be displayed
        const errorMessage = screen.getByText(/Km mensal deve estar entre 500 e 5.000/i)
        expect(errorMessage).toBeInTheDocument()
        expect(errorMessage).toHaveStyle({ color: 'red' })
    })

    it('should not display editable parameters when onParametersChange is not provided', () => {
        render(
            <TCOBreakdownCard
                tco={mockTCO}
            />
        )

        // Expand the details
        const expandButton = screen.getByText('Ver detalhamento')
        expandButton.click()

        // Editable inputs should not be present
        expect(screen.queryByLabelText(/Km rodados por mês/i)).not.toBeInTheDocument()
        expect(screen.queryByLabelText(/Preço do combustível/i)).not.toBeInTheDocument()
    })
})
