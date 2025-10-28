// 🎨 UX Especialist: Location selector with state dropdown and city input
import {
    VStack,
    HStack,
    FormControl,
    FormLabel,
    Select,
    Input,
    Text,
    Box,
    Icon,
} from '@chakra-ui/react'
import { FaMapMarkerAlt } from 'react-icons/fa'
import { ESTADOS_BR } from '@/types'

interface LocationSelectorProps {
    city?: string
    state?: string
    onChange: (location: { city?: string; state?: string }) => void
}

export const LocationSelector = ({
    city,
    state,
    onChange,
}: LocationSelectorProps) => {
    const handleStateChange = (newState: string) => {
        onChange({ city, state: newState || undefined })
    }

    const handleCityChange = (newCity: string) => {
        onChange({ city: newCity || undefined, state })
    }

    return (
        <VStack spacing={4} align="stretch">
            {/* Header */}
            <HStack spacing={2} color="gray.700">
                <Icon as={FaMapMarkerAlt} boxSize={5} color="brand.500" />
                <Text fontSize="md" fontWeight="semibold">
                    Onde você está localizado?
                </Text>
            </HStack>

            <Text fontSize="sm" color="gray.600">
                Isso nos ajuda a priorizar concessionárias próximas (opcional)
            </Text>

            {/* Location Inputs */}
            <HStack spacing={4} w="full">
                {/* Estado */}
                <FormControl flex={1}>
                    <FormLabel fontSize="sm" color="gray.700">
                        Estado
                    </FormLabel>
                    <Select
                        placeholder="Selecione"
                        value={state || ''}
                        onChange={(e) => handleStateChange(e.target.value)}
                        size="lg"
                        bg="white"
                        borderColor="gray.300"
                        _hover={{ borderColor: 'brand.400' }}
                        _focus={{
                            borderColor: 'brand.500',
                            boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
                        }}
                    >
                        {ESTADOS_BR.map((estado) => (
                            <option key={estado} value={estado}>
                                {estado}
                            </option>
                        ))}
                    </Select>
                </FormControl>

                {/* Cidade */}
                <FormControl flex={2}>
                    <FormLabel fontSize="sm" color="gray.700">
                        Cidade
                    </FormLabel>
                    <Input
                        placeholder="Ex: São Paulo"
                        value={city || ''}
                        onChange={(e) => handleCityChange(e.target.value)}
                        size="lg"
                        bg="white"
                        borderColor="gray.300"
                        _hover={{ borderColor: 'brand.400' }}
                        _focus={{
                            borderColor: 'brand.500',
                            boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
                        }}
                    />
                </FormControl>
            </HStack>

            {/* Info Box */}
            {(city || state) && (
                <Box
                    bg="green.50"
                    p={3}
                    borderRadius="md"
                    borderWidth="1px"
                    borderColor="green.200"
                >
                    <Text fontSize="sm" color="green.800">
                        ✓ Vamos priorizar concessionárias próximas a você
                    </Text>
                </Box>
            )}
        </VStack>
    )
}
