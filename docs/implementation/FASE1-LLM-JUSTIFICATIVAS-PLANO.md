# 📋 Fase 1: SLM para Justificativas Inteligentes - Plano de Implementação

## 🎯 Objetivo

Substituir a geração de justificativas baseada em templates por justificativas contextuais e precisas geradas por Small Language Model (SLM).

**Resultado esperado:** Cada recomendação de veículo terá uma explicação natural, precisa e contextualizada que explica POR QUÊ aquele carro é adequado para aquele usuário específico.

---

## 📊 Escopo

### ✅ O que vamos implementar

1. **Novo serviço:** `LLMJustificationService` para geração de justificativas
2. **Integração:** Modificar `UnifiedRecommendationEngine` para usar o novo serviço
3. **Fallback:** Manter lógica atual como backup se LLM falhar
4. **Configuração:** Suporte para múltiplos provedores (OpenAI, Anthropic, modelos locais)
5. **Testes:** Cobertura completa do novo serviço
6. **Documentação:** Guia de configuração e uso

### ❌ O que NÃO vamos implementar (ainda)

- Análise de contexto dinâmica (Fase 2)
- Ajuste de pesos por LLM (Fase 2)
- LangGraph para refinamento (Fase 3)
- Aprendizado com feedback (Fase 3)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                  UnifiedRecommendationEngine                │
│                                                             │
│  recommend() → filter → score → rank                       │
│                                     ↓                       │
│                            ┌────────────────┐              │
│                            │ Generate       │              │
│                            │ Justification  │              │
│                            └────────┬───────┘              │
│                                     ↓                       │
│                     ┌───────────────────────────┐          │
│                     │ LLMJustificationService   │          │
│                     │                           │          │
│                     │ • build_prompt()          │          │
│                     │ • call_llm()              │          │
│                     │ • validate_output()       │          │
│                     │ • cache_response()        │          │
│                     └───────────┬───────────────┘          │
│                                 ↓                           │
│                    ┌─────────────────────────┐             │
│                    │  LLM Provider           │             │
│                    │                         │             │
│                    │ • OpenAI (GPT-4o-mini)  │             │
│                    │ • Anthropic (Haiku)     │             │
│                    │ • Local (Llama 3.1 8B)  │             │
│                    └─────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
                                 ↓
                    ┌─────────────────────────┐
                    │  Fallback Strategy      │
                    │                         │
                    │ Se LLM falhar:          │
                    │ → usa justificativa     │
                    │   template atual        │
                    │ → log erro              │
                    │ → continua operação     │
                    └─────────────────────────┘
```

---

## 📁 Arquivos a Criar/Modificar

### Novos Arquivos

#### 1. `platform/backend/services/llm_justification_service.py`
```python
"""
Serviço para geração de justificativas usando LLM
"""
from typing import Dict, Optional, List
from models.car import Car
from models.user_profile import UserProfile
import os
from openai import OpenAI
from anthropic import Anthropic
import logging

class LLMJustificationService:
    """Gera justificativas contextuais para recomendações usando LLM"""

    def __init__(
        self,
        provider: str = "openai",  # "openai", "anthropic", "local"
        model: str = None,
        api_key: str = None,
        cache_enabled: bool = True
    ):
        """
        Inicializa serviço de justificativas LLM

        Args:
            provider: Provedor do LLM
            model: Nome do modelo (default usa modelo otimizado por provedor)
            api_key: Chave API (default usa variável de ambiente)
            cache_enabled: Habilita cache de respostas
        """
        pass

    def generate_justification(
        self,
        car: Car,
        profile: UserProfile,
        score: float,
        position: int,
        total_results: int,
        tco_breakdown: Dict,
        other_cars: Optional[List[Car]] = None
    ) -> str:
        """
        Gera justificativa contextual para uma recomendação

        Args:
            car: Carro recomendado
            profile: Perfil do usuário
            score: Score final do matching
            position: Posição no ranking (1-based)
            total_results: Total de resultados
            tco_breakdown: Detalhamento do TCO
            other_cars: Outros carros no ranking (para comparação)

        Returns:
            Justificativa em português (2-3 frases)
        """
        pass

    def _build_prompt(
        self,
        car: Car,
        profile: UserProfile,
        score: float,
        position: int,
        total_results: int,
        tco_breakdown: Dict
    ) -> str:
        """Constrói prompt otimizado para o LLM"""
        pass

    def _call_llm(self, prompt: str) -> str:
        """Chama o LLM com retry e error handling"""
        pass

    def _validate_output(self, text: str) -> bool:
        """Valida se a saída do LLM é adequada"""
        pass

    def _get_cache_key(self, car: Car, profile: UserProfile) -> str:
        """Gera chave de cache"""
        pass
