# 📊 Business Requirements - FacilIAuto Backend

**Autor:** Business Analyst  
**Data:** Outubro 2024  
**Versão:** 1.0

---

## 🎯 **Objetivos de Negócio**

### **Primários**
1. **Aumentar Taxa de Conversão**: De lead para contato com concessionária
   - Objetivo: 30% dos usuários clicam em WhatsApp
   - Métrica: Click-through rate (CTR) no botão WhatsApp

2. **Reduzir Tempo de Busca**: Acelerar jornada do cliente
   - Objetivo: < 3 minutos do questionário até resultados
   - Métrica: Time to first recommendation

3. **Satisfação do Cliente**: Recomendações relevantes
   - Objetivo: NPS > 70
   - Métrica: Satisfaction score após interação

### **Secundários**
1. **Engajamento de Concessionárias**: Valor percebido
   - Objetivo: 80% das concessionárias ativas mensalmente
   - Métrica: Monthly Active Dealerships (MAD)

2. **Qualidade de Leads**: Leads qualificados para concessionárias
   - Objetivo: 60% dos leads resultam em atendimento
   - Métrica: Lead quality score

3. **Escalabilidade**: Crescimento sustentável
   - Objetivo: Suportar 100 concessionárias e 10k carros
   - Métrica: System performance e response time

---

## 📋 **Regras de Negócio**

### **1. Recomendação de Veículos**

#### **Orçamento (Hard Limit)**
- ✅ **REGRA**: Nunca recomendar carros acima do orçamento máximo
- ✅ **TOLERÂNCIA**: Permitir até 5% acima se score > 90%
- ❌ **PROIBIDO**: Ultrapassar mais de 5% do orçamento máximo

```python
# Implementação
def is_within_budget(car_price, max_budget, match_score):
    if car_price <= max_budget:
        return True
    if car_price <= max_budget * 1.05 and match_score >= 0.90:
        return True  # Tolerância de 5% para matches excelentes
    return False
```

#### **Localização (Soft Limit)**
- ✅ **REGRA**: Priorizar concessionárias na mesma cidade (peso 40%)
- ✅ **REGRA**: Priorizar concessionárias no mesmo estado (peso 20%)
- ✅ **FALLBACK**: Se < 5 resultados, expandir para todo Brasil

#### **Qualidade dos Dados**
- ✅ **REGRA**: Carros sem imagem têm penalidade de 15% no score
- ✅ **REGRA**: Carros desatualizados (> 30 dias) têm penalidade de 10%
- ✅ **REGRA**: Carros "destaque" têm bonus de 10%

#### **Diversidade**
- ✅ **REGRA**: Máximo 40% de resultados da mesma marca
- ✅ **REGRA**: Máximo 30% de resultados da mesma concessionária
- ✅ **OBJETIVO**: Diversificar opções para o usuário

### **2. Algoritmo de Score**

#### **Pesos por Componente**
```python
WEIGHTS = {
    'category_match': 0.25,      # 25% - Tipo de carro
    'priorities': 0.30,          # 30% - Prioridades do usuário
    'preferences': 0.20,         # 20% - Preferências (marcas, câmbio)
    'budget_position': 0.15,     # 15% - Posição no orçamento
    'location': 0.10,            # 10% - Proximidade
}
```

#### **Score Mínimo**
- ✅ **REGRA**: Só mostrar carros com score >= 40%
- ✅ **OBJETIVO**: Top 20 resultados ou score >= 60% (o que vier primeiro)

### **3. Multi-Tenancy**

#### **Isolamento de Dados**
- ✅ **REGRA**: Cada concessionária vê apenas seus próprios dados
- ✅ **REGRA**: API pública agrega todas as concessionárias ativas
- ✅ **SEGURANÇA**: Validação de permissões em todas as operações

#### **Branding**
- ✅ **REGRA**: Concessionárias premium têm prioridade (+5% score)
- ✅ **REGRA**: Concessionárias verificadas têm badge especial
- ✅ **CUSTOMIZAÇÃO**: Logo e cores por concessionária

---

## 🎯 **Casos de Uso**

### **UC-01: Cliente Busca Carro**
**Ator:** Cliente Final  
**Fluxo Principal:**
1. Cliente preenche questionário (3 min)
2. Sistema valida dados (< 1s)
3. Sistema calcula recomendações (< 3s)
4. Sistema retorna top 20 resultados ordenados por score
5. Cliente visualiza resultados com justificativas
6. Cliente clica em WhatsApp de concessionária

**Regras de Negócio Aplicadas:**
- RN-01: Orçamento hard limit
- RN-02: Diversidade de resultados
- RN-03: Score mínimo 40%

**Métricas de Sucesso:**
- Tempo total < 5 minutos
- Score médio dos resultados > 65%
- CTR WhatsApp > 30%

### **UC-02: Concessionária Gerencia Estoque**
**Ator:** Gerente de Concessionária  
**Fluxo Principal:**
1. Concessionária faz upload de estoque (CSV/JSON)
2. Sistema valida dados (schema validation)
3. Sistema processa e indexa veículos
4. Veículos ficam disponíveis para recomendação
5. Sistema notifica gerente (email)

