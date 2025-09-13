import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';
import { Redis } from 'ioredis';

// Global test configuration
declare global {
  var __MONGO_URI__: string;
  var __MONGO_DB_NAME__: string;
  var __REDIS_INSTANCE__: Redis;
}

// Test database setup
export const setupTestDatabase = async (): Promise<void> => {
  const mongod = await MongoMemoryServer.create();
  const uri = mongod.getUri();
  global.__MONGO_URI__ = uri;
  global.__MONGO_DB_NAME__ = 'carmatch-test';
  
  await mongoose.connect(uri, {
    dbName: global.__MONGO_DB_NAME__,
  });
};

// Test database cleanup
export const teardownTestDatabase = async (): Promise<void> => {
  await mongoose.connection.dropDatabase();
  await mongoose.connection.close();
};

// Redis setup for tests
export const setupTestRedis = async (): Promise<void> => {
  const Redis = require('ioredis-mock');
  global.__REDIS_INSTANCE__ = new Redis();
};

// Clean up test data between tests
export const cleanupTestData = async (): Promise<void> => {
  const collections = mongoose.connection.collections;
  
  for (const key in collections) {
    const collection = collections[key];
    await collection.deleteMany({});
  }
  
  if (global.__REDIS_INSTANCE__) {
    await global.__REDIS_INSTANCE__.flushall();
  }
};

// Test data factories
export const createTestUser = (overrides = {}) => ({
  sessionId: 'test-session-123',
  criteria: {
    budget: { min: 50000, max: 80000 },
    location: { city: 'São Paulo', state: 'SP' },
    usage: { mainPurpose: 'familia', frequency: 'diaria' },
    family: { size: 4, hasChildren: true },
    priorities: {
      fuelEconomy: 4,
      safety: 5,
      reliability: 5,
      comfort: 4
    },
    preferences: {
      preferredBrands: ['Toyota', 'Honda'],
      vehicleTypes: ['sedan', 'suv']
    }
  },
  ...overrides
});

export const createTestCar = (overrides = {}) => ({
  marca: 'Toyota',
  modelo: 'Corolla',
  versao: 'XEI 2.0',
  ano: 2023,
  preco: {
    fipe: 125000,
    mercado: { min: 120000, max: 130000, medio: 125000 }
  },
  especificacoes: {
    tipo: 'sedan',
    categoria: 'premium',
    combustivel: 'Flex',
    motor: { cilindrada: 2.0, potencia: 177, torque: 213 },
    consumo: { cidade: 12.8, estrada: 15.2, combinado: 14.0 },
    dimensoes: { 
      comprimento: 4630, 
      largura: 1780, 
      altura: 1455, 
      portaMalas: 470, 
      entreEixos: 2700 
    },
    capacidades: { tanque: 60, lugares: 5, portas: 4 },
    transmissao: 'automatico',
    tracao: '4x2'
  },
  confiabilidade: {
    customanutencao: 'medio',
    problemas: [],
    recall: { quantidade: 0 },
    pecas: { disponibilidade: 'facil', preco: 'medio' }
  },
  mercado: {
    vendas: { ranking: 3, volume: 45000, participacao: 8.5 },
    depreciacao: { ano1: 15, ano3: 35, ano5: 55 },
    liquidez: 'alta',
    tempoMedioVenda: 25
  },
  disponibilidade: {
    regioes: ['SP', 'RJ', 'MG'],
    estoque: 'alto',
    prazoEntrega: 15
  },
  isActive: true,
  ...overrides
});

// Mock external services
export const mockExternalServices = () => {
  // Mock FIPE API
  jest.mock('../src/services/FipeService', () => ({
    FipeService: {
      getCarPrice: jest.fn().mockResolvedValue({ price: 125000, date: new Date() }),
      getBrandModels: jest.fn().mockResolvedValue([
        { codigo: '1', nome: 'Corolla' },
        { codigo: '2', nome: 'Civic' }
      ])
    }
  }));
  
  // Mock Email Service
  jest.mock('../src/services/EmailService', () => ({
    EmailService: {
      sendRecommendationEmail: jest.fn().mockResolvedValue(true),
      sendWelcomeEmail: jest.fn().mockResolvedValue(true)
    }
  }));
  
  // Mock Analytics Service
  jest.mock('../src/services/AnalyticsService', () => ({
    AnalyticsService: {
      trackEvent: jest.fn(),
      trackUserJourney: jest.fn()
    }
  }));
};

// Test assertions helpers
export const expectValidRecommendation = (recommendation: any) => {
  expect(recommendation).toHaveProperty('car');
  expect(recommendation).toHaveProperty('score');
  expect(recommendation).toHaveProperty('ranking');
  expect(recommendation).toHaveProperty('match');
  expect(recommendation).toHaveProperty('justification');
  
  expect(recommendation.score).toBeGreaterThan(0);
  expect(recommendation.score).toBeLessThanOrEqual(1);
  expect(recommendation.ranking).toBeGreaterThan(0);
  
  expect(recommendation.match).toHaveProperty('overall');
  expect(recommendation.match).toHaveProperty('categories');
  
  expect(recommendation.justification).toHaveProperty('summary');
  expect(recommendation.justification).toHaveProperty('strongPoints');
  expect(recommendation.justification).toHaveProperty('considerations');
};

export const expectValidCar = (car: any) => {
  expect(car).toHaveProperty('marca');
  expect(car).toHaveProperty('modelo');
  expect(car).toHaveProperty('ano');
  expect(car).toHaveProperty('preco');
  expect(car).toHaveProperty('especificacoes');
  expect(car).toHaveProperty('confiabilidade');
  expect(car).toHaveProperty('mercado');
  expect(car).toHaveProperty('disponibilidade');
  
  expect(car.ano).toBeGreaterThan(2010);
  expect(car.preco.fipe).toBeGreaterThan(0);
};

// Performance test helpers
export const measureExecutionTime = async (fn: Function): Promise<number> => {
  const start = Date.now();
  await fn();
  return Date.now() - start;
};

export const expectFastExecution = async (fn: Function, maxTime: number = 1000) => {
  const executionTime = await measureExecutionTime(fn);
  expect(executionTime).toBeLessThan(maxTime);
};

// Data validation helpers
export const validateApiResponse = (response: any) => {
  expect(response).toHaveProperty('success');
  
  if (response.success) {
    expect(response).toHaveProperty('data');
  } else {
    expect(response).toHaveProperty('error');
    expect(response.error).toHaveProperty('code');
    expect(response.error).toHaveProperty('message');
  }
  
  expect(response).toHaveProperty('metadata');
  expect(response.metadata).toHaveProperty('timestamp');
  expect(response.metadata).toHaveProperty('requestId');
};

// Environment setup
if (process.env.NODE_ENV !== 'test') {
  console.warn('Test setup loaded outside test environment');
}

// Increase timeout for async operations
jest.setTimeout(15000);
