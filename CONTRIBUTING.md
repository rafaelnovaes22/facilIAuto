# 🤝 **Contributing to FacilIAuto**

## 🎯 **Metodologia XP (Extreme Programming)**

Este projeto segue rigorosamente a metodologia XP. Todas as contribuições devem aderir aos princípios e práticas XP.

---

## 📋 **Antes de Contribuir**

### **1. Leia a Documentação**
- `README.md` - Visão geral do projeto
- `CarRecommendationSite/XP-Methodology.md` - Metodologia XP completa
- `CarRecommendationSite/XP-Daily-Guide.md` - Guia diário de práticas
- `REESTRUTURACAO-COMPLETA.md` - Arquitetura atual

### **2. Configure o Ambiente**
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/faciliauto.git
cd faciliauto

# Instale dependências
# Backend (Python)
cd platform/backend
pip install -r requirements.txt

# Frontend legacy (Node.js)
cd ../../RobustCar/frontend
npm install

# XP Environment (para testes)
cd ../../CarRecommendationSite
./setup-xp.sh  # Linux/Mac
# ou
setup-xp.bat   # Windows
```

---

## 🧪 **Test-Driven Development (TDD)**

### **Ciclo Red-Green-Refactor**
```
🔴 RED    → Escrever teste que falha
🟢 GREEN  → Implementar código mínimo para passar
🔵 REFACTOR → Melhorar código mantendo testes
```

### **Exemplo Prático**
```typescript
// 1. RED: Escrever teste
describe('UnifiedRecommendationEngine', () => {
  it('deve retornar carros de múltiplas concessionárias', () => {
    const engine = new UnifiedRecommendationEngine()
    const results = engine.recommend(userProfile)
    
    // Verificar diversidade de concessionárias
    const dealerships = new Set(results.map(r => r.car.dealership_id))
    expect(dealerships.size).toBeGreaterThan(1)
  })
})

// 2. GREEN: Implementar funcionalidade
// ... código mínimo ...

// 3. REFACTOR: Melhorar código
// ... otimizações ...
```

---

## 🌐 **Testes End-to-End (E2E)**

### **Executar Testes E2E**
```bash
cd CarRecommendationSite/frontend

# Interface gráfica
npm run e2e:open

# Headless (CI/CD)
npm run e2e

# Smoke tests
npm run e2e:smoke
```

### **Estrutura de Testes E2E**
```
cypress/
├── e2e/
│   ├── user-journey.cy.ts      # Jornada completa do usuário (398 linhas)
│   └── simple-validation.cy.ts # Validações básicas
├── fixtures/
│   └── cars.json               # Dados de teste
└── support/
    └── commands.ts             # Comandos customizados
```

### **Criar Novo Teste E2E**
```typescript
describe('Nova Feature', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('deve realizar ação específica', () => {
    // Arrange
    cy.get('[data-testid="elemento"]').should('be.visible')
    
    // Act
    cy.get('[data-testid="botao"]').click()
    
    // Assert
    cy.get('[data-testid="resultado"]').should('contain', 'Esperado')
  })
})
```

---

## 🔄 **Workflow de Contribuição**

### **1. Criar Branch**
```bash
# Formato: tipo/descricao-curta
git checkout -b feature/multi-tenant-frontend
git checkout -b fix/recommendation-score-bug
git checkout -b test/e2e-mobile-flow
git checkout -b docs/api-documentation
```

### **2. Desenvolver com TDD**
```bash
# 1. Escrever teste
npm test -- --watch

# 2. Implementar código
# ... desenvolvimento ...

# 3. Validar testes passando
npm test

# 4. Executar E2E
npm run e2e
```

### **3. Validar Qualidade**
```bash
# Linting
npm run lint

# Type checking
npm run type-check

# Coverage
npm run test:coverage

# Validação XP completa
cd CarRecommendationSite
./run-full-tests.sh  # Linux/Mac
# ou
run-full-tests.bat   # Windows
```

### **4. Commit com Padrão**
```bash
# Formato: tipo(escopo): mensagem

