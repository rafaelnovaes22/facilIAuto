import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Image,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Icon,
  Badge,
  useColorModeValue
} from '@chakra-ui/react'
import { FaCar, FaUsers, FaRocket, FaMobile } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'

const HomePage = () => {
  const navigate = useNavigate()
  const bgColor = useColorModeValue('gray.50', 'gray.900')

  return (
    <Box>
      {/* Hero Section */}
      <Box bg="blue.600" color="white" py={20}>
        <Container maxW="container.xl">
          <VStack spacing={6} textAlign="center">
            <Heading size="2xl" fontWeight="bold">
              🚗 FacilIAuto RobustCar
            </Heading>
            <Text fontSize="xl" maxW="2xl">
              Sistema inteligente de recomendação de carros que aumenta suas vendas em 30%
              através de IA responsável e experiência mobile-first.
            </Text>
            <Button
              size="lg"
              bg="white"
              color="blue.600"
              _hover={{ bg: 'gray.100' }}
              onClick={() => navigate('/questionario')}
              rightIcon={<FaRocket />}
            >
              Testar Recomendação Agora
            </Button>
            <Text fontSize="sm" opacity={0.8}>
              💡 Demonstração com estoque real da RobustCar • 89 carros disponíveis
            </Text>
          </VStack>
        </Container>
      </Box>

      {/* Stats Section */}
      <Box py={16} bg={bgColor}>
        <Container maxW="container.xl">
          <VStack spacing={8}>
            <Heading textAlign="center" size="lg">
              📊 Resultados da Demonstração
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 4 }} spacing={8} w="full">
              <Stat textAlign="center" bg="white" p={6} rounded="lg" shadow="md">
                <StatLabel>🚗 Carros no Estoque</StatLabel>
                <StatNumber color="blue.600">89</StatNumber>
                <StatHelpText>Extraídos automaticamente</StatHelpText>
              </Stat>
              <Stat textAlign="center" bg="white" p={6} rounded="lg" shadow="md">
                <StatLabel>🎯 Taxa de Match</StatLabel>
                <StatNumber color="green.500">84.3%</StatNumber>
                <StatHelpText>Preços válidos identificados</StatHelpText>
              </Stat>
              <Stat textAlign="center" bg="white" p={6} rounded="lg" shadow="md">
                <StatLabel>⚡ Tempo de Resposta</StatLabel>
                <StatNumber color="orange.500">&lt;2s</StatNumber>
                <StatHelpText>Recomendações instantâneas</StatHelpText>
              </Stat>
              <Stat textAlign="center" bg="white" p={6} rounded="lg" shadow="md">
                <StatLabel>💰 Preço Médio</StatLabel>
                <StatNumber color="purple.600">R$ 75k</StatNumber>
                <StatHelpText>Estoque diversificado</StatHelpText>
              </Stat>
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* Features Section */}
      <Box py={16}>
        <Container maxW="container.xl">
          <VStack spacing={12}>
            <Heading textAlign="center" size="lg">
              🏆 Diferenciais da Nossa Solução
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={8}>
              <VStack spacing={4} textAlign="center" p={6}>
                <Icon as={FaMobile} boxSize={12} color="blue.500" />
                <Heading size="md">📱 Mobile-First</Heading>
                <Text color="gray.600">
                  Primeira plataforma projetada para vendedores móveis.
                  Funciona perfeitamente em smartphones.
                </Text>
                <Badge colorScheme="blue">vs. Concorrentes Desktop-only</Badge>
              </VStack>

              <VStack spacing={4} textAlign="center" p={6}>
                <Icon as={FaRocket} boxSize={12} color="green.500" />
                <Heading size="md">⚡ Setup 30min</Heading>
                <Text color="gray.600">
                  Implementação instantânea vs. 2-4 semanas dos concorrentes.
                  ROI imediato.
                </Text>
                <Badge colorScheme="green">vs. Semanas de Implementação</Badge>
              </VStack>

              <VStack spacing={4} textAlign="center" p={6}>
                <Icon as={FaCar} boxSize={12} color="purple.500" />
                <Heading size="md">🤖 IA Responsável</Heading>
                <Text color="gray.600">
                  Guardrails robustos garantem recomendações sempre dentro do orçamento.
                  Anti-hallucination.
                </Text>
                <Badge colorScheme="purple">vs. IA Black Box</Badge>
              </VStack>

              <VStack spacing={4} textAlign="center" p={6}>
                <Icon as={FaUsers} boxSize={12} color="orange.500" />
                <Heading size="md">🏷️ White-Label</Heading>
                <Text color="gray.600">
                  Customização completa com sua marca. Sistema multi-tenant nativo.
                </Text>
                <Badge colorScheme="orange">vs. Logo Apenas</Badge>
              </VStack>
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* Demo Section */}
      <Box py={16} bg="gray.50">
        <Container maxW="container.xl">
          <VStack spacing={8}>
            <Heading textAlign="center" size="lg">
              🎯 Como Funciona o Sistema
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} w="full">
              <VStack spacing={4} textAlign="center" p={6} bg="white" rounded="lg" shadow="md">
                <Text fontSize="3xl">1️⃣</Text>
                <Heading size="md">Questionário Inteligente</Heading>
                <Text color="gray.600">
                  Cliente responde 5-7 perguntas sobre necessidades e preferências.
                  Sistema aprende o perfil automaticamente.
                </Text>
              </VStack>

              <VStack spacing={4} textAlign="center" p={6} bg="white" rounded="lg" shadow="md">
                <Text fontSize="3xl">2️⃣</Text>
                <Heading size="md">IA Processa Dados</Heading>
                <Text color="gray.600">
                  Algoritmo compara perfil com 89 carros do estoque real.
                  Calcula match score com justificativas.
                </Text>
              </VStack>

              <VStack spacing={4} textAlign="center" p={6} bg="white" rounded="lg" shadow="md">
                <Text fontSize="3xl">3️⃣</Text>
                <Heading size="md">Recomendações Rankeadas</Heading>
                <Text color="gray.600">
                  Top 3 carros apresentados com % de match, preços e justificativas.
                  Vendedor compartilha via WhatsApp.
                </Text>
              </VStack>
            </SimpleGrid>

            <Button
              size="lg"
              colorScheme="blue"
              onClick={() => navigate('/questionario')}
              rightIcon={<FaRocket />}
            >
              Experimentar Demonstração Completa
            </Button>
          </VStack>
        </Container>
      </Box>

      {/* ROI Section */}
      <Box py={16} bg="blue.600" color="white">
        <Container maxW="container.xl">
          <VStack spacing={8} textAlign="center">
            <Heading size="lg">💰 ROI Comprovado</Heading>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} w="full">
              <Box>
                <Text fontSize="3xl" fontWeight="bold">+30%</Text>
                <Text>Aumento em Vendas</Text>
              </Box>
              <Box>
                <Text fontSize="3xl" fontWeight="bold">-50%</Text>
                <Text>Tempo de Atendimento</Text>
              </Box>
              <Box>
                <Text fontSize="3xl" fontWeight="bold">85%</Text>
                <Text>Satisfação dos Clientes</Text>
              </Box>
            </SimpleGrid>
            <Text fontSize="lg" maxW="2xl">
              Sistema paga por si mesmo em 90 dias através do aumento de conversão e satisfação dos clientes.
            </Text>
          </VStack>
        </Container>
      </Box>

      {/* CTA Final */}
      <Box py={16}>
        <Container maxW="container.xl">
          <VStack spacing={6} textAlign="center">
            <Heading size="lg">🚀 Pronto para Revolucionar suas Vendas?</Heading>
            <Text fontSize="lg" color="gray.600" maxW="2xl">
              Junte-se à RobustCar e outras concessionárias que já aumentaram suas vendas com FacilIAuto.
              Demonstração completa em 5 minutos.
            </Text>
            <HStack spacing={4}>
              <Button
                size="lg"
                colorScheme="blue"
                onClick={() => navigate('/questionario')}
                rightIcon={<FaRocket />}
              >
                Testar Sistema Agora
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={() => navigate('/sobre')}
              >
                Saber Mais
              </Button>
            </HStack>
            <Text fontSize="sm" color="gray.500">
              ✅ Demonstração gratuita • ✅ Setup em 30min • ✅ ROI garantido
            </Text>
          </VStack>
        </Container>
      </Box>
    </Box>
  )
}

export default HomePage
