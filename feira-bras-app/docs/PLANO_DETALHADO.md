# Plano Detalhado - FeiraBrás App

## 1. ANÁLISE DE MERCADO E CONTEXTO

### 1.1 Feira da Madrugada - Características
- **Horário:** 2h às 10h (segunda a sábado)
- **Público:** 30.000+ vendedores informais
- **Volume:** R$ 20 milhões/dia em transações
- **Localização:** Região do Brás, São Paulo
- **Produtos:** Principalmente roupas e acessórios

### 1.2 Problemas Identificados
1. **Gestão Manual:** 95% usa cadernos para controle
2. **Perda de Vendas:** Falta de controle de estoque
3. **Inadimplência:** Sem controle de fiado
4. **Impostos:** Dificuldade para formalização
5. **Relacionamento:** Perda de contato com clientes

### 1.3 Oportunidades
- Digitalização de processos
- Integração com PIX (80% das vendas)
- WhatsApp Business API
- Formalização via MEI
- Análise de dados para decisões

## 2. PERSONAS DETALHADAS

### Persona Primária: Maria Silva
```
Idade: 35 anos
Educação: Ensino médio
Experiência: 8 anos na feira
Faturamento: R$ 15.000/mês
Produtos: Roupas femininas
Tech: WhatsApp, Instagram básico
Dores:
- Perde 20% das vendas por falta de controle
- Gasta 2h/dia fazendo contas
- R$ 2.000/mês em inadimplência
- Não sabe lucro real
```

### Persona Secundária: João Santos
```
Idade: 42 anos
Educação: Fundamental
Experiência: 15 anos na feira
Faturamento: R$ 25.000/mês
Produtos: Jeans masculino
Tech: WhatsApp apenas
Dores:
- Não consegue crescer
- Compra errado por falta de dados
- Perde clientes fiéis
- Medo de tecnologia
```

## 3. FUNCIONALIDADES MVP - PRIORIZAÇÃO MoSCoW

### MUST HAVE (Essencial)
1. **Cadastro de Produtos Simplificado**
   - Foto + nome + preço
   - Tamanhos (P/M/G/GG)
   - Quantidade em estoque
   - Busca rápida

2. **Venda Rápida**
   - Sem cadastro obrigatório
   - PIX/Dinheiro/Cartão
   - Desconto simples
   - Finalização em 3 cliques

3. **Controle de Caixa**
   - Abertura/fechamento
   - Resumo do dia
   - Sangrias e reforços
   - Conferência simples

### SHOULD HAVE (Importante)
1. **Cliente Básico**
   - Nome + WhatsApp
   - Histórico de compras
   - Fiado simples

2. **Relatórios Simples**
   - Vendas do dia/semana/mês
   - Produtos mais vendidos
   - Horários de pico

3. **Comprovante WhatsApp**
   - Envio automático
   - Template personalizado

### COULD HAVE (Desejável)
1. **Código de Barras**
2. **Múltiplos vendedores**
3. **Metas de vendas**
4. **Integração bancária**

### WON'T HAVE (Não terá agora)
1. **E-commerce**
2. **NF-e completa**
3. **Contabilidade**
4. **Multi-loja**

## 4. ARQUITETURA TÉCNICA

### 4.1 Mobile App (React Native + Expo)
```javascript
// Stack principal
- React Native 0.72+
- Expo SDK 49
- TypeScript 5.0
- React Navigation 6
- React Hook Form
- Zustand (estado)
- React Query (cache)
- AsyncStorage (offline)
```

### 4.2 Backend (Node.js)
```javascript
// Stack principal
- Node.js 20 LTS
- Express.js
- TypeScript
- Prisma ORM
- PostgreSQL
- Redis (cache)
- JWT auth
- Multer (upload)
```

### 4.3 Infraestrutura
```yaml
Development:
  - Docker Compose
  - LocalStack (AWS local)
  
Production:
  - AWS EC2 / Heroku
  - RDS PostgreSQL
  - S3 / Cloudinary
  - CloudFront CDN
  - GitHub Actions CI/CD
```

