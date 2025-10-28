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
import interactionTracker from '@/services/InteractionTracker'
import { CAR_PLACEHOLDER, CAR_PLACEHOLDER_LOADING } from '@/utils/imagePlaceholder'

interface CarCardProps {
  recommendation: Recommendation
  onWhatsAppClick?: (car: Recommendation['car']) => void
  onDetailsClick?: (car: Recommendation['car']) => void
  position?: number
  userPreferences?: {
    budget: number
    usage: string
    priorities: string[]
  }
}

export const CarCard = ({ recommendation, onWhatsAppClick, onDetailsClick, position, userPreferences }: CarCardProps) => {
  const { car, match_percentage, justification } = recommendation

  const handleWhatsAppClick = () => {
    const message = encodeURIComponent(
      `Olá! Vi o ${car.nome} no FacilIAuto e gostaria de mais informações.`
    )
    const whatsappUrl = `https://wa.me/${car.dealership_whatsapp}?text=${message}`

    window.open(whatsappUrl, '_blank')

    // 🤖 ML: Rastrear clique no WhatsApp
    if (userPreferences) {
      interactionTracker.trackWhatsAppClick(
        car.id,
        userPreferences,
        {
          marca: car.marca,
          modelo: car.modelo,
          ano: car.ano,
          preco: car.preco,
          categoria: car.categoria,
          combustivel: car.combustivel,
          cambio: car.cambio || 'Manual',
          quilometragem: car.quilometragem
        },
        position,
        recommendation.match_score
      )
    }

    if (onWhatsAppClick) {
      onWhatsAppClick(car)
    }
  }

  const handleDetailsClick = () => {
    // 🤖 ML: Rastrear clique em detalhes
    if (userPreferences) {
      interactionTracker.trackViewDetails(
        car.id,
        userPreferences,
        {
          marca: car.marca,
          modelo: car.modelo,
          ano: car.ano,
          preco: car.preco,
          categoria: car.categoria,
          combustivel: car.combustivel,
          cambio: car.cambio || 'Manual',
          quilometragem: car.quilometragem
        },
        position,
        recommendation.match_score
      )
    }

    if (onDetailsClick) {
      onDetailsClick(car)
    }
  }

  const handleCardClick = () => {
    // 🤖 ML: Rastrear clique no card
    if (userPreferences) {
      interactionTracker.trackCarClick(
        car.id,
        userPreferences,
        {
          marca: car.marca,
          modelo: car.modelo,
          ano: car.ano,
          preco: car.preco,
          categoria: car.categoria,
          combustivel: car.combustivel,
          cambio: car.cambio || 'Manual',
          quilometragem: car.quilometragem
        },
        position,
        recommendation.match_score
      )
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
      onClick={handleCardClick}
      cursor="pointer"
    >
      <CardBody p={0}>
        <VStack align="stretch" spacing={0}>
          {/* Imagem do Carro - Topo */}
          <Box position="relative" width="100%">
            <AspectRatio ratio={16 / 9} width="100%">
              <Image
                src={mainImage || CAR_PLACEHOLDER}
                alt={car.nome}
                objectFit="cover"
                borderTopRadius="lg"
                fallbackSrc={CAR_PLACEHOLDER_LOADING}
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
            {/* Score Badge no canto superior direito */}
            <Box position="absolute" top={2} right={2}>
              <Badge colorScheme="green" fontSize="lg" px={3} py={2} borderRadius="full">
                {Math.round(match_percentage)}% Match
              </Badge>
            </Box>
          </Box>

          {/* Informações do Carro - Abaixo da imagem */}
          <VStack align="stretch" spacing={4} p={6}>
            {/* Nome do Carro */}
            <Box>
              <HStack mb={2} flexWrap="wrap">
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

              {car.versao && (
                <Text fontSize="sm" color="gray.600">
                  {car.versao}
                </Text>
              )}
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
                  onClick={handleDetailsClick}
                  leftIcon={<FaImages />}
                >
                  Ver Detalhes e Fotos {hasMultipleImages && `(${car.imagens.length})`}
                </Button>
              )}
            </VStack>
          </VStack>
        </VStack>
      </CardBody>
    </Card>
  )
}

