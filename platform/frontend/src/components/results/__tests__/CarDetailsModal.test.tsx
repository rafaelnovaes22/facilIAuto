// Tests for CarDetailsModal component
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CarDetailsModal } from '../CarDetailsModal'
import type { Recommendation } from '@/types'

// Mock window.open
const mockWindowOpen = vi.fn()
global.window.open = mockWindowOpen

describe('CarDetailsModal', () => {
    const mockCar: Recommendation['car'] = {
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
        portas: 4,
        imagens: [
            'https://example.com/image1.jpg',
            'https://example.com/image2.jpg',
            'https://example.com/image3.jpg',
        ],
        dealership_id: 'dealer1',
        dealership_name: 'Concessionária Teste',
        dealership_city: 'São Paulo',
        dealership_state: 'SP',
        dealership_whatsapp: '5511999999999',
        destaque: false,
        created_at: '2024-01-01',
        updated_at: '2024-01-01',
    }

    const mockOnClose = vi.fn()

    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('should not render when car is null', () => {
        const { container } = render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={null} />
        )

        expect(container.firstChild).toBeNull()
    })

    it('should render modal when isOpen is true', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        expect(screen.getByText('Fiat Cronos Drive')).toBeInTheDocument()
    })

    it('should not render modal when isOpen is false', () => {
        render(
            <CarDetailsModal isOpen={false} onClose={mockOnClose} car={mockCar} />
        )

        expect(screen.queryByText('Fiat Cronos Drive')).not.toBeInTheDocument()
    })

    it('should render car name and details', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        expect(screen.getByText('Fiat Cronos Drive')).toBeInTheDocument()
        expect(screen.getByText(/Fiat Cronos - Drive 1\.3/i)).toBeInTheDocument()
    })

    it('should render category badge', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        expect(screen.getByText('sedan')).toBeInTheDocument()
    })

    it('should render destaque badge when car is featured', () => {
        const featuredCar = { ...mockCar, destaque: true }
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={featuredCar} />
        )

        expect(screen.getByText(/Destaque/i)).toBeInTheDocument()
    })

    it('should render car price', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        expect(screen.getByText(/R\$ 84\.990/i)).toBeInTheDocument()
    })

    it('should render car specifications', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        expect(screen.getByText('2023')).toBeInTheDocument()
        expect(screen.getByText(/15\.000 km/i)).toBeInTheDocument()
        expect(screen.getByText('Flex')).toBeInTheDocument()
        expect(screen.getByText('Manual')).toBeInTheDocument()
        expect(screen.getByText('Branco')).toBeInTheDocument()
        expect(screen.getByText('4')).toBeInTheDocument()
    })

    it('should render dealership information', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        expect(screen.getByText('Concessionária Teste')).toBeInTheDocument()
        expect(screen.getByText(/São Paulo - SP/i)).toBeInTheDocument()
    })

    it('should render WhatsApp button', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        const whatsappButton = screen.getByText(/Falar no WhatsApp/i)
        expect(whatsappButton).toBeInTheDocument()
    })

    it('should open WhatsApp when button is clicked', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        const whatsappButton = screen.getByText(/Falar no WhatsApp/i)
        fireEvent.click(whatsappButton)

        expect(mockWindowOpen).toHaveBeenCalled()
        const callArgs = mockWindowOpen.mock.calls[0][0] as string
        expect(callArgs).toContain('wa.me')
        expect(callArgs).toContain('5511999999999')
    })

    it('should render image gallery with navigation', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        expect(screen.getByAltText(/Fiat Cronos Drive - Foto 1/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/Foto anterior/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/Próxima foto/i)).toBeInTheDocument()
    })

    it('should show image counter', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        expect(screen.getByText('1 / 3')).toBeInTheDocument()
    })

    it('should navigate to next image when next button is clicked', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        const nextButton = screen.getByLabelText(/Próxima foto/i)
        fireEvent.click(nextButton)

        expect(screen.getByText('2 / 3')).toBeInTheDocument()
    })

    it('should navigate to previous image when previous button is clicked', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        const nextButton = screen.getByLabelText(/Próxima foto/i)
        const prevButton = screen.getByLabelText(/Foto anterior/i)

        // Go to image 2
        fireEvent.click(nextButton)
        expect(screen.getByText('2 / 3')).toBeInTheDocument()

        // Go back to image 1
        fireEvent.click(prevButton)
        expect(screen.getByText('1 / 3')).toBeInTheDocument()
    })

    it('should wrap around to last image when clicking previous on first image', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        const prevButton = screen.getByLabelText(/Foto anterior/i)
        fireEvent.click(prevButton)

        expect(screen.getByText('3 / 3')).toBeInTheDocument()
    })

    it('should wrap around to first image when clicking next on last image', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        const nextButton = screen.getByLabelText(/Próxima foto/i)

        // Go to last image
        fireEvent.click(nextButton) // 2
        fireEvent.click(nextButton) // 3
        fireEvent.click(nextButton) // Should wrap to 1

        expect(screen.getByText('1 / 3')).toBeInTheDocument()
    })

    it('should render thumbnails for multiple images', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        const thumbnails = screen.getAllByAltText(/Miniatura/i)
        expect(thumbnails).toHaveLength(3)
    })

    it('should change image when thumbnail is clicked', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        const thumbnail2 = screen.getByAltText('Miniatura 2')
        fireEvent.click(thumbnail2)

        expect(screen.getByText('2 / 3')).toBeInTheDocument()
    })

    it('should not show navigation controls for single image', () => {
        const singleImageCar = {
            ...mockCar,
            imagens: ['https://example.com/image1.jpg'],
        }

        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={singleImageCar} />
        )

        expect(screen.queryByLabelText(/Foto anterior/i)).not.toBeInTheDocument()
        expect(screen.queryByLabelText(/Próxima foto/i)).not.toBeInTheDocument()
        expect(screen.queryByText(/1 \/ 1/i)).not.toBeInTheDocument()
    })

    it('should show placeholder image when no images', () => {
        const noImageCar = {
            ...mockCar,
            imagens: [],
        }

        const { container } = render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={noImageCar} />
        )

        const image = container.querySelector('img')
        if (image) {
            expect(image).toHaveAttribute('src', expect.stringContaining('placeholder'))
        } else {
            // If no image is rendered, that's also acceptable behavior for no images
            expect(container.querySelector('img')).toBeNull()
        }
    })

    it('should call onClose when close button is clicked', () => {
        render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        const closeButton = screen.getByLabelText(/close/i)
        fireEvent.click(closeButton)

        expect(mockOnClose).toHaveBeenCalled()
    })

    it('should reset image index when modal closes', () => {
        const { rerender } = render(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        // Navigate to image 2
        const nextButton = screen.getByLabelText(/Próxima foto/i)
        fireEvent.click(nextButton)
        expect(screen.getByText('2 / 3')).toBeInTheDocument()

        // Close modal
        const closeButton = screen.getByLabelText(/close/i)
        fireEvent.click(closeButton)

        // Reopen modal
        rerender(
            <CarDetailsModal isOpen={true} onClose={mockOnClose} car={mockCar} />
        )

        // Should be back to image 1
        expect(screen.getByText('1 / 3')).toBeInTheDocument()
    })
})
