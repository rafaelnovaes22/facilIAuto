import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Progress,
  Container,
  Heading,
  Icon,
  useToast,
  Flex,
  Badge,
} from '@chakra-ui/react';
import { FiArrowLeft, FiArrowRight, FiCheck } from 'react-icons/fi';
import { useAppStore } from '../../store/useAppStore';
import { QuestionnaireStep } from '../../types';

// Step Components
import BudgetLocationStep from './steps/BudgetLocationStep';
import UsageProfileStep from './steps/UsageProfileStep';
import FamilyNeedsStep from './steps/FamilyNeedsStep';
import PrioritiesStep from './steps/PrioritiesStep';
import PreferencesStep from './steps/PreferencesStep';

const QUESTIONNAIRE_STEPS: QuestionnaireStep[] = [
  {
    id: 'budget-location',
    title: 'Orçamento e Localização',
    subtitle: 'Vamos começar com o básico',
    component: BudgetLocationStep,
  },
  {
    id: 'usage-profile',
    title: 'Como você vai usar o carro?',
    subtitle: 'Entenda seu perfil de uso',
    component: UsageProfileStep,
  },
  {
    id: 'family-needs',
    title: 'Necessidades da família',
    subtitle: 'Espaço e conforto necessários',
    component: FamilyNeedsStep,
  },
  {
    id: 'priorities',
    title: 'Suas prioridades',
    subtitle: 'O que é mais importante para você?',
    component: PrioritiesStep,
  },
  {
    id: 'preferences',
    title: 'Preferências pessoais',
    subtitle: 'Marcas, tipos e características',
    component: PreferencesStep,
  },
];

