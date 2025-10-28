// 🎨 UX Especialist + ✍️ Content Creator + 💻 Tech Lead
import {
    Box,
    Container,
    Heading,
    Text,
    Button,
    VStack,
    HStack,
    SimpleGrid,
    Icon,
    Stack,
    Flex,
    Spinner,
    Alert,
    AlertIcon,
    AlertDescription,
} from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import {
    FaRocket,
    FaBrain,
    FaChartLine,
    FaClock,
    FaCheckCircle,
    FaHeart,
} from 'react-icons/fa'
import { useStats } from '@/hooks/useApi'
import { formatCurrency, formatNumber } from '@/services/api'

export default function HomePage() {
    const navigate = useNavigate()
    const { data: stats, isLoading, isError } = useStats()

    return (
        <Box bg="white">
            {/* HERO SECTION */}
            <Box
                bgGradient="linear(to-br, brand.50, white, secondary.50)"
                minH="90vh"
                display="flex"
                alignItems="center"
            >
                <Container maxW="container.xl" py={20}>
                    <VStack
                        spacing={8}
                        textAlign="center"
                        animation="fadeIn 0.8s ease-in"
                        sx={{
                            '@keyframes fadeIn': {
                                '0%': { opacity: 0, transform: 'translateY(20px)' },
                                '100%': { opacity: 1, transform: 'translateY(0)' },
                            },
                        }}
                    >
                        {/* Badge */}
                        <Box
                            bg="brand.100"
                            color="brand.700"
                            px={4}
                            py={2}
                            borderRadius="full"
                            fontSize="sm"
                            fontWeight="semibold"
                        >
                            🚀 Plataforma B2B de Recomendação Inteligente
                        </Box>

                        {/* Main Heading */}
                        <Heading
                            as="h1"
                            size="3xl"
                            bgGradient="linear(to-r, brand.500, secondary.500)"
                            bgClip="text"
                            maxW="4xl"
                            lineHeight="1.2"
                        >
                            Encontre o Carro Perfeito em 3 Minutos
                        </Heading>

                        {/* Subheading */}
                        <Text fontSize="2xl" color="gray.600" maxW="2xl" lineHeight="1.6">
                            Recomendação inteligente baseada em{' '}
                            <Text as="span" color="brand.600" fontWeight="semibold">
                                IA
                            </Text>
                            , considerando suas necessidades, orçamento e preferências
                        </Text>

                        {/* CTA Button */}
                        <Button
                            size="lg"
                            h="64px"
                            px={16}
                            fontSize="xl"
                            colorScheme="brand"
                            rightIcon={<FaRocket />}
                            onClick={() => navigate('/questionario')}
                            _hover={{
                                transform: 'translateY(-4px)',
                                boxShadow: '2xl',
                            }}
                            transition="all 0.3s"
                        >
                            Começar Agora - É Grátis
                        </Button>

                        {/* Trust Indicators */}
                        <HStack spacing={8} pt={4} flexWrap="wrap" justify="center">
                            <HStack>
                                <Icon as={FaClock} color="green.500" />
                                <Text fontSize="sm" color="gray.600">
                                    <strong>3 minutos</strong> para completar
                                </Text>
                            </HStack>
                            <HStack>
                                <Icon as={FaCheckCircle} color="green.500" />
                                <Text fontSize="sm" color="gray.600">
                                    <strong>100% gratuito</strong>
                                </Text>
                            </HStack>
                            <HStack>
                                <Icon as={FaHeart} color="green.500" />
                                <Text fontSize="sm" color="gray.600">
                                    <strong>Personalizado</strong> para você
                                </Text>
                            </HStack>
                        </HStack>

                        {/* Stats */}
                        {isLoading && (
                            <VStack pt={8} spacing={4}>
                                <Spinner size="lg" color="brand.500" thickness="4px" />
                                <Text fontSize="sm" color="gray.600">
                                    Carregando estatísticas...
                                </Text>
                            </VStack>
                        )}

                        {isError && (
                            <Alert
                                status="warning"
                                borderRadius="lg"
                                maxW="2xl"
                                mt={8}
                            >
                                <AlertIcon />
                                <AlertDescription>
                                    Não foi possível carregar as estatísticas no momento.
                                </AlertDescription>
                            </Alert>
                        )}

                        {!isLoading && !isError && stats && (
                            <SimpleGrid
                                columns={{ base: 1, md: 3 }}
                                spacing={8}
                                pt={8}
                                w="full"
                                animation="fadeIn 0.6s ease-in 0.3s both"
                            >
                                <StatCard
                                    label="Carros Disponíveis"
                                    value={formatNumber(stats.total_cars || 0)}
                                    icon={FaRocket}
                                />
                                <StatCard
                                    label="Concessionárias"
                                    value={formatNumber(stats.total_dealerships || 0)}
                                    icon={FaChartLine}
                                />
                                <StatCard
                                    label="Preço Médio"
                                    value={formatCurrency(stats.avg_price || 0)}
                                    icon={FaBrain}
                                />
                            </SimpleGrid>
                        )}
                    </VStack>
                </Container>
            </Box>

            {/* HOW IT WORKS */}
            <Box bg="gray.50" py={20}>
                <Container maxW="container.xl">
                    <VStack spacing={12}>
                        <VStack spacing={4} textAlign="center">
                            <Heading size="2xl" color="gray.800">
                                Como Funciona?
                            </Heading>
                            <Text fontSize="xl" color="gray.600" maxW="2xl">
                                Encontre seu carro ideal em apenas 3 passos simples
                            </Text>
                        </VStack>

                        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10} w="full">
                            <StepCard
                                number="1"
                                title="Responda o Questionário"
                                description="Conte-nos sobre suas necessidades, orçamento e preferências em 3 minutos"
                                icon={FaBrain}
                            />
                            <StepCard
                                number="2"
                                title="IA Analisa e Recomenda"
                                description="Nossa inteligência artificial analisa milhares de opções e encontra os melhores matches"
                                icon={FaRocket}
                            />
                            <StepCard
                                number="3"
                                title="Receba Recomendações"
                                description="Veja carros personalizados com score de compatibilidade e contato direto via WhatsApp"
                                icon={FaChartLine}
                            />
                        </SimpleGrid>
                    </VStack>
                </Container>
            </Box>

            {/* FEATURES */}
            <Box bg="white" py={20}>
                <Container maxW="container.xl">
                    <VStack spacing={12}>
                        <VStack spacing={4} textAlign="center">
                            <Heading size="2xl" color="gray.800">
                                Por Que FacilIAuto?
                            </Heading>
                            <Text fontSize="xl" color="gray.600" maxW="2xl">
                                A forma mais inteligente de encontrar seu próximo carro
                            </Text>
                        </VStack>

                        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8} w="full">
                            <FeatureCard
                                title="🎯 Recomendações Personalizadas"
                                description="Algoritmo de IA considera suas necessidades específicas e encontra o match perfeito"
                            />
                            <FeatureCard
                                title="⚡ Rápido e Fácil"
                                description="Questionário intuitivo de apenas 3 minutos. Sem complicações"
                            />
                            <FeatureCard
                                title="💰 Múltiplas Concessionárias"
                                description="Compare ofertas de diversas concessionárias em um só lugar"
                            />
                            <FeatureCard
                                title="📱 Contato Direto"
                                description="Fale diretamente com a concessionária via WhatsApp após escolher"
                            />
                        </SimpleGrid>
                    </VStack>
                </Container>
            </Box>

            {/* CTA FINAL */}
            <Box bgGradient="linear(to-r, brand.500, secondary.500)" py={20}>
                <Container maxW="container.md">
                    <VStack spacing={8} textAlign="center" color="white">
                        <Heading size="2xl">
                            Pronto para Encontrar Seu Carro Ideal?
                        </Heading>
                        <Text fontSize="xl" opacity={0.9}>
                            Comece agora e receba recomendações personalizadas em minutos
                        </Text>
                        <Button
                            size="lg"
                            h="64px"
                            px={16}
                            fontSize="xl"
                            bg="white"
                            color="brand.600"
                            rightIcon={<FaRocket />}
                            onClick={() => navigate('/questionario')}
                            _hover={{
                                transform: 'translateY(-4px)',
                                boxShadow: '2xl',
                            }}
                            transition="all 0.3s"
                        >
                            Começar Gratuitamente
                        </Button>
                    </VStack>
                </Container>
            </Box>

            {/* FOOTER */}
            <Box bg="gray.900" color="white" py={10}>
                <Container maxW="container.xl">
                    <Stack
                        direction={{ base: 'column', md: 'row' }}
                        spacing={8}
                        justify="space-between"
                        align="center"
                    >
                        <VStack align={{ base: 'center', md: 'flex-start' }} spacing={2}>
                            <Text fontSize="2xl" fontWeight="bold">
                                FacilIAuto
                            </Text>
                            <Text fontSize="sm" color="gray.400">
                                Recomendação Inteligente de Veículos
                            </Text>
                        </VStack>

                        <HStack spacing={8}>
                            <Text fontSize="sm" color="gray.400">
                                © 2024 FacilIAuto. Todos os direitos reservados.
                            </Text>
                        </HStack>
                    </Stack>
                </Container>
            </Box>
        </Box>
    )
}

