// CarMatch - Types & Interfaces

export interface UserCriteria {
  // Orçamento e localização
  budget: {
    min: number;
    max: number;
    hasDownPayment: boolean;
    downPaymentAmount?: number;
  };
  location: {
    city: string;
    state: string;
    zipCode?: string;
  };

  // Perfil de uso
  usage: {
    mainPurpose: 'trabalho' | 'familia' | 'lazer' | 'comercial';
    frequency: 'diaria' | 'regular' | 'eventual';
    typicalDistance: 'cidade' | 'misto' | 'estrada';
  };

  // Necessidades familiares
  family: {
    size: number;
    hasChildren: boolean;
    childrenAges?: number[];
    hasElderly: boolean;
    needsAccessibility: boolean;
  };

  // Espaço e bagagem
  space: {
    trunkSize: 'pequeno' | 'medio' | 'grande';
    passengerPriority: 'conforto' | 'espaco' | 'performance';
    cargoNeeds: string[];
  };

  // Prioridades técnicas (1-5 scale)
  priorities: {
    fuelEconomy: number;
    performance: number;
    reliability: number;
    resaleValue: number;
    maintenance: number;
    safety: number;
    comfort: number;
    technology: number;
  };

  // Preferências pessoais
  preferences: {
    preferredBrands: string[];
    rejectedBrands: string[];
    vehicleTypes: ('hatch' | 'sedan' | 'suv' | 'pickup' | 'compacto')[];
    fuelType: ('flex' | 'gasolina' | 'etanol' | 'diesel' | 'hibrido' | 'eletrico')[];
    transmission: ('manual' | 'automatico' | 'cvt')[];
    maxAge: number; // anos
  };
}

export interface Car {
  _id: string;
  marca: string;
  modelo: string;
  versao: string;
  ano: number;
  
  preco: {
    fipe: number;
    mercado: {
      min: number;
      max: number;
      medio: number;
    };
    financiamento: {
      entradaMinima: number;
      parcelaEstimada: number;
    };
  };

  especificacoes: {
    tipo: 'hatch' | 'sedan' | 'suv' | 'pickup' | 'compacto';
    categoria: 'popular' | 'premium' | 'luxo' | 'esportivo';
    combustivel: string;
    motor: {
      cilindrada: number;
      potencia: number;
      torque: number;
    };
    consumo: {
      cidade: number;
      estrada: number;
      combinado: number;
    };
    performance: {
      aceleracao0a100?: number;
      velocidadeMaxima?: number;
    };
    dimensoes: {
      comprimento: number;
      largura: number;
      altura: number;
      portaMalas: number;
      entreEixos: number;
    };
    capacidades: {
      tanque: number;
      lugares: number;
      portas: number;
    };
    transmissao: 'manual' | 'automatico' | 'cvt';
    tracao: '4x2' | '4x4';
  };

  confiabilidade: {
    notaJDPower?: number;
    customanutencao: 'baixo' | 'medio' | 'alto';
    problemas: string[];
    recall: {
      quantidade: number;
      ultimoAno?: number;
    };
    pecas: {
      disponibilidade: 'facil' | 'moderada' | 'dificil';
      preco: 'baixo' | 'medio' | 'alto';
    };
  };

  mercado: {
    vendas: {
      ranking: number;
      volume: number;
      participacao: number;
    };
    depreciacao: {
      ano1: number;
      ano3: number;
      ano5: number;
    };
    liquidez: 'alta' | 'media' | 'baixa';
    tempoMedioVenda: number; // dias
  };

  disponibilidade: {
    regioes: string[];
    concessionarias: string[];
    estoque: 'baixo' | 'medio' | 'alto';
    prazoEntrega: number; // dias
  };

  seguranca: {
    latinNCAP?: number;
    iihsRating?: string;
    itens: string[];
  };

  imagens: {
    principal: string;
    galeria: string[];
    cores: Array<{
      nome: string;
      hex: string;
      imagem: string;
    }>;
  };

  reviews: {
    especialistas: {
      nota: number;
      fonte: string;
      pontos: {
        positivos: string[];
        negativos: string[];
      };
    }[];
    usuarios: {
      nota: number;
      totalAvaliacoes: number;
      distribuicao: {
        5: number;
        4: number;
        3: number;
        2: number;
        1: number;
      };
    };
  };
}

