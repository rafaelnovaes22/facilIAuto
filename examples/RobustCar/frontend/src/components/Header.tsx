import {
  Box,
  Flex,
  Text,
  Button,
  Stack,
  useColorModeValue,
  Container,
  Image,
  Link as ChakraLink,
} from '@chakra-ui/react'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import { FaCar, FaPhone, FaWhatsapp } from 'react-icons/fa'

export default function Header() {
  const location = useLocation()
  
  const bgColor = useColorModeValue('white', 'gray.900')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  
  const isActive = (path: string) => location.pathname === path

  return (
    <Box
      bg={bgColor}
      px={4}
      borderBottom="1px"
      borderColor={borderColor}
      shadow="sm"
      position="sticky"
      top={0}
      zIndex={1000}
    >
      <Container maxW="7xl">
        <Flex h={16} alignItems="center" justifyContent="space-between">
          {/* Logo */}
          <Flex alignItems="center" as={RouterLink} to="/">
            <Box
              w={10}
              h={10}
              bg="brand.500"
              borderRadius="lg"
              display="flex"
              alignItems="center"
              justifyContent="center"
              mr={3}
            >
              <FaCar color="white" size="20" />
            </Box>
            <Text
              fontSize="xl"
              fontWeight="bold"
              color="brand.500"
              _hover={{ color: 'brand.600' }}
              transition="color 0.2s"
            >
              RobustCar
            </Text>
          </Flex>

          {/* Navigation */}
          <Flex alignItems="center">
            <Stack direction="row" spacing={4} mr={6}>
              <Button
                as={RouterLink}
                to="/"
                variant={isActive('/') ? 'solid' : 'ghost'}
                size="sm"
              >
                Início
              </Button>
              <Button
                as={RouterLink}
                to="/questionario"
                variant={isActive('/questionario') ? 'solid' : 'ghost'}
                size="sm"
              >
                Encontrar Carro
              </Button>
              <Button
                as={RouterLink}
                to="/sobre"
                variant={isActive('/sobre') ? 'ghost' : 'ghost'}
                size="sm"
              >
                Sobre
              </Button>
            </Stack>

            {/* Contact Info */}
            <Stack direction="row" spacing={3} alignItems="center">
              <ChakraLink
                href="tel:+551126676852"
                display="flex"
                alignItems="center"
                fontSize="sm"
                color="gray.600"
                _hover={{ color: 'brand.500' }}
              >
                <FaPhone size="12" style={{ marginRight: '4px' }} />
                (11) 2667-6852
              </ChakraLink>
              
              <ChakraLink
                href="https://wa.me/551126676852"
                isExternal
                display="flex"
                alignItems="center"
                bg="green.500"
                color="white"
                px={3}
                py={1}
                borderRadius="full"
                fontSize="sm"
                _hover={{ bg: 'green.600' }}
                transition="background 0.2s"
              >
                <FaWhatsapp size="14" style={{ marginRight: '4px' }} />
                WhatsApp
              </ChakraLink>
            </Stack>
          </Flex>
        </Flex>
      </Container>
    </Box>
  )
}