**Regras de Negócio Aplicadas:**
- RN-10: Isolamento de dados
- RN-11: Validação de schema
- RN-12: Atualização automática de stats

**Métricas de Sucesso:**
- Upload success rate > 95%
- Tempo de processamento < 30s
- Zero perda de dados

### **UC-03: Sistema Recomenda Carro**
**Ator:** Sistema (Background)  
**Fluxo Principal:**
1. Recebe UserProfile
2. Filtra carros por orçamento (hard limit)
3. Calcula score para cada carro elegível
4. Aplica penalties e bonuses
5. Ordena por score
6. Aplica regras de diversidade
7. Retorna top 20 com justificativas

**Regras de Negócio Aplicadas:**
- RN-01 a RN-09: Todas as regras de recomendação

**Métricas de Sucesso:**
- Response time < 3s
- Score médio > 65%
- Diversidade atingida (max 40% mesma marca)

---

## 📊 **KPIs (Key Performance Indicators)**

### **Produto**
| KPI | Objetivo | Crítico |
|-----|----------|---------|
| CTR WhatsApp | > 30% | ✅ |
| NPS | > 70 | ✅ |
| Time to Recommendation | < 5s | ✅ |
| Match Score Médio | > 65% | ⚠️ |
| Diversidade de Resultados | 60-80% | ⚠️ |

### **Técnico**
| KPI | Objetivo | Crítico |
|-----|----------|---------|
| API Response Time | < 500ms (p95) | ✅ |
| Uptime | > 99.5% | ✅ |
| Error Rate | < 0.5% | ✅ |
| Test Coverage | > 80% | ⚠️ |
| Database Query Time | < 100ms (p95) | ⚠️ |

### **Negócio**
| KPI | Objetivo | Crítico |
|-----|----------|---------|
| MAD (Monthly Active Dealerships) | > 80% | ✅ |
| Lead Quality Score | > 60% | ✅ |
| Customer Acquisition Cost (CAC) | < R$ 50 | ⚠️ |
| Customer Lifetime Value (LTV) | > R$ 500 | ⚠️ |
| LTV/CAC Ratio | > 10x | ✅ |

---

## ⚠️ **Riscos de Negócio**

### **Alto Impacto**
1. **Baixa Qualidade de Recomendações**
   - **Risco**: Score baixo, usuários não encontram o que procuram
   - **Impacto**: Abandono, NPS baixo, churn de concessionárias
   - **Mitigação**: A/B testing contínuo, feedback loops, ML optimization

2. **Performance Inadequada**
   - **Risco**: Response time > 5s
   - **Impacto**: Frustração do usuário, abandono
   - **Mitigação**: Caching, indexação, query optimization

3. **Dados Desatualizados**
   - **Risco**: Recomendar carros já vendidos
   - **Impacto**: Frustração, leads perdidos, reputação
   - **Mitigação**: Sync automático diário, webhooks, validação

### **Médio Impacto**
4. **Falta de Diversidade**
   - **Risco**: Só mostrar carros de 1-2 concessionárias
   - **Impacto**: Percepção de favoritismo, menor comparação
   - **Mitigação**: Regras de diversidade, algoritmo balanceado

5. **Custos de Infraestrutura**
   - **Risco**: Crescimento não sustentável de custos
   - **Impacto**: Margens baixas, inviabilidade financeira
   - **Mitigação**: Auto-scaling inteligente, otimização de recursos

---

## ✅ **Critérios de Aceitação**

### **MVP (Mínimo Viável)**
- [x] API REST funcionando
- [x] Algoritmo de recomendação básico
- [x] Multi-tenant (3+ concessionárias)
- [x] Response time < 5s
- [x] Testes com coverage > 80%

### **V1.0 (Produção)**
- [ ] Todas as regras de negócio implementadas
- [ ] Monitoring e alerting 24/7
- [ ] Backup automático
- [ ] CI/CD pipeline
- [ ] Documentação completa
- [ ] SLA 99.5% uptime

### **V1.1 (Otimização)**
- [ ] ML-based recommendations
- [ ] A/B testing framework
- [ ] Dashboards de negócio
- [ ] Webhooks para concessionárias
- [ ] API rate limiting

---

## 📞 **Stakeholders**

### **Internos**
- **Product Manager**: Define roadmap e prioridades
- **Tech Lead**: Garante implementação técnica
- **Data Analyst**: Analisa métricas e otimiza
- **Operations**: Garante uptime e performance

### **Externos**
- **Concessionárias**: Clientes B2B, pagantes
- **Usuários Finais**: Compradores de carros
- **Investidores**: ROI e crescimento

---

## 🎯 **Próximos Passos**

1. **Validar Regras de Negócio** com concessionárias piloto
2. **Implementar KPIs** em dashboard
3. **Setup Monitoring** para métricas críticas
4. **A/B Testing** de algoritmo
5. **Feedback Loops** com usuários

---

**Status:** ✅ Requisitos Documentados  
**Próximo:** Data Analysis e Metrics Implementation

