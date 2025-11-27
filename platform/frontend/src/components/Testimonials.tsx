import { Box, Container, Heading, SimpleGrid, Text, VStack, Avatar, Icon, HStack } from '@chakra-ui/react'
import { FaQuoteLeft, FaStar } from 'react-icons/fa'

export default function Testimonials() {
    const testimonials = [
        {
            name: 'Ricardo Silva',
            role: 'Comprou um Honda Civic',
            image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=200&auto=format&fit=crop',
            content: 'Eu estava com medo de comprar um seminovo, mas o FacilIAuto me ajudou a encontrar um carro com laudo cautelar aprovado e garantia. O processo foi muito transparente.',
            rating: 5,
        },
        {
            name: 'Ana Costa',
            role: 'Comprou um Jeep Renegade',
            image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=200&auto=format&fit=crop',
            content: 'O quiz acertou em cheio! Eu nem sabia que queria um Renegade até ver a recomendação. O atendimento via WhatsApp da concessionária parceira foi excelente.',
            rating: 5,
        },
        {
            name: 'Carlos Mendes',
            role: 'Comprou um VW Polo',
            image: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=200&auto=format&fit=crop',
            content: 'Economizei muito tempo. Em vez de ficar rodando de loja em loja, recebi as melhores opções no meu perfil. Recomendo demais!',
            rating: 5,
        },
    ]

    return (
        <Box bg="gray.50" py={20}>
            <Container maxW="container.xl">
                <VStack spacing={12}>
                    <VStack spacing={4} textAlign="center">
                        <Heading size="2xl" color="gray.800">
                            Quem Já Encontrou Seu Carro
                        </Heading>
                        <Text fontSize="xl" color="gray.600" maxW="2xl">
                            Histórias reais de quem comprou com segurança e agilidade através do FacilIAuto.
                        </Text>
                    </VStack>

                    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} w="full">
                        {testimonials.map((testimonial, index) => (
                            <Box
                                key={index}
                                bg="white"
                                p={8}
                                borderRadius="2xl"
                                boxShadow="md"
                                position="relative"
                                _hover={{
                                    transform: 'translateY(-4px)',
                                    boxShadow: 'xl',
                                }}
                                transition="all 0.3s"
                            >
                                <Icon
                                    as={FaQuoteLeft}
                                    color="brand.100"
                                    w={12}
                                    h={12}
                                    position="absolute"
                                    top={6}
                                    right={6}
                                />
                                <VStack align="flex-start" spacing={6}>
                                    <HStack spacing={4}>
                                        <Avatar src={testimonial.image} name={testimonial.name} size="lg" />
                                        <VStack align="flex-start" spacing={0}>
                                            <Text fontWeight="bold" fontSize="lg" color="gray.800">
                                                {testimonial.name}
                                            </Text>
                                            <Text fontSize="sm" color="brand.600" fontWeight="medium">
                                                {testimonial.role}
                                            </Text>
                                        </VStack>
                                    </HStack>

                                    <HStack spacing={1}>
                                        {[...Array(testimonial.rating)].map((_, i) => (
                                            <Icon key={i} as={FaStar} color="yellow.400" w={4} h={4} />
                                        ))}
                                    </HStack>

                                    <Text color="gray.600" lineHeight="1.7" fontStyle="italic">
                                        "{testimonial.content}"
                                    </Text>
                                </VStack>
                            </Box>
                        ))}
                    </SimpleGrid>
                </VStack>
            </Container>
        </Box>
    )
}
