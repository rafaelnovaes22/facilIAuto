// 🎨 UX Especialist: Usage profile card with icon, title, and description
import { Box, VStack, Text, Icon } from '@chakra-ui/react'
import { IconType } from 'react-icons'

interface UsageProfileCardProps {
    icon: IconType
    title: string
    description: string
    value: string
    isSelected: boolean
    onClick: () => void
}

export const UsageProfileCard = ({
    icon,
    title,
    description,
    value,
    isSelected,
    onClick,
}: UsageProfileCardProps) => {
    return (
        <Box
            as="button"
            onClick={onClick}
            w="full"
            minH="44px"
            p={5}
            borderRadius="xl"
            borderWidth="3px"
            borderColor={isSelected ? 'brand.500' : 'gray.200'}
            bg={isSelected ? 'brand.50' : 'white'}
            cursor="pointer"
            transition="all 0.2s"
            _hover={{
                borderColor: isSelected ? 'brand.600' : 'brand.300',
                transform: 'translateY(-2px)',
                boxShadow: 'lg',
            }}
            _active={{
                transform: 'translateY(0)',
                boxShadow: 'md',
            }}
            _focus={{
                outline: 'none',
                boxShadow: '0 0 0 3px rgba(14, 165, 233, 0.3)',
            }}
            role="radio"
            aria-checked={isSelected}
            tabIndex={0}
        >
            <VStack spacing={3} align="center" textAlign="center">
                {/* Icon */}
                <Icon
                    as={icon}
                    boxSize={10}
                    color={isSelected ? 'brand.600' : 'gray.500'}
                    transition="color 0.2s"
                />

                {/* Title */}
                <Text
                    fontSize="lg"
                    fontWeight="bold"
                    color={isSelected ? 'brand.700' : 'gray.800'}
                    transition="color 0.2s"
                >
                    {title}
                </Text>

                {/* Description */}
                <Text
                    fontSize="sm"
                    color={isSelected ? 'gray.700' : 'gray.600'}
                    lineHeight="1.5"
                >
                    {description}
                </Text>

                {/* Selected Indicator */}
                {isSelected && (
                    <Box
                        position="absolute"
                        top={3}
                        right={3}
                        w={6}
                        h={6}
                        borderRadius="full"
                        bg="brand.500"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                    >
                        <Text color="white" fontSize="xs" fontWeight="bold">
                            ✓
                        </Text>
                    </Box>
                )}
            </VStack>
        </Box>
    )
}
