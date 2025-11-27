import { Box, Container, SimpleGrid, Image, Text, VStack } from '@chakra-ui/react'

export default function PartnerLogos() {
    // Placeholder logos - in a real app these would be actual partner logos
    const partners = [
        { name: 'AutoPremium', logo: 'https://placehold.co/150x50/e2e8f0/4a5568?text=AutoPremium' },
        { name: 'CarMax', logo: 'https://placehold.co/150x50/e2e8f0/4a5568?text=CarMax' },
        { name: 'SeminovosBR', logo: 'https://placehold.co/150x50/e2e8f0/4a5568?text=SeminovosBR' },
        { name: 'Localiza', logo: 'https://placehold.co/150x50/e2e8f0/4a5568?text=Localiza' },
        { name: 'Movida', logo: 'https://placehold.co/150x50/e2e8f0/4a5568?text=Movida' },
    ]

    return (
        <Box bg="gray.50" py={8} borderBottom="1px" borderColor="gray.100">
            <Container maxW="container.xl">
                <VStack spacing={4}>
                    <Text fontSize="sm" color="gray.500" fontWeight="medium" textTransform="uppercase" letterSpacing="wider">
                        Concessionárias Parceiras Verificadas
                    </Text>
                    <SimpleGrid
                        columns={{ base: 2, md: 5 }}
                        spacing={8}
                        w="full"
                        alignItems="center"
                        justifyItems="center"
                    >
                        {partners.map((partner) => (
                            <Image
                                key={partner.name}
                                src={partner.logo}
                                alt={partner.name}
                                filter="grayscale(100%)"
                                opacity={0.6}
                                _hover={{
                                    filter: 'grayscale(0%)',
                                    opacity: 1,
                                }}
                                transition="all 0.3s"
                                maxH="40px"
                                objectFit="contain"
                            />
                        ))}
                    </SimpleGrid>
                </VStack>
            </Container>
        </Box>
    )
}
