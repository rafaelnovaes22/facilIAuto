// 🎨 UX Especialist: Progress indicator visual
import { Box, HStack, Text, Progress, VStack } from '@chakra-ui/react'
import { FaCheck } from 'react-icons/fa'

interface ProgressIndicatorProps {
  currentStep: number
  totalSteps: number
  stepTitles: string[]
}

export const ProgressIndicator = ({
  currentStep,
  totalSteps,
  stepTitles,
}: ProgressIndicatorProps) => {
  const progress = ((currentStep + 1) / totalSteps) * 100

  return (
    <VStack spacing={6} w="full">
      {/* Progress Bar */}
      <Box w="full">
        <Progress
          value={progress}
          colorScheme="brand"
          size="sm"
          borderRadius="full"
          bg="gray.200"
        />
      </Box>

      {/* Step Indicators */}
      <HStack spacing={4} justify="center" flexWrap="wrap">
        {stepTitles.map((title, index) => {
          const isCompleted = index < currentStep
          const isCurrent = index === currentStep
          const isUpcoming = index > currentStep

          return (
            <HStack
              key={index}
              spacing={2}
              opacity={isUpcoming ? 0.5 : 1}
              transition="all 0.3s"
            >
              {/* Circle */}
              <Box
                w="32px"
                h="32px"
                borderRadius="full"
                bg={
                  isCompleted
                    ? 'brand.500'
                    : isCurrent
                    ? 'brand.500'
                    : 'gray.300'
                }
                color="white"
                display="flex"
                alignItems="center"
                justifyContent="center"
                fontWeight="bold"
                fontSize="sm"
                transition="all 0.3s"
                boxShadow={isCurrent ? 'lg' : 'none'}
              >
                {isCompleted ? <FaCheck /> : index + 1}
              </Box>

              {/* Title (hidden on mobile) */}
              <Text
                fontSize="sm"
                fontWeight={isCurrent ? 'bold' : 'normal'}
                color={isCurrent ? 'brand.600' : 'gray.600'}
                display={{ base: 'none', md: 'block' }}
              >
                {title}
              </Text>
            </HStack>
          )
        })}
      </HStack>

      {/* Current Step Title (mobile) */}
      <Text
        fontSize="lg"
        fontWeight="bold"
        color="brand.600"
        display={{ base: 'block', md: 'none' }}
        textAlign="center"
      >
        {stepTitles[currentStep]}
      </Text>
    </VStack>
  )
}

