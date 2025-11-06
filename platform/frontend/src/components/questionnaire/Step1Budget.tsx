// 🎨 UX + ✍️ Content Creator: Step 1 - Orçamento e Localização
import {
  VStack,
  Heading,
  Text,
  Divider,
} from '@chakra-ui/react'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { BudgetSlider } from './BudgetSlider'
import { LocationSelector } from './LocationSelector'
import { YearSelector } from './YearSelector'
import { SalaryRangeSelector } from './SalaryRangeSelector'

export const Step1Budget = () => {
  const { formData, updateFormData } = useQuestionnaireStore()

  const handleBudgetChange = (min: number, max: number) => {
    updateFormData({
      orcamento_min: min,
      orcamento_max: max,
    })
  }

  const handleLocationChange = (location: { city?: string; state?: string }) => {
    updateFormData(location)
  }

  const handleYearChange = (min?: number, max?: number) => {
    updateFormData({ ano_minimo: min, ano_maximo: max })
  }

  const handleSalaryChange = (range: string | null) => {
    updateFormData({ faixa_salarial: range })
  }

  return (
    <VStack spacing={8} align="stretch" maxW="700px" mx="auto">
      {/* Header */}
      <VStack spacing={3} textAlign="center">
        <Heading size="lg" color="gray.800">
          Vamos começar! 🚗
        </Heading>
        <Text color="gray.600" fontSize="md" maxW="500px">
          Primeiro, precisamos saber quanto você quer investir e onde você está
        </Text>
      </VStack>

      {/* Budget Slider */}
      <BudgetSlider
        minValue={formData.orcamento_min || 50000}
        maxValue={formData.orcamento_max || 100000}
        onChange={handleBudgetChange}
        minLimit={10000}
        maxLimit={500000}
        step={5000}
      />

      {/* Divider */}
      <Divider />

      {/* Year Selector */}
      <YearSelector
        minValue={formData.ano_minimo}
        maxValue={formData.ano_maximo}
        onChange={handleYearChange}
      />

      {/* Divider */}
      <Divider />

      {/* Salary Range Selector */}
      <SalaryRangeSelector
        value={formData.faixa_salarial || null}
        onChange={handleSalaryChange}
      />

      {/* Divider */}
      <Divider />

      {/* Location Selector */}
      <LocationSelector
        city={formData.city}
        state={formData.state}
        onChange={handleLocationChange}
      />
    </VStack>
  )
}

