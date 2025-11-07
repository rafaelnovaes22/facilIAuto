// 💻 Tech Lead: Types sincronizados com backend Python

// ============================================
// CAR TYPES
// ============================================

export interface Car {
    // Identificação
    id: string
    dealership_id: string

    // Informações básicas
    nome: string
    marca: string
    modelo: string
    versao?: string
    ano: number

    // Preço e condições
    preco: number
    quilometragem: number

    // Características
    combustivel: string // "Flex", "Gasolina", "Diesel", "Elétrico"
    cambio?: string // "Manual", "Automático", "CVT"
    cor?: string
    portas?: number

    // Categorização
    categoria: string // "Hatch", "Sedan", "SUV", "Pickup", "Compacto"

    // Scores de IA (0.0 a 1.0)
    score_familia: number
    score_economia: number
    score_performance: number
    score_conforto: number
    score_seguranca: number

    // Mídia
    imagens: string[]
    url_original?: string

    // Status
    disponivel: boolean
    destaque: boolean

    // Metadata
    data_scraping?: string
    data_atualizacao?: string

    // Informações da concessionária (denormalizado)
    dealership_name: string
    dealership_city: string
    dealership_state: string
    dealership_phone: string
    dealership_whatsapp: string
}

export interface CarFilter {
    preco_min?: number
    preco_max?: number
    marca?: string
    categoria?: string
    combustivel?: string
    ano_min?: number
    km_max?: number
    city?: string
    state?: string
    dealership_id?: string
}

// ============================================
// DEALERSHIP TYPES
// ============================================

export interface Dealership {
    id: string
    name: string
    city: string
    state: string
    region: string

    // Contato
    phone: string
    whatsapp: string
    email?: string
    website?: string

    // Branding
    logo_url?: string
    primary_color?: string

    // Address
    address?: string
    zip_code?: string

    // Status
    active: boolean
    verified: boolean
    premium: boolean

    // Metadata
    created_at?: string
    updated_at?: string

    // Stats
    total_cars?: number
    avg_price?: number
}

export interface DealershipStats {
    dealership_id: string
    total_cars: number
    active_cars: number
    avg_price: number
    price_min: number
    price_max: number
    total_recommendations: number
    conversion_rate: number
    last_updated: string
}

// ============================================
// USER PROFILE TYPES
// ============================================

export interface FinancialCapacity {
    monthly_income_range: string  // "0-3000", "3000-5000", "5000-8000", "8000-12000", "12000+"
    max_monthly_tco: number       // 30% da renda média
    is_disclosed: boolean         // true se informado, false se pulou
}

export interface UserProfile {
    // Orçamento
    orcamento_min: number
    orcamento_max: number

    // Localização
    city?: string
    state?: string
    priorizar_proximas?: boolean

    // Uso principal
    uso_principal: 'familia' | 'trabalho' | 'lazer' | 'comercial' | 'primeiro_carro' | 'transporte_passageiros'
    frequencia_uso?: 'diaria' | 'semanal' | 'eventual'

    // Composição familiar
    tamanho_familia?: number
    necessita_espaco?: boolean
    tem_criancas?: boolean
    tem_idosos?: boolean

    // Prioridades (1-5)
    prioridades: {
        economia: number
        espaco: number
        performance: number
        conforto: number
        seguranca: number
    }

    // Preferências
    marcas_preferidas?: string[]
    marcas_rejeitadas?: string[]
    tipos_preferidos?: string[]
    combustivel_preferido?: string
    cambio_preferido?: string

    // Filtros eliminatórios
    ano_minimo?: number
    ano_maximo?: number
    km_maxima?: number

    // Experiência
    primeiro_carro?: boolean
    experiencia_anos?: number

    // Capacidade financeira
    financial_capacity?: FinancialCapacity | null
}

// ============================================
// RECOMMENDATION TYPES
// ============================================

export interface TCOBreakdown {
    financing_monthly: number
    fuel_monthly: number
    maintenance_monthly: number
    insurance_monthly: number
    ipva_monthly: number
    total_monthly: number
    assumptions: {
        down_payment_percent: number
        financing_months: number
        annual_interest_rate: number
        monthly_km: number
        fuel_price_per_liter: number
        fuel_efficiency: number
        state: string
        maintenance_adjustment?: {
            factor: number
            reason: string
        }
    }
}

export interface Recommendation {
    car: Car
    match_score: number
    match_percentage: number
    justification: string
    tco_breakdown?: TCOBreakdown
    fits_budget?: boolean
    budget_percentage?: number
    financial_health?: {
        status: 'healthy' | 'caution' | 'high_commitment'
        percentage: number
        color: 'green' | 'yellow' | 'red'
        message: string
    }
}

export interface RecommendationResponse {
    total_recommendations: number
    profile_summary: {
        budget_range: string
        usage: string
        location: string
        top_priorities: string[]
    }
    recommendations: Recommendation[]
    execution_time_ms: number
}

// ============================================
// API RESPONSE TYPES
// ============================================

export interface ApiResponse<T> {
    data: T
    message?: string
    status: number
}

export interface ApiError {
    message: string
    detail?: string
    status: number
    code?: string  // Error code for specific error types (e.g., 'NETWORK_ERROR', 'TIMEOUT')
}

export interface HealthCheck {
    status: string
    version: string
    timestamp: string
}

export interface Stats {
    total_dealerships: number
    active_dealerships: number
    total_cars: number
    available_cars: number
    avg_price: number
    price_range: {
        min: number
        max: number
    }
    cars_by_category: Record<string, number>
    cars_by_brand: Record<string, number>
    last_updated: string
}

// ============================================
// FORM TYPES (Frontend specific)
// ============================================

export interface QuestionnaireFormData {
    // Step 1: Orçamento e Localização
    orcamento_min: number
    orcamento_max: number
    ano_minimo?: number
    ano_maximo?: number
    city?: string
    state?: string

    // Step 2: Uso e Família
    uso_principal: UserProfile['uso_principal']
    tamanho_familia: number
    tem_criancas: boolean
    tem_idosos: boolean
    faixa_salarial?: string | null  // "0-3000", "3000-5000", etc.

    // Step 3: Prioridades
    prioridades: UserProfile['prioridades']

    // Step 4: Preferências
    tipos_preferidos?: string[]
    marcas_preferidas?: string[]
    cambio_preferido?: string
}

// ============================================
// CONSTANTS
// ============================================

export const CATEGORIAS = [
    'Hatch',
    'Sedan',
    'SUV',
    'Pickup',
    'Compacto',
    'Van',
] as const

export const COMBUSTIVEIS = [
    'Flex',
    'Gasolina',
    'Diesel',
    'Elétrico',
    'Híbrido',
] as const

export const CAMBIOS = ['Manual', 'Automático', 'CVT'] as const

export const ESTADOS_BR = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
    'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
    'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO',
] as const

export const USOS_PRINCIPAIS = [
    'familia',
    'trabalho',
    'lazer',
    'comercial',
    'primeiro_carro',
    'transporte_passageiros',
] as const

export type Categoria = typeof CATEGORIAS[number]
export type Combustivel = typeof COMBUSTIVEIS[number]
export type Cambio = typeof CAMBIOS[number]
export type EstadoBR = typeof ESTADOS_BR[number]
export type UsoPrincipal = typeof USOS_PRINCIPAIS[number]

