// 🎨 UX Especialist + 💻 Tech Lead: Header com logo
import { Box, Image, HStack, Heading } from '@chakra-ui/react'

export default function Header() {
  return (
    <Box bg="white" boxShadow="md" position="sticky" top={0} zIndex={1000}>
      <Box maxW="container.xl" mx="auto" px={4} py={3}>
        <HStack spacing={4}>
          <Image 
            src="/src/assets/logo.png" 
            alt="FacilIAuto Logo" 
            height="40px" 
            width="auto" 
            objectFit="contain"
          />
          <Heading size="lg" color="brand.500">
            FacilIAuto
          </Heading>
        </HStack>
      </Box>
    </Box>
  )
}