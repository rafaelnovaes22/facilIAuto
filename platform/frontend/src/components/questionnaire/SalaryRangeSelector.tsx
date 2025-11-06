// 🎨 UX: Seletor de faixa salarial com cálculo de TCO máximo
import {
    VStack,
    HStack,
    FormControl,
    FormLabel,
    RadioGroup,
    Radio,
    Text,
    Box,
    Icon,
    Tooltip,
    Stack,
} from '@chakra-ui/react'
import { FiDollarSign, FiInfo } from 'react-icons/fi'

interface SalaryRangeSelectorProps {
    value: string | null
    onChange: (range: string | null) => void
}

interface SalaryRange {
    value: string
    label: string
    avgIncome: number
    maxTco: number
}

const SALARY_RANGES: SalaryRange[] = [
    { value: '0-3000', label: 'Até R$ 3.000', avgIncome: 1500, maxTco: 450 },
    { value: '3000-5000', label: 'R$ 3.000 - R$ 5.000', avgIncome: 4000, maxTco: 1200 },
    { value: '5000-8000', label: 'R$ 5.000 - R$ 8.000', avgIncome: 6500, maxTco: 1950 },
    { value: '8000-12000', label: 'R$ 8.000 - R$ 12.000', avgIncome: 10000, maxTco: 3000 },
    { value: '12000+', label: 'Acima de R$ 12.000', avgIncome: 14000, maxTco: 4200 },
]

export const SalaryRangeSelector = ({ value, onChange }: SalaryRangeSelectorProps) => {
    const selectedRange = SALARY_RANGES.find((range) => range.value === value)

    const handleChange = (newValue: string) => {
        if (newValue === 'skip') {
            onChange(null)
        } else {
            onChange(newValue)
        }
    }

    return (
        <VStack spacing={4} align="stretch">
            {/* Header */}
            <HStack spacing={2}>
                <Icon as={FiDollarSign} color="blue.500" boxSize={5} />
                <FormLabel mb={0} fontWeight="semibold" color="gray.700">
                    Qual sua faixa de renda mensal?
                </FormLabel>
                <Tooltip
                    label="Usamos essa informação para recomendar carros que cabem no seu orçamento mensal (30% da renda). Seus dados são privados e não são armazenados."
                    fontSize="sm"
                    placement="top"
                    hasArrow
                >
                    <Box as="span" cursor="help">
                        <Icon as={FiInfo} color="gray.400" boxSize={4} />
                    </Box>
                </Tooltip>
            </HStack>

            <Text fontSize="sm" color="gray.600">
                Isso nos ajuda a mostrar se o custo mensal do carro cabe no seu bolso
            </Text>

            {/* Radio Group */}
            <FormControl>
                <RadioGroup
                    value={value || 'skip'}
                    onChange={handleChange}
                >
                    <Stack spacing={3}>
                        {SALARY_RANGES.map((range) => (
                            <Radio
                                key={range.value}
                                value={range.value}
                                size="lg"
                                colorScheme="blue"
                                borderColor="gray.300"
                                _hover={{ borderColor: 'blue.400' }}
                            >
                                <Text fontSize="md" color="gray.700">
                                    {range.label}
                                </Text>
                            </Radio>
                        ))}
                        <Radio
                            value="skip"
                            size="lg"
                            colorScheme="gray"
                            borderColor="gray.300"
                            _hover={{ borderColor: 'gray.400' }}
                        >
                            <Text fontSize="md" color="gray.600" fontStyle="italic">
                                Prefiro não informar
                            </Text>
                        </Radio>
                    </Stack>
                </RadioGroup>
            </FormControl>

            {/* TCO Info Box */}
            {selectedRange && (
                <Box
                    bg="blue.50"
                    p={4}
                    borderRadius="md"
                    borderWidth="1px"
                    borderColor="blue.200"
                >
                    <VStack spacing={2} align="start">
                        <HStack spacing={2}>
                            <Icon as={FiDollarSign} color="blue.600" boxSize={4} />
                            <Text fontSize="sm" fontWeight="semibold" color="blue.800">
                                Custo mensal recomendado
                            </Text>
                        </HStack>
                        <Text fontSize="lg" fontWeight="bold" color="blue.700">
                            Até R$ {selectedRange.maxTco.toFixed(0)}/mês
                        </Text>
                        <Text fontSize="xs" color="blue.600">
                            Baseado em 30% da sua renda média (R$ {selectedRange.avgIncome.toFixed(0)})
                        </Text>
                        <Text fontSize="xs" color="blue.600" fontStyle="italic">
                            Inclui: financiamento, combustível, manutenção, seguro e IPVA
                        </Text>
                    </VStack>
                </Box>
            )}

            {/* Skip Info */}
            {!value && (
                <Box
                    bg="gray.50"
                    p={3}
                    borderRadius="md"
                    borderWidth="1px"
                    borderColor="gray.200"
                >
                    <Text fontSize="sm" color="gray.600">
                        ℹ️ Sem problema! Vamos mostrar todas as opções sem filtro de orçamento mensal
                    </Text>
                </Box>
            )}
        </VStack>
    )
}
