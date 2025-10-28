// 🎨 UX + ✍️ Content Creator: Step 2 - Uso e Família
import {
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  SimpleGrid,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Switch,
  HStack,
  Box,
  Divider,
} from '@chakra-ui/react'
import {
  FaUsers,
  FaBriefcase,
  FaUmbrellaBeach,
  FaTruck,
  FaTaxi,
  FaGraduationCap,
} from 'react-icons/fa'
import { useQuestionnaireStore } from '@/store/questionnaireStore'
import { UsageProfileCard } from './UsageProfileCard'
import type { UsoPrincipal } from '@/types'

const USAGE_PROFILES = [
  {
    value: 'familia' as UsoPrincipal,
    icon: FaUsers,
    title: 'Família',
    description: 'Levar as crianças na escola, fazer compras e passear nos finais de semana',
  },
  {
    value: 'trabalho' as UsoPrincipal,
    icon: FaBriefcase,
    title: 'Trabalho',
    description: 'Ir e voltar do trabalho todos os dias, economizando combustível',
  },
  {
    value: 'lazer' as UsoPrincipal,
    icon: FaUmbrellaBeach,
    title: 'Lazer',
    description: 'Viajar, conhecer lugares novos e curtir aventuras',
  },
  {
    value: 'comercial' as UsoPrincipal,
    icon: FaTruck,
    title: 'Comercial',
    description: 'Transportar produtos, fazer entregas e trabalhar',
  },
  {
    value: 'transporte_passageiros' as UsoPrincipal,
    icon: FaTaxi,
    title: 'Uber/99',
    description: 'Trabalhar com transporte de passageiros (Uber, 99, táxi)',
  },
  {
    value: 'primeiro_carro' as UsoPrincipal,
    icon: FaGraduationCap,
    title: 'Primeiro Carro',
    description: 'Meu primeiro carro, fácil de dirigir e estacionar',
  },
]

export const Step2Usage = () => {
  const { formData, updateFormData } = useQuestionnaireStore()

  const handleProfileSelect = (value: UsoPrincipal) => {
    updateFormData({ uso_principal: value })
  }

  return (
    <VStack spacing={8} align="stretch" maxW="900px" mx="auto">
      {/* Header */}
      <VStack spacing={3} textAlign="center">
        <Heading size="lg" color="gray.800">
          Como você vai usar o carro? 🚗
        </Heading>
        <Text color="gray.600" fontSize="md" maxW="600px">
          Escolha a opção que melhor descreve o uso principal do seu carro
        </Text>
      </VStack>

      {/* Usage Profile Grid */}
      <FormControl isRequired>
        <SimpleGrid
          columns={{ base: 1, md: 2, lg: 3 }}
          spacing={4}
          role="radiogroup"
        >
          {USAGE_PROFILES.map((profile) => (
            <UsageProfileCard
              key={profile.value}
              icon={profile.icon}
              title={profile.title}
              description={profile.description}
              value={profile.value}
              isSelected={formData.uso_principal === profile.value}
              onClick={() => handleProfileSelect(profile.value)}
            />
          ))}
        </SimpleGrid>
      </FormControl>

      <Divider />

      {/* Composição Familiar */}
      <VStack spacing={6} align="stretch">
        <VStack spacing={2} align="flex-start">
          <Heading size="md" color="gray.800">
            👥 Quem vai usar o carro?
          </Heading>
          <Text fontSize="sm" color="gray.600">
            Isso nos ajuda a encontrar um carro com o tamanho certo
          </Text>
        </VStack>

        {/* Tamanho da Família */}
        <FormControl isRequired>
          <FormLabel fontSize="md" fontWeight="semibold">
            Quantas pessoas vão usar o carro regularmente?
          </FormLabel>
          <NumberInput
            value={formData.tamanho_familia || 1}
            onChange={(_, valueNumber) =>
              updateFormData({ tamanho_familia: valueNumber })
            }
            min={1}
            max={10}
            size="lg"
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        </FormControl>

        {/* Crianças */}
        <FormControl>
          <HStack justify="space-between" align="flex-start">
            <Box flex={1}>
              <FormLabel fontSize="md" fontWeight="semibold" mb={1}>
                Tem crianças?
              </FormLabel>
              <Text fontSize="sm" color="gray.600">
                Vamos priorizar carros com mais segurança e espaço para cadeirinhas
              </Text>
            </Box>
            <Switch
              size="lg"
              colorScheme="brand"
              isChecked={formData.tem_criancas || false}
              onChange={(e) =>
                updateFormData({ tem_criancas: e.target.checked })
              }
            />
          </HStack>
        </FormControl>

        {/* Idosos */}
        <FormControl>
          <HStack justify="space-between" align="flex-start">
            <Box flex={1}>
              <FormLabel fontSize="md" fontWeight="semibold" mb={1}>
                Tem idosos?
              </FormLabel>
              <Text fontSize="sm" color="gray.600">
                Vamos priorizar carros mais confortáveis e fáceis de entrar e sair
              </Text>
            </Box>
            <Switch
              size="lg"
              colorScheme="brand"
              isChecked={formData.tem_idosos || false}
              onChange={(e) =>
                updateFormData({ tem_idosos: e.target.checked })
              }
            />
          </HStack>
        </FormControl>
      </VStack>

      {/* Summary */}
      {formData.uso_principal && (
        <Box
          bg="brand.50"
          p={4}
          borderRadius="lg"
          borderWidth="2px"
          borderColor="brand.200"
        >
          <Text fontSize="sm" color="gray.700">
            <strong>Resumo:</strong> Carro para{' '}
            <strong>
              {USAGE_PROFILES.find((p) => p.value === formData.uso_principal)
                ?.title || 'uso geral'}
            </strong>
            , usado por <strong>{formData.tamanho_familia || 1} pessoa(s)</strong>
            {formData.tem_criancas && ', com crianças'}
            {formData.tem_idosos && ', com idosos'}
          </Text>
        </Box>
      )}
    </VStack>
  )
}


