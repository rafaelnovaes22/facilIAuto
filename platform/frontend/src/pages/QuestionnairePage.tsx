// 🎨 UX + 🤖 AI Engineer + ✍️ Content: Questionário completo
import {
  Box,
  Container,
  VStack,
  HStack,
  Button,
  useToast,
} from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { FaArrowLeft, FaArrowRight, FaCheck } from 'react-icons/fa'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { useRecommendations } from '@/hooks/useApi'
import { ProgressIndicator } from '@/components/questionnaire/ProgressIndicator'
import { Step1Budget } from '@/components/questionnaire/Step1Budget'
import { Step2Usage } from '@/components/questionnaire/Step2Usage'
import { Step3Priorities } from '@/components/questionnaire/Step3Priorities'
import { Step4Preferences } from '@/components/questionnaire/Step4Preferences'

const STEP_TITLES = [
  'Orçamento',
  'Uso e Família',
  'Prioridades',
  'Preferências',
]

export default function QuestionnairePage() {
  const navigate = useNavigate()
  const toast = useToast()
  const {
    currentStep,
    previousStep,
    nextStep,
    canGoNext,
    isComplete,
    toUserProfile,
    resetForm,
  } = useQuestionnaireStore()

  const { mutate: getRecommendations, isPending } = useRecommendations()

  // Sync URL with current step
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const urlStep = params.get('step')

    if (urlStep) {
      const stepNumber = parseInt(urlStep, 10) - 1
      if (stepNumber >= 0 && stepNumber <= 3 && stepNumber !== currentStep) {
        // Don't update if it's the same step
        return
      }
    }

    // Update URL when step changes
    const newParams = new URLSearchParams()
    newParams.set('step', (currentStep + 1).toString())
    window.history.replaceState({}, '', `?${newParams.toString()}`)
  }, [currentStep])

  // Restore step from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const urlStep = params.get('step')

    if (urlStep) {
      const stepNumber = parseInt(urlStep, 10) - 1
      if (stepNumber >= 0 && stepNumber <= 3) {
        useQuestionnaireStore.getState().setCurrentStep(stepNumber)
      }
    }
  }, [])

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement ||
        e.target instanceof HTMLSelectElement
      ) {
        return
      }

      // Enter key - go to next step
      if (e.key === 'Enter' && canGoNext() && !isPending) {
        e.preventDefault()
        handleNext()
      }

      // Escape key - go to previous step
      if (e.key === 'Escape' && currentStep > 0) {
        e.preventDefault()
        previousStep()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentStep, canGoNext, isPending])

  const handleNext = () => {
    if (currentStep === 3) {
      // Última etapa - buscar recomendações
      handleSubmit()
    } else {
      nextStep()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const handleResetAndGoHome = () => {
    console.log('Reset: Usuário voltando ao início do questionário')
    resetForm() // Limpa todos os dados e volta para step 0
    navigate('/') // Volta para a home
  }

  const handleSubmit = () => {
    if (!isComplete()) {
      toast({
        title: 'Formulário incompleto',
        description: 'Por favor, preencha todos os campos obrigatórios',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    const userProfile = toUserProfile()

    getRecommendations(userProfile, {
      onSuccess: (data) => {
        // Validar se recebemos dados válidos
        if (!data || !data.profile_summary) {
          toast({
            title: 'Erro ao processar recomendações',
            description: 'Não foi possível processar sua busca. Tente novamente.',
            status: 'error',
            duration: 5000,
            isClosable: true,
          })
          return
        }

        // Mostrar mensagem apropriada
        if (data.total_recommendations === 0) {
          toast({
            title: 'Nenhum carro encontrado',
            description: 'Não encontramos carros que atendam aos seus critérios. Vamos ajustar sua busca.',
            status: 'info',
            duration: 4000,
            isClosable: true,
          })
        } else {
          toast({
            title: 'Recomendações encontradas!',
            description: `${data.total_recommendations} carros perfeitos para você`,
            status: 'success',
            duration: 3000,
            isClosable: true,
          })
        }

        // Navegar para resultados com dados
        navigate('/resultados', { state: { recommendations: data } })
      },
      onError: (error) => {
        console.error('Erro na API:', error)

        // Mensagem de erro mais amigável
        let errorMessage = 'Não foi possível buscar recomendações. Tente novamente.'

        if (error?.detail?.includes('cidade') || error?.detail?.includes('estado')) {
          errorMessage = 'Não temos concessionárias na região selecionada. Tente outra cidade ou estado.'
        } else if (error?.status === 500) {
          errorMessage = 'Erro no servidor. Nossa equipe já foi notificada.'
        } else if (error?.message) {
          errorMessage = error.message
        }

        toast({
          title: 'Erro ao buscar recomendações',
          description: errorMessage,
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      },
    })
  }

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <Step1Budget />
      case 1:
        return <Step2Usage />
      case 2:
        return <Step3Priorities />
      case 3:
        return <Step4Preferences />
      default:
        return null
    }
  }

  return (
    <Box bg="gray.50" minH="100vh" py={10}>
      <Container maxW="container.lg">
        <VStack spacing={10}>
          {/* Progress Indicator */}
          <ProgressIndicator
            currentStep={currentStep}
            totalSteps={4}
            stepTitles={STEP_TITLES}
          />

          {/* Current Step Content */}
          <Box
            w="full"
            bg="white"
            p={{ base: 6, md: 10 }}
            borderRadius="2xl"
            boxShadow="lg"
            minH="500px"
          >
            {renderStep()}
          </Box>

          {/* Navigation Buttons */}
          <HStack w="full" justify="space-between" maxW="600px">
            {/* Botão Voltar */}
            <Button
              size="lg"
              variant="outline"
              leftIcon={<FaArrowLeft />}
              onClick={previousStep}
              isDisabled={currentStep === 0}
            >
              Voltar
            </Button>

            {/* Botão Próximo/Finalizar */}
            <Button
              size="lg"
              colorScheme="brand"
              rightIcon={currentStep === 3 ? <FaCheck /> : <FaArrowRight />}
              onClick={handleNext}
              isDisabled={!canGoNext()}
              isLoading={isPending}
              loadingText="Buscando..."
              px={8}
            >
              {currentStep === 3 ? 'Ver Recomendações' : 'Próximo'}
            </Button>
          </HStack>

          {/* Back to Home Link */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleResetAndGoHome}
            color="gray.600"
          >
            ← Voltar para o início
          </Button>
        </VStack>
      </Container>
    </Box>
  )
}
