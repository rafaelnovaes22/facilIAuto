import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  SimpleGrid,
  Card,
  CardBody,
  Icon,
  Badge,
  Divider,
  Button,
  Alert,
  AlertIcon
} from '@chakra-ui/react'
import { FaRocket, FaMobile, FaBrain, FaShieldAlt, FaUsers, FaChartLine } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'

const AboutPage = () => {
  const navigate = useNavigate()

  return (
    <Box py={8}>
      <Container maxW="container.xl">
        <VStack spacing={12}>
          {/* Header */}
          <Box textAlign="center">
            <Heading size="2xl" color="blue.600" mb={4}>
              🚀 Sobre o FacilIAuto
            </Heading>
            <Text fontSize="xl" color="gray.600" maxW="3xl">
              A primeira plataforma de recomendação automotiva mobile-first do Brasil, 
              projetada especificamente para revolucionar vendas em concessionárias.
            </Text>
          </Box>

          {/* Problem Statement */}
          <Box w="full">
            <Heading size="lg" textAlign="center" mb={8}>
              🎯 O Problema que Resolvemos
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8}>
              <Card bg="red.50" borderLeft="4px solid" borderColor="red.500">
                <CardBody>
                  <Text fontWeight="bold" color="red.600" mb={2}>
                    ❌ Processo Manual e Lento
                  </Text>
                  <Text color="gray.700" fontSize="sm">
                    Vendedores gastam 30+ minutos procurando carros manualmente, 
                    perdendo clientes por falta de agilidade.
                  </Text>
                </CardBody>
              </Card>

              <Card bg="orange.50" borderLeft="4px solid" borderColor="orange.500">
                <CardBody>
                  <Text fontWeight="bold" color="orange.600" mb={2}>
                    ❌ Ferramentas Desktop Ultrapassadas
                  </Text>
                  <Text color="gray.700" fontSize="sm">
                    Sistemas atuais não funcionam em mobile, limitando vendedores 
                    que precisam de mobilidade no showroom.
                  </Text>
                </CardBody>
              </Card>

              <Card bg="yellow.50" borderLeft="4px solid" borderColor="yellow.500">
                <CardBody>
                  <Text fontWeight="bold" color="yellow.600" mb={2}>
                    ❌ Setup Complexo e Caro
                  </Text>
                  <Text color="gray.700" fontSize="sm">
                    Implementações demoram 2-4 semanas e custam R$ 8k-15k/mês, 
                    inacessível para 80% das concessionárias.
                  </Text>
                </CardBody>
              </Card>
            </SimpleGrid>
          </Box>

          {/* Our Solution */}
          <Box w="full">
            <Heading size="lg" textAlign="center" mb={8}>
              ✅ Nossa Solução
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
              <VStack spacing={4} textAlign="center" p={6} bg="blue.50" rounded="lg">
                <Icon as={FaMobile} boxSize={12} color="blue.500" />
                <Heading size="md">📱 Mobile-First</Heading>
                <Text color="gray.600" fontSize="sm">
                  Primeira plataforma projetada para smartphones. 
                  Vendedores podem usar em qualquer lugar do showroom.
                </Text>
                <Badge colorScheme="blue">Inovação Disruptiva</Badge>
              </VStack>

              <VStack spacing={4} textAlign="center" p={6} bg="green.50" rounded="lg">
                <Icon as={FaRocket} boxSize={12} color="green.500" />
                <Heading size="md">⚡ Setup 30min</Heading>
                <Text color="gray.600" fontSize="sm">
                  Implementação instantânea vs. 2-4 semanas dos concorrentes. 
                  ROI desde o primeiro dia.
                </Text>
                <Badge colorScheme="green">95% Mais Rápido</Badge>
              </VStack>

              <VStack spacing={4} textAlign="center" p={6} bg="purple.50" rounded="lg">
                <Icon as={FaBrain} boxSize={12} color="purple.500" />
                <Heading size="md">🤖 IA Responsável</Heading>
                <Text color="gray.600" fontSize="sm">
                  Guardrails robustos garantem recomendações sempre dentro do orçamento. 
                  Anti-hallucination comprovado.
                </Text>
                <Badge colorScheme="purple">Confiabilidade Total</Badge>
              </VStack>

              <VStack spacing={4} textAlign="center" p={6} bg="orange.50" rounded="lg">
                <Icon as={FaShieldAlt} boxSize={12} color="orange.500" />
                <Heading size="md">🏷️ White-Label</Heading>
                <Text color="gray.600" fontSize="sm">
                  Customização completa com sua marca. 
                  Sistema multi-tenant nativo desde o início.
                </Text>
                <Badge colorScheme="orange">Sua Marca, Nossa Tech</Badge>
              </VStack>
            </SimpleGrid>
          </Box>

          {/* Technology */}
          <Box w="full">
            <Heading size="lg" textAlign="center" mb={8}>
              🔧 Tecnologia Comprovada
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8}>
              <Box>
                <Heading size="md" mb={4}>🏗️ Arquitetura Moderna</Heading>
                <VStack align="stretch" spacing={3}>
                  <HStack>
                    <Badge colorScheme="blue">Frontend</Badge>
                    <Text fontSize="sm">React + TypeScript + Chakra UI</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="green">Backend</Badge>
                    <Text fontSize="sm">FastAPI + Python + PostgreSQL</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="purple">IA</Badge>
                    <Text fontSize="sm">Machine Learning + Guardrails</Text>
                  </HStack>
                  <HStack>
                    <Badge colorScheme="orange">Deploy</Badge>
                    <Text fontSize="sm">Cloud-native + Multi-tenant</Text>
                  </HStack>
                </VStack>
              </Box>

              <Box>
                <Heading size="md" mb={4}>📊 Proof of Concept RobustCar</Heading>
                <VStack align="stretch" spacing={3}>
                  <HStack justify="space-between">
                    <Text fontSize="sm">🚗 Carros processados:</Text>
                    <Text fontWeight="bold">89</Text>
                  </HStack>
                  <HStack justify="space-between">
                    <Text fontSize="sm">🎯 Taxa de sucesso:</Text>
                    <Text fontWeight="bold" color="green.600">84.3%</Text>
                  </HStack>
                  <HStack justify="space-between">
                    <Text fontSize="sm">⚡ Tempo de resposta:</Text>
                    <Text fontWeight="bold" color="blue.600">&lt;2s</Text>
                  </HStack>
                  <HStack justify="space-between">
                    <Text fontSize="sm">🎯 Accuracy de match:</Text>
                    <Text fontWeight="bold" color="purple.600">60-80%</Text>
                  </HStack>
                </VStack>
              </Box>
            </SimpleGrid>
          </Box>

          {/* Market Opportunity */}
          <Box w="full">
            <Heading size="lg" textAlign="center" mb={8}>
              📈 Oportunidade de Mercado
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8}>
              <Card textAlign="center" p={6}>
                <CardBody>
                  <Icon as={FaUsers} boxSize={12} color="blue.500" mb={4} />
                  <Heading size="lg" color="blue.600">26.000+</Heading>
                  <Text fontWeight="medium">Concessionárias no Brasil</Text>
                  <Text fontSize="sm" color="gray.600" mt={2}>
                    Mercado total endereçável de R$ 500M+
                  </Text>
                </CardBody>
              </Card>

              <Card textAlign="center" p={6}>
                <CardBody>
                  <Icon as={FaChartLine} boxSize={12} color="green.500" mb={4} />
                  <Heading size="lg" color="green.600">80%</Heading>
                  <Text fontWeight="medium">Pequenas/Médias não atendidas</Text>
                  <Text fontSize="sm" color="gray.600" mt={2}>
                    Mercado endereçável de R$ 50M+ negligenciado
                  </Text>
                </CardBody>
              </Card>

              <Card textAlign="center" p={6}>
                <CardBody>
                  <Icon as={FaRocket} boxSize={12} color="purple.500" mb={4} />
                  <Heading size="lg" color="purple.600">R$ 6M+</Heading>
                  <Text fontWeight="medium">ARR potencial em 3 anos</Text>
                  <Text fontSize="sm" color="gray.600" mt={2}>
                    500 concessionárias × R$ 1k/mês média
                  </Text>
                </CardBody>
              </Card>
            </SimpleGrid>
          </Box>

          {/* Competitive Advantage */}
          <Box w="full">
            <Heading size="lg" textAlign="center" mb={8}>
              🏆 Vantagem Competitiva
            </Heading>
            <Card p={6}>
              <CardBody>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8}>
                  <Box>
                    <Heading size="md" color="green.600" mb={4}>✅ FacilIAuto</Heading>
                    <VStack align="stretch" spacing={2}>
                      <Text fontSize="sm">📱 Mobile-first nativo</Text>
                      <Text fontSize="sm">⚡ Setup em 30 minutos</Text>
                      <Text fontSize="sm">💰 R$ 497-1.997/mês</Text>
                      <Text fontSize="sm">🏷️ White-label completo</Text>
                      <Text fontSize="sm">🤖 IA transparente com guardrails</Text>
                      <Text fontSize="sm">🎯 Foco em pequenas/médias</Text>
                    </VStack>
                  </Box>

                  <Box>
                    <Heading size="md" color="red.600" mb={4}>❌ Concorrentes</Heading>
                    <VStack align="stretch" spacing={2}>
                      <Text fontSize="sm">🖥️ Desktop-only ou mobile limitado</Text>
                      <Text fontSize="sm">🐌 Setup de 2-4 semanas</Text>
                      <Text fontSize="sm">💸 R$ 2.500-15.000/mês</Text>
                      <Text fontSize="sm">🏷️ Logo apenas ou sem customização</Text>
                      <Text fontSize="sm">📦 IA black box ou sem IA</Text>
                      <Text fontSize="sm">🏢 Foco apenas em grandes</Text>
                    </VStack>
                  </Box>
                </SimpleGrid>
              </CardBody>
            </Card>
          </Box>

          {/* Pricing */}
          <Box w="full">
            <Heading size="lg" textAlign="center" mb={8}>
              💰 Modelo de Pricing
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
              <Card borderWidth={1} borderColor="gray.200">
                <CardBody>
                  <VStack spacing={4}>
                    <Badge colorScheme="blue" p={2} rounded="lg">BÁSICO</Badge>
                    <Heading size="lg" color="blue.600">R$ 497/mês</Heading>
                    <VStack align="stretch" spacing={2}>
                      <Text fontSize="sm">✅ Até 50 carros</Text>
                      <Text fontSize="sm">✅ 500 recomendações/mês</Text>
                      <Text fontSize="sm">✅ Suporte email</Text>
                      <Text fontSize="sm">✅ Logo + cor primária</Text>
                    </VStack>
                  </VStack>
                </CardBody>
              </Card>

              <Card borderWidth={2} borderColor="green.500" bg="green.50">
                <CardBody>
                  <VStack spacing={4}>
                    <Badge colorScheme="green" p={2} rounded="lg">PROFISSIONAL</Badge>
                    <Heading size="lg" color="green.600">R$ 997/mês</Heading>
                    <VStack align="stretch" spacing={2}>
                      <Text fontSize="sm">✅ Até 200 carros</Text>
                      <Text fontSize="sm">✅ 2.000 recomendações/mês</Text>
                      <Text fontSize="sm">✅ Analytics avançados</Text>
                      <Text fontSize="sm">✅ Customização completa</Text>
                    </VStack>
                    <Badge colorScheme="green">MAIS POPULAR</Badge>
                  </VStack>
                </CardBody>
              </Card>

              <Card borderWidth={1} borderColor="purple.200">
                <CardBody>
                  <VStack spacing={4}>
                    <Badge colorScheme="purple" p={2} rounded="lg">ENTERPRISE</Badge>
                    <Heading size="lg" color="purple.600">R$ 1.997/mês</Heading>
                    <VStack align="stretch" spacing={2}>
                      <Text fontSize="sm">✅ Estoque ilimitado</Text>
                      <Text fontSize="sm">✅ White-label completo</Text>
                      <Text fontSize="sm">✅ Suporte dedicado</Text>
                      <Text fontSize="sm">✅ Integrações custom</Text>
                    </VStack>
                  </VStack>
                </CardBody>
              </Card>
            </SimpleGrid>
          </Box>

          <Divider />

          {/* RobustCar Case Study */}
          <Alert status="success" rounded="lg" p={6}>
            <AlertIcon />
            <Box>
              <Text fontWeight="bold" mb={2}>
                🏆 Case Study: RobustCar São Paulo
              </Text>
              <Text fontSize="sm">
                A RobustCar está testando o FacilIAuto como early adopter. 
                Sistema já processou 89 carros do estoque real e está gerando recomendações 
                com 84.3% de precisão. Esta demonstração mostra o potencial completo da plataforma.
              </Text>
            </Box>
          </Alert>

          {/* CTA */}
          <VStack spacing={6} textAlign="center">
            <Heading size="lg">🚀 Pronto para Revolucionar suas Vendas?</Heading>
            <Text color="gray.600" maxW="2xl">
              Junte-se à RobustCar e outras concessionárias pioneiras que estão 
              aumentando suas vendas com a primeira plataforma mobile-first do Brasil.
            </Text>
            <HStack spacing={4}>
              <Button
                size="lg"
                colorScheme="blue"
                onClick={() => navigate('/questionario')}
              >
                🎯 Testar Demonstração
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={() => navigate('/')}
              >
                ← Voltar ao Início
              </Button>
            </HStack>
          </VStack>
        </VStack>
      </Container>
    </Box>
  )
}

export default AboutPage
