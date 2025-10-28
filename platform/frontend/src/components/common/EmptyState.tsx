// 🎨 UX Especialist: EmptyState component for no results scenarios
// Requirements: 2.8 (Empty state handling)

import { Box, VStack, Text, Icon, BoxProps } from '@chakra-ui/react'
import { ReactElement } from 'react'
import { FiInbox } from 'react-icons/fi'
import Button from './Button'

export interface EmptyStateProps extends BoxProps {
    /** Icon to display (defaults to inbox icon) */
    icon?: ReactElement
    /** Main message to display */
    message: string
    /** Optional description text */
    description?: string
    /** Optional action button label */
    actionLabel?: string
    /** Optional action button click handler */
    onAction?: () => void
    /** Optional illustration image URL */
    illustration?: string
}

/**
 * EmptyState component for displaying helpful messages when no content is available
 * 
 * Features:
 * - Icon or illustration support
 * - Clear message and description
 * - Optional action button
 * - Responsive for mobile/desktop
 * - Friendly, helpful tone
 */
const EmptyState = ({
    icon,
    message,
    description,
    actionLabel,
    onAction,
    illustration,
    ...props
}: EmptyStateProps) => {
    return (
        <Box
            py={{ base: 12, md: 16 }}
            px={{ base: 4, md: 8 }}
            textAlign="center"
            {...props}
        >
            <VStack spacing={4} maxW="md" mx="auto">
                {/* Illustration or Icon */}
                {illustration ? (
                    <Box
                        as="img"
                        src={illustration}
                        alt=""
                        maxW={{ base: '200px', md: '300px' }}
                        mx="auto"
                    />
                ) : (
                    <Icon
                        as={icon as any || FiInbox}
                        boxSize={{ base: 12, md: 16 }}
                        color="gray.400"
                    />
                )}

                {/* Message */}
                <Text
                    fontSize={{ base: 'lg', md: 'xl' }}
                    fontWeight="semibold"
                    color="gray.700"
                >
                    {message}
                </Text>

                {/* Description */}
                {description && (
                    <Text
                        fontSize={{ base: 'sm', md: 'md' }}
                        color="gray.600"
                        maxW="sm"
                    >
                        {description}
                    </Text>
                )}

                {/* Action Button */}
                {actionLabel && onAction && (
                    <Button
                        onClick={onAction}
                        mt={4}
                        size="lg"
                    >
                        {actionLabel}
                    </Button>
                )}
            </VStack>
        </Box>
    )
}

export default EmptyState
