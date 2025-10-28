// 🎨 UX Especialist: Priority slider with 1-5 scale and visual highlighting
import {
    VStack,
    HStack,
    FormControl,
    FormLabel,
    Slider,
    SliderTrack,
    SliderFilledTrack,
    SliderThumb,
    Text,
    Badge,
    Tooltip,
    Box,
} from '@chakra-ui/react'

interface PrioritySliderProps {
    label: string
    icon: string
    description: string
    tooltip?: string
    value: number
    onChange: (value: number) => void
    isTopPriority?: boolean
}

const PRIORITY_LABELS = {
    1: 'Baixa',
    2: 'Média-Baixa',
    3: 'Média',
    4: 'Alta',
    5: 'Muito Alta',
}

const PRIORITY_COLORS = {
    1: 'gray',
    2: 'blue',
    3: 'cyan',
    4: 'green',
    5: 'brand',
}

export const PrioritySlider = ({
    label,
    icon,
    description,
    tooltip,
    value,
    onChange,
    isTopPriority = false,
}: PrioritySliderProps) => {
    return (
        <FormControl
            p={4}
            borderRadius="lg"
            bg={isTopPriority ? 'brand.50' : 'white'}
            borderWidth="2px"
            borderColor={isTopPriority ? 'brand.300' : 'gray.100'}
            transition="all 0.2s"
        >
            <VStack spacing={3} align="stretch">
                {/* Header */}
                <HStack justify="space-between" align="flex-start">
                    <VStack align="flex-start" spacing={1} flex={1}>
                        <HStack spacing={2}>
                            <Text fontSize="lg">{icon}</Text>
                            <FormLabel mb={0} fontSize="md" fontWeight="bold" color="gray.800">
                                {label}
                            </FormLabel>
                            {isTopPriority && (
                                <Badge colorScheme="brand" fontSize="xs">
                                    Top 3
                                </Badge>
                            )}
                        </HStack>
                        <Tooltip label={tooltip} placement="top" hasArrow isDisabled={!tooltip}>
                            <Text fontSize="sm" color="gray.600" cursor={tooltip ? 'help' : 'default'}>
                                {description}
                            </Text>
                        </Tooltip>
                    </VStack>

                    {/* Current Value Badge */}
                    <Badge
                        colorScheme={PRIORITY_COLORS[value as keyof typeof PRIORITY_COLORS]}
                        fontSize="sm"
                        px={3}
                        py={1}
                        borderRadius="full"
                    >
                        {PRIORITY_LABELS[value as keyof typeof PRIORITY_LABELS]}
                    </Badge>
                </HStack>

                {/* Slider */}
                <Box px={2}>
                    <Slider
                        value={value}
                        onChange={onChange}
                        min={1}
                        max={5}
                        step={1}
                        colorScheme="brand"
                    >
                        <SliderTrack h="6px" borderRadius="full">
                            <SliderFilledTrack />
                        </SliderTrack>
                        <SliderThumb
                            boxSize={8}
                            borderWidth="3px"
                            borderColor="brand.500"
                            _focus={{
                                boxShadow: '0 0 0 3px rgba(14, 165, 233, 0.3)',
                            }}
                        >
                            <Box
                                w="10px"
                                h="10px"
                                bg="brand.500"
                                borderRadius="full"
                            />
                        </SliderThumb>
                    </Slider>
                </Box>

                {/* Scale Labels */}
                <HStack justify="space-between" px={2}>
                    {[1, 2, 3, 4, 5].map((num) => (
                        <Text
                            key={num}
                            fontSize="xs"
                            color={value === num ? 'brand.600' : 'gray.400'}
                            fontWeight={value === num ? 'bold' : 'normal'}
                        >
                            {num}
                        </Text>
                    ))}
                </HStack>
            </VStack>
        </FormControl>
    )
}
