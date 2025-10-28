// 🎨 UX + ✍️ Content Creator: Step 3 - Prioridades
import { VStack, Heading, Text, Box, HStack, Badge } from '@chakra-ui/react'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { PrioritySlider } from './PrioritySlider'
import { useMemo } from 'react'

// Simplified priority definitions following "grandmother test"
const PRIORITIES = [
  {
    key: 'economia',
    label: 'Economia',
    icon: '💰',
    description: 'Gasta pouco combustível e é barato de manter',
    tooltip: 'Carros econômicos gastam menos gasolina no dia a dia e têm manutenção mais em conta',
  },
  {
    key: 'espaco',
    label: 'Espaço',
    icon: '📦',
    description: 'Cabe muita coisa no porta-malas e é espaçoso por dentro',
    tooltip: 'Perfeito para levar compras, malas de viagem ou transportar a família com conforto',
  },
  {
    key: 'performance',
    label: 'Potência',
    icon: '🚀',
    description: 'Tem força para subir ladeiras e ultrapassar com facilidade',
    tooltip: 'Carros potentes aceleram rápido e têm mais facilidade em ultrapassagens',
  },
  {
    key: 'conforto',
    label: 'Conforto',
    icon: '✨',
    description: 'Direção macia, ar-condicionado bom e bancos confortáveis',
    tooltip: 'Ideal para viagens longas e para quem passa muito tempo no carro',
  },
  {
    key: 'seguranca',
    label: 'Segurança',
    icon: '🛡️',
    description: 'Protege bem você e sua família em caso de acidente',
    tooltip: 'Inclui airbags, freios que não travam as rodas e sistemas que ajudam a evitar acidentes',
  },
]

export const Step3Priorities = () => {
  const { formData, updateFormData } = useQuestionnaireStore()

  const handlePriorityChange = (key: keyof typeof priorities) => (value: number) => {
    updateFormData({
      prioridades: {
        ...priorities,
        [key]: value,
      },
    })
  }

  const priorities = formData.prioridades || {
    economia: 3,
    espaco: 3,
    performance: 3,
    conforto: 3,
    seguranca: 3,
  }

  // Calculate top 3 priorities for highlighting
  const topPriorities = useMemo(() => {
    return Object.entries(priorities)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([key]) => key)
  }, [priorities])

  return (
    <VStack spacing={8} align="stretch" maxW="800px" mx="auto">
      {/* Header */}
      <VStack spacing={3} textAlign="center">
        <Heading size="lg" color="gray.800">
          O que é mais importante para você? 🎯
        </Heading>
        <Text color="gray.600" fontSize="md" maxW="600px">
          Ajuste os controles para mostrar o que você mais valoriza. Vamos destacar suas 3
          prioridades principais.
        </Text>
      </VStack>

      {/* Priority Sliders */}
      <VStack spacing={4} align="stretch">
        {PRIORITIES.map((priority) => (
          <PrioritySlider
            key={priority.key}
            label={priority.label}
            icon={priority.icon}
            description={priority.description}
            tooltip={priority.tooltip}
            value={priorities[priority.key as keyof typeof priorities]}
            onChange={handlePriorityChange(priority.key as keyof typeof priorities)}
            isTopPriority={topPriorities.includes(priority.key)}
          />
        ))}
      </VStack>

      {/* Summary Box */}
      <Box
        bg="brand.50"
        p={5}
        borderRadius="xl"
        borderWidth="2px"
        borderColor="brand.300"
      >
        <VStack spacing={3} align="stretch">
          <HStack spacing={2}>
            <Text fontSize="md" fontWeight="bold" color="gray.800">
              🎯 Suas 3 prioridades principais:
            </Text>
          </HStack>
          <HStack spacing={3} flexWrap="wrap">
            {topPriorities.map((key, index) => {
              const priority = PRIORITIES.find((p) => p.key === key)
              return (
                <Badge
                  key={key}
                  colorScheme="brand"
                  fontSize="md"
                  px={4}
                  py={2}
                  borderRadius="full"
                  display="flex"
                  alignItems="center"
                  gap={2}
                >
                  <Text as="span">{index + 1}º</Text>
                  <Text as="span">{priority?.icon}</Text>
                  <Text as="span">{priority?.label}</Text>
                </Badge>
              )
            })}
          </HStack>
          <Text fontSize="sm" color="gray.700" pt={2}>
            Vamos usar essas prioridades para encontrar os carros perfeitos para você!
          </Text>
        </VStack>
      </Box>
    </VStack>
  )
}


