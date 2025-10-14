// 🎨 UX + 🤖 AI Engineer: Card de carro com score
import {
  Box,
  Card,
  CardBody,
  Heading,
  Text,
  HStack,
  VStack,
  Button,
  Badge,
  Divider,
  SimpleGrid,
  Icon,
  Image,
  AspectRatio,
} from '@chakra-ui/react'
import { FaWhatsapp, FaGasPump, FaCog, FaCalendar, FaTachometerAlt, FaMapMarkerAlt, FaImages } from 'react-icons/fa'
import type { Recommendation } from '@/types'
import { formatCurrency, formatNumber } from '@/services/api'
import { ScoreVisual } from './ScoreVisual'

interface CarCardProps {
  recommendation: Recommendation
  onWhatsAppClick?: (car: Recommendation['car']) => void
  onDetailsClick?: (car: Recommendation['car']) => void
}

export const CarCard = ({ recommendation, onWhatsAppClick, onDetailsClick }: CarCardProps) => {
  const { car, match_percentage, justification } = recommendation

  const handleWhatsAppClick = () => {
    const message = encodeURIComponent(
      `Olá! Vi o ${car.nome} no FacilIAuto e gostaria de mais informações.`
    )
    const whatsappUrl = `https://wa.me/${car.dealership_whatsapp}?text=${message}`
    
    window.open(whatsappUrl, '_blank')
    
    if (onWhatsAppClick) {
      onWhatsAppClick(car)
    }
  }

  const mainImage = car.imagens && car.imagens.length > 0 ? car.imagens[0] : null
  const hasMultipleImages = car.imagens && car.imagens.length > 1

  return (
    <Card
      variant="elevated"
      data-testid="car-card"
      _hover={{
        boxShadow: '2xl',
        transform: 'translateY(-4px)',
      }}
      transition="all 0.3s"
    >
      <CardBody p={6}>
        <HStack align="flex-start" spacing={6}>
          {/* Imagem do Carro - Esquerda */}
          <Box flexShrink={0} position="relative">
            <AspectRatio ratio={4 / 3} width="200px">
              <Image
                src={mainImage || 'https://via.placeholder.com/400x300?text=Sem+Imagem'}
                alt={car.nome}
                objectFit="cover"
                borderRadius="lg"
                fallbackSrc="https://via.placeholder.com/400x300?text=Carregando..."
                cursor={onDetailsClick ? 'pointer' : 'default'}
                onClick={() => onDetailsClick?.(car)}
              />
            </AspectRatio>
            {hasMultipleImages && (
              <Badge
                position="absolute"
                bottom={2}
                right={2}
                colorScheme="blackAlpha"
                fontSize="xs"
                display="flex"
                alignItems="center"
                gap={1}
              >
                <Icon as={FaImages} />
                {car.imagens.length}
              </Badge>
            )}
          </Box>

          {/* Score Visual */}
          <Box flexShrink={0}>
            <ScoreVisual score={recommendation.match_score} percentage={match_percentage} />
          </Box>

          {/* Informações do Carro - Centro */}
          <VStack align="stretch" flex={1} spacing={4}>
            {/* Nome do Carro */}
            <Box>
              <HStack mb={2}>
                <Badge colorScheme="purple" fontSize="xs">
                  {car.categoria}
                </Badge>
                {car.destaque && (
                  <Badge colorScheme="orange" fontSize="xs">
                    ⭐ Destaque
                  </Badge>
                )}
              </HStack>
              
              <Heading size="md" color="gray.800">
                {car.nome}
              </Heading>
              
              <Text fontSize="sm" color="gray.600">
                {car.marca} {car.modelo} {car.versao && `- ${car.versao}`}
              </Text>
            </Box>

            {/* Preço */}
            <Text fontSize="2xl" fontWeight="bold" color="brand.600">
              {formatCurrency(car.preco)}
            </Text>

            {/* Características */}
            <SimpleGrid columns={2} spacing={3} fontSize="sm">
              <HStack>
                <Icon as={FaCalendar} color="gray.500" />
                <Text color="gray.700">{car.ano}</Text>
              </HStack>

              <HStack>
                <Icon as={FaTachometerAlt} color="gray.500" />
                <Text color="gray.700">{formatNumber(car.quilometragem)} km</Text>
              </HStack>

              <HStack>
                <Icon as={FaGasPump} color="gray.500" />
                <Text color="gray.700">{car.combustivel}</Text>
              </HStack>

              <HStack>
                <Icon as={FaCog} color="gray.500" />
                <Text color="gray.700">{car.cambio || 'Manual'}</Text>
              </HStack>
            </SimpleGrid>

            {/* Justificativa da IA */}
            <Box
              bg="brand.50"
              p={3}
              borderRadius="md"
              borderLeftWidth="3px"
              borderLeftColor="brand.500"
            >
              <Text fontSize="xs" color="gray.600" fontWeight="semibold" mb={1}>
                💡 Por que recomendamos:
              </Text>
              <Text fontSize="sm" color="gray.700">
                {justification}
              </Text>
            </Box>

            <Divider />

            {/* Concessionária e Ações */}
            <VStack align="stretch" spacing={3}>
              <HStack justify="space-between" align="center">
                <VStack align="flex-start" spacing={0}>
                  <Text fontSize="sm" fontWeight="semibold" color="gray.800">
                    {car.dealership_name}
                  </Text>
                  <HStack spacing={1}>
                    <Icon as={FaMapMarkerAlt} color="gray.500" boxSize={3} />
                    <Text fontSize="xs" color="gray.600">
                      {car.dealership_city} - {car.dealership_state}
                    </Text>
                  </HStack>
                </VStack>

                {/* Botão WhatsApp */}
                <Button
                  leftIcon={<FaWhatsapp />}
                  colorScheme="whatsapp"
                  size="md"
                  onClick={handleWhatsAppClick}
                >
                  WhatsApp
                </Button>
              </HStack>

              {/* Botão Ver Detalhes */}
              {onDetailsClick && (
                <Button
                  variant="outline"
                  colorScheme="brand"
                  size="sm"
                  onClick={() => onDetailsClick(car)}
                  leftIcon={<FaImages />}
                >
                  Ver Detalhes e Fotos {hasMultipleImages && `(${car.imagens.length})`}
                </Button>
              )}
            </VStack>
          </VStack>
        </HStack>
      </CardBody>
    </Card>
  )
}

