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
  RadioGroup,
  Radio,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Button,
  Link,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
} from '@chakra-ui/react'
import {
  FaUsers,
  FaBriefcase,
  FaUmbrellaBeach,
  FaTruck,
  FaTaxi,
  FaGraduationCap,
  FaLock,
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
  const { isOpen, onOpen, onClose } = useDisclosure()

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

      <Divider />

      {/* Capacidade Financeira - OPCIONAL */}
      <VStack spacing={6} align="stretch">
        <VStack spacing={2} align="flex-start">
          <Heading size="md" color="gray.800">
            💰 Qual sua renda mensal? (Opcional)
          </Heading>
          <Text fontSize="sm" color="gray.600">
            Ajuda a mostrar quanto você vai gastar por mês e recomendar carros que cabem no seu bolso
          </Text>
        </VStack>

        {/* Privacy Badge */}
        <Alert status="info" borderRadius="md" variant="left-accent">
          <AlertIcon as={FaLock} />
          <Box flex={1}>
            <AlertTitle fontSize="sm">Seus dados são seguros e anônimos</AlertTitle>
            <AlertDescription fontSize="xs">
              Usamos apenas para calcular custos. Não salvamos ou compartilhamos.
            </AlertDescription>
          </Box>
        </Alert>

        {/* Income Range Selector */}
        <FormControl>
          <FormLabel fontSize="md" fontWeight="semibold">
            Qual sua renda mensal líquida (o que cai na conta)?
          </FormLabel>

          <RadioGroup
            value={formData.faixa_salarial || ''}
            onChange={(value) => updateFormData({ faixa_salarial: value === '' ? null : value })}
          >
            <VStack spacing={3} align="stretch">
              {/* Opção padrão - Não informar */}
              <Radio value="" size="lg">
                <Text fontWeight="semibold" color="gray.600">
                  Prefiro não informar
                </Text>
              </Radio>

              <Divider />

              <Radio value="0-3000" size="lg">
                <HStack justify="space-between" w="full">
                  <Text>Até R$ 3.000</Text>
                  <Text fontSize="xs" color="gray.500">
                    Custo até R$ 900/mês
                  </Text>
                </HStack>
              </Radio>

              <Radio value="3000-5000" size="lg">
                <HStack justify="space-between" w="full">
                  <Text>R$ 3.000 - R$ 5.000</Text>
                  <Text fontSize="xs" color="gray.500">
                    Custo até R$ 1.500/mês
                  </Text>
                </HStack>
              </Radio>

              <Radio value="5000-8000" size="lg">
                <HStack justify="space-between" w="full">
                  <Text>R$ 5.000 - R$ 8.000</Text>
                  <Text fontSize="xs" color="gray.500">
                    Custo até R$ 2.400/mês
                  </Text>
                </HStack>
              </Radio>

              <Radio value="8000-12000" size="lg">
                <HStack justify="space-between" w="full">
                  <Text>R$ 8.000 - R$ 12.000</Text>
                  <Text fontSize="xs" color="gray.500">
                    Custo até R$ 3.600/mês
                  </Text>
                </HStack>
              </Radio>

              <Radio value="12000+" size="lg">
                <HStack justify="space-between" w="full">
                  <Text>Acima de R$ 12.000</Text>
                  <Text fontSize="xs" color="gray.500">
                    Custo até R$ 5.000/mês
                  </Text>
                </HStack>
              </Radio>
            </VStack>
          </RadioGroup>
        </FormControl>

        {/* Privacy Link */}
        <Link
          fontSize="sm"
          color="blue.600"
          onClick={onOpen}
          cursor="pointer"
          textDecoration="underline"
        >
          🔒 Como usamos seus dados?
        </Link>
      </VStack>

      {/* Privacy Modal - LINGUAGEM SIMPLES */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>🔒 Como usamos sua renda mensal</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={5} align="stretch">
              {/* O que coletamos */}
              <Box>
                <Text fontWeight="bold" fontSize="md" mb={2}>
                  O que coletamos
                </Text>
                <Text fontSize="sm" color="gray.700">
                  Apenas sua <strong>faixa de renda</strong> (não o valor exato)
                </Text>
                <Text fontSize="sm" color="gray.600" mt={1}>
                  Exemplo: "R$ 5.000 - R$ 8.000"
                </Text>
              </Box>

              <Divider />

              {/* Como usamos */}
              <Box>
                <Text fontWeight="bold" fontSize="md" mb={3}>
                  Como usamos
                </Text>
                <VStack align="stretch" spacing={3}>
                  <HStack align="start">
                    <Text fontSize="lg">💰</Text>
                    <VStack align="start" spacing={0}>
                      <Text fontSize="sm" fontWeight="semibold">
                        Mostrar o custo real
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        Quanto você vai gastar por mês (parcela + combustível + seguro)
                      </Text>
                    </VStack>
                  </HStack>

                  <HStack align="start">
                    <Text fontSize="lg">✅</Text>
                    <VStack align="start" spacing={0}>
                      <Text fontSize="sm" fontWeight="semibold">
                        Recomendar carros que cabem no bolso
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        Evitar carros muito caros ou muito baratos para você
                      </Text>
                    </VStack>
                  </HStack>

                  <HStack align="start">
                    <Text fontSize="lg">📊</Text>
                    <VStack align="start" spacing={0}>
                      <Text fontSize="sm" fontWeight="semibold">
                        Melhorar para todo mundo
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        Seus dados (sem seu nome) ajudam a melhorar as recomendações
                      </Text>
                    </VStack>
                  </HStack>
                </VStack>
              </Box>

              <Divider />

              {/* O que NÃO fazemos */}
              <Box>
                <Text fontWeight="bold" fontSize="md" mb={2}>
                  O que NUNCA fazemos
                </Text>
                <VStack align="stretch" spacing={2}>
                  <HStack>
                    <Text color="red.500">❌</Text>
                    <Text fontSize="sm" color="gray.700">
                      Vender seus dados
                    </Text>
                  </HStack>
                  <HStack>
                    <Text color="red.500">❌</Text>
                    <Text fontSize="sm" color="gray.700">
                      Compartilhar com outras empresas
                    </Text>
                  </HStack>
                  <HStack>
                    <Text color="red.500">❌</Text>
                    <Text fontSize="sm" color="gray.700">
                      Enviar spam ou propaganda
                    </Text>
                  </HStack>
                  <HStack>
                    <Text color="red.500">❌</Text>
                    <Text fontSize="sm" color="gray.700">
                      Guardar junto com seu nome
                    </Text>
                  </HStack>
                </VStack>
              </Box>

              <Divider />

              {/* Segurança */}
              <Box bg="green.50" p={4} borderRadius="md">
                <HStack mb={2}>
                  <Text fontSize="lg">🛡️</Text>
                  <Text fontWeight="bold" fontSize="md" color="green.800">
                    Seus dados ficam seguros
                  </Text>
                </HStack>
                <VStack align="stretch" spacing={1}>
                  <Text fontSize="sm" color="green.900">
                    • Conexão criptografada (HTTPS)
                  </Text>
                  <Text fontSize="sm" color="green.900">
                    • Dados anônimos (sem seu nome)
                  </Text>
                  <Text fontSize="sm" color="green.900">
                    • Você pode pular esta pergunta
                  </Text>
                </VStack>
              </Box>

              {/* Footer */}
              <Text fontSize="xs" color="gray.500" textAlign="center">
                💡 Você pode mudar de ideia a qualquer momento
              </Text>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>

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


