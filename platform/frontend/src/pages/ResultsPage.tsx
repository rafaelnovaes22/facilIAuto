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
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useDisclosure,
} from '@chakra-ui/react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { FaArrowLeft, FaFilter, FaSortAmountDown, FaCalendar } from 'react-icons/fa'
import type { RecommendationResponse, Recommendation } from '@/types'
import { CarCard } from '@/components/results/CarCard'
import { CarDetailsModal } from '@/components/results/CarDetailsModal'
import { ProfileSummary } from '@/components/results/ProfileSummary'
import { useQuestionnaireStore } from '@/store/questionnaireStore'

export default function ResultsPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const data = location.state?.recommendations as RecommendationResponse | undefined
  const resetForm = useQuestionnaireStore((state) => state.resetForm)

  // State para filtros e ordenação
  const [sortBy, setSortBy] = useState<'score' | 'price_asc' | 'price_desc'>('score')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterYearMin, setFilterYearMin] = useState<number | null>(null)
  const [filterYearMax, setFilterYearMax] = useState<number | null>(null)

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

  // Handler para resetar pesquisa e voltar ao início (LIMPA TUDO)
  const handleResetAndRestart = () => {
    console.log('Reset: Usuário iniciando nova pesquisa do zero')
    resetForm() // Limpa todos os dados do formulário
    navigate('/questionario') // Volta para o questionário
  }

  // Handler para editar pesquisa (MANTÉM DADOS)
  const handleEditSearch = () => {
    console.log('Edit: Usuário editando pesquisa existente')
    // Não chama resetForm() - mantém os dados
    // Apenas volta para o step 0 do questionário
    const setCurrentStep = useQuestionnaireStore.getState().setCurrentStep
    setCurrentStep(0)
    navigate('/questionario')
  }

  // Filtrar e ordenar recomendações
  const processedRecommendations = useMemo(() => {
    if (!data?.recommendations) return []

    let filtered = [...data.recommendations]

    // Filtrar por categoria
    if (filterCategory !== 'all') {
      filtered = filtered.filter((rec) => rec.car.categoria === filterCategory)
    }

    // Filtrar por ano mínimo
    if (filterYearMin !== null) {
      filtered = filtered.filter((rec) => rec.car.ano >= filterYearMin)
    }

    // Filtrar por ano máximo
    if (filterYearMax !== null) {
      filtered = filtered.filter((rec) => rec.car.ano <= filterYearMax)
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
  }, [data?.recommendations, sortBy, filterCategory, filterYearMin, filterYearMax])

  // Categorias únicas para filtro
  const categories = useMemo(() => {
    if (!data?.recommendations) return []
    const cats = new Set(data.recommendations.map((rec) => rec.car.categoria))
    return Array.from(cats).sort()
  }, [data?.recommendations])

  // Anos disponíveis para filtro
  const availableYears = useMemo(() => {
    if (!data?.recommendations) return { min: 2000, max: new Date().getFullYear() }
    const years = data.recommendations.map((rec) => rec.car.ano)
    return {
      min: Math.min(...years),
      max: Math.max(...years),
    }
  }, [data?.recommendations])

  // Gerar opções de anos para os selects
  const yearOptions = useMemo(() => {
    const years: number[] = []
    for (let year = availableYears.max; year >= availableYears.min; year--) {
      years.push(year)
    }
    return years
  }, [availableYears])

  // Handler para limpar filtros de ano
  const handleClearYearFilters = () => {
    setFilterYearMin(null)
    setFilterYearMax(null)
  }

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
              onClick={handleResetAndRestart}
              alignSelf="flex-start"
            >
              ← Voltar ao início
            </Button>

            <Box>
              <Heading size="2xl" color="gray.800" mb={2}>
                {data.total_recommendations > 0 ? (
                  <>🎉 Encontramos {data.total_recommendations} carros para você!</>
                ) : (
                  <>😔 Nenhum carro encontrado</>
                )}
              </Heading>
              <Text fontSize="lg" color="gray.600">
                {data.total_recommendations > 0 ? (
                  'Recomendações personalizadas baseadas nas suas preferências'
                ) : (
                  'Não encontramos carros que atendam aos seus critérios'
                )}
              </Text>
            </Box>

            {/* Profile Summary */}
            <ProfileSummary
              profileSummary={data.profile_summary}
              onEdit={handleEditSearch}
            />
          </VStack>

          {/* Filters & Sort */}
          <VStack
            bg="white"
            p={4}
            borderRadius="lg"
            spacing={4}
            boxShadow="sm"
            align="stretch"
          >
            {/* Primeira linha: Categoria e Ordenação */}
            <HStack spacing={4} flexWrap="wrap">
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
            </HStack>

            {/* Segunda linha: Filtros de Ano */}
            <HStack spacing={4} flexWrap="wrap" align="center">
              <HStack flex={1} minW="200px">
                <FaCalendar color="gray" />
                <Text fontSize="sm" fontWeight="semibold" color="gray.700">
                  Ano de:
                </Text>
                <Select
                  value={filterYearMin ?? ''}
                  onChange={(e) => setFilterYearMin(e.target.value ? Number(e.target.value) : null)}
                  size="sm"
                  maxW="150px"
                  placeholder="Qualquer"
                >
                  {yearOptions.map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </Select>
              </HStack>

              <HStack flex={1} minW="200px">
                <Text fontSize="sm" fontWeight="semibold" color="gray.700">
                  até:
                </Text>
                <Select
                  value={filterYearMax ?? ''}
                  onChange={(e) => setFilterYearMax(e.target.value ? Number(e.target.value) : null)}
                  size="sm"
                  maxW="150px"
                  placeholder="Qualquer"
                >
                  {yearOptions.map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </Select>
              </HStack>

              {(filterYearMin !== null || filterYearMax !== null) && (
                <Button
                  size="sm"
                  variant="ghost"
                  colorScheme="red"
                  onClick={handleClearYearFilters}
                >
                  Limpar Anos
                </Button>
              )}

              <Text fontSize="sm" color="gray.600" fontWeight="semibold">
                {processedRecommendations.length} resultado(s)
              </Text>
            </HStack>
          </VStack>

          {/* Results Grid ou Mensagem de Nenhum Resultado */}
          {data.total_recommendations === 0 || processedRecommendations.length === 0 ? (
            // Nenhum resultado encontrado
            <Alert
              status="info"
              variant="subtle"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              textAlign="center"
              minHeight="400px"
              borderRadius="xl"
              bg="white"
              boxShadow="sm"
            >
              <AlertIcon boxSize="40px" mr={0} />
              <AlertTitle mt={4} mb={1} fontSize="2xl" color="gray.800">
                Nenhum carro encontrado
              </AlertTitle>
              <AlertDescription maxWidth="md" fontSize="lg" color="gray.600">
                {data.total_recommendations === 0 ? (
                  <>
                    Não encontramos carros que correspondam aos seus critérios na faixa de{' '}
                    <Text as="span" fontWeight="bold" color="brand.600">
                      {data.profile_summary.budget_range}
                    </Text>
                    {data.profile_summary.usage === 'transporte_passageiros' && (
                      <>
                        {' '}para uso como <Text as="span" fontWeight="bold" color="brand.600">Uber/99</Text>
                      </>
                    )}
                    .
                  </>
                ) : (
                  'Nenhum carro corresponde aos filtros selecionados.'
                )}
              </AlertDescription>
              <VStack spacing={3} mt={6}>
                <Text fontSize="md" color="gray.600" fontWeight="semibold">
                  {data.profile_summary.usage === 'transporte_passageiros' ? 'Por que não encontramos?' : 'Sugestões:'}
                </Text>
                <VStack spacing={2} align="start">
                  {data.profile_summary.usage === 'transporte_passageiros' ? (
                    <>
                      <Text fontSize="sm" color="gray.600">
                        • Carros para Uber/99 precisam ter <strong>ano mínimo 2015</strong>
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        • Apenas <strong>modelos específicos</strong> são aceitos pelas plataformas
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        • Veículo não pode ter mais de <strong>10 anos de uso</strong>
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        • Tente <strong>ampliar o orçamento</strong> para R$ 40k-80k
                      </Text>
                    </>
                  ) : (
                    <>
                      <Text fontSize="sm" color="gray.600">
                        • Tente ampliar sua faixa de orçamento
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        • Ajuste suas preferências ou prioridades
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        • Remova filtros de categoria
                      </Text>
                    </>
                  )}
                </VStack>
              </VStack>
              <HStack spacing={4} mt={6}>
                <Button
                  colorScheme="brand"
                  size="lg"
                  onClick={handleEditSearch}
                >
                  ✏️ Editar Busca
                </Button>
                <Button
                  variant="outline"
                  colorScheme="brand"
                  size="lg"
                  onClick={handleResetAndRestart}
                >
                  🔄 Nova Busca
                </Button>
              </HStack>
            </Alert>
          ) : (
            // Grid de resultados
            <Box
              display="grid"
              gridTemplateColumns={{
                base: '1fr',           // Mobile: 1 coluna
                md: 'repeat(2, 1fr)',  // Tablet: 2 colunas
                lg: 'repeat(3, 1fr)',  // Desktop: 3 colunas
              }}
              gap={4}
            >
              {processedRecommendations.map((recommendation) => (
                <CarCard
                  key={recommendation.car.id}
                  recommendation={recommendation}
                  onWhatsAppClick={handleWhatsAppClick}
                  onDetailsClick={handleDetailsClick}
                />
              ))}
            </Box>
          )}

          {/* Modal de Detalhes do Carro */}
          <CarDetailsModal
            isOpen={isDetailsOpen}
            onClose={onDetailsClose}
            car={selectedCar}
          />

          {/* Footer CTA - Apenas quando há resultados */}
          {data.total_recommendations > 0 && processedRecommendations.length > 0 && (
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
                onClick={handleResetAndRestart}
              >
                Buscar Novamente
              </Button>
            </Box>
          )}
        </VStack>
      </Container>
    </Box>
  )
}