```

**Tamanho estimado:** ~300-400 linhas

---

#### 2. `platform/backend/services/llm_prompts.py`
```python
"""
Templates de prompts para LLM
"""

SYSTEM_PROMPT = """
Você é um assistente especialista em recomendação de veículos.
Sua função é explicar de forma clara, honesta e contextual por que
um veículo específico é adequado para um usuário.

REGRAS:
- Use 2-3 frases curtas e diretas
- Seja específico com números (preço, consumo, TCO)
- Compare com orçamento do usuário quando relevante
- Mencione apenas pontos realmente importantes
- Seja honesto sobre limitações (ex: "consumo moderado" não "excelente")
- Use português brasileiro coloquial mas profissional
- NÃO use emojis ou formatação markdown
- NÃO invente dados que não foram fornecidos
- NÃO seja genérico ("ótimo veículo"), seja específico
"""

USER_PROMPT_TEMPLATE = """
Explique por que este carro é recomendado para este usuário:

CARRO:
- Modelo: {car_nome}
- Preço: R$ {car_preco:,}
- Categoria: {car_categoria}
- Ano: {car_ano}
- Consumo: {car_consumo_cidade} km/L (cidade), {car_consumo_estrada} km/L (estrada)
- Itens de Segurança: {car_seguranca}
- Itens de Conforto: {car_conforto}
- Concessionária: {dealership_nome} em {dealership_cidade}

USUÁRIO:
- Uso principal: {uso_principal}
- Tamanho da família: {tamanho_familia} pessoas
- Tem crianças: {tem_criancas}
- Orçamento: R$ {orcamento_min:,} - R$ {orcamento_max:,}
- Prioridades: {prioridades_str}
- Renda mensal: R$ {renda_mensal:,}

ANÁLISE:
- Score de matching: {score_percent}%
- Ranking: #{position} de {total_results} recomendações
- TCO mensal estimado: R$ {tco_mensal:,} ({tco_percent}% da renda)
- Principais forças: {top_features}

Gere uma explicação contextual (2-3 frases).
"""

# Prompts específicos por uso
COMMERCIAL_FOCUS_PROMPT = """
ATENÇÃO: Este é uso COMERCIAL. Foque em:
- Capacidade de carga / passageiros
- Custo operacional (TCO baixo é crítico)
- Robustez e confiabilidade
- Adequação para a operação descrita
"""

FAMILY_FOCUS_PROMPT = """
ATENÇÃO: Este é uso FAMILIAR. Foque em:
- Espaço interno e porta-malas
- Segurança (airbags, ISOFIX, estrutura)
- Conforto para viagens
- Economia (se prioridade alta)
"""

FIRST_CAR_FOCUS_PROMPT = """
ATENÇÃO: Este é o PRIMEIRO CARRO. Foque em:
- Facilidade de dirigir e estacionar
- Custo de manutenção acessível
- Boa revenda futura
- Seguros mais baratos
"""
```

**Tamanho estimado:** ~200 linhas

---

#### 3. `platform/backend/tests/test_llm_justification_service.py`
```python
"""
Testes para LLMJustificationService
"""
import pytest
from services.llm_justification_service import LLMJustificationService
from models.car import Car
from models.user_profile import UserProfile

class TestLLMJustificationService:
    """Testes do serviço de justificativas LLM"""

    def test_generate_justification_basic(self):
        """Testa geração básica de justificativa"""
        pass

    def test_generate_justification_family_context(self):
        """Testa justificativa para contexto familiar"""
        pass

    def test_generate_justification_commercial_context(self):
        """Testa justificativa para contexto comercial"""
        pass

    def test_fallback_on_llm_failure(self):
        """Testa fallback quando LLM falha"""
        pass

    def test_cache_functionality(self):
        """Testa se cache está funcionando"""
        pass

    def test_prompt_building(self):
        """Testa construção de prompts"""
        pass

    def test_output_validation(self):
        """Testa validação de saída do LLM"""
        pass

    def test_different_providers(self):
        """Testa diferentes provedores (OpenAI, Anthropic)"""
        pass
