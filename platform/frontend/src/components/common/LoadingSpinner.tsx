// 🎨 UX Especialist: Loading spinner component with multiple sizes
import { Box, Spinner, SpinnerProps } from '@chakra-ui/react'

interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg'
    centered?: boolean
    color?: string
}

const sizeMap: Record<'sm' | 'md' | 'lg', SpinnerProps['size']> = {
    sm: 'md',
    md: 'lg',
    lg: 'xl',
}

const thicknessMap: Record<'sm' | 'md' | 'lg', string> = {
    sm: '2px',
    md: '3px',
    lg: '4px',
}

function LoadingSpinner({
    size = 'md',
    centered = false,
    color = 'brand.500',
}: LoadingSpinnerProps) {
    const spinner = (
        <Spinner
            size={sizeMap[size]}
            thickness={thicknessMap[size]}
            speed="0.65s"
            color={color}
            emptyColor="gray.200"
        />
    )

    if (centered) {
        return (
            <Box
                display="flex"
                alignItems="center"
                justifyContent="center"
                minH="200px"
                w="full"
            >
                {spinner}
            </Box>
        )
    }

    return spinner
}

export default LoadingSpinner
