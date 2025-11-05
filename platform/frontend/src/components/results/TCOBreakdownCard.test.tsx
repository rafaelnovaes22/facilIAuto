import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
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
