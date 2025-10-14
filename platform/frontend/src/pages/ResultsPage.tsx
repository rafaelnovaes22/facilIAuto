// 🎨 UX + 🤖 AI Engineer + 📈 Data Analyst: Página de resultados
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Select,
  Badge,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  SimpleGrid,
  useDisclosure,
} from '@chakra-ui/react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { FaArrowLeft, FaFilter, FaSortAmountDown } from 'react-icons/fa'
import type { RecommendationResponse, Recommendation } from '@/types'
import { CarCard } from '@/components/results/CarCard'
import { CarDetailsModal } from '@/components/results/CarDetailsModal'

export default function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const data = location.state?.recommendations as RecommendationResponse | undefined

  // State para filtros e ordenação
  const [sortBy, setSortBy] = useState<'score' | 'price_asc' | 'price_desc'>('score')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  
  // State para modal de detalhes
  const { isOpen: isDetailsOpen, onOpen: onDetailsOpen, onClose: onDetailsClose } = useDisclosure()
  const [selectedCar, setSelectedCar] = useState<Recommendation['car'] | null>(null)

  // 📈 Data Analyst: Track de visualizações
  const handleWhatsAppClick = (car: Recommendation['car']) => {
    console.log('WhatsApp Click:', {
      car_id: car.id,
      car_name: car.nome,
      dealership: car.dealership_name,
      price: car.preco,
    })
    // Aqui seria integrado com analytics (Google Analytics, Mixpanel, etc)
  }

  // Handler para abrir modal de detalhes
  const handleDetailsClick = (car: Recommendation['car']) => {
    setSelectedCar(car)
    onDetailsOpen()
    
    // 📈 Analytics: Track visualização de detalhes
    console.log('Details View:', {
      car_id: car.id,
      car_name: car.nome,
      total_images: car.imagens?.length || 0,
    })
  }

  // Filtrar e ordenar recomendações
  const processedRecommendations = useMemo(() => {
    if (!data?.recommendations) return []

    let filtered = [...data.recommendations]

    // Filtrar por categoria
    if (filterCategory !== 'all') {
      filtered = filtered.filter((rec) => rec.car.categoria === filterCategory)
    }

    // Ordenar
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return b.match_score - a.match_score
        case 'price_asc':
          return a.car.preco - b.car.preco
        case 'price_desc':
          return b.car.preco - a.car.preco
        default:
          return 0
      }
    })

    return filtered
  }, [data?.recommendations, sortBy, filterCategory])

  // Categorias únicas para filtro
  const categories = useMemo(() => {
    if (!data?.recommendations) return []
    const cats = new Set(data.recommendations.map((rec) => rec.car.categoria))
    return Array.from(cats).sort()
  }, [data?.recommendations])

  // Loading state
  if (!data) {
    return (
      <Box bg="gray.50" minH="100vh" display="flex" alignItems="center" justifyContent="center">
        <VStack spacing={4}>
          <Spinner size="xl" color="brand.500" thickness="4px" />
          <Text color="gray.600">Carregando recomendações...</Text>
        </VStack>
      </Box>
    )
  }

  // Nenhum resultado
  if (data.total_recommendations === 0) {
    return (
      <Box bg="gray.50" minH="100vh" py={10}>
        <Container maxW="container.md">
          <Alert
            status="info"
            variant="subtle"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            textAlign="center"
            height="400px"
            borderRadius="xl"
          >
            <AlertIcon boxSize="40px" mr={0} />
            <AlertTitle mt={4} mb={1} fontSize="lg">
              Nenhum carro encontrado
            </AlertTitle>
            <AlertDescription maxWidth="sm" fontSize="md">
              Não encontramos carros que correspondam exatamente aos seus critérios.
              Tente ajustar seu orçamento ou preferências.
            </AlertDescription>
            <Button
              mt={6}
              colorScheme="brand"
              onClick={() => navigate('/questionario')}
            >
              Tentar Novamente
            </Button>
          </Alert>
        </Container>
      </Box>
    )
  }

  return (
    <Box bg="gray.50" minH="100vh" py={10}>
      <Container maxW="container.xl">
        <VStack spacing={8} align="stretch">
          {/* Header */}
          <VStack spacing={4} align="stretch">
            <Button
              variant="ghost"
              size="sm"
              leftIcon={<FaArrowLeft />}
              onClick={() => navigate('/questionario')}
              alignSelf="flex-start"
            >
              Voltar ao questionário
            </Button>

            <Box>
              <Heading size="2xl" color="gray.800" mb={2}>
                🎉 Encontramos {data.total_recommendations} carros para você!
              </Heading>
              <Text fontSize="lg" color="gray.600">
                Recomendações personalizadas baseadas nas suas preferências
              </Text>
            </Box>

            {/* Profile Summary */}
            <Box
              bg="white"
              p={6}
              borderRadius="xl"
              boxShadow="sm"
            >
              <Heading size="sm" color="gray.700" mb={3}>
                📋 Resumo do Perfil
              </Heading>
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                <VStack align="flex-start" spacing={1}>
                  <Text fontSize="xs" color="gray.600" fontWeight="semibold">
                    Orçamento
                  </Text>
                  <Text fontSize="sm" color="gray.800">
                    {data.profile_summary.budget_range}
                  </Text>
                </VStack>

                <VStack align="flex-start" spacing={1}>
                  <Text fontSize="xs" color="gray.600" fontWeight="semibold">
                    Uso Principal
                  </Text>
                  <Text fontSize="sm" color="gray.800">
                    {data.profile_summary.usage}
                  </Text>
                </VStack>

                <VStack align="flex-start" spacing={1}>
                  <Text fontSize="xs" color="gray.600" fontWeight="semibold">
                    Localização
                  </Text>
                  <Text fontSize="sm" color="gray.800">
                    {data.profile_summary.location || 'Não especificada'}
                  </Text>
                </VStack>
              </SimpleGrid>

              {/* Top Priorities */}
              {data.profile_summary.top_priorities && data.profile_summary.top_priorities.length > 0 && (
                <Box mt={4}>
                  <Text fontSize="xs" color="gray.600" fontWeight="semibold" mb={2}>
                    Suas prioridades principais:
                  </Text>
                  <HStack spacing={2} flexWrap="wrap">
                    {data.profile_summary.top_priorities.map((priority) => (
                      <Badge key={priority} colorScheme="brand" fontSize="xs" px={3} py={1}>
                        {priority}
                      </Badge>
                    ))}
                  </HStack>
                </Box>
              )}
            </Box>
          </VStack>

          {/* Filters & Sort */}
          <HStack
            bg="white"
            p={4}
            borderRadius="lg"
            spacing={4}
            flexWrap="wrap"
            boxShadow="sm"
          >
            <HStack flex={1} minW="200px">
              <FaFilter color="gray" />
              <Text fontSize="sm" fontWeight="semibold" color="gray.700">
                Categoria:
              </Text>
              <Select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                size="sm"
                maxW="200px"
              >
                <option value="all">Todas</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </Select>
            </HStack>

            <HStack flex={1} minW="200px">
              <FaSortAmountDown color="gray" />
              <Text fontSize="sm" fontWeight="semibold" color="gray.700">
                Ordenar por:
              </Text>
              <Select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                size="sm"
                maxW="200px"
              >
                <option value="score">Melhor Match</option>
                <option value="price_asc">Menor Preço</option>
                <option value="price_desc">Maior Preço</option>
              </Select>
            </HStack>

            <Text fontSize="sm" color="gray.600">
              {processedRecommendations.length} resultado(s)
            </Text>
          </HStack>

          {/* Results Grid */}
          <VStack spacing={4} align="stretch">
            {processedRecommendations.map((recommendation) => (
              <CarCard
                key={recommendation.car.id}
                recommendation={recommendation}
                onWhatsAppClick={handleWhatsAppClick}
                onDetailsClick={handleDetailsClick}
              />
            ))}
          </VStack>

          {/* Modal de Detalhes do Carro */}
          <CarDetailsModal
            isOpen={isDetailsOpen}
            onClose={onDetailsClose}
            car={selectedCar}
          />

          {/* Footer CTA */}
          <Box
            bg="white"
            p={8}
            borderRadius="xl"
            boxShadow="sm"
            textAlign="center"
          >
            <Heading size="md" color="gray.800" mb={2}>
              Não encontrou o que procurava?
            </Heading>
            <Text color="gray.600" mb={4}>
              Refaça o questionário ajustando suas preferências
            </Text>
            <Button
              colorScheme="brand"
              size="lg"
              onClick={() => navigate('/questionario')}
            >
              Buscar Novamente
            </Button>
          </Box>
        </VStack>
      </Container>
    </Box>
  )
}
