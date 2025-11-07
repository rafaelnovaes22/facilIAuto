// 🎨 UX + ✍️ Content Creator: Step 4 - Confirmação e Preferências
import {
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  CheckboxGroup,
  Checkbox,
  Stack,
  SimpleGrid,
  RadioGroup,
  Radio,
  Box,
  HStack,
  Button,
  Icon,
  Divider,
  Badge,
  Spinner,
  Center,
} from '@chakra-ui/react'
import { useQuery } from '@tanstack/react-query'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { CATEGORIAS } from '@/types'
import { getBrandsWithModels, queryKeys } from '@/services/api'

export const Step4Preferences = () => {
  const { formData, updateFormData } = useQuestionnaireStore()

  // Buscar marcas e modelos disponíveis da API
  const { data: brandsModels, isLoading: isLoadingBrands } = useQuery({
    queryKey: queryKeys.brandsModels,
    queryFn: getBrandsWithModels,
    staleTime: 1000 * 60 * 60, // 1 hora (dados raramente mudam)
  })

  // Extrair lista de marcas ordenadas
  const availableBrands = brandsModels ? Object.keys(brandsModels).sort() : []

  return (
    <VStack spacing={8} align="stretch" maxW="700px" mx="auto">
      {/* Header */}
      <VStack spacing={3} textAlign="center">
        <Heading size="lg" color="gray.800">
          Quase lá! 🎉
        </Heading>
        <Text color="gray.600" fontSize="md">
          Confirme sua localização e adicione preferências se quiser
        </Text>
      </VStack>



      {/* Tipos de Veículo */}
      <FormControl>
        <FormLabel fontSize="md" fontWeight="semibold" mb={4}>
          🚗 Tipos de Veículo Preferidos
        </FormLabel>
        <Text fontSize="sm" color="gray.600" mb={3}>
          Selecione os tipos de carro que você prefere (opcional)
        </Text>
        <CheckboxGroup
          value={formData.tipos_preferidos || []}
          onChange={(values) =>
            updateFormData({ tipos_preferidos: values as string[] })
          }
        >
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
            {CATEGORIAS.map((categoria) => (
              <Checkbox
                key={categoria}
                value={categoria}
                size="lg"
                colorScheme="brand"
              >
                {categoria}
              </Checkbox>
            ))}
          </SimpleGrid>
        </CheckboxGroup>
      </FormControl>

      {/* Marcas */}
      <FormControl>
        <FormLabel fontSize="md" fontWeight="semibold" mb={4}>
          🏷️ Marcas Preferidas
        </FormLabel>
        <Text fontSize="sm" color="gray.600" mb={3}>
          Tem alguma marca de preferência? (opcional)
        </Text>

        {isLoadingBrands ? (
          <Center py={8}>
            <Spinner size="md" color="brand.500" />
          </Center>
        ) : (
          <CheckboxGroup
            value={formData.marcas_preferidas || []}
            onChange={(values) =>
              updateFormData({ marcas_preferidas: values as string[] })
            }
          >
            <SimpleGrid columns={{ base: 2, md: 3 }} spacing={3}>
              {availableBrands.map((marca) => {
                const modelCount = brandsModels?.[marca]?.length || 0
                return (
                  <Checkbox
                    key={marca}
                    value={marca}
                    size="lg"
                    colorScheme="brand"
                  >
                    <HStack spacing={2}>
                      <Text>{marca}</Text>
                      <Badge colorScheme="gray" fontSize="xs">
                        {modelCount}
                      </Badge>
                    </HStack>
                  </Checkbox>
                )
              })}
            </SimpleGrid>
          </CheckboxGroup>
        )}
      </FormControl>

      {/* Câmbio */}
      <FormControl>
        <FormLabel fontSize="md" fontWeight="semibold" mb={4}>
          ⚙️ Preferência de Câmbio
        </FormLabel>
        <Text fontSize="sm" color="gray.600" mb={3}>
          Qual tipo de câmbio você prefere? (opcional)
        </Text>
        <RadioGroup
          value={formData.cambio_preferido || ''}
          onChange={(value) =>
            updateFormData({ cambio_preferido: value || undefined })
          }
        >
          <Stack spacing={3}>
            <Radio value="" size="lg" colorScheme="gray">
              <Box>
                <Text fontWeight="semibold">Sem preferência</Text>
                <Text fontSize="sm" color="gray.600">
                  Considerar todas as opções
                </Text>
              </Box>
            </Radio>

            <Radio value="Manual" size="lg" colorScheme="brand">
              <Box>
                <Text fontWeight="semibold">Manual</Text>
                <Text fontSize="sm" color="gray.600">
                  Mais econômico e maior controle
                </Text>
              </Box>
            </Radio>

            <Radio value="Automático" size="lg" colorScheme="brand">
              <Box>
                <Text fontWeight="semibold">Automático</Text>
                <Text fontSize="sm" color="gray.600">
                  Mais conforto, especialmente no trânsito
                </Text>
              </Box>
            </Radio>

            <Radio value="CVT" size="lg" colorScheme="brand">
              <Box>
                <Text fontWeight="semibold">CVT (Automático Contínuo)</Text>
                <Text fontSize="sm" color="gray.600">
                  Suavidade e eficiência
                </Text>
              </Box>
            </Radio>
          </Stack>
        </RadioGroup>
      </FormControl>

      {/* Info Box */}
      <Box
        bg="secondary.50"
        p={4}
        borderRadius="lg"
        borderWidth="2px"
        borderColor="secondary.200"
      >
        <Text fontSize="sm" color="gray.700">
          💡 <strong>Dica:</strong> Essas preferências são opcionais. Se você
          não selecionar nada, nossa IA considerará todas as opções disponíveis
          para você.
        </Text>
      </Box>

      {/* Ready to see results */}
      <Box
        bg="green.50"
        p={5}
        borderRadius="xl"
        borderWidth="2px"
        borderColor="green.200"
        textAlign="center"
      >
        <Text fontSize="md" fontWeight="bold" color="green.800" mb={2}>
          ✨ Tudo pronto!
        </Text>
        <Text fontSize="sm" color="green.700">
          Clique em "Ver Recomendações" para descobrir os carros perfeitos para você
        </Text>
      </Box>
    </VStack>
  )
}

