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
    Image,
    Link,
} from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import {
    FaRocket,
    FaBrain,
    FaChartLine,
    FaWhatsapp,
    FaCheckCircle,
} from 'react-icons/fa'
import PartnerLogos from '@/components/PartnerLogos'
import CarHighlights from '@/components/CarHighlights'
import Testimonials from '@/components/Testimonials'
import TrustBadges from '@/components/TrustBadges'

export default function HomePage() {
    const navigate = useNavigate()

    return (
        <Box bg="white">
            {/* HERO SECTION */}
            <Box
                position="relative"
                minH="90vh"
                display="flex"
                alignItems="center"
                overflow="hidden"
            >
                {/* Background Image with Overlay */}
                <Box
                    position="absolute"
                    top={0}
                    left={0}
                    right={0}
                    bottom={0}
                    zIndex={0}
                >
                    <Image
                        src="https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=1920&auto=format&fit=crop"
                        alt="Carro Premium"
                        w="full"
                        h="full"
                        objectFit="cover"
                    />
                    <Box
                        position="absolute"
                        top={0}
                        left={0}
                        right={0}
                        bottom={0}
                        bgGradient="linear(to-r, blackAlpha.800, blackAlpha.600, transparent)"
                    />
                </Box>

                <Container maxW="container.xl" position="relative" zIndex={1} py={20}>
                    <VStack
                        align="flex-start"
                        spacing={8}
                        maxW="2xl"
                        animation="fadeIn 0.8s ease-in"
                    >
                        {/* Badge */}
                        <Box
                            bg="brand.500"
                            color="white"
                            px={4}
                            py={2}
                            borderRadius="full"
                            fontSize="sm"
                            fontWeight="bold"
                            boxShadow="lg"
                        >
                            🚀 O jeito mais inteligente de comprar seminovos
                        </Box>

                        {/* Main Heading */}
                        <Heading
                            as="h1"
                            size="3xl"
                            color="white"
                            lineHeight="1.1"
                            textShadow="0 2px 4px rgba(0,0,0,0.3)"
                        >
                            Seu Seminovo de Confiança, Escolhido por IA
                        </Heading>

                        {/* Subheading */}
                        <Text fontSize="xl" color="gray.100" lineHeight="1.6">
                            Esqueça a busca interminável. Nossa inteligência artificial analisa milhares de ofertas e encontra o carro perfeito para sua necessidade e bolso.
                        </Text>

                        {/* CTA Buttons */}
                        <Stack direction={{ base: 'column', sm: 'row' }} spacing={4} w="full">
                            <Button
                                size="lg"
                                h="64px"
                                px={8}
                                fontSize="xl"
                                colorScheme="brand"
                                rightIcon={<FaRocket />}
                                onClick={() => navigate('/questionario')}
                                _hover={{
                                    transform: 'translateY(-4px)',
                                    boxShadow: 'xl',
                                }}
                                transition="all 0.3s"
                            >
                                Descobrir Meu Carro Ideal
                            </Button>
                            <Button
                                size="lg"
                                h="64px"
                                px={8}
                                fontSize="xl"
                                bg="whiteAlpha.200"
                                color="white"
                                _hover={{
                                    bg: 'whiteAlpha.300',
                                }}
                                leftIcon={<FaWhatsapp />}
                                onClick={() => window.open('https://wa.me/5511999999999', '_blank')}
                            >
                                Falar com Consultor
                            </Button>
                        </Stack>

                        {/* Social Proof Text */}
                        <HStack spacing={2} color="gray.300" fontSize="sm">
                            <Icon as={FaCheckCircle} color="green.400" />
                            <Text>Mais de 500 carros analisados hoje</Text>
                            <Text mx={2}>•</Text>
                            <Icon as={FaCheckCircle} color="green.400" />
                            <Text>50+ Concessionárias Parceiras</Text>
                        </HStack>
                    </VStack>
                </Container>
            </Box>

            {/* PARTNER LOGOS */}
            <PartnerLogos />

            {/* HIGHLIGHTS */}
            <Box id="destaques">
                <CarHighlights />
            </Box>

            {/* HOW IT WORKS */}
            <Box id="como-funciona" bg="gray.50" py={20}>
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
                                title="Responda o Quiz"
                                description="Conte-nos sobre suas necessidades, orçamento e preferências em 3 minutos."
                                icon={FaBrain}
                            />
                            <StepCard
                                number="2"
                                title="IA Analisa"
                                description="Nossa inteligência artificial cruza seus dados com milhares de ofertas verificadas."
                                icon={FaRocket}
                            />
                            <StepCard
                                number="3"
                                title="Receba Recomendações"
                                description="Veja os melhores matches e negocie direto com a concessionária via WhatsApp."
                                icon={FaChartLine}
                            />
                        </SimpleGrid>
                    </VStack>
                </Container>
            </Box>

            {/* TRUST BADGES */}
            <Box id="seguranca">
                <TrustBadges />
            </Box>

            {/* TESTIMONIALS */}
            <Box id="depoimentos">
                <Testimonials />
            </Box>

            {/* CTA FINAL */}
            <Box bgGradient="linear(to-r, brand.600, brand.800)" py={24} position="relative" overflow="hidden">
                <Box
                    position="absolute"
                    top={0}
                    left={0}
                    right={0}
                    bottom={0}
                    bgImage="url('https://www.transparenttextures.com/patterns/carbon-fibre.png')"
                    opacity={0.1}
                />
                <Container maxW="container.md" position="relative" zIndex={1}>
                    <VStack spacing={8} textAlign="center" color="white">
                        <Heading size="2xl">
                            Pare de Procurar, Comece a Dirigir
                        </Heading>
                        <Text fontSize="xl" opacity={0.9}>
                            Faça como mais de 500 pessoas e encontre seu seminovo ideal hoje mesmo.
                        </Text>
                        <Button
                            size="lg"
                            h="64px"
                            px={16}
                            fontSize="xl"
                            bg="white"
                            color="brand.700"
                            rightIcon={<FaRocket />}
                            onClick={() => navigate('/questionario')}
                            _hover={{
                                transform: 'translateY(-4px)',
                                boxShadow: '2xl',
                            }}
                            transition="all 0.3s"
                        >
                            Começar Quiz Gratuito
                        </Button>
                    </VStack>
                </Container>
            </Box>

            {/* FOOTER */}
            <Box bg="gray.900" color="white" py={12}>
                <Container maxW="container.xl">
                    <Stack
                        direction={{ base: 'column', md: 'row' }}
                        spacing={8}
                        justify="space-between"
                        align="center"
                    >
                        <VStack align={{ base: 'center', md: 'flex-start' }} spacing={2}>
                            <HStack>
                                <Image
                                    src="/src/assets/faciliauto-logo.png"
                                    alt="FacilIAuto Logo"
                                    h="40px"
                                    filter="brightness(0) invert(1)"
                                />
                            </HStack>
                            <Text fontSize="sm" color="gray.400">
                                A revolução na compra de seminovos.
                            </Text>
                        </VStack>

                        <HStack spacing={8}>
                            <Link href="#" color="gray.400" _hover={{ color: 'white' }}>Termos de Uso</Link>
                            <Link href="#" color="gray.400" _hover={{ color: 'white' }}>Privacidade</Link>
                            <Text fontSize="sm" color="gray.400">
                                © 2024 FacilIAuto.
                            </Text>
                        </HStack>
                    </Stack>
                </Container>
            </Box>

            {/* Floating WhatsApp Button */}
            <Box
                position="fixed"
                bottom={8}
                right={8}
                zIndex={999}
            >
                <Button
                    w={16}
                    h={16}
                    borderRadius="full"
                    colorScheme="green"
                    boxShadow="lg"
                    onClick={() => window.open('https://wa.me/5511999999999', '_blank')}
                    _hover={{
                        transform: 'scale(1.1)',
                    }}
                    transition="all 0.2s"
                >
                    <Icon as={FaWhatsapp} w={8} h={8} />
                </Button>
            </Box>
        </Box>
    )
}

// ============================================
// SUB-COMPONENTS
// ============================================

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
