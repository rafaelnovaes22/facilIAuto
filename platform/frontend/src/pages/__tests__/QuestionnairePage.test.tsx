// Tests for QuestionnairePage component
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import QuestionnairePage from '../QuestionnairePage'
import { useQuestionnaireStore } from '@/store/questionnaireStore'

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom')
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    }
})

// Mock useRecommendations hook
const mockGetRecommendations = vi.fn()
vi.mock('@/hooks/useApi', () => ({
    useRecommendations: () => ({
        mutate: mockGetRecommendations,
        isPending: false,
        data: null,
        error: false,
        message: '',
    }),
}))

// Mock formatCurrency to avoid potential issues
vi.mock('@/services/api', () => ({
    formatCurrency: (value: number) => `R$ ${value.toLocaleString('pt-BR')}`,
}))

// Mock window.scrollTo
Object.defineProperty(window, 'scrollTo', {
    value: vi.fn(),
    writable: true,
})

describe('QuestionnairePage', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        // Reset store
        useQuestionnaireStore.getState().resetForm()
    })

    const renderQuestionnairePage = () => {
        return render(
            <BrowserRouter>
                <QuestionnairePage />
            </BrowserRouter>
        )
    }

    it('should render progress indicator', () => {
        renderQuestionnairePage()
        expect(screen.getByRole('progressbar')).toBeInTheDocument()
        expect(screen.getAllByText(/Orçamento/i)).toHaveLength(6) // Progress indicator + step content
    })

    it('should render Step 1 (Budget) initially', () => {
        renderQuestionnairePage()
        expect(screen.getByText(/Qual é o seu orçamento\?/i)).toBeInTheDocument()
    })

    it('should have Voltar button disabled on first step', () => {
        renderQuestionnairePage()
        const voltarButton = screen.getByRole('button', { name: /voltar$/i })
        expect(voltarButton).toBeDisabled()
    })

    it('should have Próximo button enabled when budget is valid', () => {
        renderQuestionnairePage()
        const proximoButton = screen.getByText(/Próximo/i)
        expect(proximoButton).not.toBeDisabled()
    })

    it('should advance to next step when Próximo is clicked', async () => {
        renderQuestionnairePage()
        const proximoButton = screen.getByText(/Próximo/i)

        fireEvent.click(proximoButton)

        await waitFor(() => {
            expect(screen.getByText(/Como você vai usar o carro\?/i)).toBeInTheDocument()
        })
    })

    it('should go back to previous step when Voltar is clicked', async () => {
        renderQuestionnairePage()

        // Go to step 2
        const proximoButton = screen.getByText(/Próximo/i)
        fireEvent.click(proximoButton)

        await waitFor(() => {
            expect(screen.getByText(/Como você vai usar o carro\?/i)).toBeInTheDocument()
        })

        // Go back to step 1
        const voltarButton = screen.getByRole('button', { name: /voltar$/i })
        fireEvent.click(voltarButton)

        await waitFor(() => {
            expect(screen.getByText(/Qual é o seu orçamento\?/i)).toBeInTheDocument()
        })
    })

    it('should show "Ver Recomendações" button on last step', async () => {
        renderQuestionnairePage()

        // Navigate to last step
        const store = useQuestionnaireStore.getState()
        store.setCurrentStep(3)

        renderQuestionnairePage()

        await waitFor(() => {
            const buttons = screen.getAllByRole('button', { name: /ver recomendações/i })
            expect(buttons).toHaveLength(2) // One from each render
            expect(buttons[0]).toBeInTheDocument()
        })
    })

    it('should navigate back to home when link is clicked', () => {
        renderQuestionnairePage()
        const homeLink = screen.getByRole('button', { name: /voltar para o início/i })

        fireEvent.click(homeLink)

        expect(mockNavigate).toHaveBeenCalledWith('/')
    })

    it('should scroll to top when advancing steps', async () => {
        const scrollToSpy = vi.spyOn(window, 'scrollTo')
        renderQuestionnairePage()

        const proximoButton = screen.getByText(/Próximo/i)
        fireEvent.click(proximoButton)

        await waitFor(() => {
            expect(scrollToSpy).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' })
        })
    })
})
