import {
  Box,
  Container,
  Heading,
  Text,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Progress,
  VStack,
  HStack,
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Button,
  Alert,
  AlertIcon,
  Icon
} from '@chakra-ui/react'
import { FaCar, FaUsers, FaDollarSign, FaChartLine, FaMobile, FaWhatsapp } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'

const DashboardPage = () => {
  const navigate = useNavigate()

  // Mock data para demonstração
  const dashboardData = {
    overview: {
      totalCars: 89,
      activeRecommendations: 156,
      conversions: 23,
      revenue: 1847500
    },
    recentActivity: [
      { id: 1, cliente: "Maria Silva", carro: "Fiat Cronos Drive", status: "Interessada", data: "Hoje 14:30" },
      { id: 2, cliente: "João Santos", carro: "Toyota Yaris XLS", status: "Agendado", data: "Hoje 11:15" },
      { id: 3, cliente: "Ana Costa", carro: "Chevrolet Tracker", status: "Proposta", data: "Ontem 16:45" },
      { id: 4, cliente: "Pedro Lima", carro: "Honda Civic", status: "Vendido", data: "Ontem 09:20" },
      { id: 5, cliente: "Carla Rocha", carro: "Volkswagen Polo", status: "Interessada", data: "26/12 15:30" }
    ],
    topCars: [
      { modelo: "Fiat Cronos Drive", recomendacoes: 34, conversoes: 8, taxa: 23.5 },
      { modelo: "Toyota Yaris XLS", recomendacoes: 28, conversoes: 6, taxa: 21.4 },
      { modelo: "Chevrolet Tracker", recomendacoes: 25, conversoes: 4, taxa: 16.0 },
      { modelo: "Honda Civic", recomendacoes: 22, conversoes: 5, taxa: 22.7 },
      { modelo: "Volkswagen Polo", recomendacoes: 19, conversoes: 3, taxa: 15.8 }
    ]
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Vendido': return 'green'
      case 'Proposta': return 'blue'
      case 'Agendado': return 'orange'
      case 'Interessada': return 'purple'
      default: return 'gray'
    }
  }

  return (
    <Box py={8}>
      <Container maxW="container.xl">
        <VStack spacing={8}>
          {/* Header */}
          <Box w="full">
            <HStack justify="space-between" align="center" mb={2}>
              <VStack align="start" spacing={1}>
                <Heading size="xl" color="blue.600">
                  📊 Dashboard RobustCar
                </Heading>
                <Text color="gray.600">
                  Sistema FacilIAuto • Última atualização: agora
                </Text>
              </VStack>
              <HStack>
                <Button colorScheme="blue" onClick={() => navigate('/questionario')}>
                  ➕ Nova Recomendação
                </Button>
                <Button variant="outline" onClick={() => navigate('/')}>
                  🏠 Início
                </Button>
              </HStack>
            </HStack>
            
            <Alert status="success" rounded="lg">
              <AlertIcon />
              <Box>
                <Text fontWeight="medium">
                  🎯 Sistema FacilIAuto ativo e funcionando perfeitamente!
                </Text>
                <Text fontSize="sm">
                  89 carros processados • IA gerando recomendações em tempo real • Mobile-first operacional
                </Text>
              </Box>
            </Alert>
          </Box>

          {/* Key Metrics */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} w="full">
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>
                    <HStack>
                      <Icon as={FaCar} color="blue.500" />
                      <Text>Carros no Estoque</Text>
                    </HStack>
                  </StatLabel>
                  <StatNumber color="blue.600">{dashboardData.overview.totalCars}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    Sistema ativo e monitorando
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>
                    <HStack>
                      <Icon as={FaUsers} color="green.500" />
                      <Text>Recomendações Geradas</Text>
                    </HStack>
                  </StatLabel>
                  <StatNumber color="green.600">{dashboardData.overview.activeRecommendations}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    +24% vs. semana passada
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>
                    <HStack>
                      <Icon as={FaChartLine} color="orange.500" />
                      <Text>Conversões</Text>
                    </HStack>
                  </StatLabel>
                  <StatNumber color="orange.600">{dashboardData.overview.conversions}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    Taxa: 14.7% (vs. 11% anterior)
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>
                    <HStack>
                      <Icon as={FaDollarSign} color="purple.500" />
                      <Text>Vendas Influenciadas</Text>
                    </HStack>
                  </StatLabel>
                  <StatNumber color="purple.600">
                    R$ {(dashboardData.overview.revenue / 1000).toFixed(0)}k
                  </StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    ROI: 380% do investimento
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Performance Indicators */}
          <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8} w="full">
            <Card>
              <CardHeader>
                <Heading size="md">⚡ Performance do Sistema</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={4}>
                  <Box w="full">
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm">Tempo de Resposta</Text>
                      <Text fontSize="sm" fontWeight="bold" color="green.600">&lt;2s</Text>
                    </HStack>
                    <Progress value={95} colorScheme="green" />
                  </Box>

                  <Box w="full">
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm">Accuracy das Recomendações</Text>
                      <Text fontSize="sm" fontWeight="bold" color="blue.600">84.3%</Text>
                    </HStack>
                    <Progress value={84.3} colorScheme="blue" />
                  </Box>

                  <Box w="full">
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm">Satisfação dos Clientes</Text>
                      <Text fontSize="sm" fontWeight="bold" color="purple.600">87%</Text>
                    </HStack>
                    <Progress value={87} colorScheme="purple" />
                  </Box>

                  <Box w="full">
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm">Uso Mobile</Text>
                      <Text fontSize="sm" fontWeight="bold" color="orange.600">78%</Text>
                    </HStack>
                    <Progress value={78} colorScheme="orange" />
                  </Box>
                </VStack>
              </CardBody>
            </Card>

            <Card>
              <CardHeader>
                <Heading size="md">🎯 Carros Mais Recomendados</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={3}>
                  {dashboardData.topCars.map((car, index) => (
                    <Box key={index} w="full" p={3} bg="gray.50" rounded="lg">
                      <HStack justify="space-between" mb={2}>
                        <Text fontWeight="medium" fontSize="sm">{car.modelo}</Text>
                        <Badge colorScheme="blue">{car.recomendacoes} rec.</Badge>
                      </HStack>
                      <HStack justify="space-between" fontSize="xs" color="gray.600">
                        <Text>{car.conversoes} conversões</Text>
                        <Text fontWeight="bold" color="green.600">{car.taxa}% taxa</Text>
                      </HStack>
                      <Progress value={car.taxa} size="sm" colorScheme="green" mt={1} />
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Recent Activity */}
          <Card w="full">
            <CardHeader>
              <HStack justify="space-between">
                <Heading size="md">🕒 Atividade Recente</Heading>
                <HStack>
                  <Icon as={FaMobile} color="blue.500" />
                  <Text fontSize="sm" color="gray.600">78% via mobile</Text>
                </HStack>
              </HStack>
            </CardHeader>
            <CardBody>
              <TableContainer>
                <Table variant="simple">
                  <Thead>
                    <Tr>
                      <Th>Cliente</Th>
                      <Th>Carro Recomendado</Th>
                      <Th>Status</Th>
                      <Th>Data/Hora</Th>
                      <Th>Ações</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {dashboardData.recentActivity.map((activity) => (
                      <Tr key={activity.id}>
                        <Td fontWeight="medium">{activity.cliente}</Td>
                        <Td>{activity.carro}</Td>
                        <Td>
                          <Badge colorScheme={getStatusColor(activity.status)}>
                            {activity.status}
                          </Badge>
                        </Td>
                        <Td fontSize="sm" color="gray.600">{activity.data}</Td>
                        <Td>
                          <HStack spacing={2}>
                            <Button size="xs" colorScheme="green" leftIcon={<FaWhatsapp />}>
                              WhatsApp
                            </Button>
                            <Button size="xs" variant="outline">
                              Detalhes
                            </Button>
                          </HStack>
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </TableContainer>
            </CardBody>
          </Card>

          {/* System Features */}
          <Card w="full">
            <CardHeader>
              <Heading size="md">🚀 Recursos FacilIAuto Ativos</Heading>
            </CardHeader>
            <CardBody>
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
                <VStack spacing={3} textAlign="center" p={4} bg="blue.50" rounded="lg">
                  <Icon as={FaMobile} boxSize={8} color="blue.500" />
                  <Text fontWeight="bold">📱 Mobile-First</Text>
                  <Text fontSize="sm" color="gray.600">
                    Interface otimizada para smartphones. Vendedores podem usar em qualquer lugar do showroom.
                  </Text>
                  <Badge colorScheme="blue">78% dos acessos via mobile</Badge>
                </VStack>

                <VStack spacing={3} textAlign="center" p={4} bg="green.50" rounded="lg">
                  <Icon as={FaChartLine} boxSize={8} color="green.500" />
                  <Text fontWeight="bold">🤖 IA Responsável</Text>
                  <Text fontSize="sm" color="gray.600">
                    Recomendações sempre dentro do orçamento do cliente. Guardrails impedem sugestões inadequadas.
                  </Text>
                  <Badge colorScheme="green">84.3% de accuracy</Badge>
                </VStack>

                <VStack spacing={3} textAlign="center" p={4} bg="purple.50" rounded="lg">
                  <Icon as={FaWhatsapp} boxSize={8} color="purple.500" />
                  <Text fontWeight="bold">📱 Compartilhamento</Text>
                  <Text fontSize="sm" color="gray.600">
                    Recomendações podem ser compartilhadas via WhatsApp instantaneamente para os clientes.
                  </Text>
                  <Badge colorScheme="purple">85% compartilham via WhatsApp</Badge>
                </VStack>
              </SimpleGrid>
            </CardBody>
          </Card>

          {/* ROI Summary */}
          <Alert status="success" rounded="lg" p={6}>
            <AlertIcon />
            <Box>
              <Text fontWeight="bold" mb={2}>
                💰 ROI do Sistema FacilIAuto
              </Text>
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                <Text fontSize="sm">
                  <strong>Investimento Mensal:</strong> R$ 997 (Plano Profissional)
                </Text>
                <Text fontSize="sm">
                  <strong>Vendas Influenciadas:</strong> R$ 1.847k (23 carros)
                </Text>
                <Text fontSize="sm">
                  <strong>ROI:</strong> <span style={{color: 'green'}}>380%</span> (vs. 120% esperado)
                </Text>
              </SimpleGrid>
            </Box>
          </Alert>

          {/* Action Items */}
          <Card w="full">
            <CardHeader>
              <Heading size="md">📋 Próximas Ações Recomendadas</Heading>
            </CardHeader>
            <CardBody>
              <VStack align="stretch" spacing={3}>
                <HStack justify="space-between" p={3} bg="blue.50" rounded="lg">
                  <Text fontSize="sm">
                    <strong>Treinar equipe</strong> - 3 vendedores ainda não usaram o sistema mobile
                  </Text>
                  <Button size="sm" colorScheme="blue">Agendar</Button>
                </HStack>

                <HStack justify="space-between" p={3} bg="green.50" rounded="lg">
                  <Text fontSize="sm">
                    <strong>Follow-up</strong> - 8 clientes com recomendações há +48h sem contato
                  </Text>
                  <Button size="sm" colorScheme="green">Listar</Button>
                </HStack>

                <HStack justify="space-between" p={3} bg="orange.50" rounded="lg">
                  <Text fontSize="sm">
                    <strong>Estoque</strong> - 12 carros com 0 recomendações no último mês
                  </Text>
                  <Button size="sm" colorScheme="orange">Analisar</Button>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        </VStack>
      </Container>
    </Box>
  )
}

export default DashboardPage
