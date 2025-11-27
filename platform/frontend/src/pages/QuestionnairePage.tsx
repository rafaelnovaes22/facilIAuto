// 🎨 UX + 🤖 AI Engineer + ✍️ Content: Questionário completo
import {
  Box,
  Container,
  VStack,
  HStack,
  Button,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Text,
} from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { FaArrowLeft, FaArrowRight, FaCheck, FaRedo } from 'react-icons/fa'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { useRecommendations } from '@/hooks/useApi'
import { ProgressIndicator } from '@/components/questionnaire/ProgressIndicator'
import { Step1Budget } from '@/components/questionnaire/Step1Budget'
import { Step2Usage } from '@/components/questionnaire/Step2Usage'
import { Step3Priorities } from '@/components/questionnaire/Step3Priorities'
import { Step4Preferences } from '@/components/questionnaire/Step4Preferences'
import type { ApiError } from '@/types'

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

  // Error state for API failures
  const [apiError, setApiError] = useState<ApiError | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const MAX_RETRIES = 3

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
    // Scroll to top when page loads
    window.scrollTo({ top: 0, behavior: 'smooth' })

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
    window.scrollTo({ top: 0, behavior: 'smooth' })
    navigate('/') // Volta para a home
  }

  const handleSubmit = (isRetry = false) => {
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

    // Clear previous error when retrying
    if (isRetry) {
      setApiError(null)
    }

    const userProfile = toUserProfile()

    getRecommendations(userProfile, {
      onSuccess: (data) => {
        // Reset error state and retry count on success
        setApiError(null)
        setRetryCount(0)

        // Validar se recebemos dados válidos
        if (!data || !data.profile_summary) {
          const validationError: ApiError = {
            message: 'Erro ao processar recomendações',
            detail: 'Não foi possível processar sua busca. Tente novamente.',
            status: 500,
            code: 'INVALID_RESPONSE',
          }
          setApiError(validationError)
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
      onError: (error: ApiError) => {
        console.error('Erro na API:', error)

        // Store error for display
        setApiError(error)

        // Implement exponential backoff retry logic for network errors
        const isNetworkError = error.code && (
          error.code === 'NETWORK_ERROR' ||
          error.code === 'ECONNABORTED' ||
          error.code === 'ETIMEDOUT'
        )

        if (isNetworkError && retryCount < MAX_RETRIES) {
          const nextRetryCount = retryCount + 1
          const backoffDelay = Math.pow(2, nextRetryCount) * 1000 // 2s, 4s, 8s

          setRetryCount(nextRetryCount)

          toast({
            title: 'Tentando reconectar...',
            description: `Tentativa ${nextRetryCount} de ${MAX_RETRIES}`,
            status: 'info',
            duration: 2000,
            isClosable: true,
          })

          // Retry with exponential backoff
          setTimeout(() => {
            handleSubmit(true)
          }, backoffDelay)
        } else {
          // Show error toast for non-retryable errors or max retries reached
          let errorTitle = 'Erro ao buscar recomendações'
          let errorDescription = error.message

          if (retryCount >= MAX_RETRIES) {
            errorTitle = 'Não foi possível conectar'
            errorDescription = 'Verifique sua conexão e tente novamente.'
          }

          toast({
            title: errorTitle,
            description: errorDescription,
            status: 'error',
            duration: 5000,
            isClosable: true,
          })
        }
      },
    })
  }

  const handleRetry = () => {
    setRetryCount(0) // Reset retry count for manual retry
    handleSubmit(true)
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

          {/* Error Alert */}
          {apiError && (
            <Alert
              status="error"
              variant="subtle"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              textAlign="center"
              borderRadius="xl"
              p={6}
            >
              <AlertIcon boxSize="40px" mr={0} />
              <AlertTitle mt={4} mb={1} fontSize="lg">
                {apiError.message}
              </AlertTitle>
              <AlertDescription maxWidth="sm" mb={4}>
                {apiError.detail || 'Ocorreu um erro ao processar sua solicitação.'}
              </AlertDescription>
              <HStack spacing={4}>
                <Button
                  colorScheme="red"
                  leftIcon={<FaRedo />}
                  onClick={handleRetry}
                  isLoading={isPending}
                  loadingText="Tentando..."
                >
                  Tentar Novamente
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setApiError(null)}
                >
                  Fechar
                </Button>
              </HStack>
              {retryCount > 0 && (
                <Text fontSize="sm" color="gray.600" mt={3}>
                  Tentativa {retryCount} de {MAX_RETRIES}
                </Text>
              )}
            </Alert>
          )}

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
              colorScheme="secondary"
              rightIcon={currentStep === 3 ? <FaCheck /> : <FaArrowRight />}
              onClick={handleNext}
              isDisabled={!canGoNext()}
              isLoading={isPending}
              loadingText="Buscando..."
              px={8}
              borderRadius="xl"
              boxShadow="md"
              _hover={{
                transform: 'translateY(-2px)',
                boxShadow: 'lg',
              }}
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