const Questionnaire: React.FC = () => {
  const {
    criteria,
    updateCriteria,
    ui,
    nextStep,
    previousStep,
    submitQuestionnaire,
  } = useAppStore();

  const toast = useToast();
  const [isValid, setIsValid] = useState(false);
  const currentStepData = QUESTIONNAIRE_STEPS[ui.currentStep];
  const StepComponent = currentStepData.component;

  // Validate current step
  useEffect(() => {
    setIsValid(validateCurrentStep());
  }, [criteria, ui.currentStep]);

  const validateCurrentStep = (): boolean => {
    switch (ui.currentStep) {
      case 0: // Budget & Location
        return !!(
          criteria.budget?.min &&
          criteria.budget?.max &&
          criteria.location?.city
        );
      
      case 1: // Usage Profile
        return !!(
          criteria.usage?.mainPurpose &&
          criteria.usage?.frequency
        );
      
      case 2: // Family Needs
        return !!(
          typeof criteria.family?.size === 'number'
        );
      
      case 3: // Priorities
        return !!(
          criteria.priorities &&
          Object.keys(criteria.priorities).length >= 4
        );
      
      case 4: // Preferences
        return true; // Optional step
      
      default:
        return false;
    }
  };

  const handleNext = async () => {
    if (!isValid) {
      toast({
        title: 'Preencha todos os campos obrigatórios',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    if (ui.currentStep === QUESTIONNAIRE_STEPS.length - 1) {
      // Last step - submit questionnaire
      try {
        await submitQuestionnaire();
        toast({
          title: 'Analisando suas preferências...',
          description: 'Você será redirecionado para os resultados',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } catch (error) {
        toast({
          title: 'Erro ao processar',
          description: 'Tente novamente em alguns instantes',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    } else {
      nextStep();
    }
  };

  const handlePrevious = () => {
    if (ui.currentStep > 0) {
      previousStep();
    }
  };

  const progressPercentage = ((ui.currentStep + 1) / QUESTIONNAIRE_STEPS.length) * 100;

  return (
    <Container maxW="4xl" py={8}>
      {/* Header */}
      <VStack spacing={6} mb={8}>
        <Box w="full">
          <HStack justify="space-between" mb={2}>
            <Text fontSize="sm" color="gray.600">
              Passo {ui.currentStep + 1} de {QUESTIONNAIRE_STEPS.length}
            </Text>
            <Badge
              colorScheme={ui.currentStep === QUESTIONNAIRE_STEPS.length - 1 ? 'green' : 'blue'}
              variant="subtle"
            >
              {Math.round(progressPercentage)}% completo
            </Badge>
          </HStack>
          <Progress
            value={progressPercentage}
            colorScheme="blue"
            size="lg"
            borderRadius="full"
            bg="gray.100"
          />
        </Box>

        <VStack spacing={2} textAlign="center">
          <Heading as="h1" size="xl" color="gray.800">
            {currentStepData.title}
          </Heading>
          {currentStepData.subtitle && (
            <Text fontSize="lg" color="gray.600">
              {currentStepData.subtitle}
            </Text>
          )}
        </VStack>
      </VStack>

      {/* Step Content */}
      <Box
        bg="white"
        borderRadius="xl"
        boxShadow="lg"
        p={8}
        mb={8}
        border="1px"
        borderColor="gray.100"
      >
        <StepComponent
          criteria={criteria}
          updateCriteria={updateCriteria}
          onNext={handleNext}
          onPrevious={handlePrevious}
          isValid={isValid}
        />
      </Box>

      {/* Navigation */}
      <Flex justify="space-between" align="center">
        <Button
          leftIcon={<Icon as={FiArrowLeft} />}
          variant="ghost"
          onClick={handlePrevious}
          isDisabled={ui.currentStep === 0}
          size="lg"
        >
          Anterior
        </Button>

        <HStack spacing={2}>
          {QUESTIONNAIRE_STEPS.map((_, index) => (
            <Box
              key={index}
              w={3}
              h={3}
              borderRadius="full"
              bg={index <= ui.currentStep ? 'blue.500' : 'gray.300'}
              transition="all 0.2s"
            />
          ))}
        </HStack>

        <Button
          rightIcon={
            <Icon 
              as={ui.currentStep === QUESTIONNAIRE_STEPS.length - 1 ? FiCheck : FiArrowRight} 
            />
          }
          colorScheme="blue"
          onClick={handleNext}
          isLoading={ui.loading}
          loadingText={ui.currentStep === QUESTIONNAIRE_STEPS.length - 1 ? 'Analisando...' : 'Carregando...'}
          isDisabled={!isValid}
          size="lg"
        >
          {ui.currentStep === QUESTIONNAIRE_STEPS.length - 1 ? 'Ver Recomendações' : 'Próximo'}
        </Button>
      </Flex>

      {/* Progress Steps */}
      <Box mt={8} px={4}>
        <HStack justify="space-between" align="start">
          {QUESTIONNAIRE_STEPS.map((step, index) => (
            <VStack
              key={step.id}
              spacing={2}
              flex={1}
              opacity={index <= ui.currentStep ? 1 : 0.5}
              transition="all 0.3s"
            >
              <Box
                w={10}
                h={10}
                borderRadius="full"
                bg={index < ui.currentStep ? 'green.500' : index === ui.currentStep ? 'blue.500' : 'gray.300'}
                display="flex"
                alignItems="center"
                justifyContent="center"
                color="white"
                fontWeight="bold"
                transition="all 0.3s"
              >
                {index < ui.currentStep ? (
                  <Icon as={FiCheck} boxSize={5} />
                ) : (
                  index + 1
                )}
              </Box>
              <Text
                fontSize="xs"
                textAlign="center"
                fontWeight={index === ui.currentStep ? 'bold' : 'normal'}
                color={index <= ui.currentStep ? 'gray.700' : 'gray.400'}
              >
                {step.title}
              </Text>
            </VStack>
          ))}
        </HStack>
      </Box>

      {/* Help Text */}
      <Box mt={6} p={4} bg="blue.50" borderRadius="lg" border="1px" borderColor="blue.100">
        <Text fontSize="sm" color="blue.700" textAlign="center">
          💡 <strong>Dica:</strong> Seja específico nas suas respostas para recomendações mais precisas
        </Text>
      </Box>
    </Container>
  );
};

export default Questionnaire;
