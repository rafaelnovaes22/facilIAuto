// 🎨 UX + ✍️ Content Creator: Step 2 - Uso e Família
import {
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  RadioGroup,
  Radio,
  Stack,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Switch,
  HStack,
  Box,
} from '@chakra-ui/react'
import { useQuestionnaireStore } from '@/store/questionnaireStore'

export const Step2Usage = () => {
  const { formData, updateFormData } = useQuestionnaireStore()

  return (
    <VStack spacing={8} align="stretch" maxW="600px" mx="auto">
      {/* Header */}
      <VStack spacing={3} textAlign="center">
        <Heading size="lg" color="gray.800">
          🚗 Como você vai usar o carro?
        </Heading>
        <Text color="gray.600" fontSize="md">
          Isso nos ajuda a encontrar o veículo perfeito para suas necessidades
        </Text>
      </VStack>

      {/* Uso Principal */}
      <FormControl isRequired>
        <FormLabel fontSize="md" fontWeight="semibold" mb={4}>
          Uso Principal
        </FormLabel>
        <RadioGroup
          value={formData.uso_principal || 'familia'}
          onChange={(value) =>
            updateFormData({
              uso_principal: value as any,
            })
          }
        >
          <Stack spacing={3}>
            <Radio value="familia" size="lg" colorScheme="brand">
              <Box>
                <Text fontWeight="semibold">👨‍👩‍👧‍👦 Família</Text>
                <Text fontSize="sm" color="gray.600">
                  Transporte da família, passeios e atividades
                </Text>
              </Box>
            </Radio>

            <Radio value="trabalho" size="lg" colorScheme="brand">
              <Box>
                <Text fontWeight="semibold">💼 Trabalho</Text>
                <Text fontSize="sm" color="gray.600">
                  Deslocamento diário, reuniões e compromissos
                </Text>
              </Box>
            </Radio>

            <Radio value="lazer" size="lg" colorScheme="brand">
              <Box>
                <Text fontWeight="semibold">🏖️ Lazer</Text>
                <Text fontSize="sm" color="gray.600">
                  Viagens, aventuras e momentos de diversão
                </Text>
              </Box>
            </Radio>

            <Radio value="comercial" size="lg" colorScheme="brand">
              <Box>
                <Text fontWeight="semibold">🚚 Comercial</Text>
                <Text fontSize="sm" color="gray.600">
                  Transporte de produtos, entregas e serviços
                </Text>
              </Box>
            </Radio>

            <Radio value="transporte_passageiros" size="lg" colorScheme="brand">
              <Box>
                <Text fontWeight="semibold">🚖 Transporte de Passageiros</Text>
                <Text fontSize="sm" color="gray.600">
                  Uber, 99, táxi, van escolar ou executivo
                </Text>
              </Box>
            </Radio>

            <Radio value="primeiro_carro" size="lg" colorScheme="brand">
              <Box>
                <Text fontWeight="semibold">🎓 Primeiro Carro</Text>
                <Text fontSize="sm" color="gray.600">
                  Meu primeiro veículo, aprendendo a dirigir
                </Text>
              </Box>
            </Radio>
          </Stack>
        </RadioGroup>
      </FormControl>

      {/* Composição Familiar */}
      <VStack spacing={6} pt={4}>
        <Heading size="md" color="gray.800" alignSelf="flex-start">
          👥 Composição Familiar
        </Heading>

        {/* Tamanho da Família */}
        <FormControl isRequired>
          <FormLabel fontSize="sm">
            Quantas pessoas usarão o carro regularmente?
          </FormLabel>
          <NumberInput
            value={formData.tamanho_familia || 1}
            onChange={(_, valueNumber) =>
              updateFormData({ tamanho_familia: valueNumber })
            }
            min={1}
            max={10}
            size="lg"
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        </FormControl>

        {/* Crianças */}
        <FormControl>
          <HStack justify="space-between">
            <Box>
              <FormLabel fontSize="sm" mb={0}>
                Tem crianças?
              </FormLabel>
              <Text fontSize="xs" color="gray.600">
                Prioriza segurança e espaço para cadeirinhas
              </Text>
            </Box>
            <Switch
              size="lg"
              colorScheme="brand"
              isChecked={formData.tem_criancas || false}
              onChange={(e) =>
                updateFormData({ tem_criancas: e.target.checked })
              }
            />
          </HStack>
        </FormControl>

        {/* Idosos */}
        <FormControl>
          <HStack justify="space-between">
            <Box>
              <FormLabel fontSize="sm" mb={0}>
                Tem idosos?
              </FormLabel>
              <Text fontSize="xs" color="gray.600">
                Prioriza conforto e facilidade de acesso
              </Text>
            </Box>
            <Switch
              size="lg"
              colorScheme="brand"
              isChecked={formData.tem_idosos || false}
              onChange={(e) =>
                updateFormData({ tem_idosos: e.target.checked })
              }
            />
          </HStack>
        </FormControl>
      </VStack>

      {/* Summary */}
      <Box
        bg="secondary.50"
        p={4}
        borderRadius="lg"
        borderWidth="2px"
        borderColor="secondary.200"
      >
        <Text fontSize="sm" color="gray.700">
          <strong>Resumo:</strong> Carro para{' '}
          <strong>{formData.uso_principal || 'família'}</strong>, usado por{' '}
          <strong>{formData.tamanho_familia || 1} pessoa(s)</strong>
          {formData.tem_criancas && ', com crianças'}
          {formData.tem_idosos && ', com idosos'}
        </Text>
      </Box>
    </VStack>
  )
}

