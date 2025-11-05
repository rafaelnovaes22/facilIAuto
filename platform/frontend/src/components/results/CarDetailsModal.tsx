// 🎨 UX + 🤖 AI Engineer: Modal de detalhes do carro com galeria
import { useState, useEffect, useRef } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Box,
  Image,
  HStack,
  VStack,
  Text,
  Button,
  IconButton,
  Badge,
  SimpleGrid,
  Icon,
  AspectRatio,
  Heading,
  Divider,
} from '@chakra-ui/react'
import {
  FaChevronLeft,
  FaChevronRight,
  FaWhatsapp,
  FaGasPump,
  FaCog,
  FaCalendar,
  FaTachometerAlt,
  FaMapMarkerAlt,
  FaPalette,
  FaDoorOpen,
} from 'react-icons/fa'
import type { Recommendation, TCOBreakdown } from '@/types'
import { formatCurrency, formatNumber } from '@/services/api'
import { TCOBreakdownCard } from './TCOBreakdownCard'
import interactionTracker from '@/services/InteractionTracker'
import { CAR_PLACEHOLDER_LARGE, CAR_PLACEHOLDER_LOADING_LARGE, CAR_PLACEHOLDER_THUMB } from '@/utils/imagePlaceholder'

interface CarDetailsModalProps {
  isOpen: boolean
  onClose: () => void
  car: Recommendation['car'] | null
  tco_breakdown?: TCOBreakdown
  fits_budget?: boolean
  budget_percentage?: number
  userPreferences?: {
    budget: number
    usage: string
    priorities: string[]
  }
  position?: number
  matchScore?: number
}

