// 💻 Tech Lead: State management com Zustand
import { create } from 'zustand'
import type { QuestionnaireFormData, UserProfile } from '@/types'

interface QuestionnaireStore {
  // Current step (0-3)
  currentStep: number

  // Form data
  formData: Partial<QuestionnaireFormData>

  // Actions
  setCurrentStep: (step: number) => void
  nextStep: () => void
  previousStep: () => void
  updateFormData: (data: Partial<QuestionnaireFormData>) => void
  resetForm: () => void

  // Computed
  canGoNext: () => boolean
  isComplete: () => boolean
  toUserProfile: () => UserProfile
}

const initialFormData: Partial<QuestionnaireFormData> = {
  orcamento_min: 50000,
  orcamento_max: 100000,
  ano_minimo: undefined,
  ano_maximo: undefined,
  city: undefined,
  state: undefined,
  uso_principal: 'familia',
  tamanho_familia: 1,
  tem_criancas: false,
  tem_idosos: false,
  faixa_salarial: null,
  prioridades: {
    economia: 3,
    espaco: 3,
    performance: 3,
    conforto: 3,
    seguranca: 3,
  },
  tipos_preferidos: [],
  marcas_preferidas: [],
  cambio_preferido: undefined,
}

export const useQuestionnaireStore = create<QuestionnaireStore>((set, get) => ({
  currentStep: 0,
  formData: initialFormData,

  setCurrentStep: (step) => set({ currentStep: step }),

  nextStep: () => {
    const { currentStep } = get()
    if (currentStep < 3) {
      set({ currentStep: currentStep + 1 })
    }
  },

  previousStep: () => {
    const { currentStep } = get()
    if (currentStep > 0) {
      set({ currentStep: currentStep - 1 })
    }
  },

  updateFormData: (data) => {
    set((state) => ({
      formData: { ...state.formData, ...data },
    }))
  },

  resetForm: () => {
    set({
      currentStep: 0,
      formData: initialFormData,
    })
  },

  canGoNext: () => {
    const { currentStep, formData } = get()

    switch (currentStep) {
      case 0: // Orçamento + Localização
        return (
          formData.orcamento_min !== undefined &&
          formData.orcamento_max !== undefined &&
          formData.orcamento_min > 0 &&
          formData.orcamento_max > formData.orcamento_min
        )
      case 1: // Uso + Família
        return (
          formData.uso_principal !== undefined &&
          formData.tamanho_familia !== undefined &&
          formData.tamanho_familia > 0
        )
      case 2: // Prioridades
        // Verificar se pelo menos 1 prioridade foi selecionada (valor 5)
        const priorities = formData.prioridades
        if (!priorities) return false
        const selectedCount = Object.values(priorities).filter(v => v === 5).length
        return selectedCount >= 1 && selectedCount <= 3
      case 3: // Preferências (opcional)
        return true
      default:
        return false
    }
  },

  isComplete: () => {
    const { formData } = get()
    return (
      formData.orcamento_min !== undefined &&
      formData.orcamento_max !== undefined &&
      formData.uso_principal !== undefined &&
      formData.tamanho_familia !== undefined &&
      formData.prioridades !== undefined
    )
  },

  toUserProfile: (): UserProfile => {
    const { formData } = get()

    return {
      orcamento_min: formData.orcamento_min || 50000,
      orcamento_max: formData.orcamento_max || 100000,
      city: formData.city,
      state: formData.state,
      priorizar_proximas: !!formData.city,
      uso_principal: formData.uso_principal || 'familia',
      frequencia_uso: 'diaria',
      tamanho_familia: formData.tamanho_familia || 1,
      necessita_espaco: (formData.tamanho_familia || 1) >= 3,
      tem_criancas: formData.tem_criancas || false,
      tem_idosos: formData.tem_idosos || false,
      prioridades: formData.prioridades || {
        economia: 3,
        espaco: 3,
        performance: 3,
        conforto: 3,
        seguranca: 3,
      },
      marcas_preferidas: formData.marcas_preferidas || [],
      marcas_rejeitadas: [],
      tipos_preferidos: formData.tipos_preferidos || [],
      cambio_preferido: formData.cambio_preferido,
      ano_minimo: formData.ano_minimo,
      ano_maximo: formData.ano_maximo,
      primeiro_carro: false,
    }
  },
}))