```

**Tamanho estimado:** ~300-400 linhas

---

### Arquivos a Modificar

#### 1. `platform/backend/services/unified_recommendation_engine.py`

**Modificações:**

```python
# Linha ~60: Adicionar import
from services.llm_justification_service import LLMJustificationService

# Linha ~110: Adicionar no __init__
def __init__(self, data_dir: str = None, use_llm: bool = True):
    # ... código existente ...

    # Inicializar LLM service
    self.use_llm = use_llm
    if use_llm:
        try:
            self.llm_service = LLMJustificationService()
            print("[ENGINE] LLM justification service habilitado")
        except Exception as e:
            print(f"[ENGINE] Erro ao inicializar LLM service: {e}")
            print("[ENGINE] Usando justificativas template como fallback")
            self.llm_service = None
    else:
        self.llm_service = None

# Linha ~1340: Modificar generate_justification
def _generate_justification(
    self,
    car: Car,
    profile: UserProfile,
    final_score: float,
    car_scores: dict,
    category_score: float,
    tco_info: dict,
    position: int = 1,
    total_results: int = 5
) -> str:
    """Gera justificativa para a recomendação"""

    # Tentar usar LLM primeiro
    if self.llm_service:
        try:
            return self.llm_service.generate_justification(
                car=car,
                profile=profile,
                score=final_score,
                position=position,
                total_results=total_results,
                tco_breakdown=tco_info.get("breakdown", {})
            )
        except Exception as e:
            print(f"[ENGINE] Erro ao gerar justificativa LLM: {e}")
            print("[ENGINE] Usando fallback template")

    # Fallback: lógica template existente
    return self._generate_justification_template(
        car, profile, final_score, car_scores, category_score, tco_info
    )

# Nova função: extrair lógica template atual
def _generate_justification_template(
    self,
    car: Car,
    profile: UserProfile,
    final_score: float,
    car_scores: dict,
    category_score: float,
    tco_info: dict
) -> str:
    """
    Geração de justificativa usando templates (fallback)
    [Mover código existente da linha 1340-1400 para cá]
    """
    # ... código existente de geração de justificativas ...
    pass
```

**Linhas afetadas:** ~1340-1400 (refatoração + nova função)

---

#### 2. `platform/backend/requirements.txt`

**Adicionar:**
```txt
# LLM Providers
openai>=1.12.0
anthropic>=0.18.0

# Caching (opcional, para otimização)
redis>=5.0.0
```

---

#### 3. `platform/backend/.env.example`

**Adicionar:**
```bash
# LLM Configuration (Fase 1)
LLM_PROVIDER=openai  # openai, anthropic, local
LLM_MODEL=gpt-4o-mini  # ou claude-3-haiku-20240307
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
LLM_CACHE_ENABLED=true
LLM_TIMEOUT_SECONDS=10
```

---

#### 4. `platform/backend/api/main.py`

**Modificações mínimas:**

```python
# Linha ~76: Adicionar configuração
use_llm = os.getenv("LLM_ENABLED", "true").lower() == "true"

try:
    print("[STARTUP] Carregando UnifiedRecommendationEngine...")
    engine = UnifiedRecommendationEngine(
        data_dir=data_dir,
        use_llm=use_llm  # ← Novo parâmetro
    )
    print(f"[STARTUP] Engine carregado com {len(engine.all_cars)} carros")
    # ...
```

---

## 🎨 Prompt Engineering

### Prompt System (instrução base)

```
Você é um assistente especialista em recomendação de veículos.
Sua função é explicar de forma clara, honesta e contextual por que
um veículo específico é adequado para um usuário.

REGRAS:
- Use 2-3 frases curtas e diretas
- Seja específico com números (preço, consumo, TCO)
- Compare com orçamento do usuário quando relevante
- Mencione apenas pontos realmente importantes
- Seja honesto sobre limitações
- Use português brasileiro coloquial mas profissional
- NÃO use emojis ou formatação markdown
- NÃO invente dados
- NÃO seja genérico
```

### Exemplo de Input/Output

**Input:**
```
Carro: Volkswagen Taos 1.4 TSI 2023 - R$ 85.000
Categoria: SUV Compacto
Consumo: 11 km/L cidade, 13.5 km/L estrada
Segurança: 6 airbags, ABS, Controle de estabilidade, ISOFIX
Conforto: Ar-condicionado, Direção elétrica, Vidros elétricos

