// 💻 Tech Lead: ErrorBoundary component tests
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ErrorBoundary from '../ErrorBoundary'

// Component that throws an error
const ThrowError = () => {
    throw new Error('Test error')
}

// Component that works fine
const WorkingComponent = () => <div>Working component</div>

describe('ErrorBoundary', () => {
    it('should render children when there is no error', () => {
        render(
            <ErrorBoundary>
                <WorkingComponent />
            </ErrorBoundary>
        )

        expect(screen.getByText('Working component')).toBeDefined()
    })

    it('should render fallback UI when an error occurs', () => {
        // Suppress console.error for this test
        const originalError = console.error
        console.error = () => { }

        render(
            <ErrorBoundary>
                <ThrowError />
            </ErrorBoundary>
        )

        expect(screen.getByText(/Ops! Algo deu errado/i)).toBeDefined()
        expect(screen.getByText(/Voltar para o início/i)).toBeDefined()

        // Restore console.error
        console.error = originalError
    })
})
