// 💻 Tech Lead: Custom hooks com React Query
import { useQuery, useMutation, UseQueryResult, UseMutationResult } from '@tanstack/react-query'
import type {
    Car,
    CarFilter,
    Dealership,
    HealthCheck,
    Stats,
    UserProfile,
    RecommendationResponse,
    ApiError,
} from '@/types'
import {
    healthCheck,
    getStats,
    getDealerships,
    getDealership,
    getCars,
    getCar,
    getRecommendations,
    queryKeys,
} from '@/services/api'

// ============================================
// HEALTH & STATS HOOKS
// ============================================

export const useHealthCheck = (): UseQueryResult<HealthCheck, ApiError> => {
    return useQuery({
        queryKey: queryKeys.health,
        queryFn: healthCheck,
        staleTime: 60 * 1000, // 1 minuto
        retry: 3,
    })
}

export const useStats = (): UseQueryResult<Stats, ApiError> => {
    return useQuery({
        queryKey: queryKeys.stats,
        queryFn: getStats,
        staleTime: 0, // Sempre buscar dados frescos
        cacheTime: 0, // Não fazer cache
    })
}

// ============================================
// DEALERSHIPS HOOKS
// ============================================

export const useDealerships = (
    activeOnly = true
): UseQueryResult<Dealership[], ApiError> => {
    return useQuery({
        queryKey: queryKeys.dealerships(activeOnly),
        queryFn: () => getDealerships(activeOnly),
        staleTime: 10 * 60 * 1000, // 10 minutos
    })
}

export const useDealership = (
    dealershipId: string
): UseQueryResult<Dealership, ApiError> => {
    return useQuery({
        queryKey: queryKeys.dealership(dealershipId),
        queryFn: () => getDealership(dealershipId),
        enabled: !!dealershipId,
        staleTime: 10 * 60 * 1000,
    })
}

// ============================================
// CARS HOOKS
// ============================================

export const useCars = (
    filters?: CarFilter
): UseQueryResult<Car[], ApiError> => {
    return useQuery({
        queryKey: queryKeys.cars(filters),
        queryFn: () => getCars(filters),
        staleTime: 5 * 60 * 1000, // 5 minutos
    })
}

export const useCar = (carId: string): UseQueryResult<Car, ApiError> => {
    return useQuery({
        queryKey: queryKeys.car(carId),
        queryFn: () => getCar(carId),
        enabled: !!carId,
        staleTime: 10 * 60 * 1000,
    })
}

// ============================================
// RECOMMENDATIONS HOOK (CORE)
// ============================================

// 🤖 AI Engineer: Hook principal com guardrails
export const useRecommendations = (): UseMutationResult<
    RecommendationResponse,
    ApiError,
    UserProfile
> => {
    return useMutation({
        mutationFn: getRecommendations,
        onError: (error: ApiError) => {
            console.error('Erro ao buscar recomendações:', error)
            // Aqui poderia adicionar tracking de erros (Sentry, etc)
        },
        onSuccess: (data) => {
            console.log(`${data.total_recommendations} recomendações encontradas`)
            // Aqui poderia adicionar analytics
        },
    })
}

// ============================================
// UTILITY HOOKS
// ============================================

// 💻 Tech Lead: Hook para verificar se API está online
export const useApiStatus = () => {
    const { data, isLoading, isError } = useHealthCheck()

    return {
        isOnline: data?.status === 'healthy',
        isLoading,
        isError,
        version: data?.version,
    }
}

// 🤖 AI Engineer: Hook para estatísticas agregadas
export const useAggregatedStats = () => {
    const { data: stats, isLoading } = useStats()
    const { data: dealerships } = useDealerships()

    if (isLoading || !stats) {
        return { isLoading: true }
    }

    return {
        isLoading: false,
        totalCars: stats.total_cars || 0,
        totalDealerships: stats.total_dealerships || 0,
        avgPrice: stats.avg_price || 0,
        priceRange: stats.price_range || { min: 0, max: 0 },
        topCategories: stats.cars_by_category
            ? Object.entries(stats.cars_by_category)
                .sort(([, a], [, b]) => (b as number) - (a as number))
                .slice(0, 5)
            : [],
        topBrands: stats.cars_by_brand
            ? Object.entries(stats.cars_by_brand)
                .sort(([, a], [, b]) => (b as number) - (a as number))
                .slice(0, 5)
            : [],
        dealershipsList: dealerships || [],
    }
}

