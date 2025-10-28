// 🎨 UX Especialist: Custom Button component with variants and loading states
// Requirements: 3.2 (Mobile-first with 44px tap targets), 9.2 (Keyboard navigation)

import { Button as ChakraButton, ButtonProps as ChakraButtonProps, Spinner } from '@chakra-ui/react'
import { ReactElement } from 'react'

export interface ButtonProps extends Omit<ChakraButtonProps, 'leftIcon' | 'rightIcon'> {
    /** Button variant: solid (default), outline, or ghost */
    variant?: 'solid' | 'outline' | 'ghost'
    /** Button size: sm, md (default), lg */
    size?: 'sm' | 'md' | 'lg'
    /** Loading state - shows spinner and disables button */
    isLoading?: boolean
    /** Icon to display on the left side */
    leftIcon?: ReactElement
    /** Icon to display on the right side */
    rightIcon?: ReactElement
    /** Button content */
    children: React.ReactNode
}

/**
 * Custom Button component with mobile-optimized tap targets and loading states
 * 
 * Features:
 * - Minimum 44px tap target for mobile (WCAG 2.1)
 * - Loading state with spinner
 * - Icon support (left/right positioning)
 * - Three variants: solid, outline, ghost
 * - Keyboard accessible
 */
const Button = ({
    variant = 'solid',
    size = 'md',
    isLoading = false,
    leftIcon,
    rightIcon,
    children,
    ...props
}: ButtonProps) => {
    return (
        <ChakraButton
            variant={variant}
            size={size}
            isLoading={isLoading}
            leftIcon={leftIcon}
            rightIcon={rightIcon}
            spinner={<Spinner size="sm" />}
            minH="44px" // Minimum tap target for mobile
            {...props}
        >
            {children}
        </ChakraButton>
    )
}

export default Button
