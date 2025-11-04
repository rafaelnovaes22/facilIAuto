// 🎨 UX: Seletor de faixa de anos do carro
import {
    VStack,
    FormControl,
    FormLabel,
    Select,
    Text,
    HStack,
    Icon,
    SimpleGrid,
} from '@chakra-ui/react'
import { FiCalendar } from 'react-icons/fi'

interface YearSelectorProps {
    minValue?: number
    maxValue?: number
    onChange: (min?: number, max?: number) => void
}

export const YearSelector = ({ minValue, maxValue, onChange }: YearSelectorProps) => {
    const currentYear = new Date().getFullYear()
    const years = Array.from({ length: 25 }, (_, i) => currentYear - i) // Últimos 25 anos

    const handleMinChange = (min?: number) => {
        // Se min > max, ajustar max
        if (min && maxValue && min > maxValue) {
            onChange(min, min)
        } else {
            onChange(min, maxValue)
        }
    }

    const handleMaxChange = (max?: number) => {
        // Se max < min, ajustar min
        if (max && minValue && max < minValue) {
            onChange(max, max)
        } else {
            onChange(minValue, max)
        }
    }

    const getYearRangeText = () => {
        if (minValue && maxValue) {
            return `Carros de ${minValue} a ${maxValue}`
        } else if (minValue) {
            return `Carros de ${minValue} em diante`
        } else if (maxValue) {
            return `Carros até ${maxValue}`
        }
        return 'Sem restrição de ano'
    }

    return (
        <VStack spacing={4} align="stretch">
            <HStack spacing={2}>
                <Icon as={FiCalendar} color="blue.500" boxSize={5} />
                <FormLabel mb={0} fontWeight="semibold" color="gray.700">
                    Ano do carro
                </FormLabel>
            </HStack>

            <SimpleGrid columns={2} spacing={4}>
                {/* Ano Mínimo */}
                <FormControl>
                    <FormLabel fontSize="sm" color="gray.600" mb={2}>
                        De (mínimo)
                    </FormLabel>
                    <Select
                        value={minValue || ''}
                        onChange={(e) => {
                            const year = e.target.value ? parseInt(e.target.value) : undefined
                            handleMinChange(year)
                        }}
                        placeholder="Qualquer"
                        size="lg"
                        bg="white"
                        borderColor="gray.300"
                        _hover={{ borderColor: 'blue.400' }}
                        _focus={{ borderColor: 'blue.500', boxShadow: '0 0 0 1px #3182ce' }}
                    >
                        {years.map((year) => (
                            <option key={year} value={year}>
                                {year}
                            </option>
                        ))}
                    </Select>
                </FormControl>

                {/* Ano Máximo */}
                <FormControl>
                    <FormLabel fontSize="sm" color="gray.600" mb={2}>
                        Até (máximo)
                    </FormLabel>
                    <Select
                        value={maxValue || ''}
                        onChange={(e) => {
                            const year = e.target.value ? parseInt(e.target.value) : undefined
                            handleMaxChange(year)
                        }}
                        placeholder="Qualquer"
                        size="lg"
                        bg="white"
                        borderColor="gray.300"
                        _hover={{ borderColor: 'blue.400' }}
                        _focus={{ borderColor: 'blue.500', boxShadow: '0 0 0 1px #3182ce' }}
                    >
                        {years.map((year) => (
                            <option key={year} value={year}>
                                {year}
                            </option>
                        ))}
                    </Select>
                </FormControl>
            </SimpleGrid>

            <Text fontSize="sm" color="gray.600" textAlign="center">
                {getYearRangeText()}
            </Text>
        </VStack>
    )
}
