// Tests for ScoreVisual component
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { ScoreVisual } from '../ScoreVisual'
import theme from '@/theme'

// Wrapper component with ChakraProvider
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('ScoreVisual', () => {
  const renderWithProvider = (score: number, percentage: number) => {
    return render(
      <TestWrapper>
        <ScoreVisual score={score} percentage={percentage} />
      </TestWrapper>
    )
  }

  it('should render score percentage', () => {
    renderWithProvider(87, 87)
    expect(screen.getByText('87%')).toBeInTheDocument()
  })

  it('should show "Match Perfeito" for score >= 90', () => {
    renderWithProvider(95, 95)
    expect(screen.getByText('Match Perfeito')).toBeInTheDocument()
  })

  it('should show "Excelente Match" for score >= 80', () => {
    renderWithProvider(85, 85)
    expect(screen.getByText('Excelente Match')).toBeInTheDocument()
  })

  it('should show "Ótimo Match" for score >= 70', () => {
    renderWithProvider(75, 75)
    expect(screen.getByText('Ótimo Match')).toBeInTheDocument()
  })

  it('should show "Bom Match" for score >= 60', () => {
    renderWithProvider(65, 65)
    expect(screen.getByText('Bom Match')).toBeInTheDocument()
  })

  it('should show "Match Razoável" for score >= 50', () => {
    renderWithProvider(55, 55)
    expect(screen.getByText('Match Razoável')).toBeInTheDocument()
  })

  it('should show "Match Baixo" for score < 50', () => {
    renderWithProvider(45, 45)
    expect(screen.getByText('Match Baixo')).toBeInTheDocument()
  })

  it('should render circular progress', () => {
    const { container } = renderWithProvider(80, 80)
    const circularProgress = container.querySelector('[role="progressbar"]')
    expect(circularProgress).toBeInTheDocument()
  })

  it('should round percentage to nearest integer', () => {
    renderWithProvider(87.6, 87.6)
    expect(screen.getByText('88%')).toBeInTheDocument()
  })

  it('should handle edge case of 0%', () => {
    renderWithProvider(0, 0)
    expect(screen.getByText('0%')).toBeInTheDocument()
    expect(screen.getByText('Match Baixo')).toBeInTheDocument()
  })

  it('should handle edge case of 100%', () => {
    renderWithProvider(100, 100)
    expect(screen.getByText('100%')).toBeInTheDocument()
    expect(screen.getByText('Match Perfeito')).toBeInTheDocument()
  })
})
