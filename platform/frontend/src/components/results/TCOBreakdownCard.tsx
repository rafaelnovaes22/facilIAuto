// 🎨 UX + 💰 Financial: TCO Breakdown Component
import { useState } from 'react'
import {
    Box,
    VStack,
    HStack,
    Text,
    Badge,
    Icon,
    Collapse,
    Button,
    Progress,
    Divider,
    SimpleGrid,
} from '@chakra-ui/react'
import {
    FaChevronDown,
    FaChevronUp,
    FaUniversity,
    FaGasPump,
    FaTools,
    FaShieldAlt,
    FaFileInvoice,
    FaCheckCircle,
    FaExclamationTriangle,
    FaCircle,
    FaInfoCircle,
} from 'react-icons/fa'
import type { TCOBreakdown } from '@/types'
import { formatCurrency } from '@/services/api'

interface TCOBreakdownCardProps {
    tco: TCOBreakdown
    fits_budget?: boolean | null
    budget_percentage?: number | null
    financial_health?: {
        status: 'healthy' | 'caution' | 'high_commitment'
        percentage: number
        color: 'green' | 'yellow' | 'red'
        message: string
    } | null
    car_mileage?: number
}

export const TCOBreakdownCard = ({ tco, fits_budget, budget_percentage, financial_health, car_mileage }: TCOBreakdownCardProps) => {
    const [isExpanded, setIsExpanded] = useState(false)

    const getBudgetColor = () => {
        if (fits_budget === undefined) return 'gray'
        return fits_budget ? 'green' : 'orange'
    }

    const getBudgetStatus = () => {
        if (fits_budget === undefined) return null
        return fits_budget ? 'Dentro do orçamento' : 'Acima do orçamento'
    }

    return (
        <Box
            bg="blue.50"
            borderRadius="lg"
            borderWidth="1px"
            borderColor="blue.200"
            overflow="hidden"
        >
            <VStack align="stretch" spacing={0}>
                {/* Header */}
                <Box p={4} bg="blue.100">
                    <HStack justify="space-between" align="center" mb={2}>
                        <HStack>
                            <Icon as={FaUniversity} color="blue.600" boxSize={5} />
                            <Text fontSize="md" fontWeight="bold" color="gray.800">
                                Custo mensal estimado
                            </Text>
                        </HStack>
                        {getBudgetStatus() && (
                            <Badge
                                colorScheme={getBudgetColor()}
                                fontSize="xs"
                                px={2}
                                py={1}
                            >
                                {fits_budget ? (
                                    <>
                                        <Icon as={FaCheckCircle} mr={1} />
                                        {getBudgetStatus()}
                                    </>
                                ) : (
                                    <>
                                        <Icon as={FaExclamationTriangle} mr={1} />
                                        {getBudgetStatus()}
                                    </>
                                )}
                            </Badge>
                        )}
                    </HStack>

                    <Text fontSize="2xl" fontWeight="bold" color="blue.700">
                        {formatCurrency(tco.total_monthly)}/mês
                    </Text>

                    {/* High Mileage Badge */}
                    {car_mileage && car_mileage > 100000 && (
                        <Badge colorScheme="orange" fontSize="xs" mt={2}>
                            <Icon as={FaExclamationTriangle} mr={1} />
                            Quilometragem alta ({(car_mileage / 1000).toFixed(0)}k km)
                        </Badge>
                    )}

                    {/* Financial Health Indicator */}
                    {financial_health && (
                        <HStack mt={2} spacing={2}>
                            <Icon
                                as={FaCircle}
                                color={`${financial_health.color}.500`}
                                boxSize={3}
                            />
                            <Text fontSize="sm" fontWeight="semibold" color="gray.700">
                                {financial_health.percentage.toFixed(0)}% da renda
                            </Text>
                            <Badge colorScheme={financial_health.color} fontSize="xs">
                                {financial_health.message}
                            </Badge>
                        </HStack>
                    )}
                </Box>



                {/* Expandable Breakdown */}
                <Box>
                    <Button
                        variant="ghost"
                        width="full"
                        onClick={() => setIsExpanded(!isExpanded)}
                        rightIcon={isExpanded ? <FaChevronUp /> : <FaChevronDown />}
                        size="sm"
                        colorScheme="blue"
                        borderRadius={0}
                    >
                        {isExpanded ? 'Ocultar detalhes' : 'Ver detalhamento'}
                    </Button>

                    <Collapse in={isExpanded} animateOpacity>
                        <VStack align="stretch" spacing={3} p={4} bg="white">
                            {/* Financing */}
                            <TCOItem
                                icon={FaUniversity}
                                label="Parcela do financiamento"
                                amount={tco.financing_monthly}
                                hint={`${tco.assumptions.financing_months}x com ${tco.assumptions.down_payment_percent.toFixed(0)}% de entrada`}
                            />

                            <Divider />

                            {/* Fuel */}
                            <TCOItem
                                icon={FaGasPump}
                                label="Combustível (gasolina)"
                                amount={tco.fuel_monthly}
                                hint={`${tco.assumptions.monthly_km} km/mês, R$ ${tco.assumptions.fuel_price_per_liter.toFixed(2)}/L gasolina`}
                            />

                            <Divider />

                            {/* Maintenance */}
                            <TCOItem
                                icon={FaTools}
                                label="Manutenção"
                                amount={tco.maintenance_monthly}
                                hint="Média anual estimada"
                            />

                            <Divider />

                            {/* Insurance */}
                            <TCOItem
                                icon={FaShieldAlt}
                                label="Seguro"
                                amount={tco.insurance_monthly}
                                hint="Estimativa anual"
                            />

                            <Divider />

                            {/* IPVA */}
                            <TCOItem
                                icon={FaFileInvoice}
                                label="IPVA"
                                amount={tco.ipva_monthly}
                                hint={`Estado: ${tco.assumptions.state}`}
                            />

                            <Divider />

                            {/* Total */}
                            <HStack justify="space-between" pt={2}>
                                <Text fontSize="md" fontWeight="bold" color="gray.800">
                                    Total mensal
                                </Text>
                                <Text fontSize="lg" fontWeight="bold" color="blue.700">
                                    {formatCurrency(tco.total_monthly)}
                                </Text>
                            </HStack>

                            {/* Transparent Assumptions Display */}
                            <Box bg="blue.50" p={3} borderRadius="md" mt={2}>
                                <HStack mb={2}>
                                    <Icon as={FaInfoCircle} color="blue.600" boxSize={4} />
                                    <Text fontSize="xs" fontWeight="bold" color="blue.800">
                                        Premissas do cálculo:
                                    </Text>
                                </HStack>
                                <VStack align="stretch" spacing={1} fontSize="xs">
                                    {tco.assumptions.fuel_efficiency && (
                                        <HStack justify="space-between">
                                            <Text color="gray.600">Consumo estimado:</Text>
                                            <Text fontWeight="semibold" color="gray.800">
                                                {tco.assumptions.fuel_efficiency.toFixed(1)} km/L
                                            </Text>
                                        </HStack>
                                    )}
                                    <HStack justify="space-between">
                                        <Text color="gray.600">Km por mês:</Text>
                                        <Text fontWeight="semibold" color="gray.800">
                                            {tco.assumptions.monthly_km} km
                                        </Text>
                                    </HStack>
                                    <HStack justify="space-between">
                                        <Text color="gray.600">Preço combustível:</Text>
                                        <Text fontWeight="semibold" color="gray.800">
                                            R$ {tco.assumptions.fuel_price_per_liter.toFixed(2)}/L
                                        </Text>
                                    </HStack>
                                    <HStack justify="space-between">
                                        <Text color="gray.600">Entrada:</Text>
                                        <Text fontWeight="semibold" color="gray.800">
                                            {tco.assumptions.down_payment_percent.toFixed(0)}%
                                        </Text>
                                    </HStack>
                                    <HStack justify="space-between">
                                        <Text color="gray.600">Prazo:</Text>
                                        <Text fontWeight="semibold" color="gray.800">
                                            {tco.assumptions.financing_months}x
                                        </Text>
                                    </HStack>
                                    {tco.assumptions.annual_interest_rate && (
                                        <HStack justify="space-between">
                                            <Text color="gray.600">Taxa de juros:</Text>
                                            <Text fontWeight="semibold" color="gray.800">
                                                {tco.assumptions.annual_interest_rate.toFixed(1)}% a.a.
                                            </Text>
                                        </HStack>
                                    )}
                                    {tco.assumptions.maintenance_adjustment && (
                                        <HStack justify="space-between">
                                            <Text color="gray.600">Ajuste manutenção:</Text>
                                            <Text fontWeight="semibold" color="orange.600">
                                                +{((tco.assumptions.maintenance_adjustment.factor - 1) * 100).toFixed(0)}% ({tco.assumptions.maintenance_adjustment.reason})
                                            </Text>
                                        </HStack>
                                    )}
                                </VStack>
                            </Box>

                            {/* Disclaimer */}
                            <Box bg="gray.50" p={3} borderRadius="md" mt={2}>
                                <Text fontSize="xs" color="gray.600">
                                    💡 <strong>Valores estimados</strong> baseados em médias de mercado.
                                    Os custos reais podem variar conforme perfil do condutor, região e uso do veículo.
                                </Text>
                            </Box>
                        </VStack>
                    </Collapse>
                </Box>
            </VStack>
        </Box>
    )
}

interface TCOItemProps {
    icon: any
    label: string
    amount: number
    hint: string
}

const TCOItem = ({ icon, label, amount, hint }: TCOItemProps) => {
    return (
        <HStack justify="space-between" align="flex-start">
            <HStack align="flex-start" flex={1}>
                <Icon as={icon} color="blue.500" boxSize={4} mt={1} />
                <VStack align="flex-start" spacing={0}>
                    <Text fontSize="sm" fontWeight="medium" color="gray.700">
                        {label}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                        {hint}
                    </Text>
                </VStack>
            </HStack>
            <Text fontSize="md" fontWeight="semibold" color="gray.800">
                {formatCurrency(amount)}
            </Text>
        </HStack>
    )
}
