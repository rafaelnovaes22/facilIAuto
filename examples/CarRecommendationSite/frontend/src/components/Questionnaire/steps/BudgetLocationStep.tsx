import React, { useState, useEffect } from 'react';
import {
  VStack,
  HStack,
  Text,
  Input,
  Select,
  Switch,
  FormControl,
  FormLabel,
  FormHelperText,
  Box,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  SliderMark,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Divider,
  Icon,
  Alert,
  AlertIcon,
  Grid,
  GridItem,
} from '@chakra-ui/react';
import { FiMapPin, FiDollarSign, FiCreditCard } from 'react-icons/fi';
import { QuestionnaireStepProps } from '../../../types';

// Brazilian states for location selection
const BRAZILIAN_STATES = [
  { value: 'AC', label: 'Acre' },
  { value: 'AL', label: 'Alagoas' },
  { value: 'AP', label: 'Amapá' },
  { value: 'AM', label: 'Amazonas' },
  { value: 'BA', label: 'Bahia' },
  { value: 'CE', label: 'Ceará' },
  { value: 'DF', label: 'Distrito Federal' },
  { value: 'ES', label: 'Espírito Santo' },
  { value: 'GO', label: 'Goiás' },
  { value: 'MA', label: 'Maranhão' },
  { value: 'MT', label: 'Mato Grosso' },
  { value: 'MS', label: 'Mato Grosso do Sul' },
  { value: 'MG', label: 'Minas Gerais' },
  { value: 'PA', label: 'Pará' },
  { value: 'PB', label: 'Paraíba' },
  { value: 'PR', label: 'Paraná' },
  { value: 'PE', label: 'Pernambuco' },
  { value: 'PI', label: 'Piauí' },
  { value: 'RJ', label: 'Rio de Janeiro' },
  { value: 'RN', label: 'Rio Grande do Norte' },
  { value: 'RS', label: 'Rio Grande do Sul' },
  { value: 'RO', label: 'Rondônia' },
  { value: 'RR', label: 'Roraima' },
  { value: 'SC', label: 'Santa Catarina' },
  { value: 'SP', label: 'São Paulo' },
  { value: 'SE', label: 'Sergipe' },
  { value: 'TO', label: 'Tocantins' },
];

