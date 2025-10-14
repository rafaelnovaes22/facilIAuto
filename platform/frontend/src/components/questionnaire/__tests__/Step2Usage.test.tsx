// Tests for Step2Usage component
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { Step2Usage } from '../Step2Usage'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import theme from '@/theme'

// Wrapper component with ChakraProvider
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('Step2Usage', () => {
    beforeEach(() => {
        // Reset store before each test
        useQuestionnaireStore.getState().resetForm()
    })

    const renderWithProvider = () => {
        return render(
            <TestWrapper>
                <Step2Usage />
            </TestWrapper>
        )
    }

    it('should render usage heading', () => {
        renderWithProvider()
        expect(screen.getByText(/Como você vai usar o carro\?/i)).toBeInTheDocument()
    })

    it('should render all usage options', () => {
        renderWithProvider()
        expect(screen.getByText(/👨‍👩‍👧‍👦 Família/i)).toBeInTheDocument()
        expect(screen.getByText(/💼 Trabalho/i)).toBeInTheDocument()
        expect(screen.getByText(/🏖️ Lazer/i)).toBeInTheDocument()
        expect(screen.getByText(/🚚 Comercial/i)).toBeInTheDocument()
        expect(screen.getByText(/🚖 Transporte de Passageiros/i)).toBeInTheDocument()
        expect(screen.getByText(/🎓 Primeiro Carro/i)).toBeInTheDocument()
    })

    it('should have familia selected by default', () => {
        renderWithProvider()
        const familiaRadio = screen.getByRole('radio', { name: /Família/i })
        expect(familiaRadio).toBeChecked()
    })

    it('should update store when usage option is selected', () => {
        renderWithProvider()
        const trabalhoRadio = screen.getByRole('radio', { name: /Trabalho/i })

        act(() => {
            fireEvent.click(trabalhoRadio)
        })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.uso_principal).toBe('trabalho')
    })

    it('should render family composition section', () => {
        renderWithProvider()
        expect(screen.getByText(/Composição Familiar/i)).toBeInTheDocument()
    })

    it('should render family size input', () => {
        renderWithProvider()
        expect(screen.getByText(/Quantas pessoas usarão o carro regularmente\?/i)).toBeInTheDocument()
    })

    it('should render children switch', () => {
        renderWithProvider()
        expect(screen.getByText(/Tem crianças\?/i)).toBeInTheDocument()
    })

    it('should render elderly switch', () => {
        renderWithProvider()
        expect(screen.getByText(/Tem idosos\?/i)).toBeInTheDocument()
    })

    it('should update store when family size changes', () => {
        renderWithProvider()

        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({ tamanho_familia: 4 })
        })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.tamanho_familia).toBe(4)
    })

    it('should update store when children switch is toggled', () => {
        renderWithProvider()
        const childrenSwitch = screen.getByRole('checkbox', { name: /Tem crianças\?/i })

        act(() => {
            fireEvent.click(childrenSwitch)
        })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.tem_criancas).toBe(true)
    })

    it('should update store when elderly switch is toggled', () => {
        renderWithProvider()
        const elderlySwitch = screen.getByRole('checkbox', { name: /Tem idosos\?/i })

        act(() => {
            fireEvent.click(elderlySwitch)
        })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.tem_idosos).toBe(true)
    })

    it('should display summary of selections', () => {
        renderWithProvider()
        expect(screen.getByText(/Resumo:/i)).toBeInTheDocument()
    })

    it('should show helper text for children switch', () => {
        renderWithProvider()
        expect(screen.getByText(/Prioriza segurança e espaço para cadeirinhas/i)).toBeInTheDocument()
    })

    it('should show helper text for elderly switch', () => {
        renderWithProvider()
        expect(screen.getByText(/Prioriza conforto e facilidade de acesso/i)).toBeInTheDocument()
    })

    it('should update summary when selections change', () => {
        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                uso_principal: 'trabalho',
                tamanho_familia: 2,
                tem_criancas: true,
            })
        })

        renderWithProvider()

        expect(screen.getAllByText(/trabalho/i)).toHaveLength(2) // In radio and summary
        expect(screen.getByText(/2 pessoa\(s\)/i)).toBeInTheDocument()
    })
})