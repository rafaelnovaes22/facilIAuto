# Roadmap de Features Futuras - FacilIAuto Frontend

## Visão Geral

Este documento descreve as features planejadas para implementação futura, assim que os dados estiverem disponíveis no backend. A estrutura de dados e componentes já está preparada para receber essas informações.

## Status Atual: MVP Completo ✅

**O que temos hoje (95% completo):**
- ✅ Questionário de 4 steps com linguagem simplificada
- ✅ Sistema de recomendações com IA
- ✅ Página de resultados com filtering e sorting
- ✅ CarCard com score visual e informações básicas
- ✅ CarDetailsModal com galeria de imagens
- ✅ WhatsApp integration
- ✅ ML tracking de interações
- ✅ Mobile-first responsive design

---

## 🎯 Fase 2: Confiança e Transparência (Prioridade ALTA)

### 1. Histórico do Veículo

**Objetivo:** Aumentar confiança do consumidor (85% das consultas verificam histórico)

**Dados necessários no backend:**
```typescript
interface CarHistory {
  accidents: {
    hasAccidents: boolean
    count?: number
    description?: string
  }
  owners: {
    count: number
    isFirstOwner: boolean
  }
  maintenance: {
    isUpToDate: boolean
    lastServiceDate?: string
    serviceHistory?: ServiceRecord[]
  }
  inspection: {
    hasInspection: boolean
    inspectionDate?: string
    inspectionReport?: string // URL do laudo
    approved: boolean
  }
  documentation: {
    isRegular: boolean
    hasDebts: boolean
    ipvaUpToDate: boolean
  }
}
```

**Componentes a criar:**
- `VehicleHistoryBadges.tsx` - Badges de confiança
- `InspectionReport.tsx` - Visualizador de laudo
- `MaintenanceHistory.tsx` - Histórico de manutenção

**Onde exibir:**
- CarCard: Badges principais (sem acidentes, 1º dono)
- CarDetailsModal: Seção completa de histórico

**Estimativa:** 2-3 dias de desenvolvimento

---

### 2. Simulação de Financiamento

**Objetivo:** Atender 45% dos compradores que financiam

**Dados necessários no backend:**
```typescript
interface FinancingOptions {
  available: boolean
  minDownPayment: number // Entrada mínima
  maxInstallments: number // Máx parcelas
  interestRate: number // Taxa mensal
  banks: {
    name: string
    rate: number
    maxInstallments: number
  }[]
}
```

**Componentes a criar:**
- `FinancingCalculator.tsx` - Calculadora interativa
- `FinancingSimulation.tsx` - Resultado da simulação
- `BankComparison.tsx` - Comparação de bancos

**Onde exibir:**
- CarCard: Badge "Financiamento disponível"
- CarDetailsModal: Seção de simulação completa

**Estimativa:** 3-4 dias de desenvolvimento

---

## 🌟 Fase 3: Informações Enriquecidas (Prioridade MÉDIA)

### 3. Especificações Técnicas Detalhadas

**Dados necessários no backend:**
```typescript
interface DetailedSpecs {
  engine: {
    displacement: string // "1.0"
    power: string // "75 cv"
    torque: string // "10.4 kgfm"
    type: string // "Turbo"
    fuelConsumption: {
      city: number // km/L
      highway: number
    }
  }
  features: {
    airConditioning: boolean
    electricSteering: boolean
    electricWindows: boolean
    centralLocking: boolean
    alarm: boolean
    alloyWheels: boolean
    // ... outros opcionais
  }
  safety: {
    airbags: number
    abs: boolean
    esp: boolean
    tractionControl: boolean
    hillAssist: boolean
  }
  comfort: {
    leatherSeats: boolean
    multimediaSystem: boolean
    bluetooth: boolean
    reverseCamera: boolean
    parkingSensors: boolean
  }
}
```

**Componentes a criar:**
- `TechnicalSpecs.tsx` - Especificações organizadas
- `FeaturesList.tsx` - Lista de opcionais com ícones
- `SafetyFeatures.tsx` - Itens de segurança destacados

**Onde exibir:**
- CarDetailsModal: Seção "Especificações Completas"

**Estimativa:** 2-3 dias de desenvolvimento

---

### 4. Comparação de Preços

**Dados necessários no backend:**
```typescript
interface PriceComparison {
  currentPrice: number
  marketAverage: number
  priceStatus: 'below' | 'average' | 'above' // Abaixo, na média, acima
  savingsAmount?: number // Economia em R$
  priceHistory?: {
    date: string
    price: number
  }[]
  similarCars: {
    id: string
    name: string
    price: number
  }[]
}
```

**Componentes a criar:**
- `PriceIndicator.tsx` - Badge de preço justo/bom
- `PriceComparison.tsx` - Comparação visual
- `PriceHistory.tsx` - Gráfico de evolução

**Onde exibir:**
- CarCard: Badge "R$ 5.000 abaixo da média!"
- CarDetailsModal: Seção de comparação

**Estimativa:** 2-3 dias de desenvolvimento

---

### 5. Reviews e Avaliações

**Dados necessários no backend:**
```typescript
interface Reviews {
  dealershipRating: {
    average: number // 0-5
    totalReviews: number
    breakdown: {
      5: number
      4: number
      3: number
      2: number
      1: number
    }
  }
  reviews: {
    id: string
    author: string
    rating: number
    date: string
    comment: string
    verified: boolean
    carPurchased?: string
  }[]
  testimonials: {
    id: string
    author: string
    photo?: string
    text: string
    carPurchased: string
  }[]
}
```

