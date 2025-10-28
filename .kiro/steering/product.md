# FacilIAuto - Product Overview

## What is FacilIAuto?

FacilIAuto is a **B2B SaaS multi-tenant automotive recommendation platform** designed for car dealerships in Brazil. It uses responsible AI to provide personalized car recommendations to customers through a mobile-first experience.

## Core Value Proposition

- **Mobile-first native experience** (not desktop adapted)
- **30-minute setup** vs 2-4 weeks for competitors
- **Affordable pricing**: R$ 497-1,997/month vs R$ 8k-15k/month competitors
- **White-label customization** (full branding, not just logo)
- **Transparent AI with guardrails** (not black box)
- **Targets small/medium dealerships** (80% of market, underserved)

## Target Market

- **26,000+ dealerships** in Brazil
- **80% small/medium** dealerships not served by enterprise solutions
- **R$ 50M+ addressable market**
- **R$ 6M+ ARR potential** in 3 years

## Business Model

**Validated ROI**: 380% for dealerships
- Investment: R$ 997/month (Professional Plan)
- Payback: 2-3 months
- +30% conversion increase

## Current Status

- **Backend**: 97/100 ⭐⭐⭐⭐⭐ (Production-ready)
- **Frontend**: 40/100 (In development, 2-3 weeks to complete)
- **Overall**: 84/100 ⭐⭐⭐⭐

## Key Features

1. **Intelligent Questionnaire**: 4-step mobile-optimized user profiling
2. **AI Recommendations**: Multi-dimensional scoring algorithm (0.0-1.0)
3. **Multi-tenant Architecture**: Aggregates cars from multiple dealerships
4. **Feedback System**: Iterative refinement based on user interactions
5. **ML Data Collection**: Tracks interactions for future model training
6. **WhatsApp Integration**: Direct contact with dealerships
7. **6 Usage Profiles**: Detailed recommendations for each use case

## Priority System

The recommendation engine uses a **5-priority system**:
- User defines 5 priorities (scale 1-5): Economia, Espaço, Performance, Conforto, Segurança
- Algorithm uses **ALL 5 priorities** in score calculation (40% weight)
- UI displays only **Top 3 priorities** for clarity and better UX
- This approach provides precision without overwhelming users

## Language Simplification (Critical UX Principle)

**"If your grandmother doesn't understand it, it's too technical"**

Users don't need to know about cars to find the perfect car. All user-facing content must use simple, everyday language:

- **NEVER use**: ISOFIX, ESP, ABS, airbags, torque, cv, suspension types, transmission types
- **ALWAYS use**: "Protects your family", "Fits lots of luggage", "Easy to drive", "Saves fuel"
- **Questions**: Based on real situations, not technical specs
- **Justifications**: Benefits, not specifications
- **Tooltips**: Visual explanations when needed

See: `.kiro/specs/questionario-simplificado/requirements.md` and `docs/guides/LINGUAGEM-SIMPLIFICADA.md`

## Usage Profiles (6 Detailed Profiles)

FacilIAuto provides specialized recommendations for 6 distinct usage profiles:

### 1. **Família** (Family)
- **Priorities**: Segurança (5), Espaço (5), Conforto (4)
- **Requirements**: 6 airbags, ISOFIX, 300L+ trunk, ESP
- **Top categories**: SUV, SUV Compacto, Sedan
- **Documentation**: `docs/business/PERFIS-USO-DETALHADOS.md`

### 2. **Trabalho** (Work/Commute)
- **Priorities**: Economia (5), Confiabilidade (5), Custo Manutenção (5)
- **Requirements**: 12 km/L+, A/C, affordable maintenance
- **Top categories**: Sedan Compacto, Hatch
- **Documentation**: `docs/business/PERFIL-TRABALHO.md`

### 3. **Lazer** (Leisure/Travel)
- **Priorities**: Performance (5), Conforto (5), Tecnologia (4)
- **Requirements**: 400L+ trunk, multimedia, connectivity
- **Top categories**: SUV, Crossover, Pickup
- **Documentation**: `docs/business/PERFIS-LAZER-COMERCIAL-PRIMEIRO.md`

### 4. **Comercial** (Commercial/Delivery)
- **Priorities**: Capacidade Carga (5), Durabilidade (5), Economia (4)
- **Requirements**: 600kg+ capacity, reinforced chassis
- **Top categories**: Pickup, Furgão, Van
- **Documentation**: `docs/business/PERFIS-LAZER-COMERCIAL-PRIMEIRO.md`

### 5. **Primeiro Carro** (First Car)
- **Priorities**: Segurança (5), Facilidade (5), Economia (4)
- **Requirements**: 4+ airbags, ABS, ESP, easy to drive
- **Top categories**: Hatch, Sedan Compacto
- **Documentation**: `docs/business/PERFIS-LAZER-COMERCIAL-PRIMEIRO.md`

### 6. **Transporte Passageiros** (Ride-sharing: Uber, 99)
- **Priorities**: Economia (5), Custo Manutenção (5), Confiabilidade (5)
- **3 categories**: UberX/99Pop, Uber Comfort, Uber Black
- **150+ accepted models** from official lists (2025)
- **Automatic validation**: 4 doors, 5 seats, A/C, year requirements
- **Documentation**: `docs/business/CARROS-TRANSPORTE-APP.md`

**Data files**: 
- `platform/backend/data/usage_profiles.json` - Structured profile data
- `platform/backend/data/app_transport_vehicles.json` - Ride-sharing vehicles

## Competitive Differentiation

FacilIAuto is **6-12 months ahead** of competitors through:
- Superior mobile-first UX
- Transparent AI with guardrails
- Rapid deployment capability
- Affordable pricing for SMB market
