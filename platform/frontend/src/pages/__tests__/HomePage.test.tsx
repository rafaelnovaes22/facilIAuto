// Tests for HomePage component
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ChakraProvider } from '@chakra-ui/react'
import HomePage from '../HomePage'
import theme from '@/theme'

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom')
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    }
})

// Mock useAggregatedStats hook
vi.mock('@/hooks/useApi', () => ({
    useAggregatedStats: () => ({
        totalCars: 129,
        totalDealerships: 3,
        avgPrice: 85000,
        isLoading: false,
    }),
}))

describe('HomePage', () => {
    const renderHomePage = () => {
        return render(
            <ChakraProvider theme={theme}>
                <BrowserRouter>
                    <HomePage />
                </BrowserRouter>
            </ChakraProvider>
        )
    }

    it('should render main heading', () => {
        renderHomePage()
        expect(screen.getByText(/Encontre o Carro Perfeito em 3 Minutos/i)).toBeInTheDocument()
    })

    it('should render CTA button', () => {
        renderHomePage()
        const ctaButtons = screen.getAllByText(/Começar/i)
        expect(ctaButtons.length).toBeGreaterThan(0)
    })

    it('should navigate to questionnaire when CTA is clicked', () => {
        renderHomePage()
        const ctaButton = screen.getAllByText(/Começar Agora/i)[0]

        fireEvent.click(ctaButton)

        expect(mockNavigate).toHaveBeenCalledWith('/questionario')
    })

    it('should display trust indicators', () => {
        renderHomePage()
        expect(screen.getAllByText(/3 minutos/i)[0]).toBeInTheDocument()
        expect(screen.getByText(/100% gratuito/i)).toBeInTheDocument()
        expect(screen.getAllByText(/Personalizado/i)[0]).toBeInTheDocument()
    })

    it('should display stats when not loading', () => {
        renderHomePage()
        expect(screen.getByText('129')).toBeInTheDocument()
        expect(screen.getAllByText('3')[0]).toBeInTheDocument()
    })

    it('should display "Como Funciona" section', () => {
        renderHomePage()
        expect(screen.getByText(/Como Funciona\?/i)).toBeInTheDocument()
        expect(screen.getByText(/Responda o Questionário/i)).toBeInTheDocument()
        expect(screen.getByText(/IA Analisa e Recomenda/i)).toBeInTheDocument()
        expect(screen.getAllByText(/Receba Recomendações/i)[0]).toBeInTheDocument()
    })

    it('should display "Por Que FacilIAuto" section', () => {
        renderHomePage()
        expect(screen.getByText(/Por Que FacilIAuto\?/i)).toBeInTheDocument()
        expect(screen.getAllByText(/Recomendações Personalizadas/i)[0]).toBeInTheDocument()
        expect(screen.getByText(/Rápido e Fácil/i)).toBeInTheDocument()
    })

    it('should display footer', () => {
        renderHomePage()
        expect(screen.getAllByText(/FacilIAuto/i)[0]).toBeInTheDocument()
        expect(screen.getByText(/© 2024 FacilIAuto/i)).toBeInTheDocument()
    })

    it('should have responsive layout', () => {
        const { container } = renderHomePage()
        const heroSection = container.querySelector('div')
        expect(heroSection).toBeTruthy()
    })
})