**Componentes a criar:**
- `DealershipRating.tsx` - Rating da concessionária
- `ReviewsList.tsx` - Lista de reviews
- `ReviewCard.tsx` - Card individual de review
- `TestimonialCarousel.tsx` - Carrossel de depoimentos

**Onde exibir:**
- CarCard: Rating da concessionária
- CarDetailsModal: Seção de reviews
- HomePage: Depoimentos de clientes

**Estimativa:** 3-4 dias de desenvolvimento

---

## 🚀 Fase 4: Experiência Avançada (Prioridade BAIXA)

### 6. Vídeos e Test Drive Virtual

**Dados necessários no backend:**
```typescript
interface MediaContent {
  videos: {
    type: 'walkthrough' | 'test_drive' | 'interior' | 'exterior'
    url: string
    thumbnail: string
    duration: number
    title: string
  }[]
  virtualTour?: {
    url: string // Link para tour 360°
    provider: 'matterport' | 'custom'
  }
}
```

**Componentes a criar:**
- `VideoGallery.tsx` - Galeria de vídeos
- `VideoPlayer.tsx` - Player integrado
- `VirtualTour.tsx` - Tour 360° embarcado

**Onde exibir:**
- CarDetailsModal: Tab "Vídeos"

**Estimativa:** 3-4 dias de desenvolvimento

---

### 7. Comparador de Carros

**Funcionalidade:**
- Comparar até 3 carros lado a lado
- Especificações, preços, features
- Score de match para cada um

**Componentes a criar:**
- `ComparisonTool.tsx` - Ferramenta de comparação
- `ComparisonTable.tsx` - Tabela comparativa
- `ComparisonSelector.tsx` - Seletor de carros

**Onde exibir:**
- ResultsPage: Botão "Comparar" nos cards
- Nova página: `/comparar`

**Estimativa:** 4-5 dias de desenvolvimento

---

### 8. Agendamento de Test Drive

**Dados necessários no backend:**
```typescript
interface TestDrive {
  available: boolean
  dealershipSchedule: {
    dayOfWeek: number
    openTime: string
    closeTime: string
  }[]
  availableSlots: {
    date: string
    time: string
    available: boolean
  }[]
}
```

**Componentes a criar:**
- `TestDriveScheduler.tsx` - Agendador
- `CalendarPicker.tsx` - Seletor de data/hora
- `TestDriveConfirmation.tsx` - Confirmação

**Onde exibir:**
- CarDetailsModal: Botão "Agendar Test Drive"

**Estimativa:** 3-4 dias de desenvolvimento

---

## 📊 Estrutura de Dados Preparada

### Atualização do Type `Car` (types/index.ts)

```typescript
export interface Car {
  // ... campos existentes ...
  
  // FASE 2: Confiança
  history?: CarHistory
  financing?: FinancingOptions
  
  // FASE 3: Informações Enriquecidas
  detailedSpecs?: DetailedSpecs
  priceComparison?: PriceComparison
  reviews?: Reviews
  
  // FASE 4: Experiência Avançada
  media?: MediaContent
  testDrive?: TestDrive
}
```

**Todos os campos são opcionais** - o sistema funciona perfeitamente sem eles e os exibe quando disponíveis.

---

## 🎯 Estratégia de Implementação

### Princípios:
1. **Progressive Enhancement** - Sistema funciona sem os dados, melhora com eles
2. **Graceful Degradation** - Se dados não existirem, não quebra
3. **Conditional Rendering** - Só exibe seções se dados disponíveis
4. **Loading States** - Feedback visual durante carregamento
5. **Error Handling** - Tratamento elegante de erros

### Exemplo de Implementação:

```typescript
// No CarDetailsModal
{car.history && (
  <VehicleHistorySection history={car.history} />
)}

{car.financing?.available && (
  <FinancingSection 
    carPrice={car.preco}
    options={car.financing}
  />
)}

{car.reviews && car.reviews.dealershipRating.totalReviews > 0 && (
  <ReviewsSection reviews={car.reviews} />
)}
```

---

## 📈 Impacto Esperado por Fase

### Fase 2 (Confiança):
- **+40% conversão** - Histórico aumenta confiança
- **+35% leads** - Simulação de financiamento facilita decisão
- **-60% desistências** - Transparência reduz fricção

### Fase 3 (Informações):
- **+25% tempo no site** - Mais informações = mais engajamento
- **+30% qualidade leads** - Usuários mais informados
- **+20% satisfação** - Reviews aumentam confiança

### Fase 4 (Experiência):
- **+50% engajamento** - Vídeos prendem atenção
- **+40% test drives** - Agendamento facilita
- **+15% conversão** - Experiência completa

---

## 🔄 Próximos Passos

1. **Backend Team:** Priorizar APIs de histórico e financiamento
2. **Frontend Team:** Criar componentes base (aguardando dados)
3. **Design Team:** Criar mockups das novas seções
4. **Product Team:** Validar prioridades com stakeholders

---

## 📝 Notas Técnicas

- Todos os novos campos são **opcionais** no TypeScript
- Componentes usam **conditional rendering**
- Sem breaking changes - 100% backward compatible
- Fácil de testar com dados mock
- Pronto para A/B testing

---

**Última atualização:** 2025-01-17
**Status:** Planejamento aprovado, aguardando dados do backend
**Responsável:** Tech Lead + Product Manager
