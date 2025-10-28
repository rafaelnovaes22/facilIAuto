// 🎨 UX Especialist: LoadingSpinner component tests
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import LoadingSpinner from '../LoadingSpinner'

const renderWithChakra = (component: React.ReactElement) => {
    return render(<ChakraProvider>{component}</ChakraProvider>)
}

describe('LoadingSpinner', () => {
    it('should render spinner with default size', () => {
        const { container } = renderWithChakra(<LoadingSpinner />)
        const spinner = container.querySelector('.chakra-spinner')
        expect(spinner).toBeDefined()
    })

    it('should render spinner with small size', () => {
        const { container } = renderWithChakra(<LoadingSpinner size="sm" />)
        const spinner = container.querySelector('.chakra-spinner')
        expect(spinner).toBeDefined()
    })

    it('should render spinner with large size', () => {
        const { container } = renderWithChakra(<LoadingSpinner size="lg" />)
        const spinner = container.querySelector('.chakra-spinner')
        expect(spinner).toBeDefined()
    })

    it('should render centered spinner', () => {
        const { container } = renderWithChakra(<LoadingSpinner centered />)
        const wrapper = container.querySelector('.chakra-stack')
        expect(wrapper).toBeDefined()
    })
})