export interface CarRecommendation {
  car: Car;
  score: number;
  ranking: number;
  
  match: {
    overall: number; // 0-100
    categories: {
      budget: number;
      usage: number;
      space: number;
      priorities: number;
      preferences: number;
    };
  };

  justification: {
    summary: string;
    strongPoints: Array<{
      category: string;
      description: string;
      impact: 'alto' | 'medio' | 'baixo';
    }>;
    considerations: Array<{
      category: string;
      description: string;
      impact: 'alto' | 'medio' | 'baixo';
    }>;
    dealBreakers?: Array<{
      issue: string;
      severity: 'critico' | 'alto' | 'medio';
    }>;
  };

  alternatives: {
    upgrade?: string; // car._id
    downgrade?: string; // car._id
    similar: string[]; // car._id[]
  };

  financing: {
    downPayment: number;
    monthlyPayment: number;
    totalInterest: number;
    term: number; // meses
  };
}

export interface UserSession {
  sessionId: string;
  timestamp: Date;
  status: 'started' | 'in_progress' | 'completed' | 'abandoned';
  
  progress: {
    currentStep: number;
    totalSteps: number;
    completedSteps: string[];
  };

  criteria?: UserCriteria;
  recommendations?: CarRecommendation[];
  
  interactions: Array<{
    type: 'step_completed' | 'car_viewed' | 'comparison_made' | 'favorite_added';
    timestamp: Date;
    data: any;
  }>;

  metadata: {
    userAgent: string;
    device: 'mobile' | 'tablet' | 'desktop';
    referrer?: string;
    utm?: {
      source?: string;
      medium?: string;
      campaign?: string;
    };
  };
}

export interface QuestionnaireStep {
  id: string;
  title: string;
  subtitle?: string;
  component: React.ComponentType<any>;
  validation?: (data: any) => boolean;
  optional?: boolean;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    timestamp: string;
    version: string;
    requestId: string;
  };
}

export interface RecommendationRequest {
  sessionId: string;
  criteria: UserCriteria;
  options?: {
    maxResults?: number;
    includeAlternatives?: boolean;
    includeFinancing?: boolean;
  };
}

export interface RecommendationResponse {
  sessionId: string;
  recommendations: CarRecommendation[];
  metadata: {
    totalCarsAnalyzed: number;
    processingTime: number;
    algorithmVersion: string;
    filters: {
      priceRange: [number, number];
      availability: string[];
      excluded: number;
    };
  };
  insights?: {
    marketTrends: string[];
    userProfile: string;
    suggestions: string[];
  };
}

// Store/State Types
export interface AppState {
  session: UserSession | null;
  criteria: Partial<UserCriteria>;
  recommendations: CarRecommendation[];
  
  ui: {
    loading: boolean;
    currentStep: number;
    error: string | null;
    theme: 'light' | 'dark';
  };

  // Actions
  updateCriteria: (criteria: Partial<UserCriteria>) => void;
  nextStep: () => void;
  previousStep: () => void;
  submitQuestionnaire: () => Promise<void>;
  loadRecommendations: () => Promise<void>;
  resetSession: () => void;
}

// Utility Types
export type BrandLogos = Record<string, string>;
export type VehicleTypeIcons = Record<string, React.ComponentType>;
export type PriorityWeights = Record<keyof UserCriteria['priorities'], number>;

// Component Props
export interface QuestionnaireStepProps {
  criteria: Partial<UserCriteria>;
  updateCriteria: (update: Partial<UserCriteria>) => void;
  onNext: () => void;
  onPrevious: () => void;
  isValid?: boolean;
}

export interface CarCardProps {
  car: Car;
  recommendation?: CarRecommendation;
  variant?: 'grid' | 'list' | 'comparison';
  onSelect?: (car: Car) => void;
  onCompare?: (car: Car) => void;
  onFavorite?: (car: Car) => void;
}

export interface FilterOptions {
  brands: string[];
  priceRange: [number, number];
  vehicleTypes: string[];
  fuelTypes: string[];
  yearRange: [number, number];
  features: string[];
}