Usuário:
- Uso: família (4 pessoas, 2 crianças)
- Orçamento: R$ 60.000 - R$ 100.000
- Prioridades: economia=5, segurança=5, espaço=4
- Renda: R$ 8.000/mês

Análise:
- Score: 88%
- Ranking: #1 de 5
- TCO mensal: R$ 1.900 (24% da renda)
- Principais forças: Segurança, Espaço, Preço adequado
```

**Output esperado:**
```
O Volkswagen Taos é a melhor opção para sua família de 4 pessoas,
oferecendo amplo espaço interno e 6 airbags com ISOFIX para as crianças.
Com TCO de R$ 1.900/mês (24% da sua renda) e consumo moderado de 11 km/L,
fica confortavelmente dentro do seu orçamento de até R$ 100 mil.
```

### Exemplos por Contexto

**Família com crianças:**
```
"O Honda HR-V combina espaço (porta-malas de 437L) e segurança
(6 airbags + ISOFIX) ideal para sua família. O consumo de 12.5 km/L
e TCO de R$ 1.650/mês (21% da renda) permitem viagens sem peso no bolso."
```

**Comercial/Entrega:**
```
"O Fiat Fiorino atende perfeitamente operações de entrega urbana,
com capacidade de 650kg e custo operacional baixíssimo (TCO R$ 1.200/mês).
Consumo de 14 km/L garante economia nas rotas diárias."
```

**Primeiro carro:**
```
"O Renault Kwid é o primeiro carro ideal: compacto (fácil de estacionar),
econômico (15 km/L) e com seguro acessível. A R$ 45 mil, sobra folga
no orçamento para eventuais manutenções enquanto você ganha experiência."
```

**Transporte app (Uber/99):**
```
"O Toyota Corolla 2020 está homologado para apps como Uber/99 e oferece
ótima durabilidade (crucial para alto km/mês). TCO de R$ 2.100/mês se paga
com 150-180h de trabalho mensal, deixando boa margem de lucro."
```

---

## 🧪 Estratégia de Testes

### Testes Unitários

```python
# test_llm_justification_service.py

def test_family_context():
    """Valida justificativa para contexto familiar"""
    car = create_test_car_suv()
    profile = create_family_profile(kids=2)

    justification = service.generate_justification(
        car, profile, score=0.88, position=1, total_results=5, tco_breakdown={}
    )

    # Validações
    assert len(justification) > 50  # Não muito curto
    assert len(justification) < 500  # Não muito longo
    assert "famíli" in justification.lower()  # Menciona família
    assert "R$" in justification  # Menciona valores
    assert not "emoji" in justification  # Sem emojis
```

### Testes de Integração

```python
# test_api_integration.py

def test_recommendations_with_llm_justifications():
    """Testa recomendações com justificativas LLM end-to-end"""

    # Criar perfil de teste
    profile = {
        "orcamento_min": 60000,
        "orcamento_max": 100000,
        "uso_principal": "familia",
        "tamanho_familia": 4,
        "tem_criancas": True,
        "prioridades": {"economia": 5, "seguranca": 5, "espaco": 4}
    }

    # Chamar API
    response = client.post("/api/recommendations", json=profile)

    # Validar
    assert response.status_code == 200
    results = response.json()

    for car in results["recommendations"]:
        justification = car["justificacao"]

        # Validar qualidade da justificativa
        assert justification is not None
        assert len(justification) > 100
        assert "R$" in justification  # Menciona preço ou TCO
        # Validar que não é template genérico
        assert not justification.startswith("Excelente opção")
```

### Testes de Fallback

```python
def test_fallback_on_api_failure():
    """Garante que sistema funciona mesmo se LLM falhar"""

    # Simular falha do LLM (API key inválida)
    service = LLMJustificationService(api_key="invalid")

    # Deve retornar justificativa template
    justification = engine._generate_justification(
        car, profile, score, car_scores, category_score, tco_info
    )

    assert justification is not None
    assert len(justification) > 0
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

**Obrigatórias:**
```bash
LLM_PROVIDER=openai  # ou anthropic
OPENAI_API_KEY=sk-...  # se provider=openai
```

