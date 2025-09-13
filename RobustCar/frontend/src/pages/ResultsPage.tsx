import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Card,
  CardBody,
  Image,
  Badge,
  Divider,
  Progress,
  SimpleGrid,
  Alert,
  AlertIcon,
  useToast,
  Spinner,
  Icon,
  Flex,
  Spacer
} from '@chakra-ui/react'
import { FaWhatsapp, FaPhone, FaMapMarkerAlt, FaGasPump, FaCar, FaCalendarAlt } from 'react-icons/fa'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

interface CarRecommendation {
  carro: {
    titulo: string
    preco: number
    ano: number
    km: number
    combustivel: string
    marca: string
    categoria: string
    cor: string
    cidade: string
  }
  score: number
  justificativa: string
  pontos_fortes: string[]
  pontos_atencao: string[]
  match_percentage: number
}

const ResultsPage = () => {
  const navigate = useNavigate()
  const toast = useToast()
  const [recommendations, setRecommendations] = useState<CarRecommendation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [questionnaireData, setQuestionnaireData] = useState<any>(null)

  useEffect(() => {
    // Recuperar dados do questionário
    const savedData = localStorage.getItem('questionario_data')
    if (!savedData) {
      toast({
        title: "❌ Dados não encontrados",
        description: "Por favor, complete o questionário primeiro.",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
      navigate('/questionario')
      return
    }

    setQuestionnaireData(JSON.parse(savedData))
    
    // Simular chamada à API e gerar recomendações mock
    generateMockRecommendations()
  }, [navigate, toast])

  const generateMockRecommendations = async () => {
    setIsLoading(true)
    
    // Simular tempo de processamento
    await new Promise(resolve => setTimeout(resolve, 3000))

    // Recomendações mock baseadas no estoque real da RobustCar
    const mockRecommendations: CarRecommendation[] = [
      {
        carro: {
          titulo: "Fiat Cronos Drive 1.3",
          preco: 84990,
          ano: 2022,
          km: 25000,
          combustivel: "Flex",
          marca: "Fiat",
          categoria: "Sedan",
          cor: "Branco",
          cidade: "São Paulo"
        },
        score: 8.7,
        justificativa: "Excelente custo-benefício que atende perfeitamente seu orçamento e necessidades familiares. O Cronos é conhecido pela economia de combustível e espaço interno.",
        pontos_fortes: [
          "Dentro do orçamento definido",
          "Ótimo espaço interno para família",
          "Economia de combustível comprovada",
          "Baixo custo de manutenção",
          "Boa revenda"
        ],
        pontos_atencao: [
          "Motor 1.3 pode ser limitado em subidas",
          "Porta-malas poderia ser maior"
        ],
        match_percentage: 87
      },
      {
        carro: {
          titulo: "Toyota Yaris Hatch XLS 1.5",
          preco: 97990,
          ano: 2023,
          km: 15000,
          combustivel: "Flex",
          marca: "Toyota",
          categoria: "Hatch",
          cor: "Prata",
          cidade: "São Paulo"
        },
        score: 8.4,
        justificativa: "Toyota oferece confiabilidade excepcional e ótima economia. Ideal para uso urbano com a praticidade de um hatch compacto.",
        pontos_fortes: [
          "Confiabilidade Toyota",
          "Baixíssimo consumo",
          "Facilidade para estacionar",
          "Tecnologia embarcada",
          "Garantia de fábrica"
        ],
        pontos_atencao: [
          "Preço um pouco acima do ideal",
          "Espaço traseiro limitado"
        ],
        match_percentage: 84
      },
      {
        carro: {
          titulo: "Chevrolet Tracker LT 1.0 Turbo",
          preco: 91990,
          ano: 2022,
          km: 32000,
          combustivel: "Flex",
          marca: "Chevrolet",
          categoria: "SUV",
          cor: "Azul",
          cidade: "São Paulo"
        },
        score: 7.9,
        justificativa: "SUV compacto com boa posição de dirigir e versatilidade. O motor turbo oferece boa performance urbana.",
        pontos_fortes: [
          "Posição elevada de dirigir",
          "Bom espaço interno",
          "Motor turbo eficiente",
          "Design moderno",
          "Itens de série completos"
        ],
        pontos_atencao: [
          "Consumo um pouco maior que sedans",
          "Quilometragem relativamente alta"
        ],
        match_percentage: 79
      }
    ]

    setRecommendations(mockRecommendations)
    setIsLoading(false)
  }

  const handleWhatsAppShare = (car: CarRecommendation) => {
    const message = `🚗 *Recomendação FacilIAuto - RobustCar*

*${car.carro.titulo}*
💰 Preço: R$ ${car.preco.toLocaleString()}
📅 Ano: ${car.carro.ano}
🛣️ KM: ${car.carro.km.toLocaleString()}
⭐ Match: ${car.match_percentage}%

📍 *Por que recomendamos:*
${car.justificativa}

✅ *Pontos fortes:*
${car.pontos_fortes.map(p => `• ${p}`).join('\n')}

⚠️ *Pontos de atenção:*
${car.pontos_atencao.map(p => `• ${p}`).join('\n')}

---
Gerado automaticamente pelo sistema FacilIAuto 🤖`

    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`
    window.open(whatsappUrl, '_blank')
  }

  const handleScheduleVisit = (car: CarRecommendation) => {
    toast({
      title: "📅 Agendamento solicitado",
      description: `Entraremos em contato para agendar sua visita para ver o ${car.carro.titulo}.`,
      status: "success",
      duration: 5000,
      isClosable: true,
    })
  }

  if (isLoading) {
    return (
      <Box py={16}>
        <Container maxW="container.md">
          <VStack spacing={8} textAlign="center">
            <Spinner size="xl" color="blue.500" thickness="4px" />
            <Heading size="lg">🤖 Processando suas preferências...</Heading>
            <Text color="gray.600">
              Nossa IA está analisando 89 carros do estoque da RobustCar para encontrar as melhores opções para você.
            </Text>
            <Progress w="full" colorScheme="blue" isIndeterminate />
          </VStack>
        </Container>
      </Box>
    )
  }

  return (
    <Box py={8}>
      <Container maxW="container.lg">
        <VStack spacing={8}>
          {/* Header */}
          <Box textAlign="center">
            <Heading size="xl" color="blue.600">
              🎯 Suas Recomendações Personalizadas
            </Heading>
            <Text color="gray.600" mt={2}>
              Baseado em suas respostas, encontramos os carros perfeitos para você no estoque da RobustCar
            </Text>
          </Box>

          {/* Summary */}
          {questionnaireData && (
            <Alert status="info" rounded="lg">
              <AlertIcon />
              <Box>
                <Text fontWeight="medium">
                  Orçamento: R$ {questionnaireData.orcamento_min?.toLocaleString()} - R$ {questionnaireData.orcamento_max?.toLocaleString()}
                </Text>
                <Text fontSize="sm">
                  Uso principal: {questionnaireData.uso_principal} • {questionnaireData.tamanho_familia} pessoas
                </Text>
              </Box>
            </Alert>
          )}

          {/* Recommendations */}
          <VStack spacing={6} w="full">
            {recommendations.map((rec, index) => (
              <Card key={index} w="full" shadow="lg" borderWidth={index === 0 ? 2 : 1} borderColor={index === 0 ? "blue.500" : "gray.200"}>
                {index === 0 && (
                  <Box bg="blue.500" color="white" py={2} px={4} roundedTop="md">
                    <Text fontWeight="bold" textAlign="center">
                      🏆 MELHOR MATCH - {rec.match_percentage}%
                    </Text>
                  </Box>
                )}
                
                <CardBody>
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                    {/* Car Image Placeholder */}
                    <Box>
                      <Box
                        h="200px"
                        bg="gray.100"
                        rounded="lg"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        mb={4}
                      >
                        <VStack>
                          <Icon as={FaCar} boxSize={12} color="gray.400" />
                          <Text color="gray.500" fontSize="sm">Foto do veículo</Text>
                        </VStack>
                      </Box>
                      
                      {/* Car Details */}
                      <VStack align="stretch" spacing={3}>
                        <Heading size="lg" color="blue.600">
                          {rec.carro.titulo}
                        </Heading>
                        
                        <Text fontSize="2xl" fontWeight="bold" color="green.600">
                          R$ {rec.carro.preco.toLocaleString()}
                        </Text>

                        <SimpleGrid columns={2} spacing={4}>
                          <HStack>
                            <Icon as={FaCalendarAlt} color="gray.500" />
                            <Text fontSize="sm">{rec.carro.ano}</Text>
                          </HStack>
                          <HStack>
                            <Icon as={FaCar} color="gray.500" />
                            <Text fontSize="sm">{rec.carro.km.toLocaleString()} km</Text>
                          </HStack>
                          <HStack>
                            <Icon as={FaGasPump} color="gray.500" />
                            <Text fontSize="sm">{rec.carro.combustivel}</Text>
                          </HStack>
                          <HStack>
                            <Icon as={FaMapMarkerAlt} color="gray.500" />
                            <Text fontSize="sm">{rec.carro.cidade}</Text>
                          </HStack>
                        </SimpleGrid>

                        <HStack>
                          <Badge colorScheme="blue">{rec.carro.marca}</Badge>
                          <Badge colorScheme="green">{rec.carro.categoria}</Badge>
                          <Badge colorScheme="purple">{rec.carro.cor}</Badge>
                        </HStack>
                      </VStack>
                    </Box>

                    {/* Recommendation Details */}
                    <VStack align="stretch" spacing={4}>
                      {/* Match Score */}
                      <Box>
                        <Flex justify="space-between" mb={2}>
                          <Text fontWeight="medium">Match Score</Text>
                          <Text color="blue.600" fontWeight="bold">{rec.match_percentage}%</Text>
                        </Flex>
                        <Progress value={rec.match_percentage} colorScheme="blue" rounded="full" />
                      </Box>

                      {/* Justificativa */}
                      <Box>
                        <Text fontWeight="medium" mb={2}>💡 Por que recomendamos:</Text>
                        <Text color="gray.700" fontSize="sm">
                          {rec.justificativa}
                        </Text>
                      </Box>

                      <Divider />

                      {/* Pontos Fortes */}
                      <Box>
                        <Text fontWeight="medium" color="green.600" mb={2}>✅ Pontos fortes:</Text>
                        <VStack align="stretch" spacing={1}>
                          {rec.pontos_fortes.map((ponto, i) => (
                            <Text key={i} fontSize="sm" color="gray.700">• {ponto}</Text>
                          ))}
                        </VStack>
                      </Box>

                      {/* Pontos de Atenção */}
                      <Box>
                        <Text fontWeight="medium" color="orange.600" mb={2}>⚠️ Pontos de atenção:</Text>
                        <VStack align="stretch" spacing={1}>
                          {rec.pontos_atencao.map((ponto, i) => (
                            <Text key={i} fontSize="sm" color="gray.700">• {ponto}</Text>
                          ))}
                        </VStack>
                      </Box>

                      {/* Actions */}
                      <VStack spacing={3} pt={4}>
                        <Button
                          colorScheme="green"
                          size="lg"
                          w="full"
                          leftIcon={<FaWhatsapp />}
                          onClick={() => handleWhatsAppShare(rec)}
                        >
                          Compartilhar no WhatsApp
                        </Button>
                        
                        <HStack w="full" spacing={3}>
                          <Button
                            colorScheme="blue"
                            variant="outline"
                            flex={1}
                            leftIcon={<FaPhone />}
                            onClick={() => handleScheduleVisit(rec)}
                          >
                            Agendar Visita
                          </Button>
                          <Button
                            colorScheme="gray"
                            variant="outline"
                            flex={1}
                          >
                            Mais Detalhes
                          </Button>
                        </HStack>
                      </VStack>
                    </VStack>
                  </SimpleGrid>
                </CardBody>
              </Card>
            ))}
          </VStack>

          {/* Footer Actions */}
          <VStack spacing={4} w="full" pt={8}>
            <Divider />
            
            <Text textAlign="center" color="gray.600">
              Não encontrou o que procura? Temos mais opções!
            </Text>
            
            <HStack spacing={4}>
              <Button
                colorScheme="blue"
                variant="outline"
                onClick={() => navigate('/questionario')}
              >
                🔄 Refazer Questionário
              </Button>
              
              <Button
                colorScheme="blue"
                onClick={() => {
                  toast({
                    title: "📞 Contato solicitado",
                    description: "Um consultor da RobustCar entrará em contato em breve!",
                    status: "success",
                    duration: 5000,
                    isClosable: true,
                  })
                }}
              >
                💬 Falar com Consultor
              </Button>
            </HStack>

            {/* RobustCar Info */}
            <Box textAlign="center" p={6} bg="gray.50" rounded="lg" w="full">
              <Heading size="md" mb={2}>🏢 RobustCar São Paulo</Heading>
              <Text color="gray.600" mb={4}>
                📍 Rua Exemplo, 123 - São Paulo, SP<br />
                📞 (11) 99999-9999<br />
                🕒 Seg-Sex: 8h-18h | Sáb: 8h-16h
              </Text>
              <Text fontSize="sm" color="gray.500">
                ✨ Sistema de recomendação FacilIAuto • Resultados baseados em estoque real
              </Text>
            </Box>
          </VStack>
        </VStack>
      </Container>
    </Box>
  )
}

export default ResultsPage
