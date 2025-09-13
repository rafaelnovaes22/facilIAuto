# 📅 Guia Diário XP - CarMatch

## 🌅 Rotina Diária XP

### **Daily Standup (9:00 - 9:15)** 💬

#### Formato das 3 Perguntas
```markdown
👋 **Nome**: [Seu nome]

🎯 **O que fiz ontem:**
- [Tarefa 1] - Status: ✅ Completo
- [Tarefa 2] - Status: 🔄 Em progresso (XX% completo)

🎯 **O que vou fazer hoje:**
- [Tarefa específica com critério de "pronto"]
- [Pair programming com [Nome] das 14h-16h]

🚧 **Impedimentos:**
- [Bloqueio específico] - Preciso de ajuda de [Pessoa/Time]
- [Decisão pendente] - Aguardando feedback do cliente

⚡ **TDD Status:**
- Testes escritos: X
- Testes passando: Y
- Coverage atual: Z%

🤝 **Pairs de hoje:**
- [Horário]: [Driver] + [Navigator] → [Objetivo específico]
```

#### Regras do Standup
- ⏰ **Máximo 15 minutos**
- 🎯 **Foco em impedimentos e colaboração**
- 🚫 **Não é reunião de resolução de problemas**
- 📝 **Anotar action items para depois**

---

## 🧪 Ciclo TDD Diário

### **Red-Green-Refactor em Prática**

#### 1. 🔴 **RED (5-10 min)**
```bash
# Escrever teste que falha
npm run test:watch

# Exemplo:
describe('RecommendationEngine', () => {
  it('should return family-friendly cars for family profile', () => {
    const familyCriteria = createFamilyProfile();
    const recommendations = engine.getRecommendations(familyCriteria);
    
    expect(recommendations[0].car.seats).toBeGreaterThanOrEqual(5);
    expect(recommendations[0].justification).toContain('família');
  });
});
```

#### 2. 🟢 **GREEN (10-20 min)**
```typescript
// Implementação mínima para passar
class RecommendationEngine {
  getRecommendations(criteria: UserCriteria): CarRecommendation[] {
    if (criteria.family?.size >= 4) {
      return [mockFamilyCar]; // Mínimo para passar
    }
    return [mockStandardCar];
  }
}
```

#### 3. 🔵 **REFACTOR (10-15 min)**
```typescript
// Melhorar sem quebrar testes
class RecommendationEngine {
  getRecommendations(criteria: UserCriteria): CarRecommendation[] {
    const cars = this.carRepository.findByCriteria(criteria);
    const scored = this.scoringService.calculateScores(cars, criteria);
    return this.rankAndFilter(scored, criteria);
  }
}
```

### **Checklist TDD Diário**
- [ ] 🔴 Teste escrito e falhando
- [ ] 🟢 Código mínimo implementado
- [ ] ✅ Teste passou
- [ ] 🔵 Código refatorado e limpo
- [ ] 📊 Coverage mantido/melhorado
- [ ] 🔄 Commit com mensagem descritiva

---

## 👥 Pair Programming Guidelines

### **Sessões de Pair Programming**

#### **Schedule Sugerido**
```markdown
## Segunda-feira
09:30-11:30: Tech Lead + Data Analyst → Recommendation Engine
14:00-16:00: Product Manager + Content Creator → UI Components

## Terça-feira  
09:30-11:30: Data Analyst + Business Analyst → Data Models
14:00-16:00: Content Creator + Tech Lead → Frontend Integration

## Quarta-feira
09:30-11:30: Business Analyst + Product Manager → Requirements
14:00-16:00: Marketing Strategist + Content Creator → Landing Page

## Quinta-feira
09:30-11:30: Rotação livre baseada em necessidades
14:00-16:00: Code review em grupo

## Sexta-feira
09:30-11:30: Retrospectiva técnica
14:00-16:00: Refactoring colaborativo
```

#### **Regras do Driver/Navigator**
```markdown
👨‍💻 **Driver (Quem digita):**
- Foca na implementação imediata
- Verbaliza o que está fazendo
- Não toma decisões de design sozinho
- Troca a cada 15-20 minutos

🧭 **Navigator (Quem guia):**
- Pensa no design geral e próximos passos
- Questiona decisões e sugere melhorias
- Monitora qualidade do código
- Pesquisa referências quando necessário
```

#### **Setup Técnico para Pairs**
```bash
# VS Code Live Share
code --install-extension ms-vsliveshare.vsliveshare

# Configuração de pair programming
git config --global user.name "Driver Name + Navigator Name"
git config --global user.email "pair@carmatch.com"

# Commit messages para pairs
git commit -m "feat: implement user scoring logic

Co-authored-by: Navigator Name <navigator@email.com>"
```

---

## 🔄 Integração Contínua Diária

