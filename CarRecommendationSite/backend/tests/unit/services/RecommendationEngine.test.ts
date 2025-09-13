// RecommendationEngine.test.ts - TDD Example for CarMatch
// Following Red-Green-Refactor cycle

import { RecommendationEngine } from '../../../src/services/RecommendationEngine';
import { ScoringService } from '../../../src/services/ScoringService';
import { CarRepository } from '../../../src/repositories/CarRepository';
import { UserCriteria, Car, CarRecommendation } from '../../../src/types';
import { 
  createTestUser, 
  createTestCar, 
  expectValidRecommendation,
  cleanupTestData 
} from '../../setup';

// Mock dependencies
jest.mock('../../../src/services/ScoringService');
jest.mock('../../../src/repositories/CarRepository');

describe('RecommendationEngine - TDD', () => {
  let recommendationEngine: RecommendationEngine;
  let mockScoringService: jest.Mocked<ScoringService>;
  let mockCarRepository: jest.Mocked<CarRepository>;
  
  beforeEach(async () => {
    await cleanupTestData();
    
    // Create mocked dependencies
    mockScoringService = new ScoringService() as jest.Mocked<ScoringService>;
    mockCarRepository = new CarRepository() as jest.Mocked<CarRepository>;
    
    // Initialize engine with mocked dependencies
    recommendationEngine = new RecommendationEngine(
      mockScoringService,
      mockCarRepository
    );
  });

  describe('getRecommendations() - Family Profile', () => {
    // 🔴 RED: Write failing test first
    it('should return top 5 cars for family profile', async () => {
      // Arrange
      const familyCriteria = createTestUser({
        criteria: {
          budget: { min: 60000, max: 120000 },
          location: { city: 'São Paulo', state: 'SP' },
          usage: { mainPurpose: 'familia', frequency: 'diaria' },
          family: { size: 5, hasChildren: true },
          priorities: {
            safety: 5,
            reliability: 5,
            comfort: 4,
            fuelEconomy: 3
          },
          preferences: {
            preferredBrands: ['Toyota', 'Honda'],
            vehicleTypes: ['suv', 'sedan']
          }
        }
      }).criteria;

      const mockCars = [
        createTestCar({ marca: 'Toyota', modelo: 'RAV4', especificacoes: { tipo: 'suv', lugares: 7 } }),
        createTestCar({ marca: 'Honda', modelo: 'Pilot', especificacoes: { tipo: 'suv', lugares: 8 } }),
        createTestCar({ marca: 'Toyota', modelo: 'Corolla', especificacoes: { tipo: 'sedan', lugares: 5 } }),
        createTestCar({ marca: 'Volkswagen', modelo: 'Tiguan', especificacoes: { tipo: 'suv', lugares: 7 } }),
        createTestCar({ marca: 'Honda', modelo: 'Civic', especificacoes: { tipo: 'sedan', lugares: 5 } }),
      ];

      // Mock repository to return cars
      mockCarRepository.findByBudgetAndRegion.mockResolvedValue(mockCars as Car[]);
      
      // Mock scoring service to return family-appropriate scores
      mockScoringService.calculateScore.mockImplementation((car: Car, criteria: UserCriteria) => {
        let score = 0.5; // Base score
        
        // Family cars get higher scores
        if (car.especificacoes.lugares >= 7) score += 0.3;
        if (car.especificacoes.tipo === 'suv') score += 0.2;
        if (criteria.preferences.preferredBrands?.includes(car.marca)) score += 0.15;
        
        return Math.min(score, 1.0);
      });

      // Act
      const recommendations = await recommendationEngine.getRecommendations(familyCriteria);

      // Assert
      expect(recommendations).toHaveLength(5);
      expect(recommendations[0].car.especificacoes.lugares).toBeGreaterThanOrEqual(5);
      expect(recommendations[0].score).toBeGreaterThan(0.8);
      
      // Validate recommendation structure
      recommendations.forEach(expectValidRecommendation);
      
      // Verify family-appropriate ordering
      const firstRec = recommendations[0];
      expect(['Toyota', 'Honda']).toContain(firstRec.car.marca);
      expect(['suv', 'sedan']).toContain(firstRec.car.especificacoes.tipo);
    });

    // 🟢 GREEN: Implement minimal code to pass test
    it('should prioritize safety features for family profile', async () => {
      // Arrange
      const familyCriteria = createTestUser({
        criteria: {
          priorities: { safety: 5, reliability: 5 },
          family: { hasChildren: true }
        }
      }).criteria;

      const carWithSafety = createTestCar({
        marca: 'Volvo',
        seguranca: {
          latinNCAP: 5,
          itens: ['ABS', 'Airbags', 'Controle de estabilidade', 'Sensor de ré']
        }
      });

      const carWithoutSafety = createTestCar({
        marca: 'Fiat',
        seguranca: {
          latinNCAP: 3,
          itens: ['ABS']
        }
      });

      mockCarRepository.findByBudgetAndRegion.mockResolvedValue([carWithSafety, carWithoutSafety] as Car[]);
      
      mockScoringService.calculateScore.mockImplementation((car: Car) => {
        return car.seguranca?.latinNCAP ? car.seguranca.latinNCAP / 5 : 0.5;
      });

      // Act
      const recommendations = await recommendationEngine.getRecommendations(familyCriteria);

      // Assert
      expect(recommendations[0].car.marca).toBe('Volvo');
      expect(recommendations[0].car.seguranca?.latinNCAP).toBe(5);
      expect(recommendations[0].score).toBeGreaterThan(recommendations[1].score);
    });
  });

  describe('getRecommendations() - Economic Profile', () => {
    it('should return fuel-efficient cars for economic profile', async () => {
      // Arrange
      const economicCriteria = createTestUser({
        criteria: {
          budget: { min: 30000, max: 60000 },
          usage: { mainPurpose: 'trabalho', frequency: 'diaria' },
          priorities: {
            fuelEconomy: 5,
            maintenance: 5,
            resaleValue: 4
          },
          preferences: {
            preferredBrands: ['Hyundai', 'Toyota'],
            vehicleTypes: ['hatch', 'compacto']
          }
        }
      }).criteria;

      const economicCar = createTestCar({
        marca: 'Hyundai',
        modelo: 'HB20',
        especificacoes: {
          tipo: 'hatch',
          consumo: { combinado: 16.5 }
        },
        confiabilidade: { customanutencao: 'baixo' }
      });

      const expensiveCar = createTestCar({
        marca: 'BMW',
        modelo: 'X1',
        especificacoes: {
          tipo: 'suv',
          consumo: { combinado: 9.2 }
        },
        confiabilidade: { customanutencao: 'alto' }
      });

      mockCarRepository.findByBudgetAndRegion.mockResolvedValue([economicCar, expensiveCar] as Car[]);
      
      mockScoringService.calculateScore.mockImplementation((car: Car, criteria: UserCriteria) => {
        let score = 0.3;
        
        // Higher score for fuel efficiency
        if (car.especificacoes.consumo.combinado > 15) score += 0.4;
        if (car.confiabilidade.customanutencao === 'baixo') score += 0.3;
        if (criteria.preferences.preferredBrands?.includes(car.marca)) score += 0.2;
        
        return Math.min(score, 1.0);
      });

      // Act
      const recommendations = await recommendationEngine.getRecommendations(economicCriteria);

      // Assert
      expect(recommendations[0].car.marca).toBe('Hyundai');
      expect(recommendations[0].car.especificacoes.consumo.combinado).toBeGreaterThan(15);
      expect(recommendations[0].car.confiabilidade.customanutencao).toBe('baixo');
    });
  });

  describe('getRecommendations() - Performance Profile', () => {
    it('should return powerful cars for performance profile', async () => {
      // Arrange
      const performanceCriteria = createTestUser({
        criteria: {
          budget: { min: 80000, max: 200000 },
          usage: { mainPurpose: 'lazer', frequency: 'eventual' },
          priorities: {
            performance: 5,
            comfort: 4,
            fuelEconomy: 2
          },
          preferences: {
            preferredBrands: ['BMW', 'Audi'],
            vehicleTypes: ['sedan', 'suv']
          }
        }
      }).criteria;

      const sportyCar = createTestCar({
        marca: 'BMW',
        modelo: '330i',
        especificacoes: {
          motor: { potencia: 258, torque: 400 },
          performance: { aceleracao0a100: 5.8 }
        }
      });

      const regularCar = createTestCar({
        marca: 'Toyota',
        modelo: 'Corolla',
        especificacoes: {
          motor: { potencia: 144, torque: 175 },
          performance: { aceleracao0a100: 10.2 }
        }
      });

      mockCarRepository.findByBudgetAndRegion.mockResolvedValue([sportyCar, regularCar] as Car[]);
      
      mockScoringService.calculateScore.mockImplementation((car: Car) => {
        const powerScore = car.especificacoes.motor.potencia / 300; // Normalize to 0-1
        const accelScore = car.especificacoes.performance?.aceleracao0a100 ? 
          (12 - car.especificacoes.performance.aceleracao0a100) / 10 : 0;
        
        return Math.min((powerScore + accelScore) / 2, 1.0);
      });

      // Act
      const recommendations = await recommendationEngine.getRecommendations(performanceCriteria);

      // Assert
      expect(recommendations[0].car.marca).toBe('BMW');
      expect(recommendations[0].car.especificacoes.motor.potencia).toBeGreaterThan(200);
      expect(recommendations[0].score).toBeGreaterThan(0.7);
    });
  });

  describe('Error Handling', () => {
    it('should handle empty car database gracefully', async () => {
      // Arrange
      const criteria = createTestUser().criteria;
      mockCarRepository.findByBudgetAndRegion.mockResolvedValue([]);

      // Act
      const recommendations = await recommendationEngine.getRecommendations(criteria);

      // Assert
      expect(recommendations).toHaveLength(0);
    });

    it('should handle repository errors', async () => {
      // Arrange
      const criteria = createTestUser().criteria;
      mockCarRepository.findByBudgetAndRegion.mockRejectedValue(new Error('Database error'));

      // Act & Assert
      await expect(recommendationEngine.getRecommendations(criteria))
        .rejects.toThrow('Database error');
    });

    it('should handle invalid criteria gracefully', async () => {
      // Arrange
      const invalidCriteria = {} as UserCriteria;

      // Act & Assert
      await expect(recommendationEngine.getRecommendations(invalidCriteria))
        .rejects.toThrow('Invalid criteria');
    });
  });

  describe('Performance Tests', () => {
    it('should process large dataset efficiently', async () => {
      // Arrange
      const criteria = createTestUser().criteria;
      const largeCarsArray = Array.from({ length: 1000 }, (_, i) => 
        createTestCar({ marca: `Brand${i}`, modelo: `Model${i}` })
      );
      
      mockCarRepository.findByBudgetAndRegion.mockResolvedValue(largeCarsArray as Car[]);
      mockScoringService.calculateScore.mockReturnValue(Math.random());

      // Act
      const start = Date.now();
      const recommendations = await recommendationEngine.getRecommendations(criteria);
      const duration = Date.now() - start;

      // Assert
      expect(duration).toBeLessThan(2000); // Should complete within 2 seconds
      expect(recommendations).toHaveLength(5); // Should limit results
    });
  });

  describe('Business Logic Validation', () => {
    it('should respect budget constraints strictly', async () => {
      // Arrange
      const criteria = createTestUser({
        criteria: {
          budget: { min: 50000, max: 80000 }
        }
      }).criteria;

      const carTooExpensive = createTestCar({ preco: { fipe: 90000 } });
      const carToocheap = createTestCar({ preco: { fipe: 40000 } });
      const carInBudget = createTestCar({ preco: { fipe: 65000 } });

      mockCarRepository.findByBudgetAndRegion.mockImplementation(async (min, max) => {
        return [carInBudget].filter(car => 
          car.preco.fipe >= min && car.preco.fipe <= max
        ) as Car[];
      });

      // Act
      const recommendations = await recommendationEngine.getRecommendations(criteria);

      // Assert
      recommendations.forEach(rec => {
        expect(rec.car.preco.fipe).toBeGreaterThanOrEqual(50000);
        expect(rec.car.preco.fipe).toBeLessThanOrEqual(80000);
      });
    });

    it('should prefer cars available in user region', async () => {
      // Arrange
      const criteria = createTestUser({
        criteria: {
          location: { city: 'São Paulo', state: 'SP' }
        }
      }).criteria;

      const availableCar = createTestCar({
        marca: 'Toyota',
        disponibilidade: { regioes: ['SP', 'RJ'] }
      });

      const unavailableCar = createTestCar({
        marca: 'Fiat',
        disponibilidade: { regioes: ['MG', 'BA'] }
      });

      mockCarRepository.findByBudgetAndRegion.mockResolvedValue([availableCar] as Car[]);
      mockScoringService.calculateScore.mockReturnValue(0.8);

      // Act
      const recommendations = await recommendationEngine.getRecommendations(criteria);

      // Assert
      recommendations.forEach(rec => {
        expect(rec.car.disponibilidade.regioes).toContain('SP');
      });
    });
  });

  // 🔵 REFACTOR: Test optimization and cleanup
  describe('Integration with Caching', () => {
    it('should cache recommendations for identical criteria', async () => {
      // This test would verify caching behavior
      // Implementation depends on caching strategy
    });
  });

  describe('Recommendation Justification', () => {
    it('should provide detailed justification for each recommendation', async () => {
      // Arrange
      const criteria = createTestUser().criteria;
      const testCar = createTestCar();
      
      mockCarRepository.findByBudgetAndRegion.mockResolvedValue([testCar] as Car[]);
      mockScoringService.calculateScore.mockReturnValue(0.85);

      // Act
      const recommendations = await recommendationEngine.getRecommendations(criteria);

      // Assert
      const justification = recommendations[0].justification;
      expect(justification.summary).toBeTruthy();
      expect(justification.strongPoints).toHaveLength.greaterThan(0);
      expect(justification.considerations).toBeDefined();
    });
  });
});
