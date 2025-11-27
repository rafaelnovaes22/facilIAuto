import { Box, Container, SimpleGrid, Text, VStack, Icon, Heading } from '@chakra-ui/react'
import { FaShieldAlt, FaSearch, FaHistory, FaCheckDouble } from 'react-icons/fa'

export default function TrustBadges() {
    const badges = [
        {
            title: 'Laudo Cautelar Aprovado',
            description: 'Todos os carros passam por vistoria completa para garantir estrutura e procedência.',
            icon: FaCheckDouble,
        },
        {
            title: 'Histórico Verificado',
            description: 'Nossa IA analisa o histórico do veículo em bases nacionais para evitar fraudes.',
            icon: FaHistory,
        },
        {
            title: 'Garantia de Procedência',
            description: 'Trabalhamos apenas com concessionárias verificadas e com boa reputação no mercado.',
            icon: FaShieldAlt,
        },
        {
            title: 'Inspeção Detalhada',
            description: 'Mais de 150 itens verificados antes do carro ser anunciado na plataforma.',
            icon: FaSearch,
        },
    ]

    return (
        <Box bg="white" py={20}>
            <Container maxW="container.xl">
                <VStack spacing={12}>
                    <VStack spacing={4} textAlign="center">
                        <Heading size="xl" color="gray.800">
                            Segurança em Primeiro Lugar
                        </Heading>
                        <Text fontSize="lg" color="gray.600" maxW="2xl">
                            Sabemos que comprar um seminovo exige confiança. Por isso, somos rigorosos.
                        </Text>
                    </VStack>

                    <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={8} w="full">
                        {badges.map((badge, index) => (
                            <VStack
                                key={index}
                                bg="gray.50"
                                p={8}
                                borderRadius="xl"
                                spacing={4}
                                align="center"
                                textAlign="center"
                                _hover={{
                                    bg: 'brand.50',
                                    transform: 'translateY(-4px)',
                                }}
                                transition="all 0.3s"
                            >
                                <Box
                                    p={4}
                                    bg="white"
                                    borderRadius="full"
                                    boxShadow="md"
                                    color="brand.500"
                                >
                                    <Icon as={badge.icon} w={8} h={8} />
                                </Box>
                                <Heading size="md" color="gray.800">
                                    {badge.title}
                                </Heading>
                                <Text color="gray.600" fontSize="sm">
                                    {badge.description}
                                </Text>
                            </VStack>
                        ))}
                    </SimpleGrid>
                </VStack>
            </Container>
        </Box>
    )
}
