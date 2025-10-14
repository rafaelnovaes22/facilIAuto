// 🎨 UX + ✍️ Content Creator: Step 3 - Prioridades
import {
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  HStack,
  Box,
  Badge,
} from '@chakra-ui/react'
import { useQuestionnaireStore } from '@/store/questionnaireStore'

const priorityLabels = {
  1: 'Baixa',
  2: 'Média-Baixa',
  3: 'Média',
  4: 'Alta',
  5: 'Muito Alta',
}

const priorityColors = {
  1: 'gray',
  2: 'blue',
  3: 'cyan',
  4: 'green',
  5: 'brand',
}

export const Step3Priorities = () => {
  const { formData, updateFormData } = useQuestionnaireStore()

  const handlePriorityChange = (key: string) => (value: number) => {
    updateFormData({
      prioridades: {
        ...formData.prioridades,
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

  return (
    <VStack spacing={8} align="stretch" maxW="700px" mx="auto">
      {/* Header */}
      <VStack spacing={3} textAlign="center">
        <Heading size="lg" color="gray.800">
          🎯 Quais são suas prioridades?
        </Heading>
        <Text color="gray.600" fontSize="md">
          Ajuste os sliders para indicar o que é mais importante para você
        </Text>
      </VStack>

      {/* Prioridade: Economia */}
      <FormControl>
        <HStack justify="space-between" mb={2}>
          <FormLabel mb={0} fontSize="md" fontWeight="semibold">
            💰 Economia
          </FormLabel>
          <Badge
            colorScheme={priorityColors[priorities.economia as keyof typeof priorityColors]}
            fontSize="sm"
            px={3}
            py={1}
            borderRadius="full"
          >
            {priorityLabels[priorities.economia as keyof typeof priorityLabels]}
          </Badge>
        </HStack>
        <Text fontSize="sm" color="gray.600" mb={3}>
          Baixo consumo de combustível e manutenção econômica
        </Text>
        <Slider
          value={priorities.economia}
          onChange={handlePriorityChange('economia')}
          min={1}
          max={5}
          step={1}
          colorScheme="brand"
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb boxSize={6} />
        </Slider>
      </FormControl>

      {/* Prioridade: Espaço */}
      <FormControl>
        <HStack justify="space-between" mb={2}>
          <FormLabel mb={0} fontSize="md" fontWeight="semibold">
            📦 Espaço
          </FormLabel>
          <Badge
            colorScheme={priorityColors[priorities.espaco as keyof typeof priorityColors]}
            fontSize="sm"
            px={3}
            py={1}
            borderRadius="full"
          >
            {priorityLabels[priorities.espaco as keyof typeof priorityLabels]}
          </Badge>
        </HStack>
        <Text fontSize="sm" color="gray.600" mb={3}>
          Porta-malas amplo e espaço interno confortável
        </Text>
        <Slider
          value={priorities.espaco}
          onChange={handlePriorityChange('espaco')}
          min={1}
          max={5}
          step={1}
          colorScheme="brand"
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb boxSize={6} />
        </Slider>
      </FormControl>

      {/* Prioridade: Performance */}
      <FormControl>
        <HStack justify="space-between" mb={2}>
          <FormLabel mb={0} fontSize="md" fontWeight="semibold">
            🚀 Performance
          </FormLabel>
          <Badge
            colorScheme={priorityColors[priorities.performance as keyof typeof priorityColors]}
            fontSize="sm"
            px={3}
            py={1}
            borderRadius="full"
          >
            {priorityLabels[priorities.performance as keyof typeof priorityLabels]}
          </Badge>
        </HStack>
        <Text fontSize="sm" color="gray.600" mb={3}>
          Potência do motor e aceleração
        </Text>
        <Slider
          value={priorities.performance}
          onChange={handlePriorityChange('performance')}
          min={1}
          max={5}
          step={1}
          colorScheme="brand"
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb boxSize={6} />
        </Slider>
      </FormControl>

      {/* Prioridade: Conforto */}
      <FormControl>
        <HStack justify="space-between" mb={2}>
          <FormLabel mb={0} fontSize="md" fontWeight="semibold">
            ✨ Conforto
          </FormLabel>
          <Badge
            colorScheme={priorityColors[priorities.conforto as keyof typeof priorityColors]}
            fontSize="sm"
            px={3}
            py={1}
            borderRadius="full"
          >
            {priorityLabels[priorities.conforto as keyof typeof priorityLabels]}
          </Badge>
        </HStack>
        <Text fontSize="sm" color="gray.600" mb={3}>
          Direção suave, ar-condicionado e acabamento interno
        </Text>
        <Slider
          value={priorities.conforto}
          onChange={handlePriorityChange('conforto')}
          min={1}
          max={5}
          step={1}
          colorScheme="brand"
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb boxSize={6} />
        </Slider>
      </FormControl>

      {/* Prioridade: Segurança */}
      <FormControl>
        <HStack justify="space-between" mb={2}>
          <FormLabel mb={0} fontSize="md" fontWeight="semibold">
            🛡️ Segurança
          </FormLabel>
          <Badge
            colorScheme={priorityColors[priorities.seguranca as keyof typeof priorityColors]}
            fontSize="sm"
            px={3}
            py={1}
            borderRadius="full"
          >
            {priorityLabels[priorities.seguranca as keyof typeof priorityLabels]}
          </Badge>
        </HStack>
        <Text fontSize="sm" color="gray.600" mb={3}>
          Airbags, freios ABS e sistemas de assistência
        </Text>
        <Slider
          value={priorities.seguranca}
          onChange={handlePriorityChange('seguranca')}
          min={1}
          max={5}
          step={1}
          colorScheme="brand"
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb boxSize={6} />
        </Slider>
      </FormControl>

      {/* Summary */}
      <Box
        bg="brand.50"
        p={4}
        borderRadius="lg"
        borderWidth="2px"
        borderColor="brand.200"
      >
        <Text fontSize="sm" color="gray.700" mb={2}>
          <strong>Suas prioridades principais:</strong>
        </Text>
        <HStack spacing={2} flexWrap="wrap">
          {Object.entries(priorities)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 3)
            .map(([key, value]) => (
              <Badge
                key={key}
                colorScheme={priorityColors[value as keyof typeof priorityColors]}
                fontSize="sm"
                px={3}
                py={1}
              >
                {key === 'economia' && '💰 Economia'}
                {key === 'espaco' && '📦 Espaço'}
                {key === 'performance' && '🚀 Performance'}
                {key === 'conforto' && '✨ Conforto'}
                {key === 'seguranca' && '🛡️ Segurança'}
              </Badge>
            ))}
        </HStack>
      </Box>
    </VStack>
  )
}

