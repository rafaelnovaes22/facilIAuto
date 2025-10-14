// Tests for CarCard component
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CarCard } from '../CarCard'
import type { Recommendation } from '@/types'

// Mock window.open
const mockWindowOpen = vi.fn()
global.window.open = mockWindowOpen

describe('CarCard', () => {
    const mockRecommendation: Recommendation = {
        car: {
            id: '1',
            nome: 'Fiat Cronos Drive',
            marca: 'Fiat',
            modelo: 'Cronos',
            versao: 'Drive 1.3',
            ano: 2023,
            preco: 84990,
            quilometragem: 15000,
            combustivel: 'Flex',
            cambio: 'Manual',
            categoria: 'sedan',
            cor: 'Branco',
            imagens: ['https://example.com/image1.jpg'],
            dealership_id: 'dealer1',
            dealership_name: 'Concessionária Teste',
            dealership_city: 'São Paulo',
            dealership_state: 'SP',
            dealership_whatsapp: '5511999999999',
            destaque: false,
            created_at: '2024-01-01',
            updated_at: '2024-01-01',
        },
        match_score: 87,
        match_percentage: 87,
        justification: 'Ótimo custo-benefício para uso familiar',
        breakdown: {
            economia: 85,
            espaco: 90,
            performance: 80,
            conforto: 85,
            seguranca: 88,
        },
    }

    const mockOnWhatsAppClick = vi.fn()
    const mockOnDetailsClick = vi.fn()

    it('should render car name', () => {
        render(
            <CarCard
                recommendation={mockRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        expect(screen.getByText('Fiat Cronos Drive')).toBeInTheDocument()
    })

    it('should render car price formatted', () => {
        render(
            <CarCard
                recommendation={mockRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        expect(screen.getByText(/R\$ 84\.990/i)).toBeInTheDocument()
    })

    it('should render car details', () => {
        render(
            <CarCard
                recommendation={mockRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        expect(screen.getByText('2023')).toBeInTheDocument()
        expect(screen.getByText(/15\.000 km/i)).toBeInTheDocument()
        expect(screen.getByText('Flex')).toBeInTheDocument()
        expect(screen.getByText('Manual')).toBeInTheDocument()
    })

    it('should render dealership information', () => {
        render(
            <CarCard
                recommendation={mockRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        expect(screen.getByText('Concessionária Teste')).toBeInTheDocument()
        expect(screen.getByText(/São Paulo - SP/i)).toBeInTheDocument()
    })

    it('should render justification', () => {
        render(
            <CarCard
                recommendation={mockRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        expect(screen.getByText(/Ótimo custo-benefício para uso familiar/i)).toBeInTheDocument()
    })

    it('should render WhatsApp button', () => {
        render(
            <CarCard
                recommendation={mockRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        const whatsappButton = screen.getByText('WhatsApp')
        expect(whatsappButton).toBeInTheDocument()
    })

    it('should open WhatsApp when button is clicked', () => {
        render(
            <CarCard
                recommendation={mockRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        const whatsappButton = screen.getByText('WhatsApp')
        fireEvent.click(whatsappButton)

        expect(mockWindowOpen).toHaveBeenCalled()
        expect(mockOnWhatsAppClick).toHaveBeenCalledWith(mockRecommendation.car)
    })

    it('should call onDetailsClick when details button is clicked', () => {
        render(
            <CarCard
                recommendation={mockRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        const detailsButton = screen.getByText(/Ver Detalhes e Fotos/i)
        fireEvent.click(detailsButton)

        expect(mockOnDetailsClick).toHaveBeenCalledWith(mockRecommendation.car)
    })

    it('should render category badge', () => {
        render(
            <CarCard
                recommendation={mockRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        expect(screen.getByText('sedan')).toBeInTheDocument()
    })

    it('should render destaque badge when car is featured', () => {
        const featuredRecommendation = {
            ...mockRecommendation,
            car: {
                ...mockRecommendation.car,
                destaque: true,
            },
        }

        render(
            <CarCard
                recommendation={featuredRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        expect(screen.getByText(/Destaque/i)).toBeInTheDocument()
    })

    it('should render image count badge when multiple images', () => {
        const multiImageRecommendation = {
            ...mockRecommendation,
            car: {
                ...mockRecommendation.car,
                imagens: ['img1.jpg', 'img2.jpg', 'img3.jpg'],
            },
        }

        render(
            <CarCard
                recommendation={multiImageRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        expect(screen.getByText('3')).toBeInTheDocument()
    })

    it('should render placeholder image when no images', () => {
        const noImageRecommendation = {
            ...mockRecommendation,
            car: {
                ...mockRecommendation.car,
                imagens: [],
            },
        }

        const { container } = render(
            <CarCard
                recommendation={noImageRecommendation}
                onWhatsAppClick={mockOnWhatsAppClick}
                onDetailsClick={mockOnDetailsClick}
            />
        )

        const image = container.querySelector('img')
        expect(image).toHaveAttribute('src', expect.stringContaining('placeholder'))
    })
})