git commit -m "feat(engine): adiciona suporte multi-concessionária"
git commit -m "test(e2e): adiciona testes de jornada mobile"
git commit -m "fix(api): corrige score de recomendação"
git commit -m "docs(readme): atualiza guia de instalação"
git commit -m "refactor(models): simplifica estrutura de Car"
```

**Tipos de commit:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `test`: Adiciona ou modifica testes
- `docs`: Documentação
- `refactor`: Refatoração de código
- `style`: Formatação, sem mudança de lógica
- `perf`: Melhoria de performance
- `chore`: Tarefas de manutenção

### **5. Push e Pull Request**
```bash
git push origin feature/multi-tenant-frontend
```

**No GitHub, criar PR com:**
- Título claro e descritivo
- Descrição detalhada das mudanças
- Screenshots/GIFs se UI
- Checklist de testes executados
- Link para issues relacionadas

---

## ✅ **Checklist de PR**

Antes de submeter PR, garantir:

### **Código**
- [ ] TDD: Testes escritos ANTES do código
- [ ] Todos os testes unitários passando
- [ ] Todos os testes E2E passando
- [ ] Coverage ≥ 80%
- [ ] Linting sem erros
- [ ] Type checking sem erros
- [ ] Código refatorado e limpo

### **XP**
- [ ] Pair programming realizado (quando aplicável)
- [ ] Código revisado por par
- [ ] Simple design aplicado (YAGNI)
- [ ] Documentação atualizada
- [ ] Práticas XP seguidas

### **Documentação**
- [ ] README atualizado (se necessário)
- [ ] Comentários em código complexo
- [ ] Changelog atualizado
- [ ] API docs atualizadas (se mudanças de API)

### **Testes**
- [ ] Testes unitários adicionados/atualizados
- [ ] Testes E2E adicionados/atualizados
- [ ] Edge cases cobertos
- [ ] Testes rodando em CI/CD

---

## 🎯 **Padrões de Código**

### **Python (Backend)**
```python
# PEP 8 compliant
# Type hints obrigatórios
from typing import List, Dict, Optional

def recommend_cars(
    profile: UserProfile,
    limit: int = 10
) -> List[Recommendation]:
    """
    Gerar recomendações de carros.
    
    Args:
        profile: Perfil do usuário
        limit: Número máximo de resultados
        
    Returns:
        Lista de recomendações ordenadas por score
    """
    pass
```

### **TypeScript (Frontend)**
```typescript
// Strict mode
// Interfaces para todos os tipos

interface Car {
  id: string
  dealership_id: string
  nome: string
  preco: number
}

// Arrow functions para componentes
export const CarCard: React.FC<CarCardProps> = ({ car }) => {
  return <div>{car.nome}</div>
}
```

### **React Components**
```typescript
// Functional components com hooks
// Props com TypeScript
// Data-testid para testes E2E

interface Props {
  car: Car
  onSelect: (car: Car) => void
}

export const CarCard: React.FC<Props> = ({ car, onSelect }) => {
  return (
    <div data-testid={`car-card-${car.id}`}>
      <h3>{car.nome}</h3>
      <button 
        data-testid={`select-car-${car.id}`}
        onClick={() => onSelect(car)}
      >
        Selecionar
      </button>
    </div>
  )
}
```

---

## 🐛 **Reportar Bugs**

### **Template de Issue**
```markdown
## 🐛 Descrição do Bug
[Descrição clara e concisa]

## 🔄 Passos para Reproduzir
1. Ir para '...'
2. Clicar em '...'
3. Rolar até '...'
4. Ver erro

## ✅ Comportamento Esperado
[O que deveria acontecer]

## ❌ Comportamento Atual
[O que está acontecendo]

## 📷 Screenshots
[Se aplicável]

## 🖥️ Ambiente
- OS: [Windows 10, Ubuntu 22.04, etc]
- Browser: [Chrome 120, Firefox 115, etc]
- Node: [v18.17.0]
- Python: [3.11.0]

## 📋 Logs/Erros
```
[Cole logs ou mensagens de erro]
```

## 🔍 Contexto Adicional
[Qualquer outra informação relevante]
```

---

## 💡 **Sugerir Features**

### **Template de Feature Request**
```markdown
## 🎯 Problema a Resolver
[Qual problema esta feature resolve?]

## 💡 Solução Proposta
[Descreva sua solução]

## 🔄 Alternativas Consideradas
[Outras soluções que você considerou]

## 📊 Benefícios
- Benefício 1
- Benefício 2

## 🎨 Mockups/Wireframes
[Se aplicável]

## 📝 Contexto Adicional
[Informações relevantes]
```

---

## 🏆 **Boas Práticas**

### **Git**
- Commits pequenos e atômicos
- Mensagens de commit descritivas
- Branch por feature/fix
- Rebase antes de PR (se necessário)

### **Código**
- KISS (Keep It Simple, Stupid)
- DRY (Don't Repeat Yourself)
- YAGNI (You Aren't Gonna Need It)
- Single Responsibility Principle

### **Testes**
- AAA (Arrange, Act, Assert)
- Testes independentes
- Nomes descritivos
- Coverage ≥ 80%

### **XP**
- TDD sempre
- Pair programming quando possível
- Refactoring contínuo
- Simple design

---

## 📞 **Ajuda e Suporte**

### **Documentação**
- [XP Methodology](CarRecommendationSite/XP-Methodology.md)
- [XP Daily Guide](CarRecommendationSite/XP-Daily-Guide.md)
- [Platform README](platform/README.md)
- [Validation Report](CarRecommendationSite/VALIDATION-REPORT.md)

### **Contato**
- 📧 Email: dev@faciliauto.com.br
- 💬 Discord: [Link do servidor]
- 🐛 Issues: GitHub Issues
- 📖 Docs: Wiki do projeto

---

## 📄 **Licença**

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

**🚀 Obrigado por contribuir com o FacilIAuto! Juntos estamos construindo o futuro das vendas automotivas no Brasil.**

