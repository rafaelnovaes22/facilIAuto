// 🎨 UX Especialist: User-friendly error message component with retry
import { Box, Button, Heading, Text, VStack, Icon } from '@chakra-ui/react'
import { FiAlertCircle, FiRefreshCw } from 'react-icons/fi'

interface ErrorMessageProps {
    title?: string
    message?: string
    onRetry?: () => void
    showRetry?: boolean
}

function ErrorMessage({
    title = 'Ops! Algo deu errado',
    message = 'Não conseguimos carregar as informações. Tente novamente.',
    onRetry,
    showRetry = true,
}: ErrorMessageProps) {
    return (
        <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            minH="300px"
            w="full"
            px={4}
        >
            <VStack spacing={4} maxW="md" textAlign="center">
                <Icon as={FiAlertCircle} boxSize={12} color="red.500" />
                <Heading size="md" color="gray.800">
                    {title}
                </Heading>
                <Text color="gray.600" fontSize="sm">
                    {message}
                </Text>
                {showRetry && onRetry && (
                    <Button
                        onClick={onRetry}
                        colorScheme="brand"
                        leftIcon={<Icon as={FiRefreshCw} />}
                        size="md"
                        mt={2}
                    >
                        Tentar novamente
                    </Button>
                )}
            </VStack>
        </Box>
    )
}

export default ErrorMessage
