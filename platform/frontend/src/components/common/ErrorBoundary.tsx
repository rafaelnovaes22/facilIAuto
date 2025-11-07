// 💻 Tech Lead: Error Boundary for catching React errors
import React, { Component, ErrorInfo, ReactNode } from 'react'
import {
    Box,
    Container,
    VStack,
    Heading,
    Text,
    Button,
    Alert,
    AlertIcon,
    AlertTitle,
    AlertDescription,
    Code,
} from '@chakra-ui/react'
import { FaHome, FaRedo } from 'react-icons/fa'

interface Props {
    children: ReactNode
    fallback?: ReactNode
    onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
    hasError: boolean
    error: Error | null
    errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props)
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        }
    }

    static getDerivedStateFromError(error: Error): State {
        // Update state so the next render will show the fallback UI
        return {
            hasError: true,
            error,
            errorInfo: null,
        }
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        // Log error to console
        console.error('ErrorBoundary caught an error:', error, errorInfo)

        // Update state with error details
        this.setState({
            error,
            errorInfo,
        })

        // Call optional error handler
        if (this.props.onError) {
            this.props.onError(error, errorInfo)
        }

        // Here you could also send error to monitoring service (Sentry, etc)
    }

    handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
        })
    }

    handleGoHome = () => {
        window.location.href = '/'
    }

    render() {
        if (this.state.hasError) {
            // Custom fallback UI
            if (this.props.fallback) {
                return this.props.fallback
            }

            // Default error UI
            return (
                <Box bg="gray.50" minH="100vh" py={10}>
                    <Container maxW="container.md">
                        <VStack spacing={6} align="stretch">
                            <Alert
                                status="error"
                                variant="subtle"
                                flexDirection="column"
                                alignItems="center"
                                justifyContent="center"
                                textAlign="center"
                                borderRadius="xl"
                                p={8}
                            >
                                <AlertIcon boxSize="50px" mr={0} />
                                <AlertTitle mt={4} mb={2} fontSize="2xl">
                                    Ops! Algo deu errado
                                </AlertTitle>
                                <AlertDescription maxWidth="lg" mb={6}>
                                    Ocorreu um erro inesperado. Nossa equipe foi notificada e
                                    estamos trabalhando para resolver o problema.
                                </AlertDescription>

                                <VStack spacing={4} w="full">
                                    <Button
                                        colorScheme="blue"
                                        size="lg"
                                        leftIcon={<FaRedo />}
                                        onClick={this.handleReset}
                                    >
                                        Tentar Novamente
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="lg"
                                        leftIcon={<FaHome />}
                                        onClick={this.handleGoHome}
                                    >
                                        Voltar para Início
                                    </Button>
                                </VStack>
                            </Alert>

                            {/* Error details (only in development) */}
                            {import.meta.env.DEV && this.state.error && (
                                <Box
                                    bg="white"
                                    p={6}
                                    borderRadius="xl"
                                    boxShadow="md"
                                    maxH="400px"
                                    overflowY="auto"
                                >
                                    <Heading size="md" mb={4} color="red.600">
                                        Detalhes do Erro (Dev Mode)
                                    </Heading>
                                    <VStack align="stretch" spacing={4}>
                                        <Box>
                                            <Text fontWeight="bold" mb={2}>
                                                Mensagem:
                                            </Text>
                                            <Code
                                                display="block"
                                                whiteSpace="pre-wrap"
                                                p={3}
                                                borderRadius="md"
                                                colorScheme="red"
                                            >
                                                {this.state.error.message}
                                            </Code>
                                        </Box>
                                        {this.state.error.stack && (
                                            <Box>
                                                <Text fontWeight="bold" mb={2}>
                                                    Stack Trace:
                                                </Text>
                                                <Code
                                                    display="block"
                                                    whiteSpace="pre-wrap"
                                                    p={3}
                                                    borderRadius="md"
                                                    fontSize="xs"
                                                    colorScheme="red"
                                                >
                                                    {this.state.error.stack}
                                                </Code>
                                            </Box>
                                        )}
                                        {this.state.errorInfo && (
                                            <Box>
                                                <Text fontWeight="bold" mb={2}>
                                                    Component Stack:
                                                </Text>
                                                <Code
                                                    display="block"
                                                    whiteSpace="pre-wrap"
                                                    p={3}
                                                    borderRadius="md"
                                                    fontSize="xs"
                                                    colorScheme="red"
                                                >
                                                    {this.state.errorInfo.componentStack}
                                                </Code>
                                            </Box>
                                        )}
                                    </VStack>
                                </Box>
                            )}
                        </VStack>
                    </Container>
                </Box>
            )
        }

        return this.props.children
    }
}

export default ErrorBoundary