// ============================================
// SUB-COMPONENTS
// ============================================

interface StatCardProps {
    label: string
    value: string
    icon: any
}

const StatCard = ({ label, value, icon }: StatCardProps) => (
    <VStack
        bg="white"
        p={6}
        borderRadius="xl"
        boxShadow="lg"
        spacing={3}
        _hover={{
            transform: 'translateY(-4px)',
            boxShadow: '2xl',
        }}
        transition="all 0.3s"
    >
        <Icon as={icon} boxSize={10} color="brand.500" />
        <Text fontSize="3xl" fontWeight="bold" color="gray.800">
            {value}
        </Text>
        <Text fontSize="sm" color="gray.600" textAlign="center">
            {label}
        </Text>
    </VStack>
)

interface StepCardProps {
    number: string
    title: string
    description: string
    icon: any
}

const StepCard = ({ number, title, description, icon }: StepCardProps) => (
    <VStack
        bg="white"
        p={8}
        borderRadius="2xl"
        boxShadow="md"
        spacing={4}
        position="relative"
        _hover={{
            boxShadow: 'xl',
            transform: 'translateY(-4px)',
        }}
        transition="all 0.3s"
    >
        <Flex
            position="absolute"
            top="-20px"
            left="50%"
            transform="translateX(-50%)"
            bg="brand.500"
            color="white"
            w="40px"
            h="40px"
            borderRadius="full"
            align="center"
            justify="center"
            fontSize="xl"
            fontWeight="bold"
            boxShadow="lg"
        >
            {number}
        </Flex>

        <Icon as={icon} boxSize={12} color="brand.400" mt={4} />
        <Heading size="md" color="gray.800" textAlign="center">
            {title}
        </Heading>
        <Text color="gray.600" textAlign="center" lineHeight="1.7">
            {description}
        </Text>
    </VStack>
)

interface FeatureCardProps {
    title: string
    description: string
}

const FeatureCard = ({ title, description }: FeatureCardProps) => (
    <Box
        bg="gray.50"
        p={6}
        borderRadius="xl"
        borderWidth="2px"
        borderColor="gray.100"
        _hover={{
            borderColor: 'brand.300',
            boxShadow: 'md',
        }}
        transition="all 0.3s"
    >
        <VStack align="flex-start" spacing={3}>
            <Text fontSize="xl" fontWeight="bold" color="gray.800">
                {title}
            </Text>
            <Text color="gray.600" lineHeight="1.7">
                {description}
            </Text>
        </VStack>
    </Box>
)
