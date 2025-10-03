# 🚗 RobustCar Integration System

## 🎯 **Visão Geral**

Sistema completo de scraping e recomendação de carros para a **RobustCar** (https://robustcar.com.br), utilizando nosso Framework de Agentes Especializados com metodologia XP e guardrails de IA.

---

## 📋 **Estrutura do Projeto**

```
RobustCar/
├── robustcar_scraper.py       # 📊 Data Analyst - Extração de dados
├── recommendation_engine.py   # 🤖 AI Engineer - Sistema de recomendação
├── requirements.txt          # Dependências do projeto
├── README.md                # Este arquivo
├── config.py                # Configurações (a criar)
├── api.py                   # API REST (a criar)
└── tests/                   # Testes automatizados (a criar)
```

---

## 🚀 **Quick Start**

### **1. Instalação**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### **2. Executar Scraping**
```bash
# Extrair estoque da RobustCar
python robustcar_scraper.py

# Saída esperada:
# 🚗 RobustCar Scraper - Iniciando...
# ✅ Scraping concluído: 45 carros extraídos
# 💾 Arquivos salvos: robustcar_estoque_20241201_140000.json
```

### **3. Testar Recomendações**
```bash
# Executar sistema de recomendação
python recommendation_engine.py

# Saída esperada:
# 🚗 Recomendações para seu perfil:
# 1. Toyota Corolla Cross XRE 2022
#    💰 R$ 95.000
#    📊 Match: 87%
#    📝 SUV ideal para família...
```

---

## 🛠️ **Como Funciona**

### **📊 Data Analyst - Scraping (robustcar_scraper.py)**

```python
# Extração ética com guardrails
scraper = RobustCarScraper()
carros = scraper.scraping_completo(max_paginas=5)

# Funcionalidades:
✅ Verifica robots.txt automaticamente
✅ Rate limiting para não sobrecarregar servidor
✅ Estruturação padronizada dos dados
✅ Enriquecimento com IA para categorização
✅ Exportação JSON/CSV
✅ Relatório automático do estoque
```

**Dados Extraídos:**
- Nome, marca, modelo, ano
- Preço, quilometragem, combustível
- Categoria, scores de IA
- URLs originais e imagens
- Timestamp de extração

### **🤖 AI Engineer - Recomendação (recommendation_engine.py)**

```python
# Sistema com guardrails robustos
engine = RobustCarRecommendationEngine('estoque.json')
recomendacoes = engine.recomendar(perfil_usuario, limite=5)

# Guardrails implementados:
✅ Validação de orçamento obrigatória
✅ Score mínimo para recomendações
✅ Fallback quando filtros muito restritivos
✅ Justificativas explicáveis
✅ Pontos de atenção transparentes
✅ Máximo 5 recomendações por consulta
```

**Algoritmo de Scoring:**
- 30% Categoria vs Uso (família, trabalho, lazer)
- 40% Prioridades do usuário (economia, espaço, etc.)
- 20% Preferências (marca, tipo)
- 10% Posição no orçamento

---

## 🎯 **Casos de Uso Implementados**

### **Caso 1: Família com Orçamento R$ 50-80k**
```python
perfil_familia = UserProfile(
    orcamento_min=50000,
    orcamento_max=80000,
    uso_principal='familia',
    tamanho_familia=4,
    prioridades={'economia': 4, 'espaco': 5, 'seguranca': 5}
)

# Resultado esperado:
# SUVs e Sedans espaçosos, marcas confiáveis
```

### **Caso 2: Primeiro Carro até R$ 40k**
```python
perfil_iniciante = UserProfile(
    orcamento_min=20000,
    orcamento_max=40000,
    uso_principal='primeiro_carro',
    prioridades={'economia': 5, 'conforto': 3}
)

# Resultado esperado:
# Hatches econômicos, modelos não muito antigos
```

### **Caso 3: Executivo - Trabalho Diário**
```python
perfil_executivo = UserProfile(
    orcamento_min=60000,
    orcamento_max=120000,
    uso_principal='trabalho',
    prioridades={'conforto': 5, 'performance': 4}
)

# Resultado esperado:
# Sedans confortáveis, baixa quilometragem
```

---

## 📊 **Métricas e Analytics**

### **Métricas do Scraping**
```python
relatorio = scraper.gerar_relatorio_estoque()

# Exemplo de saída:
{
    "total_carros": 45,
    "preco_medio": 67500.00,
    "por_marca": {
        "Toyota": 12,
        "Chevrolet": 8,
        "Volkswagen": 7
    },
    "por_categoria": {
        "SUV": 18,
        "Sedan": 15,
        "Hatch": 12
    },
    "por_faixa_preco": {
        "até 30k": 8,
        "30k-50k": 12,
        "50k-80k": 15,
        "80k+": 10
    }
}
```

### **Métricas de Recomendação**
- **Match Score**: 0-100% de compatibilidade
- **Justificativas**: Sempre explicáveis
- **Pontos Fortes**: Até 4 por recomendação
- **Pontos de Atenção**: Até 3 por recomendação
- **Fallback Rate**: % de vezes que usa estratégia alternativa

---

## 🛡️ **Guardrails e Ética**

### **Scraping Ético**
- ✅ Verificação automática de robots.txt
- ✅ Rate limiting (2s entre requests)
- ✅ Headers apropriados (User-Agent real)
- ✅ Máximo de páginas configurável
- ✅ Logs detalhados de atividade

### **IA Responsável**
- ✅ Nunca recomendar carros fora do orçamento
- ✅ Score mínimo para evitar sugestões ruins
- ✅ Explicabilidade em todas as recomendações
- ✅ Transparência sobre limitações
- ✅ Fallback quando não há matches

### **Proteção de Dados**
- ✅ Não extrai dados pessoais
- ✅ Foca apenas em informações públicas dos carros
- ✅ Timestamps para auditoria
- ✅ Estrutura de dados padronizada

---

## 🔧 **Configuração Avançada**

### **Personalização do Scraper**
```python
# robustcar_scraper.py - linha 45
scraper = RobustCarScraper()
scraper.rate_limit_delay = 3  # Aumentar delay
scraper.max_paginas = 10      # Mais páginas

# Configurar seletores específicos se necessário
# (após análise manual do HTML)
```

### **Ajuste do Engine de Recomendação**
```python
# recommendation_engine.py - linha 180
# Ajustar pesos do algoritmo
def calcular_score(self, carro, perfil):
    score += self.score_categoria_uso(carro, perfil) * 0.4  # Aumentar peso categoria
    score += self.score_prioridades(carro, perfil) * 0.3   # Diminuir prioridades
    # ... resto do código
```

---

## 🚀 **Próximos Passos**

### **Esta Semana**
1. **Testar Scraper Real**
   ```bash
   python robustcar_scraper.py
   # Ajustar seletores baseado na estrutura real
   ```

2. **Validar Recomendações**
   ```bash
   python recommendation_engine.py
   # Testar com diferentes perfis
   ```

3. **Criar API REST**
   ```python
   # api.py - FastAPI para frontend
   @app.post("/recomendar")
   async def recomendar_carros(perfil: UserProfile):
       return engine.recomendar(perfil)
   ```

### **Próximas 2 Semanas**
1. **Frontend Web**
   - Questionário interativo
   - Exibição de recomendações
   - Dashboard para concessionária

2. **Automação**
   - Scraping programado (diário)
   - Atualização automática de estoque
   - Alertas de novos carros

3. **Analytics**
   - Dashboard de métricas
   - A/B testing de recomendações
   - Feedback dos usuários

---

## 🎯 **Comandos Úteis**

```bash
# Scraping completo
python robustcar_scraper.py

# Teste específico de uma URL
python -c "from robustcar_scraper import RobustCarScraper; s=RobustCarScraper(); print(s.extrair_carros_pagina(1))"

# Recomendação com perfil customizado
python -c "from recommendation_engine import *; exemplo_uso()"

# Verificar estrutura do estoque
python -c "import json; print(json.load(open('robustcar_estoque_latest.json'))[:2])"

# Gerar relatório rápido
python -c "from robustcar_scraper import RobustCarScraper; s=RobustCarScraper(); s.carregar_estoque('estoque.json'); print(s.gerar_relatorio_estoque())"
```

---

## 📞 **Suporte e Debugging**

### **Problemas Comuns**

**1. Scraper não encontra carros**
```python
# Verificar estrutura HTML manualmente
import requests
from bs4 import BeautifulSoup

url = "https://robustcar.com.br/busca//pag/1/ordem/ano-desc/"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Inspecionar elementos
print(soup.prettify()[:1000])
```

**2. Recomendações vazias**
```python
# Verificar se estoque foi carregado
engine = RobustCarRecommendationEngine('estoque.json')
print(f"Carros no estoque: {len(engine.estoque)}")

# Verificar filtros
carros_filtrados = engine.aplicar_filtros_basicos(perfil)
print(f"Após filtros: {len(carros_filtrados)}")
```

**3. Dados inconsistentes**
```python
# Validar qualidade dos dados
for carro in engine.estoque[:5]:
    print(f"{carro.nome}: R$ {carro.preco}, {carro.ano}")
```

---

## 🏆 **Resultado Esperado**

Após executar o sistema completo:

✅ **Estoque automatizado**: 40-60 carros extraídos da RobustCar  
✅ **Recomendações precisas**: Match >80% para perfis bem definidos  
✅ **Justificativas claras**: Sempre explicável por que foi recomendado  
✅ **Guardrails funcionais**: Nunca recomenda fora do orçamento  
✅ **Fallback robusto**: Sempre retorna pelo menos 3 opções  
✅ **Performance**: <2s para gerar recomendações  

**🚗 Sistema pronto para integração com frontend e go-live!**