**Opcionais:**
```bash
LLM_MODEL=gpt-4o-mini  # default
LLM_CACHE_ENABLED=true
LLM_TIMEOUT_SECONDS=10
LLM_MAX_TOKENS=200
LLM_TEMPERATURE=0.7
```

### Modelos Recomendados

| Provedor | Modelo | Custo/1k tokens | Latência | Qualidade |
|----------|--------|-----------------|----------|-----------|
| **OpenAI** | gpt-4o-mini | $0.00015 input<br>$0.0006 output | ~300ms | ⭐⭐⭐⭐⭐ |
| **Anthropic** | claude-3-haiku | $0.00025 input<br>$0.00125 output | ~400ms | ⭐⭐⭐⭐⭐ |
| **Local** | Llama 3.1 8B | Grátis | ~800ms | ⭐⭐⭐⭐ |

**Recomendação:** Começar com **gpt-4o-mini** (melhor custo-benefício)

---

## 💰 Estimativa de Custos

### Cálculo por Requisição

**Tokens por justificativa:**
- Input prompt: ~600 tokens
- Output gerado: ~150 tokens
- Total: ~750 tokens

**Custos por recomendação (5 carros):**

| Provedor | Custo/req | Custo/100 req | Custo/10k req |
|----------|-----------|---------------|---------------|
| OpenAI (gpt-4o-mini) | $0.00054 | $0.054 | $5.40 |
| Anthropic (Haiku) | $0.00034 | $0.034 | $3.40 |
| Local (Llama) | $0.00 | $0.00 | $0.00 |

### Projeções de Uso

**Cenário 1: MVP/Beta (100 usuários/mês)**
- Requisições: 100/mês
- Custo mensal: **$0.05 - $0.10**

**Cenário 2: Lançamento (1.000 usuários/mês)**
- Requisições: 1.000/mês
- Custo mensal: **$0.50 - $1.00**

**Cenário 3: Crescimento (10.000 usuários/mês)**
- Requisições: 10.000/mês
- Custo mensal: **$5 - $10**

**Cenário 4: Escala (100.000 usuários/mês)**
- Requisições: 100.000/mês
- Custo mensal: **$50 - $100**

### Otimizações de Custo

1. **Cache agressivo:** Carros + perfil similar → reutiliza justificativa (↓ 60-70%)
2. **Batch processing:** Gerar 5 justificativas em 1 chamada (↓ 40%)
3. **Modelo local para alta escala:** Llama 3.1 8B self-hosted (custo fixo)

---

## 🔄 Estratégia de Fallback

### Níveis de Fallback

```
1. LLM primário (OpenAI/Anthropic) → se falhar
   ↓
2. Retry com exponential backoff (3 tentativas) → se falhar
   ↓
3. Justificativa template (código atual) → sempre funciona
```

### Condições de Fallback

- **Timeout:** > 10 segundos
- **Rate limit:** 429 da API
- **API key inválida:** 401
- **Erro de rede:** Connection error
- **Output inválido:** Resposta vazia ou muito curta (<50 chars)

### Logging

```python
if llm_failed:
    logger.warning(
        f"LLM fallback acionado para car_id={car.id}",
        extra={
            "error": str(e),
            "provider": self.provider,
            "model": self.model,
            "car_id": car.id,
            "profile_id": profile.id
        }
    )
```

---

## 📊 Métricas e Monitoramento

### KPIs a Rastrear

1. **Taxa de sucesso LLM:** % chamadas que não usaram fallback
2. **Latência média:** Tempo para gerar justificativa
3. **Custo por requisição:** Tracking de gastos
4. **Qualidade percebida:** Feedback dos usuários (Fase 2)

### Implementação

```python
# services/llm_justification_service.py

class LLMJustificationService:
    def __init__(self):
        self.metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "fallback_calls": 0,
            "total_latency": 0.0,
            "total_cost": 0.0
        }

    def get_metrics(self) -> dict:
        """Retorna métricas agregadas"""
        return {
            "success_rate": self.metrics["successful_calls"] / self.metrics["total_calls"],
            "avg_latency": self.metrics["total_latency"] / self.metrics["total_calls"],
            "total_cost": self.metrics["total_cost"]
        }
```

---

## 📅 Cronograma de Implementação

### Sprint 1 (2-3 dias)

**Dia 1:**
- [ ] Criar `llm_justification_service.py` (estrutura básica)
- [ ] Criar `llm_prompts.py` (todos os templates)
- [ ] Implementar integração com OpenAI
- [ ] Testes básicos manuais

