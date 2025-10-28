// 🎨 UX Especialist: Profile summary component
import {
    Box,
    Heading,
    Text,
    SimpleGrid,
    VStack,
    HStack,
    Badge,
    Button,
    Icon,
} from '@chakra-ui/react'
import { FaEdit } from 'react-icons/fa'
import type { RecommendationResponse } from '@/types'

interface ProfileSummaryProps {
    profileSummary: RecommendationResponse['profile_summary']
    onEdit?: () => void
}

export const ProfileSummary = ({ profileSummary, onEdit }: ProfileSummaryProps) => {
    return (
        <Box bg="white" p={6} borderRadius="xl" boxShadow="sm">
            <HStack justify="space-between" mb={4}>
                <Heading size="sm" color="gray.700">
                    📋 Resumo do Perfil
                </Heading>
                {onEdit && (
                    <Button
                        size="sm"
                        variant="ghost"
                        colorScheme="brand"
                        leftIcon={<Icon as={FaEdit} />}
                        onClick={onEdit}
                    >
                        Editar
                    </Button>
                )}
            </HStack>

            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                <VStack align="flex-start" spacing={1}>
                    <Text fontSize="xs" color="gray.600" fontWeight="semibold">
                        💰 Orçamento
                    </Text>
                    <Text fontSize="sm" color="gray.800" fontWeight="medium">
                        {profileSummary.budget_range}
                    </Text>
                </VStack>

                <VStack align="flex-start" spacing={1}>
                    <Text fontSize="xs" color="gray.600" fontWeight="semibold">
                        🚗 Uso Principal
                    </Text>
                    <Text fontSize="sm" color="gray.800" fontWeight="medium">
                        {profileSummary.usage}
                    </Text>
                </VStack>

                <VStack align="flex-start" spacing={1}>
                    <Text fontSize="xs" color="gray.600" fontWeight="semibold">
                        📍 Localização
                    </Text>
                    <Text fontSize="sm" color="gray.800" fontWeight="medium">
                        {profileSummary.location || 'Não especificada'}
                    </Text>
                </VStack>
            </SimpleGrid>

            {/* Top Priorities */}
            {profileSummary.top_priorities && profileSummary.top_priorities.length > 0 && (
                <Box mt={4} pt={4} borderTopWidth="1px" borderColor="gray.100">
                    <Text fontSize="xs" color="gray.600" fontWeight="semibold" mb={2}>
                        🎯 Suas prioridades principais:
                    </Text>
                    <HStack spacing={2} flexWrap="wrap">
                        {profileSummary.top_priorities.map((priority, index) => (
                            <Badge
                                key={priority}
                                colorScheme="brand"
                                fontSize="sm"
                                px={3}
                                py={1}
                                borderRadius="full"
                            >
                                {index + 1}º {priority}
                            </Badge>
                        ))}
                    </HStack>
                </Box>
            )}
        </Box>
    )
}