## 5. METODOLOGIA XP - IMPLEMENTAÇÃO

### 5.1 Práticas Core
```
Planning Game
├── Sprint Planning: Segunda 9h
├── Daily Standup: 9h (15 min)
├── Review: Sexta 16h
└── Retrospectiva: Sexta 17h

Pair Programming
├── Código crítico: 100% pareado
├── Rotação: A cada 2 horas
├── Driver/Navigator alternado
└── Code review obrigatório

TDD Cycle
├── Red: Escrever teste que falha
├── Green: Código mínimo para passar
├── Refactor: Melhorar mantendo verde
└── Commit: A cada ciclo completo
```

### 5.2 Velocity e Métricas
- **Story Points:** Fibonacci (1,2,3,5,8)
- **Velocity inicial:** 20 pontos/sprint
- **Sprint:** 1 semana
- **WIP Limit:** 3 stories
- **Lead Time:** < 3 dias
- **Cycle Time:** < 1 dia

## 6. ESTRATÉGIA DE TESTES E2E

### 6.1 Configuração Detox (Mobile)
```javascript
// .detoxrc.js
module.exports = {
  testRunner: 'jest',
  runnerConfig: 'e2e/config.json',
  apps: {
    'ios.debug': {
      type: 'ios.app',
      binaryPath: 'ios/build/FeiraBras.app',
      build: 'xcodebuild ...'
    },
    'android.debug': {
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk',
      build: 'cd android && ./gradlew assembleDebug'
    }
  },
  devices: {
    simulator: {
      type: 'ios.simulator',
      device: { type: 'iPhone 14' }
    },
    emulator: {
      type: 'android.emulator',
      device: { avdName: 'Pixel_4_API_30' }
    }
  }
};
```

### 6.2 Cenários E2E Críticos
```gherkin
Feature: Venda Completa
  Scenario: Realizar venda com PIX
    Given vendedor está na tela inicial
    When seleciona 3 produtos
    And aplica desconto de 10%
    And escolhe pagamento PIX
    Then venda é registrada
    And estoque é atualizado
    And comprovante é gerado

Feature: Fechamento de Caixa
  Scenario: Fechar caixa do dia
    Given existem vendas no dia
    When vendedor fecha o caixa
    Then mostra resumo correto
    And permite conferência
    And gera relatório
```

### 6.3 Pipeline CI/CD
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:unit
      - run: npm run test:integration
      
  e2e-android:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm run e2e:android
      
  deploy:
    needs: [test, e2e-android]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: npm run deploy
```

## 7. CRONOGRAMA DETALHADO - 13 SEMANAS

### Fase 1: Fundação (Semanas 1-3)
```
Semana 1 - Setup e Arquitetura
├── Configurar ambiente de desenvolvimento
├── Setup Docker e banco de dados
├── Configurar CI/CD pipeline
├── Criar projeto React Native
└── Implementar autenticação básica

Semana 2 - Estrutura Base
├── Implementar navegação
├── Criar componentes base
├── Setup de testes (Jest + Detox)
├── Configurar estado global
└── Implementar offline-first

Semana 3 - CRUD Produtos
├── Tela de listagem
├── Cadastro com foto
├── Edição e exclusão
├── Busca e filtros
└── Testes E2E completos
```

### Fase 2: Core Features (Semanas 4-7)
```
Semana 4-5 - Fluxo de Venda
├── Carrinho de compras
├── Cálculo de desconto
├── Formas de pagamento
├── Finalização de venda
└── Comprovante digital

Semana 6-7 - Gestão Financeira
├── Abertura/fechamento caixa
├── Dashboard de vendas
├── Relatórios básicos
├── Gráficos simples
└── Export para Excel
```

### Fase 3: Features Complementares (Semanas 8-10)
```
Semana 8 - Gestão de Clientes
├── Cadastro simplificado
├── Histórico de compras
├── Integração WhatsApp
└── Controle de fiado

