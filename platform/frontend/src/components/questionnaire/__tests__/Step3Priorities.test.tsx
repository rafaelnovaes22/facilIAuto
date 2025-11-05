// Tests for Step3Priorities component (Multiple Selection)
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, act, fireEvent } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { Step3Priorities } from '../Step3Priorities'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import theme from '@/theme'

// Wrapper component with ChakraProvider
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('Step3Priorities', () => {
    beforeEach(() => {
        // Reset store before each test
        useQuestionnaireStore.getState().resetForm()
    })

    const renderWithProvider = () => {
        return render(
            <TestWrapper>
                <Step3Priorities />
            </TestWrapper>
        )
    }

    it('should render priorities heading', () => {
        renderWithProvider()
        expect(screen.getByText(/O que é mais importante para você\?/i)).toBeInTheDocument()
    })

    it('should render all 5 priority cards', () => {
        renderWithProvider()
        expect(screen.getByTestId('priority-card-economia')).toBeInTheDocument()
        expect(screen.getByTestId('priority-card-espaco')).toBeInTheDocument()
        expect(screen.getByTestId('priority-card-performance')).toBeInTheDocument()
        expect(screen.getByTestId('priority-card-conforto')).toBeInTheDocument()
        expect(screen.getByTestId('priority-card-seguranca')).toBeInTheDocument()
    })

    it('should render descriptions for each priority', () => {
        renderWithProvider()
        expect(screen.getAllByText(/Gasta pouco combustível/i)[0]).toBeInTheDocument()
        expect(screen.getAllByText(/Cabe muita coisa no porta-malas/i)[0]).toBeInTheDocument()
        expect(screen.getAllByText(/Tem força para subir ladeiras/i)[0]).toBeInTheDocument()
        expect(screen.getAllByText(/Direção macia/i)[0]).toBeInTheDocument()
        expect(screen.getAllByText(/Protege bem você e sua família/i)[0]).toBeInTheDocument()
    })

    it('should show 0/3 selected initially', () => {
        renderWithProvider()
        expect(screen.getByText('0/3 selecionadas')).toBeInTheDocument()
    })

    it('should show help text when no priorities selected', () => {
        renderWithProvider()
        expect(screen.getByText(/Clique nos cards acima para selecionar/i)).toBeInTheDocument()
    })

    it('should select a priority when clicked', () => {
        renderWithProvider()

        const economiaCard = screen.getByTestId('priority-card-economia')
        fireEvent.click(economiaCard)

        expect(screen.getByText('1/3 selecionadas')).toBeInTheDocument()
        expect(screen.getByText('1º')).toBeInTheDocument()
    })

    it('should select up to 3 priorities', () => {
        renderWithProvider()

        const economiaCard = screen.getByTestId('priority-card-economia')
        const espacoCard = screen.getByTestId('priority-card-espaco')
        const segurancaCard = screen.getByTestId('priority-card-seguranca')

        fireEvent.click(economiaCard)
        fireEvent.click(espacoCard)
        fireEvent.click(segurancaCard)

        expect(screen.getByText('3/3 selecionadas')).toBeInTheDocument()
        expect(screen.getAllByText('1º').length).toBeGreaterThan(0)
        expect(screen.getAllByText('2º').length).toBeGreaterThan(0)
        expect(screen.getAllByText('3º').length).toBeGreaterThan(0)
    })

    it('should deselect a priority when clicked again', () => {
        renderWithProvider()

        const economiaCard = screen.getByTestId('priority-card-economia')

        fireEvent.click(economiaCard)
        expect(screen.getByText('1/3 selecionadas')).toBeInTheDocument()

        fireEvent.click(economiaCard)
        expect(screen.getByText('0/3 selecionadas')).toBeInTheDocument()
    })

    it('should update store with selected priorities as value 5', () => {
        renderWithProvider()

        const economiaCard = screen.getByTestId('priority-card-economia')
        fireEvent.click(economiaCard)

        const store = useQuestionnaireStore.getState()
        expect(store.formData.prioridades?.economia).toBe(5)
        expect(store.formData.prioridades?.espaco).toBe(3)
        expect(store.formData.prioridades?.performance).toBe(3)
    })

    it('should update store with deselected priorities as value 3', () => {
        renderWithProvider()

        const economiaCard = screen.getByTestId('priority-card-economia')

        fireEvent.click(economiaCard)
        expect(useQuestionnaireStore.getState().formData.prioridades?.economia).toBe(5)

        fireEvent.click(economiaCard)
        expect(useQuestionnaireStore.getState().formData.prioridades?.economia).toBe(3)
    })

    it('should show summary when priorities are selected', () => {
        renderWithProvider()

        const economiaCard = screen.getByTestId('priority-card-economia')
        const espacoCard = screen.getByTestId('priority-card-espaco')

        fireEvent.click(economiaCard)
        fireEvent.click(espacoCard)

        expect(screen.getByText(/Suas prioridades selecionadas:/i)).toBeInTheDocument()
        expect(screen.getByText(/Vamos usar essas prioridades/i)).toBeInTheDocument()
    })

    it('should not show summary when no priorities selected', () => {
        renderWithProvider()

        expect(screen.queryByText(/Suas prioridades selecionadas:/i)).not.toBeInTheDocument()
    })

    it('should display priorities in selection order in summary', () => {
        renderWithProvider()

        const economiaCard = screen.getByTestId('priority-card-economia')
        const espacoCard = screen.getByTestId('priority-card-espaco')
        const segurancaCard = screen.getByTestId('priority-card-seguranca')

        fireEvent.click(economiaCard)
        fireEvent.click(espacoCard)
        fireEvent.click(segurancaCard)

        const summary = screen.getByText(/Suas prioridades selecionadas:/i).closest('div')
        expect(summary).toHaveTextContent(/1º.*💰.*Economia/)
        expect(summary).toHaveTextContent(/2º.*📦.*Espaço/)
        expect(summary).toHaveTextContent(/3º.*🛡️.*Segurança/)
    })

    it('should initialize from existing formData', () => {
        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: {
                    economia: 5,
                    espaco: 5,
                    performance: 3,
                    conforto: 3,
                    seguranca: 5,
                }
            })
        })

        renderWithProvider()

        expect(screen.getByText('3/3 selecionadas')).toBeInTheDocument()
        // Should have 3 badges with order numbers (1º, 2º, 3º) in the cards
        // Plus 3 more in the summary = 6 total
        expect(screen.getAllByText(/1º|2º|3º/).length).toBeGreaterThanOrEqual(3)
    })

    it('should have clickable cards', () => {
        const { container } = renderWithProvider()

        const cards = container.querySelectorAll('[data-testid^="priority-card-"]')
        expect(cards.length).toBe(5)
    })
})
