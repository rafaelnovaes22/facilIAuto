// 🎨 UX Especialist: Custom Card component with hover effects
// Requirements: 3.2 (Mobile-first design), 3.9 (Hover animations)

import { Box, BoxProps } from '@chakra-ui/react'
import { ReactNode } from 'react'

export interface CardProps extends BoxProps {
    /** Card content */
    children: ReactNode
    /** Click handler - enables hover effects when provided */
    onClick?: () => void
    /** Whether the card is in an active/selected state */
    isActive?: boolean
    /** Disable hover effects */
    disableHover?: boolean
}

/**
 * Custom Card component with mobile-optimized touch feedback
 * 
 * Features:
 * - Hover animations (translateY, boxShadow)
 * - Click handling with active states
 * - Mobile-optimized touch feedback
 * - Accessible with keyboard navigation
 */
const Card = ({
    children,
    onClick,
    isActive = false,
    disableHover = false,
    ...props
}: CardProps) => {
    const isClickable = !!onClick

    return (
        <Box
            bg="white"
            borderRadius="xl"
            boxShadow={isActive ? 'lg' : 'sm'}
            p={4}
            cursor={isClickable ? 'pointer' : 'default'}
            onClick={onClick}
            role={isClickable ? 'button' : undefined}
            tabIndex={isClickable ? 0 : undefined}
            onKeyDown={
                isClickable
                    ? (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault()
                            onClick?.()
                        }
                    }
                    : undefined
            }
            transition="all 0.2s ease-in-out"
            borderWidth={isActive ? '2px' : '1px'}
            borderColor={isActive ? 'brand.500' : 'gray.200'}
            _hover={
                !disableHover && isClickable
                    ? {
                        transform: 'translateY(-4px)',
                        boxShadow: 'lg',
                        borderColor: 'brand.300',
                    }
                    : undefined
            }
            _active={
                isClickable
                    ? {
                        transform: 'translateY(-2px)',
                        boxShadow: 'md',
                    }
                    : undefined
            }
            _focus={
                isClickable
                    ? {
                        outline: '2px solid',
                        outlineColor: 'brand.500',
                        outlineOffset: '2px',
                    }
                    : undefined
            }
            // Mobile touch feedback
            sx={{
                WebkitTapHighlightColor: 'transparent',
                touchAction: 'manipulation',
            }}
            {...props}
        >
            {children}
        </Box>
    )
}

export default Card
