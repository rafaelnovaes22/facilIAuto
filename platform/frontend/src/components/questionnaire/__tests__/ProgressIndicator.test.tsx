// Tests for ProgressIndicator component
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProgressIndicator } from '../ProgressIndicator'

describe('ProgressIndicator', () => {
    const stepTitles = ['Orçamento', 'Uso e Família', 'Prioridades', 'Preferências']

    it('should render progress bar', () => {
        const { container } = render(
            <ProgressIndicator currentStep={0} totalSteps={4} stepTitles={stepTitles} />
        )

        const progressBar = container.querySelector('[role="progressbar"]')
        expect(progressBar).toBeInTheDocument()
    })

    it('should show correct progress percentage for step 0', () => {
        const { container } = render(
            <ProgressIndicator currentStep={0} totalSteps={4} stepTitles={stepTitles} />
        )

        const progressBar = container.querySelector('[role="progressbar"]')
        expect(progressBar).toHaveAttribute('aria-valuenow', '25') // (0+1)/4 * 100 = 25%
    })

    it('should show correct progress percentage for step 1', () => {
        const { container } = render(
            <ProgressIndicator currentStep={1} totalSteps={4} stepTitles={stepTitles} />
        )

        const progressBar = container.querySelector('[role="progressbar"]')
        expect(progressBar).toHaveAttribute('aria-valuenow', '50') // (1+1)/4 * 100 = 50%
    })

    it('should show correct progress percentage for step 2', () => {
        const { container } = render(
            <ProgressIndicator currentStep={2} totalSteps={4} stepTitles={stepTitles} />
        )

        const progressBar = container.querySelector('[role="progressbar"]')
        expect(progressBar).toHaveAttribute('aria-valuenow', '75') // (2+1)/4 * 100 = 75%
    })

    it('should show correct progress percentage for step 3', () => {
        const { container } = render(
            <ProgressIndicator currentStep={3} totalSteps={4} stepTitles={stepTitles} />
        )

        const progressBar = container.querySelector('[role="progressbar"]')
        expect(progressBar).toHaveAttribute('aria-valuenow', '100') // (3+1)/4 * 100 = 100%
    })

    it('should render all step titles', () => {
        render(
            <ProgressIndicator currentStep={0} totalSteps={4} stepTitles={stepTitles} />
        )

        stepTitles.forEach(title => {
            const elements = screen.getAllByText(title)
            expect(elements.length).toBeGreaterThan(0)
        })
    })

    it('should show step numbers for uncompleted steps', () => {
        render(
            <ProgressIndicator currentStep={0} totalSteps={4} stepTitles={stepTitles} />
        )

        expect(screen.getByText('1')).toBeInTheDocument()
        expect(screen.getByText('2')).toBeInTheDocument()
        expect(screen.getByText('3')).toBeInTheDocument()
        expect(screen.getByText('4')).toBeInTheDocument()
    })

    it('should show checkmark for completed steps', () => {
        const { container } = render(
            <ProgressIndicator currentStep={2} totalSteps={4} stepTitles={stepTitles} />
        )

        // Steps 0 and 1 should be completed (have checkmarks)
        const checkmarks = container.querySelectorAll('svg')
        expect(checkmarks.length).toBeGreaterThan(0)
    })

    it('should highlight current step', () => {
        render(
            <ProgressIndicator currentStep={1} totalSteps={4} stepTitles={stepTitles} />
        )

        // Current step title should be visible (appears twice - in indicators and mobile title)
        const elements = screen.getAllByText('Uso e Família')
        expect(elements.length).toBe(2)
    })

    it('should render correct number of step indicators', () => {
        const { container } = render(
            <ProgressIndicator currentStep={0} totalSteps={4} stepTitles={stepTitles} />
        )

        // Should have 4 step numbers (one for each step)
        expect(screen.getByText('1')).toBeInTheDocument()
        expect(screen.getByText('2')).toBeInTheDocument()
        expect(screen.getByText('3')).toBeInTheDocument()
        expect(screen.getByText('4')).toBeInTheDocument()
    })

    it('should handle different total steps', () => {
        const threeStepTitles = ['Step 1', 'Step 2', 'Step 3']
        const { container } = render(
            <ProgressIndicator currentStep={0} totalSteps={3} stepTitles={threeStepTitles} />
        )

        const progressBar = container.querySelector('[role="progressbar"]')
        expect(progressBar).toHaveAttribute('aria-valuenow', '33.33333333333333') // (0+1)/3 * 100
    })

    it('should show current step title on mobile', () => {
        render(
            <ProgressIndicator currentStep={2} totalSteps={4} stepTitles={stepTitles} />
        )

        // Should show "Prioridades" as current step (appears twice - in indicators and mobile title)
        const elements = screen.getAllByText('Prioridades')
        expect(elements.length).toBe(2)
    })

    it('should handle first step correctly', () => {
        const { container } = render(
            <ProgressIndicator currentStep={0} totalSteps={4} stepTitles={stepTitles} />
        )

        const progressBar = container.querySelector('[role="progressbar"]')
        expect(progressBar).toHaveAttribute('aria-valuenow', '25')
        const elements = screen.getAllByText('Orçamento')
        expect(elements.length).toBe(2) // Appears in indicators and mobile title
    })

    it('should handle last step correctly', () => {
        const { container } = render(
            <ProgressIndicator currentStep={3} totalSteps={4} stepTitles={stepTitles} />
        )

        const progressBar = container.querySelector('[role="progressbar"]')
        expect(progressBar).toHaveAttribute('aria-valuenow', '100')
        const elements = screen.getAllByText('Preferências')
        expect(elements.length).toBe(2) // Appears in indicators and mobile title
    })
})
