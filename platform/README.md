# 🚗 **FacilIAuto - Plataforma Unificada Multi-Concessionária**

## 🎯 **Visão Geral**

Plataforma única que agrega carros de **múltiplas concessionárias**, permitindo que usuários encontrem o carro ideal comparando opções de diferentes vendedores.

### ✅ **Status Atual**
- ✅ **Backend unificado** com recommendation engine
- ✅ **3 concessionárias** ativas (RobustCar + 2 mock)
- ✅ **129+ carros** disponíveis para recomendação
- ✅ **Sistema de scoring** multi-concessionária
- ⏳ **Frontend** em desenvolvimento

---

## 📊 **Dados Disponíveis**

### **Concessionárias Ativas**

| ID | Nome | Cidade | Estado | Carros | Status |
|----|------|--------|--------|--------|--------|
| `robustcar` | RobustCar São Paulo | São Paulo | SP | 89 | ✅ Dados reais |
| `autocenter` | AutoCenter Rio de Janeiro | Rio de Janeiro | RJ | 20 | ⚠️ Mock |
| `carplus` | CarPlus Belo Horizonte | Belo Horizonte | MG | 20 | ⚠️ Mock |

**Total**: 129+ carros de 3 concessionárias

---

## 🏗️ **Estrutura do Projeto**

```
platform/
├── backend/
│   ├── models/                 # Modelos de dados
│   │   ├── car.py             # Modelo Car com dealership_id
│   │   ├── dealership.py      # Modelo Dealership
│   │   └── user_profile.py    # Perfil do usuário
│   │
│   ├── services/              # Serviços de negócio
│   │   └── unified_recommendation_engine.py  # Engine unificado
│   │
│   ├── data/                  # Dados consolidados
│   │   ├── dealerships.json   # Lista de concessionárias
│   │   ├── robustcar_estoque.json
│   │   ├── autocenter_estoque.json
│   │   └── carplus_estoque.json
│   │
│   └── migrate_data.py        # Script de migração
│
├── frontend/                  # Frontend React (em desenvolvimento)
│   └── src/
│       ├── pages/
│       ├── components/
│       └── services/
│
├── scrapers/                  # Scrapers por concessionária
└── admin/                     # Painel administrativo
```

---

## 🚀 **Como Usar o Recommendation Engine**

### **1. Exemplo Básico**

```python
from backend.services.unified_recommendation_engine import UnifiedRecommendationEngine
from backend.models import UserProfile

# Inicializar engine
engine = UnifiedRecommendationEngine(data_dir="backend/data")

# Criar perfil do usuário
profile = UserProfile(
    orcamento_min=50000,
    orcamento_max=90000,
    city="São Paulo",
    state="SP",
    uso_principal="familia",
    tamanho_familia=4,
    prioridades={
        "economia": 4,
        "espaco": 5,
        "seguranca": 5,
        "conforto": 4,
        "performance": 2
    },
    tipos_preferidos=["SUV", "Sedan"]
)

# Gerar recomendações de TODAS as concessionárias
recommendations = engine.recommend(profile, limit=10)

# Exibir resultados
for rec in recommendations:
    car = rec['car']
    print(f"\n{rec['match_percentage']}% Match - {car.nome}")
    print(f"  Preco: R$ {car.preco:,.2f}")
    print(f"  Concessionaria: {car.dealership_name} ({car.dealership_city})")
    print(f"  Justificativa: {rec['justificativa']}")
    print(f"  WhatsApp: {car.dealership_whatsapp}")
```

### **2. Resultado Esperado**

```
87% Match - FIAT CRONOS DRIVE 1.3
  Preco: R$ 84,990.00
  Concessionaria: RobustCar São Paulo (São Paulo)
  Justificativa: Categoria Sedan ideal para familia. Excelente economia...
  WhatsApp: 5511987654321

84% Match - TOYOTA COROLLA 2.0 XEI
  Preco: R$ 95,000.00
  Concessionaria: AutoCenter Rio de Janeiro (Rio de Janeiro)
  Justificativa: Amplo espaço para família. Boa opção dentro do orçamento.
  WhatsApp: 5521987654321

79% Match - JEEP COMPASS SPORT
  Preco: R$ 110,000.00
  Concessionaria: CarPlus Belo Horizonte (Belo Horizonte)
  Justificativa: Categoria SUV de sua preferência. Amplo espaço...
  WhatsApp: 5531987654321
```

---

## 🔧 **Features Implementadas**

### ✅ **Multi-Concessionária**
- Dados de múltiplas concessionárias em um só lugar
- Cada carro referencia sua concessionária de origem
- Filtros por cidade/estado
- Priorização geográfica (carros próximos primeiro)

### ✅ **Recommendation Engine Inteligente**
- Algoritmo de scoring ponderado (categoria 30%, prioridades 40%, preferências 20%, orçamento 10%)
- Guardrails (nunca recomenda fora do orçamento)
- Fallback inteligente quando filtros muito restritivos
- Justificativas explicáveis para cada recomendação

