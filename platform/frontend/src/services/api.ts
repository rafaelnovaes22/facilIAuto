// 🤖 AI Engineer + 💻 Tech Lead: Service layer com guardrails
import axios, { AxiosError, AxiosInstance } from 'axios'
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

// ============================================
// AXIOS INSTANCE CONFIG
// ============================================

const api: AxiosInstance = axios.create({
    baseURL: '/api', // Proxy configurado no Vite
    timeout: 30000, // 30s timeout
    headers: {
        'Content-Type': 'application/json',
    },
})

// ============================================
// INTERCEPTORS - ERROR HANDLING
// ============================================

// 🤖 AI Engineer: Guardrails de erro
api.interceptors.response.use(
    response => response,
    (error: AxiosError<ApiError>) => {
        // Tratar erros de forma consistente
        const apiError: ApiError = {
            message: error.response?.data?.message || error.message || 'Erro desconhecido',
            detail: error.response?.data?.detail,
            status: error.response?.status || 500,
        }

        // Log para debugging (remover em produção)
        console.error('API Error:', apiError)

        return Promise.reject(apiError)
    }
)

// ============================================
// HEALTH & STATS
// ============================================

export const healthCheck = async (): Promise<HealthCheck> => {
    const { data } = await api.get<HealthCheck>('/health')
    return data
}

export const getStats = async (): Promise<Stats> => {
    const { data } = await api.get<Stats>('/stats')
    return data
}

// ============================================
// DEALERSHIPS
// ============================================

export const getDealerships = async (activeOnly = true): Promise<Dealership[]> => {
    const { data } = await api.get<Dealership[]>('/dealerships', {
        params: { active_only: activeOnly },
    })
    return data
}

export const getDealership = async (dealershipId: string): Promise<Dealership> => {
    const { data } = await api.get<Dealership>(`/dealerships/${dealershipId}`)
    return data
}

// ============================================
// CARS
// ============================================

export const getCars = async (filters?: CarFilter): Promise<Car[]> => {
    const { data } = await api.get<Car[]>('/cars', {
        params: filters,
    })
    return data
}

export const getCar = async (carId: string): Promise<Car> => {
    const { data } = await api.get<Car>(`/cars/${carId}`)
    return data
}

// ============================================
// RECOMMENDATIONS (CORE FEATURE)
// ============================================

// 🤖 AI Engineer: Validação de input antes de enviar
const validateUserProfile = (profile: UserProfile): void => {
    // Orçamento
    if (profile.orcamento_min <= 0 || profile.orcamento_max <= 0) {
        throw new Error('Orçamento deve ser maior que zero')
    }

    if (profile.orcamento_min > profile.orcamento_max) {
        throw new Error('Orçamento mínimo não pode ser maior que o máximo')
    }

    // Prioridades (1-5)
    const prioridades = Object.values(profile.prioridades)
    if (prioridades.some(p => p < 1 || p > 5)) {
        throw new Error('Prioridades devem estar entre 1 e 5')
    }

    // Tamanho família
    if (profile.tamanho_familia !== undefined && profile.tamanho_familia < 1) {
        throw new Error('Tamanho da família deve ser pelo menos 1')
    }
}

export const getRecommendations = async (
    profile: UserProfile
): Promise<RecommendationResponse> => {
    try {
        // 🤖 AI Engineer: Validar antes de enviar
        validateUserProfile(profile)

        const { data } = await api.post<RecommendationResponse>(
            '/recommend',
            profile
        )

        // 🤖 AI Engineer: Validar resposta
        if (!data.recommendations || data.recommendations.length === 0) {
            console.warn('Nenhuma recomendação retornada pela API')
        }

        return data
    } catch (error) {
        // Se for erro de validação, lançar com mensagem amigável
        if (error instanceof Error) {
            throw {
                message: 'Erro ao buscar recomendações',
                detail: error.message,
                status: 400,
            } as ApiError
        }
        throw error
    }
}

// ============================================
// REACT QUERY KEYS
// ============================================

// 💻 Tech Lead: Chaves consistentes para React Query
export const queryKeys = {
    health: ['health'] as const,
    stats: ['stats'] as const,
    dealerships: (activeOnly?: boolean) =>
        ['dealerships', { activeOnly }] as const,
    dealership: (id: string) => ['dealership', id] as const,
    cars: (filters?: CarFilter) => ['cars', filters] as const,
    car: (id: string) => ['car', id] as const,
    recommendations: (profile: UserProfile) =>
        ['recommendations', profile] as const,
}

// ============================================
// HELPER FUNCTIONS
// ============================================

// 💻 Tech Lead: Helpers para formatação
export const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value)
}

export const formatNumber = (value: number): string => {
    return new Intl.NumberFormat('pt-BR').format(value)
}

export const formatPercentage = (value: number): string => {
    return `${Math.round(value)}%`
}

// 🤖 AI Engineer: Helper para verificar status da API
export const checkApiHealth = async (): Promise<boolean> => {
    try {
        const health = await healthCheck()
        return health.status === 'healthy'
    } catch {
        return false
    }
}

// 🤖 AI Engineer: Retry logic para requisições críticas
export const withRetry = async <T>(
    fn: () => Promise<T>,
    maxRetries = 3,
    delay = 1000
): Promise<T> => {
    let lastError: Error | null = null

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await fn()
        } catch (error) {
            lastError = error as Error

            if (attempt < maxRetries) {
                console.warn(`Tentativa ${attempt} falhou, tentando novamente...`)
                await new Promise(resolve => setTimeout(resolve, delay * attempt))
            }
        }
    }

    throw lastError
}

// ============================================
// EXPORTS
// ============================================

export default api

