// 💻 Tech Lead + 🤖 AI Engineer: TDD - Zustand store tests
import { describe, it, expect, beforeEach } from 'vitest'
import { useQuestionnaireStore } from '../questionnaireStore'

describe('QuestionnaireStore', () => {
    beforeEach(() => {
        // Reset store antes de cada teste
        useQuestionnaireStore.setState({
            currentStep: 0,
            formData: {
                orcamento_min: 50000,
                orcamento_max: 100000,
                uso_principal: 'familia',
                tamanho_familia: 1,
                tem_criancas: false,
                tem_idosos: false,
                prioridades: {
                    economia: 3,
                    espaco: 3,
                    performance: 3,
                    conforto: 3,
                    seguranca: 3,
                },
            },
        })
    })

    describe('Navigation', () => {
        it('should start at step 0', () => {
            const { currentStep } = useQuestionnaireStore.getState()
            expect(currentStep).toBe(0)
        })

        it('should advance to next step', () => {
            const { nextStep } = useQuestionnaireStore.getState()
            nextStep()
            const { currentStep } = useQuestionnaireStore.getState()
            expect(currentStep).toBe(1)
        })

        it('should go back to previous step', () => {
            const store = useQuestionnaireStore.getState()
            store.nextStep()
            store.previousStep()
            const { currentStep } = useQuestionnaireStore.getState()
            expect(currentStep).toBe(0)
        })

        it('should not go below step 0', () => {
            const { previousStep } = useQuestionnaireStore.getState()
            previousStep()
            previousStep()
            const { currentStep } = useQuestionnaireStore.getState()
            expect(currentStep).toBe(0)
        })

        it('should not go above step 3', () => {
            const store = useQuestionnaireStore.getState()
            store.nextStep()
            store.nextStep()
            store.nextStep()
            store.nextStep() // Tentar ir para step 4
            const { currentStep } = useQuestionnaireStore.getState()
            expect(currentStep).toBe(3)
        })

        it('should set specific step', () => {
            const { setCurrentStep } = useQuestionnaireStore.getState()
            setCurrentStep(2)
            const { currentStep } = useQuestionnaireStore.getState()
            expect(currentStep).toBe(2)
        })
    })

    describe('Form Data', () => {
        it('should update form data', () => {
            const { updateFormData } = useQuestionnaireStore.getState()
            updateFormData({ orcamento_min: 70000 })
            const { formData } = useQuestionnaireStore.getState()
            expect(formData.orcamento_min).toBe(70000)
        })

        it('should merge form data', () => {
            const { updateFormData } = useQuestionnaireStore.getState()
            updateFormData({ city: 'São Paulo', state: 'SP' })
            const { formData } = useQuestionnaireStore.getState()
            expect(formData.city).toBe('São Paulo')
            expect(formData.state).toBe('SP')
            expect(formData.orcamento_min).toBe(50000) // Mantém valores existentes
        })

        it('should reset form', () => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({ city: 'São Paulo' })
            store.nextStep()
            store.resetForm()

            const { currentStep, formData } = useQuestionnaireStore.getState()
            expect(currentStep).toBe(0)
            expect(formData.city).toBeUndefined()
        })
    })

    describe('Validation - Step 0 (Orçamento)', () => {
        it('should allow next if budget is valid', () => {
            const { canGoNext } = useQuestionnaireStore.getState()
            expect(canGoNext()).toBe(true)
        })

        it('should not allow next if min > max', () => {
            const { updateFormData, canGoNext } = useQuestionnaireStore.getState()
            updateFormData({ orcamento_min: 100000, orcamento_max: 50000 })
            expect(canGoNext()).toBe(false)
        })

        it('should not allow next if budget is zero', () => {
            const { updateFormData, canGoNext } = useQuestionnaireStore.getState()
            updateFormData({ orcamento_min: 0 })
            expect(canGoNext()).toBe(false)
        })
    })

    describe('Validation - Step 1 (Uso)', () => {
        it('should allow next if usage and family size are set', () => {
            const store = useQuestionnaireStore.getState()
            store.setCurrentStep(1)
            expect(store.canGoNext()).toBe(true)
        })

        it('should not allow next if family size is 0', () => {
            const store = useQuestionnaireStore.getState()
            store.setCurrentStep(1)
            store.updateFormData({ tamanho_familia: 0 })
            expect(store.canGoNext()).toBe(false)
        })
    })

    describe('Validation - Step 2 (Prioridades)', () => {
        it('should always allow next (has defaults)', () => {
            const store = useQuestionnaireStore.getState()
            store.setCurrentStep(2)
            expect(store.canGoNext()).toBe(true)
        })
    })

    describe('Validation - Step 3 (Preferências)', () => {
        it('should always allow next (optional)', () => {
            const store = useQuestionnaireStore.getState()
            store.setCurrentStep(3)
            expect(store.canGoNext()).toBe(true)
        })
    })

    describe('Completion', () => {
        it('should be complete with all required fields', () => {
            const { isComplete } = useQuestionnaireStore.getState()
            expect(isComplete()).toBe(true)
        })

        it('should not be complete without budget', () => {
            const { updateFormData, isComplete } = useQuestionnaireStore.getState()
            updateFormData({ orcamento_min: undefined })
            expect(isComplete()).toBe(false)
        })
    })

    describe('Convert to UserProfile', () => {
        it('should convert form data to user profile', () => {
            const store = useQuestionnaireStore.getState()
            store.updateFormData({
                orcamento_min: 60000,
                orcamento_max: 90000,
                city: 'São Paulo',
                state: 'SP',
                uso_principal: 'trabalho',
                tamanho_familia: 2,
            })

            const profile = store.toUserProfile()

            expect(profile.orcamento_min).toBe(60000)
            expect(profile.orcamento_max).toBe(90000)
            expect(profile.city).toBe('São Paulo')
            expect(profile.state).toBe('SP')
            expect(profile.uso_principal).toBe('trabalho')
            expect(profile.tamanho_familia).toBe(2)
        })

        it('should set priorizar_proximas based on city', () => {
            const store = useQuestionnaireStore.getState()

            // Com cidade
            store.updateFormData({ city: 'São Paulo' })
            let profile = store.toUserProfile()
            expect(profile.priorizar_proximas).toBe(true)

            // Sem cidade
            store.updateFormData({ city: undefined })
            profile = store.toUserProfile()
            expect(profile.priorizar_proximas).toBe(false)
        })

        it('should set necessita_espaco for families 3+', () => {
            const store = useQuestionnaireStore.getState()

            store.updateFormData({ tamanho_familia: 4 })
            const profile = store.toUserProfile()
            expect(profile.necessita_espaco).toBe(true)
        })

        it('should use default values for optional fields', () => {
            const { toUserProfile } = useQuestionnaireStore.getState()
            const profile = toUserProfile()

            expect(profile.frequencia_uso).toBe('diaria')
            expect(profile.marcas_preferidas).toEqual([])
            expect(profile.tipos_preferidos).toEqual([])
            expect(profile.primeiro_carro).toBe(false)
        })
    })
})

