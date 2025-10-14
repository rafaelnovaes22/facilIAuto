// 🎨 UX + ✍️ Content Creator: Step 1 - Orçamento e Localização
import {
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Select,
  Input,
  HStack,
  Box,
  FormHelperText,
} from '@chakra-ui/react'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { ESTADOS_BR } from '@/types'
import { formatCurrency } from '@/services/api'

export const Step1Budget = () => {
  const { formData, updateFormData } = useQuestionnaireStore()

  const handleBudgetChange = (field: 'orcamento_min' | 'orcamento_max') => (
    valueString: string
  ) => {
    const value = parseFloat(valueString) || 0
    updateFormData({ [field]: value })
  }

  return (
    <VStack spacing={8} align="stretch" maxW="600px" mx="auto">
      {/* Header */}
      <VStack spacing={3} textAlign="center">
        <Heading size="lg" color="gray.800">
          💰 Qual é o seu orçamento?
        </Heading>
        <Text color="gray.600" fontSize="md">
          Defina a faixa de preço que você está disposto a investir
        </Text>
      </VStack>

      {/* Orçamento Mínimo */}
      <FormControl isRequired>
        <FormLabel fontSize="md" fontWeight="semibold">
          Orçamento Mínimo
        </FormLabel>
        <NumberInput
          value={formData.orcamento_min || 50000}
          onChange={handleBudgetChange('orcamento_min')}
          min={10000}
          max={500000}
          step={5000}
          size="lg"
        >
          <NumberInputField />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
        <FormHelperText>
          Valor atual: {formatCurrency(formData.orcamento_min || 50000)}
        </FormHelperText>
      </FormControl>

      {/* Orçamento Máximo */}
      <FormControl isRequired>
        <FormLabel fontSize="md" fontWeight="semibold">
          Orçamento Máximo
        </FormLabel>
        <NumberInput
          value={formData.orcamento_max || 100000}
          onChange={handleBudgetChange('orcamento_max')}
          min={10000}
          max={500000}
          step={5000}
          size="lg"
        >
          <NumberInputField />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
        <FormHelperText>
          Valor atual: {formatCurrency(formData.orcamento_max || 100000)}
        </FormHelperText>
      </FormControl>

      {/* Faixa de Orçamento Visual */}
      <Box
        bg="brand.50"
        p={4}
        borderRadius="lg"
        borderWidth="2px"
        borderColor="brand.200"
      >
        <Text fontSize="sm" color="gray.600" mb={2}>
          Faixa de orçamento selecionada:
        </Text>
        <Text fontSize="xl" fontWeight="bold" color="brand.600">
          {formatCurrency(formData.orcamento_min || 50000)} -{' '}
          {formatCurrency(formData.orcamento_max || 100000)}
        </Text>
      </Box>

      {/* Localização */}
      <VStack spacing={4} pt={4}>
        <Heading size="md" color="gray.800" alignSelf="flex-start">
          📍 Onde você está localizado?
        </Heading>
        <Text color="gray.600" fontSize="sm" alignSelf="flex-start">
          Isso nos ajuda a priorizar concessionárias próximas a você (opcional)
        </Text>

        <HStack spacing={4} w="full">
          {/* Estado */}
          <FormControl flex={1}>
            <FormLabel fontSize="sm">Estado</FormLabel>
            <Select
              placeholder="Selecione o estado"
              value={formData.state || ''}
              onChange={(e) => updateFormData({ state: e.target.value || undefined })}
              size="lg"
            >
              {ESTADOS_BR.map((estado) => (
                <option key={estado} value={estado}>
                  {estado}
                </option>
              ))}
            </Select>
          </FormControl>

          {/* Cidade */}
          <FormControl flex={2}>
            <FormLabel fontSize="sm">Cidade</FormLabel>
            <Input
              placeholder="Ex: São Paulo"
              value={formData.city || ''}
              onChange={(e) =>
                updateFormData({ city: e.target.value || undefined })
              }
              size="lg"
            />
          </FormControl>
        </HStack>
      </VStack>
    </VStack>
  )
}

