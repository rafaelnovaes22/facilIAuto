// 🎨 UX + ✍️ Content Creator: Step 4 - Confirmação e Preferências
import {
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  CheckboxGroup,
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
  Card,
  CardBody,
  Checkbox,
  useCheckbox,
  chakra,
  useCheckboxGroup,
} from '@chakra-ui/react'
import { useQuery } from '@tanstack/react-query'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { CATEGORIAS } from '@/types'
import { getBrandsWithModels, queryKeys } from '@/services/api'
import { FaCheck, FaCarSide, FaTruckPickup, FaShuttleVan, FaBus, FaCar, FaCheckCircle, FaCircle } from 'react-icons/fa'

// Brand Card Component
interface BrandCardProps {
  marca: string
  modelCount: number
  isChecked: boolean
  onToggle: (checked: boolean) => void
}

const BrandCard = ({ marca, modelCount, isChecked, onToggle }: BrandCardProps) => {
  const { getInputProps, getCheckboxProps, htmlProps } = useCheckbox({
    isChecked,
    onChange: (e) => onToggle(e.target.checked),
  })

  const input = getInputProps()
  const checkbox = getCheckboxProps()

  return (
    <Card
      as="label"
      cursor="pointer"
      borderWidth="2px"
      borderColor={isChecked ? 'brand.500' : 'gray.200'}
      bg={isChecked ? 'brand.50' : 'white'}
      _hover={{
        borderColor: 'brand.300',
        boxShadow: 'md',
        transform: 'translateY(-2px)',
      }}
      transition="all 0.2s"
      borderRadius="xl"
      {...htmlProps}
    >
      <CardBody p={4}>
        <input {...input} />
        <HStack spacing={3} justify="space-between">
          <Text fontWeight="medium" color={isChecked ? 'brand.700' : 'gray.700'}>
            {marca}
          </Text>
          <HStack spacing={2}>
            <Badge colorScheme="gray" fontSize="xs">
              {modelCount}
            </Badge>
            <Box
              {...checkbox}
              w={5}
              h={5}
              borderRadius="full"
              borderWidth="2px"
              borderColor={isChecked ? 'brand.500' : 'gray.300'}
              bg={isChecked ? 'secondary.500' : 'transparent'}
              display="flex"
              alignItems="center"
              justifyContent="center"
              transition="all 0.2s"
            >
              {isChecked && <Box as={FaCheck} color="white" boxSize={3} />}
            </Box>
          </HStack>
        </HStack>
      </CardBody>
    </Card>
  )
}

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
            {CATEGORIAS.map((categoria) => {
              const categoryIcons: Record<string, any> = {
                'Hatchback': FaCar,
                'Sedan': FaCarSide,
                'SUV': FaShuttleVan,
                'Pickup': FaTruckPickup,
                'Minivan': FaBus,
                'Hatch': FaCar,
              }
              const IconComponent = categoryIcons[categoria] || FaCar
              
              return (
                <Card
                  key={categoria}
                  cursor="pointer"
                  borderWidth="2px"
                  borderColor="transparent"
                  _hover={{
                    borderColor: 'brand.300',
                    bg: 'brand.50',
                    transform: 'translateY(-2px)',
                    boxShadow: 'md',
                  }}
                  transition="all 0.2s"
                  borderRadius="xl"
                >
                  <CardBody p={4}>
                    <HStack spacing={3}>
                      <Box
                        as={IconComponent}
                        color="brand.500"
                        boxSize={6}
                      />
                      <Checkbox value={categoria} size="lg" colorScheme="brand">
                        {categoria}
                      </Checkbox>
                    </HStack>
                  </CardBody>
                </Card>
              )
            })}
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
          <SimpleGrid columns={{ base: 2, md: 3 }} spacing={3}>
            {availableBrands.map((marca) => {
              const modelCount = brandsModels?.[marca]?.length || 0
              return (
                <BrandCard
                  key={marca}
                  marca={marca}
                  modelCount={modelCount}
                  isChecked={formData.marcas_preferidas?.includes(marca) || false}
                  onToggle={(checked) => {
                    const currentBrands = formData.marcas_preferidas || []
                    const newBrands = checked
                      ? [...currentBrands, marca]
                      : currentBrands.filter(b => b !== marca)
                    updateFormData({ marcas_preferidas: newBrands })
                  }}
                />
              )
            })}
          </SimpleGrid>
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
        borderRadius="xl"
        borderWidth="2px"
        borderColor="secondary.200"
        borderRadius="xl"
      >
        <Text fontSize="sm" color="gray.700">
          💡 <strong>Dica:</strong> Essas preferências são opcionais. Se você
          não selecionar nada, nossa IA considerará todas as opções disponíveis
          para você.
        </Text>
      </Box>

      {/* Ready to see results */}
      <Box
        bg="secondary.50"
        p={5}
        borderRadius="xl"
        borderWidth="2px"
        borderColor="secondary.200"
        textAlign="center"
        borderRadius="xl"
      >
        <Text fontSize="md" fontWeight="bold" color="secondary.800" mb={2}>
          ✨ Tudo pronto!
        </Text>
        <Text fontSize="sm" color="secondary.700">
          Clique em "Ver Recomendações" para descobrir os carros perfeitos para você
        </Text>
      </Box>
    </VStack>
  )
}