// Tests for ResultsPage component
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, within } from '@testing-library/react'
import { BrowserRouter, MemoryRouter } from 'react-router-dom'
import ResultsPage from '../ResultsPage'
import type { RecommendationResponse } from '@/types'

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom')
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    }
})

describe('ResultsPage', () => {
    const mockRecommendations: RecommendationResponse = {
        recommendations: [
            {
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
                    dealership_name: 'Concessionária A',
                    dealership_city: 'São Paulo',
                    dealership_state: 'SP',
                    dealership_whatsapp: '5511999999999',
                    destaque: false,
                    created_at: '2024-01-01',
                    updated_at: '2024-01-01',
                },
                match_score: 87,
                match_percentage: 87,
                justification: 'Ótimo custo-benefício',
                breakdown: {
                    economia: 85,
                    espaco: 90,
                    performance: 80,
                    conforto: 85,
                    seguranca: 88,
                },
            },
            {
                car: {
                    id: '2',
                    nome: 'Toyota Yaris XLS',
                    marca: 'Toyota',
                    modelo: 'Yaris',
                    versao: 'XLS',
                    ano: 2022,
                    preco: 97990,
                    quilometragem: 20000,
                    combustivel: 'Flex',
                    cambio: 'Automático',
                    categoria: 'hatch',
                    cor: 'Prata',
                    imagens: ['https://example.com/image2.jpg'],
                    dealership_id: 'dealer2',
                    dealership_name: 'Concessionária B',
                    dealership_city: 'Rio de Janeiro',
                    dealership_state: 'RJ',
                    dealership_whatsapp: '5521999999999',
                    destaque: true,
                    created_at: '2024-01-01',
                    updated_at: '2024-01-01',
                },
                match_score: 84,
                match_percentage: 84,
                justification: 'Excelente economia',
                breakdown: {
                    economia: 90,
                    espaco: 75,
                    performance: 85,
                    conforto: 88,
                    seguranca: 82,
                },
            },
        ],
        total_recommendations: 2,
        query_time_ms: 150,
        profile_summary: {
            budget_range: 'R$ 50.000 - R$ 100.000',
            usage: 'Família',
            location: 'São Paulo - SP',
            top_priorities: ['Economia', 'Espaço', 'Segurança'],
        },
    }

    beforeEach(() => {
        vi.clearAllMocks()
    })

    const renderWithRouter = (recommendations?: RecommendationResponse) => {
        return render(
            <MemoryRouter
                initialEntries={[
                    {
                        pathname: '/resultados',
                        state: { recommendations: recommendations || mockRecommendations },
                    },
                ]}
            >
                <ResultsPage />
            </MemoryRouter>
        )
    }

    it('should render results heading with count', () => {
        renderWithRouter()
        expect(screen.getByText(/Encontramos 2 carros para você!/i)).toBeInTheDocument()
    })

    it('should render profile summary', () => {
        renderWithRouter()
        expect(screen.getByText(/Resumo do Perfil/i)).toBeInTheDocument()
        expect(screen.getByText(/R\$ 50\.000 - R\$ 100\.000/i)).toBeInTheDocument()
        expect(screen.getByText(/Família/i)).toBeInTheDocument()
    })

    it('should render top priorities badges', () => {
        renderWithRouter()
        expect(screen.getByText('Economia')).toBeInTheDocument()
        expect(screen.getByText('Espaço')).toBeInTheDocument()
        expect(screen.getByText('Segurança')).toBeInTheDocument()
    })

    it('should render all car cards', () => {
        renderWithRouter()
        expect(screen.getByText('Fiat Cronos Drive')).toBeInTheDocument()
        expect(screen.getByText('Toyota Yaris XLS')).toBeInTheDocument()
    })

    it('should render filter controls', () => {
        renderWithRouter()
        expect(screen.getByText(/Categoria:/i)).toBeInTheDocument()
        expect(screen.getByText(/Ordenar por:/i)).toBeInTheDocument()
    })

    it('should filter by category', () => {
        renderWithRouter()

        const categorySelect = screen.getByRole('combobox', { name: /Categoria/i })
        fireEvent.change(categorySelect, { target: { value: 'sedan' } })

        // Should show only sedan
        expect(screen.getByText('Fiat Cronos Drive')).toBeInTheDocument()
        expect(screen.queryByText('Toyota Yaris XLS')).not.toBeInTheDocument()
    })

    it('should sort by price ascending', () => {
        renderWithRouter()

        const sortSelect = screen.getByRole('combobox', { name: /Ordenar por/i })
        fireEvent.change(sortSelect, { target: { value: 'price_asc' } })

        // Fiat (84990) should appear before Toyota (97990)
        const carCards = screen.getAllByTestId('car-card')
        expect(within(carCards[0]).getByText('Fiat Cronos Drive')).toBeInTheDocument()
    })

    it('should sort by price descending', () => {
        renderWithRouter()

        const sortSelect = screen.getByRole('combobox', { name: /Ordenar por/i })
        fireEvent.change(sortSelect, { target: { value: 'price_desc' } })

        // Toyota (97990) should appear before Fiat (84990)
        const carCards = screen.getAllByTestId('car-card')
        expect(within(carCards[0]).getByText('Toyota Yaris XLS')).toBeInTheDocument()
    })

    it('should show result count', () => {
        renderWithRouter()
        expect(screen.getByText(/2 resultado\(s\)/i)).toBeInTheDocument()
    })

    it('should update result count after filtering', () => {
        renderWithRouter()

        const categorySelect = screen.getByRole('combobox', { name: /Categoria/i })
        fireEvent.change(categorySelect, { target: { value: 'sedan' } })

        expect(screen.getByText(/1 resultado\(s\)/i)).toBeInTheDocument()
    })

    it('should render back button', () => {
        renderWithRouter()
        expect(screen.getByText(/Voltar ao questionário/i)).toBeInTheDocument()
    })

    it('should navigate back when back button is clicked', () => {
        renderWithRouter()

        const backButton = screen.getByText(/Voltar ao questionário/i)
        fireEvent.click(backButton)

        expect(mockNavigate).toHaveBeenCalledWith('/questionario')
    })

    it('should render "Buscar Novamente" button', () => {
        renderWithRouter()
        expect(screen.getByText(/Buscar Novamente/i)).toBeInTheDocument()
    })

    it('should navigate to questionnaire when "Buscar Novamente" is clicked', () => {
        renderWithRouter()

        const searchAgainButton = screen.getByText(/Buscar Novamente/i)
        fireEvent.click(searchAgainButton)

        expect(mockNavigate).toHaveBeenCalledWith('/questionario')
    })

    it('should show loading state when no data', () => {
        render(
            <MemoryRouter initialEntries={['/resultados']}>
                <ResultsPage />
            </MemoryRouter>
        )

        expect(screen.getByText(/Carregando recomendações.../i)).toBeInTheDocument()
    })

    it('should show empty state when no recommendations', () => {
        const emptyRecommendations: RecommendationResponse = {
            ...mockRecommendations,
            recommendations: [],
            total_recommendations: 0,
        }

        renderWithRouter(emptyRecommendations)

        expect(screen.getByText(/Nenhum carro encontrado/i)).toBeInTheDocument()
        expect(screen.getByText(/Não encontramos carros que correspondam/i)).toBeInTheDocument()
    })

    it('should show "Tentar Novamente" button in empty state', () => {
        const emptyRecommendations: RecommendationResponse = {
            ...mockRecommendations,
            recommendations: [],
            total_recommendations: 0,
        }

        renderWithRouter(emptyRecommendations)

        const tryAgainButton = screen.getByText(/Tentar Novamente/i)
        expect(tryAgainButton).toBeInTheDocument()

        fireEvent.click(tryAgainButton)
        expect(mockNavigate).toHaveBeenCalledWith('/questionario')
    })

    it('should render "Não encontrou" section at bottom', () => {
        renderWithRouter()
        expect(screen.getByText(/Não encontrou o que procurava\?/i)).toBeInTheDocument()
    })

    it('should show all categories in filter dropdown', () => {
        renderWithRouter()

        const categorySelect = screen.getByRole('combobox', { name: /Categoria/i })
        expect(within(categorySelect).getByText('Todas')).toBeInTheDocument()
        expect(within(categorySelect).getByText('sedan')).toBeInTheDocument()
        expect(within(categorySelect).getByText('hatch')).toBeInTheDocument()
    })

    it('should default to sorting by score', () => {
        renderWithRouter()

        const sortSelect = screen.getByRole('combobox', { name: /Ordenar por/i }) as HTMLSelectElement
        expect(sortSelect.value).toBe('score')
    })

    it('should show cars sorted by score by default', () => {
        renderWithRouter()

        // Fiat (87%) should appear before Toyota (84%)
        const carCards = screen.getAllByTestId('car-card')
        expect(within(carCards[0]).getByText('Fiat Cronos Drive')).toBeInTheDocument()
        expect(within(carCards[1]).getByText('Toyota Yaris XLS')).toBeInTheDocument()
    })

    it('should render year filter controls', () => {
        renderWithRouter()
        expect(screen.getByText(/Ano de:/i)).toBeInTheDocument()
        expect(screen.getByText(/até:/i)).toBeInTheDocument()
    })

    it('should filter by minimum year', () => {
        renderWithRouter()

        const yearMinSelect = screen.getAllByRole('combobox')[2] // Third select (after category and sort)
        fireEvent.change(yearMinSelect, { target: { value: '2023' } })

        // Should show only 2023 car (Fiat)
        expect(screen.getByText('Fiat Cronos Drive')).toBeInTheDocument()
        expect(screen.queryByText('Toyota Yaris XLS')).not.toBeInTheDocument()
        expect(screen.getByText(/1 resultado\(s\)/i)).toBeInTheDocument()
    })

    it('should filter by maximum year', () => {
        renderWithRouter()

        const yearMaxSelect = screen.getAllByRole('combobox')[3] // Fourth select
        fireEvent.change(yearMaxSelect, { target: { value: '2022' } })

        // Should show only 2022 car (Toyota)
        expect(screen.getByText('Toyota Yaris XLS')).toBeInTheDocument()
        expect(screen.queryByText('Fiat Cronos Drive')).not.toBeInTheDocument()
        expect(screen.getByText(/1 resultado\(s\)/i)).toBeInTheDocument()
    })

    it('should filter by year range', () => {
        renderWithRouter()

        const yearMinSelect = screen.getAllByRole('combobox')[2]
        const yearMaxSelect = screen.getAllByRole('combobox')[3]

        fireEvent.change(yearMinSelect, { target: { value: '2022' } })
        fireEvent.change(yearMaxSelect, { target: { value: '2023' } })

        // Should show both cars
        expect(screen.getByText('Fiat Cronos Drive')).toBeInTheDocument()
        expect(screen.getByText('Toyota Yaris XLS')).toBeInTheDocument()
        expect(screen.getByText(/2 resultado\(s\)/i)).toBeInTheDocument()
    })

    it('should show clear year filters button when filters are active', () => {
        renderWithRouter()

        const yearMinSelect = screen.getAllByRole('combobox')[2]
        fireEvent.change(yearMinSelect, { target: { value: '2023' } })

        expect(screen.getByText(/Limpar Anos/i)).toBeInTheDocument()
    })

    it('should clear year filters when clear button is clicked', () => {
        renderWithRouter()

        const yearMinSelect = screen.getAllByRole('combobox')[2] as HTMLSelectElement
        fireEvent.change(yearMinSelect, { target: { value: '2023' } })

        const clearButton = screen.getByText(/Limpar Anos/i)
        fireEvent.click(clearButton)

        // Should show all cars again
        expect(screen.getByText('Fiat Cronos Drive')).toBeInTheDocument()
        expect(screen.getByText('Toyota Yaris XLS')).toBeInTheDocument()
        expect(screen.getByText(/2 resultado\(s\)/i)).toBeInTheDocument()
        expect(yearMinSelect.value).toBe('')
    })

    it('should combine category and year filters', () => {
        renderWithRouter()

        const categorySelect = screen.getAllByRole('combobox')[0]
        const yearMinSelect = screen.getAllByRole('combobox')[2]

        fireEvent.change(categorySelect, { target: { value: 'sedan' } })
        fireEvent.change(yearMinSelect, { target: { value: '2023' } })

        // Should show only Fiat (sedan + 2023)
        expect(screen.getByText('Fiat Cronos Drive')).toBeInTheDocument()
        expect(screen.queryByText('Toyota Yaris XLS')).not.toBeInTheDocument()
        expect(screen.getByText(/1 resultado\(s\)/i)).toBeInTheDocument()
    })

    it('should show no results when year range excludes all cars', () => {
        renderWithRouter()

        const yearMinSelect = screen.getAllByRole('combobox')[2]
        fireEvent.change(yearMinSelect, { target: { value: '2024' } })

        // Should show empty state
        expect(screen.queryByText('Fiat Cronos Drive')).not.toBeInTheDocument()
        expect(screen.queryByText('Toyota Yaris XLS')).not.toBeInTheDocument()
        expect(screen.getByText(/0 resultado\(s\)/i)).toBeInTheDocument()
    })
})