**Dia 2:**
- [ ] Implementar cache (opcional mas recomendado)
- [ ] Implementar retry logic e error handling
- [ ] Integrar com `unified_recommendation_engine.py`
- [ ] Testes de integração

**Dia 3:**
- [ ] Implementar fallback strategy
- [ ] Criar testes unitários completos (`test_llm_justification_service.py`)
- [ ] Documentação (README + variáveis de ambiente)
- [ ] Deploy em ambiente de staging

### Sprint 2 (Opcional - 1-2 dias)

**Melhorias:**
- [ ] Suporte para Anthropic (Claude)
- [ ] Suporte para modelo local (Llama)
- [ ] Dashboard de métricas
- [ ] A/B test: LLM vs Template

---

## ✅ Critérios de Aceitação

### Funcionalidade

- [x] Justificativas geradas por LLM são contextuais e precisas
- [x] Fallback funciona perfeitamente se LLM falhar
- [x] Latência adicional < 1 segundo por requisição
- [x] Custo por requisição < $0.01
- [x] Suporta pelo menos 1 provedor (OpenAI ou Anthropic)

### Qualidade

- [x] Cobertura de testes ≥ 80%
- [x] Justificativas têm 100-300 caracteres (2-3 frases)
- [x] Linguagem natural, sem templates óbvios
- [x] Menciona detalhes específicos do carro e usuário
- [x] Sem informações inventadas ou incorretas

### Operacional

- [x] Sistema funciona sem LLM (fallback testado)
- [x] Logs adequados para debugging
- [x] Variáveis de ambiente documentadas
- [x] README com instruções de configuração

---

## 🚀 Como Executar Após Implementação

### 1. Configurar API Key

```bash
# .env
OPENAI_API_KEY=sk-proj-...
LLM_PROVIDER=openai
LLM_ENABLED=true
```

### 2. Instalar Dependências

```bash
cd platform/backend
pip install -r requirements.txt
```

### 3. Testar

```bash
# Rodar testes
pytest tests/test_llm_justification_service.py -v

# Teste manual via API
curl -X POST http://localhost:8000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "orcamento_min": 60000,
    "orcamento_max": 100000,
    "uso_principal": "familia",
    "tamanho_familia": 4,
    "tem_criancas": true,
    "prioridades": {"economia": 5, "seguranca": 5}
  }'
```

### 4. Validar Justificativas

Verificar que cada carro retornado tem:
- Campo `justificacao` preenchido
- Texto natural (não template óbvio)
- Menção a características específicas
- Contextualização com perfil do usuário

---

## 🔍 Validação de Qualidade

### Checklist de Revisão de Justificativas

Para cada justificativa gerada, verificar:

- [ ] **Especificidade:** Menciona nome do carro, preço ou características únicas?
- [ ] **Contextualização:** Relaciona com uso principal do usuário?
- [ ] **Honestidade:** Evita superlativos não justificados ("excelente", "perfeito")?
- [ ] **Números:** Inclui valores concretos (TCO, consumo, preço)?
- [ ] **Tamanho:** Entre 100-300 caracteres (2-3 frases)?
- [ ] **Português correto:** Sem erros gramaticais?
- [ ] **Sem invenções:** Todos os dados mencionados estão no input?

---

## 📖 Documentação a Criar

1. **README_LLM.md** (guia de uso)
2. **PROMPT_ENGINEERING.md** (detalhes de prompts)
3. **COST_ANALYSIS.md** (análise de custos)
4. **Atualizar CLAUDE.md** com nova funcionalidade

---

## 🎯 Próximos Passos (Fases Futuras)

Após Fase 1 estar funcionando:

- **Fase 2:** Análise de contexto dinâmica com LLM
- **Fase 3:** LangGraph para refinamento iterativo
- **Fase 4:** Aprendizado com feedback dos usuários

---

## 📞 Suporte

Em caso de dúvidas ou problemas durante implementação:
1. Revisar este plano
2. Consultar documentação dos provedores (OpenAI, Anthropic)
3. Verificar logs do backend
4. Testar com fallback desabilitado para isolar problemas

---

**Status:** 📋 Plano aprovado e pronto para implementação
**Estimativa:** 2-3 dias de desenvolvimento + 1 dia de testes
**Custo estimado:** < $10/mês para MVP (100 usuários)
