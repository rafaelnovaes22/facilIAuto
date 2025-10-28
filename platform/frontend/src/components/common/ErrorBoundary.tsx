// 💻 Tech Lead: Root error boundary component
import { Component, ErrorInfo, ReactNode } from 'react'
import { Box, Button, Heading, Text, VStack, Icon } from '@chakra-ui/react'
import { FiAlertTriangle } from 'react-icons/fi'

interface Props {
    children: ReactNode
    fallback?: ReactNode
    onReset?: () => void
}

interface State {
    hasError: boolean
    error: Error | null
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props)
        this.state = {
            hasError: false,
            error: null,
        }
    }

    static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error,
        }
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        console.error('ErrorBoundary caught an error:', error, errorInfo)
    }

    handleReset = (): void => {
        this.setState({ hasError: false, error: null })
        if (this.props.onReset) {
            this.props.onReset()
        } else {
            window.location.href = '/'
        }
    }

    render(): ReactNode {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback
            }

            return (
                <Box
                    minH="100vh"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    bg="gray.50"
                    px={4}
                >
                    <VStack spacing={6} maxW="md" textAlign="center">
                        <Icon as={FiAlertTriangle} boxSize={16} color="red.500" />
                        <Heading size="lg" color="gray.800">
                            Ops! Algo deu errado
                        </Heading>
                        <Text color="gray.600" fontSize="md">
                            Encontramos um problema inesperado. Não se preocupe, você pode
                            tentar novamente.
                        </Text>
                        {process.env.NODE_ENV === 'development' && this.state.error && (
                            <Box
                                bg="red.50"
                                p={4}
                                borderRadius="md"
                                borderWidth="1px"
                                borderColor="red.200"
                                w="full"
                                textAlign="left"
                            >
                                <Text fontSize="sm" fontFamily="mono" color="red.800">
                                    {this.state.error.message}
                                </Text>
                            </Box>
                        )}
                        <Button
                            size="lg"
                            onClick={this.handleReset}
                            colorScheme="brand"
                            w="full"
                        >
                            Voltar para o início
                        </Button>
                    </VStack>
                </Box>
            )
        }

        return this.props.children
    }
}

export default ErrorBoundary
