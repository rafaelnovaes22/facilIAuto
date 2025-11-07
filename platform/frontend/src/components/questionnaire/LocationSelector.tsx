// 🎨 UX Especialist: Location selector with state dropdown and dynamic city selector
import {
    VStack,
    HStack,
    FormControl,
    FormLabel,
    Select,
    Text,
    Box,
    Icon,
} from '@chakra-ui/react'
import { FaMapMarkerAlt } from 'react-icons/fa'
import { ESTADOS_BR } from '@/types'
import { getCitiesByState, hasCities } from '@/data/cities'
import { useState, useEffect } from 'react'

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
    const [availableCities, setAvailableCities] = useState<string[]>([])

    // Atualiza lista de cidades quando estado muda
    useEffect(() => {
        if (state) {
            const cities = getCitiesByState(state)
            setAvailableCities(cities)

            // Se a cidade atual não está na lista do novo estado, limpa
            if (city && !cities.includes(city)) {
                onChange({ city: undefined, state })
            }
        } else {
            setAvailableCities([])
        }
    }, [state])

    const handleStateChange = (newState: string) => {
        // Limpa a cidade ao trocar de estado
        onChange({ city: undefined, state: newState || undefined })
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
            <VStack spacing={4} w="full">
                {/* Estado */}
                <FormControl>
                    <FormLabel fontSize="sm" color="gray.700">
                        Estado
                    </FormLabel>
                    <Select
                        placeholder="Selecione o estado"
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

                {/* Cidade - Aparece apenas quando estado está selecionado */}
                {state && hasCities(state) && (
                    <FormControl>
                        <FormLabel fontSize="sm" color="gray.700">
                            Cidade (opcional)
                        </FormLabel>
                        <Select
                            placeholder="Todo o estado"
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
                        >
                            {availableCities.map((cidade) => (
                                <option key={cidade} value={cidade}>
                                    {cidade}
                                </option>
                            ))}
                        </Select>
                        <Text fontSize="xs" color="gray.500" mt={2}>
                            Deixe em "Todo o estado" para buscar em todas as cidades
                        </Text>
                    </FormControl>
                )}
            </VStack>

            {/* Info Box */}
            {state && (
                <Box
                    bg="green.50"
                    p={3}
                    borderRadius="md"
                    borderWidth="1px"
                    borderColor="green.200"
                >
                    <Text fontSize="sm" color="green.800">
                        {city
                            ? `✓ Vamos priorizar concessionárias em ${city} - ${state}`
                            : `✓ Vamos buscar concessionárias em todo o estado de ${state}`
                        }
                    </Text>
                </Box>
            )}
        </VStack>
    )
}
