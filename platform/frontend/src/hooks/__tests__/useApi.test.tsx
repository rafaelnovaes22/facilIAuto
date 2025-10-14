// 💻 Tech Lead: TDD - Custom hooks tests
import { describe, it, expect, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactNode } from 'react'
import { useHealthCheck, useStats, useRecommendations } from '../useApi'
import * as api from '@/services/api'

// Mock do módulo api
vi.mock('@/services/api', () => ({
    healthCheck: vi.fn(),
    getStats: vi.fn(),
    getRecommendations: vi.fn(),
    queryKeys: {
        health: ['health'],
        stats: ['stats'],
        recommendations: vi.fn(() => ['recommendations']),
    },
}))

const createWrapper = () => {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                retryDelay: 0,
            },
            mutations: {
                retry: false,
            },
        },
    })

    return ({ children }: { children: ReactNode }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    )
}

describe('useHealthCheck', () => {
    it('should fetch health check data', async () => {
        const mockHealth = {
            status: 'healthy',
            version: '1.0.0',
            timestamp: '2024-01-01T00:00:00Z',
        }

        vi.mocked(api.healthCheck).mockResolvedValue(mockHealth)

        const { result } = renderHook(() => useHealthCheck(), {
            wrapper: createWrapper(),
        })

        await waitFor(() => expect(result.current.isSuccess).toBe(true))

        expect(result.current.data).toEqual(mockHealth)
        expect(result.current.data?.status).toBe('healthy')
    })

    it('should handle health check error', async () => {
        vi.mocked(api.healthCheck).mockRejectedValue(new Error('Network error'))

        const { result } = renderHook(() => useHealthCheck(), {
            wrapper: createWrapper(),
        })

        await waitFor(() => expect(result.current.isError).toBe(true), {
            timeout: 3000
        })

        expect(result.current.error).toBeTruthy()
    })
})

describe('useStats', () => {
    it('should fetch stats data', async () => {
        const mockStats = {
            total_dealerships: 3,
            active_dealerships: 3,
            total_cars: 129,
            available_cars: 129,
            avg_price: 75000,
            price_range: { min: 40000, max: 120000 },
            cars_by_category: {},
            cars_by_brand: {},
            last_updated: '2024-01-01T00:00:00Z',
        }

        vi.mocked(api.getStats).mockResolvedValue(mockStats)

        const { result } = renderHook(() => useStats(), {
            wrapper: createWrapper(),
        })

        await waitFor(() => expect(result.current.isSuccess).toBe(true))

        expect(result.current.data).toEqual(mockStats)
        expect(result.current.data?.total_cars).toBe(129)
    })
})

describe('useRecommendations', () => {
    it('should successfully get recommendations', async () => {
        const mockResponse = {
            total_recommendations: 10,
            profile_summary: {
                budget_range: 'R$ 50.000 - R$ 100.000',
                usage: 'Família',
                location: 'São Paulo - SP',
                top_priorities: ['Segurança', 'Espaço'],
            },
            recommendations: [],
            execution_time_ms: 123,
        }

        vi.mocked(api.getRecommendations).mockResolvedValue(mockResponse)

        const { result } = renderHook(() => useRecommendations(), {
            wrapper: createWrapper(),
        })

        const mockProfile = {
            orcamento_min: 50000,
            orcamento_max: 100000,
            uso_principal: 'familia' as const,
            prioridades: {
                economia: 3,
                espaco: 5,
                performance: 2,
                conforto: 4,
                seguranca: 5,
            },
        }

        result.current.mutate(mockProfile)

        await waitFor(() => expect(result.current.isSuccess).toBe(true))

        expect(result.current.data).toEqual(mockResponse)
        expect(result.current.data?.total_recommendations).toBe(10)
    })

    it('should handle recommendations error', async () => {
        const mockError = {
            message: 'Erro ao buscar recomendações',
            detail: 'Invalid profile',
            status: 400,
        }

        vi.mocked(api.getRecommendations).mockRejectedValue(mockError)

        const { result } = renderHook(() => useRecommendations(), {
            wrapper: createWrapper(),
        })

        const mockProfile = {
            orcamento_min: 50000,
            orcamento_max: 100000,
            uso_principal: 'familia' as const,
            prioridades: {
                economia: 3,
                espaco: 3,
                performance: 3,
                conforto: 3,
                seguranca: 3,
            },
        }

        result.current.mutate(mockProfile)

        await waitFor(() => expect(result.current.isError).toBe(true))

        expect(result.current.error).toBeTruthy()
    })
})

