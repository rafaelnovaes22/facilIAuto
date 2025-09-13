import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Progress,
  FormControl,
  FormLabel,
  Input,
  Select,
  Checkbox,
  CheckboxGroup,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  SliderMark,
  Radio,
  RadioGroup,
  Stack,
  Alert,
  AlertIcon,
  useToast,
  Spinner
} from '@chakra-ui/react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

interface FormData {
  orcamento_min: number
  orcamento_max: number
  uso_principal: string
  tamanho_familia: number
  prioridades: {
    economia: number
    espaco: number
    performance: number
    conforto: number
    seguranca: number
  }
  marcas_preferidas: string[]
  tipos_preferidos: string[]
  combustivel_preferido: string
  idade_usuario: number
  experiencia_conducao: string
}

const QuestionnairePage = () => {
  const navigate = useNavigate()
  const toast = useToast()
  const [currentStep, setCurrentStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const totalSteps = 6

  const [formData, setFormData] = useState<FormData>({
    orcamento_min: 30000,
    orcamento_max: 100000,
    uso_principal: '',
    tamanho_familia: 2,
    prioridades: {
      economia: 3,
      espaco: 3,
      performance: 3,
      conforto: 3,
      seguranca: 5
    },
    marcas_preferidas: [],
    tipos_preferidos: [],
    combustivel_preferido: '',
    idade_usuario: 30,
    experiencia_conducao: ''
  })

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    } else {
      handleSubmit()
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    setIsLoading(true)
    try {
      // Simular chamada à API
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Armazenar dados para a página de resultados
      localStorage.setItem('questionario_data', JSON.stringify(formData))
      
      toast({
        title: "✅ Questionário Concluído!",
        description: "Gerando suas recomendações personalizadas...",
        status: "success",
        duration: 3000,
        isClosable: true,
      })

      navigate('/resultados')
    } catch (error) {
      toast({
        title: "❌ Erro",
        description: "Houve um problema ao processar suas respostas.",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const updateFormData = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const updatePrioridade = (tipo: string, valor: number) => {
    setFormData(prev => ({
      ...prev,
      prioridades: {
        ...prev.prioridades,
        [tipo]: valor
      }
    }))
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <VStack spacing={6} align="stretch">
            <Box textAlign="center">
              <Heading size="lg">💰 Qual seu orçamento?</Heading>
              <Text color="gray.600" mt={2}>
                Defina a faixa de preço que você está considerando
              </Text>
            </Box>

            <FormControl>
              <FormLabel>Orçamento Mínimo: R$ {formData.orcamento_min.toLocaleString()}</FormLabel>
              <Slider
                value={formData.orcamento_min}
                onChange={(val) => updateFormData('orcamento_min', val)}
                min={20000}
                max={200000}
                step={5000}
                colorScheme="blue"
              >
                <SliderMark value={20000} mt="1" ml="-2.5" fontSize="sm">R$ 20k</SliderMark>
                <SliderMark value={100000} mt="1" ml="-2.5" fontSize="sm">R$ 100k</SliderMark>
                <SliderMark value={200000} mt="1" ml="-2.5" fontSize="sm">R$ 200k</SliderMark>
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
            </FormControl>

            <FormControl mt={8}>
              <FormLabel>Orçamento Máximo: R$ {formData.orcamento_max.toLocaleString()}</FormLabel>
              <Slider
                value={formData.orcamento_max}
                onChange={(val) => updateFormData('orcamento_max', val)}
                min={formData.orcamento_min}
                max={250000}
                step={5000}
                colorScheme="blue"
              >
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
            </FormControl>

            {formData.orcamento_max <= formData.orcamento_min && (
              <Alert status="warning">
                <AlertIcon />
                O orçamento máximo deve ser maior que o mínimo
              </Alert>
            )}
          </VStack>
        )

      case 2:
        return (
          <VStack spacing={6} align="stretch">
            <Box textAlign="center">
              <Heading size="lg">🎯 Para que você usará o carro?</Heading>
              <Text color="gray.600" mt={2}>
                Isso nos ajuda a encontrar o carro ideal para seu estilo de vida
              </Text>
            </Box>

            <RadioGroup
              value={formData.uso_principal}
              onChange={(val) => updateFormData('uso_principal', val)}
            >
              <Stack spacing={4}>
                <Radio value="trabalho" size="lg">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">🏢 Trabalho/Commuting</Text>
                    <Text fontSize="sm" color="gray.600">Ir e voltar do trabalho, reuniões</Text>
                  </VStack>
                </Radio>
                <Radio value="familia" size="lg">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">👨‍👩‍👧‍👦 Família</Text>
                    <Text fontSize="sm" color="gray.600">Transportar família, viagens, escola</Text>
                  </VStack>
                </Radio>
                <Radio value="lazer" size="lg">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">🌴 Lazer/Viagens</Text>
                    <Text fontSize="sm" color="gray.600">Fins de semana, viagens, hobby</Text>
                  </VStack>
                </Radio>
                <Radio value="primeiro_carro" size="lg">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">🚗 Primeiro Carro</Text>
                    <Text fontSize="sm" color="gray.600">Aprendendo a dirigir, economia</Text>
                  </VStack>
                </Radio>
              </Stack>
            </RadioGroup>

            <FormControl>
              <FormLabel>👥 Quantas pessoas costumam andar no carro?</FormLabel>
              <Select
                value={formData.tamanho_familia}
                onChange={(e) => updateFormData('tamanho_familia', parseInt(e.target.value))}
              >
                <option value={1}>Só eu</option>
                <option value={2}>2 pessoas</option>
                <option value={3}>3 pessoas</option>
                <option value={4}>4 pessoas</option>
                <option value={5}>5+ pessoas</option>
              </Select>
            </FormControl>
          </VStack>
        )

      case 3:
        return (
          <VStack spacing={6} align="stretch">
            <Box textAlign="center">
              <Heading size="lg">⭐ O que é mais importante para você?</Heading>
              <Text color="gray.600" mt={2}>
                Dê uma nota de 1 a 5 para cada aspecto
              </Text>
            </Box>

            <VStack spacing={6}>
              {Object.entries({
                economia: { label: '💰 Economia', desc: 'Baixo consumo, manutenção barata' },
                espaco: { label: '📦 Espaço', desc: 'Porta-malas, espaço interno' },
                performance: { label: '🏎️ Performance', desc: 'Potência, acelerar' },
                conforto: { label: '🛋️ Conforto', desc: 'Bancos, ar-condicionado, silêncio' },
                seguranca: { label: '🛡️ Segurança', desc: 'Airbags, freios, estabilidade' }
              }).map(([key, {label, desc}]) => (
                <FormControl key={key}>
                  <FormLabel>
                    <VStack align="start" spacing={1}>
                      <Text>{label}</Text>
                      <Text fontSize="sm" color="gray.600">{desc}</Text>
                    </VStack>
                  </FormLabel>
                  <Slider
                    value={formData.prioridades[key as keyof typeof formData.prioridades]}
                    onChange={(val) => updatePrioridade(key, val)}
                    min={1}
                    max={5}
                    step={1}
                    colorScheme="blue"
                  >
                    <SliderMark value={1} mt="1" ml="-2.5" fontSize="sm">1</SliderMark>
                    <SliderMark value={3} mt="1" ml="-2.5" fontSize="sm">3</SliderMark>
                    <SliderMark value={5} mt="1" ml="-2.5" fontSize="sm">5</SliderMark>
                    <SliderTrack>
                      <SliderFilledTrack />
                    </SliderTrack>
                    <SliderThumb />
                  </Slider>
                </FormControl>
              ))}
            </VStack>
          </VStack>
        )

      case 4:
        return (
          <VStack spacing={6} align="stretch">
            <Box textAlign="center">
              <Heading size="lg">🏭 Tem preferência de marca?</Heading>
              <Text color="gray.600" mt={2}>
                Selecione as marcas que você considera (opcional)
              </Text>
            </Box>

            <CheckboxGroup
              value={formData.marcas_preferidas}
              onChange={(val) => updateFormData('marcas_preferidas', val)}
            >
              <Stack spacing={3}>
                {[
                  'Chevrolet', 'Fiat', 'Ford', 'Volkswagen', 'Toyota', 
                  'Honda', 'Hyundai', 'Nissan', 'Renault', 'Peugeot'
                ].map(marca => (
                  <Checkbox key={marca} value={marca} size="lg">
                    {marca}
                  </Checkbox>
                ))}
              </Stack>
            </CheckboxGroup>

            <Alert status="info">
              <AlertIcon />
              Se não selecionar nenhuma, mostraremos todas as opções disponíveis
            </Alert>
          </VStack>
        )

      case 5:
        return (
          <VStack spacing={6} align="stretch">
            <Box textAlign="center">
              <Heading size="lg">🚗 Que tipo de carro prefere?</Heading>
              <Text color="gray.600" mt={2}>
                Escolha os modelos que mais combinam com você
              </Text>
            </Box>

            <CheckboxGroup
              value={formData.tipos_preferidos}
              onChange={(val) => updateFormData('tipos_preferidos', val)}
            >
              <Stack spacing={4}>
                <Checkbox value="hatch" size="lg">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">🚙 Hatch</Text>
                    <Text fontSize="sm" color="gray.600">Compacto, ágil, estacionamento fácil</Text>
                  </VStack>
                </Checkbox>
                <Checkbox value="sedan" size="lg">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">🚘 Sedan</Text>
                    <Text fontSize="sm" color="gray.600">Elegante, porta-malas grande, conforto</Text>
                  </VStack>
                </Checkbox>
                <Checkbox value="suv" size="lg">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">🚜 SUV</Text>
                    <Text fontSize="sm" color="gray.600">Alto, espaçoso, visão elevada</Text>
                  </VStack>
                </Checkbox>
                <Checkbox value="pickup" size="lg">
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">🛻 Pickup</Text>
                    <Text fontSize="sm" color="gray.600">Robusta, carga, trabalho</Text>
                  </VStack>
                </Checkbox>
              </Stack>
            </CheckboxGroup>

            <FormControl>
              <FormLabel>⛽ Preferência de combustível</FormLabel>
              <RadioGroup
                value={formData.combustivel_preferido}
                onChange={(val) => updateFormData('combustivel_preferido', val)}
              >
                <Stack>
                  <Radio value="flex">Flex (Gasolina/Etanol)</Radio>
                  <Radio value="gasolina">Gasolina</Radio>
                  <Radio value="diesel">Diesel</Radio>
                  <Radio value="hibrido">Híbrido</Radio>
                  <Radio value="indiferente">Tanto faz</Radio>
                </Stack>
              </RadioGroup>
            </FormControl>
          </VStack>
        )

      case 6:
        return (
          <VStack spacing={6} align="stretch">
            <Box textAlign="center">
              <Heading size="lg">👤 Informações finais</Heading>
              <Text color="gray.600" mt={2}>
                Últimos detalhes para personalizar sua recomendação
              </Text>
            </Box>

            <FormControl>
              <FormLabel>🎂 Sua idade</FormLabel>
              <Input
                type="number"
                value={formData.idade_usuario}
                onChange={(e) => updateFormData('idade_usuario', parseInt(e.target.value))}
                min={18}
                max={100}
              />
            </FormControl>

            <FormControl>
              <FormLabel>🚗 Experiência com carros</FormLabel>
              <RadioGroup
                value={formData.experiencia_conducao}
                onChange={(val) => updateFormData('experiencia_conducao', val)}
              >
                <Stack>
                  <Radio value="iniciante">
                    <VStack align="start" spacing={1}>
                      <Text>🌱 Iniciante</Text>
                      <Text fontSize="sm" color="gray.600">Acabei de tirar carteira</Text>
                    </VStack>
                  </Radio>
                  <Radio value="intermediario">
                    <VStack align="start" spacing={1}>
                      <Text>🚗 Intermediário</Text>
                      <Text fontSize="sm" color="gray.600">Dirijo há alguns anos</Text>
                    </VStack>
                  </Radio>
                  <Radio value="experiente">
                    <VStack align="start" spacing={1}>
                      <Text>🏎️ Experiente</Text>
                      <Text fontSize="sm" color="gray.600">Muito tempo de estrada</Text>
                    </VStack>
                  </Radio>
                </Stack>
              </RadioGroup>
            </FormControl>

            <Alert status="success">
              <AlertIcon />
              Pronto! Vamos gerar suas recomendações personalizadas baseadas no estoque da RobustCar.
            </Alert>
          </VStack>
        )

      default:
        return null
    }
  }

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return formData.orcamento_max > formData.orcamento_min
      case 2:
        return formData.uso_principal !== ''
      case 6:
        return formData.experiencia_conducao !== ''
      default:
        return true
    }
  }

  return (
    <Box py={8}>
      <Container maxW="container.md">
        <VStack spacing={8}>
          {/* Header */}
          <Box textAlign="center">
            <Heading size="xl" color="blue.600">
              🎯 Questionário Personalizado
            </Heading>
            <Text color="gray.600" mt={2}>
              Responda algumas perguntas para encontrarmos o carro perfeito para você
            </Text>
          </Box>

          {/* Progress */}
          <Box w="full">
            <Text fontSize="sm" color="gray.600" mb={2}>
              Etapa {currentStep} de {totalSteps}
            </Text>
            <Progress value={(currentStep / totalSteps) * 100} colorScheme="blue" />
          </Box>

          {/* Content */}
          <Box w="full" minH="400px">
            {renderStep()}
          </Box>

          {/* Navigation */}
          <HStack w="full" justify="space-between">
            <Button
              variant="outline"
              onClick={handlePrevious}
              isDisabled={currentStep === 1}
            >
              ← Anterior
            </Button>

            <Button
              colorScheme="blue"
              onClick={handleNext}
              isDisabled={!isStepValid()}
              isLoading={isLoading}
              spinner={<Spinner />}
            >
              {currentStep === totalSteps ? '🚀 Gerar Recomendações' : 'Próximo →'}
            </Button>
          </HStack>
        </VStack>
      </Container>
    </Box>
  )
}

export default QuestionnairePage
