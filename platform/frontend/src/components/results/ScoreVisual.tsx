// 🤖 AI Engineer + 🎨 UX: Score visual com explicação
import { VStack, CircularProgress, CircularProgressLabel, Badge } from '@chakra-ui/react'

interface ScoreVisualProps {
  score: number
  percentage: number
}

export const ScoreVisual = ({ percentage }: ScoreVisualProps) => {
  // Determinar cor baseada no score
  const getColor = (pct: number) => {
    if (pct >= 80) return 'green'
    if (pct >= 60) return 'brand'
    if (pct >= 40) return 'yellow'
    return 'orange'
  }

  const getLabel = (pct: number) => {
    if (pct >= 90) return 'Match Perfeito'
    if (pct >= 80) return 'Excelente Match'
    if (pct >= 70) return 'Ótimo Match'
    if (pct >= 60) return 'Bom Match'
    if (pct >= 50) return 'Match Razoável'
    return 'Match Baixo'
  }

  const color = getColor(percentage)
  const label = getLabel(percentage)

  return (
    <VStack spacing={2}>
      <CircularProgress
        value={percentage}
        size="80px"
        thickness="8px"
        color={`${color}.500`}
        trackColor="gray.200"
      >
        <CircularProgressLabel fontSize="xl" fontWeight="bold" color={`${color}.600`}>
          {Math.round(percentage)}%
        </CircularProgressLabel>
      </CircularProgress>

      <Badge
        colorScheme={color}
        fontSize="xs"
        px={3}
        py={1}
        borderRadius="full"
        fontWeight="semibold"
      >
        {label}
      </Badge>
    </VStack>
  )
}

