# 🚗 **FacilIAuto** - Sistema de Recomendação de Carros com IA

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![LangGraph](https://img.shields.io/badge/LangGraph-AI%20Agents-orange)
![Tests](https://img.shields.io/badge/Tests-22%2F22%20Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-90%25+-success)

## 📋 **Visão Geral**

O **FacilIAuto** é uma plataforma inteligente de recomendação de carros usados que utiliza **Inteligência Artificial** e **agentes especializados** para personalizar sugestões baseadas no perfil único de cada usuário. Com **memória persistente** e **6 agentes IA especializados**, oferece experiência conversacional avançada e recomendações precisas.

### **🎯 Principais Funcionalidades**

- 🤖 **6 Agentes IA Especializados** (Técnico, Financeiro, Comparação, Manutenção, Avaliação, Geral)
- 🧠 **Memória Persistente** entre sessões com contexto inteligente
- ⚡ **Performance Enterprise** (<2s tempo médio, suporta 25+ usuários simultâneos)
- 📊 **Sistema de Pontuação Multi-critério** com pesos personalizáveis
- 🔍 **Busca Inteligente** com fuzzy matching para marcas/modelos
- 💬 **Chatbot Conversacional** integrado na página de detalhes
- 📈 **Analytics Avançadas** de comportamento e preferências
- 🧪 **22 Testes E2E** garantindo qualidade total

---

## 🏗️ **Arquitetura do Sistema**

```mermaid
graph TB
    subgraph "🌐 Frontend"
        A[Interface Web Bootstrap 5]
        B[Chatbot Integrado]
        C[Questionário Inteligente]
    end
    
    subgraph "📡 Backend API"
        D[FastAPI Application]
        E[Sistema de Busca]
        F[LangGraph Chatbot]
    end
    
    subgraph "🤖 Agentes IA"
        G[Agente Técnico]
        H[Agente Financeiro]
        I[Agente Comparação]
        J[Agente Manutenção]
        K[Agente Avaliação]
        L[Agente Geral]
    end
    
    subgraph "💾 Dados"
        M[PostgreSQL Database]
        N[Sistema de Memória]
        O[Analytics Engine]
    end
    
    A --> D
    B --> F
    C --> E
    D --> E
    D --> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    F --> L
    E --> M
    F --> N
    N --> M
    O --> M
```

---

## 📁 **Estrutura do Projeto**

```
facilIAuto/
├── 📱 app/                          # Código principal da aplicação
│   ├── 🤖 langgraph_chatbot_*.py   # Sistema LangGraph com agentes IA
│   ├── 🧠 memory_*.py              # Sistema de memória persistente
│   ├── 🔍 busca_inteligente.py     # Engine de busca e recomendação
│   ├── 🌐 api.py                   # FastAPI endpoints e interface
│   ├── 📊 models.py                # Modelos Pydantic de dados
│   └── 🗄️ database.py             # Acesso ao PostgreSQL
├── 🧪 tests/                       # Suíte completa de testes
│   ├── 🔄 e2e/                     # Testes End-to-End LangGraph
│   ├── 🔗 integration/             # Testes de integração
│   └── ⚡ unit/                    # Testes unitários
├── 📚 docs/                        # Documentação completa
│   ├── 🤖 LANGGRAPH_*.md          # Documentação LangGraph
│   ├── 🧠 MEMORY_*.md             # Documentação memória persistente
│   └── 📋 *.md                    # Outras documentações
├── 🔧 scripts/                     # Scripts utilitários
├── 📊 logs/                        # Logs do sistema
├── 💾 backups/                     # Backups e dados históricos
├── 🎨 static/                      # Arquivos estáticos (CSS, JS, imgs)
├── ⚙️ .github/                     # CI/CD workflows
└── 🚀 main.py                      # Entry point da aplicação
```

---

## 🚀 **Instalação e Configuração**

### **📋 Pré-requisitos**

- Python 3.11+
- PostgreSQL 13+ (ou SQLite para desenvolvimento)
- Node.js 16+ (para testes E2E com Playwright)

### **🔧 Instalação**

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/rafaelnovaes22/facilIAuto.git
   cd facilIAuto
   ```

2. **Configurar ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt  # Para desenvolvimento
   ```

4. **Configurar banco de dados:**
   ```bash
   # PostgreSQL (Produção)
   export DATABASE_URL="postgresql://user:pass@localhost/faciliauto"
   
   # SQLite (Desenvolvimento) - Configuração automática
   ```

5. **Executar aplicação:**
   ```bash
   python main.py
   ```

6. **Acessar aplicação:**
   - Interface Web: http://localhost:8000
   - Documentação API: http://localhost:8000/docs
   - Chatbot: http://localhost:8000/carro/1

---

## 🧪 **Executar Testes**

### **🏃‍♂️ Testes Rápidos (Essenciais)**
```bash
python tests/run_langgraph_e2e_tests.py --quick
```

### **📊 Testes por Categoria**
```bash
# Workflow completo
python tests/run_langgraph_e2e_tests.py --category workflow

# Agentes especializados
python tests/run_langgraph_e2e_tests.py --category agents

# Performance e carga
python tests/run_langgraph_e2e_tests.py --category performance

# Sistema de memória
python tests/run_langgraph_e2e_tests.py --category memory
```

### **🔍 Testes Completos com Coverage**
```bash
pytest --cov=app --cov-report=html
```

### **⚡ Testes de Performance**
```bash
pytest tests/e2e/ -m langgraph_performance
```

---

## 🤖 **Sistema de Agentes IA**

### **🎯 Agentes Especializados**

| Agente | Especialidade | Exemplos de Perguntas |
|--------|---------------|----------------------|
| **🔧 Técnico** | Motor, consumo, especificações | "Qual a potência?", "Como é o câmbio?" |
| **💰 Financeiro** | Financiamento, parcelas, entrada | "Como funciona o financiamento?", "Qual a entrada?" |
| **⚖️ Comparação** | Comparar com concorrentes | "Compare com Honda Civic", "É melhor que..." |
| **🛠️ Manutenção** | Custos, revisões, peças | "Qual o custo de manutenção?", "Quando revisar?" |
| **📊 Avaliação** | Preços, mercado, depreciação | "Preço está justo?", "Como está no mercado?" |
| **🤝 Geral** | Questões gerais e fallback | "Me conta sobre este carro" |

### **🧠 Memória Persistente**

- **User Session Tracking**: Reconhece usuários entre sessões
- **Contexto Automático**: Extrai preferências das conversas
- **Estado Enriquecido**: LangGraph melhorado com histórico
- **Analytics Real-time**: Insights de comportamento e padrões

---

## 📊 **Métricas de Performance**

### **⚡ Benchmarks Validados**

| Métrica | Baseline | Sob Carga | Stress |
|---------|----------|-----------|---------|
| **Tempo Médio** | 1.2s | 2.8s | 4.5s |
| **Taxa de Sucesso** | 100% | 95% | 75% |
| **Throughput** | - | 8.5 req/s | 5.2 req/s |
| **Usuários Simultâneos** | - | 10 | 25 |
| **Overhead Memória** | - | <15% | <20% |

### **🎯 Qualidade dos Agentes**

| Agente | Precisão Roteamento | Qualidade Resposta |
|--------|-------------------|------------------|
| **Técnico** | 95% | 85% |
| **Financeiro** | 90% | 80% |
| **Comparação** | 88% | 82% |
| **Manutenção** | 92% | 78% |
| **Avaliação** | 85% | 75% |

---

## 🔧 **Scripts Utilitários**

O projeto inclui diversos scripts para manutenção e desenvolvimento:

```bash
# Análise e backup de imagens
python scripts/analyze_vehicle_images.py
python scripts/backup_database_images.py

# Atualização de dados
python scripts/update_vehicle_images.py
python scripts/fix_database_images.py

# Scraping e coleta
python scripts/vehicle_image_scraper.py

# Exploração do banco
python scripts/explorar_banco.py
```

---

## 📚 **Documentação Completa**

- 📖 **[Documentação LangGraph](docs/LANGGRAPH_CHATBOT_DOCUMENTATION.md)** - Arquitetura dos agentes IA
- 🧠 **[Sistema de Memória](docs/MEMORY_SYSTEM_IMPLEMENTATION.md)** - Memória persistente
- 🧪 **[Testes E2E](docs/LANGGRAPH_E2E_TESTS_DOCUMENTATION.md)** - Suíte completa de testes
- 🏗️ **[Sistema de Marcas](docs/ADVANCED_BRAND_SYSTEM_SUMMARY.md)** - Fuzzy matching avançado
- ⚡ **[Metodologia XP](docs/XP_METHODOLOGY.md)** - Práticas de desenvolvimento

---

## 🤝 **Contribuição**

### **🔄 Fluxo de Desenvolvimento**

1. Fork o projeto
2. Crie feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Execute testes (`pytest`)
4. Commit mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
5. Push para branch (`git push origin feature/nova-funcionalidade`)
6. Abra Pull Request

### **📋 Padrões de Código**

- **Linting**: `flake8` para estilo de código
- **Formatting**: `black` para formatação automática
- **Type Checking**: `mypy` para verificação de tipos
- **Security**: `bandit` para análise de segurança
- **Testing**: Cobertura mínima de 90%

---

## 🏆 **Status do Projeto**

### **✅ Funcionalidades Implementadas**

- [x] Sistema de busca inteligente com multi-critérios
- [x] 6 agentes IA especializados com LangGraph
- [x] Memória persistente entre sessões
- [x] Interface web responsiva com Bootstrap 5
- [x] Chatbot integrado na página de detalhes
- [x] Sistema de recomendação personalizado
- [x] 22 testes E2E com 100% de sucesso
- [x] Performance enterprise validada
- [x] Documentação completa
- [x] CI/CD com GitHub Actions

### **🎯 Roadmap Futuro**

- [ ] Dashboard administrativo
- [ ] API mobile (React Native)
- [ ] Integração com CRMs automotivos
- [ ] Machine Learning avançado para recomendações
- [ ] Análise de sentimento nas conversas
- [ ] Sistema de notificações push
- [ ] Suporte multi-idiomas

---

## 📄 **Licença**

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## 👥 **Equipe**

- **Desenvolvimento**: Rafael Novaes & FacilIAuto AI Team
- **Arquitetura IA**: Sistema LangGraph com agentes especializados
- **QA**: Suíte completa de testes automatizados
- **DevOps**: CI/CD com GitHub Actions

---

## 📞 **Suporte**

- 📧 **Email**: suporte@faciliauto.com.br
- 📱 **GitHub Issues**: [Reportar problemas](https://github.com/rafaelnovaes22/facilIAuto/issues)
- 📚 **Documentação**: [Wiki do projeto](docs/)

---

**🚗 Transformando a experiência de compra de carros usados com Inteligência Artificial!** ✨