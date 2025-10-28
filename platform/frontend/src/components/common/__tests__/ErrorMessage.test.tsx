// 🎨 UX Especialist: ErrorMessage component tests
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import ErrorMessage from '../ErrorMessage'

const renderWithChakra = (component: React.ReactElement) => {
    return render(<ChakraProvider>{component}</ChakraProvider>)
}

describe('ErrorMessage', () => {
    it('should render with default props', () => {
        renderWithChakra(<ErrorMessage />)
        expect(screen.getByText(/Ops! Algo deu errado/i)).toBeDefined()
        expect(screen.getByText(/Tentar novamente/i)).toBeDefined()
    })

    it('should render with custom title and message', () => {
        renderWithChakra(
            <ErrorMessage
                title="Custom Error"
                message="Custom error message"
            />
        )
        expect(screen.getByText('Custom Error')).toBeDefined()
        expect(screen.getByText('Custom error message')).toBeDefined()
    })

    it('should call onRetry when retry button is clicked', () => {
        const onRetry = vi.fn()
        renderWithChakra(<ErrorMessage onRetry={onRetry} />)

        const retryButton = screen.getByText(/Tentar novamente/i)
        fireEvent.click(retryButton)

        expect(onRetry).toHaveBeenCalledTimes(1)
    })

    it('should not show retry button when showRetry is false', () => {
        renderWithChakra(<ErrorMessage showRetry={false} />)
        expect(screen.queryByText(/Tentar novamente/i)).toBeNull()
    })
})