### ✅ **Flexibilidade**
- Fácil adicionar novas concessionárias
- Suporte a dados reais e mock
- Sistema de scores personalizáveis
- Prioridades configuráveis por usuário

---

## 📦 **Como Adicionar Nova Concessionária**

### **Passo 1: Adicionar em `dealerships.json`**

```json
{
  "id": "nova_concessionaria",
  "name": "Nova Concessionária",
  "city": "Curitiba",
  "state": "PR",
  "region": "Sul",
  "phone": "(41) 3456-7890",
  "whatsapp": "5541987654321",
  "active": true,
  "verified": true
}
```

### **Passo 2: Criar arquivo de estoque**

Criar `backend/data/nova_concessionaria_estoque.json` com a estrutura:

```json
[
  {
    "id": "nova_001",
    "dealership_id": "nova_concessionaria",
    "nome": "VOLKSWAGEN GOL 1.0",
    "marca": "Volkswagen",
    "modelo": "Gol",
    "ano": 2022,
    "preco": 55000,
    "quilometragem": 25000,
    "combustivel": "Flex",
    "categoria": "Hatch",
    "score_familia": 0.5,
    "score_economia": 0.9,
    "score_performance": 0.4,
    "score_conforto": 0.5,
    "score_seguranca": 0.6,
    "imagens": ["url_imagem"],
    "disponivel": true,
    "dealership_name": "Nova Concessionária",
    "dealership_city": "Curitiba",
    "dealership_state": "PR",
    "dealership_phone": "(41) 3456-7890",
    "dealership_whatsapp": "5541987654321"
  }
]
```

### **Passo 3: Reiniciar Engine**

```python
engine = UnifiedRecommendationEngine(data_dir="backend/data")
# Automaticamente carrega a nova concessionária
```

**Pronto!** Os carros da nova concessionária já aparecem nas recomendações.

---

## 📊 **Estatísticas da Plataforma**

```python
# Obter estatísticas gerais
stats = engine.get_stats()

print(f"Concessionárias ativas: {stats['active_dealerships']}")
print(f"Total de carros: {stats['total_cars']}")
print(f"Carros disponíveis: {stats['available_cars']}")
print(f"Por estado: {stats['dealerships_by_state']}")
print(f"Por categoria: {stats['cars_by_category']}")
```

**Output**:
```
Concessionárias ativas: 3
Total de carros: 129
Carros disponíveis: 129
Por estado: {'SP': 1, 'RJ': 1, 'MG': 1}
Por categoria: {'Hatch': 42, 'Sedan': 45, 'SUV': 32, 'Pickup': 10}
```

---

## 🎯 **Próximos Passos**

### ⏳ **Em Desenvolvimento**
- [ ] Frontend React unificado
- [ ] API REST FastAPI
- [ ] Sistema de filtros avançados
- [ ] Dashboard administrativo

### 📅 **Planejado**
- [ ] Autenticação e autorização
- [ ] Painel de concessionárias (self-service)
- [ ] Analytics e métricas
- [ ] Integração com WhatsApp Business
- [ ] Sistema de agendamento de test drive

---

## 🔍 **Diferenças vs. Sistema Anterior**

### **❌ Antes (Dois Sistemas Separados)**
```
RobustCar/                    CarRecommendationSite/
├── frontend/                 ├── frontend/
├── api.py                    ├── backend/
└── robustcar_estoque.json    └── (testes)
```
- Usuário vê apenas carros da RobustCar
- Dados isolados
- Não escalável

### **✅ Agora (Plataforma Unificada)**
```
platform/
├── frontend/ (único)
├── backend/
│   └── data/
│       ├── robustcar_estoque.json
│       ├── autocenter_estoque.json
│       └── carplus_estoque.json
```
- Usuário vê carros de **TODAS** as concessionárias
- RobustCar é apenas uma das opções
- Escalável para centenas de concessionárias
- Cada resultado mostra qual concessionária tem o carro

---

## 💡 **Conceito da Plataforma**

> **"Um único site onde usuários encontram o carro ideal comparando opções de múltiplas concessionárias ao mesmo tempo"**

### **Benefícios**

#### **👤 Para Usuários**
- ✅ Mais opções em um só lugar
- ✅ Comparação fácil entre concessionárias
- ✅ Melhor chance de encontrar o carro ideal
- ✅ Filtros por localização

#### **🏪 Para Concessionárias**
- ✅ Maior visibilidade
- ✅ Leads qualificados
- ✅ Custos compartilhados
- ✅ Analytics de comportamento

#### **💼 Para o Negócio**
- ✅ Modelo SaaS escalável
- ✅ Network effect
- ✅ Receita recorrente
- ✅ Diferencial competitivo

---

## 📞 **Suporte e Contato**

Para adicionar sua concessionária à plataforma ou reportar problemas:
- 📧 Email: contato@faciliauto.com.br
- 💬 WhatsApp: (11) 98765-4321

---

**🎉 Plataforma Unificada FacilIAuto - O futuro das vendas automotivas no Brasil!**

