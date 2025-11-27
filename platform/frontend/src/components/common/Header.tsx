// 🎨 UX Especialist + 💻 Tech Lead: Header com logo
import { Box, Image, HStack, Link, Flex, Button } from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import faciliautoLogo from '@/assets/faciliauto-logo.png'

export default function Header() {
  const navigate = useNavigate()

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <Box bg="white" boxShadow="md" position="sticky" top={0} zIndex={1000}>
      <Box maxW="container.xl" mx="auto" px={4} py={3}>
        <Flex justify="space-between" align="center">
          <Image
            src={faciliautoLogo}
            alt="FacilIAuto Logo"
            height="40px"
            width="auto"
            objectFit="contain"
            cursor="pointer"
            onClick={() => navigate('/')}
          />

          <HStack spacing={8} display={{ base: 'none', md: 'flex' }}>
            <Link
              onClick={() => scrollToSection('destaques')}
              fontSize="sm"
              fontWeight="medium"
              color="gray.700"
              _hover={{ color: 'brand.500' }}
              cursor="pointer"
            >
              Carros Selecionados
            </Link>
            <Link
              onClick={() => scrollToSection('como-funciona')}
              fontSize="sm"
              fontWeight="medium"
              color="gray.700"
              _hover={{ color: 'brand.500' }}
              cursor="pointer"
            >
              Como Funciona
            </Link>
            <Link
              onClick={() => scrollToSection('seguranca')}
              fontSize="sm"
              fontWeight="medium"
              color="gray.700"
              _hover={{ color: 'brand.500' }}
              cursor="pointer"
            >
              Segurança
            </Link>
            <Link
              onClick={() => scrollToSection('depoimentos')}
              fontSize="sm"
              fontWeight="medium"
              color="gray.700"
              _hover={{ color: 'brand.500' }}
              cursor="pointer"
            >
              Depoimentos
            </Link>
            <Button
              size="sm"
              colorScheme="brand"
              onClick={() => navigate('/questionario')}
            >
              Começar Quiz
            </Button>
          </HStack>
        </Flex>
      </Box>
    </Box>
  )
}