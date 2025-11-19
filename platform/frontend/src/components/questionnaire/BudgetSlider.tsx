// 🎨 UX Especialist: Dual-handle range slider for budget selection with mobile-friendly input
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
    Input,
    InputGroup,
    InputLeftAddon,
    useBreakpointValue,
} from '@chakra-ui/react'
import { formatCurrency } from '@/services/api'
import { useState } from 'react'

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
    // Local state for input values (formatted)
    const [minInput, setMinInput] = useState(minValue.toString())
    const [maxInput, setMaxInput] = useState(maxValue.toString())

    // Detect mobile for better UX
    const isMobile = useBreakpointValue({ base: true, md: false })

    const handleSliderChange = (values: number[]) => {
        onChange(values[0], values[1])
        setMinInput(values[0].toString())
        setMaxInput(values[1].toString())
    }

    const parseInputValue = (value: string): number => {
        // Remove non-numeric characters
        const numericValue = value.replace(/\D/g, '')
        return numericValue ? parseInt(numericValue, 10) : 0
    }

    const handleMinInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value
        setMinInput(value)

        const numericValue = parseInputValue(value)
        if (numericValue >= minLimit && numericValue < maxValue) {
            onChange(numericValue, maxValue)
        }
    }

    const handleMaxInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value
        setMaxInput(value)

        const numericValue = parseInputValue(value)
        if (numericValue <= maxLimit && numericValue > minValue) {
            onChange(minValue, numericValue)
        }
    }

    const handleMinInputBlur = () => {
        const numericValue = parseInputValue(minInput)
        if (numericValue < minLimit || numericValue >= maxValue) {
            setMinInput(minValue.toString())
        } else {
            onChange(numericValue, maxValue)
        }
    }

    const handleMaxInputBlur = () => {
        const numericValue = parseInputValue(maxInput)
        if (numericValue > maxLimit || numericValue <= minValue) {
            setMaxInput(maxValue.toString())
        } else {
            onChange(minValue, numericValue)
        }
    }

    return (
        <FormControl>
            <FormLabel fontSize="md" fontWeight="semibold" color="gray.700">
                💰 Faixa de Orçamento
            </FormLabel>

            <VStack spacing={6} align="stretch">
                {/* Input Fields - Mobile First */}
                <VStack spacing={3} align="stretch">
                    <InputGroup size="lg">
                        <InputLeftAddon bg="gray.100" color="gray.600" fontWeight="medium">
                            Mínimo
                        </InputLeftAddon>
                        <Input
                            type="tel"
                            inputMode="numeric"
                            pattern="[0-9]*"
                            value={minInput}
                            onChange={handleMinInputChange}
                            onBlur={handleMinInputBlur}
                            placeholder="Ex: 50000"
                            fontSize="lg"
                            fontWeight="semibold"
                            color="brand.600"
                            _focus={{
                                borderColor: 'brand.500',
                                boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
                            }}
                        />
                    </InputGroup>

                    <InputGroup size="lg">
                        <InputLeftAddon bg="gray.100" color="gray.600" fontWeight="medium">
                            Máximo
                        </InputLeftAddon>
                        <Input
                            type="tel"
                            inputMode="numeric"
                            pattern="[0-9]*"
                            value={maxInput}
                            onChange={handleMaxInputChange}
                            onBlur={handleMaxInputBlur}
                            placeholder="Ex: 100000"
                            fontSize="lg"
                            fontWeight="semibold"
                            color="brand.600"
                            _focus={{
                                borderColor: 'brand.500',
                                boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
                            }}
                        />
                    </InputGroup>
                </VStack>

                {/* Display Formatted Values */}
                <HStack justify="space-between" px={2}>
                    <VStack align="flex-start" spacing={0}>
                        <Text fontSize="xs" color="gray.500" fontWeight="medium">
                            De
                        </Text>
                        <Text fontSize="lg" fontWeight="bold" color="brand.600">
                            {formatCurrency(minValue)}
                        </Text>
                    </VStack>

                    <Text fontSize="md" color="gray.400" fontWeight="bold">
                        até
                    </Text>

                    <VStack align="flex-end" spacing={0}>
                        <Text fontSize="xs" color="gray.500" fontWeight="medium">
                            Até
                        </Text>
                        <Text fontSize="lg" fontWeight="bold" color="brand.600">
                            {formatCurrency(maxValue)}
                        </Text>
                    </VStack>
                </HStack>

                {/* Range Slider - Optional visual aid */}
                {!isMobile && (
                    <Box px={2} py={4}>
                        <RangeSlider
                            value={[minValue, maxValue]}
                            min={minLimit}
                            max={maxLimit}
                            step={step}
                            onChange={handleSliderChange}
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
                                borderColor="secondary.500"
                                _focus={{
                                    boxShadow: '0 0 0 3px rgba(34, 197, 94, 0.3)',
                                }}
                                _active={{
                                    transform: 'scale(1.1)',
                                }}
                                borderRadius="full"
                            >
                                <Box
                                    w="12px"
                                    h="12px"
                                    bg="secondary.500"
                                    borderRadius="full"
                                />
                            </RangeSliderThumb>
                            <RangeSliderThumb
                                index={1}
                                boxSize="44px"
                                bg="white"
                                borderWidth="3px"
                                borderColor="secondary.500"
                                _focus={{
                                    boxShadow: '0 0 0 3px rgba(34, 197, 94, 0.3)',
                                }}
                                _active={{
                                    transform: 'scale(1.1)',
                                }}
                                borderRadius="full"
                            >
                                <Box
                                    w="12px"
                                    h="12px"
                                    bg="secondary.500"
                                    borderRadius="full"
                                />
                            </RangeSliderThumb>
                        </RangeSlider>
                    </Box>
                )}

                {/* Helper Text */}
                <FormHelperText fontSize="sm" color="gray.600" textAlign="center">
                    {isMobile
                        ? 'Digite os valores diretamente nos campos acima'
                        : 'Digite os valores ou arraste os controles para ajustar'
                    }
                </FormHelperText>

                {/* Summary Box */}
                <Box
                    bg="secondary.50"
                    p={4}
                    borderRadius="xl"
                    borderWidth="2px"
                    borderColor="secondary.200"
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
