// Tests for SalaryRangeSelector component
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { SalaryRangeSelector } from '../SalaryRangeSelector'
import theme from '@/theme'

// Wrapper component with ChakraProvider
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('SalaryRangeSelector', () => {
    const mockOnChange = vi.fn()

    const renderWithProvider = (value: string | null = null) => {
        return render(
            <TestWrapper>
                <SalaryRangeSelector value={value} onChange={mockOnChange} />
            </TestWrapper>
        )
    }

    beforeEach(() => {
        mockOnChange.mockClear()
    })

    it('should render salary range question', () => {
        renderWithProvider()
        expect(screen.getByText(/Qual sua faixa de renda mensal\?/i)).toBeInTheDocument()
    })

    it('should render all salary range options', () => {
        renderWithProvider()
        expect(screen.getByText(/Até R\$ 3\.000/i)).toBeInTheDocument()
        expect(screen.getByText(/R\$ 3\.000 - R\$ 5\.000/i)).toBeInTheDocument()
        expect(screen.getByText(/R\$ 5\.000 - R\$ 8\.000/i)).toBeInTheDocument()
        expect(screen.getByText(/R\$ 8\.000 - R\$ 12\.000/i)).toBeInTheDocument()
        expect(screen.getByText(/Acima de R\$ 12\.000/i)).toBeInTheDocument()
    })

    it('should render "Prefiro não informar" option', () => {
        renderWithProvider()
        expect(screen.getByText(/Prefiro não informar/i)).toBeInTheDocument()
    })

    it('should call onChange with selected range', () => {
        renderWithProvider()
        const radio = screen.getByText(/R\$ 5\.000 - R\$ 8\.000/i).closest('label')

        if (radio) {
            fireEvent.click(radio)
            expect(mockOnChange).toHaveBeenCalledWith('5000-8000')
        }
    })

    it('should call onChange with null when "Prefiro não informar" is selected', () => {
        renderWithProvider('5000-8000')
        const skipRadio = screen.getByText(/Prefiro não informar/i).closest('label')

        if (skipRadio) {
            fireEvent.click(skipRadio)
            expect(mockOnChange).toHaveBeenCalledWith(null)
        }
    })

    it('should display TCO info when a range is selected', () => {
        renderWithProvider('5000-8000')
        expect(screen.getByText(/Custo mensal recomendado/i)).toBeInTheDocument()
        expect(screen.getByText(/Até R\$ 1950\/mês/i)).toBeInTheDocument()
    })

    it('should display correct TCO for 3000-5000 range', () => {
        renderWithProvider('3000-5000')
        expect(screen.getByText(/Até R\$ 1200\/mês/i)).toBeInTheDocument()
    })

    it('should display correct TCO for 8000-12000 range', () => {
        renderWithProvider('8000-12000')
        expect(screen.getByText(/Até R\$ 3000\/mês/i)).toBeInTheDocument()
    })

    it('should display skip info when no range is selected', () => {
        renderWithProvider(null)
        expect(screen.getByText(/Sem problema! Vamos mostrar todas as opções/i)).toBeInTheDocument()
    })

    it('should not display TCO info when no range is selected', () => {
        renderWithProvider(null)
        expect(screen.queryByText(/Custo mensal recomendado/i)).not.toBeInTheDocument()
    })

    it('should render info tooltip icon', () => {
        renderWithProvider()
        // Check for the info icon (FiInfo)
        const infoIcons = document.querySelectorAll('svg')
        expect(infoIcons.length).toBeGreaterThan(0)
    })

    it('should display helper text about monthly budget', () => {
        renderWithProvider()
        expect(screen.getByText(/Isso nos ajuda a mostrar se o custo mensal do carro cabe no seu bolso/i)).toBeInTheDocument()
    })

    it('should display TCO breakdown explanation', () => {
        renderWithProvider('5000-8000')
        expect(screen.getByText(/Inclui: financiamento, combustível, manutenção, seguro e IPVA/i)).toBeInTheDocument()
    })
})
