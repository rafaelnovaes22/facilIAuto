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
  } = useQuestionnaireStore()

  const { mutate: getRecommendations, isPending } = useRecommendations()

  const handleNext = () => {
    if (currentStep === 3) {
      // Última etapa - buscar recomendações
      handleSubmit()
    } else {
      nextStep()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
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
        toast({
          title: 'Recomendações encontradas!',
          description: `${data.total_recommendations} carros perfeitos para você`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })

        // Navegar para resultados com dados
        navigate('/resultados', { state: { recommendations: data } })
      },
      onError: (error) => {
        toast({
          title: 'Erro ao buscar recomendações',
          description: error.message || 'Tente novamente',
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
            onClick={() => navigate('/')}
            color="gray.600"
          >
            ← Voltar para o início
          </Button>
        </VStack>
      </Container>
    </Box>
  )
}
