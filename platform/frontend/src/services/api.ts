// 🤖 AI Engineer + 💻 Tech Lead: Service layer com guardrails
import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { API_URL } from '@/config/env'
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
// SESSION ID FOR TRACEABILITY
// ============================================

// Generate unique session ID for tracking requests across the user session
const SESSION_ID = `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`

// ============================================
// AXIOS INSTANCE CONFIG
// ============================================

const api: AxiosInstance = axios.create({
    baseURL: API_URL, // Use validated environment variable from config
    timeout: 30000, // 30s timeout
    headers: {
        'Content-Type': 'application/json',
    },
})

// ============================================
// INTERCEPTORS - REQUEST LOGGING
// ============================================

// Request interceptor for detailed logging
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const timestamp = new Date().toISOString()
        const method = config.method?.toUpperCase() || 'UNKNOWN'
        const url = `${config.baseURL}${config.url}`

        console.log(`[API Request] ${timestamp} | session_id: ${SESSION_ID} | ${method} ${url}`, {
            params: config.params,
            data: config.data,
        })

        return config
    },
    (error: AxiosError) => {
        console.error(`[API Request Error] session_id: ${SESSION_ID}`, error)
        return Promise.reject(error)
    }
)

// ============================================
// INTERCEPTORS - RESPONSE ERROR HANDLING
// ============================================

// Response interceptor with specific error handling by type
api.interceptors.response.use(
    response => {
        const timestamp = new Date().toISOString()
        const status = response.status
        const url = response.config.url

        console.log(`[API Response] ${timestamp} | session_id: ${SESSION_ID} | ${status} ${url}`)

        return response
    },
    (error: AxiosError<ApiError>) => {
        const timestamp = new Date().toISOString()

        // Determine error type and create appropriate error object
        let apiError: ApiError

        if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
            // Network timeout
            apiError = {
                message: 'Servidor não respondeu. Verifique sua conexão.',
                detail: 'Timeout ao conectar com o servidor',
                status: 0,
                code: error.code,
            }
            console.error(`[API Error - Timeout] ${timestamp} | session_id: ${SESSION_ID}`, {
                code: error.code,
                url: error.config?.url,
            })
        } else if (!error.response) {
            // Network error (no response received)
            apiError = {
                message: 'Erro de conexão com servidor',
                detail: 'Não foi possível conectar ao servidor. Verifique sua conexão.',
                status: 0,
                code: 'NETWORK_ERROR',
            }
            console.error(`[API Error - Network] ${timestamp} | session_id: ${SESSION_ID}`, {
                message: error.message,
                url: error.config?.url,
            })
        } else if (error.response.status === 405) {
            // Method not allowed - configuration issue
            apiError = {
                message: 'Erro no servidor',
                detail: 'Problema de configuração da API. Nossa equipe foi notificada.',
                status: 405,
                code: 'METHOD_NOT_ALLOWED',
            }
            console.error(`[API Error - 405] ${timestamp} | session_id: ${SESSION_ID}`, {
                method: error.config?.method,
                url: error.config?.url,
                baseURL: error.config?.baseURL,
            })
        } else if (error.response.status === 500) {
            // Server error
            apiError = {
                message: 'Erro ao processar sua busca',
                detail: error.response.data?.detail || 'Erro interno do servidor',
                status: 500,
                code: 'SERVER_ERROR',
            }
            console.error(`[API Error - 500] ${timestamp} | session_id: ${SESSION_ID}`, {
                url: error.config?.url,
                detail: error.response.data?.detail,
            })
        } else if (error.response.status === 400) {
            // Bad request - validation error
            apiError = {
                message: error.response.data?.message || 'Dados inválidos',
                detail: error.response.data?.detail || 'Verifique os dados informados',
                status: 400,
                code: 'VALIDATION_ERROR',
            }
            console.error(`[API Error - 400] ${timestamp} | session_id: ${SESSION_ID}`, {
                url: error.config?.url,
                detail: error.response.data?.detail,
            })
        } else {
            // Other errors
            apiError = {
                message: error.response.data?.message || error.message || 'Erro desconhecido',
                detail: error.response.data?.detail,
                status: error.response.status || 500,
                code: 'UNKNOWN_ERROR',
            }
            console.error(`[API Error - ${error.response.status}] ${timestamp} | session_id: ${SESSION_ID}`, {
                url: error.config?.url,
                status: error.response.status,
                detail: error.response.data,
            })
        }

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

export const getBrandsWithModels = async (): Promise<Record<string, string[]>> => {
    const { data } = await api.get<Record<string, string[]>>('/brands-models')
    return data
}

export const uploadCarImage = async (
    dealershipId: string,
    carId: string,
    file: File
): Promise<{ url: string; filename: string }> => {
    const formData = new FormData()
    formData.append('file', file)

    const { data } = await api.post<{ url: string; filename: string }>(
        `/api/dealerships/${dealershipId}/cars/${carId}/images`,
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        }
    )
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

        // Use /recommend (without /api prefix) - backend has both routes but /recommend is primary
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
    brandsModels: ['brands-models'] as const,
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