export const CarDetailsModal = ({ isOpen, onClose, car, tco_breakdown, fits_budget, budget_percentage, userPreferences, position, matchScore }: CarDetailsModalProps) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const viewStartTime = useRef<number | null>(null)

  // 🤖 ML: Rastrear tempo de visualização
  useEffect(() => {
    if (isOpen && car) {
      // Iniciar contagem de tempo
      viewStartTime.current = Date.now()
    }

    return () => {
      // Ao fechar, calcular duração e enviar
      if (viewStartTime.current && car && userPreferences) {
        const durationSeconds = Math.floor((Date.now() - viewStartTime.current) / 1000)

        interactionTracker.trackViewDuration(
          car.id,
          durationSeconds,
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
          matchScore
        )

        viewStartTime.current = null
      }
    }
  }, [isOpen, car, userPreferences, position, matchScore])

  if (!car) return null

  const images = car.imagens && car.imagens.length > 0 ? car.imagens : [CAR_PLACEHOLDER_LARGE]
  const totalImages = images.length

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % totalImages)
  }

  const previousImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + totalImages) % totalImages)
  }

  const handleWhatsAppClick = () => {
    const message = encodeURIComponent(
      `Olá! Vi o ${car.nome} no FacilIAuto e gostaria de mais informações.`
    )
    const whatsappUrl = `https://wa.me/${car.dealership_whatsapp}?text=${message}`
    window.open(whatsappUrl, '_blank')
  }

  // Reset image index when modal closes
  const handleClose = () => {
    setCurrentImageIndex(0)
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="6xl">
      <ModalOverlay bg="blackAlpha.700" />
      <ModalContent maxH="90vh" overflow="hidden">
        <ModalHeader>
          <VStack align="flex-start" spacing={1}>
            <HStack>
              <Badge colorScheme="purple">{car.categoria}</Badge>
              {car.destaque && (
                <Badge colorScheme="orange">⭐ Destaque</Badge>
              )}
            </HStack>
            <Heading size="lg">{car.nome}</Heading>
            <Text fontSize="md" color="gray.600" fontWeight="normal">
              {car.marca} {car.modelo} {car.versao && `- ${car.versao}`}
            </Text>
          </VStack>
        </ModalHeader>
        <ModalCloseButton />

        <ModalBody pb={6} overflowY="auto">
          <VStack spacing={6} align="stretch">
            {/* Galeria de Imagens */}
            <Box position="relative">
              <AspectRatio ratio={16 / 9} maxH="500px">
                <Image
                  src={images[currentImageIndex]}
                  alt={`${car.nome} - Foto ${currentImageIndex + 1}`}
                  objectFit="contain"
                  bg="gray.100"
                  borderRadius="lg"
                  fallbackSrc={CAR_PLACEHOLDER_LOADING_LARGE}
                />
              </AspectRatio>

              {/* Controles de Navegação */}
              {totalImages > 1 && (
                <>
                  <IconButton
                    aria-label="Foto anterior"
                    icon={<FaChevronLeft />}
                    position="absolute"
                    left={4}
                    top="50%"
                    transform="translateY(-50%)"
                    onClick={previousImage}
                    colorScheme="blackAlpha"
                    size="lg"
                    isRound
                  />
                  <IconButton
                    aria-label="Próxima foto"
                    icon={<FaChevronRight />}
                    position="absolute"
                    right={4}
                    top="50%"
                    transform="translateY(-50%)"
                    onClick={nextImage}
                    colorScheme="blackAlpha"
                    size="lg"
                    isRound
                  />

                  {/* Indicador de Posição */}
                  <Badge
                    position="absolute"
                    bottom={4}
                    left="50%"
                    transform="translateX(-50%)"
                    colorScheme="blackAlpha"
                    fontSize="sm"
                    px={3}
                    py={1}
                  >
                    {currentImageIndex + 1} / {totalImages}
                  </Badge>
                </>
              )}
            </Box>

            {/* Miniaturas */}
            {totalImages > 1 && (
              <HStack spacing={2} overflowX="auto" pb={2}>
                {images.map((img, index) => (
                  <Box
                    key={index}
                    flexShrink={0}
                    cursor="pointer"
                    onClick={() => setCurrentImageIndex(index)}
                    borderWidth={currentImageIndex === index ? '3px' : '1px'}
                    borderColor={currentImageIndex === index ? 'brand.500' : 'gray.200'}
                    borderRadius="md"
                    overflow="hidden"
                    transition="all 0.2s"
                    _hover={{ borderColor: 'brand.400' }}
                  >
                    <AspectRatio ratio={4 / 3} width="100px">
                      <Image
                        src={img}
                        alt={`Miniatura ${index + 1}`}
                        objectFit="cover"
                        fallbackSrc={CAR_PLACEHOLDER_THUMB}
                      />
                    </AspectRatio>
                  </Box>
                ))}
              </HStack>
            )}

            <Divider />

            {/* TCO Breakdown */}
            {tco_breakdown && (
              <>
                <TCOBreakdownCard
                  tco={tco_breakdown}
                  fits_budget={fits_budget}
                  budget_percentage={budget_percentage}
                />
                <Divider />
              </>
            )}

            {/* Informações do Veículo */}
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
              {/* Coluna 1: Preço e Características */}
              <VStack align="stretch" spacing={4}>
                <Box>
                  <Text fontSize="sm" color="gray.600" mb={1}>
                    Preço
                  </Text>
                  <Text fontSize="3xl" fontWeight="bold" color="brand.600">
                    {formatCurrency(car.preco)}
                  </Text>
                </Box>

                <SimpleGrid columns={2} spacing={4}>
                  <VStack align="flex-start" spacing={1}>
                    <HStack color="gray.600">
                      <Icon as={FaCalendar} />
                      <Text fontSize="xs">Ano</Text>
                    </HStack>
                    <Text fontWeight="semibold">{car.ano}</Text>
                  </VStack>

                  <VStack align="flex-start" spacing={1}>
                    <HStack color="gray.600">
                      <Icon as={FaTachometerAlt} />
                      <Text fontSize="xs">Quilometragem</Text>
                    </HStack>
                    <Text fontWeight="semibold">{formatNumber(car.quilometragem)} km</Text>
                  </VStack>

                  <VStack align="flex-start" spacing={1}>
                    <HStack color="gray.600">
                      <Icon as={FaGasPump} />
                      <Text fontSize="xs">Combustível</Text>
                    </HStack>
                    <Text fontWeight="semibold">{car.combustivel}</Text>
                  </VStack>

                  <VStack align="flex-start" spacing={1}>
                    <HStack color="gray.600">
                      <Icon as={FaCog} />
                      <Text fontSize="xs">Câmbio</Text>
                    </HStack>
                    <Text fontWeight="semibold">{car.cambio || 'Manual'}</Text>
                  </VStack>

                  {car.cor && (
                    <VStack align="flex-start" spacing={1}>
                      <HStack color="gray.600">
                        <Icon as={FaPalette} />
                        <Text fontSize="xs">Cor</Text>
                      </HStack>
                      <Text fontWeight="semibold">{car.cor}</Text>
                    </VStack>
                  )}

                  {car.portas && (
                    <VStack align="flex-start" spacing={1}>
                      <HStack color="gray.600">
                        <Icon as={FaDoorOpen} />
                        <Text fontSize="xs">Portas</Text>
                      </HStack>
                      <Text fontWeight="semibold">{car.portas}</Text>
                    </VStack>
                  )}
                </SimpleGrid>
              </VStack>

              {/* Coluna 2: Concessionária */}
              <VStack align="stretch" spacing={4}>
                <Box
                  bg="gray.50"
                  p={4}
                  borderRadius="lg"
                  borderWidth="1px"
                  borderColor="gray.200"
                >
                  <Text fontSize="sm" color="gray.600" mb={2}>
                    Concessionária
                  </Text>
                  <Text fontSize="lg" fontWeight="bold" color="gray.800" mb={3}>
                    {car.dealership_name}
                  </Text>

                  <VStack align="flex-start" spacing={2}>
                    <HStack>
                      <Icon as={FaMapMarkerAlt} color="brand.500" />
                      <Text fontSize="sm">
                        {car.dealership_city} - {car.dealership_state}
                      </Text>
                    </HStack>
                  </VStack>

                  <Button
                    leftIcon={<FaWhatsapp />}
                    colorScheme="whatsapp"
                    width="full"
                    mt={4}
                    size="lg"
                    onClick={handleWhatsAppClick}
                  >
                    Falar no WhatsApp
                  </Button>
                </Box>
              </VStack>
            </SimpleGrid>
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  )
}

