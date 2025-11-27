import { Box, Container, Heading, SimpleGrid, Text, Image, Badge, Button, VStack, HStack, Icon } from '@chakra-ui/react'
import { FaGasPump, FaTachometerAlt, FaCalendarAlt, FaWhatsapp } from 'react-icons/fa'
import nivusImage from '@/assets/nivus.png'
import jeepCompassImage from '@/assets/jeep-compass.png'

export default function CarHighlights() {
    // Mock data for highlights
    const highlights = [
        {
            id: 1,
            name: 'Jeep Compass Longitude',
            price: 'R$ 145.900',
            year: '2022/2023',
            km: '15.000 km',
            fuel: 'Flex',
            image: jeepCompassImage,
            badge: 'Revisado',
        },
        {
            id: 2,
            name: 'Toyota Corolla XEi',
            price: 'R$ 129.900',
            year: '2021/2022',
            km: '28.000 km',
            fuel: 'Híbrido',
            image: 'https://images.unsplash.com/photo-1623869675781-80aa31012a5a?q=80&w=600&auto=format&fit=crop',
            badge: 'Garantia de Fábrica',
        },
        {
            id: 3,
            name: 'Volkswagen Nivus Highline',
            price: 'R$ 115.900',
            year: '2021/2021',
            km: '32.000 km',
            fuel: 'Flex',
            image: nivusImage,
            badge: 'Único Dono',
        },
    ]

    return (
        <Box bg="white" py={20}>
            <Container maxW="container.xl">
                <VStack spacing={12}>
                    <VStack spacing={4} textAlign="center">
                        <Badge colorScheme="brand" px={3} py={1} borderRadius="full">
                            Destaques da Semana
                        </Badge>
                        <Heading size="2xl" color="gray.800">
                            Carros Selecionados para Você
                        </Heading>
                        <Text fontSize="xl" color="gray.600" maxW="2xl">
                            Confira algumas das melhores oportunidades que nossa IA encontrou hoje.
                        </Text>
                    </VStack>

                    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} w="full">
                        {highlights.map((car) => (
                            <Box
                                key={car.id}
                                bg="white"
                                borderRadius="2xl"
                                overflow="hidden"
                                boxShadow="lg"
                                border="1px"
                                borderColor="gray.100"
                                _hover={{
                                    transform: 'translateY(-8px)',
                                    boxShadow: '2xl',
                                }}
                                transition="all 0.3s"
                            >
                                <Box position="relative" h="240px">
                                    <Image
                                        src={car.image}
                                        alt={car.name}
                                        w="full"
                                        h="full"
                                        objectFit="cover"
                                    />
                                    <Badge
                                        position="absolute"
                                        top={4}
                                        right={4}
                                        colorScheme="green"
                                        fontSize="sm"
                                        px={3}
                                        py={1}
                                        borderRadius="full"
                                        boxShadow="md"
                                    >
                                        {car.badge}
                                    </Badge>
                                </Box>

                                <VStack p={6} align="flex-start" spacing={4}>
                                    <VStack align="flex-start" spacing={1}>
                                        <Heading size="md" color="gray.800">
                                            {car.name}
                                        </Heading>
                                        <Text fontSize="2xl" fontWeight="bold" color="brand.600">
                                            {car.price}
                                        </Text>
                                    </VStack>

                                    <HStack spacing={4} color="gray.600" fontSize="sm">
                                        <HStack>
                                            <Icon as={FaCalendarAlt} color="brand.500" />
                                            <Text>{car.year}</Text>
                                        </HStack>
                                        <HStack>
                                            <Icon as={FaTachometerAlt} color="brand.500" />
                                            <Text>{car.km}</Text>
                                        </HStack>
                                        <HStack>
                                            <Icon as={FaGasPump} color="brand.500" />
                                            <Text>{car.fuel}</Text>
                                        </HStack>
                                    </HStack>

                                    <Button
                                        w="full"
                                        colorScheme="green"
                                        leftIcon={<FaWhatsapp />}
                                        variant="outline"
                                        _hover={{
                                            bg: 'green.50',
                                        }}
                                    >
                                        Tenho Interesse
                                    </Button>
                                </VStack>
                            </Box>
                        ))}
                    </SimpleGrid>
                </VStack>
            </Container>
        </Box>
    )
}
