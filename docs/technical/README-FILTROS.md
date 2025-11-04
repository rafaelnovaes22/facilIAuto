# 🎯 Documentação de Filtros - Índice

## Princípio Fundamental

**Todo filtro opcional, quando selecionado pelo usuário, torna-se obrigatório nos resultados.**

---

## Documentos Disponíveis

### 1. 📋 [FILTROS-RESUMO.md](./FILTROS-RESUMO.md)
**Referência rápida** com tabela de filtros, regras e checklist.

**Use quando:**
- Precisa de uma visão geral rápida
- Está implementando um novo filtro
- Quer verificar a ordem de aplicação

**Conteúdo:**
- Tabela de filtros disponíveis
- Regras de implementação (✅ correto vs ❌ errado)
- Ordem de aplicação
- Checklist para novos filtros

---

### 2. 📖 [PRINCIPIO-FILTROS-OBRIGATORIOS.md](./PRINCIPIO-FILTROS-OBRIGATORIOS.md)
**Documentação completa** com explicações detalhadas, exemplos e casos de uso.

**Use quando:**
- Está aprendendo sobre o sistema de filtros
- Precisa entender o "porquê" das decisões
- Quer ver exemplos práticos completos
- Está debugando um problema de filtros

**Conteúdo:**
- Explicação do princípio
- Por que isso é importante
- Implementação de cada filtro
- Fluxo completo do engine
- Mensagens do frontend
- Exemplos práticos detalhados
- Benefícios do princípio

---

### 3. 🔄 [FILTROS-FLUXOGRAMA.md](./FILTROS-FLUXOGRAMA.md)
**Visualização do fluxo** com diagramas e exemplos visuais.

**Use quando:**
- Quer entender o fluxo visualmente
- Está apresentando para o time
- Precisa debugar onde carros estão sendo eliminados
- Quer ver exemplos de busca restritiva vs bem-sucedida

**Conteúdo:**
- Fluxograma completo do recommend()
- Exemplo de busca restritiva (lista vazia)
- Exemplo de busca bem-sucedida
- Tipos de filtros (eliminatórios, priorizadores, scoring)
- Regra de ouro

---

## Guia de Uso Rápido

### Para Desenvolvedores

**Implementando um novo filtro?**
1. Leia: [FILTROS-RESUMO.md](./FILTROS-RESUMO.md) → Checklist
2. Veja exemplos: [PRINCIPIO-FILTROS-OBRIGATORIOS.md](./PRINCIPIO-FILTROS-OBRIGATORIOS.md) → Seção "Filtros Implementados"
3. Teste: Garanta que retorna lista vazia quando nenhum carro atende

**Debugando um problema?**
1. Veja o fluxo: [FILTROS-FLUXOGRAMA.md](./FILTROS-FLUXOGRAMA.md)
2. Verifique logs: `[FILTRO] Após X: Y carros`
3. Identifique onde carros foram eliminados

**Entendendo o sistema?**
1. Comece: [PRINCIPIO-FILTROS-OBRIGATORIOS.md](./PRINCIPIO-FILTROS-OBRIGATORIOS.md) → "O que isso significa?"
2. Visualize: [FILTROS-FLUXOGRAMA.md](./FILTROS-FLUXOGRAMA.md)
3. Referência: [FILTROS-RESUMO.md](./FILTROS-RESUMO.md)

---

### Para Product Managers / UX

**Entendendo o comportamento?**
1. Leia: [PRINCIPIO-FILTROS-OBRIGATORIOS.md](./PRINCIPIO-FILTROS-OBRIGATORIOS.md) → "Por que isso é importante?"
2. Veja exemplos: [FILTROS-FLUXOGRAMA.md](./FILTROS-FLUXOGRAMA.md) → Exemplos práticos

**Definindo mensagens de erro?**
1. Veja: [PRINCIPIO-FILTROS-OBRIGATORIOS.md](./PRINCIPIO-FILTROS-OBRIGATORIOS.md) → "Frontend: Mensagens Apropriadas"
2. Exemplos de mensagens específicas por contexto

**Apresentando para stakeholders?**
1. Use: [FILTROS-FLUXOGRAMA.md](./FILTROS-FLUXOGRAMA.md) → Diagramas visuais
2. Mostre: Exemplo de busca restritiva vs bem-sucedida

---

## Filtros Disponíveis

| Filtro | Tipo | Documento |
|--------|------|-----------|
| Orçamento | Obrigatório | [PRINCIPIO](./PRINCIPIO-FILTROS-OBRIGATORIOS.md#1-orçamento-sempre-obrigatório) |
| Ano (min/max) | Opcional → Obrigatório | [PRINCIPIO](./PRINCIPIO-FILTROS-OBRIGATORIOS.md#2-faixa-de-anos-opcional--obrigatório) |
| Quilometragem | Opcional → Obrigatório | [PRINCIPIO](./PRINCIPIO-FILTROS-OBRIGATORIOS.md#3-quilometragem-máxima-opcional--obrigatório) |
| Must-haves | Opcional → Obrigatório | [PRINCIPIO](./PRINCIPIO-FILTROS-OBRIGATORIOS.md#4-must-haves--itens-obrigatórios-opcional--obrigatório) |
| Raio geográfico | Opcional → Obrigatório | [PRINCIPIO](./PRINCIPIO-FILTROS-OBRIGATORIOS.md#5-raio-geográfico-opcional--obrigatório) |
| Uber/99 | Opcional → Obrigatório | [PRINCIPIO](./PRINCIPIO-FILTROS-OBRIGATORIOS.md#6-transporte-de-passageiros--uber99-opcional--obrigatório) |

---

## Implementações Relacionadas

### Backend
- `platform/backend/models/user_profile.py` - Modelo com filtros
- `platform/backend/services/unified_recommendation_engine.py` - Engine com filtros

### Frontend
- `platform/frontend/src/types/index.ts` - Tipos TypeScript
- `platform/frontend/src/store/questionnaireStore.ts` - State management
- `platform/frontend/src/components/questionnaire/YearSelector.tsx` - Componente de ano
- `platform/frontend/src/components/questionnaire/Step1Budget.tsx` - Step 1 com filtros

### Documentação de Implementação
- `docs/implementation/FILTRO-FAIXA-ANOS-IMPLEMENTADO.md` - Implementação do filtro de anos

---

## Regra de Ouro

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  Se o usuário selecionou um filtro,                 │
│  TODOS os resultados DEVEM atender a esse filtro.   │
│                                                      │
│  Nunca use fallback que ignore filtros!             │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Contato

Dúvidas sobre filtros? Consulte:
1. Esta documentação
2. Logs do backend: `[FILTRO] Após X: Y carros`
3. Testes: `platform/backend/tests/test_year_filter.py`
