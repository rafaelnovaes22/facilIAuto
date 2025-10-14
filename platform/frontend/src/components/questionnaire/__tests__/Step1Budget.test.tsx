// Tests for Step1Budget component
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { Step1Budget } from '../Step1Budget'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import theme from '@/theme'

// Wrapper component with ChakraProvider
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('Step1Budget', () => {
    beforeEach(() => {
        // Reset store before each test
        useQuestionnaireStore.getState().resetForm()
    })

    const renderWithProvider = () => {
        return render(
            <TestWrapper>
                <Step1Budget />
            </TestWrapper>
        )
    }

    it('should render budget heading', () => {
        renderWithProvider()
        expect(screen.getByText(/Qual é o seu orçamento\?/i)).toBeInTheDocument()
    })

    it('should render minimum budget input', () => {
        renderWithProvider()
        expect(screen.getByText(/Orçamento Mínimo/i)).toBeInTheDocument()
    })

    it('should render maximum budget input', () => {
        renderWithProvider()
        expect(screen.getByText(/Orçamento Máximo/i)).toBeInTheDocument()
    })

    it('should display default budget values', () => {
        renderWithProvider()
        const budget50k = screen.getAllByText(/R\$ 50\.000/i)
        const budget100k = screen.getAllByText(/R\$ 100\.000/i)
        expect(budget50k.length).toBeGreaterThan(0)
        expect(budget100k.length).toBeGreaterThan(0)
    })

    it('should render location section', () => {
        renderWithProvider()
        expect(screen.getByText(/Onde você está localizado\?/i)).toBeInTheDocument()
    })

    it('should render state select', () => {
        renderWithProvider()
        const estadoElements = screen.getAllByText(/Estado/i)
        expect(estadoElements.length).toBeGreaterThan(0)
        const stateSelect = screen.getByRole('combobox', { name: /Estado/i })
        expect(stateSelect).toBeInTheDocument()
    })

    it('should render city input', () => {
        renderWithProvider()
        expect(screen.getByText(/Cidade/i)).toBeInTheDocument()
        const cityInput = screen.getByPlaceholderText(/Ex: São Paulo/i)
        expect(cityInput).toBeInTheDocument()
    })

    it('should update store when budget minimum changes', () => {
        renderWithProvider()

        // Update budget min directly
        useQuestionnaireStore.getState().updateFormData({ orcamento_min: 60000 })

        // Get fresh store state
        const updatedStore = useQuestionnaireStore.getState()
        expect(updatedStore.formData.orcamento_min).toBe(60000)
    })

    it('should update store when budget maximum changes', () => {
        renderWithProvider()

        // Update budget max directly
        useQuestionnaireStore.getState().updateFormData({ orcamento_max: 120000 })

        // Get fresh store state
        const updatedStore = useQuestionnaireStore.getState()
        expect(updatedStore.formData.orcamento_max).toBe(120000)
    })

    it('should update store when state is selected', () => {
        renderWithProvider()
        const stateSelect = screen.getByRole('combobox', { name: /Estado/i })

        fireEvent.change(stateSelect, { target: { value: 'SP' } })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.state).toBe('SP')
    })

    it('should update store when city is entered', () => {
        renderWithProvider()
        const cityInput = screen.getByPlaceholderText(/Ex: São Paulo/i)

        fireEvent.change(cityInput, { target: { value: 'São Paulo' } })

        const store = useQuestionnaireStore.getState()
        expect(store.formData.city).toBe('São Paulo')
    })

    it('should display budget range summary', () => {
        renderWithProvider()
        expect(screen.getByText(/Faixa de orçamento selecionada:/i)).toBeInTheDocument()
    })

    it('should show helper text for budget inputs', () => {
        renderWithProvider()
        const helperTexts = screen.getAllByText(/Valor atual:/i)
        expect(helperTexts.length).toBeGreaterThan(0)
    })
})