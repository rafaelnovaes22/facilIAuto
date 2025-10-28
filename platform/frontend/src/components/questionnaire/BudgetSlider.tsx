// 🎨 UX Especialist: Dual-handle range slider for budget selection
import {
    VStack,
    HStack,
    Text,
    Box,
    RangeSlider,
    RangeSliderTrack,
    RangeSliderFilledTrack,
    RangeSliderThumb,
    FormControl,
    FormLabel,
    FormHelperText,
} from '@chakra-ui/react'
import { formatCurrency } from '@/services/api'

interface BudgetSliderProps {
    minValue: number
    maxValue: number
    onChange: (min: number, max: number) => void
    minLimit?: number
    maxLimit?: number
    step?: number
}

export const BudgetSlider = ({
    minValue,
    maxValue,
    onChange,
    minLimit = 10000,
    maxLimit = 500000,
    step = 5000,
}: BudgetSliderProps) => {
    const handleChange = (values: number[]) => {
        onChange(values[0], values[1])
    }

    return (
        <FormControl>
            <FormLabel fontSize="md" fontWeight="semibold" color="gray.700">
                💰 Faixa de Orçamento
            </FormLabel>

            <VStack spacing={6} align="stretch">
                {/* Display Values */}
                <HStack justify="space-between" px={2}>
                    <VStack align="flex-start" spacing={0}>
                        <Text fontSize="xs" color="gray.500" fontWeight="medium">
                            Mínimo
                        </Text>
                        <Text fontSize="xl" fontWeight="bold" color="brand.600">
                            {formatCurrency(minValue)}
                        </Text>
                    </VStack>

                    <Text fontSize="lg" color="gray.400" fontWeight="bold">
                        até
                    </Text>

                    <VStack align="flex-end" spacing={0}>
                        <Text fontSize="xs" color="gray.500" fontWeight="medium">
                            Máximo
                        </Text>
                        <Text fontSize="xl" fontWeight="bold" color="brand.600">
                            {formatCurrency(maxValue)}
                        </Text>
                    </VStack>
                </HStack>

                {/* Range Slider */}
                <Box px={2} py={4}>
                    <RangeSlider
                        value={[minValue, maxValue]}
                        min={minLimit}
                        max={maxLimit}
                        step={step}
                        onChange={handleChange}
                        minStepsBetweenThumbs={1}
                    >
                        <RangeSliderTrack bg="gray.200" h="8px" borderRadius="full">
                            <RangeSliderFilledTrack bg="brand.500" />
                        </RangeSliderTrack>
                        <RangeSliderThumb
                            index={0}
                            boxSize="44px"
                            bg="white"
                            borderWidth="3px"
                            borderColor="brand.500"
                            _focus={{
                                boxShadow: '0 0 0 3px rgba(14, 165, 233, 0.3)',
                            }}
                            _active={{
                                transform: 'scale(1.1)',
                            }}
                        >
                            <Box
                                w="12px"
                                h="12px"
                                bg="brand.500"
                                borderRadius="full"
                            />
                        </RangeSliderThumb>
                        <RangeSliderThumb
                            index={1}
                            boxSize="44px"
                            bg="white"
                            borderWidth="3px"
                            borderColor="brand.500"
                            _focus={{
                                boxShadow: '0 0 0 3px rgba(14, 165, 233, 0.3)',
                            }}
                            _active={{
                                transform: 'scale(1.1)',
                            }}
                        >
                            <Box
                                w="12px"
                                h="12px"
                                bg="brand.500"
                                borderRadius="full"
                            />
                        </RangeSliderThumb>
                    </RangeSlider>
                </Box>

                {/* Helper Text */}
                <FormHelperText fontSize="sm" color="gray.600" textAlign="center">
                    Arraste os controles para ajustar sua faixa de orçamento
                </FormHelperText>

                {/* Summary Box */}
                <Box
                    bg="brand.50"
                    p={4}
                    borderRadius="lg"
                    borderWidth="2px"
                    borderColor="brand.200"
                >
                    <Text fontSize="sm" color="gray.600" mb={1}>
                        Você está buscando carros entre:
                    </Text>
                    <Text fontSize="lg" fontWeight="bold" color="brand.700">
                        {formatCurrency(minValue)} e {formatCurrency(maxValue)}
                    </Text>
                </Box>
            </VStack>
        </FormControl>
    )
}
