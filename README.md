# 🚗 FacilIAuto v2.0 - Sistema Prático de Recomendação de Carros

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-150+-brightgreen.svg)](./tests/)
[![Coverage](https://img.shields.io/badge/Coverage-90%+-brightgreen.svg)](./tests/)
[![XP](https://img.shields.io/badge/Methodology-XP/TDD-orange.svg)](./docs/TESTING_STRATEGY_XP.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

> **Sistema inteligente que recomenda carros baseado no que REALMENTE importa para o brasileiro**

## 🎯 **Sobre o Projeto**

O FacilIAuto v2.0 é um sistema de recomendação de carros revolucionário que entende as **necessidades práticas** dos brasileiros. Diferente de sistemas genéricos, nosso algoritmo considera critérios reais como:

- 💰 **Orçamento rigoroso** - Não perde tempo com carros fora da faixa
- 🎯 **Motivo de compra** - Trabalho vs Família vs Investimento 
- 🚗 **Frequência de uso** - Todo dia vs esporádico muda tudo
- 👥 **Necessidades reais** - Solo, casal, família, cargo
- ⛽ **Economia prática** - Máxima economia vs performance
- 🛡️ **Confiabilidade** - Dados reais de marcas (Toyota 95, Fiat 65)
- 💹 **Valor de revenda** - Mercado brasileiro atual
- 🔧 **Custo de manutenção** - Peças baratas vs caras
- ❤️ **"Eu quero"** - Respeita preferências pessoais

## 🚀 **Quick Start**

### **Pré-requisitos**
```bash
Python 3.11+
```

### **Instalação Rápida**
```bash
# 1. Clone o repositório
git clone https://github.com/usuario/faciliauto.git
cd faciliauto

# 2. Instale dependências
pip install -r requirements.txt

# 3. Execute o sistema
python main.py
```

### **Acesse o Sistema**
- 🏠 **Questionário**: http://localhost:8000
- 📊 **Admin**: http://localhost:8000/admin.html
- 🔧 **API Docs**: http://localhost:8000/docs

## 📁 **Estrutura do Projeto**

```
faciliauto/
├── 🐍 main.py                      # FastAPI app principal
├── 🧠 recommendations.py           # Engine de recomendação prática
├── 📦 requirements.txt             # Dependências core
├── 📦 requirements-test.txt        # Dependências de teste
├── ⚙️ pytest.ini                  # Configuração de testes
├── 🌐 static/
│   ├── index.html                 # Questionário prático redesenhado
│   ├── results.html               # Página de recomendações
│   └── admin.html                 # Dashboard administrativo
├── 🧪 tests/                      # Suíte de testes XP
│   ├── unit/                      # Testes unitários TDD
│   ├── integration/               # Testes de integração
│   ├── e2e/                       # Testes end-to-end
│   └── fixtures/                  # Dados de teste
├── 📚 docs/                       # Documentação
│   └── TESTING_STRATEGY_XP.md     # Estratégia de testes XP
├── 🚀 .github/workflows/          # Pipeline CI/CD
│   └── xp_ci_pipeline.yml         # Pipeline de qualidade
└── 🛠️ scripts/
    └── run_tests_xp.sh            # Script de execução de testes
```

## 🎯 **Funcionalidades Práticas**

### **1. Questionário Inteligente (8 Perguntas)**
- **Faixa de preço** - Filtro eliminatório principal
- **Motivo principal** - Por que está comprando?
- **Frequência de uso** - Com que frequência vai usar?
- **Necessidades de espaço** - Quantas pessoas + bagagem?
- **Prioridade de combustível** - Quanto te preocupa o consumo?
- **Experiência com carros** - Primeira vez ou experiente?
- **Prioridade máxima** - O que é MAIS importante?
- **Preferência de marca** - Marcas que você confia

### **2. Engine de Recomendação Prática**
```python
# Pesos realistas baseados em necessidades reais
PESOS = {
    'motivo_principal': 30%,    # Maior peso - define o perfil
    'frequencia_uso': 20%,      # Alto peso - impacta durabilidade
    'necessidades_espaco': 15%, # Médio peso - funcionalidade
    'economia_combustivel': 15%, # Médio peso - custo operacional
    'prioridade_maxima': 10%,   # Baixo peso - refinamento
    'experiencia_usuario': 5%,  # Baixo peso - adequação
    'preferencia_marca': 5%     # Boost adicional - "eu quero"
}
```

### **3. Dados de Mercado Real**
- **Confiabilidade**: Toyota (95), Honda (92), Chevrolet (80), Fiat (65)
- **Revenda**: Corolla (90), Civic (88), Onix (78), Kwid (65)
- **Manutenção**: Chevrolet (Baixo), Honda (Médio), BMW (Muito Alto)

### **4. Sistema de Boost Inteligente**
```python
# Palavras-chave que aumentam score
"uber" + carro_economico = +15 pontos
"economia" + consumo_12km/l+ = +10 pontos
"família" + sedan/suv = +12 pontos
"confiável" + toyota/honda = +8 pontos
```

## 🧪 **Metodologia XP Implementada**

### **Test-Driven Development (TDD)**
```
🔴 RED   → Escrever teste que falha
🟢 GREEN → Implementação mínima que passa
🔵 REFACTOR → Melhorar código mantendo testes
```

### **Pirâmide de Testes**
```
        🔺 E2E (Poucos, Lentos, Valiosos)
       🔺🔺 Integration (Médios, Médios)  
    🔺🔺🔺🔺 Unit (Muitos, Rápidos, Baratos)
```

### **Execução de Testes**
```bash
# Testes por categoria
./scripts/run_tests_xp.sh unit        # Testes unitários rápidos
./scripts/run_tests_xp.sh integration # Testes de integração
./scripts/run_tests_xp.sh e2e         # Testes end-to-end
./scripts/run_tests_xp.sh all         # Suíte completa

# Testes por user story
./scripts/run_tests_xp.sh story1      # Recomendações práticas
./scripts/run_tests_xp.sh story2      # Sistema de leads
```

## 🔧 **API Endpoints**

### **Recomendações**
```http
POST /api/recommendations
{
  "answers": {
    "budget": "30k_50k",
    "main_purpose": "work_app",
    "frequency": "daily_work",
    "space_needs": "solo",
    "fuel_priority": "maximum_economy",
    "top_priority": "economy",
    "experience_level": "some_experience",
    "brand_preference": ["toyota", "chevrolet"]
  },
  "details": "Vou trabalhar como motorista de Uber",
  "session_id": "practical_session_123"
}
```

### **Resposta**
```json
{
  "recommendations": [
    {
      "id": 1,
      "brand": "Toyota",
      "model": "Etios",
      "year": 2020,
      "price": 42000,
      "score": 92.5,
      "reasons": [
        "🎯 Excelente compatibilidade com suas necessidades",
        "🚖 Economia ideal para trabalho com apps",
        "🛡️ Marca muito confiável"
      ],
      "reliability_score": 95,
      "resale_score": 85,
      "maintenance_cost": "Baixo"
    }
  ],
  "total_found": 5,
  "session_id": "practical_session_123",
  "criteria_used": { ... }
}
```

### **Outros Endpoints**
- `GET /api/cars/{id}` - Detalhes do carro
- `POST /api/leads` - Gerar lead de interesse
- `GET /api/admin/stats` - Estatísticas do sistema
- `GET /api/admin/leads` - Lista de leads
- `GET /api/health` - Health check

## 💾 **Schema do Banco**

### **Tabela Cars**
```sql
CREATE TABLE cars (
    id INTEGER PRIMARY KEY,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    price INTEGER NOT NULL,
    category TEXT NOT NULL,           -- hatch, sedan, suv, pickup
    fuel_type TEXT DEFAULT 'flex',
    transmission TEXT NOT NULL,       -- manual, automatic
    consumption REAL NOT NULL,        -- km/l
    seats INTEGER DEFAULT 5,
    safety_rating INTEGER DEFAULT 4,
    region TEXT DEFAULT 'sp',
    photo_url TEXT,
    available BOOLEAN DEFAULT 1,
    -- Campos práticos novos
    reliability_score REAL,           -- 0-100 (confiabilidade)
    resale_score REAL,               -- 0-100 (valor revenda)
    maintenance_cost TEXT            -- Baixo, Médio, Alto, Muito Alto
);
```

### **Tabela Leads**
```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    car_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES cars (id)
);
```

## 🎮 **Cenários de Uso**

### **Cenário 1: Motorista de App**
```
Input: Budget R$ 30-50k, trabalho diário, máxima economia
Output: Toyota Etios (92 pts) - "Ideal para trabalho com apps"
```

### **Cenário 2: Família com Crianças**
```
Input: Budget R$ 80-120k, família, espaço, confiabilidade
Output: Honda Civic (87 pts) - "Espaço adequado para família"
```

### **Cenário 3: Primeiro Carro**
```
Input: Budget até R$ 40k, iniciante, simplicidade
Output: Chevrolet Onix Joy (85 pts) - "Fácil de dirigir e manter"
```

### **Cenário 4: Investimento**
```
Input: Boa revenda, não muito antigo, marca tradicional
Output: Toyota Corolla (89 pts) - "Excelente valor de revenda"
```

## 🚀 **Deploy e Produção**

### **Deploy Local**
```bash
python main.py
# Servidor em http://localhost:8000
```

### **Deploy Railway/Render**
```bash
# Configurar variáveis de ambiente
DATABASE_URL=sqlite:///faciliauto.db
PORT=8000

# Deploy automático via Git
git push origin main
```

### **Deploy Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

## 📊 **Métricas de Qualidade**

- ✅ **150+ Testes** automatizados
- ✅ **90%+ Cobertura** de código
- ✅ **< 2s Response Time** para recomendações
- ✅ **85%+ Minimum Coverage** exigido
- ✅ **Zero Errors** em linting
- ✅ **Pipeline CI/CD** com quality gate

## 🤝 **Contribuindo (Metodologia XP)**

### **Workflow XP**
1. **📋 User Story** - Escreva história do usuário
2. **🔴 Red** - Teste que falha primeiro
3. **🟢 Green** - Implementação mínima
4. **🔵 Refactor** - Melhore mantendo testes
5. **✅ Integration** - Garanta que tudo funciona
6. **🚀 Deploy** - Entregue valor rapidamente

### **Comandos Úteis**
```bash
# Executar todos os testes
./scripts/run_tests_xp.sh all

# Executar com coverage
pytest --cov=. --cov-report=html

# Linting e formatação
flake8 . && black . && isort .

# Testes de performance
pytest tests/ -m performance

# Pipeline completo local
./scripts/run_tests_xp.sh all && flake8 . && black --check .
```

## 📚 **Documentação Adicional**

- 📖 [Estratégia de Testes XP](./docs/TESTING_STRATEGY_XP.md)
- 🔧 [API Documentation](http://localhost:8000/docs)
- 🎯 [User Stories](./tests/) - Implementadas como testes
- 🚀 [CI/CD Pipeline](./.github/workflows/xp_ci_pipeline.yml)

## 🏆 **Características Técnicas**

### **Backend**
- **FastAPI** - Framework moderno e rápido
- **SQLite** - Banco simples e eficiente
- **Pydantic** - Validação de dados robusta
- **Uvicorn** - Servidor ASGI de alta performance

### **Frontend**
- **Vanilla JavaScript** - Sem frameworks pesados
- **Tailwind CSS** - Design system moderno
- **Responsive Design** - Mobile-first approach
- **Progressive Enhancement** - Funciona sem JS

### **Testing**
- **Pytest** - Framework de testes Python
- **Playwright** - Testes E2E modernos
- **Factory Boy** - Geração de dados de teste
- **Coverage.py** - Análise de cobertura

### **DevOps**
- **GitHub Actions** - CI/CD automatizado
- **Docker** - Containerização
- **Railway/Render** - Deploy simplificado
- **SQLite** - Zero configuração de banco

## 🎯 **Roadmap**

### **v2.1 (Próxima)**
- [ ] Sistema de favoritos
- [ ] Comparação lado a lado
- [ ] Histórico de buscas
- [ ] Notificações de preço

### **v2.2 (Futuro)**
- [ ] Integração com APIs de concessionárias
- [ ] Sistema de avaliações
- [ ] Chat com vendedores
- [ ] App mobile nativo

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.

## 👥 **Equipe**

Desenvolvido com ❤️ seguindo metodologia XP e princípios de Clean Code.

---

**🚗 FacilIAuto v2.0 - Recomendações inteligentes baseadas no que realmente importa! 🇧🇷**