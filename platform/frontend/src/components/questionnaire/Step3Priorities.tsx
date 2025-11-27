// 🎨 UX + ✍️ Content Creator: Step 3 - Prioridades (Seleção Múltipla)
import { VStack, Heading, Text, Box, SimpleGrid, useToast } from '@chakra-ui/react'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { useState, useEffect } from 'react'

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

type PriorityKey = 'economia' | 'espaco' | 'performance' | 'conforto' | 'seguranca'

export const Step3Priorities = () => {
  const { formData, updateFormData } = useQuestionnaireStore()
  const toast = useToast()

  // Initialize from formData if exists (only if user has actually selected priorities)
  const initialPriorities = (() => {
    if (formData.prioridades) {
      // Only initialize if there are priorities with value 5 (user selected)
      const selected = Object.entries(formData.prioridades)
        .filter(([, value]) => value === 5)
        .map(([key]) => key as PriorityKey)

      return selected.length > 0 ? selected : []
    }
    return []
  })()

  const [selectedPriorities, setSelectedPriorities] = useState<PriorityKey[]>(initialPriorities)

  const handlePriorityToggle = (key: PriorityKey) => {
    setSelectedPriorities((prev) => {
      const isSelected = prev.includes(key)

      if (isSelected) {
        // Remove priority
        const newSelected = prev.filter((p) => p !== key)
        updatePriorities(newSelected)
        return newSelected
      } else {
        // Add priority (max 3)
        if (prev.length >= 3) {
          toast({
            title: 'Máximo de 3 prioridades',
            description: 'Você pode selecionar até 3 prioridades. Desmarque uma para adicionar outra.',
            status: 'warning',
            duration: 3000,
            isClosable: true,
            position: 'top',
          })
          return prev
        }
        const newSelected = [...prev, key]
        updatePriorities(newSelected)
        return newSelected
      }
    })
  }

  const updatePriorities = (selected: PriorityKey[]) => {
    // Convert selected priorities to the format expected by backend
    // Selected priorities get value 5, others get value 3
    const priorities = {
      economia: selected.includes('economia') ? 5 : 3,
      espaco: selected.includes('espaco') ? 5 : 3,
      performance: selected.includes('performance') ? 5 : 3,
      conforto: selected.includes('conforto') ? 5 : 3,
      seguranca: selected.includes('seguranca') ? 5 : 3,
    }

    updateFormData({ prioridades: priorities })
  }

  const getSelectionOrder = (key: PriorityKey): number | null => {
    const index = selectedPriorities.indexOf(key)
    return index >= 0 ? index + 1 : null
  }

  return (
    <VStack spacing={8} align="stretch" maxW="900px" mx="auto">
      {/* Header */}
      <VStack spacing={3} textAlign="center">
        <Heading size="lg" color="gray.800">
          O que é mais importante para você? 🎯
        </Heading>
        <Text color="gray.600" fontSize="md" maxW="600px">
          Escolha até 3 prioridades que mais importam na hora de escolher seu carro.
        </Text>
        <Text color="brand.600" fontSize="sm" fontWeight="medium">
          {selectedPriorities.length}/3 selecionadas
        </Text>
      </VStack>

      {/* Priority Cards Grid */}
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
        {PRIORITIES.map((priority) => {
          const isSelected = selectedPriorities.includes(priority.key as PriorityKey)
          const order = getSelectionOrder(priority.key as PriorityKey)

          return (
            <Box
              key={priority.key}
              data-testid={`priority-card-${priority.key}`}
              p={5}
              borderRadius="xl"
              borderWidth="3px"
              borderColor={isSelected ? 'brand.500' : 'gray.200'}
              bg={isSelected ? 'brand.50' : 'white'}
              cursor="pointer"
              onClick={() => handlePriorityToggle(priority.key as PriorityKey)}
              transition="all 0.2s"
              position="relative"
              _hover={{
                borderColor: isSelected ? 'brand.600' : 'gray.300',
                transform: 'translateY(-2px)',
                shadow: 'md',
              }}
              _active={{
                transform: 'translateY(0)',
              }}
            >
              {/* Selection Badge */}
              {isSelected && (
                <Box
                  position="absolute"
                  top={3}
                  right={3}
                  bg="brand.500"
                  color="white"
                  borderRadius="full"
                  w={8}
                  h={8}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  fontWeight="bold"
                  fontSize="sm"
                >
                  {order}º
                </Box>
              )}

              <VStack align="flex-start" spacing={3}>
                {/* Icon and Label */}
                <Box>
                  <Text fontSize="3xl" mb={2}>
                    {priority.icon}
                  </Text>
                  <Text fontSize="xl" fontWeight="bold" color="gray.800">
                    {priority.label}
                  </Text>
                </Box>

                {/* Description */}
                <Text fontSize="sm" color="gray.600" lineHeight="tall">
                  {priority.description}
                </Text>
              </VStack>
            </Box>
          )
        })}
      </SimpleGrid>

      {/* Help Text */}
      {selectedPriorities.length === 0 && (
        <Box
          bg="gray.50"
          p={4}
          borderRadius="lg"
          textAlign="center"
        >
          <Text fontSize="sm" color="gray.600">
            👆 Clique nos cards acima para selecionar suas prioridades
          </Text>
        </Box>
      )}

      {/* Summary Box */}
      {selectedPriorities.length > 0 && (
        <Box
          bg="brand.50"
          p={5}
          borderRadius="xl"
          borderWidth="2px"
          borderColor="brand.300"
        >
          <VStack spacing={3} align="stretch">
            <Text fontSize="md" fontWeight="bold" color="gray.800">
              ✅ Suas prioridades selecionadas:
            </Text>
            <VStack align="flex-start" spacing={2}>
              {selectedPriorities.map((key, index) => {
                const priority = PRIORITIES.find((p) => p.key === key)
                return (
                  <Text key={key} fontSize="md" color="gray.700">
                    {index + 1}º {priority?.icon} <strong>{priority?.label}</strong> - {priority?.description}
                  </Text>
                )
              })}
            </VStack>
            <Text fontSize="sm" color="gray.700" pt={2}>
              Vamos usar essas prioridades para encontrar os carros perfeitos para você!
            </Text>
          </VStack>
        </Box>
      )}
    </VStack>
  )
}