### **Git Workflow XP**

#### **Branches Strategy**
```bash
main           # Produção (sempre deployável)
├── develop    # Staging (features integradas)
├── feature/   # Features individuais (vida curta)
└── hotfix/    # Correções urgentes
```

#### **Commits Frequentes**
```bash
# Commits pequenos e frequentes (a cada 30-60 min)
git add .
git commit -m "test: add failing test for family car filtering"

# 15 minutos depois...
git commit -m "feat: implement basic family car filter"

# 10 minutos depois...
git commit -m "refactor: extract scoring logic to separate service"
```

#### **Push/Pull Contínuo**
```bash
# Push frequente (várias vezes por dia)
git push origin feature/recommendation-engine

# Pull frequente para evitar conflitos
git pull origin develop --rebase
```

### **CI Feedback Loop**
```markdown
📊 **Status do Build (verificar a cada push):**
- ✅ Linting passou
- ✅ Testes unitários: 95% coverage
- ✅ Testes integração: todos passando  
- ✅ E2E críticos: ✅
- ⚠️  Performance: resposta > 2s (investigar)

🚨 **Se build quebrar:**
1. Parar desenvolvimento imediatamente
2. Investigar e corrigir em pair
3. Não fazer novos commits até build verde
```

---

## 🏃‍♂️ Desenvolvimento Incremental

### **Slice Vertical (Feature Completa)**
```markdown
📋 **User Story**: "Como usuário família, quero ver carros adequados para minha família"

🔹 **Slice 1 (Day 1)**: Filtro básico por número de assentos
  - [ ] Teste: filter cars by minimum seats
  - [ ] Backend: simple seat filter
  - [ ] Frontend: seat input
  - [ ] Deploy: staging test

🔹 **Slice 2 (Day 2)**: Scoring por segurança  
  - [ ] Teste: prioritize safe cars for families
  - [ ] Backend: safety scoring algorithm
  - [ ] Frontend: safety indicators
  - [ ] Deploy: staging test

🔹 **Slice 3 (Day 3)**: UI de justificativa
  - [ ] Teste: show family-specific justification
  - [ ] Backend: justification generation
  - [ ] Frontend: justification display
  - [ ] Deploy: production
```

### **Working Software Daily**
```bash
# Deploy diário para staging
npm run build
npm run deploy:staging
npm run smoke-test:staging

# Se passou nos smoke tests → considerar production
npm run deploy:production
```

---

## 🎯 Métricas XP Diárias

### **Dashboard Diário**
```markdown
📊 **Métricas de Hoje** (atualizado às 17h):

🧪 **Qualidade:**
- Testes escritos hoje: 12
- Coverage delta: +2.3%
- Bugs encontrados: 1
- Bugs corrigidos: 3

⚡ **Velocidade:**
- Commits hoje: 23
- Deploys: 3 (staging)
- Pair hours: 4h
- Code review time: avg 45min

🎯 **Valor:**
- User stories completadas: 1.5
- Features em produção: 2
- Customer feedback: +1 feature request

🤝 **Colaboração:**
- Pair programming: 67% do tempo
- Knowledge sharing: 1 sessão
- Impedimentos resolvidos: 2
```

### **Red Flags Diários**
```markdown
🚨 **Alertas para investigar:**

❌ **Coverage caiu abaixo de 90%**
  → Ação: Pair session para escrever testes missing

❌ **Mais de 2h sem commit**
  → Ação: Quebrar tarefa em partes menores

❌ **Build quebrado por > 30min**
  → Ação: Drop everything e corrigir

❌ **Pair programming < 50% do dia**
  → Ação: Reorganizar schedule amanhã
```

---

## 🎉 Cerimônias XP Semanais

### **Planning Meeting (Segunda, 16h-17h)**
```markdown
🎯 **Agenda:**
1. Review da semana anterior (10min)
2. Priorização de stories (20min)
3. Estimativas colaborativas (20min)
4. Definição de pairs da semana (10min)

📋 **Output:**
- [ ] Stories priorizadas para a semana
- [ ] Critérios de aceitação definidos
- [ ] Pairs programados
- [ ] Impedimentos identificados
```

### **Retrospective (Sexta, 16h-17h)**
```markdown
🔄 **Formato:**

**😊 O que funcionou bem:**
- TDD rhythm foi consistente
- Pair programming melhorou qualidade
- Deploy diário reduziu stress

**😐 O que pode melhorar:**
- Testes E2E estão lentos (45min)
- Comunicação com cliente precisa ser mais frequente
- Refactoring ficou atrasado

**💡 Experimentos para próxima semana:**
- Usar parallel testing para E2E
- Customer demo às quartas
- Reserve sexta tarde para refactoring

**📊 Métricas da semana:**
- Pair programming: 72% (↑15%)
- Test coverage: 94% (↑3%)
- Deploy frequency: 12 deploys (↑4)
- Customer feedback: 3 conversations
```

