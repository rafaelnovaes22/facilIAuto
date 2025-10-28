// 🎨 UX Especialist: SkeletonCard component tests
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import SkeletonCard from '../SkeletonCard'

const renderWithChakra = (component: React.ReactElement) => {
    return render(<ChakraProvider>{component}</ChakraProvider>)
}

describe('SkeletonCard', () => {
    it('should render single skeleton card by default', () => {
        const { container } = renderWithChakra(<SkeletonCard />)
        const skeletons = container.querySelectorAll('.chakra-skeleton')
        expect(skeletons.length).toBeGreaterThan(0)
    })

    it('should render multiple skeleton cards when count is specified', () => {
        const { container } = renderWithChakra(<SkeletonCard count={3} />)
        const cards = container.querySelectorAll('[class*="css-"]')
        // Should have multiple skeleton elements
        expect(cards.length).toBeGreaterThan(3)
    })
})
