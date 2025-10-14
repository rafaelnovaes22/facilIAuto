// Tests for Step4Preferences component
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import { Step4Preferences } from '../Step4Preferences'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import theme from '@/theme'

// Wrapper component with ChakraProvider
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <ChakraProvider theme={theme}>{children}</ChakraProvider>
)

describe('Step4Preferences', () => {
    beforeEach(() => {
        // Reset store before each test
        useQuestionnaireStore.getState().resetForm()
    })

    const renderWithProvider = () => {
        return render(
            <TestWrapper>
                <Step4Preferences />
            </TestWrapper>
        )
    }

    it('should render preferences heading', () => {
        renderWithProvider()
        expect(screen.getByText(/Preferências \(Opcional\)/i)).toBeInTheDocument()
    })

    it('should indicate that preferences are optional', () => {
        renderWithProvider()
        expect(screen.getByText(/Ajude-nos a refinar ainda mais/i)).toBeInTheDocument()
    })

    it('should render vehicle types section', () => {
        renderWithProvider()
        expect(screen.getByText(/Tipos de Veículo Preferidos/i)).toBeInTheDocument()
    })

    it('should render all vehicle type checkboxes', () => {
        renderWithProvider()
        // Check for vehicle type checkboxes
        expect(screen.getByRole('checkbox', { name: /Hatch/i })).toBeInTheDocument()
        expect(screen.getByRole('checkbox', { name: /Sedan/i })).toBeInTheDocument()
        expect(screen.getByRole('checkbox', { name: /SUV/i })).toBeInTheDocument()
    })

    it('should render brands section', () => {
        renderWithProvider()
        expect(screen.getByText(/Marcas Preferidas/i)).toBeInTheDocument()
    })

    it('should render popular brand checkboxes', () => {
        renderWithProvider()
        expect(screen.getByRole('checkbox', { name: /Fiat/i })).toBeInTheDocument()
        expect(screen.getByRole('checkbox', { name: /Ford/i })).toBeInTheDocument()
        expect(screen.getByRole('checkbox', { name: /Volkswagen/i })).toBeInTheDocument()
        expect(screen.getByRole('checkbox', { name: /Chevrolet/i })).toBeInTheDocument()
        expect(screen.getByRole('checkbox', { name: /Toyota/i })).toBeInTheDocument()
    })

    it('should render transmission preference section', () => {
        renderWithProvider()
        expect(screen.getByText(/Preferência de Câmbio/i)).toBeInTheDocument()
    })

    it('should render all transmission options', () => {
        renderWithProvider()
        expect(screen.getByRole('radio', { name: /Sem preferência/i })).toBeInTheDocument()
        expect(screen.getByRole('radio', { name: /Manual/i })).toBeInTheDocument()

        // Use more specific selector for Automático to avoid CVT confusion
        const radioButtons = screen.getAllByRole('radio')
        const automaticoRadio = radioButtons.find(radio =>
            radio.getAttribute('value') === 'Automático'
        )
        expect(automaticoRadio).toBeInTheDocument()

        const cvtRadio = radioButtons.find(radio =>
            radio.getAttribute('value') === 'CVT'
        )
        expect(cvtRadio).toBeInTheDocument()
    })

    it('should update store when automatic transmission is selected', () => {
        renderWithProvider()

        // Use specific selector to avoid confusion with CVT
        const radioButtons = screen.getAllByRole('radio')
        const automaticoRadio = radioButtons.find(radio =>
            radio.getAttribute('value') === 'Automático'
        )

        fireEvent.click(automaticoRadio!)

        const store = useQuestionnaireStore.getState()
        expect(store.formData.cambio_preferido).toBe('Automático')
    })

    it('should have "Sem preferência" selected by default', () => {
        renderWithProvider()
        const semPreferenciaRadio = screen.getByRole('radio', { name: /Sem preferência/i })
        expect(semPreferenciaRadio).toBeChecked()
    })

    it('should update store when vehicle type is selected', () => {
        renderWithProvider()
        const suvCheckbox = screen.getByRole('checkbox', { name: /SUV/i })

        fireEvent.click(suvCheckbox)

        const store = useQuestionnaireStore.getState()
        expect(store.formData.tipos_preferidos).toContain('SUV')
    })

    it('should update store when brand is selected', () => {
        renderWithProvider()
        const fiatCheckbox = screen.getByRole('checkbox', { name: /Fiat/i })

        fireEvent.click(fiatCheckbox)

        const store = useQuestionnaireStore.getState()
        expect(store.formData.marcas_preferidas).toContain('Fiat')
    })

    it('should allow multiple vehicle types to be selected', () => {
        renderWithProvider()
        const suvCheckbox = screen.getByRole('checkbox', { name: /SUV/i })
        const sedanCheckbox = screen.getByRole('checkbox', { name: /Sedan/i })

        fireEvent.click(suvCheckbox)
        fireEvent.click(sedanCheckbox)

        const store = useQuestionnaireStore.getState()
        expect(store.formData.tipos_preferidos).toContain('SUV')
        expect(store.formData.tipos_preferidos).toContain('Sedan')
    })

    it('should allow multiple brands to be selected', () => {
        renderWithProvider()
        const fiatCheckbox = screen.getByRole('checkbox', { name: /Fiat/i })
        const toyotaCheckbox = screen.getByRole('checkbox', { name: /Toyota/i })

        fireEvent.click(fiatCheckbox)
        fireEvent.click(toyotaCheckbox)

        const store = useQuestionnaireStore.getState()
        expect(store.formData.marcas_preferidas).toContain('Fiat')
        expect(store.formData.marcas_preferidas).toContain('Toyota')
    })

    it('should update store when transmission preference is selected', () => {
        renderWithProvider()
        const manualRadio = screen.getByRole('radio', { name: /Manual/i })

        fireEvent.click(manualRadio)

        const store = useQuestionnaireStore.getState()
        expect(store.formData.cambio_preferido).toBe('Manual')
    })

    it('should display tip about optional preferences', () => {
        renderWithProvider()
        expect(screen.getByText(/Dica:/i)).toBeInTheDocument()
        expect(screen.getByText(/Essas preferências são opcionais/i)).toBeInTheDocument()
    })

    it('should show descriptions for transmission options', () => {
        renderWithProvider()
        expect(screen.getByText(/Mais econômico e maior controle/i)).toBeInTheDocument()
        expect(screen.getByText(/Mais conforto, especialmente no trânsito/i)).toBeInTheDocument()
        expect(screen.getByText(/Suavidade e eficiência/i)).toBeInTheDocument()
    })

    it('should allow deselecting vehicle types', () => {
        renderWithProvider()
        const suvCheckbox = screen.getByRole('checkbox', { name: /SUV/i })

        // Select
        fireEvent.click(suvCheckbox)
        let store = useQuestionnaireStore.getState()
        expect(store.formData.tipos_preferidos).toContain('SUV')

        // Deselect
        fireEvent.click(suvCheckbox)
        store = useQuestionnaireStore.getState()
        expect(store.formData.tipos_preferidos).not.toContain('SUV')
    })

    it('should allow deselecting brands', () => {
        renderWithProvider()
        const fiatCheckbox = screen.getByRole('checkbox', { name: /Fiat/i })

        // Select
        fireEvent.click(fiatCheckbox)
        let store = useQuestionnaireStore.getState()
        expect(store.formData.marcas_preferidas).toContain('Fiat')

        // Deselect
        fireEvent.click(fiatCheckbox)
        store = useQuestionnaireStore.getState()
        expect(store.formData.marcas_preferidas).not.toContain('Fiat')
    })
})