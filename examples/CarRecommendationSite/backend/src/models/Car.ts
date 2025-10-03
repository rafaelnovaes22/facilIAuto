import mongoose, { Document, Schema } from 'mongoose';

// Interfaces
export interface ICar extends Document {
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
    performance?: {
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
    tempoMedioVenda: number;
  };

  disponibilidade: {
    regioes: string[];
    concessionarias: string[];
    estoque: 'baixo' | 'medio' | 'alto';
    prazoEntrega: number;
  };

  seguranca?: {
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
    especialistas: Array<{
      nota: number;
      fonte: string;
      pontos: {
        positivos: string[];
        negativos: string[];
      };
    }>;
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

  // Metadata
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
}

// Schema Definition
const CarSchema = new Schema<ICar>({
  marca: { 
    type: String, 
    required: true, 
    index: true,
    trim: true 
  },
  modelo: { 
    type: String, 
    required: true, 
    index: true,
    trim: true 
  },
  versao: { 
    type: String, 
    required: true,
    trim: true 
  },
  ano: { 
    type: Number, 
    required: true, 
    min: 2010, 
    max: new Date().getFullYear() + 1,
    index: true
  },

  preco: {
    fipe: { 
      type: Number, 
      required: true, 
      min: 0,
      index: true 
    },
    mercado: {
      min: { type: Number, required: true, min: 0 },
      max: { type: Number, required: true, min: 0 },
      medio: { type: Number, required: true, min: 0 }
    },
    financiamento: {
      entradaMinima: { type: Number, required: true, min: 0 },
      parcelaEstimada: { type: Number, required: true, min: 0 }
    }
  },

  especificacoes: {
    tipo: { 
      type: String, 
      required: true, 
      enum: ['hatch', 'sedan', 'suv', 'pickup', 'compacto'],
      index: true
    },
    categoria: { 
      type: String, 
      required: true, 
      enum: ['popular', 'premium', 'luxo', 'esportivo'] 
    },
    combustivel: { 
      type: String, 
      required: true,
      index: true
    },
    
    motor: {
      cilindrada: { type: Number, required: true, min: 0.8, max: 8.0 },
      potencia: { type: Number, required: true, min: 50, max: 1000 },
      torque: { type: Number, required: true, min: 50, max: 2000 }
    },
    
    consumo: {
      cidade: { type: Number, required: true, min: 3, max: 25 },
      estrada: { type: Number, required: true, min: 5, max: 35 },
      combinado: { type: Number, required: true, min: 4, max: 30 }
    },
    
    performance: {
      aceleracao0a100: { type: Number, min: 4, max: 20 },
      velocidadeMaxima: { type: Number, min: 120, max: 350 }
    },
    
    dimensoes: {
      comprimento: { type: Number, required: true, min: 3000, max: 6000 },
      largura: { type: Number, required: true, min: 1500, max: 2500 },
      altura: { type: Number, required: true, min: 1200, max: 2200 },
      portaMalas: { type: Number, required: true, min: 100, max: 2000 },
      entreEixos: { type: Number, required: true, min: 2000, max: 4000 }
    },
    
    capacidades: {
      tanque: { type: Number, required: true, min: 30, max: 120 },
      lugares: { type: Number, required: true, min: 2, max: 9 },
      portas: { type: Number, required: true, min: 2, max: 5 }
    },
    
    transmissao: { 
      type: String, 
      required: true, 
      enum: ['manual', 'automatico', 'cvt'],
      index: true
    },
    tracao: { 
      type: String, 
      required: true, 
      enum: ['4x2', '4x4'] 
    }
  },

  confiabilidade: {
    notaJDPower: { type: Number, min: 1, max: 5 },
    customanutencao: { 
      type: String, 
      required: true, 
      enum: ['baixo', 'medio', 'alto'],
      index: true
    },
    problemas: [{ type: String }],
    recall: {
      quantidade: { type: Number, default: 0, min: 0 },
      ultimoAno: { type: Number, min: 2010 }
    },
    pecas: {
      disponibilidade: { 
        type: String, 
        required: true, 
        enum: ['facil', 'moderada', 'dificil'] 
      },
      preco: { 
        type: String, 
        required: true, 
        enum: ['baixo', 'medio', 'alto'] 
      }
    }
  },

  mercado: {
    vendas: {
      ranking: { type: Number, required: true, min: 1 },
      volume: { type: Number, required: true, min: 0 },
      participacao: { type: Number, required: true, min: 0, max: 100 }
    },
    depreciacao: {
      ano1: { type: Number, required: true, min: 0, max: 50 },
      ano3: { type: Number, required: true, min: 0, max: 70 },
      ano5: { type: Number, required: true, min: 0, max: 80 }
    },
    liquidez: { 
      type: String, 
      required: true, 
      enum: ['alta', 'media', 'baixa'],
      index: true
    },
    tempoMedioVenda: { type: Number, required: true, min: 1, max: 365 }
  },

  disponibilidade: {
    regioes: [{ 
      type: String, 
      required: true,
      index: true
    }],
    concessionarias: [{ type: String }],
    estoque: { 
      type: String, 
      required: true, 
      enum: ['baixo', 'medio', 'alto'],
      index: true
    },
    prazoEntrega: { type: Number, required: true, min: 0, max: 180 }
  },

  seguranca: {
    latinNCAP: { type: Number, min: 0, max: 5 },
    iihsRating: { type: String },
    itens: [{ type: String }]
  },

  imagens: {
    principal: { type: String, required: true },
    galeria: [{ type: String }],
    cores: [{
      nome: { type: String, required: true },
      hex: { type: String, required: true },
      imagem: { type: String, required: true }
    }]
  },

  reviews: {
    especialistas: [{
      nota: { type: Number, required: true, min: 0, max: 10 },
      fonte: { type: String, required: true },
      pontos: {
        positivos: [{ type: String }],
        negativos: [{ type: String }]
      }
    }],
    usuarios: {
      nota: { type: Number, required: true, min: 0, max: 5, default: 0 },
      totalAvaliacoes: { type: Number, required: true, min: 0, default: 0 },
      distribuicao: {
        5: { type: Number, default: 0 },
        4: { type: Number, default: 0 },
        3: { type: Number, default: 0 },
        2: { type: Number, default: 0 },
        1: { type: Number, default: 0 }
      }
    }
  },

  // Metadata
  isActive: { type: Boolean, default: true, index: true }
}, {
  timestamps: true, // Automatically add createdAt and updatedAt
});

// Compound Indexes for better query performance
CarSchema.index({ marca: 1, modelo: 1, ano: -1 });
CarSchema.index({ 'preco.fipe': 1, 'especificacoes.tipo': 1 });
CarSchema.index({ 'disponibilidade.regioes': 1, isActive: 1 });
CarSchema.index({ 'especificacoes.consumo.combinado': 1 });
CarSchema.index({ 'mercado.vendas.ranking': 1 });

// Text index for search functionality
CarSchema.index({
  marca: 'text',
  modelo: 'text',
  versao: 'text'
}, {
  weights: {
    marca: 10,
    modelo: 5,
    versao: 1
  }
});

// Virtual for search score calculation
CarSchema.virtual('searchScore').get(function() {
  return this.mercado.vendas.participacao * 0.3 + 
         (6 - this.mercado.vendas.ranking) * 0.2 +
         this.reviews.usuarios.nota * 20;
});

// Static methods
CarSchema.statics.findByBudgetRange = function(min: number, max: number) {
  return this.find({
    'preco.fipe': { $gte: min, $lte: max },
    isActive: true
  });
};

CarSchema.statics.findByRegion = function(region: string) {
  return this.find({
    'disponibilidade.regioes': region,
    isActive: true
  });
};

CarSchema.statics.findByType = function(type: string) {
  return this.find({
    'especificacoes.tipo': type,
    isActive: true
  });
};

// Instance methods
CarSchema.methods.calculateReliabilityScore = function(): number {
  let score = 5; // Base score
  
  // Adjust based on maintenance cost
  if (this.confiabilidade.customanutencao === 'baixo') score += 2;
  else if (this.confiabilidade.customanutencao === 'alto') score -= 2;
  
  // Adjust based on recalls
  score -= Math.min(this.confiabilidade.recall.quantidade * 0.5, 2);
  
  // Adjust based on parts availability
  if (this.confiabilidade.pecas.disponibilidade === 'facil') score += 1;
  else if (this.confiabilidade.pecas.disponibilidade === 'dificil') score -= 1;
  
  return Math.max(1, Math.min(10, score));
};

CarSchema.methods.calculateValueScore = function(): number {
  let score = 5; // Base score
  
  // Better resale value = higher score
  const avgDepreciation = (this.mercado.depreciacao.ano1 + this.mercado.depreciacao.ano3) / 2;
  score += (25 - avgDepreciation) / 5; // Lower depreciation = higher score
  
  // Market liquidity affects resale
  if (this.mercado.liquidez === 'alta') score += 1;
  else if (this.mercado.liquidez === 'baixa') score -= 1;
  
  // Sales volume indicates market acceptance
  if (this.mercado.vendas.participacao > 5) score += 1;
  else if (this.mercado.vendas.participacao < 1) score -= 1;
  
  return Math.max(1, Math.min(10, score));
};

// Pre-save middleware
CarSchema.pre('save', function(next) {
  // Calculate combined fuel consumption if not provided
  if (!this.especificacoes.consumo.combinado) {
    this.especificacoes.consumo.combinado = 
      (this.especificacoes.consumo.cidade + this.especificacoes.consumo.estrada) / 2;
  }
  
  // Calculate average market price if not provided
  if (!this.preco.mercado.medio) {
    this.preco.mercado.medio = 
      (this.preco.mercado.min + this.preco.mercado.max) / 2;
  }
  
  next();
});

// Export the model
export const Car = mongoose.model<ICar>('Car', CarSchema);
export default Car;