const BudgetLocationStep: React.FC<QuestionnaireStepProps> = ({
  criteria,
  updateCriteria,
}) => {
  const [budgetRange, setBudgetRange] = useState<[number, number]>([
    criteria.budget?.min || 30000,
    criteria.budget?.max || 80000,
  ]);
  const [hasDownPayment, setHasDownPayment] = useState(
    criteria.budget?.hasDownPayment || false
  );
  const [downPaymentAmount, setDownPaymentAmount] = useState(
    criteria.budget?.downPaymentAmount || 10000
  );

  // Format currency for display
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Update criteria when values change
  useEffect(() => {
    updateCriteria({
      budget: {
        min: budgetRange[0],
        max: budgetRange[1],
        hasDownPayment,
        downPaymentAmount: hasDownPayment ? downPaymentAmount : undefined,
      },
    });
  }, [budgetRange, hasDownPayment, downPaymentAmount, updateCriteria]);

  const handleLocationChange = (field: string, value: string) => {
    updateCriteria({
      location: {
        ...criteria.location,
        [field]: value,
      },
    });
  };

  const handleBudgetRangeChange = (values: number[]) => {
    setBudgetRange([values[0], values[1]]);
  };

  const calculateMonthlyPayment = (totalValue: number, downPayment: number = 0): number => {
    const financed = totalValue - downPayment;
    const monthlyRate = 0.01; // 1% ao mês (estimativa)
    const months = 60; // 5 anos
    const payment = (financed * monthlyRate * Math.pow(1 + monthlyRate, months)) /
                   (Math.pow(1 + monthlyRate, months) - 1);
    return payment;
  };

  return (
    <VStack spacing={8} align="stretch">
      {/* Budget Section */}
      <Box>
        <HStack mb={4}>
          <Icon as={FiDollarSign} color="blue.500" boxSize={6} />
          <Text fontSize="xl" fontWeight="bold" color="gray.700">
            Qual seu orçamento?
          </Text>
        </HStack>

        <VStack spacing={6} align="stretch">
          {/* Budget Range Slider */}
          <FormControl>
            <FormLabel>Faixa de preço</FormLabel>
            <Box px={4} py={6}>
              <Slider
                min={20000}
                max={300000}
                step={5000}
                value={budgetRange}
                onChange={handleBudgetRangeChange}
                colorScheme="blue"
              >
                <SliderMark
                  value={budgetRange[0]}
                  textAlign="center"
                  bg="blue.500"
                  color="white"
                  mt="-10"
                  ml="-12"
                  w="24"
                  borderRadius="md"
                  fontSize="sm"
                  fontWeight="bold"
                  py={1}
                >
                  {formatCurrency(budgetRange[0])}
                </SliderMark>
                <SliderMark
                  value={budgetRange[1]}
                  textAlign="center"
                  bg="blue.500"
                  color="white"
                  mt="-10"
                  ml="-12"
                  w="24"
                  borderRadius="md"
                  fontSize="sm"
                  fontWeight="bold"
                  py={1}
                >
                  {formatCurrency(budgetRange[1])}
                </SliderMark>
                <SliderTrack bg="gray.100" h={2}>
                  <SliderFilledTrack bg="blue.400" />
                </SliderTrack>
                <SliderThumb boxSize={6} index={0} bg="blue.500" />
                <SliderThumb boxSize={6} index={1} bg="blue.500" />
              </Slider>
            </Box>
            <FormHelperText>
              Arraste para definir o valor mínimo e máximo que você pode investir
            </FormHelperText>
          </FormControl>

          {/* Down Payment */}
          <Box p={4} bg="gray.50" borderRadius="lg">
            <FormControl display="flex" alignItems="center" mb={4}>
              <FormLabel htmlFor="down-payment" mb="0" flex={1}>
                <HStack>
                  <Icon as={FiCreditCard} color="green.500" />
                  <Text>Você tem valor para entrada?</Text>
                </HStack>
              </FormLabel>
              <Switch
                id="down-payment"
                colorScheme="green"
                isChecked={hasDownPayment}
                onChange={(e) => setHasDownPayment(e.target.checked)}
              />
            </FormControl>

            {hasDownPayment && (
              <FormControl>
                <FormLabel>Valor da entrada</FormLabel>
                <NumberInput
                  value={downPaymentAmount}
                  onChange={(_, value) => setDownPaymentAmount(value)}
                  min={5000}
                  max={budgetRange[1] * 0.8}
                  step={1000}
                  format={formatCurrency}
                >
                  <NumberInputField placeholder="Ex: R$ 20.000" />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
                <FormHelperText>
                  Quanto maior a entrada, menor será a parcela do financiamento
                </FormHelperText>
              </FormControl>
            )}
          </Box>

          {/* Payment Estimation */}
          {budgetRange[1] > 0 && (
            <Alert status="info" borderRadius="lg">
              <AlertIcon />
              <Box>
                <Text fontWeight="bold">Estimativa de financiamento</Text>
                <Text fontSize="sm">
                  Parcela aproximada: {formatCurrency(
                    calculateMonthlyPayment(budgetRange[1], hasDownPayment ? downPaymentAmount : 0)
                  )}/mês
                  {hasDownPayment && (
                    <> • Entrada: {formatCurrency(downPaymentAmount)}</>
                  )}
                </Text>
              </Box>
            </Alert>
          )}
        </VStack>
      </Box>

      <Divider />

      {/* Location Section */}
      <Box>
        <HStack mb={4}>
          <Icon as={FiMapPin} color="blue.500" boxSize={6} />
          <Text fontSize="xl" fontWeight="bold" color="gray.700">
            Onde você está localizado?
          </Text>
        </HStack>

        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
          <GridItem>
            <FormControl isRequired>
              <FormLabel>Cidade</FormLabel>
              <Input
                placeholder="Ex: São Paulo, Belo Horizonte..."
                value={criteria.location?.city || ''}
                onChange={(e) => handleLocationChange('city', e.target.value)}
                size="lg"
              />
              <FormHelperText>
                Usamos para mostrar carros disponíveis na sua região
              </FormHelperText>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isRequired>
              <FormLabel>Estado</FormLabel>
              <Select
                placeholder="Selecione seu estado"
                value={criteria.location?.state || ''}
                onChange={(e) => handleLocationChange('state', e.target.value)}
                size="lg"
              >
                {BRAZILIAN_STATES.map((state) => (
                  <option key={state.value} value={state.value}>
                    {state.label}
                  </option>
                ))}
              </Select>
            </FormControl>
          </GridItem>
        </Grid>

        {criteria.location?.city && criteria.location?.state && (
          <Alert status="success" mt={4} borderRadius="lg">
            <AlertIcon />
            <Box>
              <Text fontWeight="bold">Localização confirmada</Text>
              <Text fontSize="sm">
                Buscando carros disponíveis em {criteria.location.city}, {criteria.location.state}
              </Text>
            </Box>
          </Alert>
        )}
      </Box>

      {/* Tips */}
      <Box p={4} bg="blue.50" borderRadius="lg" border="1px" borderColor="blue.100">
        <Text fontSize="sm" color="blue.700" mb={2}>
          <strong>💰 Dicas de orçamento:</strong>
        </Text>
        <VStack align="start" spacing={1}>
          <Text fontSize="xs" color="blue.600">
            • Considere custos extras: seguro, IPVA, manutenção
          </Text>
          <Text fontSize="xs" color="blue.600">
            • Parcela ideal: até 20-30% da sua renda mensal
          </Text>
          <Text fontSize="xs" color="blue.600">
            • Entrada maior = juros menores no financiamento
          </Text>
        </VStack>
      </Box>
    </VStack>
  );
};

export default BudgetLocationStep;
