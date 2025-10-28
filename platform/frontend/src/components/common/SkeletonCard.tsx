// 🎨 UX Especialist: Skeleton loading placeholder for car cards
import { Box, Skeleton, SkeletonText, VStack } from '@chakra-ui/react'

interface SkeletonCardProps {
    count?: number
}

function SkeletonCard({ count = 1 }: SkeletonCardProps) {
    return (
        <>
            {Array.from({ length: count }).map((_, index) => (
                <Box
                    key={index}
                    bg="white"
                    borderRadius="xl"
                    overflow="hidden"
                    boxShadow="sm"
                    w="full"
                >
                    {/* Image skeleton */}
                    <Skeleton height="200px" />

                    {/* Content skeleton */}
                    <VStack align="stretch" p={4} spacing={3}>
                        {/* Badge skeleton */}
                        <Skeleton height="24px" width="60px" borderRadius="full" />

                        {/* Title skeleton */}
                        <SkeletonText noOfLines={1} spacing="4" skeletonHeight="6" />

                        {/* Price skeleton */}
                        <Skeleton height="28px" width="120px" />

                        {/* Features skeleton */}
                        <VStack align="stretch" spacing={2} mt={2}>
                            <SkeletonText noOfLines={3} spacing="3" skeletonHeight="3" />
                        </VStack>
                    </VStack>
                </Box>
            ))}
        </>
    )
}

export default SkeletonCard
