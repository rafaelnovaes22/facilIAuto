// Tipos para API da RobustCar

export interface Car {
  id: string
  nome: string
  marca: string
  modelo: string
  ano: number
  preco: number
  quilometragem: number
  combustivel: string
  cambio: string
  cor: string
  categoria: string
  imagens: string[]
  url_original: string
  disponivel: boolean
}

export interface Recommendation {
  carro: Car
  score: number
  justificativa: string
  pontos_fortes: string[]
  pontos_atencao: string[]
  match_percentage: number
}

export interface UserProfile {
  orcamento_min: number
  orcamento_max: number
  uso_principal: 'trabalho' | 'familia' | 'lazer' | 'primeiro_carro'
  tamanho_familia: number
  prioridades: {
    economia: number
    espaco: number
    performance: number
    conforto: number
    seguranca: number
  }
  marcas_preferidas: string[]
  tipos_preferidos: string[]
  combustivel_preferido: string
  idade_usuario: number
  experiencia_conducao: 'iniciante' | 'intermediario' | 'experiente'
}

export interface EstoqueStats {
  total_carros: number
  preco_medio: number
  por_marca: Record<string, number>
  por_categoria: Record<string, number>
  por_faixa_preco: Record<string, number>
  ultima_atualizacao: string
}

export interface QuestionnaireStep {
  id: string
  title: string
  description: string
  component: React.ComponentType<any>
  isValid?: (data: Partial<UserProfile>) => boolean
}

export interface ApiResponse<T> {
  data?: T
  error?: string
  loading: boolean
}
