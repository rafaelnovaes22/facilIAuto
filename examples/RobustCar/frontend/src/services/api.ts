import axios from 'axios'
import { UserProfile, Recommendation, EstoqueStats, Car } from '../types'

// Configuração da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptors para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    
    if (error.response?.status === 503) {
      throw new Error('Sistema temporariamente indisponível. Tente novamente em alguns minutos.')
    }
    
    if (error.response?.status === 404) {
      throw new Error('Nenhuma recomendação encontrada para seu perfil. Tente ajustar seus critérios.')
    }
    
    if (error.code === 'ECONNABORTED') {
      throw new Error('Tempo limite excedido. Verifique sua conexão.')
    }
    
    throw new Error(error.response?.data?.detail || 'Erro interno do servidor')
  }
)

// Serviços da API
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  // Obter estatísticas do estoque
  async getEstoqueStats(): Promise<EstoqueStats> {
    const response = await api.get('/estoque/stats')
    return response.data
  },

  // Buscar carros com filtros
  async buscarCarros(filtros: {
    marca?: string
    categoria?: string
    preco_min?: number
    preco_max?: number
    limit?: number
  }) {
    const params = new URLSearchParams()
    
    Object.entries(filtros).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString())
      }
    })
    
    const response = await api.get(`/carros/buscar?${params}`)
    return response.data
  },

  // Gerar recomendações (endpoint principal)
  async gerarRecomendacoes(perfil: UserProfile): Promise<Recommendation[]> {
    const response = await api.post('/recomendar', perfil)
    return response.data
  },

  // Obter marcas disponíveis
  async getMarcas(): Promise<string[]> {
    const response = await api.get('/marcas')
    return response.data.marcas
  },

  // Obter categorias disponíveis
  async getCategorias(): Promise<string[]> {
    const response = await api.get('/categorias')
    return response.data.categorias
  },

  // Admin: Atualizar estoque
  async atualizarEstoque() {
    const response = await api.post('/admin/atualizar-estoque')
    return response.data
  },
}

export default api
