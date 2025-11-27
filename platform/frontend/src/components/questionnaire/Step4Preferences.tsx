// 🎨 UX + ✍️ Content Creator: Step 4 - Preferências de Marca e Modelo
import {
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  SimpleGrid,
  Box,
  HStack,
  Card,
  CardBody,
  Select,
  Badge,
  Icon,
} from '@chakra-ui/react'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { BRANDS_MODELS, getBrandsOrdered, getModelsByBrand } from '@/data/brandsModels'
import { FaCheck, FaCar } from 'react-icons/fa'

// Marcas mais famosas (priorizadas no topo da lista)
const TOP_BRANDS = [
  'Chevrolet',
  'Volkswagen',
  'Fiat',
  'Hyundai',
  'Toyota',
  'Honda',
  'Jeep',
  'Renault',
  'Nissan',
  'Ford',
]

// Função para ordenar marcas: top brands primeiro, depois alfabético
const getOrderedBrands = (): string[] => {
  const allBrands = getBrandsOrdered()
  const otherBrands = allBrands.filter(b => !TOP_BRANDS.includes(b)).sort()
  return [...TOP_BRANDS, ...otherBrands]
}

export const Step4Preferences = () => {
  const { formData, updateFormData } = useQuestionnaireStore()

  const orderedBrands = getOrderedBrands()
  const selectedBrand = formData.marca_preferida || ''
  const availableModels = selectedBrand ? getModelsByBrand(selectedBrand) : []

  const handleBrandChange = (brand: string) => {
    updateFormData({
      marca_preferida: brand || undefined,
      modelo_preferido: undefined // Limpa modelo ao trocar marca
    })
  }

  const handleModelChange = (model: string) => {
    updateFormData({ modelo_preferido: model || undefined })
  }

  return (
    <VStack spacing={8} align="stretch" maxW="700px" mx="auto">
      {/* Header */}
      <VStack spacing={3} textAlign="center">
        <Heading size="lg" color="gray.800">
          Tem alguma preferência? 🚗
        </Heading>
        <Text color="gray.600" fontSize="md">
          Se você já sabe qual marca ou modelo quer, nos conte aqui
        </Text>
      </VStack>

      {/* Seleção de Marca */}
      <FormControl>
        <FormLabel fontSize="md" fontWeight="semibold" mb={3}>
          <HStack spacing={2}>
            <Icon as={FaCar} color="brand.500" />
            <Text>Marca do Carro</Text>
          </HStack>
        </FormLabel>
        <Text fontSize="sm" color="gray.600" mb={4}>
          Escolha uma marca para ver os modelos disponíveis (opcional)
        </Text>

        <Select
          placeholder="Selecione uma marca..."
          value={selectedBrand}
          onChange={(e) => handleBrandChange(e.target.value)}
          size="lg"
          bg="white"
          borderWidth="2px"
          borderColor="gray.200"
          _hover={{ borderColor: 'brand.300' }}
          _focus={{ borderColor: 'brand.500', boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)' }}
        >
          <optgroup label="⭐ Marcas Populares">
            {TOP_BRANDS.map((marca) => (
              <option key={marca} value={marca}>
                {marca} ({BRANDS_MODELS[marca]?.length || 0} modelos)
              </option>
            ))}
          </optgroup>
          <optgroup label="📋 Outras Marcas">
            {orderedBrands
              .filter(b => !TOP_BRANDS.includes(b))
              .map((marca) => (
                <option key={marca} value={marca}>
                  {marca} ({BRANDS_MODELS[marca]?.length || 0} modelos)
                </option>
              ))}
          </optgroup>
        </Select>
      </FormControl>

      {/* Seleção de Modelo (aparece após selecionar marca) */}
      {selectedBrand && (
        <FormControl>
          <FormLabel fontSize="md" fontWeight="semibold" mb={3}>
            <HStack spacing={2}>
              <Badge colorScheme="brand" fontSize="sm">{selectedBrand}</Badge>
              <Text>Modelo</Text>
            </HStack>
          </FormLabel>
          <Text fontSize="sm" color="gray.600" mb={4}>
            Escolha um modelo específico ou deixe em branco para ver todos
          </Text>

          <Select
            placeholder={`Todos os modelos ${selectedBrand}...`}
            value={formData.modelo_preferido || ''}
            onChange={(e) => handleModelChange(e.target.value)}
            size="lg"
            bg="white"
            borderWidth="2px"
            borderColor="gray.200"
            _hover={{ borderColor: 'brand.300' }}
            _focus={{ borderColor: 'brand.500', boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)' }}
          >
            {availableModels.map((modelo) => (
              <option key={modelo} value={modelo}>
                {modelo}
              </option>
            ))}
          </Select>
        </FormControl>
      )}

      {/* Resumo da Seleção */}
      {(selectedBrand || formData.modelo_preferido) && (
        <Card bg="brand.50" borderWidth="2px" borderColor="brand.200">
          <CardBody>
            <HStack spacing={3}>
              <Icon as={FaCheck} color="brand.500" />
              <Box>
                <Text fontWeight="semibold" color="brand.700">
                  Sua preferência:
                </Text>
                <Text color="brand.600">
                  {selectedBrand}
                  {formData.modelo_preferido && ` ${formData.modelo_preferido}`}
                </Text>
              </Box>
            </HStack>
          </CardBody>
        </Card>
      )}

      {/* Info Box */}
      <Box
        bg="secondary.50"
        p={4}
        borderRadius="xl"
        borderWidth="2px"
        borderColor="secondary.200"
      >
        <Text fontSize="sm" color="gray.700">
          💡 <strong>Dica:</strong> Essa preferência é opcional. Se você não
          selecionar nada, nossa IA vai considerar todas as marcas e modelos
          disponíveis para encontrar o carro ideal para você.
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