Semana 9-10 - Polish e Performance
├── Otimização de queries
├── Lazy loading
├── Cache estratégico
├── Melhorias de UX
└── Correção de bugs
```

### Fase 4: Lançamento (Semanas 11-13)
```
Semana 11 - Beta Testing
├── Deploy em produção
├── 10 usuários beta
├── Coleta de feedback
└── Ajustes críticos

Semana 12 - Preparação Launch
├── Material de treinamento
├── Vídeos tutoriais
├── Documentação usuário
└── Suporte WhatsApp

Semana 13 - Go Live
├── Lançamento oficial
├── Monitoramento 24/7
├── Suporte ativo
└── Coleta de métricas
```

## 8. ORÇAMENTO ESTIMADO

### Desenvolvimento (13 semanas)
```
2 Desenvolvedores Full-Stack
├── Salário: R$ 8.000/mês cada
├── Total: R$ 52.000

1 UX Designer (part-time)
├── Salário: R$ 3.000/mês
├── Total: R$ 9.750

Total Desenvolvimento: R$ 61.750
```

### Infraestrutura (Ano 1)
```
AWS/Heroku: R$ 500/mês = R$ 6.000
Domínio: R$ 50/ano
SSL: R$ 200/ano
Cloudinary: R$ 100/mês = R$ 1.200
Total Infra: R$ 7.450/ano
```

### Marketing e Lançamento
```
Material gráfico: R$ 2.000
Vídeos tutorial: R$ 3.000
Eventos na feira: R$ 2.000
Ads (Facebook/Google): R$ 3.000
Total Marketing: R$ 10.000
```

### **TOTAL PROJETO: R$ 79.200**

## 9. RISCOS E MITIGAÇÕES

### Riscos Técnicos
| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Performance ruim offline | Média | Alto | Testes extensivos, cache otimizado |
| Bugs em produção | Média | Alto | CI/CD robusto, testes E2E |
| Escala não suportada | Baixa | Alto | Arquitetura escalável, monitoring |

### Riscos de Negócio
| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Baixa adoção | Média | Alto | MVP gratuito, treinamento |
| Resistência à tecnologia | Alta | Médio | Interface simples, suporte |
| Concorrência | Média | Médio | Diferenciação, preço justo |

## 10. MÉTRICAS DE SUCESSO

### Métricas Técnicas
- **Uptime:** > 99.5%
- **Response Time:** < 2s (95 percentil)
- **Crash Rate:** < 1%
- **Test Coverage:** > 80%
- **Build Time:** < 10 min

### Métricas de Produto
- **Downloads:** 1.000 em 3 meses
- **MAU:** 100 usuários ativos
- **Retenção D1:** > 60%
- **Retenção D7:** > 40%
- **Retenção D30:** > 20%

### Métricas de Negócio
- **NPS:** > 8
- **Vendas/dia/usuário:** > 5
- **Ticket médio aumento:** > 10%
- **Redução inadimplência:** > 30%
- **ROI:** Positivo em 6 meses

## 11. PRÓXIMOS PASSOS

### Imediato (Próxima semana)
1. ✅ Validar plano com stakeholders
2. ⏳ Recrutar time de desenvolvimento
3. ⏳ Configurar ambiente de desenvolvimento
4. ⏳ Iniciar Sprint 0

### Curto Prazo (Próximo mês)
1. Desenvolver primeira versão
2. Conseguir 3 vendedores parceiros
3. Realizar testes de campo
4. Coletar feedback inicial

### Médio Prazo (3 meses)
1. Lançar MVP
2. 100 usuários ativos
3. Iterar baseado em feedback
4. Planejar versão 2.0

---

*Documento atualizado em: [Data atual]*
*Versão: 1.0*
*Autor: Time FeiraBrás*