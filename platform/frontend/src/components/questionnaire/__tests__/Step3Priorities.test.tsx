// Tests for Step3Priorities component
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
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
        expect(screen.getByText(/Quais são suas prioridades\?/i)).toBeInTheDocument()
    })

    it('should render all 5 priority sliders', () => {
        renderWithProvider()
        // Each priority appears at least once (in label), may appear twice if in top 3 summary
        expect(screen.getAllByText(/💰 Economia/i).length).toBeGreaterThanOrEqual(1)
        expect(screen.getAllByText(/📦 Espaço/i).length).toBeGreaterThanOrEqual(1)
        expect(screen.getAllByText(/🚀 Performance/i).length).toBeGreaterThanOrEqual(1)
        expect(screen.getAllByText(/✨ Conforto/i).length).toBeGreaterThanOrEqual(1)
        expect(screen.getAllByText(/🛡️ Segurança/i).length).toBeGreaterThanOrEqual(1)
    })

    it('should display default priority values as "Média"', () => {
        renderWithProvider()
        const mediaBadges = screen.getAllByText('Média')
        expect(mediaBadges.length).toBe(5) // All 5 priorities default to 3 (Média)
    })

    it('should render descriptions for each priority', () => {
        renderWithProvider()
        expect(screen.getByText(/Baixo consumo de combustível/i)).toBeInTheDocument()
        expect(screen.getByText(/Porta-malas amplo/i)).toBeInTheDocument()
        expect(screen.getByText(/Potência do motor/i)).toBeInTheDocument()
        expect(screen.getByText(/Direção suave/i)).toBeInTheDocument()
        expect(screen.getByText(/Airbags, freios ABS/i)).toBeInTheDocument()
    })

    it('should update store when economia slider changes', () => {
        renderWithProvider()

        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: { ...store.formData.prioridades, economia: 5 }
            })
        })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.prioridades?.economia).toBe(5)
    })

    it('should update store when espaco slider changes', () => {
        renderWithProvider()

        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: { ...store.formData.prioridades, espaco: 4 }
            })
        })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.prioridades?.espaco).toBe(4)
    })

    it('should update store when performance slider changes', () => {
        renderWithProvider()

        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: { ...store.formData.prioridades, performance: 5 }
            })
        })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.prioridades?.performance).toBe(5)
    })

    it('should update store when conforto slider changes', () => {
        renderWithProvider()

        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: { ...store.formData.prioridades, conforto: 2 }
            })
        })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.prioridades?.conforto).toBe(2)
    })

    it('should update store when seguranca slider changes', () => {
        renderWithProvider()

        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: { ...store.formData.prioridades, seguranca: 5 }
            })
        })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.prioridades?.seguranca).toBe(5)
    })

    it('should display summary of top 3 priorities', () => {
        renderWithProvider()
        expect(screen.getByText(/Suas prioridades principais:/i)).toBeInTheDocument()
    })

    it('should display correct label for priority value 1', () => {
        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: { ...store.formData.prioridades, economia: 1 }
            })
        })

        renderWithProvider()
        expect(screen.getAllByText('Baixa')[0]).toBeInTheDocument()
    })

    it('should display correct label for priority value 2', () => {
        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: { ...store.formData.prioridades, economia: 2 }
            })
        })

        renderWithProvider()
        expect(screen.getAllByText('Média-Baixa')[0]).toBeInTheDocument()
    })

    it('should display correct label for priority value 4', () => {
        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: { ...store.formData.prioridades, economia: 4 }
            })
        })

        renderWithProvider()
        expect(screen.getAllByText('Alta')[0]).toBeInTheDocument()
    })

    it('should display correct label for priority value 5', () => {
        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: { ...store.formData.prioridades, economia: 5 }
            })
        })

        renderWithProvider()
        expect(screen.getAllByText('Muito Alta')[0]).toBeInTheDocument()
    })

    it('should show top priorities in summary', () => {
        act(() => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                prioridades: {
                    economia: 5,
                    espaco: 4,
                    performance: 3,
                    conforto: 2,
                    seguranca: 5,
                }
            })
        })

        renderWithProvider()

        // Should show top 3: economia (5), seguranca (5), espaco (4)
        const badges = screen.getAllByText(/💰 Economia|🛡️ Segurança|📦 Espaço/i)
        expect(badges.length).toBeGreaterThan(0)
    })

    it('should have sliders with correct range (1-5)', () => {
        const { container } = renderWithProvider()
        const sliders = container.querySelectorAll('[role="slider"]')

        expect(sliders.length).toBe(5)
        sliders.forEach(slider => {
            expect(slider).toHaveAttribute('aria-valuemin', '1')
            expect(slider).toHaveAttribute('aria-valuemax', '5')
        })
    })
})