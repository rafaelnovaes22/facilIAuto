// 💻 Tech Lead: Page-level error boundary wrapper
import React, { ReactNode } from 'react'
import { Box, Button, Heading, Text, VStack, Icon } from '@chakra-ui/react'
import { FiAlertCircle, FiHome } from 'react-icons/fi'
import { useNavigate } from 'react-router-dom'

interface Props {
    children: ReactNode
}

interface State {
    hasError: boolean
    error: Error | null
}

class PageErrorBoundaryClass extends React.Component<Props, State> {
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

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
        console.error('PageErrorBoundary caught an error:', error, errorInfo)
    }

    render(): ReactNode {
        if (this.state.hasError) {
            return <PageErrorFallback error={this.state.error} />
        }

        return this.props.children
    }
}

function PageErrorFallback({ error }: { error: Error | null }) {
    const navigate = useNavigate()

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
                <Icon as={FiAlertCircle} boxSize={12} color="orange.500" />
                <Heading size="md" color="gray.800">
                    Esta página encontrou um problema
                </Heading>
                <Text color="gray.600" fontSize="sm">
                    Não se preocupe, o resto do site continua funcionando normalmente.
                </Text>
                {process.env.NODE_ENV === 'development' && error && (
                    <Box
                        bg="orange.50"
                        p={3}
                        borderRadius="md"
                        borderWidth="1px"
                        borderColor="orange.200"
                        w="full"
                        textAlign="left"
                    >
                        <Text fontSize="xs" fontFamily="mono" color="orange.800">
                            {error.message}
                        </Text>
                    </Box>
                )}
                <VStack spacing={3} w="full">
                    <Button
                        size="md"
                        onClick={() => window.location.reload()}
                        colorScheme="brand"
                        w="full"
                    >
                        Recarregar página
                    </Button>
                    <Button
                        size="md"
                        onClick={() => navigate('/')}
                        variant="outline"
                        leftIcon={<Icon as={FiHome} />}
                        w="full"
                    >
                        Voltar para o início
                    </Button>
                </VStack>
            </VStack>
        </Box>
    )
}

export default PageErrorBoundaryClass