---

## 🛠️ Ferramentas Diárias

### **IDE Setup para XP**
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "testing.automaticallyOpenPeekView": "failureInVisibleDocument",
  "liveshare.presence": true,
  "liveshare.showInStatusBar": "whileCollaborating"
}
```

### **Git Hooks para Quality**
```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "🧪 Running tests before commit..."
npm run test:unit
if [ $? -ne 0 ]; then
  echo "❌ Tests failed. Commit aborted."
  exit 1
fi

echo "🔍 Running linter..."
npm run lint
if [ $? -ne 0 ]; then
  echo "❌ Linting failed. Commit aborted."
  exit 1
fi

echo "✅ All checks passed. Committing..."
```

### **Monitoring Diário**
```bash
# Script para status diário
#!/bin/bash
# daily-status.sh

echo "📊 CarMatch Daily Status $(date)"
echo "=================================="

echo "🧪 Test Status:"
npm run test:coverage | grep "All files"

echo "🚀 Build Status:"
curl -s https://api.github.com/repos/carmatch/status | jq '.state'

echo "📈 Production Health:"
curl -s https://api.carmatch.com/health | jq '.status'

echo "🎯 Performance:"
curl -s https://api.carmatch.com/metrics | jq '.response_time'
```

---

## 🎭 XP Mindset Diário

### **Mantras para o Dia**
```markdown
🧠 **Mindset XP:**

💭 "Simplicidade é a máxima sofisticação"
  → Sempre escolher solução mais simples que funciona

💭 "Se dói, faça mais frequentemente"  
  → Deploy, refactor, testes - quanto mais, melhor

💭 "Código é comunicação"
  → Escrever para humanos, não máquinas

💭 "Feedback rápido é feedback valioso"
  → Buscar validação em ciclos curtos

💭 "Qualidade não é negociável"
  → Nunca sacrificar qualidade por velocidade
```

### **Checklist de Final de Dia**
```markdown
✅ **Before leaving:**

🧪 **Código:**
- [ ] Todos os testes passando
- [ ] Código commitado e pushado
- [ ] Build verde no CI
- [ ] Coverage mantido/melhorado

🤝 **Colaboração:**
- [ ] Pair session realizada
- [ ] Knowledge compartilhado
- [ ] Impedimentos comunicados
- [ ] Próxima sessão agendada

📋 **Amanhã:**
- [ ] Próxima tarefa identificada
- [ ] Critério de "pronto" definido
- [ ] Pair partner confirmado
- [ ] Ambiente preparado
```

---

## 🚨 Troubleshooting XP

### **Quando as Coisas Dão Errado**

#### **Build Quebrado** 🔥
```markdown
🚨 **Ação Imediata:**
1. Parar todo development
2. Identificar último commit que quebrou
3. Reverter ou corrigir em pair
4. Revisar processo que permitiu quebra

🔍 **Root Cause Analysis:**
- Por que os testes não pegaram?
- Como melhorar o pipeline?
- Que prática XP foi ignorada?
```

#### **Pair Programming Não Funciona** 😤
```markdown
🤔 **Problemas Comuns:**
- Personalities incompatíveis → Rotacionar pairs
- Skill gap muito grande → Mentorar gradualmente  
- Falta de foco → Definir objetivo claro da sessão
- Cansaço → Fazer breaks frequentes (Pomodoro)

💡 **Soluções:**
- Mob programming (3+ pessoas)
- Async collaboration com code review
- Pair + solo rotation
```

#### **Testes Demoram Muito** ⏰
```markdown
🐌 **Otimizações:**
- Parallel execution
- Mocking external services
- Test data factories
- Focus no happy path primeiro
- Split unit vs integration

⚡ **Meta:** Unit tests < 30s, Integration < 5min
```

---

## 📚 Recursos de Apoio

### **Daily Reading (5-10 min/dia)**
- [Extreme Programming Explained](https://www.amazon.com/Extreme-Programming-Explained-Embrace-Change/dp/0321278658) - 1 capítulo/semana
- [Test Driven Development](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530) - Técnicas específicas
- [Refactoring](https://refactoring.com/) - Patterns de melhoria

### **Comunidade XP**
- **Daily Slack**: #xp-practices channel
- **Weekly Show & Tell**: Sexta 17h - compartilhar learnings
- **Monthly XP Book Club**: Discussão aprofundada

### **Métricas Mensais**
```markdown
📊 **Review Mensal XP:**
- Pair programming hours
- Test coverage trend  
- Deploy frequency
- Customer satisfaction
- Team happiness
- Technical debt reduction
```

---

**Lembre-se**: XP é sobre pessoas, não processos. Adapte conforme necessário! 🚀
